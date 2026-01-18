"""
Views for the About Hampton Roads public website.
"""

from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from .models import (
    Region, City, Venue, MilitaryBase, Tunnel,
    VacationDestination, VendorUtility, Testimonial, TeamMember
)


class HomeView(TemplateView):
    """Homepage with overview and city cards."""
    template_name = 'guide/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['regions'] = Region.objects.prefetch_related('cities').all()
        context['cities'] = City.objects.select_related('region').filter(is_published=True)
        context['testimonials'] = Testimonial.objects.filter(is_published=True, is_featured=True)[:3]
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

        # Get venues by type
        context['restaurants'] = city.venues.filter(venue_type='restaurant', is_published=True)
        context['cafes'] = city.venues.filter(venue_type='cafe_brewery', is_published=True)
        context['attractions'] = city.venues.filter(venue_type='attraction', is_published=True)
        context['events'] = city.venues.filter(venue_type='event', is_published=True)
        context['beaches'] = city.venues.filter(venue_type='beach', is_published=True)

        # Get other cities for navigation
        context['other_cities'] = City.objects.select_related('region').filter(
            is_published=True
        ).exclude(pk=city.pk)

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
