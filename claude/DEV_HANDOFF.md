# Development Handoff Notes

This file contains server-side actions needed after `git pull`.

---

## 2026-01-21: Venue Enrichment System

### Summary
Implemented Google Places API integration to enrich venue data with ratings, reviews, hours, photos, and location data.

### Required Actions After `git pull`

1. **Run migrations:**
   ```bash
   python manage.py migrate guide
   ```

2. **Add Google Places API key to .keys file:**
   ```bash
   echo "GOOGLE_PLACES_API_KEY=your-api-key-here" >> .keys
   ```

   Get your API key from Google Cloud Console:
   - Enable "Places API (New)" in APIs & Services
   - Create credentials > API Key
   - Restrict the key to "Places API (New)" only

3. **Collect static files:**
   ```bash
   python manage.py collectstatic --no-input
   ```

4. **Restart the service:**
   ```bash
   sudo systemctl restart gunicorn
   ```

### Optional: Set Up Weekly Refresh Timer

To automatically refresh stale venue data weekly:

```bash
# Copy systemd files
sudo cp systemd/venue-refresh.service /etc/systemd/system/
sudo cp systemd/venue-refresh.timer /etc/systemd/system/

# Enable and start timer
sudo systemctl daemon-reload
sudo systemctl enable venue-refresh.timer
sudo systemctl start venue-refresh.timer

# Verify timer is active
sudo systemctl list-timers | grep venue
```

### Using the Feature

1. **Enable the API in CMS:**
   - Go to CMS > Settings (sidebar)
   - Click "Enable API" for Google Places
   - Configure venues per city if needed

2. **Sync venues:**
   - Use the Settings page to sync all cities
   - Or use individual "Sync" buttons on city detail pages

3. **Command line options:**
   ```bash
   # Enrich existing venues in all cities
   python manage.py enrich_venues --all

   # Enrich + discover new venues for a specific city
   python manage.py enrich_venues --city=norfolk --discover

   # Refresh stale venues (7+ days old)
   python manage.py refresh_venues --days=7

   # Dry run to see what would happen
   python manage.py enrich_venues --dry-run
   ```

### New Files
- `guide/services/` - API service layer
- `guide/management/commands/enrich_venues.py`
- `guide/management/commands/refresh_venues.py`
- `cms/views/settings.py`
- `templates/cms/settings.html`
- `templates/guide/includes/venue_list.html`
- `systemd/venue-refresh.service`
- `systemd/venue-refresh.timer`

### Modified Files
- `guide/models.py` - Added enrichment fields to Venue, new VenueAPIConfig model
- `cms/urls.py` - Added settings and venue refresh routes
- `cms/views/__init__.py` - Added settings imports
- `cms/views/dashboard.py` - Added enrichment stats
- `templates/cms/dashboard.html` - Added enrichment card
- `templates/cms/cities/_venue_table.html` - Added ratings and refresh buttons
- `templates/cms/components/sidebar.html` - Added settings link
- `templates/guide/city_detail.html` - Display ratings and price levels
- `static/css/style.css` - Added venue card styles
