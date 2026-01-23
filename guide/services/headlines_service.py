"""
Fetch and summarize local news headlines.

Pulls from local RSS feeds and uses Claude to summarize
the most important/interesting stories.
"""
import os
import json
import logging
from datetime import datetime
import feedparser
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

SUMMARIZE_PROMPT = """You are a local news editor for a Hampton Roads, Virginia RELOCATION GUIDE website.

Your audience is people considering moving to Hampton Roads. Select 5-6 stories that showcase the region positively while still being informative.

NEWS ITEMS:
{news_items}

Return JSON in this exact format (no markdown, just raw JSON):
{{
    "items": [
        {{
            "headline": "Clear, engaging headline (rewrite if needed for clarity)",
            "summary": "1-2 sentence summary of why this matters to local residents",
            "source": "Original source name",
            "category": "development|traffic|events|weather|crime|politics|business|community|military"
        }}
    ]
}}

CONTENT PRIORITIES (in order):
1. Community events, festivals, things to do
2. New business openings, restaurant news, economic development
3. Military community news (this is a major military region)
4. Infrastructure/development projects
5. Weather alerts (only if significant)
6. Local politics that affect quality of life

STRICT LIMITS:
- Maximum 1 crime/accident story, and ONLY if it's a major public safety issue (not routine crime)
- NO shootings, murders, or violent crime unless it's an extraordinary regional emergency
- NO routine traffic accidents
- NO obituaries or death notices
- NO national news without strong local angle

Remember: People use this site to decide if they want to MOVE here. Show them a vibrant, welcoming community."""


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
                for entry in feed.entries[:10]:
                    # Clean up summary text
                    summary = entry.get('summary', entry.get('description', ''))
                    # Remove HTML tags roughly
                    import re
                    summary = re.sub(r'<[^>]+>', '', summary)
                    summary = summary[:500]

                    all_items.append({
                        'title': entry.get('title', ''),
                        'summary': summary,
                        'source': feed_config['name'],
                        'link': entry.get('link', ''),
                        'published': entry.get('published', ''),
                        'priority': feed_config['priority']
                    })
                logger.info(f"Fetched {len(feed.entries[:10])} items from {feed_config['name']}")
            except Exception as e:
                logger.warning(f"Failed to fetch {feed_config['name']}: {e}")

        # Sort by priority
        all_items.sort(key=lambda x: x['priority'])
        return all_items[:max_items]

    def summarize_headlines(self, news_items: list[dict]) -> dict | None:
        """
        Use Claude to summarize and select top headlines.

        Returns:
            dict with 'items' list and metadata, or None on failure
        """
        if not self.client:
            logger.warning("Anthropic API key not configured, skipping headlines")
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

            # Clean up response if it has markdown code blocks
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
            content = content.strip()

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

            logger.info(f"Summarized {len(result.get('items', []))} headlines")
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
