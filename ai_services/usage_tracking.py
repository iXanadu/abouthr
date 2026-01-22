"""
AI Usage Tracking Utility

Provides easy-to-use functions for logging AI API usage across all services.
Usage tracking enables cost analysis, financial modeling, and usage monitoring.
"""
import logging
import time
from typing import Optional, Any

logger = logging.getLogger(__name__)


def log_ai_usage(
    task_type: str,
    provider: str,
    model: str,
    response_time_ms: int,
    input_tokens: int = None,
    output_tokens: int = None,
    total_tokens: int = None,
    user=None,
    success: bool = True,
    error_message: str = "",
    metadata: dict = None
):
    """
    Log an AI API call to the AIUsageLog model.

    Args:
        task_type: One of the operation types (e.g., 'content_venue_description')
        provider: Provider name ('anthropic', 'xai', 'openai')
        model: Model name (e.g., 'claude-haiku-4-5-20251001')
        response_time_ms: Time taken for API call in milliseconds
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        total_tokens: Total tokens (if input/output not available separately)
        user: User who triggered the call (optional)
        success: Whether the call succeeded
        error_message: Error message if failed
        metadata: Additional context dict (venue_id, city_id, etc.)

    Returns:
        AIUsageLog instance or None if logging failed
    """
    # Don't fail the main operation if logging fails
    try:
        from ai_services.models import AIUsageLog

        return AIUsageLog.log_usage(
            task_type=task_type,
            provider=provider,
            model=model,
            response_time_ms=response_time_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            user=user,
            success=success,
            error_message=error_message,
            metadata=metadata
        )
    except Exception as e:
        # Log but don't raise - usage tracking should never break main functionality
        logger.warning(f"Failed to log AI usage: {e}")
        return None


def log_ai_error(
    task_type: str,
    provider: str,
    model: str,
    error: Exception,
    response_time_ms: int,
    user=None,
    metadata: dict = None
):
    """
    Log a failed AI API call.

    Convenience wrapper for log_ai_usage with success=False.
    """
    return log_ai_usage(
        task_type=task_type,
        provider=provider,
        model=model,
        response_time_ms=response_time_ms,
        user=user,
        metadata=metadata,
        success=False,
        error_message=str(error)
    )


class AIUsageTimer:
    """
    Context manager for timing AI API calls and logging usage.

    Usage:
        from ai_services.usage_tracking import AIUsageTimer

        with AIUsageTimer('content_venue_description', 'anthropic', 'claude-haiku-4-5-20251001') as timer:
            response = client.messages.create(...)
            timer.set_response(response)

    For Anthropic responses, set the response object to extract token counts.
    """

    def __init__(
        self,
        task_type: str,
        provider: str,
        model: str,
        user=None,
        metadata: dict = None
    ):
        self.task_type = task_type
        self.provider = provider
        self.model = model
        self.user = user
        self.metadata = metadata or {}

        self.start_time = None
        self.response = None
        self.error = None
        self.input_tokens = None
        self.output_tokens = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def set_response(self, response):
        """Set the API response for token counting"""
        self.response = response
        # Extract tokens from response object
        if response and hasattr(response, 'usage'):
            usage = response.usage
            if hasattr(usage, 'input_tokens'):
                self.input_tokens = usage.input_tokens
            if hasattr(usage, 'output_tokens'):
                self.output_tokens = usage.output_tokens

    def set_tokens(self, input_tokens: int, output_tokens: int):
        """Manually set token counts"""
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens

    def set_error(self, error: Exception):
        """Set error if the call failed"""
        self.error = error

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed_ms = int((time.time() - self.start_time) * 1000)

        if exc_val:
            # Exception occurred
            log_ai_error(
                task_type=self.task_type,
                provider=self.provider,
                model=self.model,
                error=exc_val,
                response_time_ms=elapsed_ms,
                user=self.user,
                metadata=self.metadata
            )
        elif self.error:
            # Error was set manually
            log_ai_error(
                task_type=self.task_type,
                provider=self.provider,
                model=self.model,
                error=self.error,
                response_time_ms=elapsed_ms,
                user=self.user,
                metadata=self.metadata
            )
        else:
            # Success
            log_ai_usage(
                task_type=self.task_type,
                provider=self.provider,
                model=self.model,
                response_time_ms=elapsed_ms,
                input_tokens=self.input_tokens,
                output_tokens=self.output_tokens,
                user=self.user,
                metadata=self.metadata,
                success=True
            )

        # Don't suppress exceptions
        return False


def get_usage_summary(days: int = 30) -> dict:
    """
    Get a summary of AI usage for the last N days.

    Returns:
        Dict with total_cost, total_calls, by_task_type, by_provider
    """
    from django.utils import timezone
    from django.db.models import Sum, Count
    from datetime import timedelta
    from decimal import Decimal

    try:
        from ai_services.models import AIUsageLog

        start_date = timezone.now() - timedelta(days=days)
        usage_qs = AIUsageLog.objects.filter(created_at__gte=start_date)

        # Summary stats
        summary = usage_qs.aggregate(
            total_cost=Sum('cost_usd'),
            total_calls=Count('id'),
            total_tokens=Sum('total_tokens'),
        )

        # By task type
        by_task = list(
            usage_qs.values('task_type')
            .annotate(cost=Sum('cost_usd'), count=Count('id'))
            .order_by('-cost')
        )

        # By provider
        by_provider = list(
            usage_qs.values('provider')
            .annotate(cost=Sum('cost_usd'), count=Count('id'))
            .order_by('-cost')
        )

        return {
            'total_cost': float(summary['total_cost'] or Decimal('0')),
            'total_calls': summary['total_calls'] or 0,
            'total_tokens': summary['total_tokens'] or 0,
            'by_task_type': by_task,
            'by_provider': by_provider,
            'days': days,
        }

    except Exception as e:
        logger.error(f"Failed to get usage summary: {e}")
        return {
            'total_cost': 0,
            'total_calls': 0,
            'total_tokens': 0,
            'by_task_type': [],
            'by_provider': [],
            'days': days,
            'error': str(e),
        }
