# Hampton Roads Pulse - Implementation Spec

## Overview

A dynamic homepage widget showing real-time local trends and news summaries, refreshed every 4-6 hours. Creates "bookmark-worthy" content that brings users back.

---

## Feature Components

### 1. X Trends (via Grok)
- 3-5 trending local topics people are buzzing about
- Uses Grok's `x_search` tool to find what Hampton Roads is discussing
- Examples: "HRBT traffic", "Norfolk flooding", "VA Beach oceanfront event"

### 2. Local Headlines (via Claude Haiku)
- 3-5 AI-summarized headlines from local news
- Sources: Local RSS feeds or web search
- Brief, scannable summaries (1-2 sentences each)

### 3. Display Widget
- Clean card on homepage
- "Last updated: 2 hours ago" timestamp
- Mobile-friendly layout
- Optional: "Refresh" button for logged-in users

---

## Data Model

**File:** `guide/models.py`

```python
class PulseContent(models.Model):
    """
    Cached pulse content - trends and headlines.
    One active record per content type at a time.
    """
    CONTENT_TYPES = [
        ('trends', 'X Trends'),
        ('headlines', 'Local Headlines'),
    ]

    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    content_json = models.JSONField()  # List of items
    generated_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    model_used = models.CharField(max_length=100)
    tokens_used = models.PositiveIntegerField(default=0)
    cost_usd = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['content_type', 'is_active']),
        ]

    @classmethod
    def get_current(cls, content_type):
        """Get current active content, or None if expired."""
        from django.utils import timezone
        return cls.objects.filter(
            content_type=content_type,
            is_active=True,
            expires_at__gt=timezone.now()
        ).first()
```

**Content JSON Structure:**

```python
# Trends content_json
{
    "items": [
        {
            "topic": "HRBT Traffic",
            "summary": "Major delays reported after morning accident...",
            "sentiment": "negative",  # positive/negative/neutral
            "post_count": "2.4K posts"
        },
        # ... more items
    ],
    "query_used": "Hampton Roads Virginia trending",
    "search_timestamp": "2024-01-21T10:30:00Z"
}

# Headlines content_json
{
    "items": [
        {
            "headline": "Norfolk announces new waterfront development",
            "summary": "A $50M project will transform the downtown waterfront...",
            "source": "Virginian-Pilot",
            "category": "development"  # development/traffic/events/weather/crime/politics
        },
        # ... more items
    ],
    "sources_checked": ["pilotonline.com", "wavy.com", "13newsnow.com"]
}
```

---

## Service Layer

### Directory Structure
```
guide/
├── services/
│   ├── pulse_service.py        # Main orchestration
│   ├── trends_service.py       # Grok X search
│   └── headlines_service.py    # News fetching + summarization
```

### Trends Service

**File:** `guide/services/trends_service.py`

```python
"""
Fetch trending topics from X via Grok API.
"""
import os
import json
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from openai import OpenAI  # xAI uses OpenAI-compatible API

logger = logging.getLogger(__name__)

TRENDS_PROMPT = """You are a local news analyst for Hampton Roads, Virginia.

Search X/Twitter for what people in Hampton Roads are currently talking about.
Focus on: {focus_areas}

Return exactly 5 trending local topics in this JSON format:
{{
    "items": [
        {{
            "topic": "Brief topic name (2-5 words)",
            "summary": "What people are saying about this (1-2 sentences)",
            "sentiment": "positive|negative|neutral",
            "relevance": "Why this matters to HR residents (1 sentence)"
        }}
    ]
}}

Prioritize:
1. Breaking local news
2. Traffic/weather impacts
3. Local events and happenings
4. Community discussions
5. Military/base news

Exclude: National politics, celebrity gossip, sports scores (unless local teams)."""

FOCUS_AREAS = [
    "Virginia Beach", "Norfolk", "Chesapeake", "Newport News", "Hampton",
    "HRBT", "MMBT", "Downtown Tunnel",
    "Naval Station Norfolk", "Langley AFB", "Fort Eustis",
    "local events", "traffic", "weather"
]


class TrendsService:
    """Fetch X trends via Grok API."""

    def __init__(self):
        self.api_key = os.environ.get('XAI_API_KEY', '')
        self.client = None
        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.x.ai/v1"
            )

    def fetch_trends(self) -> dict | None:
        """
        Fetch current trending topics for Hampton Roads.

        Returns:
            dict with 'items' list and metadata, or None on failure
        """
        if not self.client:
            logger.error("XAI API key not configured")
            return None

        try:
            response = self.client.chat.completions.create(
                model="grok-3-fast",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a local trends analyst. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": TRENDS_PROMPT.format(focus_areas=", ".join(FOCUS_AREAS))
                    }
                ],
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "x_search",
                            "description": "Search X/Twitter for posts",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string"}
                                }
                            }
                        }
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )

            content = response.choices[0].message.content

            # Parse JSON from response
            result = json.loads(content)
            result['query_used'] = ", ".join(FOCUS_AREAS[:5])
            result['search_timestamp'] = datetime.now().isoformat()

            # Track usage
            usage = {
                'input_tokens': response.usage.prompt_tokens,
                'output_tokens': response.usage.completion_tokens,
                'model': 'grok-3-fast'
            }
            result['_usage'] = usage

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Grok response as JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching trends: {e}")
            return None


trends_service = TrendsService()
```

### Headlines Service

**File:** `guide/services/headlines_service.py`

```python
"""
Fetch and summarize local news headlines.
"""
import os
import json
import logging
import feedparser
import requests
from datetime import datetime
from anthropic import Anthropic

logger = logging.getLogger(__name__)

# Local news RSS feeds
LOCAL_RSS_FEEDS = [
    {
        'name': 'Virginian-Pilot',
        'url': 'https://www.pilotonline.com/arc/outboundfeeds/rss/?outputType=xml',
        'priority': 1
    },
    {
        'name': 'WAVY News 10',
        'url': 'https://www.wavy.com/feed/',
        'priority': 2
    },
    {
        'name': '13 News Now',
        'url': 'https://www.13newsnow.com/feeds/syndication/rss/news/local',
        'priority': 2
    },
    {
        'name': 'Daily Press',
        'url': 'https://www.dailypress.com/arc/outboundfeeds/rss/?outputType=xml',
        'priority': 2
    },
]

SUMMARIZE_PROMPT = """You are a local news editor for Hampton Roads, Virginia.

Given these recent news headlines and snippets, select the 5 most important/interesting stories for Hampton Roads residents and write brief summaries.

NEWS ITEMS:
{news_items}

Return JSON in this exact format:
{{
    "items": [
        {{
            "headline": "Clear, engaging headline (rewrite if needed)",
            "summary": "1-2 sentence summary of why this matters",
            "source": "Original source name",
            "category": "development|traffic|events|weather|crime|politics|business|community"
        }}
    ]
}}

Prioritize: Local impact, breaking news, community interest, unusual/interesting stories.
Exclude: Routine crime blotter, sports scores, obituaries, national news."""


class HeadlinesService:
    """Fetch local news and generate AI summaries."""

    def __init__(self):
        self.api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        self.client = None
        if self.api_key:
            self.client = Anthropic(api_key=self.api_key)

    def fetch_rss_items(self, max_items: int = 20) -> list[dict]:
        """Fetch recent items from local RSS feeds."""
        all_items = []

        for feed_config in LOCAL_RSS_FEEDS:
            try:
                feed = feedparser.parse(feed_config['url'])
                for entry in feed.entries[:10]:  # Max 10 per feed
                    all_items.append({
                        'title': entry.get('title', ''),
                        'summary': entry.get('summary', entry.get('description', ''))[:500],
                        'source': feed_config['name'],
                        'link': entry.get('link', ''),
                        'published': entry.get('published', ''),
                        'priority': feed_config['priority']
                    })
            except Exception as e:
                logger.warning(f"Failed to fetch {feed_config['name']}: {e}")

        # Sort by priority and recency
        all_items.sort(key=lambda x: x['priority'])
        return all_items[:max_items]

    def summarize_headlines(self, news_items: list[dict]) -> dict | None:
        """
        Use Claude to summarize and select top headlines.

        Returns:
            dict with 'items' list and metadata, or None on failure
        """
        if not self.client:
            logger.error("Anthropic API key not configured")
            return None

        if not news_items:
            logger.warning("No news items to summarize")
            return None

        # Format news items for prompt
        formatted_items = "\n\n".join([
            f"SOURCE: {item['source']}\n"
            f"HEADLINE: {item['title']}\n"
            f"SNIPPET: {item['summary'][:300]}"
            for item in news_items
        ])

        try:
            response = self.client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": SUMMARIZE_PROMPT.format(news_items=formatted_items)
                    }
                ]
            )

            content = response.content[0].text

            # Parse JSON from response
            result = json.loads(content)
            result['sources_checked'] = list(set(item['source'] for item in news_items))
            result['generated_at'] = datetime.now().isoformat()

            # Track usage
            usage = {
                'input_tokens': response.usage.input_tokens,
                'output_tokens': response.usage.output_tokens,
                'model': 'claude-haiku-4-5-20251001'
            }
            result['_usage'] = usage

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response as JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Error summarizing headlines: {e}")
            return None

    def fetch_headlines(self) -> dict | None:
        """Full pipeline: fetch RSS then summarize."""
        news_items = self.fetch_rss_items()
        if not news_items:
            return None
        return self.summarize_headlines(news_items)


headlines_service = HeadlinesService()
```

### Pulse Orchestration Service

**File:** `guide/services/pulse_service.py`

```python
"""
Hampton Roads Pulse - Main orchestration service.

Manages refreshing and caching of trends and headlines.
"""
import logging
from datetime import timedelta
from decimal import Decimal
from django.utils import timezone
from django.db import transaction

from guide.models import PulseContent
from .trends_service import trends_service
from .headlines_service import headlines_service
from ai_services.models import AIUsageLog

logger = logging.getLogger(__name__)

# Pricing per 1M tokens
PRICING = {
    'grok-3-fast': {'input': 5.00, 'output': 25.00},
    'claude-haiku-4-5-20251001': {'input': 1.00, 'output': 5.00},
}

# Cache durations
CACHE_HOURS = {
    'trends': 4,      # Refresh every 4 hours
    'headlines': 6,   # Refresh every 6 hours
}


class PulseService:
    """
    Orchestrates the Hampton Roads Pulse feature.

    Handles:
    - Fetching fresh content when cache expires
    - Cost tracking and logging
    - Graceful degradation on API failures
    """

    def get_pulse_data(self) -> dict:
        """
        Get current pulse data for display.

        Returns cached data if fresh, otherwise triggers refresh.
        Always returns a dict (may have empty sections on failure).
        """
        trends = self._get_or_refresh('trends')
        headlines = self._get_or_refresh('headlines')

        return {
            'trends': trends.content_json if trends else {'items': []},
            'trends_updated': trends.generated_at if trends else None,
            'headlines': headlines.content_json if headlines else {'items': []},
            'headlines_updated': headlines.generated_at if headlines else None,
        }

    def _get_or_refresh(self, content_type: str) -> PulseContent | None:
        """Get current content or refresh if expired."""
        current = PulseContent.get_current(content_type)

        if current:
            return current

        # Need to refresh
        logger.info(f"Refreshing pulse content: {content_type}")
        return self._refresh_content(content_type)

    def _refresh_content(self, content_type: str) -> PulseContent | None:
        """Fetch fresh content and store it."""
        if content_type == 'trends':
            result = trends_service.fetch_trends()
        elif content_type == 'headlines':
            result = headlines_service.fetch_headlines()
        else:
            logger.error(f"Unknown content type: {content_type}")
            return None

        if not result:
            logger.warning(f"Failed to fetch {content_type}")
            return None

        # Extract usage data
        usage = result.pop('_usage', {})

        # Calculate cost
        model = usage.get('model', '')
        input_tokens = usage.get('input_tokens', 0)
        output_tokens = usage.get('output_tokens', 0)

        cost = Decimal('0')
        if model in PRICING:
            cost = Decimal(str(
                (input_tokens / 1_000_000 * PRICING[model]['input']) +
                (output_tokens / 1_000_000 * PRICING[model]['output'])
            ))

        # Deactivate old content
        with transaction.atomic():
            PulseContent.objects.filter(
                content_type=content_type,
                is_active=True
            ).update(is_active=False)

            # Create new content
            pulse = PulseContent.objects.create(
                content_type=content_type,
                content_json=result,
                expires_at=timezone.now() + timedelta(hours=CACHE_HOURS[content_type]),
                model_used=model,
                tokens_used=input_tokens + output_tokens,
                cost_usd=cost,
                is_active=True
            )

            # Log to AI usage tracking
            if model:
                AIUsageLog.objects.create(
                    task_type='research_happenings' if content_type == 'trends' else 'research_events',
                    provider='xai' if 'grok' in model else 'anthropic',
                    model=model,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=input_tokens + output_tokens,
                    cost_usd=cost,
                    success=True,
                    metadata={'content_type': content_type}
                )

        return pulse

    def force_refresh(self, content_type: str = None) -> dict:
        """
        Force refresh content (for admin use).

        Args:
            content_type: 'trends', 'headlines', or None for both
        """
        results = {}

        types_to_refresh = [content_type] if content_type else ['trends', 'headlines']

        for ct in types_to_refresh:
            # Deactivate current to force refresh
            PulseContent.objects.filter(content_type=ct, is_active=True).update(is_active=False)
            result = self._refresh_content(ct)
            results[ct] = 'success' if result else 'failed'

        return results


pulse_service = PulseService()
```

---

## Management Command

**File:** `guide/management/commands/refresh_pulse.py`

```python
"""
Management command to refresh Hampton Roads Pulse content.

Usage:
    python manage.py refresh_pulse           # Refresh expired content only
    python manage.py refresh_pulse --force   # Force refresh all
    python manage.py refresh_pulse --trends  # Refresh trends only
    python manage.py refresh_pulse --headlines  # Refresh headlines only
"""
from django.core.management.base import BaseCommand
from guide.services.pulse_service import pulse_service


class Command(BaseCommand):
    help = 'Refresh Hampton Roads Pulse content (trends and headlines)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force refresh even if cache is valid'
        )
        parser.add_argument(
            '--trends',
            action='store_true',
            help='Refresh only trends'
        )
        parser.add_argument(
            '--headlines',
            action='store_true',
            help='Refresh only headlines'
        )

    def handle(self, *args, **options):
        if options['force']:
            if options['trends']:
                result = pulse_service.force_refresh('trends')
            elif options['headlines']:
                result = pulse_service.force_refresh('headlines')
            else:
                result = pulse_service.force_refresh()

            self.stdout.write(f"Force refresh complete: {result}")
        else:
            # Normal refresh (only if expired)
            data = pulse_service.get_pulse_data()

            trends_status = "OK" if data['trends']['items'] else "EMPTY"
            headlines_status = "OK" if data['headlines']['items'] else "EMPTY"

            self.stdout.write(f"Trends: {trends_status} (updated: {data['trends_updated']})")
            self.stdout.write(f"Headlines: {headlines_status} (updated: {data['headlines_updated']})")
```

---

## Systemd Timer (Auto-Refresh)

**File:** `systemd/pulse-refresh.service`

```ini
[Unit]
Description=Refresh Hampton Roads Pulse content
After=network.target postgresql.service

[Service]
Type=oneshot
User=abouthr_user
WorkingDirectory=/var/www/abouthamptonroads.com/dev
ExecStart=/usr/local/pyenv/shims/python manage.py refresh_pulse
StandardOutput=journal
StandardError=journal
```

**File:** `systemd/pulse-refresh.timer`

```ini
[Unit]
Description=Refresh Hampton Roads Pulse every 4 hours

[Timer]
# Every 4 hours starting at midnight
OnCalendar=*-*-* 00,04,08,12,16,20:00:00 America/New_York
Persistent=true
RandomizedDelaySec=300

[Install]
WantedBy=timers.target
```

---

## Template Integration

**File:** `templates/guide/includes/pulse_widget.html`

```html
<!-- Hampton Roads Pulse Widget -->
<div class="pulse-widget">
    <div class="pulse-header">
        <h3><i class="bi bi-lightning-charge-fill text-warning me-2"></i>Hampton Roads Pulse</h3>
        <small class="text-muted">What's happening now</small>
    </div>

    <div class="row g-4">
        <!-- Trending Topics -->
        <div class="col-md-6">
            <div class="pulse-section">
                <h5 class="pulse-section-title">
                    <i class="bi bi-twitter-x me-2"></i>Trending Now
                </h5>
                {% if pulse.trends.items %}
                <ul class="pulse-list">
                    {% for item in pulse.trends.items %}
                    <li class="pulse-item">
                        <div class="pulse-topic">{{ item.topic }}</div>
                        <div class="pulse-summary">{{ item.summary }}</div>
                        {% if item.sentiment == 'positive' %}
                        <span class="badge bg-success-subtle text-success">
                            <i class="bi bi-emoji-smile"></i>
                        </span>
                        {% elif item.sentiment == 'negative' %}
                        <span class="badge bg-danger-subtle text-danger">
                            <i class="bi bi-exclamation-triangle"></i>
                        </span>
                        {% endif %}
                    </li>
                    {% endfor %}
                </ul>
                {% if pulse.trends_updated %}
                <small class="text-muted">
                    <i class="bi bi-clock me-1"></i>{{ pulse.trends_updated|timesince }} ago
                </small>
                {% endif %}
                {% else %}
                <p class="text-muted">Trends temporarily unavailable</p>
                {% endif %}
            </div>
        </div>

        <!-- Local Headlines -->
        <div class="col-md-6">
            <div class="pulse-section">
                <h5 class="pulse-section-title">
                    <i class="bi bi-newspaper me-2"></i>Local Headlines
                </h5>
                {% if pulse.headlines.items %}
                <ul class="pulse-list">
                    {% for item in pulse.headlines.items %}
                    <li class="pulse-item">
                        <div class="pulse-headline">{{ item.headline }}</div>
                        <div class="pulse-summary">{{ item.summary }}</div>
                        <div class="pulse-meta">
                            <span class="badge bg-light text-dark">{{ item.source }}</span>
                            <span class="badge bg-secondary">{{ item.category }}</span>
                        </div>
                    </li>
                    {% endfor %}
                </ul>
                {% if pulse.headlines_updated %}
                <small class="text-muted">
                    <i class="bi bi-clock me-1"></i>{{ pulse.headlines_updated|timesince }} ago
                </small>
                {% endif %}
                {% else %}
                <p class="text-muted">Headlines temporarily unavailable</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>
```

---

## Homepage View Update

**File:** `guide/views.py` (modify HomeView)

```python
class HomeView(TemplateView):
    """Homepage with overview and city cards."""
    template_name = 'guide/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['regions'] = Region.objects.prefetch_related('cities').all()
        context['cities'] = City.objects.select_related('region').filter(is_published=True)
        context['testimonials'] = Testimonial.objects.filter(is_published=True, is_featured=True)[:3]

        # Add Hampton Roads Pulse
        from guide.services.pulse_service import pulse_service
        context['pulse'] = pulse_service.get_pulse_data()

        return context
```

---

## CSS Styles

**Add to:** `static/css/style.css`

```css
/* ===== Hampton Roads Pulse ===== */
.pulse-widget {
    background: var(--bg-white);
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    margin-bottom: 2rem;
}

.pulse-header {
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid var(--primary-color);
}

.pulse-header h3 {
    margin-bottom: 0.25rem;
    font-size: 1.25rem;
}

.pulse-section {
    background: var(--bg-light);
    border-radius: 8px;
    padding: 1rem;
    height: 100%;
}

.pulse-section-title {
    font-size: 1rem;
    margin-bottom: 1rem;
    color: var(--primary-color);
}

.pulse-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.pulse-item {
    padding: 0.75rem 0;
    border-bottom: 1px solid var(--border-color);
}

.pulse-item:last-child {
    border-bottom: none;
}

.pulse-topic,
.pulse-headline {
    font-weight: 600;
    font-size: 0.95rem;
    margin-bottom: 0.25rem;
    color: var(--text-dark);
}

.pulse-summary {
    font-size: 0.85rem;
    color: var(--text-muted);
    line-height: 1.4;
    margin-bottom: 0.5rem;
}

.pulse-meta {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}

/* Mobile adjustments */
@media (max-width: 768px) {
    .pulse-widget {
        padding: 1rem;
    }

    .pulse-section {
        margin-bottom: 1rem;
    }
}
```

---

## Dependencies

Add to `requirements.txt`:
```
feedparser>=6.0.0
```

---

## Implementation Order

1. **Add feedparser dependency** - `pip install feedparser`
2. **Create PulseContent model** - Add to guide/models.py, run migrations
3. **Create services** - trends_service.py, headlines_service.py, pulse_service.py
4. **Update services/__init__.py** - Export new services
5. **Create management command** - refresh_pulse.py
6. **Update HomeView** - Add pulse data to context
7. **Create template partial** - pulse_widget.html
8. **Update home.html** - Include pulse widget
9. **Add CSS styles** - Pulse widget styles
10. **Test manually** - `python manage.py refresh_pulse --force`
11. **Set up systemd timer** - For automated refresh

---

## API Keys Required

In `.keys` file:
```
XAI_API_KEY=your-xai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
```

---

## Cost Tracking

All AI calls are logged to `AIUsageLog` with:
- `task_type`: 'research_happenings' (trends) or 'research_events' (headlines)
- Full token counts and cost calculations
- Links to AI Cost Report in CMS

---

## Future Enhancements

1. **City-specific pulse** - Filter trends/news by city
2. **Push notifications** - Alert users to breaking news
3. **User preferences** - Let users choose categories
4. **Historical trends** - "This time last year..."
5. **Social sharing** - Share interesting trends
