# Django Deployment Standards

## Claude's Role in Deployment - IMPORTANT

**Claude does NOT automate server deployment.** The workflow is:

1. Claude and user work locally (MacBook/dev machine)
2. Code is committed and pushed to repository
3. User manually SSHs to server, runs `git pull`, restarts service
4. Claude leaves handoff notes in `claude/DEV_HANDOFF.md` when server-side actions are needed

### Handoff Notes (DEV_HANDOFF.md)

**Local Claude → Dev/Prod**: When pushing changes that require actions beyond `git pull`:
- New pip packages to install
- Migrations to run
- collectstatic needed
- New environment variables

**Dev Claude → Local**: When finishing work on the server, note:
- Any server-specific issues discovered
- Configuration changes made
- Things to test locally next

**Never create deployment automation scripts.** Just document what's needed.

---

## Overview
This document defines the standard deployment architecture, configuration, and procedures for Django applications. It covers development, staging, and production environments.

## Architecture Overview

### Three-Tier Deployment
```
Production (domain.com)           ← Users
    ↓
Development (dev.domain.com)      ← Testing and additional Development2
    ↓
Local (localhost)              ← Development
```

### Technology Stack
- **Web Server**: Nginx (reverse proxy, static files)
- **Application Server**: Gunicorn (WSGI server)
- **Database**: PostgreSQL (all environments)
- **Process Management**: Systemd (service management)
- **SSL/TLS**: Let's Encrypt (automated certificates)
- **Monitoring**: System logs, application logs

## Server Configuration

### System Requirements
- **OS**: Ubuntu 20.04 LTS or newer
- **Python**: 3.12+ (via pyenv)
- **PostgreSQL**: 14+
- **Nginx**: Latest stable
- **Memory**: Minimum 2GB RAM (4GB+ recommended)
- **Storage**: SSD with sufficient space for media files


### Directory Structure
```
/var/www/
├── projectname/               # Application code
│   ├── .pyenv/                 # Application virtual environment
│   ├── .env                  # Environment configuration
│   ├── .keys                 # Sensitive credentials
│   └── manage.py             # Django management
├── staticfiles_dev/          # Development static files
├── staticfiles_prod/         # Production static files
├── mediafiles_dev/           # Development media files
├── mediafiles_prod/          # Production media files
└── logs/                     # Application logs
    ├── gunicorn_dev.log
    └── gunicorn_prod.log
```


### Deployment Steps
1. **Pull latest code**: `git pull origin main`
2. **Update dependencies**: `pip install -r requirements.txt`
3. **Run migrations**: `python manage.py migrate`
4. **Collect static files**: `python manage.py collectstatic --noinput`
5. **Restart services**: `sudo systemctl restart projectname_dev`
6. **Test application**: Verify functionality
7. **Monitor logs**: Check for errors



This deployment standard ensures consistent, secure, and maintainable Django applications across all environments.