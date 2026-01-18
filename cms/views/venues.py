"""
CMS Venue Views

CRUD operations for venues with HTMX support.
"""

import json
from django.views.generic import CreateView, UpdateView, DeleteView, View
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.template.loader import render_to_string

from guide.models import City, Venue
from .mixins import CMSAccessMixin
from cms.forms import VenueForm


class VenueCreateView(CMSAccessMixin, CreateView):
    """
    Create a new venue for a city.
    """
    model = Venue
    form_class = VenueForm
    template_name = 'cms/venues/form.html'

    def get_initial(self):
        initial = super().get_initial()
        # Pre-fill city and venue_type from URL
        city_slug = self.kwargs.get('city_slug')
        venue_type = self.kwargs.get('venue_type')

        if city_slug:
            initial['city'] = get_object_or_404(City, slug=city_slug)
        if venue_type:
            initial['venue_type'] = venue_type

        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['city'] = get_object_or_404(City, slug=self.kwargs.get('city_slug'))
        context['venue_type'] = self.kwargs.get('venue_type')
        context['is_create'] = True
        return context

    def form_valid(self, form):
        # Ensure city is set from URL
        city = get_object_or_404(City, slug=self.kwargs.get('city_slug'))
        form.instance.city = city

        venue_type = self.kwargs.get('venue_type')
        if venue_type:
            form.instance.venue_type = venue_type

        return super().form_valid(form)

    def get_success_url(self):
        city_slug = self.kwargs.get('city_slug')
        venue_type = self.object.venue_type
        tab = venue_type if venue_type != 'cafe_brewery' else 'cafes'
        return reverse_lazy('cms:city_detail', kwargs={'slug': city_slug}) + f'?tab={tab}'


class VenueUpdateView(CMSAccessMixin, UpdateView):
    """
    Update an existing venue.
    """
    model = Venue
    form_class = VenueForm
    template_name = 'cms/venues/form.html'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['city'] = self.object.city
        context['venue_type'] = self.object.venue_type
        context['is_create'] = False
        return context

    def get_success_url(self):
        venue = self.object
        tab_map = {
            'restaurant': 'restaurants',
            'cafe_brewery': 'cafes',
            'attraction': 'attractions',
            'event': 'events',
            'beach': 'beaches',
        }
        tab = tab_map.get(venue.venue_type, 'overview')
        return reverse_lazy('cms:city_detail', kwargs={'slug': venue.city.slug}) + f'?tab={tab}'


class VenueDeleteView(CMSAccessMixin, DeleteView):
    """
    Delete a venue.
    """
    model = Venue
    template_name = 'cms/venues/confirm_delete.html'
    pk_url_kwarg = 'pk'

    def get_success_url(self):
        venue = self.object
        tab_map = {
            'restaurant': 'restaurants',
            'cafe_brewery': 'cafes',
            'attraction': 'attractions',
            'event': 'events',
            'beach': 'beaches',
        }
        tab = tab_map.get(venue.venue_type, 'overview')
        return reverse_lazy('cms:city_detail', kwargs={'slug': venue.city.slug}) + f'?tab={tab}'


class VenueTogglePublishView(CMSAccessMixin, View):
    """
    HTMX endpoint to toggle venue publish status.
    """
    def post(self, request, pk):
        venue = get_object_or_404(Venue, pk=pk)
        venue.is_published = not venue.is_published
        venue.save(update_fields=['is_published', 'updated_at'])

        # Return updated toggle HTML
        html = render_to_string('cms/components/publish_toggle.html', {
            'obj': venue,
            'toggle_url': reverse_lazy('cms:venue_toggle_publish', kwargs={'pk': venue.pk})
        })
        return HttpResponse(html)


class VenueReorderView(CMSAccessMixin, View):
    """
    HTMX endpoint to reorder venues (drag and drop).
    """
    def post(self, request):
        try:
            data = json.loads(request.body)
            venue_ids = data.get('order', [])

            for index, venue_id in enumerate(venue_ids):
                Venue.objects.filter(pk=venue_id).update(order=index)

            return JsonResponse({'success': True})
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({'success': False, 'error': 'Invalid data'}, status=400)
