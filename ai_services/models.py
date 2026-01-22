"""
AI Services Models for About Hampton Roads

Tracks AI usage, costs, and provides model configuration management.
"""
from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal
import os

User = get_user_model()


# =============================================================================
# AI Model Manager - Database-driven AI configuration
# =============================================================================

class AIProvider(models.Model):
    """
    AI Provider configuration (OpenAI, Anthropic, xAI, etc.)

    Global configuration - not account-scoped since providers are shared.
    API keys stay in environment variables for security.
    """
    PROVIDER_TYPES = [
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic'),
        ('xai', 'xAI'),
        ('blackforestlabs', 'Black Forest Labs'),
        ('google', 'Google AI'),
    ]

    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="Internal identifier (e.g., 'openai', 'anthropic')"
    )
    display_name = models.CharField(
        max_length=100,
        help_text="Human-readable name"
    )
    provider_type = models.CharField(
        max_length=50,
        choices=PROVIDER_TYPES,
        help_text="Provider type for SDK selection"
    )
    api_key_env_var = models.CharField(
        max_length=100,
        default='',
        blank=True,
        help_text="Environment variable name for API key (e.g., OPENAI_API_KEY)"
    )
    base_url = models.URLField(
        blank=True,
        help_text="Custom API base URL (leave blank for default)"
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this provider is available for use"
    )

    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "AI Provider"
        verbose_name_plural = "AI Providers"
        ordering = ['display_name']

    def __str__(self):
        return self.display_name

    @property
    def is_configured(self):
        """Check if API key is available in environment"""
        if self.api_key_env_var:
            return bool(os.environ.get(self.api_key_env_var))
        return False

    @property
    def active_model_count(self):
        """Count of active models for this provider"""
        return self.models.filter(is_active=True).count()


class AIModel(models.Model):
    """
    Specific AI model with capabilities and pricing.

    Pricing can be synced from providers.yaml or overridden manually.
    """
    CAPABILITY_CHOICES = [
        ('text', 'Text Generation'),
        ('vision', 'Vision/Image Analysis'),
        ('image_gen', 'Image Generation'),
        ('embedding', 'Embeddings'),
        ('code', 'Code Generation'),
        ('web_search', 'Web Search'),
    ]

    provider = models.ForeignKey(
        AIProvider,
        on_delete=models.CASCADE,
        related_name='models'
    )
    model_id = models.CharField(
        max_length=100,
        help_text="Model identifier for API calls (e.g., 'gpt-4o', 'claude-sonnet-4-20250514')"
    )
    display_name = models.CharField(
        max_length=150,
        help_text="Human-readable name for admin display"
    )

    # Capabilities (stored as JSON list)
    capabilities = models.JSONField(
        default=list,
        help_text="List of capabilities: text, vision, image_gen, embedding, code, web_search"
    )

    # Pricing (per 1K tokens, or per image for image_gen)
    input_price_per_1k = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Price per 1K input tokens (USD)"
    )
    output_price_per_1k = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Price per 1K output tokens (USD)"
    )
    price_per_image = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Price per image (for image generation models)"
    )

    # Model parameters
    max_tokens = models.IntegerField(
        default=4096,
        help_text="Maximum output tokens for this model"
    )
    context_window = models.IntegerField(
        null=True,
        blank=True,
        help_text="Maximum context window size"
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this model is available for use"
    )
    is_deprecated = models.BooleanField(
        default=False,
        help_text="Mark as deprecated (warn on use)"
    )

    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "AI Model"
        verbose_name_plural = "AI Models"
        unique_together = ['provider', 'model_id']
        ordering = ['provider', 'display_name']

    def __str__(self):
        return f"{self.provider.display_name} - {self.display_name}"

    def has_capability(self, capability: str) -> bool:
        """Check if model has a specific capability"""
        return capability in (self.capabilities or [])


class AIOperationConfig(models.Model):
    """
    Configure which model to use for each AI operation.

    Global defaults - defines what operations are available and their model assignments.
    """
    # About Hampton Roads specific operations
    OPERATION_CHOICES = [
        # Content Generation
        ('content_venue_description', 'Content: Venue Description'),
        ('content_city_description', 'Content: City Description'),
        ('content_refresh', 'Content: Refresh/Update'),
        # Web Research (with live search capabilities)
        ('research_events', 'Research: Event Discovery'),
        ('research_happenings', 'Research: Local Happenings'),
        ('research_fact_check', 'Research: Fact Checking'),
        # Future operations
        ('search_venues', 'Search: Venue Recommendations'),
        ('general_assistant', 'General: Assistant'),
    ]

    operation = models.CharField(
        max_length=50,
        choices=OPERATION_CHOICES,
        unique=True,
        primary_key=True,
        help_text="The AI operation to configure"
    )
    model = models.ForeignKey(
        AIModel,
        on_delete=models.PROTECT,
        related_name='operation_configs',
        help_text="Model to use for this operation"
    )

    # Optional model parameters override
    temperature = models.FloatField(
        null=True,
        blank=True,
        help_text="Override temperature (0.0-2.0). Leave blank for model default."
    )
    max_tokens = models.IntegerField(
        null=True,
        blank=True,
        help_text="Override max tokens. Leave blank for model default."
    )

    # Feature flags
    is_enabled = models.BooleanField(
        default=True,
        help_text="Whether this operation is enabled"
    )

    # Fallback configuration
    fallback_model = models.ForeignKey(
        AIModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fallback_for',
        help_text="Fallback model if primary fails"
    )

    # Metadata
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "AI Operation Config"
        verbose_name_plural = "AI Operation Configs"
        ordering = ['operation']

    def __str__(self):
        return f"{self.get_operation_display()} -> {self.model.display_name}"


# =============================================================================
# AI Usage Tracking
# =============================================================================


class AIUsageLog(models.Model):
    """
    Track ALL AI API calls for cost analysis and financial modeling.

    This model captures every AI API call made by the system, allowing:
    - Cost tracking
    - Task type analysis (which operations cost most)
    - Financial modeling for pricing decisions
    - Token usage patterns
    """

    # Task types match operation choices for consistency
    TASK_TYPE_CHOICES = AIOperationConfig.OPERATION_CHOICES + [
        ('other', 'Other'),
    ]

    PROVIDER_CHOICES = [
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic'),
        ('xai', 'xAI'),
        ('blackforestlabs', 'Black Forest Labs'),
        ('google', 'Google'),
    ]

    # User who triggered the API call (optional - some may be system calls)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_usage_logs'
    )

    # What type of AI operation
    task_type = models.CharField(
        max_length=50,
        choices=TASK_TYPE_CHOICES,
        db_index=True
    )

    # Provider and model info
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES)
    model = models.CharField(max_length=100)

    # Token counts (from API response)
    input_tokens = models.IntegerField(null=True, blank=True)
    output_tokens = models.IntegerField(null=True, blank=True)
    total_tokens = models.IntegerField(null=True, blank=True)

    # Cost calculation
    cost_usd = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        help_text="Calculated cost in USD"
    )

    # Performance metrics
    response_time_ms = models.IntegerField(help_text="API response time in milliseconds")

    # Success/failure tracking
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)

    # Context for debugging/analysis
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional context (venue_id, city_id, etc.)"
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['task_type', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]
        verbose_name = "AI Usage Log"
        verbose_name_plural = "AI Usage Logs"

    def __str__(self):
        return f"{self.task_type} - {self.model} - ${self.cost_usd:.4f}"

    @classmethod
    def get_pricing(cls, model: str, provider: str = 'openai') -> dict:
        """
        Get pricing per 1K tokens for a model.
        Returns {'input': rate, 'output': rate}
        """
        from .pricing import get_pricing
        return get_pricing(provider, model)

    @classmethod
    def calculate_cost(cls, model: str, input_tokens: int, output_tokens: int, provider: str = 'openai') -> Decimal:
        """Calculate cost in USD from token counts"""
        from .pricing import calculate_cost
        return calculate_cost(provider, model, input_tokens, output_tokens)

    @classmethod
    def log_usage(
        cls,
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
        Convenience method to log AI usage.
        Automatically calculates cost from token counts.
        """
        # Calculate cost using centralized pricing
        if input_tokens and output_tokens:
            cost = cls.calculate_cost(model, input_tokens, output_tokens, provider=provider)
        elif total_tokens:
            # Estimate 70/30 split if only total provided
            est_input = int(total_tokens * 0.7)
            est_output = int(total_tokens * 0.3)
            cost = cls.calculate_cost(model, est_input, est_output, provider=provider)
        else:
            cost = Decimal('0')

        return cls.objects.create(
            user=user,
            task_type=task_type,
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens or (input_tokens + output_tokens if input_tokens and output_tokens else None),
            cost_usd=cost,
            response_time_ms=response_time_ms,
            success=success,
            error_message=error_message,
            metadata=metadata or {}
        )
