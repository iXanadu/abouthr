# About Hampton Roads - Codebase State

**Last Updated:** 2026-01-21 (End of Day)

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

---

## Current State Summary

### Phase / Milestone
- **Current Phase:** Phase 6 Complete - Venue Enrichment System Operational
- **Progress:** 95%
- **Status:** Dev deployed, Google Places integration complete, rich mobile display

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

---

## App Structure

```
abouthr/
├── abouthr/           # Project settings
├── accounts/          # User auth, profiles, multi-tenancy
├── core/              # Base models, shared utilities
├── guide/             # Domain models + public views + URLs
│   ├── management/commands/seed_data.py  # Data seeding
│   ├── models.py      # City, Venue, MilitaryBase, etc.
│   ├── views.py       # All page views + sitemap + robots
│   └── urls.py        # URL routing
├── cms/               # Content Management System
│   ├── forms.py       # ModelForms with crispy_forms
│   ├── urls.py        # 33 URL patterns
│   └── views/         # Dashboard, CRUD for all models
│       ├── __init__.py
│       ├── mixins.py      # CMSAccessMixin
│       ├── dashboard.py   # Dashboard + Help views
│       ├── cities.py      # City CRUD
│       ├── venues.py      # Venue CRUD + HTMX toggle
│       ├── military.py    # Military CRUD
│       └── content.py     # Tunnels, Vacation, Vendors, Testimonials, Team
├── templates/
│   ├── base.html          # Main template with SEO meta tags
│   ├── guide/             # Public page templates (9 files)
│   ├── cms/               # CMS templates
│   │   ├── base.html      # CMS base with sidebar
│   │   ├── dashboard.html
│   │   ├── help.html      # Content guidelines
│   │   ├── components/    # sidebar, publish_toggle
│   │   ├── cities/        # list, detail, edit
│   │   ├── venues/        # form, confirm_delete
│   │   ├── military/      # list, form, confirm_delete
│   │   ├── tunnels/       # list, form, confirm_delete
│   │   ├── vacation/      # list, form, confirm_delete
│   │   ├── vendors/       # list, form, confirm_delete
│   │   ├── testimonials/  # list, form, confirm_delete
│   │   └── team/          # list, form, confirm_delete
│   └── registration/
│       └── login.html     # CMS login page
└── static/
    ├── css/style.css  # Custom styles with animations
    └── images/        # Hero and city images
```

---

## Key Models (guide/models.py)

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

**Note:** All guide models use `BaseModel` (timestamps only), NOT `AccountScopedModel` - this is single-tenant shared content.

---

## URLs

### Public Site (guide/urls.py)
| View | URL | Template |
|------|-----|----------|
| HomeView | `/` | home.html |
| CityDetailView | `/city/<slug>/` | city_detail.html |
| MilitaryView | `/military/` | military.html |
| TunnelsView | `/tunnels/` | tunnels.html |
| VacationView | `/vacation/` | vacation.html |
| UtilitiesView | `/utilities/` | utilities.html |
| TestimonialsView | `/testimonials/` | testimonials.html |
| AboutView | `/about/` | about.html |
| ContactView | `/contact/` | contact.html |
| sitemap_xml | `/sitemap.xml` | (dynamic XML) |
| robots_txt | `/robots.txt` | (dynamic text) |

### CMS (cms/urls.py) - 33 patterns
| Section | URLs |
|---------|------|
| Dashboard | `/cms/`, `/cms/help/` |
| Cities | `/cms/cities/`, `/cms/cities/<slug>/`, `/cms/cities/<slug>/edit/` |
| Venues | `/cms/cities/<slug>/venues/add/<type>/`, `/cms/venues/<pk>/edit/`, `/cms/venues/<pk>/delete/`, `/cms/venues/<pk>/toggle/` |
| Military | `/cms/military/`, `/cms/military/add/`, `/cms/military/<slug>/edit/`, `/cms/military/<slug>/delete/` |
| Tunnels | `/cms/tunnels/`, `/cms/tunnels/add/`, etc. |
| Vacation | `/cms/vacation/`, `/cms/vacation/add/`, etc. |
| Vendors | `/cms/vendors/`, `/cms/vendors/add/`, etc. |
| Testimonials | `/cms/testimonials/`, `/cms/testimonials/add/`, etc. |
| Team | `/cms/team/`, `/cms/team/add/`, etc. |

### Auth (django.contrib.auth.urls)
| URL | Purpose |
|-----|---------|
| `/accounts/login/` | CMS login |
| `/accounts/logout/` | Logout |

---

## Next Planned Work

### IMMEDIATE
- [ ] Set up systemd timer for weekly venue refresh (optional)
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
- [ ] AI-generated events/happenings content
- [ ] CMS drag-and-drop reordering
- [ ] Search functionality
- [ ] Google Maps integration with venue coordinates
- [ ] Contact form with email

---

## Environment Status
| Environment | Status | URL | Last Deploy |
|-------------|--------|-----|-------------|
| Development | **Running** | dev.abouthamptonroads.com | 2026-01-18 |
| Production | Not deployed | abouthamptonroads.com | - |

### Server Commands
```bash
# Restart development server (after Python changes)
sudo systemctl restart gunicorn_abouthamptonroads_dev

# Check status
systemctl status gunicorn_abouthamptonroads_dev

# View logs
journalctl -u gunicorn_abouthamptonroads_dev -n 50
```

---

## Architecture Notes

### Design Decisions
1. **Single Venue Model:** Using `venue_type` discriminator instead of 5 separate models
2. **Mobile-First:** Site designed for phone first, scales up to desktop
3. **PDF as Source:** All content seeded from the 40-page PDF
4. **Tabs/Accordions:** Desktop uses tabs for venue types, mobile uses accordions
5. **Premium Fonts:** Montserrat (headers) + Inter (body) for modern look
6. **CMS-Managed Images:** City images stored via ImageField, editable in CMS
7. **Dynamic Sitemap:** Generated via view to auto-include new content
8. **HTMX for CMS:** Publish toggles use HTMX for no-reload updates

### CMS Access Control
Users can access CMS if any of these are true:
- `user.is_superuser`
- `user.profile.is_admin`
- `user.profile.system_role in ['account_owner', 'admin']`

---

## Known Issues / Technical Debt

### Issues
- [ ] City images not uploaded yet (showing "No image" in CMS)
- [ ] Image sizes large (up to 1.1MB) - optimize during deployment

### Technical Debt
- [ ] OpenGraph image URLs may need absolute paths for some platforms
- [ ] No unit/integration tests implemented

---

## Testing Status
- All public pages return 200 status
- All CMS pages return 200 status (when authenticated)
- sitemap.xml generates valid XML
- robots.txt generates valid format
- OpenGraph tags present in HTML
- Lazy loading attributes added
- CMS CRUD operations functional
- Unit tests: Not implemented
- Integration tests: Not implemented

---

## Quick Reference

### Important Files
- `abouthr/settings.py` - Django configuration
- `guide/models.py` - All domain models
- `guide/views.py` - Public page views
- `cms/views/` - CMS views
- `cms/forms.py` - All CMS forms
- `cms/urls.py` - CMS URL routing
- `templates/base.html` - Main public template
- `templates/cms/base.html` - CMS base template
- `templates/cms/help.html` - CMS content guidelines
- `static/css/style.css` - Custom styles
- `claude/SERVER_COMMANDS.md` - Gunicorn restart commands

### Common Commands
```bash
python manage.py runserver          # Local dev server
python manage.py seed_data          # Seed database from PDF content
python manage.py createsuperuser    # Create admin user
python manage.py collectstatic      # Collect static files
python manage.py migrate            # Run migrations
```

### CMS URLs
- Dashboard: `/cms/`
- Help: `/cms/help/`
- Login: `/accounts/login/`
