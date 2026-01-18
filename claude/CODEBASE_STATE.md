# About Hampton Roads - Codebase State

**Last Updated:** 2026-01-18

## Project Overview
Web-based Hampton Roads, Virginia relocation guide. Digital version of the Trustworthy Agents Group's relocation guide PDF, providing comprehensive information about the Hampton Roads/Tidewater region for people relocating to the area.

---

## Technical Stack
- **Framework:** Django 5.2
- **Database:** PostgreSQL (abouthr_dev / abouthr_prod on postgres.o6.org)
- **Python:** 3.12+
- **Frontend:** Bootstrap 5, Google Fonts (Montserrat + Inter)
- **CSS:** Custom mobile-first stylesheet with CSS variables
- **API:** Django REST Framework

---

## Current State Summary

### Phase / Milestone
- **Current Phase:** Phase 1 Complete - Public Website MVP
- **Progress:** 50%
- **Status:** Active

### Recent Major Work Completed
1. Project initialization with Django - 2026-01-17
2. Core and accounts apps created - 2026-01-17
3. Database setup (user, dev/prod databases) - 2026-01-17
4. Guide app with domain models - 2026-01-18
5. PDF analysis complete (40 pages split and reviewed) - 2026-01-18
6. **Phase 1: All content seeded (501 venues, 16 bases, etc.)** - 2026-01-18
7. **Phase 1: Base template with Bootstrap 5 + modern fonts** - 2026-01-18
8. **Phase 1: All 9 page templates + views + routing** - 2026-01-18

---

## App Structure

```
abouthr/
├── abouthr/           # Project settings
├── accounts/          # User auth, profiles, multi-tenancy
├── core/              # Base models, shared utilities
├── guide/             # Domain models + views + URLs
│   ├── management/commands/seed_data.py  # Data seeding
│   ├── models.py      # City, Venue, MilitaryBase, etc.
│   ├── views.py       # All page views
│   └── urls.py        # URL routing
├── cms/               # Content management (paused)
├── templates/
│   ├── base.html      # Main template
│   └── guide/         # All page templates
└── static/
    └── css/style.css  # Custom styles
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

## Page Views (guide/views.py)

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

---

## Next Planned Work

### HIGH PRIORITY (Phase 2)
1. Add city images to city cards and detail pages
2. Add hero background images
3. Review mobile responsiveness
4. Polish UI details

### MEDIUM PRIORITY
5. Add search functionality
6. Google Maps integration for contact page
7. SEO enhancements

### FUTURE / BACKLOG
- AI-generated events/happenings content
- CMS interface for content management
- User accounts for personalized features

---

## Architecture Notes

### Design Decisions
1. **Single Venue Model:** Using `venue_type` discriminator instead of 5 separate models
2. **Mobile-First:** Site designed for phone first, scales up to desktop
3. **PDF as Source:** All content seeded from the 40-page PDF
4. **Tabs/Accordions:** Desktop uses tabs for venue types, mobile uses accordions
5. **Premium Fonts:** Montserrat (headers) + Inter (body) for modern look

### Content Structure
- **9 Cities:** Virginia Beach, Chesapeake, Norfolk, Portsmouth, Suffolk, Smithfield, Hampton, Newport News, Williamsburg/Yorktown
- **Per City:** Description, restaurants, cafes/breweries, attractions, events, beaches (where applicable)
- **Special Sections:** Military, tunnels, vacation destinations, vendors, testimonials

---

## Known Issues / Technical Debt

### Issues
- [ ] None currently

### Technical Debt
- [ ] CMS app partially built but paused - may need cleanup
- [ ] Images need extraction from PDF (placeholders until originals available)
- [ ] Hero section needs real background image

---

## Testing Status
- All pages return 200 status
- Static files loading correctly
- Unit tests: Not implemented
- Integration tests: Not implemented

---

## Environment Status
| Environment | Status | Last Deploy |
|-------------|--------|-------------|
| Local | Working | 2026-01-18 |
| Development | Not deployed | - |
| Production | Not deployed | - |

---

## Quick Reference

### Important Files
- `abouthr/settings.py` - Django configuration
- `guide/models.py` - All domain models
- `guide/views.py` - All page views
- `guide/urls.py` - URL routing
- `templates/base.html` - Main template
- `static/css/style.css` - Custom styles
- `guide/management/commands/seed_data.py` - Data seeding
- `claude/specs/abouthr.pdf` - Source content (40 pages)

### Common Commands
```bash
python manage.py runserver
python manage.py seed_data  # Seed database from PDF content
python manage.py test
python manage.py migrate
python manage.py makemigrations guide
```

### Reference Projects
- `../tagApp` - Infrastructure patterns
- `../trustworthyagents.com/prod` - Website patterns
