"""
CMS Military Views

CRUD operations for military bases.
"""

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from guide.models import MilitaryBase
from .mixins import CMSAccessMixin
from cms.forms import MilitaryBaseForm


class MilitaryListView(CMSAccessMixin, ListView):
    """
    List all military bases.
    """
    model = MilitaryBase
    template_name = 'cms/military/list.html'
    context_object_name = 'bases'

    def get_queryset(self):
        return MilitaryBase.objects.select_related('city').order_by('order', 'name')


class MilitaryBaseCreateView(CMSAccessMixin, CreateView):
    """
    Create a new military base.
    """
    model = MilitaryBase
    form_class = MilitaryBaseForm
    template_name = 'cms/military/form.html'
    success_url = reverse_lazy('cms:military_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = True
        return context


class MilitaryBaseUpdateView(CMSAccessMixin, UpdateView):
    """
    Update an existing military base.
    """
    model = MilitaryBase
    form_class = MilitaryBaseForm
    template_name = 'cms/military/form.html'
    success_url = reverse_lazy('cms:military_list')
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = False
        return context


class MilitaryBaseDeleteView(CMSAccessMixin, DeleteView):
    """
    Delete a military base.
    """
    model = MilitaryBase
    template_name = 'cms/military/confirm_delete.html'
    success_url = reverse_lazy('cms:military_list')
    slug_url_kwarg = 'slug'
