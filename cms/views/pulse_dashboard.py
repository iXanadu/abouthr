"""
CMS Views for Hampton Roads Pulse Management

Dashboard to view and control the Pulse content refresh system.
"""
import subprocess
import logging
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone

from .mixins import CMSAccessMixin
from guide.models import PulseContent
from guide.services.pulse_service import pulse_service

logger = logging.getLogger(__name__)

# Managed timers for this application
MANAGED_TIMERS = {
    'pulse-refresh': {
        'name': 'Hampton Roads Pulse',
        'description': 'Refreshes X trends and local news headlines for the homepage',
        'schedule_description': 'Every 4 hours (6 times daily)',
        'cost_estimate': '~$3-5/month',
        'command': 'python manage.py refresh_pulse',
    },
    'venue-refresh': {
        'name': 'Venue Data Refresh',
        'description': 'Updates venue ratings and hours from Google Places',
        'schedule_description': 'Weekly (Sundays at 3 AM)',
        'cost_estimate': '~$2/month',
        'command': 'python manage.py refresh_venues --days=7',
    },
}


def _run_systemctl(command, timer_name):
    """Run a systemctl command and return result."""
    try:
        result = subprocess.run(
            ['sudo', 'systemctl', command, f'{timer_name}.timer'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0, result.stderr or result.stdout
    except subprocess.TimeoutExpired:
        return False, 'Command timed out'
    except Exception as e:
        return False, str(e)


def _get_timer_status(timer_name):
    """Get the status of a systemd timer."""
    try:
        # Check if timer is active
        result = subprocess.run(
            ['systemctl', 'is-active', f'{timer_name}.timer'],
            capture_output=True,
            text=True,
            timeout=5
        )
        is_active = result.stdout.strip() == 'active'

        # Check if timer is enabled (will start on boot)
        result_enabled = subprocess.run(
            ['systemctl', 'is-enabled', f'{timer_name}.timer'],
            capture_output=True,
            text=True,
            timeout=5
        )
        is_enabled = result_enabled.stdout.strip() == 'enabled'

        # Get next run time
        next_run = None
        if is_active:
            result_list = subprocess.run(
                ['systemctl', 'list-timers', f'{timer_name}.timer', '--no-pager'],
                capture_output=True,
                text=True,
                timeout=5
            )
            # Parse output to get next run time
            lines = result_list.stdout.strip().split('\n')
            if len(lines) > 1:
                # Format: NEXT LEFT LAST PASSED UNIT ACTIVATES
                parts = lines[1].split()
                if len(parts) >= 2:
                    next_run = f"{parts[0]} {parts[1]}" if parts[0] != 'n/a' else None

        return {
            'is_active': is_active,
            'is_enabled': is_enabled,
            'next_run': next_run,
            'error': None,
        }
    except Exception as e:
        return {
            'is_active': False,
            'is_enabled': False,
            'next_run': None,
            'error': str(e),
        }


class PulseDashboardView(CMSAccessMixin, TemplateView):
    """
    Dashboard for managing Hampton Roads Pulse.

    Shows:
    - Current pulse content status
    - Timer status and controls
    - Cost statistics
    - Manual refresh button
    """
    template_name = 'cms/pulse/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get pulse statistics
        stats = pulse_service.get_stats()

        # Get current content for preview
        pulse_data = pulse_service.get_pulse_data(refresh_if_expired=False)

        # Build timer list with status
        timers = []
        for timer_name, timer_info in MANAGED_TIMERS.items():
            status = _get_timer_status(timer_name)
            timers.append({
                'id': timer_name,
                'name': timer_info['name'],
                'description': timer_info['description'],
                'schedule_description': timer_info['schedule_description'],
                'cost_estimate': timer_info['cost_estimate'],
                'command': timer_info['command'],
                **status,
            })

        # Get recent pulse content history
        recent_content = PulseContent.objects.order_by('-generated_at')[:10]

        context.update({
            'stats': stats,
            'pulse_data': pulse_data,
            'timers': timers,
            'recent_content': recent_content,
        })

        return context


@login_required
@require_POST
def api_pulse_refresh(request):
    """
    API endpoint to manually refresh pulse content.
    """
    content_type = request.POST.get('content_type')  # 'trends', 'headlines', or None for both

    try:
        if content_type and content_type in ['trends', 'headlines']:
            result = pulse_service.force_refresh(content_type)
        else:
            result = pulse_service.force_refresh()

        success_count = sum(1 for v in result.values() if v == 'success')
        fail_count = sum(1 for v in result.values() if v == 'failed')

        if fail_count == 0:
            return JsonResponse({
                'success': True,
                'message': f'Successfully refreshed {success_count} content type(s)',
                'result': result,
            })
        else:
            return JsonResponse({
                'success': True,
                'message': f'Refreshed with {fail_count} failure(s)',
                'result': result,
            })

    except Exception as e:
        logger.error(f"Error refreshing pulse: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


@login_required
@require_http_methods(["POST"])
def api_timer_action(request, timer_name, action):
    """
    API to start/stop/enable/disable a systemd timer.
    """
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)

    if timer_name not in MANAGED_TIMERS:
        return JsonResponse({'success': False, 'error': 'Unknown timer'}, status=404)

    if action not in ['start', 'stop', 'enable', 'disable']:
        return JsonResponse({'success': False, 'error': 'Invalid action'}, status=400)

    success, message = _run_systemctl(action, timer_name)

    if success:
        status = _get_timer_status(timer_name)
        return JsonResponse({
            'success': True,
            'message': f'Timer {action}ed successfully',
            'status': status,
        })
    else:
        return JsonResponse({
            'success': False,
            'error': f'Failed to {action} timer: {message}',
        }, status=500)


@login_required
def api_timer_status(request, timer_name):
    """
    API to get current timer status.
    """
    if timer_name not in MANAGED_TIMERS:
        return JsonResponse({'success': False, 'error': 'Unknown timer'}, status=404)

    status = _get_timer_status(timer_name)
    timer_info = MANAGED_TIMERS[timer_name]

    return JsonResponse({
        'success': True,
        'timer': {
            'id': timer_name,
            'name': timer_info['name'],
            **status,
        },
    })


@login_required
def api_pulse_stats(request):
    """
    API to get current pulse statistics.
    """
    stats = pulse_service.get_stats()

    return JsonResponse({
        'success': True,
        'stats': {
            'trends_active': stats['trends_active'],
            'trends_updated': stats['trends_updated'].isoformat() if stats['trends_updated'] else None,
            'headlines_active': stats['headlines_active'],
            'headlines_updated': stats['headlines_updated'].isoformat() if stats['headlines_updated'] else None,
            'month_cost': float(stats['month_cost']),
            'month_refreshes': stats['month_refreshes'],
        },
    })
