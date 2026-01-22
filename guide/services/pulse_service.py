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

logger = logging.getLogger(__name__)

# Pricing per 1M tokens
PRICING = {
    'grok-3-fast': {'input': 5.00, 'output': 25.00},
    'claude-haiku-4-5-20251001': {'input': 1.00, 'output': 5.00},
}

# Cache durations
CACHE_HOURS = {
    'trends': 4,
    'headlines': 6,
}


class PulseService:
    """
    Orchestrates the Hampton Roads Pulse feature.

    Handles:
    - Fetching fresh content when cache expires
    - Cost tracking and logging
    - Graceful degradation on API failures
    """

    def get_pulse_data(self, refresh_if_expired: bool = False) -> dict:
        """
        Get current pulse data for display.

        Args:
            refresh_if_expired: If True, fetch fresh data when cache expires.
                              If False (default), only return cached data.
                              Page loads should use False to stay fast.
                              Management commands use True.

        Returns:
            dict with trends and headlines (may have empty sections)
            Always returns content if available, even if stale.
        """
        if refresh_if_expired:
            trends = self._get_or_refresh('trends')
            headlines = self._get_or_refresh('headlines')
        else:
            # Only return cached data - don't block page loads
            # include_stale=True ensures we always show something
            trends = PulseContent.get_current('trends', include_stale=True)
            headlines = PulseContent.get_current('headlines', include_stale=True)

        return {
            'trends': trends.content_json if trends else {'items': []},
            'trends_updated': trends.generated_at if trends else None,
            'trends_stale': trends.is_stale if trends else False,
            'headlines': headlines.content_json if headlines else {'items': []},
            'headlines_updated': headlines.generated_at if headlines else None,
            'headlines_stale': headlines.is_stale if headlines else False,
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
                try:
                    from ai_services.models import AIUsageLog
                    AIUsageLog.objects.create(
                        task_type='research_happenings' if content_type == 'trends' else 'research_events',
                        provider='xai' if 'grok' in model else 'anthropic',
                        model=model,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        total_tokens=input_tokens + output_tokens,
                        cost_usd=cost,
                        response_time_ms=0,  # Not tracked for background refreshes
                        success=True,
                        metadata={'content_type': content_type, 'source': 'pulse'}
                    )
                except Exception as e:
                    logger.warning(f"Failed to log AI usage: {e}")

        logger.info(f"Created new {content_type} content, cost: ${cost:.6f}")
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

    def get_stats(self) -> dict:
        """Get pulse statistics for dashboard display."""
        from django.db.models import Sum, Count

        # Get current content status
        trends = PulseContent.get_current('trends')
        headlines = PulseContent.get_current('headlines')

        # Get cost stats for this month
        from datetime import date
        first_of_month = date.today().replace(day=1)
        month_stats = PulseContent.objects.filter(
            generated_at__date__gte=first_of_month
        ).aggregate(
            total_cost=Sum('cost_usd'),
            total_refreshes=Count('id'),
            total_tokens=Sum('tokens_used')
        )

        return {
            'trends_active': trends is not None,
            'trends_updated': trends.generated_at if trends else None,
            'trends_expires': trends.expires_at if trends else None,
            'headlines_active': headlines is not None,
            'headlines_updated': headlines.generated_at if headlines else None,
            'headlines_expires': headlines.expires_at if headlines else None,
            'month_cost': month_stats['total_cost'] or Decimal('0'),
            'month_refreshes': month_stats['total_refreshes'] or 0,
            'month_tokens': month_stats['total_tokens'] or 0,
        }


pulse_service = PulseService()
