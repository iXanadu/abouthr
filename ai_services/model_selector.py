"""
Central AI Model Selection Service

Provides a single function to get the configured model for any operation.
Supports fallback chain: global config -> hardcoded default.

Usage:
    from ai_services.model_selector import get_model_config, get_model_for_operation

    # Get full configuration
    config = get_model_config('content_venue_description')
    client = Anthropic(api_key=...)
    response = client.messages.create(
        model=config.model_id,
        temperature=config.temperature or 0.7,
        max_tokens=config.max_tokens or 500,
        ...
    )

    # Or just get the model ID
    model_id = get_model_for_operation('content_venue_description')
"""

import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """Configuration for an AI model operation"""
    provider: str
    model_id: str
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    fallback_model_id: Optional[str] = None
    fallback_provider: Optional[str] = None

    def __repr__(self):
        return f"ModelConfig({self.provider}/{self.model_id})"


# =============================================================================
# Hardcoded Defaults for About Hampton Roads
# =============================================================================
# These are used as fallback when database config doesn't exist.
# This ensures services work even before seed_ai_models is run.

HARDCODED_DEFAULTS: dict[str, ModelConfig] = {
    # Content Generation - Claude Haiku (cheap, fast, good enough for descriptions)
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

    # Future operations
    'search_venues': ModelConfig(
        provider='anthropic',
        model_id='claude-haiku-4-5-20251001',
        temperature=0.3,
        max_tokens=1000
    ),
    'general_assistant': ModelConfig(
        provider='anthropic',
        model_id='claude-sonnet-4-20250514',
        temperature=0.7,
        max_tokens=2000
    ),
}


# =============================================================================
# Main Functions
# =============================================================================

def get_model_config(operation: str) -> ModelConfig:
    """
    Get the configured model for an AI operation.

    Fallback chain:
    1. Global AIOperationConfig from database
    2. Hardcoded defaults (HARDCODED_DEFAULTS)

    Args:
        operation: Operation identifier (e.g., 'content_venue_description',
                   'research_events')

    Returns:
        ModelConfig with provider, model_id, and optional parameters

    Raises:
        ValueError: If operation is unknown and no default exists

    Example:
        config = get_model_config('content_venue_description')
        # Returns ModelConfig(provider='anthropic', model_id='claude-haiku-4-5-20251001', ...)
    """
    # Try database config first
    try:
        from .models import AIOperationConfig

        config = AIOperationConfig.objects.select_related(
            'model', 'model__provider', 'fallback_model', 'fallback_model__provider'
        ).get(operation=operation, is_enabled=True)

        fallback_model_id = None
        fallback_provider = None
        if config.fallback_model:
            fallback_model_id = config.fallback_model.model_id
            fallback_provider = config.fallback_model.provider.name

        logger.debug(
            f"Using DB config for {operation}: {config.model.model_id}"
        )

        return ModelConfig(
            provider=config.model.provider.name,
            model_id=config.model.model_id,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            fallback_model_id=fallback_model_id,
            fallback_provider=fallback_provider,
        )

    except Exception as e:
        # Log but don't fail - fall back to hardcoded
        logger.debug(f"Using hardcoded default for {operation}: {e}")

    # Fall back to hardcoded defaults
    if operation in HARDCODED_DEFAULTS:
        return HARDCODED_DEFAULTS[operation]

    # Unknown operation - raise error
    valid_operations = list(HARDCODED_DEFAULTS.keys())
    raise ValueError(
        f"Unknown AI operation: '{operation}'. "
        f"Valid operations: {valid_operations}. "
        f"Configure in admin or add to HARDCODED_DEFAULTS."
    )


def get_model_for_operation(operation: str) -> str:
    """
    Convenience function to get just the model ID for an operation.

    Args:
        operation: Operation identifier

    Returns:
        Model ID string (e.g., 'claude-haiku-4-5-20251001')

    Example:
        model_id = get_model_for_operation('content_venue_description')
        # Returns 'claude-haiku-4-5-20251001'
    """
    config = get_model_config(operation)
    return config.model_id


def get_provider_for_operation(operation: str) -> str:
    """
    Convenience function to get just the provider name for an operation.

    Args:
        operation: Operation identifier

    Returns:
        Provider name string (e.g., 'anthropic', 'xai')

    Example:
        provider = get_provider_for_operation('content_venue_description')
        # Returns 'anthropic'
    """
    config = get_model_config(operation)
    return config.provider


def list_operations() -> list[str]:
    """
    List all valid operation identifiers.

    Returns:
        List of operation strings that can be passed to get_model_config()
    """
    return list(HARDCODED_DEFAULTS.keys())


def get_all_configs() -> dict[str, ModelConfig]:
    """
    Get configurations for all operations.

    Useful for debugging or displaying current configuration.

    Returns:
        Dict mapping operation names to their ModelConfig
    """
    return {op: get_model_config(op) for op in HARDCODED_DEFAULTS.keys()}
