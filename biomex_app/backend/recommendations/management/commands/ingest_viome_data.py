"""
Management command: ingest_viome_data
Ingest Viome microbiome abundance + metadata CSV into Pinecone for BiomeX RAG.

Strategy:
- DO NOT index raw rows (meaningless for embeddings)
- Aggregate species by mean/std/presence_rate across all 40 samples
- Join with patient metadata to enrich context
- Index top-N most abundant species as semantically meaningful sentences

Usage:
    python manage.py ingest_viome_data \
        --species-csv /path/to/Viome_species_readcount_40samples.csv \
        --metadata-csv /path/to/Viome_microbiome_metadata.csv \
        --namespace biomex-microbiome \
        --top-n 200

Dependencies:
    pip install pandas numpy
    (already in requirements.txt)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError

from recommendations.rag_service import BiomexRAGService, RAGConfigurationError, RAGServiceError

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Known biological annotations for key microbiome species
# These are used to enrich the text chunks with semantic context
# ---------------------------------------------------------------------------
SPECIES_ANNOTATIONS: dict[str, str] = {
    "faecalibacterium prausnitzii": "producteur de butyrate, anti-inflammatoire, marqueur de santé intestinale",
    "akkermansia muciniphila": "protecteur de la barrière intestinale, inversement corrélé à l'obésité",
    "bifidobacterium": "probiotique majeur, régulateur immunitaire, favorise l'absorption des nutriments",
    "lactobacillus": "probiotique fermentant, protège contre les pathogènes, soutient l'immunité",
    "bacteroides": "décomposeur de polysaccharides complexes, rôle dans le métabolisme des acides biliaires",
    "prevotella copri": "associé à une alimentation riche en fibres végétales, présent dans les populations africaines",
    "ruminococcus": "dégradation de la cellulose et production de butyrate",
    "clostridium": "diversifié — certaines espèces bénéfiques (butyrogènes), d'autres pathogènes potentiels",
    "roseburia": "producteur de butyrate, effet protecteur sur le côlon",
    "eubacterium": "métabolisme des graisses, production de butyrate",
    "blautia": "associé à l'équilibre métabolique et au contrôle du glucose",
    "streptococcus": "peut être commensale ou pathogène selon l'espèce et le site",
    "escherichia": "commensale en faible quantité; certaines souches pathogènes à haute abondance",
    "coprococcus": "producteur de butyrate, corrélé positivement à la qualité de vie mentale",
    "alistipes": "dégradation des protéines, rôle potentiel dans l'humeur et la dépression",
}


def _get_annotation(species_name: str) -> str:
    """Return biological annotation for a species if known."""
    name_lower = species_name.lower()
    for key, annotation in SPECIES_ANNOTATIONS.items():
        if key in name_lower:
            return annotation
    return ""


def _symptom_label(symptom: str) -> str:
    mapping = {
        "healthy": "asymptomatique / sain",
        "mild": "symptômes légers",
        "moderate": "symptômes modérés",
        "severe": "symptômes sévères",
    }
    return mapping.get((symptom or "").strip().lower(), symptom or "inconnu")


# ---------------------------------------------------------------------------
# Django management command
# ---------------------------------------------------------------------------

class Command(BaseCommand):
    help = "Ingestion des données Viome (species + fonctions KO) dans Pinecone pour BiomeX RAG."

    def add_arguments(self, parser):
        parser.add_argument(
            "--species-csv",
            required=True,
            help="Chemin vers Viome_species_readcount_40samples.csv",
        )
        parser.add_argument(
            "--metadata-csv",
            default="",
            help="Chemin vers Viome_microbiome_metadata.csv (optionnel).",
        )
        parser.add_argument(
            "--function-csv",
            default="",
            help="Chemin vers Viome_function_KO_readcount_40samples.csv (optionnel).",
        )
        parser.add_argument(
            "--namespace",
            default="biomex-microbiome",
            help="Namespace Pinecone cible (défaut: biomex-microbiome).",
        )
        parser.add_argument(
            "--top-n",
            type=int,
            default=200,
            help="Nombre d'espèces les plus abondantes à indexer (défaut: 200).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Simuler sans envoyer à Pinecone.",
        )

    def handle(self, *args, **options):
        try:
            import pandas as pd
            import numpy as np
        except ImportError:
            raise CommandError("pandas et numpy sont requis. Lance: pip install pandas numpy")

        species_csv = options["species_csv"]
        metadata_csv = (options.get("metadata_csv") or "").strip()
        function_csv = (options.get("function_csv") or "").strip()
        namespace = (options.get("namespace") or "biomex-microbiome").strip()
        top_n = options["top_n"]
        dry_run = options["dry_run"]

        # Validate paths
        species_path = Path(species_csv)
        if not species_path.exists():
            raise CommandError(f"Fichier introuvable: {species_csv}")

        # ----------------------------------------------------------------
        # Step 1: Load and aggregate species data
        # ----------------------------------------------------------------
        self.stdout.write("📂  Chargement du CSV espèces...")
        try:
            # Detect CSV format: long (sample_name, species_name, readcount) or wide (index=species, cols=samples)
            header = pd.read_csv(species_path, nrows=1)
            columns = list(header.columns)

            if "species_name" in columns and "species_readcount" in columns:
                # LONG FORMAT: one row per (sample, species) pair
                self.stdout.write("   → Format détecté: long (tidy) — pivot en cours...")
                df_long = pd.read_csv(species_path, usecols=["sample_name", "species_name", "species_readcount"])
                df_long["species_readcount"] = pd.to_numeric(df_long["species_readcount"], errors="coerce").fillna(0)
                # Pivot: index=species, columns=samples
                df_species = df_long.pivot_table(
                    index="species_name",
                    columns="sample_name",
                    values="species_readcount",
                    aggfunc="sum",
                    fill_value=0,
                )
            else:
                # WIDE FORMAT: index=species, columns=samples
                self.stdout.write("   → Format détecté: wide — lecture directe...")
                df_species = pd.read_csv(species_path, index_col=0)
                df_species = df_species.apply(pd.to_numeric, errors="coerce").fillna(0)
        except Exception as exc:
            raise CommandError(f"Erreur lecture CSV espèces: {exc}")

        n_species = len(df_species)
        n_samples = len(df_species.columns)
        self.stdout.write(f"   → {n_species} espèces × {n_samples} échantillons (après pivot)")

        # Aggregate statistics per species
        species_stats = pd.DataFrame({
            "mean_abundance": df_species.mean(axis=1),
            "std_abundance": df_species.std(axis=1),
            "max_abundance": df_species.max(axis=1),
            "presence_rate": (df_species > 0).mean(axis=1),  # % of samples with presence
        })

        # Sort by mean abundance descending and take top-N
        species_stats = species_stats.sort_values("mean_abundance", ascending=False).head(top_n)
        self.stdout.write(f"   → Top {top_n} espèces sélectionnées")

        # ----------------------------------------------------------------
        # Step 2: Load patient metadata (optional)
        # ----------------------------------------------------------------
        metadata_summary = ""
        if metadata_csv and Path(metadata_csv).exists():
            self.stdout.write("📋  Chargement des métadonnées patients...")
            try:
                df_meta = pd.read_csv(metadata_csv)
                n_patients = len(df_meta)
                mean_age = df_meta["age"].mean() if "age" in df_meta.columns else None
                mean_bmi = df_meta["bmi"].mean() if "bmi" in df_meta.columns else None
                gender_counts = df_meta["gender"].value_counts().to_dict() if "gender" in df_meta.columns else {}

                metadata_summary = (
                    f"Cohorte : {n_patients} patients"
                    + (f", âge moyen {mean_age:.1f} ans" if mean_age else "")
                    + (f", IMC moyen {mean_bmi:.1f}" if mean_bmi else "")
                    + (f", genres : {gender_counts}" if gender_counts else "")
                    + "."
                )
                self.stdout.write(f"   → {metadata_summary}")
            except Exception as exc:
                self.stdout.write(self.style.WARNING(f"   ⚠ Métadonnées ignorées: {exc}"))

        # ----------------------------------------------------------------
        # Step 3: Build text chunks for each species
        # ----------------------------------------------------------------
        self.stdout.write("🧬  Construction des chunks d'espèces microbiennes...")
        custom_documents: list[dict[str, Any]] = []

        for species_name, row in species_stats.iterrows():
            mean_ab = row["mean_abundance"]
            std_ab = row["std_abundance"]
            max_ab = row["max_abundance"]
            presence = row["presence_rate"]

            # Abundance level label
            if mean_ab > 10000:
                level = "très élevée"
            elif mean_ab > 1000:
                level = "élevée"
            elif mean_ab > 100:
                level = "modérée"
            elif mean_ab > 0:
                level = "faible"
            else:
                level = "absente"

            annotation = _get_annotation(str(species_name))

            text_parts = [
                f"Espèce microbienne: {species_name}.",
                f"Abondance moyenne (cohorte Viome, n={len(df_species.columns)}): {mean_ab:.1f} reads (niveau: {level}).",
                f"Présente dans {presence * 100:.0f}% des échantillons.",
                f"Variabilité (écart-type): {std_ab:.1f}. Abondance maximale observée: {max_ab:.0f}.",
            ]

            if annotation:
                text_parts.append(f"Rôle biologique connu: {annotation}.")

            if metadata_summary:
                text_parts.append(f"Contexte de la cohorte: {metadata_summary}")

            chunk_text = " ".join(text_parts)

            custom_documents.append({
                "text": chunk_text,
                "title": f"Microbiome | {species_name}",
                "metadata": {
                    "doc_name": "viome_species_abundance",
                    "species": str(species_name),
                    "mean_abundance": float(mean_ab),
                    "presence_rate": float(presence),
                    "abundance_level": level,
                    "block_type": "microbiome_species",
                },
            })

        self.stdout.write(f"   → {len(custom_documents)} chunks espèces prêts")

        # ----------------------------------------------------------------
        # Step 4: Load KEGG functions (optional)
        # ----------------------------------------------------------------
        if function_csv and Path(function_csv).exists():
            self.stdout.write("⚗️   Chargement des fonctions KEGG (KO)...")
            try:
                func_header = pd.read_csv(Path(function_csv), nrows=1)
                func_cols = list(func_header.columns)

                if "species_name" in func_cols and "species_readcount" in func_cols:
                    # Long format with species columns — try KO column
                    ko_col = next((c for c in func_cols if "ko" in c.lower() or "function" in c.lower() or "gene" in c.lower()), None)
                    count_col = next((c for c in func_cols if "count" in c.lower() or "read" in c.lower()), func_cols[-1])
                    sample_col = "sample_name"
                    if ko_col and sample_col in func_cols:
                        df_func_long = pd.read_csv(Path(function_csv), usecols=[sample_col, ko_col, count_col])
                        df_func_long[count_col] = pd.to_numeric(df_func_long[count_col], errors="coerce").fillna(0)
                        df_func = df_func_long.pivot_table(
                            index=ko_col, columns=sample_col, values=count_col, aggfunc="sum", fill_value=0
                        )
                    else:
                        df_func = pd.read_csv(Path(function_csv), index_col=0).apply(pd.to_numeric, errors="coerce").fillna(0)
                else:
                    df_func = pd.read_csv(Path(function_csv), index_col=0).apply(pd.to_numeric, errors="coerce").fillna(0)

                func_stats = pd.DataFrame({
                    "mean_count": df_func.mean(axis=1),
                    "presence_rate": (df_func > 0).mean(axis=1),
                }).sort_values("mean_count", ascending=False).head(100)  # top 100 KEGG functions

                for ko_id, row in func_stats.iterrows():
                    ko_name = str(ko_id)
                    mean_c = row["mean_count"]
                    pres = row["presence_rate"]

                    chunk_text = (
                        f"Fonction métabolique KEGG: {ko_name}. "
                        f"Activité moyenne dans la cohorte Viome: {mean_c:.1f} reads. "
                        f"Présente dans {pres * 100:.0f}% des échantillons. "
                        f"Impliquée dans le métabolisme microbien intestinal."
                    )
                    custom_documents.append({
                        "text": chunk_text,
                        "title": f"KEGG | {ko_name}",
                        "metadata": {
                            "doc_name": "viome_function_ko",
                            "ko_id": ko_name,
                            "mean_count": float(mean_c),
                            "presence_rate": float(pres),
                            "block_type": "microbiome_function",
                        },
                    })

                self.stdout.write(self.style.SUCCESS(f"   → {len(df_func)} fonctions KO → 100 top ajoutées"))
            except Exception as exc:
                self.stdout.write(self.style.WARNING(f"   ⚠ Fonctions KO ignorées: {exc}"))

        # ----------------------------------------------------------------
        # Step 5: Dry run or ingest
        # ----------------------------------------------------------------
        self.stdout.write(f"\n📦  Total chunks à indexer: {len(custom_documents)}")

        if dry_run:
            self.stdout.write(self.style.WARNING("\n[DRY RUN] Aucun vecteur envoyé à Pinecone."))
            for i, doc in enumerate(custom_documents[:5]):
                self.stdout.write(f"  [{i}] {doc['text'][:150]}...")
            return

        service = BiomexRAGService()
        self.stdout.write(f"🚀  Envoi vers Pinecone (namespace: {namespace})...")

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
