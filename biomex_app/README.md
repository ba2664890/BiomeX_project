# BiomeX - Application Mobile

BiomeX est une plateforme IA pour l'analyse du microbiome et la médecine préventive personnalisée en Afrique.

## Architecture

Ce projet est composé de deux parties :

### Backend (Django)
- **Framework**: Django 4.2 + Django REST Framework
- **Base de données**: PostgreSQL (Neon)
- **Authentification**: JWT (JSON Web Tokens)
- **Documentation**: API RESTful

### Frontend (Flutter)
- **Framework**: Flutter 3.x
- **State Management**: Provider
- **HTTP Client**: Dio + http
- **Charts**: fl_chart
- **Storage**: flutter_secure_storage

## Fonctionnalités

### Authentification
- Inscription / Connexion
- Profil utilisateur
- Gestion des préférences alimentaires et allergies
- Paramètres de confidentialité

### Microbiome
- Score de diversité microbienne
- Équilibre bactérien
- Marqueurs de santé
- Historique des scores
- Commande de kits de test

### Nutrition
- Super-aliments personnalisés
- Aliments à limiter
- Substitutions alimentaires
- Calendrier des récoltes saisonnières
- Recettes recommandées

### Suivi
- Bilan quotidien (digestion, énergie, sommeil, peau)
- Graphiques d'évolution
- Insights hebdomadaires
- Rappels de tests

## Installation

### Prérequis
- Python 3.11+
- Flutter 3.0+
- PostgreSQL (ou compte Neon)

### Backend

```bash
cd backend

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos configurations

# Créer la base de données
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

### Frontend

```bash
cd frontend

# Installer les dépendances
flutter pub get

# Lancer l'application
flutter run
```

## Configuration

### Variables d'environnement Backend (.env)

```env
SECRET_KEY=votre-cle-secrete
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Neon PostgreSQL
DATABASE_URL=postgresql://user:password@host.neon.tech/database?sslmode=require
```

### Configuration Flutter

Modifier `lib/constants/api_constants.dart` :

```dart
// Pour Android Emulator
static const String baseUrl = 'http://10.0.2.2:8000';

// Pour iOS Simulator
static const String baseUrl = 'http://localhost:8000';

// Pour Production
static const String baseUrl = 'https://votre-api.com';
```

## Structure du projet

```
biomex_app/
├── backend/
│   ├── biomex/              # Configuration Django
│   ├── users/               # Authentification & profils
│   ├── microbiome/          # Analyses microbiome
│   ├── nutrition/           # Aliments & recettes
│   ├── tracking/            # Suivi de santé
│   ├── recommendations/     # Recommandations
│   └── requirements.txt
│
└── frontend/
    ├── lib/
    │   ├── constants/       # Thèmes & API
    │   ├── models/          # Modèles de données
    │   ├── services/        # Services API
    │   ├── providers/       # State management
    │   ├── screens/         # Écrans
    │   ├── widgets/         # Widgets réutilisables
    │   └── main.dart
    └── pubspec.yaml
```

## API Endpoints

### Authentification
- `POST /api/token/` - Login
- `POST /api/token/refresh/` - Rafraîchir token
- `POST /api/users/register/` - Inscription
- `GET/PUT /api/users/profile/` - Profil

### Microbiome
- `GET /api/microbiome/dashboard-scores/` - Scores actuels
- `GET /api/microbiome/latest/` - Dernière analyse
- `GET /api/microbiome/bacteria-balance/` - Équilibre bactérien
- `POST /api/microbiome/request-kit/` - Commander un kit

### Nutrition
- `GET /api/nutrition/superfoods/` - Super-aliments
- `GET /api/nutrition/foods-to-avoid/` - Aliments à limiter
- `GET /api/nutrition/substitutions/` - Substitutions
- `GET /api/nutrition/seasonal/` - Calendrier saisonnier

### Suivi
- `GET /api/tracking/dashboard/` - Tableau de bord
- `POST /api/tracking/wellness/create/` - Bilan quotidien
- `GET /api/tracking/insights/` - Insights hebdomadaires

## Déploiement

### Backend (Railway/Render/Heroku)

```bash
# Créer un Procfile
echo "web: gunicorn biomex.wsgi:application" > Procfile

# Déployer
git push origin main
```

Pour Render (service Docker):

```bash
# Root Directory: biomex_app/backend
# Dockerfile: Dockerfile
```

Le script `backend/docker-entrypoint.sh` exécute automatiquement `makemigrations`, `migrate`, `collectstatic`, puis démarre Gunicorn.
L'image Docker `python:3.11.11-slim` fixe Python pour éviter les incompatibilités de build avec Python 3.14.

### Frontend

```bash
# Build Android
flutter build apk --release

# Build iOS
flutter build ios --release
```

## Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## Contact

- Email: contact@biomex.ai
- Site web: www.biomex.ai
