"""
CMS Content Views

CRUD operations for tunnels, vacation destinations, vendors, testimonials, and team members.
"""

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from guide.models import (
    Tunnel, VacationDestination, VendorUtility, Testimonial, TeamMember, City
)
from .mixins import CMSAccessMixin
from cms.forms import (
    TunnelForm, VacationDestinationForm, VendorUtilityForm,
    TestimonialForm, TeamMemberForm
)


# =============================================================================
# Tunnel Views
# =============================================================================

class TunnelListView(CMSAccessMixin, ListView):
    """List all tunnels."""
    model = Tunnel
    template_name = 'cms/tunnels/list.html'
    context_object_name = 'tunnels'

    def get_queryset(self):
        return Tunnel.objects.all().order_by('order', 'name')


class TunnelCreateView(CMSAccessMixin, CreateView):
    """Create a new tunnel."""
    model = Tunnel
    form_class = TunnelForm
    template_name = 'cms/tunnels/form.html'
    success_url = reverse_lazy('cms:tunnel_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = True
        return context


class TunnelUpdateView(CMSAccessMixin, UpdateView):
    """Update an existing tunnel."""
    model = Tunnel
    form_class = TunnelForm
    template_name = 'cms/tunnels/form.html'
    success_url = reverse_lazy('cms:tunnel_list')
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = False
        return context


class TunnelDeleteView(CMSAccessMixin, DeleteView):
    """Delete a tunnel."""
    model = Tunnel
    template_name = 'cms/tunnels/confirm_delete.html'
    success_url = reverse_lazy('cms:tunnel_list')
    slug_url_kwarg = 'slug'


# =============================================================================
# Vacation Destination Views
# =============================================================================

class DestinationListView(CMSAccessMixin, ListView):
    """List all vacation destinations."""
    model = VacationDestination
    template_name = 'cms/vacation/list.html'
    context_object_name = 'destinations'

    def get_queryset(self):
        return VacationDestination.objects.all().order_by('order', 'name')


class DestinationCreateView(CMSAccessMixin, CreateView):
    """Create a new vacation destination."""
    model = VacationDestination
    form_class = VacationDestinationForm
    template_name = 'cms/vacation/form.html'
    success_url = reverse_lazy('cms:destination_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = True
        return context


class DestinationUpdateView(CMSAccessMixin, UpdateView):
    """Update an existing vacation destination."""
    model = VacationDestination
    form_class = VacationDestinationForm
    template_name = 'cms/vacation/form.html'
    success_url = reverse_lazy('cms:destination_list')
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = False
        return context


class DestinationDeleteView(CMSAccessMixin, DeleteView):
    """Delete a vacation destination."""
    model = VacationDestination
    template_name = 'cms/vacation/confirm_delete.html'
    success_url = reverse_lazy('cms:destination_list')
    slug_url_kwarg = 'slug'


# =============================================================================
# Vendor Utility Views
# =============================================================================

class VendorListView(CMSAccessMixin, ListView):
    """List all vendor utilities grouped by city."""
    model = VendorUtility
    template_name = 'cms/vendors/list.html'
    context_object_name = 'vendors'

    def get_queryset(self):
        return VendorUtility.objects.select_related('city').order_by(
            'city__name', 'category', 'order', 'name'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Group vendors by city for display
        vendors_by_city = {}
        for vendor in context['vendors']:
            city_name = vendor.city.name
            if city_name not in vendors_by_city:
                vendors_by_city[city_name] = []
            vendors_by_city[city_name].append(vendor)
        context['vendors_by_city'] = vendors_by_city
        context['cities'] = City.objects.order_by('region__order', 'order', 'name')
        return context


class VendorCreateView(CMSAccessMixin, CreateView):
    """Create a new vendor utility."""
    model = VendorUtility
    form_class = VendorUtilityForm
    template_name = 'cms/vendors/form.html'
    success_url = reverse_lazy('cms:vendor_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = True
        return context

    def get_initial(self):
        initial = super().get_initial()
        # Pre-fill city from query param if provided
        city_slug = self.request.GET.get('city')
        if city_slug:
            try:
                initial['city'] = City.objects.get(slug=city_slug)
            except City.DoesNotExist:
                pass
        return initial


class VendorUpdateView(CMSAccessMixin, UpdateView):
    """Update an existing vendor utility."""
    model = VendorUtility
    form_class = VendorUtilityForm
    template_name = 'cms/vendors/form.html'
    success_url = reverse_lazy('cms:vendor_list')
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = False
        return context


class VendorDeleteView(CMSAccessMixin, DeleteView):
    """Delete a vendor utility."""
    model = VendorUtility
    template_name = 'cms/vendors/confirm_delete.html'
    success_url = reverse_lazy('cms:vendor_list')
    pk_url_kwarg = 'pk'


# =============================================================================
# Testimonial Views
# =============================================================================

class TestimonialListView(CMSAccessMixin, ListView):
    """List all testimonials."""
    model = Testimonial
    template_name = 'cms/testimonials/list.html'
    context_object_name = 'testimonials'

    def get_queryset(self):
        return Testimonial.objects.all().order_by('-is_featured', 'order', '-created_at')


class TestimonialCreateView(CMSAccessMixin, CreateView):
    """Create a new testimonial."""
    model = Testimonial
    form_class = TestimonialForm
    template_name = 'cms/testimonials/form.html'
    success_url = reverse_lazy('cms:testimonial_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = True
        return context


class TestimonialUpdateView(CMSAccessMixin, UpdateView):
    """Update an existing testimonial."""
    model = Testimonial
    form_class = TestimonialForm
    template_name = 'cms/testimonials/form.html'
    success_url = reverse_lazy('cms:testimonial_list')
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = False
        return context


class TestimonialDeleteView(CMSAccessMixin, DeleteView):
    """Delete a testimonial."""
    model = Testimonial
    template_name = 'cms/testimonials/confirm_delete.html'
    success_url = reverse_lazy('cms:testimonial_list')
    pk_url_kwarg = 'pk'


# =============================================================================
# Team Member Views
# =============================================================================

class TeamMemberListView(CMSAccessMixin, ListView):
    """List all team members."""
    model = TeamMember
    template_name = 'cms/team/list.html'
    context_object_name = 'team_members'

    def get_queryset(self):
        return TeamMember.objects.all().order_by('order', 'name')


class TeamMemberCreateView(CMSAccessMixin, CreateView):
    """Create a new team member."""
    model = TeamMember
    form_class = TeamMemberForm
    template_name = 'cms/team/form.html'
    success_url = reverse_lazy('cms:team_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = True
        return context


class TeamMemberUpdateView(CMSAccessMixin, UpdateView):
    """Update an existing team member."""
    model = TeamMember
    form_class = TeamMemberForm
    template_name = 'cms/team/form.html'
    success_url = reverse_lazy('cms:team_list')
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = False
        return context


class TeamMemberDeleteView(CMSAccessMixin, DeleteView):
    """Delete a team member."""
    model = TeamMember
    template_name = 'cms/team/confirm_delete.html'
    success_url = reverse_lazy('cms:team_list')
    pk_url_kwarg = 'pk'
