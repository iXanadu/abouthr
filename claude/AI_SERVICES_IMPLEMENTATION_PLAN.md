# AI Services Implementation Plan for About Hampton Roads

**Date**: 2026-01-18
**Status**: Planning
**Source**: Porting ai_services from TAG App (`/var/www/app.trustworthyagents.com/dev`)

---

## Overview

This document outlines the plan to integrate AI capabilities into About Hampton Roads using the proven ai_services framework from the TAG App.

**Reference**: See `TAG App/claude/AI_SERVICES_PORTABILITY_ANALYSIS.md` for detailed analysis of the source code.

---

## Project Context

**About Hampton Roads** is a public website providing local information:
- 501 venues (restaurants, attractions, beaches, events, cafes)
- 9 cities with descriptions and images
- Military bases, tunnels, vacation destinations
- CMS backend for content management
- Single maintainer (TAG)

**AI Use Cases** (planned):
- Auto-generate/refresh venue descriptions
- Discover current local events (web search)
- Content freshness monitoring
- Future: Drive times, local search, recommendations

---

## Architecture Decision: Account Scoping

### Current State
- `Account` model exists in `accounts` app
- `AccountScopedModel` base class exists in `core` app
- Guide content (Venue, City, etc.) is NOT account-scoped (correct for public content)

### Recommendation: Use Account for AI Tracking

**Create one Account** for "About Hampton Roads" to:
- Attribute all AI usage costs
- Enable future per-user tracking if needed
- Maintain consistency with TAG App patterns
- Keep AIUsageLog model unchanged

```python
# One-time setup
Account.objects.create(
    name="About Hampton Roads",
    slug="abouthr",
    is_active=True
)
```

---

## Files to Copy from TAG App

### Core Infrastructure (Copy As-Is)

```
From: /var/www/app.trustworthyagents.com/dev/ai_services/
To:   /var/www/abouthamptonroads.com/dev/ai_services/

ai_services/
├── __init__.py
├── apps.py
├── models.py              # All 6 models
├── pricing.py             # Cost calculation from YAML
├── usage_tracking.py      # log_ai_usage(), AIUsageTimer
├── admin.py               # Django admin interface
├── views.py               # Cost report, model manager views (optional)
├── urls.py                # Routes (optional)
├── config/
│   └── providers.yaml     # Provider/model pricing config
├── providers/
│   ├── __init__.py
│   └── base.py            # Abstract base class
└── management/
    └── commands/
        └── seed_ai_models.py  # Initialize DB from YAML
```

### Do NOT Copy (TAG App Domain-Specific)

```
# These are real estate specific - don't copy
ai_services/services/form_detector.py
ai_services/services/form_analyzer_registry.py
ai_services/services/purchase_agreement_extractor.py
ai_services/services/tax_form_extractor.py
ai_services/services/mls_extractor.py
ai_services/providers/openai_provider.py
ai_services/providers/anthropic_provider.py
```

---

## Customizations Required

### 1. Update OPERATION_CHOICES in models.py

Replace TAG App operations with abouthr operations:

```python
# ai_services/models.py

OPERATION_CHOICES = [
    # Content Generation
    ('content_venue_description', 'Venue Description Generation'),
    ('content_city_description', 'City Description Generation'),
    ('content_refresh', 'Content Refresh/Update'),

    # Web Research (Grok with web search)
    ('research_events', 'Event Discovery'),
    ('research_happenings', 'Local Happenings Search'),
    ('research_fact_check', 'Content Fact Checking'),

    # Future
    ('search_venues', 'Venue Search/Recommendations'),
    ('calculate_drive_time', 'Drive Time Calculation'),
]

TASK_TYPE_CHOICES = OPERATION_CHOICES  # Keep in sync
```

### 2. Update HARDCODED_DEFAULTS in model_selector.py

```python
# ai_services/model_selector.py

HARDCODED_DEFAULTS = {
    # Content Generation - Claude Haiku (cheap, fast, good enough)
    'content_venue_description': ModelConfig(
        provider='anthropic',
        model_id='claude-haiku-4-5-20251001',
        temperature=0.7,
        max_tokens=500
    ),
    'content_city_description': ModelConfig(
        provider='anthropic',
        model_id='claude-haiku-4-5-20251001',
        temperature=0.7,
        max_tokens=800
    ),
    'content_refresh': ModelConfig(
        provider='anthropic',
        model_id='claude-haiku-4-5-20251001',
        temperature=0.3,
        max_tokens=500
    ),

    # Web Research - Grok 4 (has live web search capability)
    'research_events': ModelConfig(
        provider='xai',
        model_id='grok-4-1-fast-reasoning',
        temperature=0.5,
        max_tokens=2000
    ),
    'research_happenings': ModelConfig(
        provider='xai',
        model_id='grok-4-1-fast-reasoning',
        temperature=0.5,
        max_tokens=2000
    ),
    'research_fact_check': ModelConfig(
        provider='xai',
        model_id='grok-4-1-fast-reasoning',
        temperature=0.2,
        max_tokens=1000
    ),
}
```

### 3. Update settings.py

```python
# abouthr/settings.py

INSTALLED_APPS = [
    ...
    'ai_services',  # Add this
]

# Optional: Add URL config for admin views
# abouthr/urls.py
urlpatterns = [
    ...
    path('ai/', include('ai_services.urls')),
]
```

### 4. Environment Variables

Add to `.env`:
```bash
# AI Provider API Keys
ANTHROPIC_API_KEY=sk-ant-...
XAI_API_KEY=xai-...

# Optional (if using these providers)
OPENAI_API_KEY=sk-...
BFL_API_KEY=...  # Black Forest Labs for FLUX images
```

---

## Implementation Steps

### Phase 1: Infrastructure Setup

```bash
# 1. Copy ai_services app
cp -r /var/www/app.trustworthyagents.com/dev/ai_services /var/www/abouthamptonroads.com/dev/

# 2. Remove TAG-specific files
rm -rf ai_services/services/
rm ai_services/providers/openai_provider.py
rm ai_services/providers/anthropic_provider.py

# 3. Update models.py with new OPERATION_CHOICES
# 4. Update model_selector.py with new HARDCODED_DEFAULTS
# 5. Update settings.py to include ai_services

# 6. Run migrations
python manage.py makemigrations ai_services
python manage.py migrate

# 7. Seed database with models
python manage.py seed_ai_models

# 8. Create Account for AI tracking
python manage.py shell
>>> from accounts.models import Account
>>> Account.objects.create(name="About Hampton Roads", slug="abouthr", is_active=True)
```

### Phase 2: Create AI Services

Create new services specific to abouthr:

```
ai_services/services/
├── __init__.py
├── venue_service.py       # Venue description generation
├── event_discovery.py     # Event/happenings web search
└── content_refresh.py     # Content freshness checking
```

Example service pattern:

```python
# ai_services/services/venue_service.py

import os
from anthropic import Anthropic
from ai_services.model_selector import get_model_config
from ai_services.usage_tracking import log_ai_usage
import time

class VenueDescriptionService:
    def __init__(self, account):
        self.account = account
        self.config = get_model_config('content_venue_description')
        self.client = Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])

    def generate_description(self, venue_name, venue_type, city, existing_info=None, user=None):
        """Generate or refresh a venue description."""
        start_time = time.time()

        prompt = self._build_prompt(venue_name, venue_type, city, existing_info)

        response = self.client.messages.create(
            model=self.config.model_id,
            temperature=self.config.temperature or 0.7,
            max_tokens=self.config.max_tokens or 500,
            messages=[{"role": "user", "content": prompt}]
        )

        elapsed_ms = int((time.time() - start_time) * 1000)

        # Log usage for cost tracking
        log_ai_usage(
            account=self.account,
            task_type='content_venue_description',
            model=self.config.model_id,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            response_time_ms=elapsed_ms,
            user=user,
            metadata={'venue_name': venue_name, 'city': city}
        )

        return response.content[0].text

    def _build_prompt(self, venue_name, venue_type, city, existing_info):
        return f"""Write a brief, engaging description for a {venue_type} in {city}, Hampton Roads, Virginia.

Venue: {venue_name}
Type: {venue_type}
City: {city}
{f"Existing info: {existing_info}" if existing_info else ""}

Requirements:
- 2-3 sentences, conversational tone
- Highlight what makes this venue special
- Mention the city/area context if relevant
- Don't make up specific details (hours, prices) unless provided
- Focus on atmosphere and experience

Description:"""
```

### Phase 3: CMS Integration

Add AI features to CMS venue editing:

```python
# cms/views/venue_views.py

from ai_services.services.venue_service import VenueDescriptionService

class VenueEditView(CMSAccessMixin, UpdateView):
    # ... existing code ...

    def post(self, request, *args, **kwargs):
        if 'generate_description' in request.POST:
            venue = self.get_object()
            account = Account.objects.get(slug='abouthr')
            service = VenueDescriptionService(account)

            description = service.generate_description(
                venue_name=venue.name,
                venue_type=venue.venue_type,
                city=venue.city.name,
                existing_info=venue.description,
                user=request.user
            )
            # Return via HTMX or redirect
            ...

        return super().post(request, *args, **kwargs)
```

---

## Cost Estimates

Based on TAG App experience:

| Operation | Model | Est. Cost per Call |
|-----------|-------|-------------------|
| Venue description | Claude Haiku 4.5 | ~$0.001 |
| City description | Claude Haiku 4.5 | ~$0.002 |
| Event discovery | Grok 4 | ~$0.15-0.20 |
| Content refresh | Claude Haiku 4.5 | ~$0.001 |

**Monthly estimates** (moderate usage):
- 100 venue descriptions: ~$0.10
- 50 city refreshes: ~$0.10
- 30 event discoveries: ~$5.00
- **Total**: ~$5-10/month

---

## Admin Features (Optional)

If you include `ai_services/views.py` and `ai_services/urls.py`:

| URL | Feature |
|-----|---------|
| `/ai/model-manager/` | Configure which model handles each operation |
| `/ai/cost-report/` | View AI spending by operation, time period |

These require superuser access.

---

## Future Considerations

### Event Discovery Automation

```python
# management/commands/discover_events.py
# Run daily via cron to find new local events

class Command(BaseCommand):
    def handle(self, *args, **options):
        service = EventDiscoveryService(account)
        events = service.discover_events(
            region="Hampton Roads",
            categories=["concerts", "festivals", "community"]
        )
        # Create/update Venue records with venue_type='event'
```

### Content Freshness Monitoring

```python
# Check if venue info is outdated
# Flag for human review or auto-refresh
```

### Search/Recommendations

```python
# "Find Italian restaurants near downtown Norfolk"
# Powered by AI understanding of venue data
```

---

## Checklist

- [ ] Copy ai_services app from TAG App
- [ ] Remove TAG-specific files (form extractors, providers)
- [ ] Update OPERATION_CHOICES for abouthr operations
- [ ] Update HARDCODED_DEFAULTS for abouthr models
- [ ] Add ai_services to INSTALLED_APPS
- [ ] Set environment variables (API keys)
- [ ] Run migrations
- [ ] Seed database with python manage.py seed_ai_models
- [ ] Create "About Hampton Roads" Account
- [ ] Create first service (VenueDescriptionService)
- [ ] Test with a single venue
- [ ] Add CMS integration (generate button)
- [ ] Optional: Add admin views for cost tracking

---

## Questions to Resolve

1. **Which operations are priority?**
   - Event discovery (most valuable for fresh content)?
   - Venue descriptions (bulk generation)?

2. **Automation level?**
   - Manual trigger from CMS?
   - Scheduled background jobs?
   - Both?

3. **Content review workflow?**
   - AI generates → human approves → publish?
   - AI generates → auto-publish with flag for review?

---

*Document created 2026-01-18 for abouthr AI integration planning*
