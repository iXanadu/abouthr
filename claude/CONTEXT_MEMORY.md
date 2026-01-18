# About Hampton Roads - Context Memory

**Last Updated:** 2026-01-18

## Current Status
Phase 1 Complete. All public website pages built and tested. Database seeded with all PDF content. Mobile-first design with Bootstrap 5 and premium fonts.

---

## Working Context

### Active Focus Area
Phase 1 complete - all pages working. Ready for review and Phase 2 enhancements.

### Recent Decisions
- **Single Venue Model:** Instead of 5 separate models, using one with `venue_type` discriminator
- **Mobile-First Priority:** Perfect on phone > great on tablet > good on desktop
- **PDF is THE Content:** Not reference material - the exact content to display
- **CMS Deprioritized:** No content staff, focus on public site first
- **BaseModel (not AccountScopedModel):** Guide content is single-tenant shared
- **Font Choice:** Montserrat (headers) + Inter (body) - premium mobile-friendly fonts
- **Tabs/Accordions:** Desktop uses tabs for content, mobile uses accordions for touch UX

### Patterns Being Used
- **BaseModel:** Abstract model with created_at/updated_at timestamps
- **Venue with venue_type:** Unified model for restaurants, cafes, attractions, events, beaches
- **Region/City hierarchy:** Peninsula vs Southside geographic organization
- **Class-based views:** TemplateView, ListView, DetailView for all pages
- **CSS Variables:** Centralized theming with custom properties

---

## Session Priorities

### Completed This Session (Phase 1)
1. [COMPLETED] All PDF content seeded to database (501 venues, 16 bases, etc.)
2. [COMPLETED] Base template with Bootstrap 5 + Montserrat/Inter fonts
3. [COMPLETED] Homepage with hero, city cards, quick links
4. [COMPLETED] City detail pages with tabs/accordions for venues
5. [COMPLETED] All special pages (military, tunnels, vacation, utilities, testimonials, about, contact)
6. [COMPLETED] URL routing for all pages
7. [COMPLETED] All pages tested and working

### Next Session (Phase 2)
1. [ ] Add city images to cards and detail pages
2. [ ] Add hero background images
3. [ ] Review and polish mobile responsiveness
4. [ ] UI refinements based on user review

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
- [ ] Hero section needs real background image
- [ ] City cards need images
- [ ] CMS app partially built but paused - may need cleanup later

### Recently Resolved
- [x] MilitaryBase slug field too short - increased to 255
- [x] VendorUtility phone field too short - increased to 50
- [x] All pages return 200 status
- [x] Static files loading correctly

---

## Reference Information

### Key Stakeholders
- Robert & Nate Pickles - CEOs, Trustworthy Agents Group

### External Documentation
- Relocation guide PDF: `claude/specs/abouthr.pdf` (40 pages)
- Split pages: `claude/specs/pages/page_*.pdf`
- Extracted images: `claude/specs/images/`
- Trustworthy Agents website: www.trustworthyagents.com
- Home search site: explorevirginiahomes.com

### Reference Projects
- `../tagApp` - Good infrastructure patterns (Django app)
- `../trustworthyagents.com/prod` - Website patterns (can do better)

---

## Notes for Future Sessions

### Design Direction
- Mobile-first responsive design - IMPLEMENTED
- Montserrat (headers) + Inter (body) fonts - IMPLEMENTED
- Clean layout optimized for web/mobile - IMPLEMENTED
- Bootstrap 5 as foundation - IMPLEMENTED

### Content Seeded
From PDF pages:
- [x] Pages 4-5: About Hampton Roads overview text
- [x] Pages 8-25: All 9 city content (descriptions, venue lists) - 501 venues
- [x] Page 28: Military bases list - 16 bases
- [x] Page 29: Tunnel descriptions - 6 tunnels
- [x] Page 30: Vacation destinations - 13 destinations
- [x] Page 31: Vendor utilities per city - 47 utilities
- [x] Pages 32-34: Testimonials - 7 testimonials
- [x] Team members: Robert & Nate Pickles - 2 members

### Future AI Features
- Current events in each city
- Upcoming events and happenings
- Dynamic content layer over static guide content

### Contact Info (in site footer and contact page)
- Office: 757-361-0106
- Direct: 757-500-2404
- Email: info@trustworthyagents.com
- Address: 1100 Volvo Parkway, Suite #200, Chesapeake, VA 23320
