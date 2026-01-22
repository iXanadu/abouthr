"""
Fetch trending topics from X via Grok API.

Uses xAI's Grok model with x_search tool to find what
Hampton Roads residents are talking about.
"""
import os
import json
import logging
from datetime import datetime
from openai import OpenAI

logger = logging.getLogger(__name__)

TRENDS_PROMPT = """You are a local news analyst for Hampton Roads, Virginia.

Search X/Twitter for what people in Hampton Roads are currently talking about.
Focus on these areas and topics: {focus_areas}

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

Exclude: National politics, celebrity gossip, sports scores (unless local teams like Norfolk Tides, ODU)."""

FOCUS_AREAS = [
    "Virginia Beach", "Norfolk", "Chesapeake", "Newport News", "Hampton",
    "HRBT", "MMBT", "Downtown Tunnel",
    "Naval Station Norfolk", "Langley AFB", "Fort Eustis",
    "local events", "traffic", "weather", "Hampton Roads"
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
            logger.warning("XAI API key not configured, skipping trends")
            return None

        try:
            response = self.client.chat.completions.create(
                model="grok-3-fast",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a local trends analyst. Always respond with valid JSON only, no markdown."
                    },
                    {
                        "role": "user",
                        "content": TRENDS_PROMPT.format(focus_areas=", ".join(FOCUS_AREAS))
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )

            content = response.choices[0].message.content

            # Clean up response if it has markdown code blocks
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
            content = content.strip()

            # Parse JSON from response
            result = json.loads(content)
            result['query_used'] = ", ".join(FOCUS_AREAS[:5])
            result['search_timestamp'] = datetime.now().isoformat()

            # Track usage
            usage = {
                'input_tokens': response.usage.prompt_tokens if response.usage else 0,
                'output_tokens': response.usage.completion_tokens if response.usage else 0,
                'model': 'grok-3-fast'
            }
            result['_usage'] = usage

            logger.info(f"Fetched {len(result.get('items', []))} trends")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Grok response as JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching trends: {e}")
            return None


trends_service = TrendsService()
