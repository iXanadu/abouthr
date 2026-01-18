# Django Project Examples

## Quick Start

1. **Choose your project type**:
   - `basic_project/` - Simple Django app with accounts and auth
   - `saas_project/` - Multi-tenant SaaS with Google OAuth, common external services
   - `external_apis/` - Project with Google, AI services, and other integrations

2. **Copy example files**:
   ```bash
   cp examples/basic_project/.env.example .env
   cp examples/basic_project/.keys.example .keys
   cp examples/basic_project/settings.py projectname/settings.py
   cp examples/basic_project/requirements.txt .
   ```

3. **Copy code patterns** (from basic_project/code_patterns/):
   ```bash
   cp examples/basic_project/code_patterns/core_models.py core/models.py
   cp examples/basic_project/code_patterns/accounts_models.py accounts/models.py
   cp examples/basic_project/code_patterns/context_processors.py accounts/context_processors.py
   ```

4. **Edit with your actual values**:
   ```bash
   nano .env      # Update database URLs, domains, hosts
   nano .keys     # Replace placeholder values with real keys
   ```

5. **Generate new secret key**:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

6. **Set proper permissions**:
   ```bash
   chmod 600 .keys
   chmod 644 .env
   ```

---

## Project Types

### Basic Project (`basic_project/`)
**Use for**: Simple Django applications with core functionality
- Account-based multi-tenancy
- PostgreSQL database
- Basic authentication
- Static/media files
- REST API support
- Crispy forms with Bootstrap 5

**Contents**:
- `.env.example` - Environment configuration
- `.keys.example` - Sensitive credentials
- `settings.py` - Django settings with environment support
- `requirements.txt` - Core dependencies
- `code_patterns/` - Model and utility patterns
- `scripts/` - Utility scripts

### SaaS Project (`saas_project/`)
**Use for**: Multi-tenant SaaS applications with common integrations
- All basic features plus:
- Google OAuth integration
- Ready for payment processing (Stripe)
- Ready for email services (SendGrid)
- Ready for background tasks (Celery/Redis)

### External APIs (`external_apis/`)
**Use for**: Projects with extensive third-party integrations
- Google Workspace (Drive, Calendar, OAuth)
- AI Services (OpenAI, Anthropic)
- Payment processing (Stripe)
- Cloud services (AWS)
- PDF processing

---

## Code Patterns (`basic_project/code_patterns/`)

### Core Models (`core_models.py`)
Abstract base models for all applications:
- `BaseModel` - Timestamps (created_at, updated_at)
- `AccountScopedModel` - Multi-tenant data isolation
- `UserTrackingModel` - Audit trail (created_by, modified_by)

### Account Models (`accounts_models.py`)
Multi-tenant foundation:
- `Account` - Organization/tenant entity
- `AccountSettings` - Per-account configuration
- `UserProfile` - Extended user with roles and permissions

### Context Processors (`context_processors.py`)
Template context helpers:
- `user_context` - Adds user profile, account, and role info to all templates

### Documentation Templates
- `CLAUDE.md.template` - Project instructions for Claude Code
- `CODEBASE_STATE.md.template` - Technical state tracking
- `CONTEXT_MEMORY.md.template` - Working context tracking
- `.gitignore.template` - Comprehensive gitignore

---

## Key Management

### Security Notes
- **Never commit .keys files** to version control
- **Always use .keys.example** as template with placeholder values
- **Generate new SECRET_KEY** for each project
- **Use environment-specific keys** (separate dev/prod keys)
- **Rotate keys regularly** in production

### Common Key Labels
All examples use consistent key labels:
- `SECRET_KEY` - Django secret key
- `DB_PASSWORD` - Database password
- `GOOGLE_CLIENT_ID` - Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Google OAuth client secret

---

## Customization

### Database Configuration
Default assumes PostgreSQL with these naming conventions:
- Development: `projectname_dev`
- Production: `projectname_prod`

### Domain Configuration
Update these in `.env`:
- `DEV_DOMAIN` - Development domain (e.g., dev.yourdomain.com)
- `PROD_DOMAIN` - Production domain (e.g., yourdomain.com)
- `DEV_ALLOWED_HOSTS` - Development allowed hosts
- `PROD_ALLOWED_HOSTS` - Production allowed hosts

---

## Next Steps

After copying and configuring:
1. **Test database connection**: `python manage.py check --database default`
2. **Run migrations**: `python manage.py migrate`
3. **Create superuser**: `python manage.py createsuperuser`
4. **Collect static files**: `python manage.py collectstatic`
5. **Run development server**: `python manage.py runserver`

---

## Troubleshooting

### Common Issues
- **Database connection errors**: Check `DB_PASSWORD` in `.keys` and database URLs in `.env`
- **Secret key errors**: Generate new `SECRET_KEY`
- **Permission errors**: Ensure `.keys` has 600 permissions
- **Static files not loading**: Check static root paths and run `collectstatic`

### Validation Commands
```bash
# Check Django configuration
python manage.py check

# Test database connection
python manage.py dbshell

# Validate environment
./scripts/check_env
```
