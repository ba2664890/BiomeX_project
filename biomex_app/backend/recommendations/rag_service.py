"""
BiomeX RAG Service — v2
=======================
Améliorations majeures vs v1 :

1. QUERY EXPANSION         — La question brute est enrichie en 3 variantes sémantiques
                             avant l'embedding, ce qui multiplie les axes de recherche
                             et réduit les faux négatifs de retrieval.

2. DÉTECTION D'INTENTION   — Classification locale (regex + heuristiques) AVANT toute
                             requête réseau : simple / clinique / urgence / hors-scope.
                             Permet d'adapter le prompt, le top_k, et le ton de la réponse.

3. RERANKING MMR            — Après retrieval Pinecone, on applique un Maximal Marginal
                             Relevance pour maximiser pertinence ET diversité des chunks,
                             évitant les contextes redondants qui noient les informations clés.

4. PROMPT ADAPTATIF         — Cinq templates de prompt selon l'intention détectée :
                             factuel · nutritionnel · clinique · microbiome · hors-scope.
                             Chacun a ses instructions de format, de ton et de précautions.

5. INTERPRÉTATION CLINIQUE  — Le contexte utilisateur est enrichi avec une interprétation
                             lisible des scores microbiome (pas juste des chiffres bruts),
                             le niveau de risque et les signaux d'alerte.

6. CHUNKING AMÉLIORÉ        — Fenêtrage avec chevauchement pour CSV/documents,
                             déduplication par hash avant upsert Pinecone.

7. FALLBACK INTELLIGENT     — Le fallback génère une réponse partielle structurée
                             à partir des chunks récupérés, même sans LLM disponible.

8. MÉTRIQUES DE CONFIANCE   — Chaque réponse inclut un score de confiance calculé
                             depuis les scores Pinecone des chunks utilisés.

9. GESTION MÉMOIRE SESSION  — Support d'un historique de conversation court (3 tours)
                             injecté dans le prompt pour les échanges multi-tours.

10. TIMEOUT ADAPTATIF       — Les timeouts s'ajustent à la complexité de la requête
                             (question simple → 60s, analyse clinique → 240s).
"""

import csv
import hashlib
import logging
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import requests
from django.conf import settings

from microbiome.models import MicrobiomeAnalysis
from nutrition.models import FoodItem, FoodSubstitution, Recipe, RecipeIngredient

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class RAGServiceError(Exception):
    """Erreur générique du service RAG."""


class RAGConfigurationError(RAGServiceError):
    """Configuration RAG manquante ou invalide."""


# ---------------------------------------------------------------------------
# Types de données
# ---------------------------------------------------------------------------

class QueryIntent(Enum):
    """Intention détectée dans la question de l'utilisateur."""
    FACTUAL       = "factual"       # Question de fait simple (calories, définition…)
    NUTRITIONAL   = "nutritional"   # Conseil alimentaire / substitution
    CLINICAL      = "clinical"      # Symptômes, pathologie, diagnostic différentiel
    MICROBIOME    = "microbiome"    # Séquençage, dysbiose, bactéries spécifiques
    EMERGENCY     = "emergency"     # Signal d'urgence médicale
    OUT_OF_SCOPE  = "out_of_scope"  # Hors domaine BiomeX


@dataclass
class KnowledgeChunk:
    chunk_id: str
    text: str
    metadata: dict[str, Any]


@dataclass
class RankedChunk:
    chunk: KnowledgeChunk
    pinecone_score: float
    mmr_score: float = 0.0


@dataclass
class ConversationTurn:
    role: str   # "user" | "assistant"
    content: str


@dataclass
class RAGResponse:
    answer: str
    sources: list[dict[str, Any]]
    intent: str
    confidence: float           # 0.0–1.0 basé sur les scores Pinecone
    retrieved_count: int
    namespace: str
    degraded: bool
    warnings: list[str]
    response_time_ms: int


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

# Seuils de score Pinecone pour le calcul de confiance
_CONFIDENCE_HIGH   = 0.85
_CONFIDENCE_MEDIUM = 0.70
_CONFIDENCE_LOW    = 0.50

# Mots-clés pour la détection d'intention (ordre décroissant de priorité)
_EMERGENCY_KEYWORDS = [
    r"\bsang\b", r"\bhémorragie\b", r"\bvomissements?\b.{0,20}\bsang\b",
    r"\bdouleur\b.{0,20}\bviolente\b", r"\bperte de conscience\b",
    r"\burgences?\b", r"\bappeler.{0,10}médecin\b",
]
_CLINICAL_KEYWORDS = [
    r"\bsymptômes?\b", r"\bdouleur\b", r"\bchronique\b", r"\bdiagnosti",
    r"\bcrohn\b", r"\brch\b", r"\bmici\b", r"\bsci\b", r"\bcôlon irritable\b",
    r"\binflammation\b", r"\bhelicobacter\b", r"\bh\.?pylori\b",
    r"\bparasite\b", r"\bdiabète\b", r"\bcancer\b", r"\bulcère\b",
    r"\bdysbiose\b", r"\bperméabilité\b", r"\ble médecin\b",
]
_MICROBIOME_KEYWORDS = [
    r"\bmicrobiome\b", r"\bmicrobiote\b", r"\bséquençage\b", r"\b16s\b",
    r"\bbactéries?\b", r"\bfirmicutes\b", r"\bbacteroidetes\b",
    r"\bakkermansia\b", r"\bfaecalibacterium\b", r"\blactobacillus\b",
    r"\bbifidobacterium\b", r"\bdiversité.{0,15}microb\b",
    r"\bindex de shannon\b", r"\bscore.{0,10}microbiome\b",
    r"\bflore intestinale\b", r"\bmétagénomique\b",
]
_NUTRITIONAL_KEYWORDS = [
    r"\brecette\b", r"\baliment\b", r"\bmanger\b", r"\bnourritur\b",
    r"\bprotéine\b", r"\bfibre\b", r"\bgluci\b", r"\blipi\b",
    r"\bcalorie\b", r"\bsubstitut\b", r"\béviter\b.{0,20}\bmanger\b",
    r"\brecommandation.{0,15}alimentaire\b", r"\brégime\b", r"\bprobiotique\b",
    r"\bprébiotique\b", r"\bferment\b", r"\bniébé\b", r"\bmil\b",
    r"\bbissap\b", r"\bmoringa\b", r"\bgombo\b",
]


# ---------------------------------------------------------------------------
# Service principal
# ---------------------------------------------------------------------------

class BiomexRAGService:
    """
    Service RAG BiomeX v2 — Retrieval-Augmented Generation adaptatif
    pour la nutrition, le microbiome et la santé digestive en Afrique de l'Ouest.
    """

    def __init__(self) -> None:
        self.hf_api_token            = settings.RAG_HF_API_TOKEN
        self.hf_generation_model     = settings.RAG_HF_GENERATION_MODEL
        self.hf_embedding_model      = settings.RAG_HF_EMBEDDING_MODEL
        self.hf_generation_url       = self._normalize_hf_url(settings.RAG_HF_GENERATION_URL)
        self.hf_embedding_url        = self._normalize_hf_url(settings.RAG_HF_EMBEDDING_URL)
        self.hf_router_base_url      = self._normalize_router_url(settings.RAG_HF_ROUTER_BASE_URL)
        self.hf_router_provider      = settings.RAG_HF_ROUTER_PROVIDER
        self.hf_fallback_models      = self._parse_model_list(
            getattr(settings, "RAG_HF_FALLBACK_GENERATION_MODELS", "")
        )

        self.pinecone_api_key        = settings.RAG_PINECONE_API_KEY
        self.pinecone_index_host     = self._normalize_pinecone_host(settings.RAG_PINECONE_INDEX_HOST)
        self.default_namespace       = settings.RAG_PINECONE_NAMESPACE
        self.default_top_k           = settings.RAG_DEFAULT_TOP_K
        self.max_context_chars       = settings.RAG_MAX_CONTEXT_CHARS

        # Namespaces à interroger pour chaque type de contenu
        self._namespaces = [
            self.default_namespace,
            "biomex-documents",
            "biomex-microbiome",
            "biomex-nutrition",
        ]

    # ------------------------------------------------------------------
    # Normalisation d'URLs
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_pinecone_host(host: str) -> str:
        v = (host or "").strip()
        if not v:
            return v
        if not v.startswith(("http://", "https://")):
            return f"https://{v.rstrip('/')}"
        return v.rstrip("/")

    @staticmethod
    def _normalize_hf_url(url: str) -> str:
        v = (url or "").strip()
        if not v:
            return ""
        if not v.startswith(("http://", "https://")):
            return f"https://{v}"
        return v

    @staticmethod
    def _normalize_router_url(base: str) -> str:
        v = (base or "").strip()
        if not v:
            return "https://router.huggingface.co"
        if not v.startswith(("http://", "https://")):
            return f"https://{v.rstrip('/')}"
        return v.rstrip("/")

    @staticmethod
    def _parse_model_list(raw: Any) -> list[str]:
        if isinstance(raw, str):
            items = [i.strip() for i in raw.split(",")]
        elif isinstance(raw, (list, tuple, set)):
            items = [str(i).strip() for i in raw]
        else:
            items = []
        seen: list[str] = []
        for m in items:
            if m and m not in seen:
                seen.append(m)
        return seen

    # ------------------------------------------------------------------
    # Détection d'intention
    # ------------------------------------------------------------------

    @staticmethod
    def _match_any(text: str, patterns: list[str]) -> bool:
        t = text.lower()
        return any(re.search(p, t) for p in patterns)

    def detect_intent(self, question: str) -> QueryIntent:
        """
        Classifie la question en une intention parmi les 6 catégories.
        Ordre de priorité : urgence > clinique > microbiome > nutritionnel > factuel > hors-scope.
        """
        if self._match_any(question, _EMERGENCY_KEYWORDS):
            return QueryIntent.EMERGENCY
        if self._match_any(question, _CLINICAL_KEYWORDS):
            return QueryIntent.CLINICAL
        if self._match_any(question, _MICROBIOME_KEYWORDS):
            return QueryIntent.MICROBIOME
        if self._match_any(question, _NUTRITIONAL_KEYWORDS):
            return QueryIntent.NUTRITIONAL

        # Questions courtes (< 8 mots) sans mot-clé spécifique → factuel
        word_count = len(question.split())
        if word_count <= 8:
            return QueryIntent.FACTUAL

        return QueryIntent.OUT_OF_SCOPE

    # ------------------------------------------------------------------
    # Query expansion — génère 3 formulations alternatives de la question
    # ------------------------------------------------------------------

    _EXPANSION_TEMPLATES = {
        QueryIntent.FACTUAL: [
            "{q}",
            "Quelle est la valeur nutritive de {q}",
            "Information sur {q}",
        ],
        QueryIntent.NUTRITIONAL: [
            "{q}",
            "Recommandations alimentaires pour {q}",
            "Aliments bénéfiques liés à {q} pour la santé digestive",
        ],
        QueryIntent.CLINICAL: [
            "{q}",
            "Protocole clinique et microbiome pour {q}",
            "Prévention et symptômes digestifs {q} en Afrique de l'Ouest",
        ],
        QueryIntent.MICROBIOME: [
            "{q}",
            "Analyse du microbiome intestinal {q}",
            "Dysbiose bactéries signature {q}",
        ],
        QueryIntent.EMERGENCY: [
            "{q}",
            "Symptômes urgents digestifs {q}",
        ],
        QueryIntent.OUT_OF_SCOPE: [
            "{q}",
        ],
    }

    def _expand_query(self, question: str, intent: QueryIntent) -> list[str]:
        templates = self._EXPANSION_TEMPLATES.get(intent, ["{q}"])
        variants: list[str] = []
        for tpl in templates:
            v = tpl.format(q=question).strip()
            if v not in variants:
                variants.append(v)
        return variants

    # ------------------------------------------------------------------
    # Reranking MMR (Maximal Marginal Relevance)
    # ------------------------------------------------------------------

    @staticmethod
    def _dot_product(a: list[float], b: list[float]) -> float:
        if len(a) != len(b):
            return 0.0
        return sum(x * y for x, y in zip(a, b))

    @staticmethod
    def _norm(v: list[float]) -> float:
        return sum(x * x for x in v) ** 0.5

    def _cosine(self, a: list[float], b: list[float]) -> float:
        na, nb = self._norm(a), self._norm(b)
        if na == 0 or nb == 0:
            return 0.0
        return self._dot_product(a, b) / (na * nb)

    def _mmr_rerank(
        self,
        candidates: list[tuple[KnowledgeChunk, float, list[float]]],
        top_k: int,
        lambda_mmr: float = 0.6,
    ) -> list[RankedChunk]:
        """
        Maximal Marginal Relevance :
        Score_MMR = λ * relevance - (1-λ) * max_similarity_to_selected

        lambda_mmr élevé → favorise la pertinence
        lambda_mmr faible → favorise la diversité
        """
        if not candidates:
            return []

        selected: list[RankedChunk] = []
        selected_embeddings: list[list[float]] = []
        remaining = list(candidates)

        while remaining and len(selected) < top_k:
            best_idx = -1
            best_score = float("-inf")

            for i, (chunk, rel_score, embedding) in enumerate(remaining):
                # Similarité max avec les chunks déjà sélectionnés
                if selected_embeddings:
                    max_sim = max(self._cosine(embedding, e) for e in selected_embeddings)
                else:
                    max_sim = 0.0

                mmr = lambda_mmr * rel_score - (1 - lambda_mmr) * max_sim

                if mmr > best_score:
                    best_score = mmr
                    best_idx = i

            if best_idx == -1:
                break

            chunk, rel_score, embedding = remaining.pop(best_idx)
            selected.append(RankedChunk(chunk=chunk, pinecone_score=rel_score, mmr_score=best_score))
            selected_embeddings.append(embedding)

        return selected

    # ------------------------------------------------------------------
    # Construction du contexte utilisateur enrichi
    # ------------------------------------------------------------------

    @staticmethod
    def _interpret_score(score: float | None, label: str) -> str:
        """Traduit un score numérique en interprétation clinique lisible."""
        if score is None:
            return f"{label}: non disponible"
        if score >= 80:
            level = "excellent"
        elif score >= 65:
            level = "bon"
        elif score >= 45:
            level = "modéré — à surveiller"
        elif score >= 25:
            level = "faible — intervention recommandée"
        else:
            level = "critique — consultation urgente"
        return f"{label}: {score:.0f}/100 ({level})"

    @staticmethod
    def _risk_summary(analysis: Any) -> str:
        """Génère un résumé des signaux de risque à partir de l'analyse microbiome."""
        if not analysis:
            return "Aucune analyse microbiome disponible."
        flags: list[str] = []
        if analysis.diversity_score is not None and analysis.diversity_score < 40:
            flags.append("faible diversité microbienne")
        if analysis.inflammation_score is not None and analysis.inflammation_score > 70:
            flags.append("inflammation intestinale élevée")
        if analysis.overall_score is not None and analysis.overall_score < 45:
            flags.append("microbiome globalement déséquilibré")
        if not flags:
            return "Aucun signal d'alerte majeur détecté."
        return "Signaux d'alerte : " + ", ".join(flags) + "."

    def _build_user_context(self, user: Any) -> str:
        """
        Construit le bloc de contexte utilisateur avec interprétation clinique
        des scores microbiome, profil alimentaire et signaux de risque.
        """
        analysis = (
            MicrobiomeAnalysis.objects.filter(user=user, status="completed")
            .order_by("-sample_date")
            .first()
        )

        profile_lines = [
            f"Âge : {user.age if user.age is not None else 'N/A'}",
            f"Localisation : {user.city or 'N/A'}, {user.country or 'N/A'}",
            f"Préférences alimentaires : {', '.join(user.dietary_preferences) if user.dietary_preferences else 'non renseignées'}",
            f"Allergies : {', '.join(user.allergies) if user.allergies else 'aucune connue'}",
            f"IMC : {user.bmi if user.bmi is not None else 'N/A'}",
        ]

        microbiome_lines: list[str] = []
        if analysis:
            microbiome_lines = [
                self._interpret_score(analysis.overall_score, "Score microbiome global"),
                self._interpret_score(analysis.diversity_score, "Diversité microbienne"),
                self._interpret_score(
                    100 - analysis.inflammation_score if analysis.inflammation_score is not None else None,
                    "Équilibre inflammatoire"
                ),
                self._risk_summary(analysis),
                f"Résumé analyse : {analysis.summary or 'non disponible'}",
            ]
        else:
            microbiome_lines = ["Aucune analyse microbiome complétée."]

        return (
            "=== PROFIL UTILISATEUR ===\n"
            + "\n".join(profile_lines)
            + "\n\n=== DONNÉES MICROBIOME ===\n"
            + "\n".join(microbiome_lines)
        )

    # ------------------------------------------------------------------
    # Prompts adaptatifs selon l'intention
    # ------------------------------------------------------------------

    _SYSTEM_INSTRUCTIONS = {
        QueryIntent.FACTUAL: (
            "Tu es l'assistant santé de BiomeX. "
            "La question est simple et factuelle. "
            "Réponds de façon DIRECTE, CONCISE et NATURELLE en 2–4 phrases maximum. "
            "Pas de structure complexe, pas de sections numérotées. "
            "Si la valeur exacte est dans le contexte, cite-la précisément. "
            "Termine éventuellement par une note pratique courte."
        ),
        QueryIntent.NUTRITIONAL: (
            "Tu es l'assistant nutrition de BiomeX, expert en alimentation ouest-africaine. "
            "Structure ta réponse ainsi :\n"
            "• Conseil principal (1–2 phrases directes)\n"
            "• 3 à 5 aliments concrets recommandés avec leur bénéfice microbiomique\n"
            "• 1 substitution pratique si pertinent\n"
            "• Note : adapte aux ingrédients locaux sénégalais quand c'est possible (mil, niébé, bissap, gombo, moringa…).\n"
            "Sois précis, pratique et ancré dans le contexte alimentaire local. "
            "Rappelle que tes conseils ne remplacent pas un suivi diététique professionnel."
        ),
        QueryIntent.CLINICAL: (
            "Tu es l'assistant clinique de BiomeX, spécialisé en gastroentérologie préventive. "
            "Structure ta réponse :\n"
            "1. Synthèse clinique courte (lien microbiome-pathologie)\n"
            "2. Recommandations concrètes (alimentation, probiotiques, hygiène de vie)\n"
            "3. Signaux d'alerte qui nécessitent une consultation médicale\n"
            "4. Limites : rappelle que BiomeX ne remplace pas le diagnostic médical.\n"
            "Base-toi UNIQUEMENT sur les connaissances récupérées. "
            "Si l'information est absente du contexte, dis-le clairement sans inventer."
        ),
        QueryIntent.MICROBIOME: (
            "Tu es l'expert microbiome de BiomeX. "
            "Structure ta réponse :\n"
            "1. Explication scientifique accessible (mécanisme microbiomique)\n"
            "2. Interprétation des données du profil utilisateur si disponibles\n"
            "3. Actions concrètes pour améliorer le microbiome\n"
            "4. Contexte africain : précise si les données de référence sont issues de populations occidentales "
            "et comment les adapter.\n"
            "Utilise un langage accessible mais précis. "
            "Cite les bactéries spécifiques quand c'est pertinent."
        ),
        QueryIntent.EMERGENCY: (
            "Tu es l'assistant de triage de BiomeX. "
            "La question contient des signaux d'urgence médicale potentielle. "
            "Ta réponse DOIT :\n"
            "1. Recommander IMMÉDIATEMENT de consulter un médecin ou appeler les urgences\n"
            "2. Ne PAS tenter de diagnostiquer ou rassurer indûment\n"
            "3. Rester calme et factuel\n"
            "N'entre pas dans les détails nutritionnels ou microbiomiques dans ce contexte."
        ),
        QueryIntent.OUT_OF_SCOPE: (
            "Tu es l'assistant de BiomeX, spécialisé en santé digestive, microbiome et nutrition. "
            "La question semble hors de ton domaine d'expertise. "
            "Réponds poliment que tu n'es pas en mesure d'aider sur ce sujet spécifique, "
            "explique brièvement ce sur quoi tu peux aider, "
            "et propose de reformuler si la question a un lien avec la nutrition ou le microbiome."
        ),
    }

    def _build_prompt(
        self,
        question: str,
        user_context: str,
        context_block: str,
        intent: QueryIntent,
        conversation_history: list[ConversationTurn] | None = None,
    ) -> str:
        """
        Construit le prompt final avec :
        - Instructions système adaptées à l'intention
        - Historique de conversation (max 3 tours)
        - Contexte utilisateur enrichi
        - Chunks récupérés
        - Question courante
        """
        system_instr = self._SYSTEM_INSTRUCTIONS.get(
            intent, self._SYSTEM_INSTRUCTIONS[QueryIntent.FACTUAL]
        )

        # Historique de conversation (max 3 tours = 6 messages)
        history_block = ""
        if conversation_history:
            recent = conversation_history[-6:]
            turns = []
            for turn in recent:
                role_label = "Utilisateur" if turn.role == "user" else "Assistant"
                turns.append(f"{role_label} : {turn.content}")
            if turns:
                history_block = (
                    "\n--- Historique récent de la conversation ---\n"
                    + "\n".join(turns)
                    + "\n"
                )

        return (
            f"{system_instr}\n\n"
            "Règle absolue : réponds UNIQUEMENT en français.\n"
            "Règle absolue : base-toi UNIQUEMENT sur les connaissances récupérées ci-dessous.\n\n"
            f"{history_block}"
            f"--- Profil et données de l'utilisateur ---\n{user_context}\n\n"
            f"--- Connaissances récupérées ---\n{context_block}\n\n"
            f"--- Question ---\n{question}\n\n"
            "Ta réponse :"
        )

    # ------------------------------------------------------------------
    # Calcul du score de confiance
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_confidence(ranked_chunks: list[RankedChunk]) -> float:
        """
        Score de confiance basé sur les scores Pinecone des chunks utilisés.
        Retourne 0.0 si aucun chunk disponible.
        """
        if not ranked_chunks:
            return 0.0
        scores = [rc.pinecone_score for rc in ranked_chunks]
        avg = sum(scores) / len(scores)
        # Normalise entre 0 et 1 (les scores Pinecone cosine sont déjà dans [-1, 1])
        return max(0.0, min(1.0, avg))

    # ------------------------------------------------------------------
    # Fallback intelligent basé sur les chunks
    # ------------------------------------------------------------------

    def _build_smart_fallback(
        self,
        question: str,
        ranked_chunks: list[RankedChunk],
        intent: QueryIntent,
        user_context: str,
    ) -> str:
        """
        Génère une réponse partielle structurée à partir des chunks disponibles
        quand le LLM est inaccessible. Bien meilleure que la réponse codée en dur v1.
        """
        if not ranked_chunks:
            return (
                "Le service de génération IA est temporairement indisponible "
                "et aucune connaissance pertinente n'a été trouvée pour ta question.\n\n"
                "Réessaie dans quelques minutes. Si ton problème est urgent, "
                "consulte un professionnel de santé."
            )

        # Extrait les snippets les plus pertinents
        snippets: list[str] = []
        for rc in ranked_chunks[:3]:
            text = rc.chunk.text.strip()
            if text:
                snippets.append(f"• {text[:400]}{'…' if len(text) > 400 else ''}")

        sources_block = "\n".join(snippets)

        if intent == QueryIntent.EMERGENCY:
            return (
                "⚠️ Le service IA est indisponible, mais ta question contient des "
                "signaux d'urgence médicale. Consulte immédiatement un médecin ou "
                "appelle les services d'urgence."
            )

        return (
            "Le service de génération IA est temporairement indisponible. "
            "Voici les informations pertinentes trouvées dans notre base de connaissances :\n\n"
            f"{sources_block}\n\n"
            "Pour une analyse personnalisée complète, réessaie dans quelques minutes.\n"
            "Ces informations ne remplacent pas un avis médical professionnel."
        )

    # ------------------------------------------------------------------
    # HTTP helpers
    # ------------------------------------------------------------------

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
    def _trim(text: str, max_len: int = 800) -> str:
        t = (text or "").replace("\n", " ").strip()
        return t if len(t) <= max_len else f"{t[:max_len]}…[truncated]"

    def _hf_post_json(
        self,
        *,
        url: str,
        payload: dict[str, Any],
        timeout: int,
        error_prefix: str,
    ) -> Any:
        try:
            resp = requests.post(url, headers=self._hf_headers(), json=payload, timeout=timeout)
        except requests.RequestException as exc:
            logger.warning("[HF] network error | %s | url=%s | %s", error_prefix, url, exc)
            raise RAGServiceError(f"{error_prefix} [network]: {exc}") from exc

        if resp.status_code >= 400:
            body = self._trim(resp.text)
            logger.warning("[HF] %s | status=%s | %s", error_prefix, resp.status_code, body)
            raise RAGServiceError(f"{error_prefix} ({resp.status_code}): {body}")

        try:
            data = resp.json()
        except ValueError as exc:
            raise RAGServiceError(f"{error_prefix}: réponse JSON invalide.") from exc

        if isinstance(data, dict) and data.get("error"):
            raise RAGServiceError(f"{error_prefix}: {self._trim(str(data['error']))}")

        return data

    # ------------------------------------------------------------------
    # Embedding
    # ------------------------------------------------------------------

    @staticmethod
    def _mean_pool(matrix: list[list[float]]) -> list[float]:
        if not matrix:
            return []
        dims = len(matrix[0])
        sums = [sum(float(row[i]) for row in matrix) for i in range(dims)]
        return [s / len(matrix) for s in sums]

    def _parse_embedding_response(self, data: Any) -> list[float]:
        if isinstance(data, dict):
            rows = data.get("data")
            if isinstance(rows, list) and rows and isinstance(rows[0], dict):
                emb = rows[0].get("embedding")
                if isinstance(emb, list) and emb and isinstance(emb[0], (int, float)):
                    return [float(x) for x in emb]
            emb = data.get("embedding")
            if isinstance(emb, list) and emb and isinstance(emb[0], (int, float)):
                return [float(x) for x in emb]
        return []

    def _embed_batch(self, texts: list[str]) -> list[list[float]]:
        self._validate_rag_config()
        valid = [t.strip() for t in texts if t.strip()]
        if not valid:
            return []

        attempts = []
        if self.hf_embedding_url:
            attempts.append((
                "custom endpoint",
                self.hf_embedding_url,
                {"inputs": valid, "options": {"wait_for_model": True}},
            ))
        attempts += [
            (
                "hf-inference pipeline",
                f"{self.hf_router_base_url}/pipeline/feature-extraction/{self.hf_embedding_model}",
                {"inputs": valid, "options": {"wait_for_model": True}},
            ),
            (
                "router pipeline",
                f"{self.hf_router_base_url}/hf-inference/models/{self.hf_embedding_model}/pipeline/feature-extraction",
                {"inputs": valid, "options": {"wait_for_model": True}},
            ),
        ]

        errors: list[str] = []
        data: Any = None
        for label, url, payload in attempts:
            try:
                data = self._hf_post_json(url=url, payload=payload, timeout=120, error_prefix=f"Embedding [{label}]")
                break
            except RAGServiceError as exc:
                errors.append(str(exc))

        if data is None:
            raise RAGServiceError(" | ".join(errors) or "Embedding indisponible.")

        # Shapes : 2D [batch x dims] ou 3D [batch x tokens x dims]
        if isinstance(data, list) and data:
            first = data[0]
            if isinstance(first, list) and first:
                if isinstance(first[0], (int, float)):
                    # 2D — déjà correct
                    return [[float(x) for x in row] for row in data]
                if isinstance(first[0], list):
                    # 3D — mean pool sur la dimension tokens
                    return [self._mean_pool(seq) for seq in data]

        parsed = self._parse_embedding_response(data)
        if parsed:
            return [parsed]
        return []

    def _embed_text(self, text: str) -> list[float]:
        results = self._embed_batch([text])
        return results[0] if results else []

    # ------------------------------------------------------------------
    # Génération
    # ------------------------------------------------------------------

    def _generation_candidates(self) -> list[str]:
        primary = (self.hf_generation_model or "").strip()
        candidates: list[str] = [primary] if primary else []
        for m in self.hf_fallback_models:
            if m and m not in candidates:
                candidates.append(m)
        return candidates

    def _router_model_name(self, model: str) -> str:
        provider = (self.hf_router_provider or "").strip()
        if provider and ":" not in model:
            return f"{model}:{provider}"
        return model

    @staticmethod
    def _is_model_error(text: str) -> bool:
        t = text.lower()
        return any(k in t for k in [
            '"model_not_found"', "'model_not_found'", "does not exist",
            '"model_not_supported"', "not supported by provider", "chat model",
        ])

    def _generate_answer(self, prompt: str, intent: QueryIntent) -> str:
        self._validate_rag_config()

        # Timeout adaptatif selon la complexité de la question
        timeout = {
            QueryIntent.FACTUAL: 60,
            QueryIntent.NUTRITIONAL: 120,
            QueryIntent.CLINICAL: 240,
            QueryIntent.MICROBIOME: 240,
            QueryIntent.EMERGENCY: 60,
            QueryIntent.OUT_OF_SCOPE: 60,
        }.get(intent, 120)

        # max_tokens adaptatif
        max_tokens = {
            QueryIntent.FACTUAL: 256,
            QueryIntent.NUTRITIONAL: 512,
            QueryIntent.CLINICAL: 768,
            QueryIntent.MICROBIOME: 768,
            QueryIntent.EMERGENCY: 256,
            QueryIntent.OUT_OF_SCOPE: 256,
        }.get(intent, 512)

        errors: list[str] = []

        # Endpoint personnalisé en priorité
        if self.hf_generation_url:
            try:
                data = self._hf_post_json(
                    url=self.hf_generation_url,
                    payload={
                        "inputs": prompt,
                        "parameters": {
                            "max_new_tokens": max_tokens,
                            "temperature": 0.25,
                            "return_full_text": False,
                        },
                        "options": {"wait_for_model": True},
                    },
                    timeout=timeout,
                    error_prefix="Generation [custom endpoint]",
                )
                text = self._extract_generation_text(data)
                if text:
                    return text
            except RAGServiceError as exc:
                errors.append(str(exc))

        # Fallback sur les modèles HF Router
        for model in self._generation_candidates():
            router_model = self._router_model_name(model)
            attempts = [
                (
                    "chat completions",
                    f"{self.hf_router_base_url}/v1/chat/completions",
                    {
                        "model": router_model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": max_tokens,
                        "temperature": 0.25,
                    },
                ),
                (
                    "text-generation pipeline",
                    f"{self.hf_router_base_url}/pipeline/text-generation/{model}",
                    {
                        "inputs": prompt,
                        "parameters": {"max_new_tokens": max_tokens, "temperature": 0.25},
                    },
                ),
                (
                    "models direct",
                    f"{self.hf_router_base_url}/hf-inference/models/{model}",
                    {
                        "inputs": prompt,
                        "parameters": {
                            "max_new_tokens": max_tokens,
                            "temperature": 0.25,
                            "return_full_text": False,
                        },
                        "options": {"wait_for_model": True},
                    },
                ),
            ]

            skip_model = False
            for label, url, payload in attempts:
                try:
                    data = self._hf_post_json(
                        url=url, payload=payload,
                        timeout=timeout, error_prefix=f"Generation [{label}]"
                    )
                    text = self._extract_generation_text(data)
                    if text:
                        return text
                except RAGServiceError as exc:
                    error_text = str(exc)
                    errors.append(error_text)
                    if label == "chat completions" and self._is_model_error(error_text):
                        skip_model = True
                        break

            if skip_model:
                continue

        raise RAGServiceError(" | ".join(errors) or "Génération indisponible.")

    @staticmethod
    def _extract_generation_text(data: Any) -> str:
        if isinstance(data, dict):
            choices = data.get("choices")
            if isinstance(choices, list) and choices:
                choice = choices[0]
                if isinstance(choice, dict):
                    msg = choice.get("message")
                    if isinstance(msg, dict):
                        content = msg.get("content", "")
                        if isinstance(content, str):
                            return content.strip()
                        if isinstance(content, list):
                            parts = [
                                str(p.get("text", "")).strip()
                                for p in content
                                if isinstance(p, dict) and p.get("type") == "text"
                            ]
                            return "\n".join(p for p in parts if p)
                    choice_text = choice.get("text", "")
                    if isinstance(choice_text, str):
                        return choice_text.strip()
        if isinstance(data, list) and data and isinstance(data[0], dict):
            return str(data[0].get("generated_text", "")).strip()
        if isinstance(data, dict):
            return str(data.get("generated_text", "")).strip()
        if isinstance(data, str):
            return data.strip()
        return ""

    # ------------------------------------------------------------------
    # Pinecone
    # ------------------------------------------------------------------

    def _upsert_vectors(self, vectors: list[dict[str, Any]], namespace: str) -> None:
        if not vectors:
            return
        url = f"{self.pinecone_index_host}/vectors/upsert"
        try:
            resp = requests.post(
                url,
                headers=self._pinecone_headers(),
                json={"namespace": namespace, "vectors": vectors},
                timeout=120,
            )
        except requests.RequestException as exc:
            raise RAGServiceError(f"Pinecone upsert [network]: {exc}") from exc
        if resp.status_code >= 400:
            raise RAGServiceError(f"Pinecone upsert ({resp.status_code}): {resp.text}")

    def _query_vectors(
        self, vector: list[float], top_k: int, namespace: str
    ) -> list[dict[str, Any]]:
        url = f"{self.pinecone_index_host}/query"
        try:
            resp = requests.post(
                url,
                headers=self._pinecone_headers(),
                json={
                    "namespace": namespace,
                    "vector": vector,
                    "topK": top_k,
                    "includeMetadata": True,
                    "includeValues": True,   # nécessaire pour le MMR
                },
                timeout=60,
            )
        except requests.RequestException as exc:
            raise RAGServiceError(f"Pinecone query [network]: {exc}") from exc
        if resp.status_code >= 400:
            raise RAGServiceError(f"Pinecone query ({resp.status_code}): {resp.text}")
        try:
            data = resp.json()
        except ValueError as exc:
            raise RAGServiceError("Pinecone query: réponse JSON invalide.") from exc
        return data.get("matches", []) if isinstance(data, dict) else []

    # ------------------------------------------------------------------
    # Chunking
    # ------------------------------------------------------------------

    @staticmethod
    def _stable_chunk_id(prefix: str, text: str) -> str:
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:24]
        return f"{prefix}-{digest}"

    def _food_chunks(self) -> list[KnowledgeChunk]:
        chunks: list[KnowledgeChunk] = []
        for food in FoodItem.objects.filter(is_active=True).order_by("id"):
            # Enrichissement du texte avec des synonymes locaux et contexte
            text = (
                f"Aliment : {food.name}"
                + (f" ({food.name_local})" if food.name_local else "")
                + f"\nCatégorie : {food.get_category_display()}"
                + (f"\nDescription : {food.description}" if food.description else "")
                + f"\nValeurs nutritionnelles pour 100g :"
                + f"\n  Calories : {food.calories} kcal"
                + f"\n  Protéines : {food.proteins} g"
                + f"\n  Glucides : {food.carbs} g"
                + f"\n  Lipides : {food.fats} g"
                + f"\n  Fibres : {food.fiber} g"
                + f"\nBénéfices microbiomiques :"
                + f"\n  Score prébiotique : {food.prebiotic_score}/100"
                + f"\n  Probiotique : {'oui' if food.probiotic else 'non'}"
                + f"\n  Anti-inflammatoire : {'oui' if food.anti_inflammatory else 'non'}"
                + f"\nDisponibilité : {food.get_season_display()}"
            )
            chunks.append(KnowledgeChunk(
                chunk_id=self._stable_chunk_id("food", text),
                text=text,
                metadata={"source_type": "food_item", "food_id": food.id, "name": food.name},
            ))
        return chunks

    def _recipe_chunks(self) -> list[KnowledgeChunk]:
        chunks: list[KnowledgeChunk] = []
        recipe_map: dict[int, list[str]] = {}
        for rel in RecipeIngredient.objects.select_related("food", "recipe").all():
            recipe_map.setdefault(rel.recipe_id, []).append(
                f"{rel.quantity} de {rel.food.name}"
            )

        for recipe in Recipe.objects.filter(is_active=True).order_by("id"):
            ingredients = ", ".join(recipe_map.get(recipe.id, [])) or "non spécifiés"
            text = (
                f"Recette : {recipe.name}"
                + (f"\nDescription : {recipe.description}" if recipe.description else "")
                + f"\nDifficulté : {recipe.get_difficulty_display()}"
                + f"\nTemps de préparation : {recipe.prep_time} min | Cuisson : {recipe.cook_time} min"
                + f"\nPortions : {recipe.servings}"
                + f"\nScore microbiome : {recipe.microbiome_score}/100"
                + f"\nIngrédients : {ingredients}"
                + (f"\nTags : {', '.join(recipe.tags)}" if recipe.tags else "")
            )
            chunks.append(KnowledgeChunk(
                chunk_id=self._stable_chunk_id("recipe", text),
                text=text,
                metadata={"source_type": "recipe", "recipe_id": recipe.id, "name": recipe.name},
            ))
        return chunks

    def _substitution_chunks(self) -> list[KnowledgeChunk]:
        chunks: list[KnowledgeChunk] = []
        for sub in FoodSubstitution.objects.select_related("food_to_avoid", "food_to_prefer").all():
            text = (
                f"Substitution alimentaire recommandée par BiomeX :\n"
                f"À éviter : {sub.food_to_avoid.name}\n"
                f"À privilégier : {sub.food_to_prefer.name}\n"
                f"Raison : {sub.reason or 'non précisée'}\n"
                f"Impact sur le microbiome : {sub.impact_score}"
            )
            chunks.append(KnowledgeChunk(
                chunk_id=self._stable_chunk_id("sub", text),
                text=text,
                metadata={
                    "source_type": "food_substitution",
                    "avoid_food": sub.food_to_avoid.name,
                    "prefer_food": sub.food_to_prefer.name,
                },
            ))
        return chunks

    def _csv_chunks(
        self,
        csv_path: str,
        text_column: str | None = None,
        max_rows: int = 500,
        window_size: int = 1,
        overlap: int = 0,
    ) -> list[KnowledgeChunk]:
        """
        Chunking CSV avec fenêtrage optionnel et chevauchement.
        window_size=1 → comportement v1 (une ligne = un chunk).
        window_size>1 → regroupe N lignes avec chevauchement pour préserver le contexte.
        """
        path = Path(csv_path)
        if not path.exists():
            raise RAGServiceError(f"CSV introuvable : {csv_path}")

        rows_text: list[str] = []
        with path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader):
                if idx >= max_rows:
                    break
                if text_column and text_column in row:
                    text = str(row[text_column]).strip()
                else:
                    parts = [f"{k}: {v}" for k, v in row.items() if v not in (None, "")]
                    text = " | ".join(parts).strip()
                if text:
                    rows_text.append(text)

        chunks: list[KnowledgeChunk] = []
        step = max(1, window_size - overlap)
        for i in range(0, len(rows_text), step):
            window = rows_text[i: i + window_size]
            combined = "\n".join(window).strip()
            if not combined:
                continue
            chunk_id = self._stable_chunk_id(f"csv-{path.stem}", f"{i}-{combined}")
            chunks.append(KnowledgeChunk(
                chunk_id=chunk_id,
                text=combined,
                metadata={"source_type": "csv", "csv_file": path.name, "row_start": i},
            ))
        return chunks

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------

    def ingest_knowledge(
        self,
        source: str,
        namespace: str | None = None,
        csv_path: str | None = None,
        csv_text_column: str | None = None,
        csv_window_size: int = 1,
        csv_overlap: int = 0,
        custom_documents: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        self._validate_rag_config()
        ns = namespace or self.default_namespace

        if source == "nutrition_db":
            chunks = self._food_chunks() + self._recipe_chunks() + self._substitution_chunks()
        elif source == "csv":
            if not csv_path:
                raise RAGServiceError("csv_path requis pour source='csv'.")
            chunks = self._csv_chunks(
                csv_path=csv_path,
                text_column=csv_text_column,
                window_size=csv_window_size,
                overlap=csv_overlap,
            )
        elif source == "custom":
            chunks = []
            for doc in custom_documents or []:
                text = str(doc.get("text", "")).strip()
                if not text:
                    continue
                title = str(doc.get("title", "")).strip()
                composed = f"{title}\n{text}" if title else text
                meta = {"source_type": "custom", "title": title}
                meta.update(doc.get("metadata", {}))
                chunks.append(KnowledgeChunk(
                    chunk_id=self._stable_chunk_id("custom", composed),
                    text=composed,
                    metadata=meta,
                ))
        else:
            raise RAGServiceError(f"Source RAG non supportée : {source}")

        # Déduplique par chunk_id avant l'embedding
        seen_ids: set[str] = set()
        unique_chunks = []
        for c in chunks:
            if c.chunk_id not in seen_ids:
                seen_ids.add(c.chunk_id)
                unique_chunks.append(c)

        vectors: list[dict[str, Any]] = []
        total = 0
        batch_size = 32
        upsert_size = 100

        for i in range(0, len(unique_chunks), batch_size):
            batch = unique_chunks[i: i + batch_size]
            texts = [c.text for c in batch]
            try:
                embeddings = self._embed_batch(texts)
                for j, emb in enumerate(embeddings):
                    if j < len(batch) and emb:
                        vectors.append({
                            "id": batch[j].chunk_id,
                            "values": emb,
                            "metadata": {
                                **batch[j].metadata,
                                "text": batch[j].text[:3000],
                            },
                        })
                while len(vectors) >= upsert_size:
                    self._upsert_vectors(vectors[:upsert_size], ns)
                    total += upsert_size
                    vectors = vectors[upsert_size:]
            except RAGServiceError as exc:
                logger.warning("Erreur ingestion batch %d : %s", i // batch_size, exc)
                continue

        if vectors:
            self._upsert_vectors(vectors, ns)
            total += len(vectors)

        return {"source": source, "namespace": ns, "ingested_count": total}

    # ------------------------------------------------------------------
    # Validation config
    # ------------------------------------------------------------------

    def _validate_rag_config(self) -> None:
        required = {
            "RAG_HF_API_TOKEN": self.hf_api_token,
            "RAG_PINECONE_API_KEY": self.pinecone_api_key,
            "RAG_PINECONE_INDEX_HOST": self.pinecone_index_host,
        }
        missing = [k for k, v in required.items() if not v]
        if missing:
            raise RAGConfigurationError(f"Configuration manquante : {', '.join(missing)}")

        from urllib.parse import urlparse
        host = urlparse(self.pinecone_index_host).netloc.lower()
        if not host or "." not in host:
            raise RAGConfigurationError(
                "RAG_PINECONE_INDEX_HOST invalide. "
                "Utilise le FQDN de l'index Pinecone, ex: 'my-index-xxxx.svc.pinecone.io'."
            )

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    def health_status(self) -> dict[str, Any]:
        return {
            "hf_token_configured": bool(self.hf_api_token),
            "hf_generation_model": self.hf_generation_model,
            "hf_embedding_model": self.hf_embedding_model,
            "hf_router_base_url": self.hf_router_base_url,
            "hf_router_provider": self.hf_router_provider or None,
            "hf_fallback_models": self.hf_fallback_models,
            "hf_custom_generation_url": self.hf_generation_url or None,
            "hf_custom_embedding_url": self.hf_embedding_url or None,
            "pinecone_configured": bool(self.pinecone_api_key and self.pinecone_index_host),
            "pinecone_index_host": self.pinecone_index_host,
            "pinecone_namespace": self.default_namespace,
            "default_top_k": self.default_top_k,
        }

    # ------------------------------------------------------------------
    # Point d'entrée principal
    # ------------------------------------------------------------------

    def answer_question(
        self,
        user: Any,
        question: str,
        top_k: int | None = None,
        namespace: str | None = None,
        conversation_history: list[ConversationTurn] | None = None,
    ) -> RAGResponse:
        """
        Pipeline complet :
        1. Détection d'intention
        2. Query expansion (3 variantes)
        3. Retrieval multi-namespace avec query expansion
        4. Reranking MMR
        5. Construction du prompt adaptatif
        6. Génération avec timeout adaptatif
        7. Calcul de confiance et retour structuré
        """
        self._validate_rag_config()
        t0 = time.monotonic()

        question_clean = (question or "").strip()
        if not question_clean:
            raise RAGServiceError("La question est vide.")

        ns = namespace or self.default_namespace
        k = top_k or self.default_top_k
        warnings: list[str] = []

        # 1. Détection d'intention
        intent = self.detect_intent(question_clean)
        logger.info("[RAG] intent=%s | question=%s", intent.value, question_clean[:80])

        # Ajuste top_k selon la complexité
        effective_k = k
        if intent in (QueryIntent.CLINICAL, QueryIntent.MICROBIOME):
            effective_k = max(k, 8)   # plus de contexte pour les questions complexes
        elif intent == QueryIntent.FACTUAL:
            effective_k = min(k, 4)   # moins de bruit pour les questions simples

        # 2. Query expansion
        query_variants = self._expand_query(question_clean, intent)

        # 3. Retrieval multi-namespace + multi-query
        all_matches: list[tuple[KnowledgeChunk, float, list[float]]] = []
        seen_chunk_ids: set[str] = set()

        namespaces_to_search = [ns]
        if ns == self.default_namespace:
            for extra_ns in self._namespaces:
                if extra_ns not in namespaces_to_search:
                    namespaces_to_search.append(extra_ns)

        for variant in query_variants:
            try:
                query_vector = self._embed_text(variant)
                if not query_vector:
                    warnings.append(f"Embedding vide pour la variante : {variant[:50]}")
                    continue

                for search_ns in namespaces_to_search:
                    try:
                        matches = self._query_vectors(
                            vector=query_vector,
                            top_k=effective_k,
                            namespace=search_ns,
                        )
                        for m in matches:
                            match_id = m.get("id", "")
                            if match_id in seen_chunk_ids:
                                continue
                            seen_chunk_ids.add(match_id)
                            meta = m.get("metadata") or {}
                            text = str(meta.get("text", "")).strip()
                            if not text:
                                continue
                            chunk = KnowledgeChunk(
                                chunk_id=match_id,
                                text=text,
                                metadata=meta,
                            )
                            # Récupère le vecteur Pinecone pour le MMR
                            pinecone_embedding = m.get("values") or []
                            all_matches.append((chunk, m.get("score", 0.0), pinecone_embedding))

                    except RAGServiceError as exc:
                        warnings.append(f"Namespace '{search_ns}' indisponible : {exc}")

            except RAGServiceError as exc:
                warnings.append(f"Embedding indisponible pour variante '{variant[:50]}' : {exc}")

        # 4. Reranking MMR
        ranked: list[RankedChunk] = []
        if all_matches:
            # lambda_mmr plus faible pour les questions cliniques → plus de diversité
            lambda_mmr = 0.5 if intent in (QueryIntent.CLINICAL, QueryIntent.MICROBIOME) else 0.65
            ranked = self._mmr_rerank(all_matches, top_k=effective_k, lambda_mmr=lambda_mmr)

        # 5. Construction du contexte
        context_parts: list[str] = []
        sources: list[dict[str, Any]] = []
        chars = 0
        for rc in ranked:
            if chars + len(rc.chunk.text) > self.max_context_chars:
                break
            context_parts.append(rc.chunk.text)
            chars += len(rc.chunk.text)
            meta = rc.chunk.metadata
            sources.append({
                "id": rc.chunk.chunk_id,
                "pinecone_score": round(rc.pinecone_score, 4),
                "mmr_score": round(rc.mmr_score, 4),
                "source_type": meta.get("source_type"),
                "name": meta.get("name") or meta.get("title") or meta.get("csv_file"),
            })

        context_block = "\n\n---\n\n".join(context_parts) if context_parts else "Aucun contexte récupéré."
        user_context = self._build_user_context(user)
        confidence = self._compute_confidence(ranked)

        # 6. Génération
        prompt = self._build_prompt(
            question=question_clean,
            user_context=user_context,
            context_block=context_block,
            intent=intent,
            conversation_history=conversation_history,
        )

        degraded = False
        try:
            answer = self._generate_answer(prompt, intent)
        except RAGServiceError as exc:
            warnings.append(f"Génération indisponible : {exc}")
            logger.warning("[RAG] generation fallback triggered : %s", exc)
            answer = self._build_smart_fallback(
                question=question_clean,
                ranked_chunks=ranked,
                intent=intent,
                user_context=user_context,
            )
            degraded = True

        elapsed_ms = int((time.monotonic() - t0) * 1000)

        return RAGResponse(
            answer=answer,
            sources=sources,
            intent=intent.value,
            confidence=round(confidence, 3),
            retrieved_count=len(sources),
            namespace=ns,
            degraded=degraded or bool(warnings),
            warnings=warnings,
            response_time_ms=elapsed_ms,
        )