"""
CMS Settings Views

Configuration pages for API settings and venue enrichment.
"""

import logging
import os

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView, View

from guide.models import City, Venue, VenueAPIConfig
from guide.services import VenueEnrichmentService
from .mixins import CMSAccessMixin

logger = logging.getLogger(__name__)


class SettingsView(CMSAccessMixin, TemplateView):
    """
    CMS Settings page for API configuration.
    """
    template_name = 'cms/settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get or create Google config
        google_config, _ = VenueAPIConfig.objects.get_or_create(
            provider='google',
            defaults={
                'api_key_name': 'GOOGLE_PLACES_API_KEY',
            }
        )

        # Check if API key is configured
        api_key = os.environ.get(google_config.api_key_name, '')
        google_config.key_configured = bool(api_key)

        context['google_config'] = google_config

        # Get enrichment stats
        service = VenueEnrichmentService(provider='google')
        context['enrichment_stats'] = service.get_enrichment_stats()

        # Cities for sync dropdown
        context['cities'] = City.objects.filter(is_published=True).order_by('name')

        return context


class ToggleAPIView(CMSAccessMixin, View):
    """
    Toggle API provider enabled status.
    """

    def post(self, request, provider):
        config = VenueAPIConfig.objects.filter(provider=provider).first()
        if config:
            config.is_enabled = not config.is_enabled
            config.save()
            status = "enabled" if config.is_enabled else "disabled"
            messages.success(request, f"{config.get_provider_display()} API {status}.")
        else:
            messages.error(request, f"Configuration for '{provider}' not found.")

        return redirect('cms:settings')


class UpdateAPISettingsView(CMSAccessMixin, View):
    """
    Update API settings (quota, venues per city).
    """

    def post(self, request, provider):
        config = VenueAPIConfig.objects.filter(provider=provider).first()
        if not config:
            messages.error(request, f"Configuration for '{provider}' not found.")
            return redirect('cms:settings')

        try:
            daily_quota = int(request.POST.get('daily_quota', config.daily_quota))
            venues_per_city = int(request.POST.get('venues_per_city', config.venues_per_city))

            config.daily_quota = max(100, min(100000, daily_quota))
            config.venues_per_city = max(5, min(100, venues_per_city))
            config.save()

            messages.success(request, "Settings updated successfully.")
        except (ValueError, TypeError):
            messages.error(request, "Invalid values provided.")

        return redirect('cms:settings')


class SyncVenuesView(CMSAccessMixin, View):
    """
    Trigger venue sync for a single city.
    For bulk syncs, use: python manage.py enrich_venues --all
    """

    def post(self, request):
        city_slug = request.POST.get('city')
        discover = request.POST.get('discover') == 'on'
        provider = request.POST.get('provider', 'google')

        service = VenueEnrichmentService(provider=provider)

        if not service.is_enabled():
            messages.error(request, "API provider is not enabled or out of quota.")
            return redirect('cms:settings')

        # Require a specific city to avoid timeout on bulk operations
        if not city_slug:
            messages.warning(
                request,
                "Please select a specific city. For bulk sync of all cities, "
                "use the command line: python manage.py enrich_venues --all"
            )
            return redirect('cms:settings')

        city = City.objects.filter(slug=city_slug).first()
        if not city:
            messages.error(request, f"City not found: {city_slug}")
            return redirect('cms:settings')

        # Sync single city
        results = service.match_and_enrich_city(city)
        total_matched = results['matched']
        total_added = 0

        # Discover new if requested
        if discover:
            discover_results = service.discover_new_venues(
                city,
                limit=service.config.venues_per_city if service.config else 20
            )
            total_added = discover_results.get('added', 0)

        # Update last sync time
        if service.config:
            service.config.last_full_sync = timezone.now()
            service.config.save()

        msg = f"Sync complete for {city.name}: {total_matched} venues enriched"
        if discover:
            msg += f", {total_added} new venues discovered"
        messages.success(request, msg)

        return redirect('cms:settings')


class RefreshVenueView(CMSAccessMixin, View):
    """
    Refresh a single venue from the API.
    """

    def post(self, request, pk):
        try:
            venue = Venue.objects.get(pk=pk)
        except Venue.DoesNotExist:
            messages.error(request, "Venue not found.")
            return redirect('cms:city_list')

        service = VenueEnrichmentService(provider='google')

        if not service.is_enabled():
            messages.error(request, "API provider is not enabled or out of quota.")
            return redirect('cms:city_detail', slug=venue.city.slug)

        if venue.google_place_id:
            success, message = service.refresh_venue(venue)
        else:
            success, message = service.match_and_enrich_venue(venue)

        if success:
            messages.success(request, f"Venue '{venue.name}' refreshed successfully.")
        else:
            messages.warning(request, f"Could not refresh venue: {message}")

        # Redirect back to city detail
        return redirect(f"{reverse_lazy('cms:city_detail', kwargs={'slug': venue.city.slug})}?tab={self._get_tab_for_venue(venue)}")

    def _get_tab_for_venue(self, venue):
        """Get the appropriate tab name for the venue type."""
        tab_map = {
            'restaurant': 'restaurants',
            'cafe_brewery': 'cafes',
            'attraction': 'attractions',
            'event': 'events',
            'beach': 'beaches',
        }
        return tab_map.get(venue.venue_type, 'overview')


class SyncCityVenuesView(CMSAccessMixin, View):
    """
    Sync all venues of a type for a specific city.
    """

    def post(self, request, slug, venue_type):
        try:
            city = City.objects.get(slug=slug)
        except City.DoesNotExist:
            messages.error(request, "City not found.")
            return redirect('cms:city_list')

        service = VenueEnrichmentService(provider='google')

        if not service.is_enabled():
            messages.error(request, "API provider is not enabled or out of quota.")
            return redirect('cms:city_detail', slug=slug)

        # Match and enrich
        results = service.match_and_enrich_city(
            city,
            venue_types=[venue_type]
        )

        # Also discover if requested
        discover = request.POST.get('discover') == 'on'
        if discover:
            discover_results = service.discover_new_venues(
                city,
                venue_types=[venue_type],
                limit=service.config.venues_per_city if service.config else 20
            )
            messages.success(
                request,
                f"Synced {results['matched']} venues, discovered {discover_results.get('added', 0)} new."
            )
        else:
            messages.success(request, f"Synced {results['matched']} venues.")

        tab_map = {
            'restaurant': 'restaurants',
            'cafe_brewery': 'cafes',
        }
        tab = tab_map.get(venue_type, 'overview')

        return redirect(f"{reverse_lazy('cms:city_detail', kwargs={'slug': slug})}?tab={tab}")
