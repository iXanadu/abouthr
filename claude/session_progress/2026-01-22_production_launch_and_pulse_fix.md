# Session Progress: Production Launch & Pulse Content Fix

**Date:** 2026-01-22 (evening)
**Focus:** First production deployment and fixing pulse content balance

---

## Session Overview

Completed the first production deployment of About Hampton Roads to https://abouthamptonroads.com. Also fixed the Hampton Roads Pulse headlines to exclude crime/tragedy content and focus on relocation-friendly news.

---

## Major Accomplishments

### 1. Production Deployment (LIVE!)

**Site is now live at:** https://abouthamptonroads.com

Deployment steps completed:
- Created `/var/www/abouthamptonroads.com/prod` directory via git clone
- Created production `.env` (ENVIRONMENT=production, DEBUG=False)
- Copied `.keys` file with API credentials
- User's setup script handled gunicorn, nginx, and SSL
- Cloned dev database to prod using pg_dump/pg_restore (550KB)
  - 9 cities, 527 venues, 39 drive destinations
- Ran collectstatic (177 files)
- Started gunicorn_abouthamptonroads_prod service

### 2. Production Systemd Timers

Created and enabled automated refresh timers:

| Timer | Schedule | Purpose |
|-------|----------|---------|
| `pulse-refresh-prod.timer` | Every 4 hours (00,04,08,12,16,20:00) | Refresh trends & headlines |
| `venue-refresh-prod.timer` | Sundays 3:00 AM | Refresh Google Places data |

### 3. Pulse Headlines Content Fix

**Problem:** Headlines were showing too much violent crime (murders, fires, missing persons) - inappropriate for a relocation guide.

**Solution:** Rewrote the headlines prompt with strict exclusions:

```
ABSOLUTELY EXCLUDE (non-negotiable):
- NO crime stories of any kind (shootings, murders, robberies, assaults)
- NO fires, accidents, or deaths
- NO missing persons cases
- NO court cases or arrests
- NO obituaries
- NO tragedy or disaster stories
```

**Key insight:** Added the test: "Would this headline make someone excited to relocate? If not, skip it."

Also updated trends prompt to be relocation-focused, though it was already more balanced.

---

## Files Modified

| File | Changes |
|------|---------|
| `guide/services/headlines_service.py` | Rewrote prompt to exclude all crime/tragedy, prioritize events/community news |
| `guide/services/trends_service.py` | Added relocation guide framing, limited negative content |
| `claude/CODEBASE_STATE.md` | Updated environment status to show prod running |
| `claude/CONTEXT_MEMORY.md` | Updated status to show production live |

---

## Server Files Created

| File | Purpose |
|------|---------|
| `/var/www/abouthamptonroads.com/prod/` | Production code directory |
| `/var/www/abouthamptonroads.com/prod/.env` | Production environment config |
| `/var/www/abouthamptonroads.com/prod/.keys` | API keys (copied from dev) |
| `/var/www/abouthamptonroads.com/gunicorn_config_prod.py` | Gunicorn config (port 8009) |
| `/etc/systemd/system/pulse-refresh-prod.service` | Pulse refresh service |
| `/etc/systemd/system/pulse-refresh-prod.timer` | Pulse refresh timer (4 hours) |
| `/etc/systemd/system/venue-refresh-prod.service` | Venue refresh service |
| `/etc/systemd/system/venue-refresh-prod.timer` | Venue refresh timer (weekly) |

---

## Production URLs

| Page | URL |
|------|-----|
| Homepage | https://abouthamptonroads.com/ |
| Drive Calculator | https://abouthamptonroads.com/drive-calculator/ |
| Norfolk | https://abouthamptonroads.com/city/norfolk/ |
| Military | https://abouthamptonroads.com/military/ |
| CMS | https://abouthamptonroads.com/cms/ |

---

## Database Details

Cloned from dev to prod:
- **Database:** `abouthr_prod` on `postgres-private.o6.org`
- **Content:** 9 cities, 527 venues, 39 drive destinations
- **Method:** `pg_dump -Fc` → `pg_restore --clean --if-exists`

---

## Commands Reference

### Production Management
```bash
# Restart production
sudo systemctl restart gunicorn_abouthamptonroads_prod

# View logs
journalctl -u gunicorn_abouthamptonroads_prod -n 50

# Check timers
systemctl list-timers | grep prod
```

### Deploying Updates to Production
```bash
cd /var/www/abouthamptonroads.com/prod
git pull
python manage.py migrate
python manage.py collectstatic --no-input
sudo systemctl restart gunicorn_abouthamptonroads_prod
```

### Refreshing Pulse Content
```bash
# Dev
cd /var/www/abouthamptonroads.com/dev
python manage.py refresh_pulse --force

# Prod
cd /var/www/abouthamptonroads.com/prod
python manage.py refresh_pulse --force
```

---

## Lessons Learned

1. **RSS feeds are crime-heavy:** Local TV news RSS feeds (WAVY, 13 News Now) are dominated by crime stories. Need explicit AI filtering.

2. **"Major public safety issue" is too vague:** The AI interpreted fatal fires and missing children as "major public safety issues." Had to use explicit hard excludes.

3. **Relocation guide framing works:** Adding "Would this make someone excited to relocate?" as a test helped the AI understand the content goal.

---

## Next Session Priorities

1. [ ] Monitor pulse content quality over time
2. [ ] Test on mobile devices
3. [ ] Consider www redirect (www.abouthamptonroads.com → abouthamptonroads.com)
4. [ ] City-specific pulse content (future feature)
