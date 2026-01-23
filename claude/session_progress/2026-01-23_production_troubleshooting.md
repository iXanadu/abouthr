# Session Progress: Production Troubleshooting

**Date:** 2026-01-23
**Focus:** Fix production deployment issues and document infrastructure responsibilities

---

## Session Overview

Production site at https://abouthamptonroads.com was returning "Bad Request (400)" errors. Troubleshot and resolved issues caused by conflicting setup between user's website setup script and Claude's manual configuration during initial deployment.

---

## Major Accomplishments

### 1. Diagnosed Production 400 Error

**Root Cause:** Port mismatch between nginx and gunicorn
- nginx config was proxying to port **8009**
- gunicorn_config_prod.py was binding to port **8014**
- Port 8009 was actually used by trustworthyagents.com

**Resolution:** User updated nginx config to proxy to port 8014:
```bash
sudo sed -i 's/127.0.0.1:8009/127.0.0.1:8014/' /etc/nginx/sites-enabled/abouthamptonroads_prod
sudo nginx -t && sudo systemctl reload nginx
```

### 2. Fixed Google Maps API Referrer Error

**Symptom:** Drive Calculator autocomplete returning 403 Forbidden
```
RpcError: Requests from referer https://abouthamptonroads.com are blocked.
```

**Root Cause:** Google API key HTTP referrer restrictions had:
- `*.abouthamptonroads.com/*` (matches subdomains only)
- `abouthamptonroads.com/*` (missing protocol)

**Resolution:** User added `https://abouthamptonroads.com/*` to API key restrictions in Google Cloud Console. Note: wildcard `*.domain.com` does NOT match bare domain.

### 3. Documented Infrastructure Responsibilities

Updated documentation to clarify that Claude should NOT configure:
- Nginx configs
- SSL certificates
- Gunicorn systemd services
- Server infrastructure

These are handled by the user's website setup script.

---

## Files Modified

| File | Changes |
|------|---------|
| `claude/PRODUCTION_DEPLOYMENT.md` | Added "Infrastructure Setup" section at top clarifying user responsibility |
| `claude/DEV_HANDOFF.md` | Added infrastructure responsibility note, documented resolved issues |
| `CLAUDE.md` | Updated deployment workflow section with infrastructure guidelines |

---

## Technical Decisions

### Infrastructure Ownership
- User's website setup script handles: nginx, SSL, gunicorn services, systemd timers, ports
- Claude handles: Django code, migrations, seeding, static files, documentation
- If infrastructure changes needed, Claude documents in DEV_HANDOFF.md and asks user

---

## Production Status

Site is now fully operational:
- Homepage: https://abouthamptonroads.com/ ✅
- Drive Calculator: https://abouthamptonroads.com/drive-calculator/ ✅
- City pages with weather ✅
- Google Maps API (autocomplete, directions) ✅
- CMS login ✅

---

## Pending / Next Session

1. [ ] Add favicon.ico (currently 404)
2. [ ] Test on real mobile devices
3. [ ] Monitor production logs for any errors
4. [ ] Consider www redirect (www → non-www)
5. [ ] City-specific pulse content
6. [ ] Search functionality
