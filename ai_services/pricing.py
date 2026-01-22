"""
Centralized AI Pricing Configuration

Single source of truth for all AI provider/model pricing.
Reads from providers.yaml and provides utilities for cost calculation.
"""
import os
import yaml
import logging
from decimal import Decimal
from typing import Dict
from functools import lru_cache

logger = logging.getLogger(__name__)

# Path to the config file
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config', 'providers.yaml')


@lru_cache(maxsize=1)
def _load_pricing_config() -> Dict:
    """Load pricing configuration from YAML file (cached)."""
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = yaml.safe_load(f)
            return config.get('pricing', {})
    except Exception as e:
        logger.error(f"Failed to load pricing config: {e}")
        return {}


def get_pricing(provider: str, model: str) -> Dict[str, float]:
    """
    Get pricing rates for a provider/model combination.

    Args:
        provider: Provider name ('openai', 'anthropic', 'xai')
        model: Model name (e.g., 'gpt-4o', 'claude-haiku-4-5-20251001')

    Returns:
        Dict with 'input' and 'output' rates per 1K tokens
    """
    pricing_config = _load_pricing_config()

    # Try exact match first
    provider_pricing = pricing_config.get(provider.lower(), {})
    if model in provider_pricing:
        return provider_pricing[model]

    # Try partial model match (e.g., 'gpt-4o-2024-05-13' matches 'gpt-4o')
    for known_model, rates in provider_pricing.items():
        if model.startswith(known_model) or known_model.startswith(model):
            logger.debug(f"Matched {model} to {known_model} for pricing")
            return rates

    # Fall back to default rates
    default_rates = pricing_config.get('default', {'input': 0.01, 'output': 0.03})
    logger.warning(f"No pricing found for {provider}/{model}, using defaults: {default_rates}")
    return default_rates


def calculate_cost(
    provider: str,
    model: str,
    input_tokens: int,
    output_tokens: int
) -> Decimal:
    """
    Calculate cost in USD from token counts.

    Args:
        provider: Provider name
        model: Model name
        input_tokens: Number of input/prompt tokens
        output_tokens: Number of output/completion tokens

    Returns:
        Cost in USD as Decimal
    """
    rates = get_pricing(provider, model)
    input_cost = (input_tokens / 1000) * rates['input']
    output_cost = (output_tokens / 1000) * rates['output']
    return Decimal(str(round(input_cost + output_cost, 6)))


def estimate_cost_from_total(
    provider: str,
    model: str,
    total_tokens: int,
    input_ratio: float = 0.7
) -> Decimal:
    """
    Estimate cost when only total tokens are known.

    Args:
        provider: Provider name
        model: Model name
        total_tokens: Total token count
        input_ratio: Assumed ratio of input to total (default 70%)

    Returns:
        Estimated cost in USD as Decimal
    """
    input_tokens = int(total_tokens * input_ratio)
    output_tokens = total_tokens - input_tokens
    return calculate_cost(provider, model, input_tokens, output_tokens)


def get_all_pricing() -> Dict:
    """Get the complete pricing configuration (for admin/display purposes)."""
    return _load_pricing_config()


def clear_pricing_cache():
    """Clear the cached pricing config (call after config file changes)."""
    _load_pricing_config.cache_clear()
