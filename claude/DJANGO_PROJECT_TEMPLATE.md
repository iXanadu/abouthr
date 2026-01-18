# Django Project Template & Foundation Guide

## Overview
This document provides a comprehensive template for starting new Django projects with Claude Code, based on proven patterns from real-world multi-tenant SaaS applications. This template emphasizes production-ready architecture from day one.

## Core Philosophy
- **PostgreSQL from the start** - Never use SQLite, even for local development
- **Multi-tenant architecture by default** - Build for scale from the beginning
- **Security-first approach** - Proper credential management and SSL configuration
- **Progressive enhancement** - MVP first, polish later
- **Account-based isolation** - All major models scoped to accounts
- **Role-based permissions** - Granular access control from the start

## Project Structure

### Standard Django App Organization
```
project_name/
├── project_name/           # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/               # Multi-tenant account management
├── main/                   # Core views, authentication, navigation
├── users/                  # User management (if separate from accounts)
├── [domain_apps]/          # Business domain apps
├── shared/                 # Reusable utilities and components
├── static/                 # Global static files
├── media/                  # User uploaded content
├── templates/              # Global templates
├── server/                 # Deployment configurations
│   ├── dev/
│   └── prod/
├── claude/                 # Claude documentation and context
├── requirements.txt
├── .env                    # Non-sensitive configuration
├── .keys                   # Sensitive credentials (never commit)
└── .gitignore
```

### App Design Patterns

#### 1. Core Apps (Always Include)
- **accounts/** - Multi-tenant account management
- **main/** - Authentication, navigation, core views
- **shared/** - Reusable utilities (if needed)

#### 2. Domain Apps (Project-Specific)
- Name apps after business domains, not technical functions
- Each app should have clear boundaries and responsibilities
- Use generic relations for cross-app functionality

#### 3. Reusable Component Apps
- **photos_app/** - Generic file/photo management using ContentType
- **communications/** - Email routing and external integrations
- **notifications/** - System notifications and alerts

## Environment Configuration

### File Structure
```
.env                    # Non-sensitive configuration (committed)
.keys                   # Sensitive credentials (never committed)
.env.example           # Template for .env file
.keys.example          # Template for .keys file
```

### Settings Architecture
Use single `settings.py` with environment-based branching:

```python
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

# Core settings
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ENVIRONMENT = env('ENVIRONMENT')

# Database configuration
DB_PASSWORD = env('DB_PASSWORD')

if ENVIRONMENT == 'production':
    ALLOWED_HOSTS = env('PROD_ALLOWED_HOSTS').split(',')
    DATABASES = {
        'default': env.db('PROD_DATABASE_URL')
    }
    DATABASES['default']['PASSWORD'] = DB_PASSWORD
    STATIC_ROOT = env('PROD_STATIC_ROOT')
    MEDIA_ROOT = env('PROD_MEDIA_ROOT')
    SECURE_SSL_REDIRECT = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
elif ENVIRONMENT == 'development':
    ALLOWED_HOSTS = env('DEV_ALLOWED_HOSTS').split(',')
    DATABASES = {
        'default': env.db('DEV_DATABASE_URL')
    }
    DATABASES['default']['PASSWORD'] = DB_PASSWORD
    STATIC_ROOT = env('DEV_STATIC_ROOT')
    MEDIA_ROOT = env('DEV_MEDIA_ROOT')
    SECURE_SSL_REDIRECT = True
    CSRF_TRUSTED_ORIGINS = [f'https://{env("DEV_DOMAIN")}']
    
else:  # local environment
    ALLOWED_HOSTS = env('LOCAL_ALLOWED_HOSTS').split(',')
    # Local still uses dev database for consistency
    DATABASES = {
        'default': env.db('DEV_DATABASE_URL')
    }
    DATABASES['default']['PASSWORD'] = DB_PASSWORD
    STATIC_ROOT = BASE_DIR / "staticfiles"
    MEDIA_ROOT = BASE_DIR / 'media'
    SECURE_SSL_REDIRECT = False

# Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',  # If building APIs
    
    # Project apps
    'accounts',
    'main',
    'users',
    # Add your domain apps here
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = '/media/'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'main': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

### Environment File Templates

#### .env.example
```bash
# Environment
ENVIRONMENT=local
DEBUG=True

# Database URLs (PostgreSQL)
DEV_DATABASE_URL=postgres://username:password@localhost:5432/projectname_dev
PROD_DATABASE_URL=postgres://username:password@localhost:5432/projectname_prod

# Allowed hosts
LOCAL_ALLOWED_HOSTS=localhost,127.0.0.1
DEV_ALLOWED_HOSTS=dev.yourdomain.com
PROD_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Static and media paths
DEV_STATIC_ROOT=/var/www/staticfiles_dev/
DEV_MEDIA_ROOT=/var/www/mediafiles_dev/
PROD_STATIC_ROOT=/var/www/staticfiles_prod/
PROD_MEDIA_ROOT=/var/www/mediafiles_prod/

# Domain configuration
DEV_DOMAIN=dev.yourdomain.com
PROD_DOMAIN=yourdomain.com
```

#### .keys.example
```bash
# Django
SECRET_KEY=your-secret-key-here

# Database
DB_PASSWORD=your-db-password

# External APIs
GOOGLE_MAPS_API_KEY=your-google-maps-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Email services
EMAIL_HOST_PASSWORD=your-email-password
SENDGRID_API_KEY=your-sendgrid-key

# SMS services
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token

# Cloud services
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret

# Other API keys
RECAPTCHA_SITE_KEY=your-recaptcha-site-key
RECAPTCHA_SECRET_KEY=your-recaptcha-secret-key
```

## Model Architecture

### Multi-Tenant Account Model
```python
# accounts/models.py
from django.db import models
from django.contrib.auth.models import User

class Account(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('user', 'User'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    
    # Permission flags
    can_manage_users = models.BooleanField(default=False)
    can_manage_settings = models.BooleanField(default=False)
    can_delete_data = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.account.name}"
```

### Domain Model Pattern
```python
# your_app/models.py
from django.db import models
from accounts.models import Account

class YourModel(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived'),
    ]
    
    # Always include account for multi-tenancy
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    
    # Your model fields
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Standard timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
```

### File Upload Pattern
```python
def upload_path(instance, filename):
    """Generate upload path based on model and instance"""
    return f"{instance._meta.model_name}/{instance.pk}/{filename}"

class DocumentModel(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    file = models.FileField(upload_to=upload_path)
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
```

## View Patterns

### Account-Scoped Views
```python
# main/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404

@login_required
def account_scoped_view(request, pk):
    """Template for account-scoped views"""
    try:
        user_profile = request.user.userprofile
        account = user_profile.account
        
        # Get object ensuring it belongs to user's account
        obj = get_object_or_404(YourModel, pk=pk, account=account)
        
        context = {
            'object': obj,
            'account': account,
            'user_profile': user_profile,
        }
        return render(request, 'your_app/template.html', context)
        
    except UserProfile.DoesNotExist:
        raise Http404("Access denied")

@login_required
def account_list_view(request):
    """Template for account-scoped list views"""
    try:
        user_profile = request.user.userprofile
        account = user_profile.account
        
        # Only show objects from user's account
        objects = YourModel.objects.filter(account=account)
        
        context = {
            'objects': objects,
            'account': account,
            'user_profile': user_profile,
        }
        return render(request, 'your_app/list.html', context)
        
    except UserProfile.DoesNotExist:
        raise Http404("Access denied")
```

### Permission-Based Views
```python
from django.contrib.auth.decorators import user_passes_test

def has_permission(user, permission_field):
    """Check if user has specific permission"""
    try:
        return getattr(user.userprofile, permission_field, False)
    except UserProfile.DoesNotExist:
        return False

@login_required
@user_passes_test(lambda u: has_permission(u, 'can_manage_users'))
def admin_only_view(request):
    """View requiring specific permission"""
    # Implementation here
    pass
```

## URL Configuration

### Project URLs
```python
# project_name/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('api/v1/', include('api.urls')),  # If using APIs
    path('', include('main.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### App URLs
```python
# main/urls.py
from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('settings/', views.settings, name='settings'),
    path('profile/', views.profile, name='profile'),
    
    # Account management
    path('accounts/', views.account_list, name='account_list'),
    path('accounts/create/', views.account_create, name='account_create'),
    path('accounts/<int:pk>/', views.account_detail, name='account_detail'),
    path('accounts/<int:pk>/edit/', views.account_edit, name='account_edit'),
    path('accounts/<int:pk>/delete/', views.account_delete, name='account_delete'),
    
    # User management
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
]
```

## Template Architecture

### Base Template
```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{{ account.name }}{% endblock %}</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Custom CSS -->
    <link href="{% static 'css/main.css' %}" rel="stylesheet">
    
    {% block extra_css %}{% endblock %}
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="{% url 'main:dashboard' %}">
                {{ account.name }}
            </a>
            
            <div class="navbar-nav ms-auto">
                {% if user.is_authenticated %}
                    <span class="navbar-text me-3">
                        Welcome, {{ user.first_name|default:user.username }}
                    </span>
                    <a class="nav-link" href="{% url 'main:profile' %}">Profile</a>
                    <a class="nav-link" href="{% url 'admin:logout' %}">Logout</a>
                {% else %}
                    <a class="nav-link" href="{% url 'admin:login' %}">Login</a>
                {% endif %}
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            {% endfor %}
        {% endif %}
        
        {% block content %}{% endblock %}
    </div>
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### Context Processors
```python
# main/context_processors.py
from .models import UserProfile

def user_context(request):
    """Add user profile and account to all templates"""
    context = {}
    
    if request.user.is_authenticated:
        try:
            user_profile = request.user.userprofile
            context.update({
                'user_profile': user_profile,
                'account': user_profile.account,
            })
        except UserProfile.DoesNotExist:
            pass
    
    return context
```

## Security Configuration

### Authentication & Authorization
```python
# settings.py additions
LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

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

# Context processors
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
                'main.context_processors.user_context',
            ],
        },
    },
]
```

## Database Setup

### PostgreSQL Configuration
```bash
# Create databases
createdb projectname_dev
createdb projectname_prod

# Create user (optional)
createuser -P projectname_user

# Grant permissions
psql -d projectname_dev -c "GRANT ALL PRIVILEGES ON DATABASE projectname_dev TO projectname_user;"
psql -d projectname_prod -c "GRANT ALL PRIVILEGES ON DATABASE projectname_prod TO projectname_user;"
```

### Initial Migration Commands
```bash
# Create initial migrations
python manage.py makemigrations accounts
python manage.py makemigrations main

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## Server Configuration

### Development Server
```nginx
# /etc/nginx/sites-available/projectname_dev
server {
    server_name dev.yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /var/www/staticfiles_dev/;
    }
    
    location /media/ {
        alias /var/www/mediafiles_dev/;
    }
}
```

### Gunicorn Service
```ini
# /etc/systemd/system/projectname_dev.service
[Unit]
Description=Gunicorn instance to serve projectname_dev
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/projectname
Environment="PATH=/home/ubuntu/.pyenv/versions/3.12.0/bin"
ExecStart=/home/ubuntu/.pyenv/versions/3.12.0/bin/gunicorn --workers 3 --bind 127.0.0.1:8001 projectname.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

## Git Configuration

### .gitignore
```
# Environment files
.env
.keys
.env.*
.keys.*

# Django
*.log
*.pot
*.pyc
__pycache__/
local_settings.py
db.sqlite3
db.sqlite3-journal

# Media files
media/
staticfiles/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Python
*.egg-info/
dist/
build/
.coverage
htmlcov/
.pytest_cache/
.tox/
```

## Dependencies

### requirements.txt
```
Django==5.2.4
django-environ==0.12.0
psycopg2-binary==2.9.10
pillow==11.3.0
djangorestframework==3.15.2
django-cors-headers==4.3.1
gunicorn==21.2.0
```

## Deployment Checklist

### Pre-Deployment
- [ ] Environment files configured (.env, .keys)
- [ ] Database created and accessible
- [ ] Static/media directories created with proper permissions
- [ ] SSL certificates installed
- [ ] Domain DNS configured

### Post-Deployment
- [ ] Migrations applied
- [ ] Static files collected
- [ ] Superuser created
- [ ] Services enabled and started
- [ ] Nginx configuration tested
- [ ] SSL redirect working
- [ ] Media uploads functional

## Claude Integration

### Claude Settings
Create `.claude/settings.local.json` with appropriate permissions for Django development:

```json
{
  "tools": {
    "bash": {
      "enabled": true,
      "allowed_commands": [
        "python manage.py *",
        "pip install *",
        "django-admin *"
      ]
    }
  }
}
```

### Documentation Structure
```
claude/
├── context_memory.md           # Current project status
├── session_notes/             # Daily session summaries
├── project_specifications.md  # Requirements and features
├── development_patterns.md    # Code patterns and conventions
└── deployment_notes.md        # Server configuration notes
```

This template provides a solid foundation for Django projects with multi-tenancy, proper security, and scalable architecture. Customize the domain-specific apps and models based on your project requirements.