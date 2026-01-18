# About Hampton Roads - Codebase State

**Last Updated:** 2026-01-18

## Project Overview
Web-based Hampton Roads, Virginia relocation guide. Digital version of the Trustworthy Agents Group's relocation guide PDF, providing comprehensive information about the Hampton Roads/Tidewater region for people relocating to the area.

---

## Technical Stack
- **Framework:** Django 5.2
- **Database:** PostgreSQL (abouthr_dev / abouthr_prod on postgres.o6.org)
- **Python:** 3.12+
- **Frontend:** Bootstrap 5, Crispy Forms (mobile-first)
- **API:** Django REST Framework

---

## Current State Summary

### Phase / Milestone
- **Current Phase:** Domain Models Complete, Ready for Public Site Build
- **Progress:** 25%
- **Status:** Active

### Recent Major Work Completed
1. Project initialization with Django - 2026-01-17
2. Core and accounts apps created - 2026-01-17
3. Database setup (user, dev/prod databases) - 2026-01-17
4. **Guide app with domain models** - 2026-01-18
5. **PDF analysis complete (40 pages split and reviewed)** - 2026-01-18
6. **CMS app structure started (paused)** - 2026-01-18

---

## App Structure

```
abouthr/
├── abouthr/      # Project settings
├── accounts/     # User auth, profiles, multi-tenancy
├── core/         # Base models, shared utilities
├── guide/        # Domain models (City, Venue, etc.) - NEW
├── cms/          # Content management (paused) - NEW
└── templates/    # Global templates
```

---

## Key Models (guide/models.py)

| Model | Purpose |
|-------|---------|
| `Region` | Peninsula vs Southside geographic division |
| `City` | 9 Hampton Roads cities with descriptions, images |
| `Venue` | Unified: restaurants, cafes, attractions, events, beaches |
| `MilitaryBase` | Military installations by branch |
| `Tunnel` | 6 tunnel/bridge systems |
| `VacationDestination` | Nearby getaway destinations |
| `VendorUtility` | Per-city utility contacts |
| `Testimonial` | Client quotes |
| `TeamMember` | Company team members |

**Note:** All guide models use `BaseModel` (timestamps only), NOT `AccountScopedModel` - this is single-tenant shared content.

---

## Next Planned Work

### IMMEDIATE (Before Coding)
1. Set up .gitignore
2. Git init, commit, push
3. Extract images from PDF
4. Research mobile-first fonts/responsive patterns

### HIGH PRIORITY (Public Website)
1. Design mobile-first template architecture
2. Create base template with navigation
3. Build city page templates (9 cities, 2-page pattern each)
4. Create data seeding script
5. Build military, tunnels, testimonials pages

### MEDIUM PRIORITY
6. Add search functionality
7. Implement contact forms
8. Google Maps integration

### FUTURE / BACKLOG
- AI-generated events/happenings content
- CMS interface for content management
- User accounts for personalized features

---

## Architecture Notes

### Design Decisions
1. **Single Venue Model:** Using `venue_type` discriminator instead of 5 separate models
2. **Mobile-First:** Site must be perfect on phone, great on tablet, good on desktop
3. **PDF as Source:** All content seeded from the 40-page PDF

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

---

## Testing Status
- Unit tests: Not implemented
- Integration tests: Not implemented
- Last test run: N/A

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
- `guide/admin.py` - Admin registration
- `claude/specs/abouthr.pdf` - Source content (40 pages)
- `claude/specs/pages/` - Split PDF pages

### Common Commands
```bash
python manage.py runserver
python manage.py test
python manage.py migrate
python manage.py makemigrations guide
```

### Reference Projects
- `../tagApp` - Infrastructure patterns
- `../trustworthyagents.com/prod` - Website patterns
