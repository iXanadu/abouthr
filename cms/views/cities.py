"""
CMS City Views

City list and detail views with venue management.
"""

from django.views.generic import ListView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.db.models import Count

from guide.models import City, Venue, Region, VendorUtility
from .mixins import CMSAccessMixin
from cms.forms import CityForm


class CityListView(CMSAccessMixin, ListView):
    """
    List all cities in a card grid layout.
    """
    model = City
    template_name = 'cms/cities/list.html'
    context_object_name = 'cities'

    def get_queryset(self):
        return City.objects.select_related('region').annotate(
            venue_count=Count('venues')
        ).order_by('region__order', 'order', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['regions'] = Region.objects.all().order_by('order')
        return context


class CityDetailView(CMSAccessMixin, DetailView):
    """
    City detail view with tabbed venue management.

    Tabs: Overview, Restaurants, Cafes, Attractions, Events, Beaches, Vendors
    """
    model = City
    template_name = 'cms/cities/detail.html'
    context_object_name = 'city'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return City.objects.select_related('region')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        city = self.object

        # Get active tab from query param, default to 'overview'
        context['active_tab'] = self.request.GET.get('tab', 'overview')

        # Venue counts by type for tab badges
        venue_counts = Venue.objects.filter(city=city).values('venue_type').annotate(
            count=Count('id')
        )
        context['venue_counts'] = {vc['venue_type']: vc['count'] for vc in venue_counts}

        # Venues by type
        context['restaurants'] = Venue.objects.filter(
            city=city, venue_type='restaurant'
        ).order_by('order', 'name')

        context['cafes'] = Venue.objects.filter(
            city=city, venue_type='cafe_brewery'
        ).order_by('order', 'name')

        context['attractions'] = Venue.objects.filter(
            city=city, venue_type='attraction'
        ).order_by('order', 'name')

        context['events'] = Venue.objects.filter(
            city=city, venue_type='event'
        ).order_by('order', 'name')

        context['beaches'] = Venue.objects.filter(
            city=city, venue_type='beach'
        ).order_by('order', 'name')

        # Vendor utilities
        context['vendors'] = VendorUtility.objects.filter(
            city=city
        ).order_by('category', 'order', 'name')

        # All venue types for dropdown
        context['venue_types'] = Venue.VENUE_TYPE_CHOICES

        return context


class CityUpdateView(CMSAccessMixin, UpdateView):
    """
    Update city information (overview tab).
    """
    model = City
    form_class = CityForm
    template_name = 'cms/cities/edit.html'
    slug_url_kwarg = 'slug'

    def get_success_url(self):
        return reverse_lazy('cms:city_detail', kwargs={'slug': self.object.slug})
