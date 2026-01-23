# Session Progress: First Production Deployment

**Date:** 2026-01-22
**Focus:** Deploy About Hampton Roads to production

---

## Session Overview

Completed the first production deployment of About Hampton Roads. The site is now live at https://abouthamptonroads.com with all content, drive calculator, and automated refresh timers.

---

## Major Accomplishments

### 1. Production Infrastructure Setup
- Created `/var/www/abouthamptonroads.com/prod` directory
- Cloned repo from GitHub
- Created production `.env` file (ENVIRONMENT=production, DEBUG=False)
- Copied `.keys` file with API credentials
- User's setup script handled gunicorn service, nginx config, and SSL certificate

### 2. Database Migration
- Dumped dev database using `pg_dump` (550KB)
- Restored to `abouthr_prod` database on postgres-private.o6.org
- Verified: 9 cities, 527 venues, 39 drive destinations

### 3. Static Files
- Ran `collectstatic` - 177 files copied to `/var/www/staticfiles/abouthamptonroads.com/prod/`

### 4. Systemd Timers for Production
Created and enabled production timers:
- `pulse-refresh-prod.timer` - Every 4 hours (00:00, 04:00, 08:00, 12:00, 16:00, 20:00)
- `venue-refresh-prod.timer` - Sundays at 3:00 AM

### 5. Content Sync Tooling (Earlier in Session)
- Created `PRODUCTION_DEPLOYMENT.md` guide
- Created `sync_content` management command for dev→prod data migration

---

## Files Created

| File | Purpose |
|------|---------|
| `/var/www/abouthamptonroads.com/prod/` | Production code directory |
| `/var/www/abouthamptonroads.com/prod/.env` | Production environment config |
| `/var/www/abouthamptonroads.com/gunicorn_config_prod.py` | Gunicorn config (port 8009) |
| `/etc/systemd/system/pulse-refresh-prod.service` | Pulse refresh service |
| `/etc/systemd/system/pulse-refresh-prod.timer` | Pulse refresh timer |
| `/etc/systemd/system/venue-refresh-prod.service` | Venue refresh service |
| `/etc/systemd/system/venue-refresh-prod.timer` | Venue refresh timer |
| `claude/PRODUCTION_DEPLOYMENT.md` | Deployment guide |
| `guide/management/commands/sync_content.py` | Content sync tool |

---

## Production URLs

| Page | URL | Status |
|------|-----|--------|
| Homepage | https://abouthamptonroads.com/ | ✅ 200 |
| Drive Calculator | https://abouthamptonroads.com/drive-calculator/ | ✅ 200 |
| City Page | https://abouthamptonroads.com/city/norfolk/ | ✅ 200 |
| Military | https://abouthamptonroads.com/military/ | ✅ 200 |
| CMS | https://abouthamptonroads.com/cms/ | ✅ 302 (login) |

---

## Technical Details

### Server Configuration
- **Gunicorn port:** 8009 (prod) vs 8008 (dev)
- **Static files:** `/var/www/staticfiles/abouthamptonroads.com/prod/`
- **Database:** `abouthr_prod` on `postgres-private.o6.org`

### Timers Schedule
| Timer | Schedule | Next Run |
|-------|----------|----------|
| pulse-refresh-prod | Every 4 hours | ~1h 20min |
| venue-refresh-prod | Sundays 3 AM | 2 days |

---

## Commands Reference

```bash
# Restart production
sudo systemctl restart gunicorn_abouthamptonroads_prod

# Check production logs
journalctl -u gunicorn_abouthamptonroads_prod -n 50

# Manual pulse refresh
cd /var/www/abouthamptonroads.com/prod && python manage.py refresh_pulse --force

# Check timers
systemctl list-timers | grep prod

# Deploy code updates
cd /var/www/abouthamptonroads.com/prod
git pull
python manage.py migrate
python manage.py collectstatic --no-input
sudo systemctl restart gunicorn_abouthamptonroads_prod
```

---

## Next Steps

1. [ ] Run initial pulse refresh on prod
2. [ ] Monitor production logs for errors
3. [ ] Test CMS login on production
4. [ ] Consider www redirect (www.abouthamptonroads.com → abouthamptonroads.com)
