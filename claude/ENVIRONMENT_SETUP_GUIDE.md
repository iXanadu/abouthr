# Django Environment Setup Guide

## Overview
This guide provides step-by-step instructions for setting up Django development environments that mirror production from day one. **We never use SQLite** - PostgreSQL is used for all environments (local, dev, prod) to ensure consistency and catch database-specific issues early.

## Prerequisites

### System Requirements
- Python 3.12+ (via pyenv)
- PostgreSQL 14+
- Git
- Node.js (for frontend tooling if needed)

### Development Tools
- Code editor (VS Code recommended)
- Database client (pgAdmin, DBeaver, or psql)
- Terminal/command line access

## Environment Philosophy

### Three-Tier Architecture
1. **Local** - Developer machine, uses dev database
2. **Development** - Staging server, separate dev database
3. **Production** - Live server, production database

### Key Principles
- **PostgreSQL everywhere** - No SQLite, even for local development
- **Separate credentials** - .env for config, .keys for secrets
- **Environment parity** - Local mirrors production as closely as possible
- **Security first** - SSL in dev/prod, proper credential management

## Step 1: System Setup

### Install Python with pyenv
```bash
# Install pyenv (macOS)
brew install pyenv

# Install Python 3.12
pyenv install 3.12.0
pyenv global 3.12.0

# Verify installation
python --version  # Should show 3.12.0
```

### Install PostgreSQL
```bash
# macOS
brew install postgresql
brew services start postgresql

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Start service
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Configure PostgreSQL
```bash
# Create databases
createdb projectname_dev
createdb projectname_prod

# Create dedicated user (optional but recommended)
createuser -P projectname_user
# Enter password when prompted

# Grant permissions
psql -d projectname_dev -c "GRANT ALL PRIVILEGES ON DATABASE projectname_dev TO projectname_user;"
psql -d projectname_prod -c "GRANT ALL PRIVILEGES ON DATABASE projectname_prod TO projectname_user;"
```

## Step 2: Project Initialization

### Create Project Structure
```bash
# Create project directory
mkdir projectname
cd projectname

# Initialize git repository
git init

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Django and dependencies
pip install django django-environ psycopg2-binary pillow

# Create Django project
django-admin startproject projectname .

# Create essential apps
python manage.py startapp accounts
python manage.py startapp main
```

### Create Environment Files
```bash
# Create environment files
touch .env .keys
touch .env.example .keys.example

# Ensure proper permissions
chmod 600 .keys
```

## Step 3: Environment Configuration

### .env File (Non-sensitive configuration)
```bash
# .env
# Environment
ENVIRONMENT=local
DEBUG=True

# Database URLs - PostgreSQL only
DEV_DATABASE_URL=postgres://projectname_user@localhost:5432/projectname_dev
PROD_DATABASE_URL=postgres://projectname_user@localhost:5432/projectname_prod

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

# Application settings
TIME_ZONE=America/New_York
LANGUAGE_CODE=en-us
```

### .keys File (Sensitive credentials)
```bash
# .keys
# Django secret key
SECRET_KEY=django-insecure-change-this-in-production

# Database password
DB_PASSWORD=your-secure-database-password

# External API Keys
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret

# Email configuration
EMAIL_HOST_PASSWORD=your-email-password
SENDGRID_API_KEY=your-sendgrid-api-key

# SMS services
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token

# Cloud storage
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=your-s3-bucket-name

# Other services
STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key
STRIPE_SECRET_KEY=your-stripe-secret-key
RECAPTCHA_SITE_KEY=your-recaptcha-site-key
RECAPTCHA_SECRET_KEY=your-recaptcha-secret-key
```

### Example Files (.env.example, .keys.example)
Create template files showing the structure without actual values:

```bash
# .env.example
ENVIRONMENT=local
DEBUG=True
DEV_DATABASE_URL=postgres://username@localhost:5432/projectname_dev
PROD_DATABASE_URL=postgres://username@localhost:5432/projectname_prod
LOCAL_ALLOWED_HOSTS=localhost,127.0.0.1
DEV_ALLOWED_HOSTS=dev.yourdomain.com
PROD_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

```bash
# .keys.example
SECRET_KEY=your-secret-key-here
DB_PASSWORD=your-database-password
GOOGLE_MAPS_API_KEY=your-google-maps-key
# ... etc
```

## Step 4: Django Settings Configuration

### Implement Environment-Based Settings
Replace the contents of `projectname/settings.py`:

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

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')
ENVIRONMENT = env('ENVIRONMENT')

# Database password from .keys file
DB_PASSWORD = env('DB_PASSWORD')

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
    
elif ENVIRONMENT == 'development':
    ALLOWED_HOSTS = env('DEV_ALLOWED_HOSTS').split(',')
    DATABASES = {
        'default': env.db('DEV_DATABASE_URL')
    }
    DATABASES['default']['PASSWORD'] = DB_PASSWORD
    STATIC_ROOT = env('DEV_STATIC_ROOT')
    MEDIA_ROOT = env('DEV_MEDIA_ROOT')
    
    # Security settings for development
    SECURE_SSL_REDIRECT = True
    CSRF_TRUSTED_ORIGINS = [f'https://{env("DEV_DOMAIN")}']
    
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

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',  # Remove if not using APIs
    
    # Local apps
    'accounts',
    'main',
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
LANGUAGE_CODE = env('LANGUAGE_CODE')
TIME_ZONE = env('TIME_ZONE')
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]

# Media files
MEDIA_URL = '/media/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login URLs
LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'debug.log',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'] if DEBUG else ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'main': {
            'handlers': ['file', 'console'] if DEBUG else ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# External API Configuration
GOOGLE_MAPS_API_KEY = env('GOOGLE_MAPS_API_KEY')
GOOGLE_CLIENT_ID = env('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = env('GOOGLE_CLIENT_SECRET')
```

## Step 5: Database Initialization

### Create and Apply Migrations
```bash
# Make sure PostgreSQL is running
brew services start postgresql  # macOS
# OR
sudo systemctl start postgresql  # Linux

# Test database connection
python manage.py dbshell
# Should connect to PostgreSQL, not SQLite
\q  # Exit psql

# Create initial migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Verify Database Setup
```bash
# Check database tables
python manage.py dbshell
\dt  # List tables - should show Django tables in PostgreSQL
\q   # Exit

# Test Django server
python manage.py runserver
# Visit http://localhost:8000/admin/ to verify
```

## Step 6: Git Configuration

### Create .gitignore
```gitignore
# Environment files
.env
.keys
.env.*
.keys.*

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
media/
staticfiles/

# Testing
.coverage
htmlcov/
.tox/
.pytest_cache/
.coverage.*

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
```

### Initial Git Commit
```bash
# Add files to git
git add .
git commit -m "Initial Django project setup with PostgreSQL"

# Create remote repository (GitHub, GitLab, etc.)
git remote add origin https://github.com/yourusername/projectname.git
git push -u origin main
```

## Step 7: Development Workflow

### Daily Development Process
```bash
# Activate virtual environment
source venv/bin/activate

# Start PostgreSQL (if not running)
brew services start postgresql

# Run development server
python manage.py runserver

# In another terminal, make changes and test
python manage.py makemigrations
python manage.py migrate
python manage.py test
```

### Environment Testing
```bash
# Test different environments
ENVIRONMENT=local python manage.py check
ENVIRONMENT=development python manage.py check
ENVIRONMENT=production python manage.py check --deploy
```

## Step 8: Server Deployment

### Development Server Setup
```bash
# On server, install dependencies
sudo apt-get update
sudo apt-get install python3-pip python3-venv postgresql nginx

# Create project directory
sudo mkdir -p /var/www/projectname
sudo chown ubuntu:ubuntu /var/www/projectname

# Clone repository
git clone https://github.com/yourusername/projectname.git /var/www/projectname

# Set up virtual environment
cd /var/www/projectname
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create environment files
cp .env.example .env
cp .keys.example .keys

# Edit environment files with production values
nano .env
nano .keys

# Set proper permissions
chmod 600 .keys

# Create static/media directories
sudo mkdir -p /var/www/staticfiles_dev /var/www/mediafiles_dev
sudo chown ubuntu:www-data /var/www/staticfiles_dev /var/www/mediafiles_dev
sudo chmod 775 /var/www/staticfiles_dev /var/www/mediafiles_dev

# Run migrations
python manage.py migrate
python manage.py collectstatic
```

### Nginx Configuration
```nginx
# /etc/nginx/sites-available/projectname_dev
server {
    listen 80;
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
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /var/www/mediafiles_dev/;
        expires 1y;
        add_header Cache-Control "public, immutable";
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
WorkingDirectory=/var/www/projectname
Environment="PATH=/var/www/projectname/venv/bin"
Environment="ENVIRONMENT=development"
ExecStart=/var/www/projectname/venv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:8001 \
    --log-level info \
    --access-logfile /var/log/gunicorn/access.log \
    --error-logfile /var/log/gunicorn/error.log \
    projectname.wsgi:application
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### SSL Configuration
```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d dev.yourdomain.com

# Verify auto-renewal
sudo certbot renew --dry-run
```

## Step 9: Monitoring and Maintenance

### Log Management
```bash
# View application logs
tail -f /var/log/gunicorn/error.log
tail -f /var/www/projectname/debug.log

# View system logs
sudo journalctl -u projectname_dev -f
```

### Database Backup
```bash
# Create backup script
#!/bin/bash
# /home/ubuntu/backup_db.sh
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump projectname_dev > /home/ubuntu/backups/projectname_dev_$DATE.sql
```

### Performance Monitoring
```bash
# Check service status
sudo systemctl status projectname_dev
sudo systemctl status nginx
sudo systemctl status postgresql

# Monitor resource usage
htop
df -h
```

## Step 10: Troubleshooting

### Common Issues

#### Database Connection Problems
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check database existence
psql -l

# Test connection
python manage.py dbshell
```

#### Environment Variable Issues
```bash
# Check loaded environment variables
python manage.py shell
>>> import os
>>> print(os.environ.get('ENVIRONMENT'))
>>> print(os.environ.get('SECRET_KEY'))
```

#### Static Files Not Loading
```bash
# Collect static files
python manage.py collectstatic --clear

# Check permissions
ls -la /var/www/staticfiles_dev/
```

#### SSL Certificate Issues
```bash
# Check certificate status
sudo certbot certificates

# Renew certificate
sudo certbot renew
```

## Security Checklist

### Development Environment
- [ ] `.keys` file has proper permissions (600)
- [ ] Environment files not committed to git
- [ ] Database password is strong
- [ ] Debug mode disabled in production
- [ ] SSL certificates installed and valid

### Production Environment
- [ ] All security headers enabled
- [ ] Database backups configured
- [ ] Log rotation configured
- [ ] Monitoring and alerting set up
- [ ] Regular security updates scheduled

## Next Steps

After completing this setup:

1. **Implement core models** - Start with Account and User models
2. **Set up authentication** - Configure login/logout flows
3. **Create base templates** - Establish UI framework
4. **Add business logic** - Implement domain-specific features
5. **Set up testing** - Create test suite for your application
6. **Configure CI/CD** - Automate deployments
7. **Add monitoring** - Set up application monitoring and alerting

This environment setup ensures your Django project starts with production-ready infrastructure and can scale as your application grows.