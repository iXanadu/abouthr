# Production Deployment Guide

## IMPORTANT: Infrastructure Setup

**Claude should NOT configure server infrastructure.** The following are set up by the user using their website setup script:

- Nginx configuration (sites-available/sites-enabled)
- SSL certificates (Let's Encrypt/Certbot)
- Gunicorn systemd services
- Systemd timers
- User accounts and permissions
- Firewall rules

Claude's role is limited to:
- Django application code and configuration
- Database migrations and seeding
- Static file collection
- Documentation

If infrastructure changes are needed, Claude should document what's required in `DEV_HANDOFF.md` and let the user handle the actual setup.

---

## Environment Overview

```
┌─────────────┐     ┌─────────────────────────────────┐     ┌──────────────┐
│   MacBook   │     │      Ubuntu Server              │     │  PostgreSQL  │
│   (local)   │────▶│  dev.abouthamptonroads.com      │────▶│   Server     │
│             │     │  abouthamptonroads.com (prod)   │     │              │
└─────────────┘     └─────────────────────────────────┘     │ abouthr_dev  │
      │                       │                             │ abouthr_prod │
      │         git push      │  git pull                   └──────────────┘
      └───────────────────────┘
```

---

## Initial Production Setup (One-Time)

### Option A: Clone Dev Database (Recommended)

This gives you all content, settings, and enrichment data immediately.

```bash
# On PostgreSQL server
pg_dump -U abouthr_user abouthr_dev > /tmp/abouthr_backup.sql
psql -U abouthr_user abouthr_prod < /tmp/abouthr_backup.sql
```

### Option B: Fresh Database

```bash
# On production server
cd /var/www/abouthamptonroads.com/prod

# Run migrations
python manage.py migrate

# Seed all data
python manage.py seed_data
python manage.py seed_ai_models
python manage.py seed_destinations

# Then enrich venues (this calls Google API)
python manage.py enrich_venues --all
```

### Production Configuration

1. **Create `.env` file** (copy from dev, update):
```bash
cp /var/www/abouthamptonroads.com/dev/.env .env
# Edit: Change DATABASE_URL to abouthr_prod
# Edit: Change DEBUG=False
# Edit: Update ALLOWED_HOSTS
```

2. **Copy `.keys` file**:
```bash
cp /var/www/abouthamptonroads.com/dev/.keys .keys
```

3. **Collect static files**:
```bash
python manage.py collectstatic --no-input
```

4. **Set up systemd service** (gunicorn_abouthamptonroads_prod)

---

## Regular Deployments

### Standard Deploy (Code Only)

When you've pushed code changes that don't affect data:

```bash
cd /var/www/abouthamptonroads.com/prod
git pull origin main
python manage.py migrate           # Always safe to run
python manage.py collectstatic --no-input
sudo systemctl restart gunicorn_abouthamptonroads_prod
```

### With New Reference Data

When you've added new DriveDestinations, AIModels, etc:

```bash
# After git pull...
python manage.py seed_destinations  # Idempotent - uses update_or_create
python manage.py seed_ai_models     # Idempotent
```

---

## Content Sync Strategies

### Content Categories

| Category | Examples | Sync Strategy |
|----------|----------|---------------|
| **Schema** | Tables, columns | `migrate` (always safe) |
| **Reference Data** | DriveDestination, AIModel, Region | Idempotent seed commands |
| **CMS Content** | Cities, Venues, Testimonials | Manual or sync_content tool |
| **API Data** | Ratings, photos, Pulse | Don't sync - refetch fresh |
| **Logs** | AIUsageLog | Never sync |

### Using sync_content Command

```bash
# EXPORT from dev
cd /var/www/abouthamptonroads.com/dev
python manage.py sync_content --export --type=reference > /tmp/reference.json
python manage.py sync_content --export --type=cms > /tmp/cms.json

# IMPORT to prod
cd /var/www/abouthamptonroads.com/prod
python manage.py sync_content --import /tmp/reference.json --preview  # Dry run
python manage.py sync_content --import /tmp/reference.json            # Apply

python manage.py sync_content --import /tmp/cms.json --preview
python manage.py sync_content --import /tmp/cms.json
```

### What NOT to Sync

- **Venue enrichment data** (rating, photos, hours) - Let prod fetch fresh from Google
- **PulseContent** - Auto-refreshes every 4 hours
- **AIUsageLog** - Production tracking data
- **User accounts** - May differ between environments

---

## Refreshing API Data on Production

After initial deploy, set up the refresh timers:

```bash
# Pulse refresh (every 4 hours)
sudo systemctl enable pulse-refresh.timer
sudo systemctl start pulse-refresh.timer

# Venue refresh (weekly)
sudo systemctl enable venue-refresh.timer
sudo systemctl start venue-refresh.timer

# Verify timers
systemctl list-timers | grep -E "(pulse|venue)"
```

Or run manually:
```bash
python manage.py refresh_pulse --force
python manage.py enrich_venues --all
```

---

## Rollback Procedures

### Code Rollback

```bash
git log --oneline -5              # Find previous commit
git checkout <commit-hash>        # Checkout previous version
python manage.py migrate          # May need reverse migrations
sudo systemctl restart gunicorn_abouthamptonroads_prod
```

### Database Rollback

```bash
# If you have a backup
psql -U abouthr_user abouthr_prod < backup_before_deploy.sql
```

### Quick Database Backup Before Deploy

```bash
pg_dump -U abouthr_user abouthr_prod > ~/backups/prod_$(date +%Y%m%d_%H%M).sql
```

---

## Checklist: First Production Deploy

- [ ] PostgreSQL database `abouthr_prod` created
- [ ] Database user has access to prod database
- [ ] Clone dev data OR run seed commands
- [ ] Production `.env` configured (DEBUG=False, correct DB)
- [ ] `.keys` file copied with all API keys
- [ ] `collectstatic` run
- [ ] Gunicorn systemd service configured and started
- [ ] Nginx configured for production domain
- [ ] SSL certificate (Let's Encrypt) installed
- [ ] DNS configured for abouthamptonroads.com
- [ ] Systemd timers enabled (pulse-refresh, venue-refresh)
- [ ] Test all pages load correctly
- [ ] Test CMS login works
- [ ] Test Drive Calculator API calls work

---

## Quick Reference

```bash
# Dev server
sudo systemctl restart gunicorn_abouthamptonroads_dev
journalctl -u gunicorn_abouthamptonroads_dev -n 50

# Prod server
sudo systemctl restart gunicorn_abouthamptonroads_prod
journalctl -u gunicorn_abouthamptonroads_prod -n 50

# Database backup
pg_dump -U abouthr_user abouthr_prod > backup.sql

# Check timers
systemctl list-timers | grep abouthr
```
