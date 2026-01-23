# Development Handoff Notes

This file contains server-side actions needed after `git pull`.

**For full production deployment instructions, see:** `claude/PRODUCTION_DEPLOYMENT.md`

---

## 2026-01-22: Drive Calculator Landing Page

### Summary
Added a standalone landing page for the Drive Time Calculator at `/drive-calculator/`. This page is designed for ads and drip campaigns, featuring a hero section with the tunnels/bridges map and the full calculator widget.

### Required Actions After `git pull`

1. **Collect static files:**
   ```bash
   python manage.py collectstatic --no-input
   ```

2. **Restart the service:**
   ```bash
   sudo systemctl restart gunicorn_abouthamptonroads_dev
   ```

### New/Modified Files
- `templates/guide/drive_calculator.html` - New landing page template
- `guide/views.py` - Added DriveCalculatorView, added /drive-calculator/ to sitemap
- `guide/urls.py` - Added /drive-calculator/ route
- `static/css/style.css` - Added hero section styles

### Landing Page URL
- Dev: https://dev.abouthamptonroads.com/drive-calculator/
- Prod: https://abouthamptonroads.com/drive-calculator/

### Marketing Features
- Hero section with tunnels/bridges map image
- Strong CTAs for contacting Trustworthy Agents
- Lists all 39 preset destinations by category
- SEO optimized with meta tags
- OpenGraph image set to tunnels map for social sharing

---

## 2026-01-22: Drive Time Calculator

### Summary
Added an interactive Drive Time Calculator to city pages that shows route comparisons with traffic estimates. Users can calculate drive times from any address to military bases, beaches, airports, hospitals, and universities.

### Required Actions After `git pull`

1. **Run migrations:**
   ```bash
   python manage.py migrate guide
   ```

2. **Seed drive destinations:**
   ```bash
   python manage.py seed_destinations
   ```

3. **Add Google Maps API key to .keys file (if not already configured):**
   ```bash
   # The calculator uses GOOGLE_MAPS_API_KEY
   # If you already have GOOGLE_PLACES_API_KEY, you can use the same key
   echo "GOOGLE_MAPS_API_KEY=your-api-key-here" >> .keys
   ```

   **Google Cloud Console Setup:**
   - Enable these APIs:
     - Maps JavaScript API
     - Places API
     - Directions API
   - Restrict the key to your domains:
     - `dev.abouthamptonroads.com`
     - `abouthamptonroads.com`

4. **Collect static files:**
   ```bash
   python manage.py collectstatic --no-input
   ```

5. **Restart the service:**
   ```bash
   sudo systemctl restart gunicorn
   ```

### Features
- Address autocomplete for starting location
- Preset destinations grouped by category (16 military bases, 3 airports, 8 hospitals, 6 universities, 6 beaches)
- Custom destination address entry
- Time toggle: Now / Morning Rush (7:30 AM) / Evening Rush (5:00 PM)
- Route comparison showing 2-3 routes with names, times, distances
- Share functionality with URL-based bookmarkable links
- "Open in Google Maps" link for full directions

### New Files
- `guide/migrations/0006_drivedestination.py`
- `guide/management/commands/seed_destinations.py`
- `templates/guide/includes/drive_calculator.html`
- `cms/views/drive_destinations.py`
- `templates/cms/drive_destinations/list.html`
- `templates/cms/drive_destinations/form.html`
- `templates/cms/drive_destinations/confirm_delete.html`

### Modified Files
- `guide/models.py` - Added DriveDestination model
- `guide/views.py` - Updated CityDetailView context
- `abouthr/settings.py` - Added GOOGLE_MAPS_API_KEY
- `static/css/style.css` - Added drive calculator styles
- `templates/guide/city_detail.html` - Included calculator widget + Google Maps API
- `cms/urls.py` - Added drive destination routes
- `cms/views/__init__.py` - Import drive destination views
- `cms/forms.py` - Added DriveDestinationForm
- `templates/cms/components/sidebar.html` - Added Drive Destinations link

### CMS Management
- Go to CMS > Drive Destinations to add/edit/delete preset destinations
- 39 destinations are seeded by default

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
