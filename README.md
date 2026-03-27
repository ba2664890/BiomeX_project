# BiomeX_project

# BiomeX - Mobile Application

BiomeX is an AI-powered platform for microbiome analysis and personalized preventive medicine in Africa.

## Architecture

This project consists of two parts:

### Backend (Django)
- **Framework**: Django 4.2 + Django REST Framework  
- **Database**: PostgreSQL (Neon)  
- **Authentication**: JWT (JSON Web Tokens)  
- **Documentation**: RESTful API  

### Frontend (Flutter)
- **Framework**: Flutter 3.x  
- **State Management**: Provider  
- **HTTP Client**: Dio + http  
- **Charts**: fl_chart  
- **Storage**: flutter_secure_storage  

## Features

### Authentication
- Sign up / Login  
- User profile  
- Dietary preferences and allergy management  
- Privacy settings  

### Microbiome
- Microbial diversity score  
- Bacterial balance  
- Health markers  
- Score history  
- Test kit ordering  

### Nutrition
- Personalized superfoods  
- Foods to limit  
- Food substitutions  
- Seasonal harvest calendar  
- Recommended recipes  

### Tracking
- Daily check-in (digestion, energy, sleep, skin)  
- Progress charts  
- Weekly insights  
- Test reminders  

## Installation

### Prerequisites
- Python 3.11+  
- Flutter 3.0+  
- PostgreSQL (or Neon account)  

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your configuration

# Create database
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```
```
Frontend
cd frontend

# Install dependencies
flutter pub get
```
```
# Run application
flutter run
Configuration
Backend Environment Variables (.env)
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Neon PostgreSQL
DATABASE_URL=postgresql://user:password@host.neon.tech/database?sslmode=require
```
```
Flutter Configuration

Modify lib/constants/api_constants.dart:

// For Android Emulator
static const String baseUrl = 'http://10.0.2.2:8000';

// For iOS Simulator
static const String baseUrl = 'http://localhost:8000';

// For Production
static const String baseUrl = 'https://your-api.com';
Project Structure
biomex_app/
├── backend/
│   ├── biomex/              # Django configuration
│   ├── users/               # Authentication & profiles
│   ├── microbiome/          # Microbiome analysis
│   ├── nutrition/           # Foods & recipes
│   ├── tracking/            # Health tracking
│   ├── recommendations/     # Recommendations
│   └── requirements.txt
│
└── frontend/
    ├── lib/
    │   ├── constants/       # Themes & API
    │   ├── models/          # Data models
    │   ├── services/        # API services
    │   ├── providers/       # State management
    │   ├── screens/         # Screens
    │   ├── widgets/         # Reusable widgets
    │   └── main.dart
    └── pubspec.yaml
```
```
API Endpoints
Authentication
POST /api/token/ - Login
POST /api/token/refresh/ - Refresh token
POST /api/users/register/ - Register
GET/PUT /api/users/profile/ - Profile
Microbiome
GET /api/microbiome/dashboard-scores/ - Current scores
GET /api/microbiome/latest/ - Latest analysis
GET /api/microbiome/bacteria-balance/ - Bacterial balance
POST /api/microbiome/request-kit/ - Order test kit
Nutrition
GET /api/nutrition/superfoods/ - Superfoods
GET /api/nutrition/foods-to-avoid/ - Foods to limit
GET /api/nutrition/substitutions/ - Substitutions
GET /api/nutrition/seasonal/ - Seasonal calendar
Tracking
GET /api/tracking/dashboard/ - Dashboard
POST /api/tracking/wellness/create/ - Daily check-in
GET /api/tracking/insights/ - Weekly insights

```

```
Deployment
Backend (Railway / Render / Heroku)
# Create Procfile
echo "web: gunicorn biomex.wsgi:application" > Procfile

# Deploy
git push origin main
```
For Render (Docker service):

# Root Directory: biomex_app/backend
# Dockerfile: Dockerfile

The script backend/docker-entrypoint.sh automatically runs makemigrations, migrate, collectstatic, then starts Gunicorn.
The Docker image python:3.11.11-slim locks the Python version to avoid build issues with Python 3.14.

Frontend
# Build Android
flutter build apk --release

# Build iOS
flutter build ios --release
Contribution
Fork the project
Create a branch (git checkout -b feature/AmazingFeature)
Commit changes (git commit -m 'Add some AmazingFeature')
Push to branch (git push origin feature/AmazingFeature)
Open a Pull Request
License

This project is licensed under the MIT License. See the LICENSE file for more details.

Contact
Email: contact@biomex.ai
Website: www.biomex.ai
