"""
Django settings for basic project.
Multi-tenant Django application with PostgreSQL and basic functionality.

Replace 'projectname' with your actual project name throughout this file.
"""

import os
import environ
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Environment setup
env = environ.Env(
    DEBUG=(bool, False),
    ENVIRONMENT=(str, 'local')
)

# Read environment files
environ.Env.read_env(env_file='.env')
environ.Env.read_env(env_file='.keys')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')
ENVIRONMENT = env('ENVIRONMENT')

# Database password from .keys file
DB_PASSWORD = env('DB_PASSWORD')

# Application URL (used in emails, links, etc.)
APP_URL = "http://localhost:8000"
if ENVIRONMENT == 'development':
    APP_URL = f"https://{env('DEV_DOMAIN')}"
elif ENVIRONMENT == 'production':
    APP_URL = f"https://{env('PROD_DOMAIN')}"

# Environment-specific configuration
if ENVIRONMENT == 'production':
    ALLOWED_HOSTS = env('PROD_ALLOWED_HOSTS').split(',')
    DATABASES = {
        'default': env.db('PROD_DATABASE_URL')
    }
    DATABASES['default']['PASSWORD'] = DB_PASSWORD
    STATIC_ROOT = env('PROD_STATIC_ROOT')
    MEDIA_ROOT = env('PROD_MEDIA_ROOT')

    # Security settings for production
    SECURE_SSL_REDIRECT = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

elif ENVIRONMENT == 'development':
    ALLOWED_HOSTS = env('DEV_ALLOWED_HOSTS').split(',')
    DATABASES = {
        'default': env.db('DEV_DATABASE_URL')
    }
    DATABASES['default']['PASSWORD'] = DB_PASSWORD
    STATIC_ROOT = env('DEV_STATIC_ROOT')
    MEDIA_ROOT = env('DEV_MEDIA_ROOT')

    # Security settings for development server (behind nginx/SSL)
    SECURE_SSL_REDIRECT = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    CSRF_TRUSTED_ORIGINS = [f'https://{env("DEV_DOMAIN")}']

    STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

else:  # local environment
    ALLOWED_HOSTS = env('LOCAL_ALLOWED_HOSTS').split(',')
    # Local development uses dev database for consistency
    DATABASES = {
        'default': env.db('DEV_DATABASE_URL')
    }
    DATABASES['default']['PASSWORD'] = DB_PASSWORD
    STATIC_ROOT = BASE_DIR / "staticfiles"
    MEDIA_ROOT = BASE_DIR / 'media'

    # No SSL for local development
    SECURE_SSL_REDIRECT = False
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False

    # Only include static dir if it exists
    STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")] if os.path.exists(BASE_DIR / "static") else []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'crispy_forms',
    'crispy_bootstrap5',
    'rest_framework',

    # Local apps
    'core',      # Shared base models and utilities
    'accounts',  # Multi-tenant account management
    # Add your domain apps here
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'projectname.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'accounts.context_processors.user_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'projectname.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'

# NOTE: For SaaS deployment, timezone should be configurable per account
TIME_ZONE = 'America/New_York'

USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# Media files
MEDIA_URL = '/media/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Crispy forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
            'formatter': 'verbose'
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': env('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
    },
}
