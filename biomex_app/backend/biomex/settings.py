"""
Django settings for biomex project.
"""
import os
from pathlib import Path
from datetime import timedelta
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-dev-key-change-in-production')

DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'drf_yasg',
    'rest_framework_simplejwt',
    'corsheaders',
    'users',
    'microbiome',
    'nutrition',
    'tracking',
    'recommendations',
    'site_content',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'biomex.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'biomex.wsgi.application'

# Database - Neon PostgreSQL
DATABASE_URL = os.getenv('DATABASE_URL')
DB_CONN_MAX_AGE = int(os.getenv('DB_CONN_MAX_AGE', '0'))
DB_CONN_HEALTH_CHECKS = os.getenv('DB_CONN_HEALTH_CHECKS', 'True').lower() == 'true'
DB_CONNECT_TIMEOUT = int(os.getenv('DB_CONNECT_TIMEOUT', '10'))
if DATABASE_URL:
    db_config = dj_database_url.parse(DATABASE_URL, conn_max_age=DB_CONN_MAX_AGE)
    db_config['CONN_HEALTH_CHECKS'] = DB_CONN_HEALTH_CHECKS
    db_config.setdefault('OPTIONS', {})
    db_config['OPTIONS'].setdefault('connect_timeout', DB_CONNECT_TIMEOUT)
    DATABASES = {
        'default': db_config
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'biomex'),
            'USER': os.getenv('DB_USER', 'biomex_user'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'password'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
            'CONN_MAX_AGE': DB_CONN_MAX_AGE,
            'CONN_HEALTH_CHECKS': DB_CONN_HEALTH_CHECKS,
            'OPTIONS': {
                'connect_timeout': DB_CONNECT_TIMEOUT,
            },
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Dakar'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://10.0.2.2:8000",
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Swagger / OpenAPI
SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False,
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'JWT Authorization header using the Bearer scheme. Example: "Bearer <token>"',
        },
    },
}

# Jazzmin admin theme
JAZZMIN_SETTINGS = {
    'site_title': 'BiomeX Admin',
    'site_header': 'BiomeX',
    'site_brand': 'BiomeX',
    'welcome_sign': 'Bienvenue dans l administration BiomeX',
    'site_logo_classes': 'img-circle',
    'navigation_expanded': True,
    'hide_apps': [],
    'hide_models': [],
}

JAZZMIN_UI_TWEAKS = {
    'theme': 'flatly',
    'dark_mode_theme': None,
    'navbar': 'navbar-dark navbar-success',
    'accent': 'accent-primary',
    'sidebar': 'sidebar-dark-success',
    'button_classes': {
        'primary': 'btn-success',
        'secondary': 'btn-secondary',
        'info': 'btn-info',
        'warning': 'btn-warning',
        'danger': 'btn-danger',
        'success': 'btn-success',
    },
}

# RAG / LLM Configuration
RAG_HF_API_TOKEN = os.getenv('RAG_HF_API_TOKEN', '')
RAG_HF_GENERATION_MODEL = os.getenv('RAG_HF_GENERATION_MODEL', '')
RAG_HF_EMBEDDING_MODEL = os.getenv('RAG_HF_EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
RAG_HF_ROUTER_BASE_URL = os.getenv('RAG_HF_ROUTER_BASE_URL', 'https://router.huggingface.co')
RAG_HF_ROUTER_PROVIDER = os.getenv('RAG_HF_ROUTER_PROVIDER', '')
RAG_HF_GENERATION_URL = os.getenv('RAG_HF_GENERATION_URL', '')
RAG_HF_EMBEDDING_URL = os.getenv('RAG_HF_EMBEDDING_URL', '')
RAG_HF_FALLBACK_GENERATION_MODELS = os.getenv('RAG_HF_FALLBACK_GENERATION_MODELS', '')

RAG_PINECONE_API_KEY = os.getenv('RAG_PINECONE_API_KEY', '')
RAG_PINECONE_INDEX_HOST = os.getenv('RAG_PINECONE_INDEX_HOST', '')
RAG_PINECONE_NAMESPACE = os.getenv('RAG_PINECONE_NAMESPACE', 'biomex-knowledge')

RAG_DEFAULT_TOP_K = int(os.getenv('RAG_DEFAULT_TOP_K', '6'))
RAG_MAX_CONTEXT_CHARS = int(os.getenv('RAG_MAX_CONTEXT_CHARS', '12000'))
