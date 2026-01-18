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
- **SEO:** OpenGraph, Twitter Cards, sitemap.xml, robots.txt

---

## Current State Summary

### Phase / Milestone
- **Current Phase:** Phase 3 Complete - Ready for Deployment
- **Progress:** 75%
- **Status:** Ready for Production Deploy

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
│   ├── views.py       # All page views + sitemap + robots
│   └── urls.py        # URL routing
├── cms/               # Content management (paused)
├── templates/
│   ├── base.html      # Main template with SEO meta tags
│   └── guide/         # All page templates
└── static/
    ├── css/style.css  # Custom styles with animations
    └── images/        # Hero and city images
        ├── hero/pier-sunset.jpg
        └── cities/*.jpg (9 city images)
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
| sitemap_xml | `/sitemap.xml` | (dynamic XML) |
| robots_txt | `/robots.txt` | (dynamic text) |

---

## Next Planned Work

### DEPLOYMENT (User Action Required)
1. Deploy to development server
2. Test on real mobile devices
3. Configure DNS for abouthamptonroads.com
4. Deploy to production
5. SSL certificate setup
6. Image optimization on server

### FUTURE / BACKLOG (Phase 4)
- AI-generated events/happenings content
- CMS interface for content management
- Search functionality
- Google Maps integration
- Contact form with email

---

## Architecture Notes

### Design Decisions
1. **Single Venue Model:** Using `venue_type` discriminator instead of 5 separate models
2. **Mobile-First:** Site designed for phone first, scales up to desktop
3. **PDF as Source:** All content seeded from the 40-page PDF
4. **Tabs/Accordions:** Desktop uses tabs for venue types, mobile uses accordions
5. **Premium Fonts:** Montserrat (headers) + Inter (body) for modern look
6. **Static Images:** City images stored as static files, not database ImageFields
7. **Dynamic Sitemap:** Generated via view to auto-include new content

### Content Structure
- **9 Cities:** Virginia Beach, Chesapeake, Norfolk, Portsmouth, Suffolk, Smithfield, Hampton, Newport News, Williamsburg/Yorktown
- **Per City:** Description, restaurants, cafes/breweries, attractions, events, beaches (where applicable)
- **Special Sections:** Military, tunnels, vacation destinations, vendors, testimonials

---

## Known Issues / Technical Debt

### Issues
- [ ] Image sizes large (up to 1.1MB) - optimize during deployment

### Technical Debt
- [ ] CMS app partially built but paused - may need cleanup
- [ ] OpenGraph image URLs are relative - may need absolute for some platforms

---

## Testing Status
- All 17 pages return 200 status
- All 10 images loading correctly
- sitemap.xml generates valid XML
- robots.txt generates valid format
- OpenGraph tags present in HTML
- Lazy loading attributes added
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
- `guide/views.py` - All page views + SEO views
- `guide/urls.py` - URL routing
- `templates/base.html` - Main template with SEO tags
- `static/css/style.css` - Custom styles with animations
- `static/images/` - Hero and city images
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

### SEO URLs
- `/sitemap.xml` - Dynamic XML sitemap (17 URLs)
- `/robots.txt` - Search engine instructions

### Reference Projects
- `../tagApp` - Infrastructure patterns
- `../trustworthyagents.com/prod` - Website patterns
