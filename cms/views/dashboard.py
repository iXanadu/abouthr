"""
CMS Dashboard View

Main landing page for the CMS with content statistics.
"""

from django.views.generic import TemplateView
from django.db.models import Count

from guide.models import (
    Region, City, Venue, MilitaryBase, Tunnel,
    VacationDestination, VendorUtility, Testimonial, TeamMember
)
from guide.services import VenueEnrichmentService
from .mixins import CMSAccessMixin


class DashboardView(CMSAccessMixin, TemplateView):
    """
    CMS Dashboard showing content statistics and quick actions.
    """
    template_name = 'cms/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Content counts
        context['stats'] = {
            'cities': City.objects.count(),
            'cities_published': City.objects.filter(is_published=True).count(),
            'venues': Venue.objects.count(),
            'venues_published': Venue.objects.filter(is_published=True).count(),
            'military_bases': MilitaryBase.objects.count(),
            'tunnels': Tunnel.objects.count(),
            'destinations': VacationDestination.objects.count(),
            'testimonials': Testimonial.objects.count(),
            'team_members': TeamMember.objects.count(),
        }

        # Venue breakdown by type
        context['venue_counts'] = Venue.objects.values('venue_type').annotate(
            count=Count('id')
        ).order_by('venue_type')

        # Recent updates
        context['recent_venues'] = Venue.objects.order_by('-updated_at')[:5]
        context['recent_testimonials'] = Testimonial.objects.order_by('-updated_at')[:3]

        # Cities with venue counts
        context['cities_summary'] = City.objects.annotate(
            venue_count=Count('venues')
        ).order_by('region__order', 'order')[:5]

        # Venue enrichment stats
        try:
            service = VenueEnrichmentService(provider='google')
            context['enrichment_stats'] = service.get_enrichment_stats()
        except Exception:
            context['enrichment_stats'] = None

        return context


class HelpView(CMSAccessMixin, TemplateView):
    """
    CMS Help page with content guidelines for managers.
    """
    template_name = 'cms/help.html'
