# About Hampton Roads - Context Memory

**Last Updated:** 2026-01-18

## Current Status
Domain models complete. PDF fully analyzed (40 pages). Ready to build mobile-first public website. CMS development paused - focus on public site first.

---

## Working Context

### Active Focus Area
Building mobile-first public website to display Hampton Roads relocation guide content.

### Recent Decisions
- **Single Venue Model:** Instead of 5 separate models, using one with `venue_type` discriminator
- **Mobile-First Priority:** Perfect on phone > great on tablet > good on desktop
- **PDF is THE Content:** Not reference material - the exact content to display
- **CMS Deprioritized:** No content staff, focus on public site first
- **BaseModel (not AccountScopedModel):** Guide content is single-tenant shared

### Patterns Being Used
- **BaseModel:** Abstract model with created_at/updated_at timestamps
- **Venue with venue_type:** Unified model for restaurants, cafes, attractions, events, beaches
- **Region/City hierarchy:** Peninsula vs Southside geographic organization

---

## Session Priorities

### Completed This Session
1. [COMPLETED] Guide app with all domain models
2. [COMPLETED] PDF analysis (40 pages split and reviewed)
3. [COMPLETED] CMS app structure (paused)
4. [COMPLETED] Migrations created and applied

### Before Next Coding Session
1. [ ] Set up .gitignore (copy from tagApp)
2. [ ] Git init, commit, push
3. [ ] Extract images from PDF
4. [ ] Research mobile-first fonts and responsive patterns

### Next Coding Session
1. [ ] Design mobile-first template architecture
2. [ ] Create base template with navigation
3. [ ] Build city page templates
4. [ ] Create data seeding script
5. [ ] Build remaining section pages

---

## Important Context

### Business Rules
- This is a relocation guide for Hampton Roads, VA region
- Content comes directly from the 40-page PDF brochure
- Target audience: Military families and others relocating to the area
- Future feature: AI-generated events/happenings content

### Technical Constraints
- Domain: abouthamptonroads.com
- **Mobile-first is critical** - many users viewing on phones during relocation
- Images from PDF are placeholders - higher-res originals coming later

### The 9 Cities

**Southside (South of James River):**
- Virginia Beach (has beaches)
- Chesapeake
- Norfolk
- Portsmouth
- Suffolk
- Smithfield

**Peninsula (North of James River):**
- Hampton
- Newport News
- Williamsburg/Yorktown

### City Page Content Pattern
Each city has:
- Description paragraph
- Restaurants list (15-20 items)
- Cafes & Breweries list (10-15 items)
- Attractions list (20+ items)
- Events & Festivals list
- Beaches (Virginia Beach primarily)

---

## Known Issues Being Tracked

### Active Issues
- [ ] Images need extraction from PDF
- [ ] CMS app partially built but paused - may need cleanup later

### Recently Resolved
- [x] Domain models created and migrated
- [x] PDF fully analyzed and understood

---

## Reference Information

### Key Stakeholders
- Robert & Nate Pickles - CEOs, Trustworthy Agents Group

### External Documentation
- Relocation guide PDF: `claude/specs/abouthr.pdf` (40 pages)
- Split pages: `claude/specs/pages/page_*.pdf`
- Trustworthy Agents website: www.trustworthyagents.com
- Home search site: explorevirginiahomes.com

### Reference Projects
- `../tagApp` - Good infrastructure patterns (Django app)
- `../trustworthyagents.com/prod` - Website patterns (can do better)

---

## Notes for Future Sessions

### Design Direction
- Mobile-first responsive design
- Modern, relevant fonts (research needed)
- Clean layout like PDF but optimized for web/mobile
- Bootstrap 5 as foundation

### Content to Seed
From PDF pages:
- Pages 4-5: About Hampton Roads overview text
- Pages 8-25: All 9 city content (descriptions, venue lists)
- Page 28: Military bases list
- Page 29: Tunnel descriptions
- Page 30: Vacation destinations
- Page 31: Vendor utilities per city
- Pages 32-34: Testimonials
- Page 36: Financing (Brad Schloss info)

### Future AI Features
- Current events in each city
- Upcoming events and happenings
- Dynamic content layer over static guide content

### Contact Info (for site footer/contact page)
- Office: 757-361-0106
- Direct: 757-500-2404
- Email: info@trustworthyagents.com
- Address: 1100 Volvo Parkway, Suite #200, Chesapeake, VA 23320
