# Systemd Service Configuration

This directory contains systemd unit files for scheduled tasks.

## Venue Refresh Timer

Automatically refreshes stale venue data from Google Places API every Sunday at 3:00 AM.

### Installation

1. Copy the unit files to systemd directory:
```bash
sudo cp venue-refresh.service /etc/systemd/system/
sudo cp venue-refresh.timer /etc/systemd/system/
```

2. Reload systemd daemon:
```bash
sudo systemctl daemon-reload
```

3. Enable and start the timer:
```bash
sudo systemctl enable venue-refresh.timer
sudo systemctl start venue-refresh.timer
```

### Managing the Timer

```bash
# Check timer status
sudo systemctl status venue-refresh.timer

# List all timers
sudo systemctl list-timers

# View next scheduled run
sudo systemctl list-timers venue-refresh.timer

# Manually trigger a run
sudo systemctl start venue-refresh.service

# View logs
sudo journalctl -u venue-refresh.service -f

# View last run output
sudo journalctl -u venue-refresh.service --since "1 hour ago"
```

### Disabling

```bash
sudo systemctl stop venue-refresh.timer
sudo systemctl disable venue-refresh.timer
```

## Notes

- The timer runs as `abouthr_user` for proper file permissions
- Environment variables are loaded from `.env` and `.keys` files
- Logs are written to the systemd journal
- Timer persists across reboots
