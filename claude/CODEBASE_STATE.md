# About Hampton Roads - Codebase State

**Last Updated:** 2026-01-22 (evening)

## Project Overview
Web-based Hampton Roads, Virginia relocation guide. Digital version of the Trustworthy Agents Group's relocation guide PDF, providing comprehensive information about the Hampton Roads/Tidewater region for people relocating to the area.

---

## Technical Stack
- **Framework:** Django 5.2
- **Database:** PostgreSQL (abouthr_dev / abouthr_prod on postgres.o6.org)
- **Python:** 3.12+
- **Frontend:** Bootstrap 5, Google Fonts (Montserrat + Inter), HTMX
- **CSS:** Custom mobile-first stylesheet with CSS variables
- **Forms:** crispy_forms + crispy_bootstrap5
- **SEO:** OpenGraph, Twitter Cards, sitemap.xml, robots.txt
- **AI:** Anthropic Claude, xAI Grok, OpenAI (configurable per operation)
- **Weather:** Open-Meteo (free, no API key)

---

## Current State Summary

### Phase / Milestone
- **Current Phase:** Phase 7 - AI Services & Dynamic Content
- **Progress:** 98%
- **Status:** Dev deployed, AI infrastructure complete, Pulse system live

### Recent Major Work Completed
1. Project initialization with Django - 2026-01-17
2. Core and accounts apps created - 2026-01-17
3. Database setup (user, dev/prod databases) - 2026-01-17
4. Guide app with domain models - 2026-01-18
5. PDF analysis complete (40 pages split and reviewed) - 2026-01-18
6. **Phase 1: All content seeded (501 venues, 16 bases, etc.)** - 2026-01-18
7. **Phase 1: Base template with Bootstrap 5 + modern fonts** - 2026-01-18
8. **Phase 1: All 9 page templates + views + routing** - 2026-01-18
9. **Phase 2: City images added to all cards and detail pages** - 2026-01-18
10. **Phase 2: CSS polish with animations and transitions** - 2026-01-18
11. **Phase 3: OpenGraph and Twitter Card meta tags** - 2026-01-18
12. **Phase 3: Dynamic sitemap.xml and robots.txt** - 2026-01-18
13. **Phase 3: Lazy loading for all images** - 2026-01-18
14. **Deployment prep: requirements.txt created** - 2026-01-18
15. **Utility scripts added (check_env, push_keys)** - 2026-01-18
16. **Phase 4: CMS infrastructure (urls, forms, views)** - 2026-01-18
17. **Phase 4: CMS templates for all 8 content types** - 2026-01-18
18. **Phase 4: CMS help page with content guidelines** - 2026-01-18
19. **Phase 4: Superuser created, CMS operational** - 2026-01-18
20. **Phase 5: Venue Enrichment System - Google Places API integration** - 2026-01-21
21. **Phase 5: CMS Settings page with API controls** - 2026-01-21
22. **Phase 6: Rich venue display with photos, ratings, hours** - 2026-01-21
23. **Phase 6: Mobile-optimized venue cards (90% of traffic)** - 2026-01-21
24. **Phase 7: AI Services infrastructure (models, pricing, tracking)** - 2026-01-21
25. **Phase 7: Weather integration (Open-Meteo) on city pages** - 2026-01-21
26. **Phase 7: Hampton Roads Pulse (X trends + headlines)** - 2026-01-21
27. **Phase 7: Pulse Dashboard with timer controls** - 2026-01-21
28. **Phase 7: Systemd timers for automated refresh** - 2026-01-21
29. **Military bases map added to /military/ page** - 2026-01-22
30. **Tunnels/bridges map added to /tunnels/ page** - 2026-01-22
31. **Pulse widget: collapsible UI with partial-open default** - 2026-01-22
32. **Pulse staleness fix: content always shows, never empty** - 2026-01-22
33. **Drive Time Calculator on city pages** - 2026-01-22
34. **DriveDestination model with 39 preset locations** - 2026-01-22
35. **Google Maps/Places/Directions API integration** - 2026-01-22
36. **CMS management for Drive Destinations** - 2026-01-22
37. **Utilities section added to city Quick Info** - 2026-01-22
38. **Drive Calculator landing page for ads/campaigns** - 2026-01-22
39. **Optimized hero image (9MB→441KB)** - 2026-01-22

---

## App Structure

```
abouthr/
├── abouthr/           # Project settings
├── accounts/          # User auth, profiles, multi-tenancy
├── core/              # Base models, shared utilities
├── guide/             # Domain models + public views + URLs
│   ├── management/commands/
│   │   ├── seed_data.py       # Data seeding
│   │   ├── enrich_venues.py   # Google Places enrichment
│   │   ├── refresh_venues.py  # Venue data refresh
│   │   └── refresh_pulse.py   # Pulse content refresh
│   ├── services/
│   │   ├── google_places_service.py
│   │   ├── venue_enrichment_service.py
│   │   ├── weather_service.py      # Open-Meteo integration
│   │   ├── trends_service.py       # Grok X search
│   │   ├── headlines_service.py    # RSS + Claude
│   │   └── pulse_service.py        # Orchestration
│   ├── models.py      # City, Venue, MilitaryBase, PulseContent, etc.
│   ├── views.py       # All page views + sitemap + robots
│   └── urls.py        # URL routing
├── cms/               # Content Management System
│   ├── forms.py       # ModelForms with crispy_forms
│   ├── urls.py        # 40+ URL patterns
│   └── views/         # Dashboard, CRUD for all models
│       ├── dashboard.py      # Dashboard + Help views
│       ├── cities.py         # City CRUD
│       ├── venues.py         # Venue CRUD + HTMX toggle
│       ├── settings.py       # API configuration
│       ├── ai_settings.py    # AI cost report + model manager
│       └── pulse_dashboard.py # Pulse management
├── ai_services/       # AI model management
│   ├── models.py      # AIProvider, AIModel, AIOperationConfig, AIUsageLog
│   ├── pricing.py     # Cost calculation
│   ├── model_selector.py # Model configuration
│   ├── config/providers.yaml
│   └── management/commands/seed_ai_models.py
├── templates/
│   ├── base.html
│   ├── guide/             # Public page templates
│   │   └── includes/
│   │       └── pulse_widget.html
│   ├── cms/
│   │   ├── ai/            # AI management templates
│   │   └── pulse/         # Pulse dashboard
│   └── registration/
└── static/
    ├── css/style.css
    └── images/
```

---

## Key Models

| Model | Purpose | Count |
|-------|---------|-------|
| `Region` | Peninsula vs Southside geographic division | 2 |
| `City` | 9 Hampton Roads cities with descriptions, images | 9 |
| `Venue` | Unified: restaurants, cafes, attractions, events, beaches | 501 |
| `MilitaryBase` | Military installations by branch | 16 |
| `Tunnel` | 6 tunnel/bridge systems | 6 |
| `VacationDestination` | Nearby getaway destinations | 13 |
| `VendorUtility` | Per-city utility contacts | 47 |
| `Testimonial` | Client quotes | 7 |
| `TeamMember` | Company team members | 2 |
| `VenueAPIConfig` | Google/Yelp API configuration | 1 |
| `DriveDestination` | Drive calculator preset locations | 39 |
| `PulseContent` | Cached trends/headlines JSON | varies |
| `AIProvider` | AI service providers | 5 |
| `AIModel` | Available AI models | 17 |
| `AIOperationConfig` | Operation-to-model mapping | 8 |
| `AIUsageLog` | AI usage and cost tracking | varies |

---

## URLs

### Public Site (guide/urls.py)
| View | URL | Template |
|------|-----|----------|
| HomeView | `/` | home.html (includes pulse widget) |
| CityDetailView | `/city/<slug>/` | city_detail.html (includes weather) |
| MilitaryView | `/military/` | military.html |
| TunnelsView | `/tunnels/` | tunnels.html |
| VacationView | `/vacation/` | vacation.html |
| UtilitiesView | `/utilities/` | utilities.html |
| TestimonialsView | `/testimonials/` | testimonials.html |
| AboutView | `/about/` | about.html |
| ContactView | `/contact/` | contact.html |
| DriveCalculatorView | `/drive-calculator/` | drive_calculator.html |
| venue_photo | `/venue/<id>/photo/` | (proxy to Google) |

### CMS (cms/urls.py)
| Section | URLs |
|---------|------|
| Dashboard | `/cms/`, `/cms/help/` |
| Pulse | `/cms/pulse/`, `/cms/pulse/refresh/`, `/cms/pulse/timer/<name>/<action>/` |
| Settings | `/cms/settings/` |
| AI | `/cms/ai/costs/`, `/cms/ai/models/`, `/cms/ai/operation/<op>/update/` |
| Cities | `/cms/cities/`, etc. |
| Venues | `/cms/venues/`, etc. |
| Military | `/cms/military/`, etc. |
| Content | tunnels, vacation, vendors, testimonials, team |

---

## Next Planned Work

### IMMEDIATE
- [x] Add utility companies expandable section to city pages
- [x] Drive Time Calculator on city pages
- [ ] Test on real mobile devices
- [ ] Optimize images (large files, up to 1.1MB)

### PRODUCTION DEPLOYMENT
- [ ] Configure DNS for abouthamptonroads.com
- [ ] Deploy to production environment
- [ ] SSL certificate setup
- [ ] Performance optimization
- [ ] Backup strategy

### FUTURE / BACKLOG
- [ ] Yelp integration (stub ready in yelp_service.py)
- [ ] City-specific pulse content
- [ ] Search functionality
- [ ] Google Maps integration with venue coordinates
- [ ] Contact form with email

---

## Environment Status
| Environment | Status | URL | Last Deploy |
|-------------|--------|-----|-------------|
| Development | **Running** | dev.abouthamptonroads.com | 2026-01-22 |
| Production | Not deployed | abouthamptonroads.com | - |

### Server Commands
```bash
# Restart development server
sudo systemctl restart gunicorn_abouthamptonroads_dev

# Check status
systemctl status gunicorn_abouthamptonroads_dev

# View logs
journalctl -u gunicorn_abouthamptonroads_dev -n 50

# Pulse management
python manage.py refresh_pulse --stats
python manage.py refresh_pulse --force

# Timer status
systemctl list-timers pulse-refresh.timer
systemctl list-timers venue-refresh.timer
```

---

## Testing Status
- All public pages return 200 status
- All CMS pages return 200 status (when authenticated)
- sitemap.xml generates valid XML
- robots.txt generates valid format
- Weather integration tested and working
- Pulse refresh tested and working
- AI Model Manager edit functionality fixed
- Systemd timers installed and running
- Unit tests: Not implemented
- Integration tests: Not implemented

---

## Quick Reference

### Important Files
- `abouthr/settings.py` - Django configuration
- `guide/models.py` - All domain models
- `guide/services/` - External service integrations
- `cms/views/pulse_dashboard.py` - Pulse management
- `ai_services/models.py` - AI infrastructure
- `static/css/style.css` - Custom styles

### Common Commands
```bash
python manage.py runserver              # Local dev server
python manage.py seed_data              # Seed database from PDF
python manage.py seed_ai_models         # Seed AI models
python manage.py refresh_pulse          # Refresh pulse content
python manage.py refresh_pulse --force  # Force refresh
python manage.py enrich_venues          # Enrich venues from Google
python manage.py collectstatic          # Collect static files
```

### CMS URLs
- Dashboard: `/cms/`
- Pulse Dashboard: `/cms/pulse/`
- AI Models: `/cms/ai/models/`
- AI Costs: `/cms/ai/costs/`
- Help: `/cms/help/`
