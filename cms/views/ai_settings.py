"""
CMS Views for AI Services Management

Provides cost reporting and model configuration UI.
"""
import os
import json
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .mixins import CMSAccessMixin
from ai_services.models import AIProvider, AIModel, AIOperationConfig, AIUsageLog


class AICostReportView(CMSAccessMixin, TemplateView):
    """
    AI Cost Report - Shows AI usage and costs.

    Displays:
    - Summary statistics (total cost, calls, tokens)
    - Cost breakdown by task type
    - Cost breakdown by provider
    - Daily cost trend
    - Recent usage log
    """
    template_name = 'cms/ai/cost_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get date range from query params (default: last 30 days)
        days = int(self.request.GET.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)

        usage_qs = AIUsageLog.objects.filter(created_at__gte=start_date)

        # Summary statistics
        summary = usage_qs.aggregate(
            total_cost=Sum('cost_usd'),
            total_calls=Count('id'),
            total_tokens=Sum('total_tokens'),
            avg_response_time=Avg('response_time_ms'),
        )

        # Handle None values
        summary['total_cost'] = summary['total_cost'] or Decimal('0')
        summary['total_calls'] = summary['total_calls'] or 0
        summary['total_tokens'] = summary['total_tokens'] or 0
        summary['avg_response_time'] = int(summary['avg_response_time'] or 0)

        # Calculate success rate
        if summary['total_calls'] > 0:
            success_count = usage_qs.filter(success=True).count()
            summary['success_rate'] = round((success_count / summary['total_calls']) * 100, 1)
        else:
            summary['success_rate'] = 100

        # Cost by task type
        cost_by_task = list(
            usage_qs.values('task_type')
            .annotate(
                cost=Sum('cost_usd'),
                count=Count('id'),
                tokens=Sum('total_tokens')
            )
            .order_by('-cost')
        )

        # Cost by provider
        cost_by_provider = list(
            usage_qs.values('provider')
            .annotate(
                cost=Sum('cost_usd'),
                count=Count('id'),
                tokens=Sum('total_tokens')
            )
            .order_by('-cost')
        )

        # Daily cost trend (for chart)
        daily_cost = list(
            usage_qs.annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(cost=Sum('cost_usd'), count=Count('id'))
            .order_by('date')
        )

        # Recent usage log (last 50 entries)
        recent_usage = usage_qs.select_related('user').order_by('-created_at')[:50]

        # Task type labels for display
        task_type_labels = dict(AIUsageLog.TASK_TYPE_CHOICES)

        context.update({
            'summary': summary,
            'cost_by_task': cost_by_task,
            'cost_by_provider': cost_by_provider,
            'daily_cost': daily_cost,
            'daily_cost_json': json.dumps([
                {'date': d['date'].isoformat(), 'cost': float(d['cost'] or 0)}
                for d in daily_cost
            ]),
            'recent_usage': recent_usage,
            'task_type_labels': task_type_labels,
            'days': days,
            'start_date': start_date,
        })

        return context


class AIModelManagerView(CMSAccessMixin, TemplateView):
    """
    AI Model Manager - Configure AI providers, models, and operations.

    Displays:
    - All providers with API key status
    - All models grouped by provider
    - Operation configurations with model assignments
    """
    template_name = 'cms/ai/model_manager.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get all providers with configuration status
        providers = []
        for provider in AIProvider.objects.all().order_by('display_name'):
            api_key_configured = bool(os.environ.get(provider.api_key_env_var, '')) if provider.api_key_env_var else False
            providers.append({
                'id': provider.id,
                'name': provider.name,
                'display_name': provider.display_name,
                'provider_type': provider.provider_type,
                'api_key_env_var': provider.api_key_env_var,
                'is_active': provider.is_active,
                'is_configured': api_key_configured,
                'model_count': provider.models.filter(is_active=True).count(),
            })

        # Get all models grouped by provider
        models_by_provider = {}
        for model in AIModel.objects.select_related('provider').filter(is_active=True).order_by('provider__display_name', 'display_name'):
            pname = model.provider.display_name
            if pname not in models_by_provider:
                models_by_provider[pname] = []
            models_by_provider[pname].append({
                'id': model.id,
                'model_id': model.model_id,
                'display_name': model.display_name,
                'capabilities': model.capabilities or [],
                'input_price': float(model.input_price_per_1k) if model.input_price_per_1k else None,
                'output_price': float(model.output_price_per_1k) if model.output_price_per_1k else None,
                'price_per_image': float(model.price_per_image) if model.price_per_image else None,
                'is_deprecated': model.is_deprecated,
            })

        # Get operation configs
        operations = []
        for config in AIOperationConfig.objects.select_related('model', 'model__provider', 'fallback_model').order_by('operation'):
            operations.append({
                'operation': config.operation,
                'display': config.get_operation_display(),
                'model_id': config.model.id,
                'model_display': config.model.display_name,
                'provider': config.model.provider.name,
                'provider_display': config.model.provider.display_name,
                'temperature': config.temperature,
                'max_tokens': config.max_tokens,
                'is_enabled': config.is_enabled,
                'fallback_model_id': config.fallback_model.id if config.fallback_model else None,
                'fallback_display': config.fallback_model.display_name if config.fallback_model else None,
            })

        # Group operations by category
        content_operations = [op for op in operations if op['operation'].startswith('content_')]
        research_operations = [op for op in operations if op['operation'].startswith('research_')]
        other_operations = [op for op in operations if not op['operation'].startswith('content_') and not op['operation'].startswith('research_')]

        # All active models for dropdown
        all_models = list(
            AIModel.objects.filter(is_active=True)
            .select_related('provider')
            .values('id', 'display_name', 'model_id', 'provider__name', 'provider__display_name')
            .order_by('provider__display_name', 'display_name')
        )

        context.update({
            'providers': providers,
            'models_by_provider': models_by_provider,
            'content_operations': content_operations,
            'research_operations': research_operations,
            'other_operations': other_operations,
            'all_models': all_models,
        })

        return context


from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

# Function-based view for AJAX update (simpler CSRF handling)
@login_required
@require_POST
def update_operation_ajax(request, operation):
    """API endpoint to update operation configuration via AJAX."""
    try:
        data = json.loads(request.body)
        config = AIOperationConfig.objects.get(operation=operation)

        # Update model if provided
        if 'model_id' in data:
            model = AIModel.objects.get(id=data['model_id'])
            config.model = model

        # Update optional fields
        if 'temperature' in data:
            config.temperature = data['temperature'] if data['temperature'] is not None else None
        if 'max_tokens' in data:
            config.max_tokens = data['max_tokens'] if data['max_tokens'] is not None else None
        if 'is_enabled' in data:
            config.is_enabled = data['is_enabled']
        if 'fallback_model_id' in data:
            if data['fallback_model_id']:
                config.fallback_model = AIModel.objects.get(id=data['fallback_model_id'])
            else:
                config.fallback_model = None

        config.updated_by = request.user
        config.save()

        return JsonResponse({
            'success': True,
            'message': f'Updated {config.get_operation_display()}',
            'model_display': config.model.display_name,
            'provider_display': config.model.provider.display_name,
        })
    except AIOperationConfig.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Operation not found'}, status=404)
    except AIModel.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Model not found'}, status=404)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# Keep class-based for backwards compatibility
class UpdateOperationView(CMSAccessMixin, View):
    """API endpoint to update operation configuration via AJAX."""

    def post(self, request, operation):
        return update_operation_ajax(request, operation)
