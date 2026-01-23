"""
Views for the About Hampton Roads public website.
"""

import requests
import logging
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from django.http import HttpResponse, Http404
from django.urls import reverse
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from .models import (
    Region, City, Venue, MilitaryBase, Tunnel,
    VacationDestination, VendorUtility, Testimonial, TeamMember,
    VenueAPIConfig
)

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    """Homepage with overview and city cards."""
    template_name = 'guide/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['regions'] = Region.objects.prefetch_related('cities').all()
        context['cities'] = City.objects.select_related('region').filter(is_published=True)
        context['testimonials'] = Testimonial.objects.filter(is_published=True, is_featured=True)[:3]

        # Add Hampton Roads Pulse
        from guide.services.pulse_service import pulse_service
        context['pulse'] = pulse_service.get_pulse_data()

        return context


class CityDetailView(DetailView):
    """Detailed view for a single city with all venues."""
    model = City
    template_name = 'guide/city_detail.html'
    context_object_name = 'city'

    def get_queryset(self):
        return City.objects.select_related('region').filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        city = self.object

        # Get venues by type, sorted by rating (highest first), then by name
        from django.db.models import F
        from django.db.models.functions import Coalesce

        def get_sorted_venues(venue_type):
            return city.venues.filter(
                venue_type=venue_type, is_published=True
            ).order_by(
                F('rating').desc(nulls_last=True),
                'name'
            )

        context['restaurants'] = get_sorted_venues('restaurant')
        context['cafes'] = get_sorted_venues('cafe_brewery')
        context['attractions'] = city.venues.filter(venue_type='attraction', is_published=True).order_by('order', 'name')
        context['events'] = city.venues.filter(venue_type='event', is_published=True).order_by('order', 'name')
        context['beaches'] = city.venues.filter(venue_type='beach', is_published=True).order_by('order', 'name')

        # Get other cities for navigation
        context['other_cities'] = City.objects.select_related('region').filter(
            is_published=True
        ).exclude(pk=city.pk)

        # Get weather for this city
        from guide.services import weather_service
        context['weather'] = weather_service.get_weather(city.slug)

        # Drive Time Calculator
        from guide.models import DriveDestination
        from django.conf import settings
        context['drive_destinations'] = DriveDestination.objects.filter(
            is_published=True
        ).order_by('category', 'order', 'name')
        context['google_maps_api_key'] = settings.GOOGLE_MAPS_API_KEY

        # Pre-fill from URL params (for shared links)
        context['drive_from'] = self.request.GET.get('from', '')
        context['drive_to'] = self.request.GET.get('to', '')
        context['drive_time'] = self.request.GET.get('time', 'now')

        return context


class MilitaryView(TemplateView):
    """Military relocation information and bases."""
    template_name = 'guide/military.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Group bases by branch
        context['navy_bases'] = MilitaryBase.objects.filter(branch='navy', is_published=True)
        context['army_bases'] = MilitaryBase.objects.filter(branch='army', is_published=True)
        context['air_force_bases'] = MilitaryBase.objects.filter(branch='air_force', is_published=True)
        context['coast_guard_bases'] = MilitaryBase.objects.filter(branch='coast_guard', is_published=True)
        context['marine_bases'] = MilitaryBase.objects.filter(branch='marines', is_published=True)

        return context


class TunnelsView(ListView):
    """Hampton Roads tunnel systems."""
    model = Tunnel
    template_name = 'guide/tunnels.html'
    context_object_name = 'tunnels'

    def get_queryset(self):
        return Tunnel.objects.filter(is_published=True)


class VacationView(ListView):
    """Nearby vacation destinations."""
    model = VacationDestination
    template_name = 'guide/vacation.html'
    context_object_name = 'destinations'

    def get_queryset(self):
        return VacationDestination.objects.filter(is_published=True)


class UtilitiesView(TemplateView):
    """Vendors and utilities by city."""
    template_name = 'guide/utilities.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get all cities with their utilities
        cities = City.objects.prefetch_related('vendor_utilities').filter(is_published=True)
        context['cities'] = cities

        return context


class TestimonialsView(ListView):
    """Client testimonials."""
    model = Testimonial
    template_name = 'guide/testimonials.html'
    context_object_name = 'testimonials'

    def get_queryset(self):
        return Testimonial.objects.filter(is_published=True)


class AboutView(TemplateView):
    """About page with team information."""
    template_name = 'guide/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['team_members'] = TeamMember.objects.filter(is_published=True)
        return context


class ContactView(TemplateView):
    """Contact page."""
    template_name = 'guide/contact.html'


class DriveCalculatorView(TemplateView):
    """Standalone Drive Time Calculator landing page for marketing campaigns."""
    template_name = 'guide/drive_calculator.html'

    def get_context_data(self, **kwargs):
        from guide.models import DriveDestination
        from django.conf import settings

        context = super().get_context_data(**kwargs)
        context['drive_destinations'] = DriveDestination.objects.filter(
            is_published=True
        ).order_by('category', 'order', 'name')
        context['google_maps_api_key'] = settings.GOOGLE_MAPS_API_KEY

        # Pre-fill from URL params (for shared links)
        context['drive_from'] = self.request.GET.get('from', '')
        context['drive_to'] = self.request.GET.get('to', '')
        context['drive_time'] = self.request.GET.get('time', 'now')

        return context


def sitemap_xml(request):
    """Generate sitemap.xml dynamically."""
    base_url = 'https://abouthamptonroads.com'

    urls = [
        {'loc': base_url + '/', 'priority': '1.0', 'changefreq': 'weekly'},
        {'loc': base_url + '/drive-calculator/', 'priority': '0.9', 'changefreq': 'monthly'},
        {'loc': base_url + '/military/', 'priority': '0.8', 'changefreq': 'monthly'},
        {'loc': base_url + '/tunnels/', 'priority': '0.7', 'changefreq': 'monthly'},
        {'loc': base_url + '/vacation/', 'priority': '0.7', 'changefreq': 'monthly'},
        {'loc': base_url + '/utilities/', 'priority': '0.7', 'changefreq': 'monthly'},
        {'loc': base_url + '/testimonials/', 'priority': '0.6', 'changefreq': 'monthly'},
        {'loc': base_url + '/about/', 'priority': '0.6', 'changefreq': 'monthly'},
        {'loc': base_url + '/contact/', 'priority': '0.8', 'changefreq': 'monthly'},
    ]

    # Add city pages
    cities = City.objects.filter(is_published=True)
    for city in cities:
        urls.append({
            'loc': base_url + f'/city/{city.slug}/',
            'priority': '0.9',
            'changefreq': 'weekly'
        })

    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for url in urls:
        xml_content += '  <url>\n'
        xml_content += f'    <loc>{url["loc"]}</loc>\n'
        xml_content += f'    <changefreq>{url["changefreq"]}</changefreq>\n'
        xml_content += f'    <priority>{url["priority"]}</priority>\n'
        xml_content += '  </url>\n'

    xml_content += '</urlset>'

    return HttpResponse(xml_content, content_type='application/xml')


def robots_txt(request):
    """Generate robots.txt - blocks crawling on non-production environments."""
    from django.conf import settings

    environment = getattr(settings, 'ENVIRONMENT', 'production')

    if environment == 'production':
        content = """User-agent: *
Allow: /

Sitemap: https://abouthamptonroads.com/sitemap.xml
"""
    else:
        # Block all crawling on dev/local environments
        content = """User-agent: *
Disallow: /

# This is a development/staging environment - do not index
"""
    return HttpResponse(content, content_type='text/plain')


def venue_photo(request, venue_id, photo_index=0):
    """
    Proxy view to serve venue photos from Google Places.
    Caches photos for 24 hours to minimize API calls.
    """
    import os

    # Check cache first
    cache_key = f'venue_photo_{venue_id}_{photo_index}'
    cached_photo = cache.get(cache_key)
    if cached_photo:
        return HttpResponse(cached_photo['data'], content_type=cached_photo['content_type'])

    # Get venue
    try:
        venue = Venue.objects.get(pk=venue_id)
    except Venue.DoesNotExist:
        raise Http404("Venue not found")

    # Check for photos
    if not venue.photos_json or photo_index >= len(venue.photos_json):
        raise Http404("Photo not found")

    photo_ref = venue.photos_json[photo_index]
    photo_name = photo_ref.get('name')
    if not photo_name:
        raise Http404("Photo reference not found")

    # Get API key
    config = VenueAPIConfig.objects.filter(provider='google', is_enabled=True).first()
    if not config:
        raise Http404("API not configured")

    api_key = os.environ.get(config.api_key_name, '')
    if not api_key:
        raise Http404("API key not configured")

    # Fetch photo from Google
    max_width = request.GET.get('w', 400)
    try:
        max_width = min(int(max_width), 800)  # Cap at 800px
    except (ValueError, TypeError):
        max_width = 400

    photo_url = f"https://places.googleapis.com/v1/{photo_name}/media?maxWidthPx={max_width}&key={api_key}"

    try:
        response = requests.get(photo_url, timeout=10)
        response.raise_for_status()

        content_type = response.headers.get('Content-Type', 'image/jpeg')

        # Cache for 24 hours
        cache.set(cache_key, {
            'data': response.content,
            'content_type': content_type
        }, 60 * 60 * 24)

        return HttpResponse(response.content, content_type=content_type)

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching venue photo: {e}")
        raise Http404("Could not fetch photo")
