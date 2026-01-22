"""
AI Services Admin Configuration

Provides Django admin interface for managing AI providers, models, and usage tracking.
"""
from django.contrib import admin
from django.utils.html import format_html
import os

from .models import AIProvider, AIModel, AIOperationConfig, AIUsageLog


@admin.register(AIProvider)
class AIProviderAdmin(admin.ModelAdmin):
    """Admin for AI Providers (OpenAI, Anthropic, xAI, etc.)"""

    list_display = [
        'display_name', 'name', 'provider_type',
        'api_key_status', 'model_count', 'is_active'
    ]
    list_filter = ['provider_type', 'is_active']
    search_fields = ['name', 'display_name']
    readonly_fields = ['created_at', 'updated_at', 'api_key_status_detail']

    fieldsets = (
        ('Provider Information', {
            'fields': ('name', 'display_name', 'provider_type')
        }),
        ('API Configuration', {
            'fields': ('api_key_env_var', 'base_url', 'api_key_status_detail'),
            'description': 'API keys are stored in environment variables for security.'
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def api_key_status(self, obj):
        """Display API key configuration status with color coding"""
        if obj.is_configured:
            return format_html(
                '<span style="color: green; font-weight: bold;">Configured</span>'
            )
        return format_html(
            '<span style="color: red;">Missing</span>'
        )
    api_key_status.short_description = "API Key"

    def api_key_status_detail(self, obj):
        """Detailed API key status for edit form"""
        if not obj.api_key_env_var:
            return "No environment variable configured"
        key = os.environ.get(obj.api_key_env_var, '')
        if key:
            # Show that key exists without exposing it
            masked = key[:8] + '...' + key[-4:] if len(key) > 12 else '***'
            return format_html(
                '<span style="color: green;">Found in ${} ({} chars): {}</span>',
                obj.api_key_env_var, len(key), masked
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">NOT FOUND: ${}</span>',
            obj.api_key_env_var
        )
    api_key_status_detail.short_description = "API Key Status"

    def model_count(self, obj):
        """Count of active models with link to filter"""
        count = obj.models.filter(is_active=True).count()
        total = obj.models.count()
        if count == total:
            return f"{count} models"
        return f"{count} active / {total} total"
    model_count.short_description = "Models"


@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    """Admin for AI Models with capabilities and pricing"""

    list_display = [
        'display_name', 'model_id', 'provider_link',
        'capabilities_display', 'pricing_display',
        'is_active', 'is_deprecated'
    ]
    list_filter = ['provider', 'is_active', 'is_deprecated']
    search_fields = ['model_id', 'display_name', 'provider__name', 'provider__display_name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['provider__display_name', 'display_name']
    list_select_related = ['provider']

    fieldsets = (
        ('Model Information', {
            'fields': ('provider', 'model_id', 'display_name')
        }),
        ('Capabilities', {
            'fields': ('capabilities',),
            'description': 'Enter as JSON list: ["text", "vision"]. Options: text, vision, image_gen, embedding, code, web_search'
        }),
        ('Pricing', {
            'fields': ('input_price_per_1k', 'output_price_per_1k', 'price_per_image'),
            'description': 'Prices in USD. Token models: per 1K tokens. Image models: per image.'
        }),
        ('Model Parameters', {
            'fields': ('max_tokens', 'context_window'),
        }),
        ('Status', {
            'fields': ('is_active', 'is_deprecated'),
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def provider_link(self, obj):
        """Provider name"""
        return obj.provider.display_name
    provider_link.short_description = "Provider"
    provider_link.admin_order_field = 'provider__display_name'

    def capabilities_display(self, obj):
        """Display capabilities as compact badges"""
        caps = obj.capabilities or []
        if not caps:
            return '-'
        icons = {
            'text': ('T', 'Text'),
            'vision': ('V', 'Vision'),
            'image_gen': ('I', 'Image Gen'),
            'embedding': ('E', 'Embedding'),
            'code': ('C', 'Code'),
            'web_search': ('W', 'Web Search')
        }
        badges = []
        for cap in caps:
            icon, title = icons.get(cap, (cap[0].upper(), cap))
            badges.append(f'<span title="{title}" style="background: #e0e0e0; padding: 2px 6px; border-radius: 3px; margin-right: 2px;">{icon}</span>')
        return format_html(''.join(badges))
    capabilities_display.short_description = "Caps"

    def pricing_display(self, obj):
        """Display pricing in compact format"""
        if obj.price_per_image:
            return f"${obj.price_per_image}/img"
        if obj.input_price_per_1k is not None and obj.output_price_per_1k is not None:
            return f"${obj.input_price_per_1k:.4f} / ${obj.output_price_per_1k:.4f}"
        return "-"
    pricing_display.short_description = "Price (in/out)"


@admin.register(AIOperationConfig)
class AIOperationConfigAdmin(admin.ModelAdmin):
    """Admin for AI Operation Configuration (global defaults)"""

    list_display = [
        'operation_display', 'model', 'provider_display',
        'temperature_display', 'max_tokens_display',
        'is_enabled', 'has_fallback', 'updated_at'
    ]
    list_filter = ['is_enabled', 'model__provider']
    search_fields = ['operation', 'model__display_name', 'model__model_id']
    readonly_fields = ['updated_at']
    list_select_related = ['model', 'model__provider', 'fallback_model']
    autocomplete_fields = ['model', 'fallback_model']

    fieldsets = (
        ('Operation Configuration', {
            'fields': ('operation', 'model', 'is_enabled'),
            'description': 'Configure which AI model to use for this operation.'
        }),
        ('Model Parameters Override', {
            'fields': ('temperature', 'max_tokens'),
            'description': 'Leave blank to use model defaults. Temperature: 0.0 (deterministic) to 2.0 (creative).',
            'classes': ('collapse',)
        }),
        ('Fallback Configuration', {
            'fields': ('fallback_model',),
            'description': 'Optional fallback model if the primary model fails.',
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('updated_at', 'updated_by'),
            'classes': ('collapse',)
        }),
    )

    def operation_display(self, obj):
        """Display operation with human-readable name"""
        return obj.get_operation_display()
    operation_display.short_description = "Operation"
    operation_display.admin_order_field = 'operation'

    def provider_display(self, obj):
        """Display provider name"""
        return obj.model.provider.display_name
    provider_display.short_description = "Provider"

    def temperature_display(self, obj):
        """Display temperature or default"""
        if obj.temperature is not None:
            return f"{obj.temperature:.1f}"
        return format_html('<span style="color: #888;">default</span>')
    temperature_display.short_description = "Temp"

    def max_tokens_display(self, obj):
        """Display max tokens or default"""
        if obj.max_tokens is not None:
            return str(obj.max_tokens)
        return format_html('<span style="color: #888;">default</span>')
    max_tokens_display.short_description = "Max Tokens"

    def has_fallback(self, obj):
        """Indicate if fallback is configured"""
        if obj.fallback_model:
            return format_html(
                '<span title="{}">Yes</span>',
                obj.fallback_model.display_name
            )
        return ""
    has_fallback.short_description = "Fallback"

    def save_model(self, request, obj, form, change):
        """Track who updated the configuration"""
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(AIUsageLog)
class AIUsageLogAdmin(admin.ModelAdmin):
    """Admin for AI Usage Logs - cost and usage tracking"""

    list_display = [
        'created_at', 'user', 'task_type', 'provider', 'model',
        'cost_display', 'tokens_display', 'success'
    ]
    list_filter = ['task_type', 'provider', 'success', 'created_at']
    search_fields = ['model', 'user__email']
    readonly_fields = [
        'user', 'task_type', 'provider', 'model',
        'input_tokens', 'output_tokens', 'total_tokens', 'cost_usd',
        'response_time_ms', 'success', 'error_message',
        'metadata', 'created_at'
    ]
    date_hierarchy = 'created_at'
    list_select_related = ['user']

    def cost_display(self, obj):
        """Format cost with color coding"""
        cost = obj.cost_usd
        if cost >= 0.10:
            color = 'red'
        elif cost >= 0.01:
            color = 'orange'
        else:
            color = 'green'
        return format_html(
            '<span style="color: {};">${:.4f}</span>',
            color, cost
        )
    cost_display.short_description = "Cost"
    cost_display.admin_order_field = 'cost_usd'

    def tokens_display(self, obj):
        """Display token counts"""
        if obj.input_tokens and obj.output_tokens:
            return f"{obj.input_tokens} / {obj.output_tokens}"
        if obj.total_tokens:
            return str(obj.total_tokens)
        return "-"
    tokens_display.short_description = "Tokens (in/out)"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
