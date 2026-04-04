"""
Management command: ingest_pdf_documents
Multimodal PDF ingestion pipeline for BiomeX RAG system.

Handles: text (layout-aware), tables (row→sentences), images (caption+context), OCR fallback.

Usage:
    python manage.py ingest_pdf_documents \
        --pdf-path /path/to/file.pdf \
        --doc-name west_african_food_composition \
        --namespace biomex-documents \
        --extract-tables \
        --extract-images

Dependencies:
    pip install pymupdf pdfplumber pytesseract Pillow
    sudo apt-get install -y tesseract-ocr tesseract-ocr-fra
"""

from __future__ import annotations

import hashlib
import io
import logging
import re
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError

from recommendations.rag_service import BiomexRAGService, RAGConfigurationError, RAGServiceError

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CHUNK_TARGET_CHARS = 2200  # ~550 tokens @ 4 chars/token
CHUNK_OVERLAP_CHARS = 320  # ~80 tokens overlap between consecutive chunks
MIN_TEXT_CHARS = 60        # Minimum text length to index a chunk
OCR_MIN_CHARS = 80         # Trigger OCR fallback if native text extraction is below this
FONT_SIZE_TITLE_THRESHOLD = 13.0  # Font size >= this → section title


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sha256_chunk_id(prefix: str, text: str) -> str:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:24]
    return f"{prefix}-{digest}"


def _clean_text(text: str) -> str:
    """Normalise whitespace and strip common PDF artefacts."""
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"(\w)-\s+(\w)", r"\1\2", text)  # re-join hyphenated line breaks
    return text.strip()


def _chunk_text(text: str, target: int = CHUNK_TARGET_CHARS, overlap: int = CHUNK_OVERLAP_CHARS) -> list[str]:
    """Split text into overlapping semantic chunks at sentence boundaries."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks: list[str] = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) > target and current:
            chunks.append(current.strip())
            # Keep last part for overlap
            words = current.split()
            overlap_words = words[max(0, len(words) - overlap // 6):]
            current = " ".join(overlap_words) + " " + sentence
        else:
            current = (current + " " + sentence).strip()

    if current.strip():
        chunks.append(current.strip())

    return [c for c in chunks if len(c) >= MIN_TEXT_CHARS]


# ---------------------------------------------------------------------------
# Extraction functions
# ---------------------------------------------------------------------------

def _extract_text_blocks(pdf_path: str) -> list[dict[str, Any]]:
    """Extract all text blocks with section-level metadata using pymupdf."""
    try:
        import fitz  # pymupdf
    except ImportError:
        raise CommandError("pymupdf n'est pas installé. Lance: pip install pymupdf")

    doc = fitz.open(pdf_path)
    results: list[dict[str, Any]] = []
    current_section = "Introduction"
    page_buffer = ""

    for page_num, page in enumerate(doc):
        page_dict = page.get_text("dict")
        page_text_native = page.get_text().strip()

        # OCR fallback for scanned pages
        if len(page_text_native) < OCR_MIN_CHARS:
            ocr_text = _ocr_page(page)
            if ocr_text:
                chunks = _chunk_text(_clean_text(ocr_text))
                for chunk in chunks:
                    results.append({
                        "text": chunk,
                        "page": page_num + 1,
                        "section": current_section,
                        "type": "text_ocr",
                    })
            continue

        # Process native text blocks with layout awareness
        for block in page_dict.get("blocks", []):
            if block.get("type") != 0:  # 0 = text block
                continue

            spans_text = []
            is_title = False

            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    span_text = span.get("text", "").strip()
                    if not span_text:
                        continue
                    font_size = span.get("size", 0)
                    if font_size >= FONT_SIZE_TITLE_THRESHOLD and len(span_text) < 200:
                        is_title = True
                    spans_text.append(span_text)

            block_text = _clean_text(" ".join(spans_text))
            if not block_text or len(block_text) < 20:
                continue

            if is_title and len(block_text) < 200:
                current_section = block_text
                continue

            page_buffer += " " + block_text

        # Flush buffer at end of page
        if page_buffer.strip():
            for chunk in _chunk_text(_clean_text(page_buffer)):
                results.append({
                    "text": chunk,
                    "page": page_num + 1,
                    "section": current_section,
                    "type": "text",
                })
            page_buffer = ""

    doc.close()
    return results


def _extract_tables(pdf_path: str) -> list[dict[str, Any]]:
    """Extract tables and convert each row into a structured sentence for embedding."""
    try:
        import pdfplumber
    except ImportError:
        raise CommandError("pdfplumber n'est pas installé. Lance: pip install pdfplumber")

    results: list[dict[str, Any]] = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            try:
                tables = page.extract_tables()
            except Exception as exc:
                logger.warning("Erreur extraction tableau page %d: %s", page_num + 1, exc)
                continue

            for table_idx, table in enumerate(tables):
                if not table or len(table) < 2:
                    continue

                # First row = headers
                headers = [str(h or "").strip() for h in table[0]]
                if not any(headers):
                    continue

                # Accumulate row chunks
                row_texts: list[str] = []
                for row in table[1:]:
                    cells = [str(c or "").strip() for c in row]
                    pairs = [
                        f"{h}: {v}"
                        for h, v in zip(headers, cells)
                        if h and v and v.lower() not in ("", "-", "n/a", "nd")
                    ]
                    if len(pairs) >= 2:
                        sentence = ". ".join(pairs) + "."
                        row_texts.append(sentence)

                # Group rows into manageable chunks
                buffer = ""
                chunk_idx = 0
                for row_sentence in row_texts:
                    if len(buffer) + len(row_sentence) > CHUNK_TARGET_CHARS and buffer:
                        results.append({
                            "text": buffer.strip(),
                            "page": page_num + 1,
                            "type": "table",
                            "table_index": table_idx,
                            "chunk_index": chunk_idx,
                            "headers": ", ".join(h for h in headers if h),
                        })
                        buffer = row_sentence
                        chunk_idx += 1
                    else:
                        buffer = (buffer + " " + row_sentence).strip()

                if buffer.strip() and len(buffer.strip()) >= MIN_TEXT_CHARS:
                    results.append({
                        "text": buffer.strip(),
                        "page": page_num + 1,
                        "type": "table",
                        "table_index": table_idx,
                        "chunk_index": chunk_idx,
                        "headers": ", ".join(h for h in headers if h),
                    })

    return results


def _extract_images(pdf_path: str, doc_name: str) -> list[dict[str, Any]]:
    """Extract image context: captions found near the image + surrounding page text snippet."""
    try:
        import fitz
    except ImportError:
        raise CommandError("pymupdf n'est pas installé. Lance: pip install pymupdf")

    doc = fitz.open(pdf_path)
    results: list[dict[str, Any]] = []

    # Regex patterns for figure/table captions in French and English
    caption_patterns = [
        re.compile(r"(Figure|Fig\.?|Tableau|Table|Graphe|Graph|Graphique)\s*\.?\s*\d+[:\.\s][^\n]{5,200}", re.IGNORECASE),
    ]

    for page_num, page in enumerate(doc):
        images = page.get_images(full=True)
        if not images:
            continue

        page_text = page.get_text()
        context_snippet = _clean_text(page_text[:800])

        # Find captions in the page text
        captions: list[str] = []
        for pattern in caption_patterns:
            for match in pattern.findall(page_text):
                caption = _clean_text(match if isinstance(match, str) else " ".join(match))
                if caption and caption not in captions:
                    captions.append(caption)

        for img_idx, img_info in enumerate(images):
            xref = img_info[0]
            try:
                base_image = doc.extract_image(xref)
            except Exception:
                continue

            # Skip very small images (icons, decorative elements)
            width = base_image.get("width", 0)
            height = base_image.get("height", 0)
            if width < 80 or height < 80:
                continue

            caption_text = captions[img_idx] if img_idx < len(captions) else ""
            description = caption_text or f"Graphe/Image {img_idx + 1} page {page_num + 1}"

            chunk_text = (
                f"[Contenu visuel - {doc_name}] {description}\n"
                f"Contexte de la page {page_num + 1}: {context_snippet}"
            )

            if len(chunk_text) >= MIN_TEXT_CHARS:
                results.append({
                    "text": chunk_text,
                    "page": page_num + 1,
                    "type": "image",
                    "image_index": img_idx,
                    "caption": caption_text,
                    "image_size": f"{width}x{height}",
                })

    doc.close()
    return results


def _ocr_page(page) -> str:
    """Attempt OCR on a page using pytesseract. Returns empty string if unavailable."""
    try:
        import pytesseract
        from PIL import Image
        import fitz

        pix = page.get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        return pytesseract.image_to_string(img, lang="fra+eng").strip()
    except Exception as exc:
        logger.debug("OCR indisponible: %s", exc)
        return ""


# ---------------------------------------------------------------------------
# Django management command
# ---------------------------------------------------------------------------

class Command(BaseCommand):
    help = "Ingestion multimodale de PDFs (texte, tableaux, images) dans Pinecone pour BiomeX RAG."

    def add_arguments(self, parser):
        parser.add_argument(
            "--pdf-path",
            required=True,
            help="Chemin absolu ou relatif vers le fichier PDF.",
        )
        parser.add_argument(
            "--doc-name",
            required=True,
            help="Identifiant unique du document (ex: west_african_food_composition).",
        )
        parser.add_argument(
            "--namespace",
            default="biomex-documents",
            help="Namespace Pinecone cible (défaut: biomex-documents).",
        )
        parser.add_argument(
            "--extract-tables",
            action="store_true",
            default=True,
            help="Extraire et indexer les tableaux (activé par défaut).",
        )
        parser.add_argument(
            "--no-extract-tables",
            action="store_false",
            dest="extract_tables",
            help="Désactiver l'extraction des tableaux.",
        )
        parser.add_argument(
            "--extract-images",
            action="store_true",
            default=False,
            help="Extraire les légendes et contextes des images/graphes.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Simuler l'extraction sans envoyer à Pinecone.",
        )

    def handle(self, *args, **options):
        pdf_path = options["pdf_path"]
        doc_name = options["doc_name"].strip().replace(" ", "_").lower()
        namespace = (options.get("namespace") or "biomex-documents").strip()
        extract_tables = options["extract_tables"]
        extract_images = options["extract_images"]
        dry_run = options["dry_run"]

        # Validate path
        path = Path(pdf_path)
        if not path.exists() or not path.is_file():
            raise CommandError(f"Fichier PDF introuvable: {pdf_path}")
        if path.suffix.lower() != ".pdf":
            raise CommandError(f"Le fichier doit être un PDF: {pdf_path}")

        self.stdout.write(f"🔍  Lecture: {path.name}")
        self.stdout.write(f"📌  Namespace: {namespace}  |  Doc: {doc_name}")

        # --- Step 1: Extract text ---
        self.stdout.write("📄  Extraction du texte (layout-aware)...")
        text_blocks = _extract_text_blocks(str(path))
        self.stdout.write(self.style.SUCCESS(f"   → {len(text_blocks)} blocs texte extraits"))

        # --- Step 2: Extract tables ---
        table_blocks: list[dict] = []
        if extract_tables:
            self.stdout.write("📊  Extraction des tableaux...")
            try:
                table_blocks = _extract_tables(str(path))
                self.stdout.write(self.style.SUCCESS(f"   → {len(table_blocks)} chunks tableau extraits"))
            except CommandError as exc:
                self.stdout.write(self.style.WARNING(f"   ⚠ Tableaux ignorés: {exc}"))

        # --- Step 3: Extract images ---
        image_blocks: list[dict] = []
        if extract_images:
            self.stdout.write("🖼️   Extraction des images/graphes...")
            try:
                image_blocks = _extract_images(str(path), doc_name)
                self.stdout.write(self.style.SUCCESS(f"   → {len(image_blocks)} chunks image extraits"))
            except CommandError as exc:
                self.stdout.write(self.style.WARNING(f"   ⚠ Images ignorées: {exc}"))

        # --- Merge all blocks ---
        all_blocks = text_blocks + table_blocks + image_blocks
        self.stdout.write(f"\n📦  Total chunks à indexer: {len(all_blocks)}")

        if dry_run:
            self.stdout.write(self.style.WARNING("\n[DRY RUN] Aucun vecteur envoyé à Pinecone."))
            for i, block in enumerate(all_blocks[:5]):
                self.stdout.write(f"  [{i}] ({block['type']}) {block['text'][:120]}...")
            return

        # --- Step 4: Build KnowledgeChunks and ingest ---
        service = BiomexRAGService()
        custom_documents = []
        for block in all_blocks:
            block_type = block.get("type", "text")
            chunk_text = block["text"]

            meta_prefix = {
                "text": "[Texte]",
                "text_ocr": "[OCR]",
                "table": "[Tableau]",
                "image": "[Visuel]",
            }.get(block_type, "[Doc]")

            full_text = (
                f"{meta_prefix} {doc_name} | Section: {block.get('section', block.get('headers', ''))} "
                f"| Page {block.get('page', '?')}\n{chunk_text}"
            )

            metadata = {
                "doc_name": doc_name,
                "pdf_file": path.name,
                "page": block.get("page"),
                "section": block.get("section", ""),
                "headers": block.get("headers", ""),
                "block_type": block_type,
                "caption": block.get("caption", ""),
            }

            custom_documents.append({
                "text": full_text,
                "title": f"{doc_name} | {block_type} | p.{block.get('page', '?')}",
                "metadata": metadata,
            })

        self.stdout.write(f"\n🚀  Envoi de {len(custom_documents)} vecteurs vers Pinecone (namespace: {namespace})...")

        try:
            result = service.ingest_knowledge(
                source="custom",
                namespace=namespace,
                custom_documents=custom_documents,
            )
        except (RAGConfigurationError, RAGServiceError) as exc:
            raise CommandError(str(exc))

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅  Ingestion terminée: {result['ingested_count']} chunks "
                f"→ namespace '{result['namespace']}'"
            )
        )
