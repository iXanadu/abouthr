# About Hampton Roads - Project Plan

**Created:** 2026-01-18
**Status:** Ready for public website implementation

---

## Project Summary

Build a mobile-first public website for the Hampton Roads VA Relocation Guide. The content comes directly from a 40-page PDF brochure created by Trustworthy Agents Group (Robert & Nate Pickles).

**Domain:** abouthamptonroads.com
**Target Audience:** Military families and others relocating to Hampton Roads, VA

---

## What's Done

### 1. Django Project Structure
- [x] Project initialized with Django 5.2
- [x] PostgreSQL database configured (abouthr_dev on postgres.o6.org)
- [x] Core app with BaseModel, AccountScopedModel
- [x] Accounts app with User/Account/UserProfile models
- [x] Settings configured for local/dev/prod environments

### 2. Guide App - Domain Models (guide/models.py)
All models created and migrated:

| Model | Purpose | Key Fields |
|-------|---------|------------|
| `Region` | Peninsula vs Southside | name, slug, order |
| `City` | 9 HR cities | name, slug, region FK, description, image, school_url, has_beaches |
| `Venue` | Restaurants, cafes, attractions, events, beaches | city FK, venue_type, cuisine_type, name, description, address |
| `MilitaryBase` | Military installations | name, branch, city FK, description |
| `Tunnel` | 6 tunnel/bridge systems | name, connects_from, connects_to, description |
| `VacationDestination` | Nearby getaways | name, distance_description, highlights |
| `VendorUtility` | Per-city utility contacts | city FK, category, name, phone, website |
| `Testimonial` | Client quotes | client_name, quote, is_featured |
| `TeamMember` | Company team | name, title, bio, photo |

### 3. CMS App (Partially Built - PAUSED)
Started but paused - focus shifted to public website first:
- views/mixins.py - CMSAccessMixin
- views/dashboard.py - DashboardView
- views/cities.py - CityListView, CityDetailView
- views/venues.py - Venue CRUD views
- views/military.py - Military views

### 4. PDF Analysis Complete
- Split 40-page PDF into individual pages (claude/specs/pages/)
- Extracted 126 images (claude/specs/images/)
- Full content structure documented

### 5. Git Repository
- Initialized and committed
- Pushed to git@github.com:iXanadu/abouthr.git

---

## What's NOT Done

### Phase 1: Public Website Templates (HIGH PRIORITY)

1. **Base Template Architecture**
   - [ ] Create base.html with mobile-first responsive layout
   - [ ] Navigation (hamburger on mobile, full nav on desktop)
   - [ ] Footer with contact info
   - [ ] Include Bootstrap 5 + custom CSS
   - [ ] Choose and implement fonts (research needed)

2. **Homepage**
   - [ ] Hero section with Hampton Roads overview
   - [ ] City cards grid (links to city pages)
   - [ ] Quick links to Military, Tunnels, etc.
   - [ ] Call-to-action to explorevirginiahomes.com

3. **City Pages (9 cities)**
   - [ ] City detail template with sections:
     - Hero/header with city image
     - Description
     - Restaurants tab/section
     - Cafes & Breweries tab/section
     - Attractions tab/section
     - Events & Festivals tab/section
     - Beaches (where applicable)
     - School info link
   - [ ] Mobile: accordion or tabs
   - [ ] Desktop: tabs or side-by-side

4. **Special Section Pages**
   - [ ] Military Relocation page
   - [ ] Military Bases page (list with map)
   - [ ] Tunnel Systems page
   - [ ] Vacation Destinations page
   - [ ] Vendors & Utilities page (per-city tabs)
   - [ ] Testimonials page
   - [ ] About/Team page
   - [ ] Contact page

5. **URL Routing**
   - [ ] Configure guide app URLs
   - [ ] Create public views
   - [ ] Wire up to abouthr/urls.py

### Phase 2: Data Seeding

1. **Create Seed Script**
   - [ ] guide/management/commands/seed_data.py
   - [ ] Seed Regions (Peninsula, Southside)
   - [ ] Seed all 9 Cities with descriptions
   - [ ] Seed all Venues (restaurants, cafes, attractions, events, beaches)
   - [ ] Seed Military Bases
   - [ ] Seed Tunnels
   - [ ] Seed Vacation Destinations
   - [ ] Seed Vendor Utilities
   - [ ] Seed Testimonials
   - [ ] Seed Team Members

2. **Image Organization**
   - [ ] Organize extracted images by content type
   - [ ] Create media directory structure
   - [ ] Link images to seeded data

### Phase 3: Polish & Deploy

1. **SEO & Meta**
   - [ ] Meta tags for all pages
   - [ ] OpenGraph tags
   - [ ] Sitemap
   - [ ] robots.txt

2. **Performance**
   - [ ] Image optimization
   - [ ] Lazy loading
   - [ ] CSS/JS minification

3. **Deployment**
   - [ ] Deploy to development server
   - [ ] Test on real mobile devices
   - [ ] Deploy to production

### Phase 4: Future Features (BACKLOG)

1. **AI-Generated Content**
   - [ ] Current events per city
   - [ ] Upcoming events/happenings
   - [ ] Dynamic content layer

2. **CMS Interface**
   - [ ] Complete paused CMS work
   - [ ] Add HTMX inline editing
   - [ ] Drag-and-drop reordering

3. **Additional Features**
   - [ ] Search functionality
   - [ ] Google Maps integration
   - [ ] Contact form
   - [ ] Newsletter signup

---

## The 9 Cities

**Southside (South of James River):**
1. Virginia Beach - has beaches, largest city
2. Chesapeake - office location
3. Norfolk - Naval Station
4. Portsmouth - Naval Shipyard
5. Suffolk - rural/suburban
6. Smithfield - small town, ham!

**Peninsula (North of James River):**
7. Hampton - Langley AFB nearby
8. Newport News - shipbuilding
9. Williamsburg/Yorktown - historic, colonial

---

## Design Requirements

### Mobile-First Priority
- **Phone:** Must be PERFECT
- **Tablet:** Must be GREAT
- **Desktop:** Must be GOOD

This is inverse of typical priority because relocation guides are often viewed on phones by people traveling or in temporary housing.

### Typography (Research Needed)
- Script font for headers (like PDF's "Relocation Guide" script)
- Clean sans-serif for body text
- Good mobile readability
- Google Fonts preferred

### Color Scheme (From PDF)
- Black headers
- White/light backgrounds
- Accent colors TBD
- High contrast for accessibility

---

## Content Structure Per City Page

From PDF analysis, each city has:

```
City Name (script header)
├── Hero Image
├── Description (1-2 paragraphs)
├── Popular Restaurants (15-20 items)
├── Cafes & Breweries (10-15 items)
├── City Sites & Attractions (20+ items)
├── Events & Festivals (8-12 items)
├── Beaches (if applicable - Virginia Beach mainly)
├── QR Code / Link to city info
└── QR Code / Link to school info
```

---

## Reference Projects

- `../tagApp` - Good Django infrastructure patterns
- `../trustworthyagents.com/prod` - Website patterns (but can do better)

---

## Key Files

| File | Purpose |
|------|---------|
| `guide/models.py` | All domain models |
| `guide/admin.py` | Django admin registration |
| `claude/specs/abouthr.pdf` | Source PDF (40 pages) |
| `claude/specs/pages/` | Split PDF pages |
| `claude/specs/images/` | Extracted images (126 files) |
| `claude/CODEBASE_STATE.md` | Technical state |
| `claude/CONTEXT_MEMORY.md` | Working context |

---

## Commands

```bash
# Run development server
python manage.py runserver

# Make migrations
python manage.py makemigrations guide

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Future: Seed data
python manage.py seed_data
```

---

## Contact Info (For Site Footer)

- **Direct:** 757-500-2404
- **Office:** 757-361-0106
- **Email:** info@trustworthyagents.com
- **Address:** 1100 Volvo Parkway, Suite #200, Chesapeake, VA 23320
- **Website:** www.trustworthyagents.com
- **Home Search:** explorevirginiahomes.com
