# Server Commands Reference

## Systemctl - Service Management

### Find Services
```bash
# List running services (filtered by keyword)
systemctl list-units --type=service --state=running | grep <keyword>

# List ALL services including stopped
systemctl list-units --type=service --all | grep <keyword>

# Common keywords to search: gunicorn, uwsgi, django, nginx, postgres
```

### Service Status & Logs
```bash
# Check service status (shows recent logs too)
systemctl status <service-name>

# Follow logs in real-time
journalctl -u <service-name> -f

# View last 50 log lines
journalctl -u <service-name> -n 50
```

### Restart Services
```bash
# Restart a service
sudo systemctl restart <service-name>

# Stop / Start
sudo systemctl stop <service-name>
sudo systemctl start <service-name>

# Reload config without full restart (if supported)
sudo systemctl reload <service-name>
```

## This Project's Services

| Environment | Service Name | Port | Config File |
|-------------|--------------|------|-------------|
| Development | `gunicorn_abouthamptonroads_dev` | 8008 | `/var/www/abouthamptonroads.com/gunicorn_config_dev.py` |
| Production  | `gunicorn_abouthamptonroads_prod` | TBD | TBD |

**Working Directory:** `/var/www/abouthamptonroads.com/dev/`
**Virtual Environment:** `abouthr-3.12.0`
**WSGI Module:** `abouthr.wsgi:application`

### Quick Commands
```bash
# Restart dev (REQUIRED after any Python file changes)
sudo systemctl restart gunicorn_abouthamptonroads_dev

# Restart prod
sudo systemctl restart gunicorn_abouthamptonroads_prod

# Check dev status
systemctl status gunicorn_abouthamptonroads_dev

# Check dev logs
journalctl -u gunicorn_abouthamptonroads_dev -n 50

# Find running gunicorn process (alternative method)
ps aux | grep abouthr | grep gunicorn
```

### When to Restart
Gunicorn does NOT auto-reload. Restart is required after:
- Changes to views, urls, models, forms, or any Python files
- Adding new apps or URL patterns
- Modifying settings.py

Template changes do NOT require restart (Django reloads them automatically).

## Nginx

```bash
# Test nginx config before reload
sudo nginx -t

# Reload nginx (applies config changes)
sudo systemctl reload nginx

# Restart nginx (full restart)
sudo systemctl restart nginx
```

## Service Naming Pattern

Gunicorn services follow: `gunicorn_<projectname>_<env>.service`

Examples from this server:
- `gunicorn_abouthamptonroads_dev`
- `gunicorn_trustworthyagents_prod`
- `gunicorn_757openhouse_prod`
