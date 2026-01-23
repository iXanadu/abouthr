# [Project Name] - Django Application

## Project Overview
Brief description of what this application does and its purpose.

---

## Critical Rules - NEVER VIOLATE THESE

### Architecture Summary (Quick Reference)
```
Views → Business Logic (Services/Managers) → Database Models
```

### Critical Rules
1. **Always use AccountScopedModel** for multi-tenant data isolation
2. **Never commit .env or .keys files** - use .example files as templates
3. **PostgreSQL only** - no SQLite, even for local development
4. **Test before commit** - run tests before committing changes

---

## Common Commands

### Django Development
```bash
# Start development server
python manage.py runserver

# Run all tests
python manage.py test

# Database operations
python manage.py makemigrations
python manage.py migrate
python manage.py showmigrations

# Create superuser
python manage.py createsuperuser

# Static files
python manage.py collectstatic --no-input

# Shell
python manage.py shell
```

### Testing
```bash
# Run tests
python manage.py test

# Run specific test
python manage.py test app_name.tests.test_module
```

### Git Workflow
```bash
git status
git add .
git commit -m "Description of changes"
git push origin branch-name
```

---

## Documentation Index

### Essential Docs (claude/ folder)
- **CODEBASE_STATE.md** - Current technical state and next tasks
- **CONTEXT_MEMORY.md** - Working context and priorities
- **DEV_HANDOFF.md** - Server-side actions needed after git pull
- **session_progress/** - Session history and progress notes

### Reference
- DJANGO_PROJECT_TEMPLATE.md - Model/view/template patterns
- ENVIRONMENT_SETUP_GUIDE.md - Environment configuration
- DEPLOYMENT_STANDARDS.md - Deployment procedures

---

## Development Workflow

### Starting a Session
1. Read `claude/CODEBASE_STATE.md` for current state
2. Check recent `claude/session_progress/` files
3. Verify environment is configured correctly

### Before Making Changes
1. Understand the architecture layer you're working in
2. Check for existing patterns in codebase
3. Plan approach before coding

### Before Committing
- [ ] All tests pass
- [ ] No debug code remains
- [ ] Documentation updated if needed

---

## Deployment Workflow - IMPORTANT

**Claude does NOT automate server deployment.** The workflow is:

1. Claude and user work locally (MacBook/dev machine)
2. Code is committed and pushed to repository
3. User manually SSHs to server, runs `git pull`, restarts service
4. Claude leaves handoff notes when server-side actions are needed

### Infrastructure Setup - USER RESPONSIBILITY

**Claude should NEVER configure server infrastructure.** These are handled by the user's website setup script:
- Nginx configuration (sites-available/sites-enabled)
- SSL certificates (Let's Encrypt/Certbot)
- Gunicorn systemd services and ports
- Systemd timers
- User accounts and permissions

If infrastructure changes are needed, Claude should **ask first** and document requirements in `DEV_HANDOFF.md` rather than making changes directly.

### DEV_HANDOFF.md Pattern

When pushing changes that require server-side actions beyond `git pull`:
- Update `claude/DEV_HANDOFF.md` with required steps
- Include: new pip packages, migrations, collectstatic, new env vars
- This tells "server Claude" or user what to do after pulling

**Never create deployment automation scripts.** Just document what's needed.

---

## Code Standards

### Python/Django
- Follow PEP 8 style guidelines
- Use type hints where beneficial
- Business logic in services/managers, NOT in views
- Use Django ORM for database queries

### JavaScript
- Modern ES6+ syntax
- Prefer `const` and `let` over `var`
- Use template literals for string interpolation

---

## Key Technical Details

### Multi-Tenancy Pattern
All models inherit from `AccountScopedModel`:
```python
from core.models import AccountScopedModel

class YourModel(AccountScopedModel):
    name = models.CharField(max_length=255)
    # account field is inherited automatically
```

### Environment Configuration
- `.env` - Non-sensitive configuration
- `.keys` - Sensitive credentials (never commit)
- Three environments: local, development, production

---

## Quick Troubleshooting

### Database Connection Issues
→ Check `DB_PASSWORD` in `.keys` and database URL in `.env`

### Static Files Not Loading
→ Run `python manage.py collectstatic`

### Authentication Errors
→ Check LOGIN_URL setting and authentication backend

---

## Session Progress Tracking

After significant work, create a session progress file:
```
claude/session_progress/YYYY-MM-DD_brief_description.md
```

Include:
- Session overview and objectives
- Major accomplishments
- Files modified
- Pending tasks for next session
