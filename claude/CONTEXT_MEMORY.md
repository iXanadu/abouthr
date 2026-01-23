# About Hampton Roads - Context Memory

**Last Updated:** 2026-01-23

## Current Status
**PRODUCTION LIVE & VERIFIED** at https://abouthamptonroads.com

Phase 7+ Complete. Site deployed to production with all features working: Drive Time Calculator, Hampton Roads Pulse, venue enrichment, weather integration. Systemd timers configured for automated content refresh.

SEO tagline added 2026-01-23: "Hampton Roads Interactive Relocation Guide" now appears in all meta tags, OG/Twitter cards, and visibly in the homepage hero section.

Drive Calculator promoted 2026-01-23: Added to main nav, footer (all pages), and homepage CTA section. Ready for sitemap submission to Google/Bing.

---

## Working Context

### Active Focus Area
Dynamic content features complete. Site now has fresh, updating content that gives users a reason to return.

### Recent Decisions
- **Single Venue Model:** Instead of 5 separate models, using one with `venue_type` discriminator
- **Mobile-First Priority:** Perfect on phone > great on tablet > good on desktop
- **PDF is THE Content:** Not reference material - the exact content to display
- **BaseModel (not AccountScopedModel):** Guide content is single-tenant shared
- **Font Choice:** Montserrat (headers) + Inter (body) - premium mobile-friendly fonts
- **Tabs/Accordions:** Desktop uses tabs for content, mobile uses accordions for touch UX
- **Weather API:** Open-Meteo chosen (free, no API key, reliable)
- **Pulse Caching:** Page loads only use cached data; API calls via timer/command only
- **Grok for X trends:** Only provider with native X search capability
- **RSS for headlines:** More reliable and cheaper than AI web search
- **Two API keys for Google:** Server-side (IP restricted) vs client-side (HTTP referrer restricted)
- **Modern Places API:** Using AutocompleteSuggestion instead of deprecated Autocomplete widget
- **Pulse Content Policy:** NO crime, fires, deaths, missing persons - this is a relocation guide, show positive community content
- **Infrastructure Ownership:** User's setup script handles nginx/SSL/gunicorn; Claude handles Django code only

### Patterns Being Used
- **AI Services:** Configurable model-per-operation with fallback chain
- **Service Layer:** Separate services for weather, trends, headlines, pulse orchestration
- **Cached Content:** PulseContent model stores JSON with expiration
- **Systemd Timers:** Automated refresh every 4 hours for pulse

---

## Session Priorities

### Completed (All Phases)
1. [COMPLETED] All PDF content seeded to database (501 venues, 16 bases, etc.)
2. [COMPLETED] Base template with Bootstrap 5 + Montserrat/Inter fonts
3. [COMPLETED] All 9 page templates + views + routing
4. [COMPLETED] OpenGraph, Twitter Cards, sitemap.xml, robots.txt
5. [COMPLETED] CMS infrastructure with all CRUD operations
6. [COMPLETED] Google Places API integration for venue enrichment
7. [COMPLETED] Rich venue display with photos, ratings, hours
8. [COMPLETED] Mobile-optimized venue cards
9. [COMPLETED] AI Services infrastructure (models, pricing, tracking)
10. [COMPLETED] Weather integration (Open-Meteo) on city pages
11. [COMPLETED] Hampton Roads Pulse (X trends + headlines)
12. [COMPLETED] Pulse Dashboard with timer controls
13. [COMPLETED] Systemd timers for automated refresh
14. [COMPLETED] Military bases map on /military/ page
15. [COMPLETED] Tunnels/bridges map on /tunnels/ page
16. [COMPLETED] Pulse widget collapsible UI with partial-open default
17. [COMPLETED] Pulse staleness fix - content always shows
18. [COMPLETED] Drive Time Calculator on city pages
19. [COMPLETED] DriveDestination model with 39 preset locations
20. [COMPLETED] Google Maps/Places/Directions API integration
21. [COMPLETED] CMS management for Drive Destinations
22. [COMPLETED] Utilities section added to city Quick Info
23. [COMPLETED] Drive Calculator landing page for marketing campaigns
24. [COMPLETED] Optimized landing page hero image (9MB→441KB)
25. [COMPLETED] Production deployment guide & sync_content command
26. [COMPLETED] **PRODUCTION DEPLOYED** - https://abouthamptonroads.com
27. [COMPLETED] Pulse headlines prompt fix - no crime/tragedy content
28. [COMPLETED] SEO tagline "Hampton Roads Interactive Relocation Guide" - all meta tags + visible hero
29. [COMPLETED] Drive Calculator visibility - nav menu, footer, homepage CTA section

### Next Session
1. [ ] **REMINDER: Add favicon.ico** (currently 404 - user requested reminder)
2. [ ] Submit sitemap to Google/Bing (ready now)
3. [ ] Test on real mobile devices
4. [ ] Monitor production logs for errors
5. [ ] Consider www redirect setup (www → non-www)
6. [ ] City-specific pulse content
7. [ ] Search functionality

---

## Important Context

### Business Rules
- This is a relocation guide for Hampton Roads, VA region
- Content comes directly from the 40-page PDF brochure
- Target audience: Military families and others relocating to the area
- Dynamic content (pulse) keeps users returning

### Technical Constraints
- Domain: abouthamptonroads.com
- **Mobile-first is critical** - many users viewing on phones during relocation
- Images need optimization during deployment (some up to 1.1MB)

### AI Services Configuration
| Operation | Provider | Model | Use Case |
|-----------|----------|-------|----------|
| research_happenings | xAI | grok-3-fast | X trends for Pulse |
| research_events | Anthropic | claude-haiku-4-5 | Headlines summarization |
| content_venue_description | Anthropic | claude-haiku-4-5 | Venue descriptions |
| content_city_description | Anthropic | claude-sonnet-4 | City descriptions |

### Systemd Timers
| Timer | Schedule | Purpose |
|-------|----------|---------|
| pulse-refresh | Every 4 hours | X trends + headlines |
| venue-refresh | Sundays 3 AM | Google Places refresh |

### Monthly Cost Estimates
| Service | Cost |
|---------|------|
| Pulse (trends + headlines) | ~$2-5/month |
| Venue refresh | ~$2/month |
| Weather | FREE |
| Google Places | ~$5-10/month |

---

## Known Issues Being Tracked

### Active Issues
- [ ] Favicon.ico missing (404 error)
- [ ] Image sizes large (up to 1.1MB) - optimize during deployment
- [ ] OpenGraph image URLs are relative - may need absolute for some platforms

### Recently Resolved
- [x] Production 400 error - nginx proxying to wrong port (8009→8014) - 2026-01-23
- [x] Google Maps API 403 - bare domain needed in referrer restrictions - 2026-01-23
- [x] Pulse showing empty when stale - now returns expired content as fallback
- [x] AI Model Manager Bootstrap error - fixed with DOMContentLoaded wrapper
- [x] AIUsageLog null constraint - added response_time_ms=0
- [x] Sluggish page loads - pulse now only uses cached data
- [x] Venue enrichment API timeout - fixed by limiting web sync
- [x] Systemd timer permissions - configured sudoers for abouthr_user

---

## Reference Information

### Key Stakeholders
- Robert & Nate Pickles - CEOs, Trustworthy Agents Group

### External Documentation
- Relocation guide PDF: `claude/specs/abouthr.pdf` (40 pages)
- Trustworthy Agents website: www.trustworthyagents.com
- Home search site: explorevirginiahomes.com

### API Keys Configured
All in `.keys` file:
- ANTHROPIC_API_KEY
- XAI_API_KEY
- OPENAI_API_KEY
- GOOGLE_AI_API_KEY
- GOOGLE_PLACES_API_KEY (server-side, IP restricted)
- GOOGLE_MAPS_API_KEY (client-side, HTTP referrer restricted)
- BFL_API_KEY (Black Forest Labs for images)

---

## Notes for Future Sessions

### Pending Features
- [x] Utility companies section on city pages
- [x] Drive Time Calculator on city pages
- [ ] City-specific pulse content
- [ ] Yelp integration (stub ready)
- [ ] Search functionality
- [ ] Contact form with email

### Server Files Created
```
/etc/systemd/system/pulse-refresh.timer
/etc/systemd/system/pulse-refresh.service
/etc/systemd/system/venue-refresh.timer
/etc/systemd/system/venue-refresh.service
/etc/sudoers.d/abouthr-timers
```

### Useful Commands
```bash
# Pulse management
python manage.py refresh_pulse --stats
python manage.py refresh_pulse --force
python manage.py refresh_pulse --trends
python manage.py refresh_pulse --headlines

# Timer management
systemctl list-timers pulse-refresh.timer
sudo systemctl start pulse-refresh.timer
sudo systemctl stop pulse-refresh.timer

# AI models
python manage.py seed_ai_models
```

### Contact Info (in site footer and contact page)
- Office: 757-361-0106
- Direct: 757-500-2404
- Email: info@trustworthyagents.com
- Address: 1100 Volvo Parkway, Suite #200, Chesapeake, VA 23320
