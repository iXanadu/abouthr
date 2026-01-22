"""
CMS Drive Destination Views

CRUD operations for drive time calculator destinations.
"""

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from guide.models import DriveDestination
from .mixins import CMSAccessMixin
from cms.forms import DriveDestinationForm


class DriveDestinationListView(CMSAccessMixin, ListView):
    """List all drive destinations grouped by category."""
    model = DriveDestination
    template_name = 'cms/drive_destinations/list.html'
    context_object_name = 'destinations'

    def get_queryset(self):
        return DriveDestination.objects.all().order_by('category', 'order', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Group destinations by category for display
        destinations_by_category = {}
        for dest in context['destinations']:
            category_display = dest.get_category_display()
            if category_display not in destinations_by_category:
                destinations_by_category[category_display] = []
            destinations_by_category[category_display].append(dest)
        context['destinations_by_category'] = destinations_by_category
        context['category_order'] = ['Military Base', 'Airport', 'Hospital', 'University', 'Beach']
        return context


class DriveDestinationCreateView(CMSAccessMixin, CreateView):
    """Create a new drive destination."""
    model = DriveDestination
    form_class = DriveDestinationForm
    template_name = 'cms/drive_destinations/form.html'
    success_url = reverse_lazy('cms:drive_destination_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = True
        return context


class DriveDestinationUpdateView(CMSAccessMixin, UpdateView):
    """Update an existing drive destination."""
    model = DriveDestination
    form_class = DriveDestinationForm
    template_name = 'cms/drive_destinations/form.html'
    success_url = reverse_lazy('cms:drive_destination_list')
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = False
        return context


class DriveDestinationDeleteView(CMSAccessMixin, DeleteView):
    """Delete a drive destination."""
    model = DriveDestination
    template_name = 'cms/drive_destinations/confirm_delete.html'
    success_url = reverse_lazy('cms:drive_destination_list')
    slug_url_kwarg = 'slug'
