# About Hampton Roads - Context Memory

**Last Updated:** 2026-01-18

## Current Status
Phase 3 Complete. Site is fully functional with images, SEO, and performance optimizations. Ready for deployment to production.

---

## Working Context

### Active Focus Area
Deployment preparation. All development phases (1-3) complete.

### Recent Decisions
- **Single Venue Model:** Instead of 5 separate models, using one with `venue_type` discriminator
- **Mobile-First Priority:** Perfect on phone > great on tablet > good on desktop
- **PDF is THE Content:** Not reference material - the exact content to display
- **CMS Deprioritized:** No content staff, focus on public site first
- **BaseModel (not AccountScopedModel):** Guide content is single-tenant shared
- **Font Choice:** Montserrat (headers) + Inter (body) - premium mobile-friendly fonts
- **Tabs/Accordions:** Desktop uses tabs for content, mobile uses accordions for touch UX
- **Static Images:** City images stored as static files, not in database
- **Dynamic Sitemap:** Generated via view to auto-include new content

### Patterns Being Used
- **BaseModel:** Abstract model with created_at/updated_at timestamps
- **Venue with venue_type:** Unified model for restaurants, cafes, attractions, events, beaches
- **Region/City hierarchy:** Peninsula vs Southside geographic organization
- **Class-based views:** TemplateView, ListView, DetailView for all pages
- **CSS Variables:** Centralized theming with custom properties
- **Lazy Loading:** Native browser lazy loading for images

---

## Session Priorities

### Completed (Phases 1-3)
1. [COMPLETED] All PDF content seeded to database (501 venues, 16 bases, etc.)
2. [COMPLETED] Base template with Bootstrap 5 + Montserrat/Inter fonts
3. [COMPLETED] Homepage with hero, city cards, quick links
4. [COMPLETED] City detail pages with tabs/accordions for venues
5. [COMPLETED] All special pages (military, tunnels, vacation, utilities, testimonials, about, contact)
6. [COMPLETED] URL routing for all pages
7. [COMPLETED] Hero and city images added
8. [COMPLETED] CSS polish with animations and transitions
9. [COMPLETED] OpenGraph and Twitter Card meta tags
10. [COMPLETED] Dynamic sitemap.xml and robots.txt
11. [COMPLETED] Lazy loading for all images

### Next Session (Deployment)
1. [ ] Deploy to development server
2. [ ] Test on real mobile devices
3. [ ] Configure DNS for abouthamptonroads.com
4. [ ] Deploy to production
5. [ ] SSL certificate setup
6. [ ] Image optimization on server

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
- Images need optimization during deployment (some up to 1.1MB)

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
- [ ] Image sizes large (up to 1.1MB) - optimize during deployment
- [ ] OpenGraph image URLs are relative - may need absolute for some platforms
- [ ] CMS app partially built but paused - may need cleanup later

### Recently Resolved
- [x] MilitaryBase slug field too short - increased to 255
- [x] VendorUtility phone field too short - increased to 50
- [x] All pages return 200 status
- [x] Static files loading correctly
- [x] Hero and city images added
- [x] SEO meta tags implemented
- [x] Sitemap and robots.txt working

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

### Design Direction - IMPLEMENTED
- Mobile-first responsive design - DONE
- Montserrat (headers) + Inter (body) fonts - DONE
- Clean layout optimized for web/mobile - DONE
- Bootstrap 5 as foundation - DONE
- CSS animations and transitions - DONE

### Content Seeded - ALL DONE
- [x] Pages 4-5: About Hampton Roads overview text
- [x] Pages 8-25: All 9 city content (descriptions, venue lists) - 501 venues
- [x] Page 28: Military bases list - 16 bases
- [x] Page 29: Tunnel descriptions - 6 tunnels
- [x] Page 30: Vacation destinations - 13 destinations
- [x] Page 31: Vendor utilities per city - 47 utilities
- [x] Pages 32-34: Testimonials - 7 testimonials
- [x] Team members: Robert & Nate Pickles - 2 members

### SEO - IMPLEMENTED
- [x] OpenGraph meta tags
- [x] Twitter Card meta tags
- [x] Dynamic sitemap.xml (17 URLs)
- [x] robots.txt

### Future AI Features (Phase 4)
- Current events in each city
- Upcoming events and happenings
- Dynamic content layer over static guide content

### Contact Info (in site footer and contact page)
- Office: 757-361-0106
- Direct: 757-500-2404
- Email: info@trustworthyagents.com
- Address: 1100 Volvo Parkway, Suite #200, Chesapeake, VA 23320
