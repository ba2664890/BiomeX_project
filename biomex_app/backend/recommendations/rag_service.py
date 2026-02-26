import csv
import hashlib
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, urlunparse

import requests
from django.conf import settings

from microbiome.models import MicrobiomeAnalysis
from nutrition.models import FoodItem, FoodSubstitution, Recipe, RecipeIngredient

logger = logging.getLogger(__name__)


class RAGServiceError(Exception):
    """Generic RAG service error."""


class RAGConfigurationError(RAGServiceError):
    """Raised when required RAG configuration is missing."""


@dataclass
class KnowledgeChunk:
    chunk_id: str
    text: str
    metadata: dict[str, Any]


class BiomexRAGService:
    """RAG service using Hugging Face Inference + Pinecone HTTP API."""

    def __init__(self) -> None:
        self.hf_api_token = settings.RAG_HF_API_TOKEN
        self.hf_generation_model = settings.RAG_HF_GENERATION_MODEL
        self.hf_embedding_model = settings.RAG_HF_EMBEDDING_MODEL
        self.hf_generation_url = self._normalize_hf_endpoint_url(settings.RAG_HF_GENERATION_URL)
        self.hf_embedding_url = self._normalize_hf_endpoint_url(settings.RAG_HF_EMBEDDING_URL)
        self.hf_router_base_url = self._normalize_router_base_url(settings.RAG_HF_ROUTER_BASE_URL)
        self.hf_router_provider = settings.RAG_HF_ROUTER_PROVIDER

        self.pinecone_api_key = settings.RAG_PINECONE_API_KEY
        self.pinecone_index_host = self._normalize_pinecone_host(settings.RAG_PINECONE_INDEX_HOST)
        self.default_namespace = settings.RAG_PINECONE_NAMESPACE
        self.default_top_k = settings.RAG_DEFAULT_TOP_K
        self.max_context_chars = settings.RAG_MAX_CONTEXT_CHARS

    @staticmethod
    def _normalize_pinecone_host(host: str) -> str:
        value = (host or "").strip()
        if not value:
            return value
        if value.startswith("http://") or value.startswith("https://"):
            return value.rstrip("/")
        return f"https://{value.rstrip('/')}"

    @staticmethod
    def _normalize_router_base_url(base_url: str) -> str:
        legacy_host = "api-inference.huggingface.co"
        router_host = "router.huggingface.co"
        value = (base_url or "").strip()
        if not value:
            return f"https://{router_host}"
        if value.startswith("http://") or value.startswith("https://"):
            normalized = value.rstrip("/")
        else:
            normalized = f"https://{value.rstrip('/')}"

        parsed = urlparse(normalized)
        if parsed.netloc.lower() == legacy_host:
            logger.warning(
                "Deprecated Hugging Face base URL detected (%s). Falling back to https://%s.",
                legacy_host,
                router_host,
            )
            parsed = parsed._replace(scheme="https", netloc=router_host)
            return urlunparse(parsed).rstrip("/")
        return normalized

    @staticmethod
    def _normalize_hf_endpoint_url(url: str) -> str:
        legacy_host = "api-inference.huggingface.co"
        router_host = "router.huggingface.co"
        value = (url or "").strip()
        if not value:
            return ""
        if not (value.startswith("http://") or value.startswith("https://")):
            value = f"https://{value}"
        parsed = urlparse(value)
        if parsed.netloc.lower() == legacy_host:
            logger.warning(
                "Deprecated Hugging Face endpoint detected (%s). Falling back to https://%s.",
                legacy_host,
                router_host,
            )
            parsed = parsed._replace(scheme="https", netloc=router_host)
            return urlunparse(parsed)
        return value

    def _validate_rag_config(self) -> None:
        required = {
            "RAG_HF_API_TOKEN": self.hf_api_token,
            "RAG_PINECONE_API_KEY": self.pinecone_api_key,
            "RAG_PINECONE_INDEX_HOST": self.pinecone_index_host,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise RAGConfigurationError(
                f"Configuration RAG manquante: {', '.join(missing)}"
            )

    def health_status(self) -> dict[str, Any]:
        return {
            "huggingface_token_configured": bool(self.hf_api_token),
            "huggingface_generation_model": self.hf_generation_model,
            "huggingface_embedding_model": self.hf_embedding_model,
            "huggingface_router_base_url": self.hf_router_base_url,
            "huggingface_router_provider": self.hf_router_provider or None,
            "huggingface_custom_generation_url": self.hf_generation_url or None,
            "huggingface_custom_embedding_url": self.hf_embedding_url or None,
            "pinecone_configured": bool(self.pinecone_api_key and self.pinecone_index_host),
            "pinecone_index_host": self.pinecone_index_host,
            "pinecone_namespace": self.default_namespace,
            "default_top_k": self.default_top_k,
        }

    def _hf_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.hf_api_token}",
            "Content-Type": "application/json",
        }

    def _pinecone_headers(self) -> dict[str, str]:
        return {
            "Api-Key": self.pinecone_api_key,
            "Content-Type": "application/json",
        }

    @staticmethod
    def _mean_pool(matrix: list[list[float]]) -> list[float]:
        if not matrix:
            return []
        dims = len(matrix[0])
        sums = [0.0] * dims
        for row in matrix:
            for i, val in enumerate(row):
                sums[i] += float(val)
        return [val / len(matrix) for val in sums]

    def _router_model_name(self, model_name: str) -> str:
        model = (model_name or "").strip()
        provider = (self.hf_router_provider or "").strip()
        if provider and ":" not in model:
            return f"{model}:{provider}"
        return model

    def _hf_post_json(
        self,
        *,
        url: str,
        payload: dict[str, Any],
        timeout: int,
        error_prefix: str,
    ) -> Any:
        def _trim(value: str, max_len: int = 800) -> str:
            text = (value or "").replace("\n", " ").strip()
            if len(text) <= max_len:
                return text
            return f"{text[:max_len]}...[truncated]"

        try:
            response = requests.post(url, headers=self._hf_headers(), json=payload, timeout=timeout)
        except requests.RequestException as exc:
            debug_message = (
                f"[HF DEBUG] network error | stage={error_prefix} | url={url} | error={exc}"
            )
            print(debug_message, flush=True)
            logger.warning(debug_message)
            raise RAGServiceError(f"{error_prefix} [url={url}] (network): {exc}") from exc

        if response.status_code >= 400:
            response_body = _trim(response.text)
            debug_message = (
                f"[HF DEBUG] request failed | stage={error_prefix} | url={url} | "
                f"status={response.status_code} | body={response_body}"
            )
            print(debug_message, flush=True)
            logger.warning(debug_message)
            raise RAGServiceError(
                f"{error_prefix} ({response.status_code}) [url={url}]: {response_body}"
            )
        try:
            data = response.json()
        except ValueError as exc:
            response_body = _trim(response.text)
            debug_message = (
                f"[HF DEBUG] invalid json | stage={error_prefix} | url={url} | "
                f"status={response.status_code} | body={response_body}"
            )
            print(debug_message, flush=True)
            logger.warning(debug_message)
            raise RAGServiceError(
                f"{error_prefix} [url={url}]: réponse JSON invalide."
            ) from exc
        if isinstance(data, dict) and data.get("error"):
            api_error = _trim(str(data["error"]))
            debug_message = (
                f"[HF DEBUG] api error field | stage={error_prefix} | url={url} | "
                f"status={response.status_code} | error={api_error}"
            )
            print(debug_message, flush=True)
            logger.warning(debug_message)
            raise RAGServiceError(f"{error_prefix} [url={url}]: {api_error}")
        return data

    def _parse_embedding_response(self, data: Any) -> list[float]:
        # OpenAI-compatible embeddings response:
        # {"data":[{"embedding":[...]}], ...}
        if isinstance(data, dict):
            rows = data.get("data")
            if isinstance(rows, list) and rows and isinstance(rows[0], dict):
                emb = rows[0].get("embedding")
                if isinstance(emb, list) and emb and isinstance(emb[0], (int, float)):
                    return [float(x) for x in emb]
            # Some providers may return {"embedding":[...]}
            emb = data.get("embedding")
            if isinstance(emb, list) and emb and isinstance(emb[0], (int, float)):
                return [float(x) for x in emb]
        return []

    def _embed_text(self, text: str) -> list[float]:
        self._validate_rag_config()
        if not text.strip():
            raise RAGServiceError("Le texte à encoder est vide.")

        attempts: list[tuple[str, str, dict[str, Any]]] = []

        if self.hf_embedding_url:
            attempts.append(
                (
                    "custom embedding endpoint",
                    self.hf_embedding_url,
                    {"inputs": text, "options": {"wait_for_model": True}},
                )
            )

        attempts.extend(
            [
                (
                    "router feature-extraction pipeline",
                    f"{self.hf_router_base_url}/hf-inference/models/{self.hf_embedding_model}/pipeline/feature-extraction",
                    {"inputs": text, "options": {"wait_for_model": True}},
                ),
                (
                    "router models directly",
                    f"{self.hf_router_base_url}/hf-inference/models/{self.hf_embedding_model}",
                    {"inputs": text, "options": {"wait_for_model": True}},
                ),
                (
                    "router models list-input",
                    f"{self.hf_router_base_url}/hf-inference/models/{self.hf_embedding_model}",
                    {"inputs": [text], "options": {"wait_for_model": True}},
                ),
            ]
        )

        errors: list[str] = []
        data: Any = None
        for label, url, payload in attempts:
            try:
                data = self._hf_post_json(
                    url=url,
                    payload=payload,
                    timeout=90,
                    error_prefix=f"Hugging Face embedding error [{label}]",
                )
                break
            except RAGServiceError as exc:
                errors.append(str(exc))
                continue
        else:
            raise RAGServiceError(" | ".join(errors) if errors else "Embedding indisponible.")

        parsed = self._parse_embedding_response(data)
        if parsed:
            return parsed

        # Possible response shapes:
        # 1) [0.01, 0.02, ...]
        # 2) [[token_1...], [token_2...], ...] -> mean pool
        # 3) [[[token_1...], ...]] -> first batch + mean pool
        if isinstance(data, list) and data:
            first = data[0]
            if isinstance(first, (int, float)):
                return [float(x) for x in data]
            if isinstance(first, list) and first and isinstance(first[0], (int, float)):
                return self._mean_pool([[float(x) for x in row] for row in data])
            if isinstance(first, list) and first and isinstance(first[0], list):
                return self._mean_pool([[float(x) for x in row] for row in first])

        raise RAGServiceError("Format de réponse embedding inattendu.")

    @staticmethod
    def _extract_generation_text(data: Any) -> str:
        # OpenAI-compatible chat completions.
        if isinstance(data, dict):
            choices = data.get("choices")
            if isinstance(choices, list) and choices and isinstance(choices[0], dict):
                choice = choices[0]
                message = choice.get("message")
                if isinstance(message, dict):
                    content = message.get("content")
                    if isinstance(content, str):
                        return content.strip()
                    if isinstance(content, list):
                        parts = [
                            str(part.get("text", "")).strip()
                            for part in content
                            if isinstance(part, dict) and part.get("type") == "text"
                        ]
                        text = "\n".join([part for part in parts if part])
                        if text:
                            return text
                choice_text = choice.get("text")
                if isinstance(choice_text, str):
                    return choice_text.strip()

        # Legacy text-generation response.
        if isinstance(data, list) and data and isinstance(data[0], dict) and data[0].get("generated_text"):
            return str(data[0]["generated_text"]).strip()
        if isinstance(data, dict) and data.get("generated_text"):
            return str(data["generated_text"]).strip()
        if isinstance(data, str):
            return data.strip()
        return ""

    def _generate_answer(self, prompt: str) -> str:
        self._validate_rag_config()
        router_model = self._router_model_name(self.hf_generation_model)
        attempts: list[tuple[str, str, dict[str, Any]]] = []

        if self.hf_generation_url:
            attempts.append(
                (
                    "custom generation endpoint",
                    self.hf_generation_url,
                    {
                        "inputs": prompt,
                        "parameters": {
                            "max_new_tokens": 512,
                            "temperature": 0.2,
                            "return_full_text": False,
                        },
                        "options": {"wait_for_model": True},
                    },
                )
            )

        attempts.extend(
            [
                (
                    "router text-generation pipeline",
                    f"{self.hf_router_base_url}/hf-inference/models/{self.hf_generation_model}/pipeline/text-generation",
                    {
                        "inputs": prompt,
                        "parameters": {
                            "max_new_tokens": 512,
                            "temperature": 0.2,
                        },
                        "options": {"wait_for_model": True},
                    },
                ),
                (
                    "router v1 chat completions",
                    f"{self.hf_router_base_url}/v1/chat/completions",
                    {
                        "model": router_model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 512,
                        "temperature": 0.2,
                    },
                ),
            ]
        )

        errors: list[str] = []
        for label, url, payload in attempts:
            try:
                data = self._hf_post_json(
                    url=url,
                    payload=payload,
                    timeout=180,
                    error_prefix=f"Hugging Face generation error [{label}]",
                )
                text = self._extract_generation_text(data)
                if text:
                    return text
                errors.append(f"Hugging Face generation error [{label}]: format de réponse inattendu.")
            except RAGServiceError as exc:
                errors.append(str(exc))
                continue

        raise RAGServiceError(" | ".join(errors) if errors else "Génération indisponible.")

    def _upsert_vectors(self, vectors: list[dict[str, Any]], namespace: str) -> None:
        if not vectors:
            return
        url = f"{self.pinecone_index_host}/vectors/upsert"
        payload = {
            "namespace": namespace,
            "vectors": vectors,
        }
        response = requests.post(url, headers=self._pinecone_headers(), json=payload, timeout=120)
        if response.status_code >= 400:
            raise RAGServiceError(
                f"Pinecone upsert error ({response.status_code}): {response.text}"
            )

    def _query_vectors(self, query_vector: list[float], top_k: int, namespace: str) -> list[dict[str, Any]]:
        url = f"{self.pinecone_index_host}/query"
        payload = {
            "namespace": namespace,
            "vector": query_vector,
            "topK": top_k,
            "includeMetadata": True,
        }
        response = requests.post(url, headers=self._pinecone_headers(), json=payload, timeout=60)
        if response.status_code >= 400:
            raise RAGServiceError(
                f"Pinecone query error ({response.status_code}): {response.text}"
            )
        data = response.json()
        return data.get("matches", []) if isinstance(data, dict) else []

    @staticmethod
    def _stable_chunk_id(prefix: str, text: str) -> str:
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:24]
        return f"{prefix}-{digest}"

    def _food_chunks(self) -> list[KnowledgeChunk]:
        chunks: list[KnowledgeChunk] = []
        for food in FoodItem.objects.filter(is_active=True).order_by("id"):
            text = (
                f"Food: {food.name}\n"
                f"Nom local: {food.name_local or 'N/A'}\n"
                f"Categorie: {food.get_category_display()}\n"
                f"Description: {food.description or 'N/A'}\n"
                f"Calories: {food.calories} kcal/100g\n"
                f"Proteines: {food.proteins} g/100g\n"
                f"Glucides: {food.carbs} g/100g\n"
                f"Lipides: {food.fats} g/100g\n"
                f"Fibres: {food.fiber} g/100g\n"
                f"Score prebiotique: {food.prebiotic_score}/100\n"
                f"Probiotique: {'oui' if food.probiotic else 'non'}\n"
                f"Anti-inflammatoire: {'oui' if food.anti_inflammatory else 'non'}\n"
                f"Saison: {food.get_season_display()}"
            )
            chunks.append(
                KnowledgeChunk(
                    chunk_id=self._stable_chunk_id("food", text),
                    text=text,
                    metadata={
                        "source_type": "food_item",
                        "food_id": food.id,
                        "name": food.name,
                    },
                )
            )
        return chunks

    def _recipe_chunks(self) -> list[KnowledgeChunk]:
        chunks: list[KnowledgeChunk] = []
        recipe_map: dict[int, list[str]] = {}
        for rel in RecipeIngredient.objects.select_related("food", "recipe").all():
            recipe_map.setdefault(rel.recipe_id, []).append(f"{rel.quantity} {rel.food.name}")

        for recipe in Recipe.objects.filter(is_active=True).order_by("id"):
            ingredients = ", ".join(recipe_map.get(recipe.id, [])) or "N/A"
            text = (
                f"Recette: {recipe.name}\n"
                f"Description: {recipe.description or 'N/A'}\n"
                f"Difficulte: {recipe.get_difficulty_display()}\n"
                f"Preparation: {recipe.prep_time} min\n"
                f"Cuisson: {recipe.cook_time} min\n"
                f"Portions: {recipe.servings}\n"
                f"Score microbiome: {recipe.microbiome_score}/100\n"
                f"Ingrédients: {ingredients}\n"
                f"Tags: {', '.join(recipe.tags or []) if recipe.tags else 'N/A'}"
            )
            chunks.append(
                KnowledgeChunk(
                    chunk_id=self._stable_chunk_id("recipe", text),
                    text=text,
                    metadata={
                        "source_type": "recipe",
                        "recipe_id": recipe.id,
                        "name": recipe.name,
                    },
                )
            )
        return chunks

    def _substitution_chunks(self) -> list[KnowledgeChunk]:
        chunks: list[KnowledgeChunk] = []
        substitutions = FoodSubstitution.objects.select_related("food_to_avoid", "food_to_prefer").all()
        for substitution in substitutions:
            text = (
                f"Substitution alimentaire: eviter {substitution.food_to_avoid.name}; "
                f"preferer {substitution.food_to_prefer.name}. "
                f"Impact score: {substitution.impact_score}. "
                f"Raison: {substitution.reason or 'N/A'}"
            )
            chunks.append(
                KnowledgeChunk(
                    chunk_id=self._stable_chunk_id("substitution", text),
                    text=text,
                    metadata={
                        "source_type": "food_substitution",
                        "avoid_food": substitution.food_to_avoid.name,
                        "prefer_food": substitution.food_to_prefer.name,
                    },
                )
            )
        return chunks

    def _csv_chunks(self, csv_path: str, text_column: str | None = None, max_rows: int = 500) -> list[KnowledgeChunk]:
        path = Path(csv_path)
        if not path.exists() or not path.is_file():
            raise RAGServiceError(f"CSV introuvable: {csv_path}")
        chunks: list[KnowledgeChunk] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for index, row in enumerate(reader):
                if index >= max_rows:
                    break
                if text_column and text_column in row:
                    text = str(row[text_column]).strip()
                else:
                    parts = [f"{k}: {v}" for k, v in row.items() if v not in (None, "")]
                    text = " | ".join(parts).strip()
                if not text:
                    continue
                chunk_id = self._stable_chunk_id(f"csv-{path.stem}", f"{index}-{text}")
                chunks.append(
                    KnowledgeChunk(
                        chunk_id=chunk_id,
                        text=text,
                        metadata={
                            "source_type": "csv",
                            "csv_file": path.name,
                            "row_index": index,
                        },
                    )
                )
        return chunks

    def ingest_knowledge(
        self,
        source: str,
        namespace: str | None = None,
        csv_path: str | None = None,
        csv_text_column: str | None = None,
        custom_documents: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        self._validate_rag_config()
        namespace_value = namespace or self.default_namespace

        if source == "nutrition_db":
            chunks = self._food_chunks() + self._recipe_chunks() + self._substitution_chunks()
        elif source == "csv":
            if not csv_path:
                raise RAGServiceError("csv_path est requis pour source='csv'.")
            chunks = self._csv_chunks(csv_path=csv_path, text_column=csv_text_column)
        elif source == "custom":
            chunks = []
            for doc in custom_documents or []:
                text = str(doc.get("text", "")).strip()
                if not text:
                    continue
                title = str(doc.get("title", "")).strip()
                composed = f"{title}\n{text}" if title else text
                chunk_id = self._stable_chunk_id("custom", composed)
                metadata = {
                    "source_type": "custom",
                    "title": title,
                }
                metadata.update(doc.get("metadata", {}))
                chunks.append(KnowledgeChunk(chunk_id=chunk_id, text=composed, metadata=metadata))
        else:
            raise RAGServiceError(f"Source RAG non supportée: {source}")

        vectors = []
        for chunk in chunks:
            embedding = self._embed_text(chunk.text)
            vectors.append(
                {
                    "id": chunk.chunk_id,
                    "values": embedding,
                    "metadata": {
                        **chunk.metadata,
                        "text": chunk.text[:3000],
                    },
                }
            )

        self._upsert_vectors(vectors=vectors, namespace=namespace_value)
        return {
            "source": source,
            "namespace": namespace_value,
            "ingested_count": len(vectors),
        }

    @staticmethod
    def _build_user_context(user) -> str:
        latest_analysis = (
            MicrobiomeAnalysis.objects.filter(user=user, status="completed")
            .order_by("-sample_date")
            .first()
        )
        lines = [
            f"Age: {user.age if user.age is not None else 'N/A'}",
            f"Ville: {user.city or 'N/A'}",
            f"Pays: {user.country or 'N/A'}",
            f"Preferences alimentaires: {', '.join(user.dietary_preferences) if user.dietary_preferences else 'N/A'}",
            f"Allergies: {', '.join(user.allergies) if user.allergies else 'N/A'}",
            f"BMI: {user.bmi if user.bmi is not None else 'N/A'}",
        ]
        if latest_analysis:
            lines.extend(
                [
                    f"Microbiome score global: {latest_analysis.overall_score}/100",
                    f"Diversite microbiome: {latest_analysis.diversity_score}/100",
                    f"Inflammation: {latest_analysis.inflammation_score}/100",
                    f"Resume analyse: {latest_analysis.summary or 'N/A'}",
                ]
            )
        return "\n".join(lines)

    @staticmethod
    def _build_fallback_answer(question: str, sources: list[dict[str, Any]]) -> str:
        source_names = [
            str(src.get("name") or src.get("source_type") or src.get("id") or "").strip()
            for src in sources
        ]
        source_names = [name for name in source_names if name]
        source_summary = ", ".join(source_names[:5]) if source_names else "Aucune source récupérée."

        return (
            "1) Synthèse clinique courte\n"
            "Le service de génération IA est temporairement indisponible. "
            "Je ne peux pas fournir une synthèse clinique personnalisée fiable pour le moment.\n\n"
            "2) Recommandations alimentaires concrètes (3 à 5)\n"
            "- Prioriser des aliments peu transformés et riches en fibres (légumineuses, légumes, céréales complètes).\n"
            "- Introduire progressivement des aliments fermentés tolérés.\n"
            "- Hydratation régulière et suivi des symptômes digestifs pendant 7 jours.\n"
            "- Poser à nouveau la question dans quelques minutes lorsque le service IA sera revenu.\n\n"
            "3) Précautions / limites\n"
            "- Réponse de secours non générée par le modèle clinique.\n"
            "- Ne remplace pas un avis médical.\n\n"
            "4) Sources utilisées (liste courte)\n"
            f"- {source_summary}\n\n"
            f"Question reçue: {question}"
        )

    def answer_question(
        self,
        user,
        question: str,
        top_k: int | None = None,
        namespace: str | None = None,
    ) -> dict[str, Any]:
        self._validate_rag_config()
        question_clean = (question or "").strip()
        if not question_clean:
            raise RAGServiceError("La question est vide.")

        namespace_value = namespace or self.default_namespace
        top_k_value = top_k or self.default_top_k

        context_parts = []
        sources = []
        warnings: list[str] = []

        try:
            query_vector = self._embed_text(question_clean)
            matches = self._query_vectors(query_vector=query_vector, top_k=top_k_value, namespace=namespace_value)

            chars = 0
            for match in matches:
                metadata = match.get("metadata", {}) or {}
                snippet = str(metadata.get("text", "")).strip()
                if not snippet:
                    continue
                if chars + len(snippet) > self.max_context_chars:
                    break
                context_parts.append(snippet)
                chars += len(snippet)
                sources.append(
                    {
                        "id": match.get("id"),
                        "score": match.get("score"),
                        "source_type": metadata.get("source_type"),
                        "name": metadata.get("name") or metadata.get("title") or metadata.get("csv_file"),
                    }
                )
        except RAGServiceError as exc:
            warnings.append(f"Retrieval indisponible: {exc}")
            logger.warning("RAG retrieval fallback triggered: %s", exc)

        context_block = "\n\n---\n\n".join(context_parts) if context_parts else "Aucun contexte retrouvé."
        user_context = self._build_user_context(user)

        prompt = (
            "Tu es un assistant clinique nutritionnel pour BiomeX.\n"
            "Tu dois fournir des recommandations prudentes, exploitables et expliquees.\n"
            "Contraintes:\n"
            "- N'invente pas de faits non présents dans le contexte.\n"
            "- Signale clairement les incertitudes.\n"
            "- Ne remplace pas un avis médical.\n"
            "- Réponds en français.\n\n"
            f"Contexte utilisateur:\n{user_context}\n\n"
            f"Connaissances récupérées:\n{context_block}\n\n"
            f"Question utilisateur: {question_clean}\n\n"
            "Réponds en 4 sections:\n"
            "1) Synthèse clinique courte\n"
            "2) Recommandations alimentaires concrètes (3 à 5)\n"
            "3) Précautions / limites\n"
            "4) Sources utilisées (liste courte)\n"
        )
        try:
            answer = self._generate_answer(prompt)
        except RAGServiceError as exc:
            warnings.append(f"Generation indisponible: {exc}")
            logger.warning("RAG generation fallback triggered: %s", exc)
            answer = self._build_fallback_answer(question=question_clean, sources=sources)

        return {
            "answer": answer,
            "sources": sources,
            "retrieved_count": len(sources),
            "namespace": namespace_value,
            "degraded": bool(warnings),
            "warnings": warnings,
        }
