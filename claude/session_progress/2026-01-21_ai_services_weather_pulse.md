# Session Progress: AI Services, Weather & Hampton Roads Pulse

**Date:** 2026-01-21 (Evening Session)
**Duration:** ~3 hours
**Focus:** AI infrastructure, weather integration, dynamic content system

---

## Session Overview

Built comprehensive AI services infrastructure and dynamic content features to make the site "bookmark-worthy" with fresh, updating content. Implemented weather display, X trends, and local news headlines.

### Objectives
1. Implement AI services infrastructure with model switching and cost tracking
2. Add weather display to city pages
3. Create "Hampton Roads Pulse" - trending topics and local headlines
4. Build CMS dashboard for managing pulse content and timers

---

## Major Accomplishments

### 1. AI Services Infrastructure
Created full `ai_services` Django app adapted from TAG App:

- **Models:** `AIProvider`, `AIModel`, `AIOperationConfig`, `AIUsageLog`
- **Operations configured for abouthr:**
  - content_venue_description, content_city_description, content_refresh
  - research_events, research_happenings, research_fact_check
  - search_venues, general_assistant
- **Model Selector:** Hardcoded defaults with database override capability
- **Pricing Configuration:** YAML-based pricing for all providers
- **Seeding:** Management command to seed 5 providers, 17 models, 8 operations

### 2. Weather Integration (Open-Meteo)
- **Service:** `guide/services/weather_service.py`
- **Features:**
  - Current conditions (temp, feels like, humidity, wind)
  - 5-day forecast
  - Weather codes mapped to Bootstrap icons
  - 15-minute cache to minimize API calls
  - Hardcoded coordinates for all 9 Hampton Roads cities
- **Display:** Blue gradient weather card on city detail pages
- **Cost:** FREE (no API key required)

### 3. Hampton Roads Pulse
Dynamic homepage widget with two content streams:

**X Trends (via Grok):**
- Uses grok-3-fast with x_search capability
- Fetches 5 trending local topics
- Includes sentiment analysis (positive/negative/neutral)
- Cost: ~$0.01 per refresh

**Local Headlines (via Claude Haiku):**
- Fetches from 4 RSS feeds: Virginian-Pilot, WAVY, 13 News Now, Daily Press
- AI summarizes to 5 most important stories
- Categorizes: development, traffic, events, weather, crime, politics, etc.
- Cost: ~$0.004 per refresh

**Architecture:**
- `PulseContent` model for cached JSON storage
- Automatic expiration (4 hours for trends, 6 hours for headlines)
- Page loads only use cache (no API calls blocking requests)
- Management command for manual/scheduled refresh

### 4. Pulse Dashboard (CMS)
Full management interface at `/cms/pulse/`:
- Status cards showing current trends and headlines preview
- Cost statistics (monthly cost, refreshes, tokens)
- Scheduled timer controls (start/stop/enable/disable)
- Refresh history table
- Manual refresh buttons

### 5. Bug Fixes
- **AI Model Manager Bootstrap error:** Fixed by wrapping script in DOMContentLoaded
- **AIUsageLog error:** Added response_time_ms=0 for background refreshes
- **Sluggish page loads:** Changed pulse service to only return cached data on page load

---

## Files Created

### AI Services App
```
ai_services/
├── __init__.py
├── apps.py
├── models.py                    # AIProvider, AIModel, AIOperationConfig, AIUsageLog
├── pricing.py                   # Pricing utilities
├── model_selector.py            # Model configuration with fallbacks
├── usage_tracking.py            # Cost tracking utilities
├── admin.py                     # Django admin integration
├── config/
│   └── providers.yaml           # Model pricing configuration
└── management/commands/
    └── seed_ai_models.py        # Seeding command
```

### Weather Service
```
guide/services/weather_service.py    # Open-Meteo integration
```

### Pulse System
```
guide/services/trends_service.py     # Grok X search
guide/services/headlines_service.py  # RSS + Claude summarization
guide/services/pulse_service.py      # Orchestration + caching
guide/management/commands/refresh_pulse.py
```

### CMS Views & Templates
```
cms/views/ai_settings.py             # AI cost report + model manager
cms/views/pulse_dashboard.py         # Pulse management
templates/cms/ai/cost_report.html
templates/cms/ai/model_manager.html
templates/cms/pulse/dashboard.html
templates/guide/includes/pulse_widget.html
```

---

## Files Modified

| File | Changes |
|------|---------|
| `guide/models.py` | Added `PulseContent` model |
| `guide/views.py` | Added weather to CityDetailView, pulse to HomeView |
| `guide/services/__init__.py` | Exported weather and pulse services |
| `cms/urls.py` | Added AI and pulse routes |
| `templates/cms/components/sidebar.html` | Added AI Models, AI Costs, Pulse Dashboard links |
| `templates/guide/home.html` | Added pulse widget include |
| `templates/guide/city_detail.html` | Added weather card |
| `static/css/style.css` | Added weather card and pulse widget styles |
| `abouthr/settings.py` | Added `ai_services` to INSTALLED_APPS |
| `requirements.txt` | Added anthropic, openai, feedparser, pyyaml |

---

## Database Changes

### New Migration
- `guide/migrations/0005_pulse_content.py` - PulseContent model
- `ai_services/migrations/0001_initial.py` - All AI services models

### Seeded Data
- 5 AI Providers (Anthropic, OpenAI, xAI, Google AI, Black Forest Labs)
- 17 AI Models with pricing
- 8 Operation Configurations

---

## Server Configuration

### Systemd Timers Created
```
/etc/systemd/system/pulse-refresh.timer
/etc/systemd/system/pulse-refresh.service
/etc/systemd/system/venue-refresh.timer
/etc/systemd/system/venue-refresh.service
```

### Sudoers Configuration
```
/etc/sudoers.d/abouthr-timers
```
Allows abouthr_user to manage timers without password.

---

## Cost Estimates

| Feature | Frequency | Monthly Cost |
|---------|-----------|--------------|
| Pulse - X Trends | 6x/day | ~$1.80 |
| Pulse - Headlines | 4x/day | ~$0.50 |
| Weather | FREE | $0 |
| **Total** | | **~$2-5/month** |

---

## Architectural Decisions

1. **Pulse caching strategy:** Page loads only return cached data. API calls happen via management command/timer, not during requests.

2. **Weather coordinates hardcoded:** Only 9 cities, unlikely to change. Avoided database migration.

3. **RSS over web search for headlines:** More reliable, lower cost than AI web search.

4. **Grok for X trends:** Only provider with native X search capability.

5. **Separate services pattern:** trends_service, headlines_service, pulse_service - clean separation of concerns.

---

## Pending / Next Session

### Immediate
- [ ] Add utility companies expandable section to city pages
- [ ] Test AI Model Manager edit functionality (Bootstrap fix deployed)
- [ ] Image optimization

### Future
- [ ] City-specific pulse content
- [ ] Push notifications for breaking news
- [ ] Historical trends comparison

---

## API Keys Required

All keys configured in `.keys`:
```
ANTHROPIC_API_KEY=xxx
XAI_API_KEY=xxx
OPENAI_API_KEY=xxx
GOOGLE_AI_API_KEY=xxx
GOOGLE_PLACES_API_KEY=xxx
BFL_API_KEY=xxx
```

---

## Commands Reference

```bash
# Refresh pulse content
python manage.py refresh_pulse           # Refresh if expired
python manage.py refresh_pulse --force   # Force refresh
python manage.py refresh_pulse --stats   # Show statistics

# Seed AI models
python manage.py seed_ai_models

# Timer management
sudo systemctl start pulse-refresh.timer
sudo systemctl status pulse-refresh.timer
systemctl list-timers pulse-refresh.timer
```
