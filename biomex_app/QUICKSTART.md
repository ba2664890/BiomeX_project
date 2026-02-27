# Guide de Démarrage Rapide - BiomeX

Ce guide vous aide à démarrer rapidement avec l'application BiomeX.

## Prérequis

- Python 3.11+
- Flutter 3.0+
- Compte [Neon](https://neon.tech) (PostgreSQL gratuit)

## Étape 1: Configuration du Backend

### 1.1 Créer la base de données Neon

1. Allez sur [neon.tech](https://neon.tech) et créez un compte
2. Créez un nouveau projet
3. Créez une base de données nommée `biomex`
4. Copiez l'URL de connexion

### 1.2 Configurer le Backend

```bash
cd backend

# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Configuration
cp .env.example .env
```

Éditez le fichier `.env`:

```env
SECRET_KEY=votre-cle-secrete-tres-longue-et-aleatoire
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,10.0.2.2

# Remplacez par votre URL Neon
DATABASE_URL=postgresql://user:password@host.neon.tech/biomex?sslmode=require
```

### 1.3 Initialiser la base de données

```bash
# Créer les tables
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver 0.0.0.0:8000
```

Le backend est accessible sur `http://localhost:8000`

Admin: `http://localhost:8000/admin`

## Étape 2: Configuration du Frontend

### 2.1 Installer Flutter

Suivez les instructions sur [flutter.dev](https://flutter.dev/docs/get-started/install)

### 2.2 Configurer l'application

```bash
cd frontend

# Installer les dépendances
flutter pub get
```

Vérifiez la configuration API dans `lib/constants/api_constants.dart`:

```dart
// Pour Android Emulator
static const String baseUrl = 'http://10.0.2.2:8000';

// Pour iOS Simulator
// static const String baseUrl = 'http://localhost:8000';
```

### 2.3 Lancer l'application

```bash
# Vérifier les appareils disponibles
flutter devices

# Lancer sur un appareil connecté
flutter run

# Ou spécifier un appareil
flutter run -d <device_id>
```

## Étape 3: Tester l'application

### 3.1 Créer un compte

1. Sur l'écran de connexion, tapez sur "S'inscrire"
2. Remplissez le formulaire d'inscription
3. Connectez-vous avec vos identifiants

### 3.2 Initialiser les données de démo

Pour tester avec des données:

1. Allez dans l'onglet "Rapport"
2. Appuyez sur "Générer des données de démo"
3. Les données microbiome seront créées

Ou via l'API:

```bash
# Créer une analyse de démo
curl -X POST http://localhost:8000/api/microbiome/create-sample/ \
  -H "Authorization: Bearer <votre-token>"

# Initialiser les données nutrition
curl -X POST http://localhost:8000/api/nutrition/initialize-data/ \
  -H "Authorization: Bearer <votre-token>"

# Initialiser les données de suivi
curl -X POST http://localhost:8000/api/tracking/initialize-data/ \
  -H "Authorization: Bearer <votre-token>"
```

## Structure des Écrans

| Écran | Description |
|-------|-------------|
| **Accueil** | Dashboard avec score microbiome, indicateurs, recommandations |
| **Rapport** | Analyse détaillée, équilibre bactérien, graphiques |
| **Nutrition** | Super-aliments, substitutions, calendrier saisonnier |
| **Suivi** | Bilan quotidien, graphiques d'évolution, insights |
| **Profil** | Informations utilisateur, paramètres, confidentialité |

## Étape 4: Activer le Chatbot RAG (HF Router + Pinecone)

### 4.1 Variables d'environnement backend

Dans `backend/.env`, ajoute:

```env
RAG_HF_API_TOKEN=hf_xxx
# Modèle chat disponible sur le Router
RAG_HF_GENERATION_MODEL=Qwen/Qwen2.5-7B-Instruct
# Optionnel: modèles de secours séparés par des virgules
RAG_HF_FALLBACK_GENERATION_MODELS=meta-llama/Llama-3.1-8B-Instruct,mistralai/Mistral-7B-Instruct-v0.3,google/gemma-2-2b-it
RAG_HF_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
RAG_HF_ROUTER_BASE_URL=https://router.huggingface.co
RAG_HF_ROUTER_PROVIDER=
RAG_HF_GENERATION_URL=
RAG_HF_EMBEDDING_URL=

RAG_PINECONE_API_KEY=pcsk_xxx
# Host complet de l'index Pinecone (pas le nom d'index)
RAG_PINECONE_INDEX_HOST=your-index-xxxx.svc.aped-4627-b74a.pinecone.io
RAG_PINECONE_NAMESPACE=biomex-knowledge
RAG_DEFAULT_TOP_K=6
RAG_MAX_CONTEXT_CHARS=12000
```

### 4.2 Ingestion des connaissances nutritionnelles

Depuis `backend/`:

```bash
# Ingestion depuis la base nutrition (FoodItem, Recipe, substitutions)
python manage.py ingest_rag_knowledge --source nutrition_db

# Option CSV (exemple)
python manage.py ingest_rag_knowledge --source csv --csv-path ../Data/Data_proccesing/viome-abundance/abundance/Viome_species_readcount_40samples.csv
```

### 4.3 Endpoints API RAG

```bash
# Status de la configuration RAG (auth requis)
GET /api/recommendations/rag/status/

# Ingestion via API (admin uniquement)
POST /api/recommendations/rag/ingest/

# Chatbot RAG
POST /api/recommendations/rag/chat/
{
  "question": "Quels aliments privilégier pour améliorer ma diversité microbiome ?",
  "top_k": 6
}
```

## Fonctionnalités Clés

### Authentification
- JWT tokens avec refresh automatique
- Stockage sécurisé des credentials
- Profil utilisateur complet

### Microbiome
- Score de diversité (0-100)
- Équilibre bactérien avec barres de progression
- Historique des scores avec graphiques
- Commande de kits de suivi

### Nutrition
- Super-aliments personnalisés avec pourcentage de correspondance
- Aliments à limiter avec tags inflammatoires
- Tableau des substitutions
- Calendrier des récoltes saisonnières

### Suivi
- Bilan quotidien par catégorie (digestion, énergie, sommeil, peau)
- Graphiques d'évolution sur 6 mois
- Insights hebdomadaires
- Rappels de prochains tests

## Dépannage

### Problème: Connexion refusée

**Solution**: Vérifiez que le backend tourne sur `0.0.0.0:8000` et non `127.0.0.1:8000`

```bash
python manage.py runserver 0.0.0.0:8000
```

### Problème: CORS errors

**Solution**: Vérifiez la configuration CORS dans `settings.py`:

```python
CORS_ALLOW_ALL_ORIGINS = True
# ou
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://10.0.2.2:8000",
]
```

### Problème: Base de données non trouvée

**Solution**: Vérifiez l'URL de connexion Neon dans `.env`:

```env
DATABASE_URL=postgresql://user:password@host.neon.tech/biomex?sslmode=require
```

### Problème: Packages Flutter manquants

**Solution**: Nettoyez et réinstallez:

```bash
flutter clean
flutter pub get
```

## Déploiement

### Backend (Production)

Options recommandées:
- [Railway](https://railway.app)
- [Render](https://render.com)
- [Heroku](https://heroku.com)

Configuration Render recommandée (backend Django, Docker):

```bash
# Service type: Web Service (Docker)
# Root Directory: biomex_app/backend
# Dockerfile: Dockerfile
```

Important:
- Le script `docker-entrypoint.sh` lance automatiquement:
  - `python manage.py makemigrations --noinput`
  - `python manage.py migrate --noinput --run-syncdb`
  - `python manage.py collectstatic --noinput`
  - `gunicorn biomex.wsgi:application`

Version Python:
- L'image Docker `python:3.11.11-slim` fixe la version Python pour éviter les erreurs de build avec Python 3.14 (ex: Pillow).

### Mobile (Production)

```bash
# Android APK
flutter build apk --release

# Android App Bundle
flutter build appbundle --release

# iOS
flutter build ios --release
```

## Ressources

- [Documentation Django](https://docs.djangoproject.com/)
- [Documentation Flutter](https://docs.flutter.dev/)
- [Documentation Django REST Framework](https://www.django-rest-framework.org/)

## Support

Pour toute question ou problème:
- Email: contact@biomex.ai
- Issues: [GitHub Issues](https://github.com/biomex/issues)
