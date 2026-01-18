# Django Project Template for Claude Code

## Overview
This template folder contains reusable documentation, configuration examples, and code patterns for starting new Django projects with Claude Code. Based on proven patterns from production Django applications.

**Last Updated:** January 2026

---

## Quick Start

```bash
# 1. Create project folder and copy template
mkdir ~/pyprojects/myproject
cd ~/pyprojects/myproject
cp -r ~/pyprojects/claude_template/. .

# 2. Set up pyenv
pyenv virtualenv 3.12 myproject_3.12
pyenv local myproject_3.12

# 3. (Optional) Add your PRD
nano claude/specs/prd.md

# 4. Start Claude and initialize
claude
/init
```

Claude will ask for **project name** and **domain**, then automatically:
- Copy and configure `.env` and `.keys` from `~/.config/django-base/`
- Generate a new SECRET_KEY
- Initialize Django project
- Create core and accounts apps
- Copy code patterns and run migrations

### For Existing Projects
```bash
cd ~/pyprojects/myproject
claude
/startup
```

---

## Contents

### Documentation (claude/ folder)

| File | Purpose |
|------|---------|
| `DJANGO_PROJECT_TEMPLATE.md` | Complete Django patterns and architecture guide |
| `ENVIRONMENT_SETUP_GUIDE.md` | Step-by-step environment setup instructions |
| `PROJECT_INITIALIZATION_CHECKLIST.md` | Comprehensive new project checklist |
| `DEPLOYMENT_STANDARDS.md` | Production deployment procedures |
| `DEV_HANDOFF.md` | Server-side action notes for after git pull |

### Examples (claude/examples/ folder)

| Folder | Use For |
|--------|---------|
| `basic_project/` | Simple Django apps with accounts and auth |
| `saas_project/` | Multi-tenant SaaS with Google OAuth, payments |
| `external_apis/` | Projects with extensive third-party integrations |

### Code Patterns (claude/examples/basic_project/code_patterns/)

| File | Purpose |
|------|---------|
| `core_models.py` | BaseModel, AccountScopedModel, UserTrackingModel |
| `accounts_models.py` | Account, AccountSettings, UserProfile models |
| `context_processors.py` | User context for templates |
| `CLAUDE.md.template` | Project instructions for Claude Code |
| `CODEBASE_STATE.md.template` | Technical state tracking |
| `CONTEXT_MEMORY.md.template` | Working context tracking |

### Claude Commands (.claude/commands/)

| Command | Purpose |
|---------|---------|
| `/init` | **New projects only** - Initialize Django, configure env, create apps |
| `/startup` | Resume work - read state, context, recent progress |
| `/wrapup` | Session end - create progress notes |

---

## Key Principles

### PostgreSQL Everywhere
Never use SQLite, even for local development. This ensures:
- Consistency across all environments
- Early detection of database-specific issues
- Realistic performance characteristics

### Multi-Tenant by Default
All models use `AccountScopedModel` for data isolation:
```python
from core.models import AccountScopedModel

class YourModel(AccountScopedModel):
    name = models.CharField(max_length=255)
    # account field is inherited automatically
```

### Security First
- Credentials separated: `.env` (config) vs `.keys` (secrets)
- SSL everywhere (dev and prod)
- Proper security headers (HSTS, CSRF, etc.)

### Three-Tier Architecture
```
Local (localhost)           → Development machine
Development (dev.domain)    → Testing server with SSL
Production (domain)         → Live server
```

### Deployment Workflow
**Critical**: Claude does NOT automate server deployment. The workflow is:

1. Claude and user work locally (MacBook/dev machine)
2. Code is committed and pushed to repository
3. User manually SSHs to server, runs `git pull`, restarts service
4. **Claude leaves handoff notes** in `DEV_HANDOFF.md` when server-side actions are needed beyond normal pull

This file tells "server Claude" or the user what steps are needed after git pull:
- New pip packages to install
- Migrations to run
- Collectstatic needed
- New environment variables
- Any special considerations

---

## Environment Configuration

### .env (Non-sensitive config)
```bash
ENVIRONMENT=local
DEBUG=True
DEV_DATABASE_URL=postgres://user@host:5432/db_dev
PROD_DATABASE_URL=postgres://user@host:5432/db_prod
DEV_DOMAIN=dev.yourdomain.com
PROD_DOMAIN=yourdomain.com
```

### .keys (Sensitive credentials)
```bash
SECRET_KEY=your-django-secret-key
DB_PASSWORD=your-database-password
GOOGLE_CLIENT_ID=your-oauth-client-id
GOOGLE_CLIENT_SECRET=your-oauth-secret
```

---

## Dependencies

### Core Requirements
- Python 3.12+
- Django 5.2+
- PostgreSQL 14+
- django-environ
- psycopg2-binary

### Production Requirements
- Nginx (reverse proxy)
- Gunicorn (WSGI server)
- Let's Encrypt (SSL certificates)

### Version Management Strategy

**Patch versions** (e.g., 5.2.3 → 5.2.4): Update regularly, low risk. These contain bug fixes and security patches.

**Minor versions** (e.g., 5.2 → 5.3): Update every few months. Test in development first. Usually backward compatible but may deprecate features.

**Major versions** (e.g., 5.x → 6.x): Plan it carefully. Read the release notes and changelog. May require code changes.

**When to update:**
- Security advisories: Update immediately
- Starting a new project: Use latest stable versions
- Existing projects: Update patch versions regularly, minor versions quarterly
- Before adding major features: Good time to update dependencies

**Checking for updates:**
```bash
pip list --outdated                    # See outdated packages
pip install --upgrade package-name     # Update specific package
```

---

## Project Structure (After Setup)

```
myproject/
├── .claude/
│   └── commands/
│       ├── startup.md
│       └── wrapup.md
├── claude/
│   ├── CODEBASE_STATE.md
│   ├── CONTEXT_MEMORY.md
│   ├── DEV_HANDOFF.md       # Server-side actions after git pull
│   ├── session_progress/
│   └── [reference docs]
├── core/
│   └── models.py          # Base models
├── accounts/
│   ├── models.py          # Account, UserProfile
│   └── context_processors.py
├── myproject/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── templates/
├── static/
├── .env
├── .keys
├── .gitignore
├── CLAUDE.md
├── requirements.txt
└── manage.py
```

---

## Common Commands

### Development
```bash
python manage.py runserver              # Start dev server
python manage.py makemigrations         # Create migrations
python manage.py migrate                # Apply migrations
python manage.py createsuperuser        # Create admin user
python manage.py test                   # Run tests
python manage.py shell                  # Django shell
```

### Static Files
```bash
python manage.py collectstatic          # Collect static files (for deployment)
```

### Database
```bash
python manage.py dbshell                # Connect to database
python manage.py showmigrations         # List migration status
```

### Server Deployment
```bash
# Restart gunicorn (replace projectname and environment)
sudo systemctl restart gunicorn_projectname_dev.service
sudo systemctl status gunicorn_projectname_dev.service --no-pager

# View logs
sudo journalctl -u gunicorn_projectname_dev.service -n 50 --no-pager
```

---

## Customization Guide

### Replacing Placeholders
Throughout the template files, replace:
- `projectname` → Your actual project name
- `yourdomain.com` → Your actual domain
- `myproject` → Your Django project folder name

### Adding Domain Apps
1. Create the app: `python manage.py startapp myapp`
2. Use `AccountScopedModel` for multi-tenant data
3. Add to `INSTALLED_APPS` in settings.py
4. Create URLs, views, templates following existing patterns

---

## Support

These templates are based on proven patterns from production Django applications. They emphasize:
- **Rapid development** with solid foundations
- **Production readiness** from day one
- **Security best practices** throughout
- **Scalable architecture** patterns
- **Maintainable code** structures

---

**Note**: This template assumes you're working with Claude Code and following established patterns for Django applications with PostgreSQL, multi-tenancy, and production deployment.
