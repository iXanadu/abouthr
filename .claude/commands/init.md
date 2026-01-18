This is a NEW PROJECT initialization. Follow these steps:

## 1. Gather Project Information

Ask the user for:
- **Project name** (lowercase, no spaces, e.g., `myapp`)
- **Domain** (e.g., `myapp.trustworthyagents.com`)

## 2. Set Up Environment Files

```bash
# Copy base environment files
cp ~/.config/django-base/.env .env
cp ~/.config/django-base/.keys .keys
chmod 600 .keys
```

Then use the Edit tool to replace in `.env`:
- `PROJECTNAME` → actual project name (4 places)
- `YOURDOMAIN` → actual domain (8 places)

## 3. Generate and Set SECRET_KEY

Run this to generate a new key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Then update `.keys` replacing `GENERATE_NEW_KEY_FOR_EACH_PROJECT` with the generated key.

## 4. Initialize Django Project

```bash
django-admin startproject projectname .
```
(Use the actual project name)

## 5. Create Core Apps

```bash
python manage.py startapp core
python manage.py startapp accounts
```

## 6. Copy Code Patterns

Copy from `claude/examples/basic_project/code_patterns/`:
- `core_models.py` → `core/models.py`
- `accounts_models.py` → `accounts/models.py`
- `context_processors.py` → `accounts/context_processors.py`

## 7. Set Up Settings

Copy and customize settings:
- Copy `claude/examples/basic_project/settings.py` → `projectname/settings.py`
- Replace `projectname` with actual project name in ROOT_URLCONF and WSGI_APPLICATION

## 8. Copy Supporting Files

```bash
cp claude/examples/basic_project/.gitignore.template .gitignore
cp claude/examples/basic_project/CLAUDE.md.template CLAUDE.md
cp claude/examples/basic_project/code_patterns/CODEBASE_STATE.md.template claude/CODEBASE_STATE.md
cp claude/examples/basic_project/code_patterns/CONTEXT_MEMORY.md.template claude/CONTEXT_MEMORY.md
```

## 9. Read Project Specs

Read any files in `claude/specs/` (especially `prd.md`) to understand what this project should do.

## 10. Create Database (if needed)

Ask user if they want you to create the PostgreSQL databases. If yes, run these commands:

```bash
# Create dedicated user for this app
createuser -h postgres.o6.org -U db_admin projectname

# Set password (uses shared DB_PASSWORD from .keys)
psql -h postgres.o6.org -U db_admin -d postgres -c "ALTER USER projectname WITH PASSWORD 'R%qMuGnizHl^V0iD';"

# Grant db_admin ability to set ownership to new user
psql -h postgres.o6.org -U db_admin -d postgres -c "GRANT projectname TO db_admin;"

# Create dev and prod databases owned by app user
createdb -h postgres.o6.org -U db_admin -O projectname projectname_dev
createdb -h postgres.o6.org -U db_admin -O projectname projectname_prod
```
(Uses db_admin credentials from ~/.pgpass)

## 11. Run Initial Setup

```bash
pip install -r claude/examples/basic_project/requirements.txt
python manage.py makemigrations
python manage.py migrate
```

## 12. Update Project State

Update `claude/CODEBASE_STATE.md`:
- Mark completed setup steps
- Add project name and domain
- Update "Last Updated" date

Update `claude/CONTEXT_MEMORY.md`:
- Add project name, domain, database info
- Note any PRD/specs that were read

## 13. Summary

When complete, summarize:
- What was set up
- What the PRD says the project should do
- Suggested next steps based on the PRD
- Ask what the user wants to work on first
