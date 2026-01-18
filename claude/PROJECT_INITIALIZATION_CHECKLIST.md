# Django Project Initialization Checklist

## Overview
This checklist ensures every new Django project with Claude follows the established patterns and best practices. Use this as a step-by-step guide to set up production-ready Django applications.

## Pre-Project Setup

### System Requirements
- [ ] Python 3.12+ installed via pyenv
- [ ] PostgreSQL 14+ installed and running
- [ ] Git configured with proper credentials
- [ ] Code editor set up (VS Code recommended)
- [ ] Terminal access configured

### Domain and Hosting
- [ ] Domain name registered (if applicable)
- [ ] DNS configured for dev.yourdomain.com
- [ ] SSL certificates planned/ordered
- [ ] Server access configured (development and production)

## Project Creation

### 1. Repository Setup
```bash
# Navigate to development folder
cd ~/pyprojects

# Create Django project (this creates the project directory)
django-admin startproject projectname

# Navigate into the project
cd projectname

# Initialize git repository
git init
git branch -M main

# Create .gitignore from template
```

- [ ] Navigated to ~/pyprojects
- [ ] Django project created with django-admin startproject
- [ ] Git repository initialized in project root
- [ ] .gitignore file created and configured
- [ ] Remote repository created (GitHub/GitLab)

### 2. Python Environment
```bash
# Create project-specific pyenv version (replace 'proj' with project abbreviation)
# Note: Only install if 3.12.0 not already available
# pyenv install 3.12.0  # Skip if already installed
pyenv virtualenv 3.12.0 proj-3.12

# Set local Python version for this project
pyenv local proj-3.12

# Verify Python version
python --version

# Upgrade pip
pip install --upgrade pip
```

- [ ] Verified Python 3.12.0 is available (skip install if already present)
- [ ] Project-specific pyenv version created (proj-3.12, where 'proj' = project abbreviation)
- [ ] Local pyenv version set for project
- [ ] Python version verified
- [ ] Pip upgraded to latest version

### 3. Django Installation
```bash
# Install core dependencies
pip install django django-environ psycopg2-binary pillow

# Create requirements.txt
pip freeze > requirements.txt
```

- [ ] Django and core dependencies installed
- [ ] requirements.txt created
- [ ] Dependencies tested and working

### 4. Django Project Structure
```bash
# Project structure verified (apps will be created after Claude planning)
# Note: Defer app creation until project specifications are finalized with Claude
```

- [ ] Project structure verified
- [ ] Environment files will be at project root level
- [ ] App creation deferred until project planning complete

### 5. Claude Template Setup
```bash
# Copy claude template folder to project
cp -r ~/pyprojects/claude_template ./claude

# Create session notes directory for tracking development
mkdir -p ./claude/session_notes

# Copy example environment files to project root
cp ./claude/examples/basic_project/.env.example ./.env
cp ./claude/examples/basic_project/.keys.example ./.keys

# Set proper permissions on keys file
chmod 600 .keys
```

- [ ] Claude template folder copied to project/claude
- [ ] Session notes directory created (./claude/session_notes)
- [ ] .env.example copied to project root as .env
- [ ] .keys.example copied to project root as .keys
- [ ] Proper permissions set on .keys file (600)

### 6. Django Settings Configuration
```bash
# Navigate to the Django project folder (same name as project)
cd projectname

# Backup original settings and replace with template
mv settings.py old_settings.py
cp ../claude/examples/basic_project/settings.py ./

# Edit settings.py to replace 'projectname' with actual project name
# Change line 107: ROOT_URLCONF = 'projectname.urls' → 'actualprojectname.urls'
# Change line 126: WSGI_APPLICATION = 'projectname.wsgi.application' → 'actualprojectname.wsgi.application'
```

- [ ] Original settings.py backed up as old_settings.py
- [ ] Template settings.py copied to project
- [ ] ROOT_URLCONF updated with actual project name
- [ ] WSGI_APPLICATION updated with actual project name

## Database Setup

### 1. PostgreSQL Configuration
```bash
# Connect to remote PostgreSQL server (replace with your project name)
# Server: postgres.o6.org

# Create database user (replace 'projectname' with your actual project name)
psql -h postgres.o6.org -U ixanadu -d postgres -c "CREATE USER projectname WITH PASSWORD 'secure_password_here';"

# Create databases
createdb -h postgres.o6.org -U ixanadu projectname_dev
createdb -h postgres.o6.org -U ixanadu projectname_prod

# Grant permissions to user
psql -h postgres.o6.org -U ixanadu -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE projectname_dev TO projectname;"
psql -h postgres.o6.org -U ixanadu -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE projectname_prod TO projectname;"

# Test connections
psql -h postgres.o6.org -U projectname -d projectname_dev
psql -h postgres.o6.org -U projectname -d projectname_prod
```

- [ ] Database user created (projectname)
- [ ] Development database created (projectname_dev)
- [ ] Production database created (projectname_prod)
- [ ] Permissions granted to user
- [ ] Database connections tested from local machine

### 2. Database Settings
- [ ] Database URLs configured in .env
- [ ] Database password set in .keys
- [ ] Database connection tested with Django
- [ ] No SQLite references remaining

## Environment Customization

### Customize Environment Variables
```bash
# Edit .env file with project-specific values
vi .env
# Update: projectname references, domains, paths

# Edit .keys file with secure credentials  
vi .keys
# Update: SECRET_KEY, DB_PASSWORD, API keys
```

- [ ] .env file customized with project-specific values
- [ ] .keys file updated with secure credentials
- [ ] Database URLs point to correct databases
- [ ] All placeholder values replaced

### Create Initial Project Status
```bash
# Create project status file for Claude
cat > ./claude/project_status.md << EOF
# Project Status

## Initialization Complete
- Project created and basic setup completed
- Database configured (postgres.o6.org)
- Environment files configured
- Claude template copied to project
- Ready to begin development with Claude

## Current State
- **Django Project**: Created and configured
- **Apps**: None created yet (pending architecture discussion)
- **Database**: Empty (migrations not run)
- **Next Steps**: Define project architecture and create initial apps

## Claude Instructions
- Use ./claude/session_notes/ to track development sessions
- Reference the template files in ./claude/ for Django patterns
- Follow the multi-tenant, PostgreSQL-first architecture patterns
- See ./claude/PROJECT_INITIALIZATION_CHECKLIST.md for setup patterns and examples
- See ./claude/DJANGO_PROJECT_TEMPLATE.md for model/view/template patterns

## Setup Details
- Python Environment: [replace with actual pyenv version]
- Database: [replace with actual database names]
- Server: postgres.o6.org
- User: [replace with actual db username]

Last Updated: $(date "+%Y-%m-%d %H:%M")
EOF

# Edit the file to fill in actual project details if needed
vi ./claude/project_status.md
```

- [ ] Initial project_status.md created in claude folder
- [ ] Project details filled in (pyenv version, database names, etc.)
- [ ] Status file ready for Claude reference

## Security Configuration

### 1. Development Security
- [ ] Debug mode properly configured
- [ ] Secret key generated and secured
- [ ] CORS settings configured (if needed)
- [ ] CSRF protection enabled

### 2. Production Security
- [ ] SSL redirect enabled
- [ ] Secure cookies configured
- [ ] HSTS headers configured
- [ ] Security middleware enabled
- [ ] Allowed hosts restricted

## Core Models

### 1. Account Model
```python
# accounts/models.py
class Account(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

- [ ] Account model created
- [ ] Multi-tenant architecture implemented
- [ ] Account admin interface configured

### 2. User Profile Model
```python
# accounts/models.py
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    # Permission flags
```

- [ ] UserProfile model created
- [ ] Role-based permissions implemented
- [ ] User-Account relationship established

### 3. Domain Models
- [ ] Business domain models created
- [ ] All models include account foreign key
- [ ] Model relationships defined
- [ ] Model validation implemented

## URL Configuration

### 1. Project URLs
```python
# projectname/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('main.urls')),
]
```

- [ ] Main URL configuration updated
- [ ] App URLs included
- [ ] Media URL configuration added (for development)

### 2. App URLs
- [ ] accounts/urls.py created
- [ ] main/urls.py created
- [ ] URL namespacing implemented
- [ ] RESTful URL patterns followed

## Template System

### 1. Base Templates
```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{{ account.name }}{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <!-- Navigation -->
    </nav>
    
    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

- [ ] Base template created
- [ ] Bootstrap CSS/JS included
- [ ] Navigation structure implemented
- [ ] Message framework integrated

### 2. Context Processors
```python
# main/context_processors.py
def user_context(request):
    # Add user profile and account to all templates
```

- [ ] Context processors created
- [ ] User context processor implemented
- [ ] Context processors added to settings
- [ ] Template context tested

## View Patterns

### 1. Account-Scoped Views
```python
@login_required
def account_scoped_view(request, pk):
    try:
        user_profile = request.user.userprofile
        account = user_profile.account
        obj = get_object_or_404(YourModel, pk=pk, account=account)
        # ...
    except UserProfile.DoesNotExist:
        raise Http404("Access denied")
```

- [ ] Account-scoped view pattern implemented
- [ ] Permission decorators created
- [ ] Error handling configured
- [ ] View templates created

### 2. Authentication Views
- [ ] Login/logout views configured
- [ ] Registration views implemented (if needed)
- [ ] Password reset views configured
- [ ] Authentication templates created

## Static Files

### 1. Static File Configuration
```python
# settings.py
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = env('STATIC_ROOT')  # Environment-specific
```

- [ ] Static files directories created
- [ ] Static files configuration tested
- [ ] CSS/JS files organized
- [ ] collectstatic command tested

### 2. Media Files
- [ ] Media files configuration added
- [ ] Upload directories created
- [ ] File upload patterns implemented
- [ ] Media serving configured for development

## Testing

### 1. Test Framework
```python
# tests/test_models.py
from django.test import TestCase
from accounts.models import Account, UserProfile

class AccountModelTest(TestCase):
    def setUp(self):
        self.account = Account.objects.create(
            name="Test Account",
            slug="test-account"
        )
    
    def test_account_creation(self):
        self.assertEqual(self.account.name, "Test Account")
        self.assertTrue(self.account.is_active)
```

- [ ] Test directory structure created
- [ ] Model tests implemented
- [ ] View tests implemented
- [ ] Form tests implemented (if applicable)
- [ ] Test database configured

### 2. Test Execution
```bash
# Run tests
python manage.py test

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

- [ ] Test suite runs successfully
- [ ] Coverage measurement configured
- [ ] Test data fixtures created (if needed)
- [ ] Continuous integration setup planned

## Database Migrations

### 1. Initial Migrations
```bash
# Create migrations
python manage.py makemigrations accounts
python manage.py makemigrations main

# Apply migrations
python manage.py migrate
```

- [ ] Initial migrations created
- [ ] Migrations applied successfully
- [ ] Database schema verified
- [ ] Migration rollback tested

### 2. Data Migrations
- [ ] Data migration patterns established
- [ ] Initial data fixtures created
- [ ] Migration dependencies configured
- [ ] Migration testing procedure established

## Admin Interface

### 1. Admin Configuration
```python
# accounts/admin.py
from django.contrib import admin
from .models import Account, UserProfile

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
```

- [ ] Admin classes created for all models
- [ ] Admin interface customized
- [ ] Search and filtering configured
- [ ] Superuser account created

### 2. Admin Testing
- [ ] Admin interface tested
- [ ] CRUD operations verified
- [ ] Permissions tested
- [ ] Admin workflows documented

## Deployment Preparation

### 1. Server Requirements
- [ ] Server specifications documented
- [ ] Domain configuration planned
- [ ] SSL certificate requirements identified
- [ ] Backup strategy planned

### 2. Deployment Scripts
```bash
# server/dev/startserver.sh
#!/bin/bash
cd /var/www/projectname
source venv/bin/activate
python manage.py collectstatic --noinput
sudo systemctl start projectname_dev
sudo systemctl start nginx
```

- [ ] Start/stop scripts created
- [ ] Service configuration files created
- [ ] Nginx configuration prepared
- [ ] Systemd service files created

### 3. Production Checklist
- [ ] Production environment variables configured
- [ ] Database backups configured
- [ ] Log rotation configured
- [ ] Monitoring system planned
- [ ] Security audit completed

## Documentation

### 1. Project Documentation
- [ ] README.md created
- [ ] Installation instructions documented
- [ ] API documentation created (if applicable)
- [ ] Deployment instructions documented

### 2. Claude Context
```
claude/
├── CONTEXT_MEMORY.md           # Current project status
├── CODEBASE_STATE.md           # Architecture and file locations
├── DEV_HANDOFF.md              # Server-side actions needed after git pull
├── project_specifications.md   # Requirements and features
├── development_patterns.md     # Code patterns and conventions
└── session_progress/           # Daily session summaries
```

- [ ] Claude context directory created
- [ ] Project specifications documented
- [ ] Development patterns documented
- [ ] Context memory initialized
- [ ] DEV_HANDOFF.md created (see Deployment Workflow section)

### 3. Deployment Workflow Documentation

**Critical Pattern**: Claude does NOT automate server deployment. The workflow is:

1. Claude and user work locally (MacBook/dev machine)
2. Code is committed and pushed to repository
3. User manually SSHs to server, runs `git pull`, restarts service
4. Claude leaves handoff notes for server-side actions beyond normal pull

**DEV_HANDOFF.md Template:**
```markdown
# Dev Server Handoff Notes

**Last Updated:** YYYY-MM-DD

When you pull this to the dev server, here's what needs to happen beyond `git pull`:

---

## Current Handoff (YYYY-MM-DD)

### Required Steps After Pull:
- pip install -r requirements.txt (if new packages)
- python manage.py migrate (if new models)
- python manage.py collectstatic --noinput (if new templates/static)
- sudo systemctl restart servicename

### New Environment Variables:
- List any new .env/.keys variables needed

### Notes:
- Any special considerations for this deployment

---

## Handoff History

### YYYY-MM-DD - Description
- What changed, what actions were needed
```

- [ ] DEV_HANDOFF.md created with template structure
- [ ] Claude updates this file when changes need server-side action
- [ ] User checks this file after git pull on server

## Quality Assurance

### 1. Code Quality
- [ ] Code formatting standards established
- [ ] Linting configuration added
- [ ] Code review process planned
- [ ] Git commit message standards defined

### 2. Performance
- [ ] Database query optimization planned
- [ ] Static file optimization configured
- [ ] Caching strategy planned
- [ ] Performance monitoring planned

### 3. Security
- [ ] Security testing completed
- [ ] Vulnerability scanning planned
- [ ] Security headers configured
- [ ] Authentication security verified

## Go-Live Checklist

### 1. Pre-Launch
- [ ] All tests passing
- [ ] Performance testing completed
- [ ] Security audit completed
- [ ] Backup and recovery tested
- [ ] Monitoring systems active

### 2. Launch Day
- [ ] DNS records updated
- [ ] SSL certificates installed
- [ ] Database migrations applied
- [ ] Static files deployed
- [ ] Services started and verified

### 3. Post-Launch
- [ ] Application monitoring active
- [ ] Error tracking configured
- [ ] Performance monitoring active
- [ ] User feedback collection ready
- [ ] Maintenance procedures documented

## Common Pitfalls to Avoid

### Development
- [ ] ❌ Never use SQLite for any environment
- [ ] ❌ Don't commit .env or .keys files
- [ ] ❌ Don't use DEBUG=True in production
- [ ] ❌ Don't hardcode sensitive values
- [ ] ❌ Don't skip database migrations

### Security
- [ ] ❌ Don't use default SECRET_KEY
- [ ] ❌ Don't disable CSRF protection
- [ ] ❌ Don't use HTTP in production
- [ ] ❌ Don't expose debug information
- [ ] ❌ Don't use weak authentication

### Performance
- [ ] ❌ Don't ignore database indexing
- [ ] ❌ Don't serve media files through Django in production
- [ ] ❌ Don't skip static file optimization
- [ ] ❌ Don't ignore query optimization
- [ ] ❌ Don't skip caching strategies

## Success Criteria

### Technical
- [ ] Application runs without errors
- [ ] All tests pass
- [ ] Database operations work correctly
- [ ] Static files serve properly
- [ ] Authentication works correctly

### Business
- [ ] Core user workflows function
- [ ] Multi-tenant isolation works
- [ ] Performance meets requirements
- [ ] Security requirements met
- [ ] Deployment pipeline works

### Maintenance
- [ ] Documentation is complete
- [ ] Monitoring is active
- [ ] Backup procedures work
- [ ] Update procedures documented
- [ ] Support procedures established

## Post-Initialization

After completing this checklist:

1. **Begin feature development** - Start implementing business logic
2. **Set up CI/CD** - Configure automated testing and deployment
3. **Add monitoring** - Implement application and infrastructure monitoring
4. **Plan scaling** - Design for future growth and load requirements
5. **User testing** - Begin user acceptance testing and feedback collection

This checklist ensures your Django project starts with a solid foundation and follows proven patterns for scalability, security, and maintainability.