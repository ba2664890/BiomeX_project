import csv
import hashlib
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

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
        self.hf_generation_url = settings.RAG_HF_GENERATION_URL

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

    def _embed_text(self, text: str) -> list[float]:
        self._validate_rag_config()
        if not text.strip():
            raise RAGServiceError("Le texte à encoder est vide.")

        url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{self.hf_embedding_model}"
        payload = {
            "inputs": text,
            "options": {"wait_for_model": True},
        }
        response = requests.post(url, headers=self._hf_headers(), json=payload, timeout=90)
        if response.status_code >= 400:
            raise RAGServiceError(
                f"Hugging Face embedding error ({response.status_code}): {response.text}"
            )
        data = response.json()
        if isinstance(data, dict) and data.get("error"):
            raise RAGServiceError(f"Hugging Face embedding error: {data['error']}")

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

    def _generate_answer(self, prompt: str) -> str:
        self._validate_rag_config()
        generation_url = self.hf_generation_url or f"https://api-inference.huggingface.co/models/{self.hf_generation_model}"
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 512,
                "temperature": 0.2,
                "return_full_text": False,
            },
            "options": {"wait_for_model": True},
        }
        response = requests.post(
            generation_url,
            headers=self._hf_headers(),
            json=payload,
            timeout=180,
        )
        if response.status_code >= 400:
            raise RAGServiceError(
                f"Hugging Face generation error ({response.status_code}): {response.text}"
            )
        data = response.json()
        if isinstance(data, dict) and data.get("error"):
            raise RAGServiceError(f"Hugging Face generation error: {data['error']}")
        if isinstance(data, list) and data and isinstance(data[0], dict) and data[0].get("generated_text"):
            return data[0]["generated_text"].strip()
        if isinstance(data, dict) and data.get("generated_text"):
            return str(data["generated_text"]).strip()
        if isinstance(data, str):
            return data.strip()
        raise RAGServiceError("Format de réponse génération inattendu.")

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

        query_vector = self._embed_text(question_clean)
        matches = self._query_vectors(query_vector=query_vector, top_k=top_k_value, namespace=namespace_value)

        context_parts = []
        sources = []
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
        answer = self._generate_answer(prompt)
        return {
            "answer": answer,
            "sources": sources,
            "retrieved_count": len(sources),
            "namespace": namespace_value,
        }
