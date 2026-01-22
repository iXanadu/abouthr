"""
CMS Forms

ModelForms using crispy_forms for all guide content models.
"""

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit, HTML, Div

from guide.models import (
    City, Venue, MilitaryBase, Tunnel,
    VacationDestination, VendorUtility, Testimonial, TeamMember,
    DriveDestination
)


class CityForm(forms.ModelForm):
    """Form for editing city information."""

    class Meta:
        model = City
        fields = [
            'name', 'slug', 'region', 'description', 'image',
            'school_url', 'has_beaches', 'is_published', 'order'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Fieldset(
                'Basic Information',
                Row(
                    Column('name', css_class='col-md-6'),
                    Column('slug', css_class='col-md-6'),
                ),
                'region',
                'description',
            ),
            Fieldset(
                'Media & Links',
                'image',
                'school_url',
            ),
            Fieldset(
                'Settings',
                Row(
                    Column('has_beaches', css_class='col-md-4'),
                    Column('is_published', css_class='col-md-4'),
                    Column('order', css_class='col-md-4'),
                ),
            ),
            Div(
                Submit('submit', 'Save City', css_class='btn-primary'),
                HTML('<a href="{% url \'cms:city_list\' %}" class="btn btn-secondary ms-2">Cancel</a>'),
                css_class='mt-4'
            )
        )


class VenueForm(forms.ModelForm):
    """Form for creating/editing venues."""

    class Meta:
        model = Venue
        fields = [
            'name', 'venue_type', 'description', 'cuisine_type',
            'address', 'website', 'phone', 'image',
            'is_featured', 'is_published', 'order'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Fieldset(
                'Venue Details',
                Row(
                    Column('name', css_class='col-md-8'),
                    Column('venue_type', css_class='col-md-4'),
                ),
                'description',
                'cuisine_type',
            ),
            Fieldset(
                'Location & Contact',
                'address',
                Row(
                    Column('website', css_class='col-md-6'),
                    Column('phone', css_class='col-md-6'),
                ),
            ),
            Fieldset(
                'Media & Display',
                'image',
                Row(
                    Column('is_featured', css_class='col-md-4'),
                    Column('is_published', css_class='col-md-4'),
                    Column('order', css_class='col-md-4'),
                ),
            ),
            Div(
                Submit('submit', 'Save Venue', css_class='btn-primary'),
                HTML('<a href="{{ request.META.HTTP_REFERER|default:\'/cms/cities/\' }}" class="btn btn-secondary ms-2">Cancel</a>'),
                css_class='mt-4'
            )
        )


class MilitaryBaseForm(forms.ModelForm):
    """Form for creating/editing military bases."""

    class Meta:
        model = MilitaryBase
        fields = [
            'name', 'slug', 'branch', 'description', 'city',
            'website', 'image', 'is_published', 'order'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Fieldset(
                'Base Information',
                Row(
                    Column('name', css_class='col-md-6'),
                    Column('slug', css_class='col-md-6'),
                ),
                Row(
                    Column('branch', css_class='col-md-6'),
                    Column('city', css_class='col-md-6'),
                ),
                'description',
                'website',
            ),
            Fieldset(
                'Media & Display',
                'image',
                Row(
                    Column('is_published', css_class='col-md-6'),
                    Column('order', css_class='col-md-6'),
                ),
            ),
            Div(
                Submit('submit', 'Save Base', css_class='btn-primary'),
                HTML('<a href="{% url \'cms:military_list\' %}" class="btn btn-secondary ms-2">Cancel</a>'),
                css_class='mt-4'
            )
        )


class TunnelForm(forms.ModelForm):
    """Form for creating/editing tunnels."""

    class Meta:
        model = Tunnel
        fields = [
            'name', 'slug', 'description', 'connects_from', 'connects_to',
            'length_info', 'toll_info', 'image', 'is_published', 'order'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Fieldset(
                'Tunnel Information',
                Row(
                    Column('name', css_class='col-md-6'),
                    Column('slug', css_class='col-md-6'),
                ),
                'description',
            ),
            Fieldset(
                'Route Details',
                Row(
                    Column('connects_from', css_class='col-md-6'),
                    Column('connects_to', css_class='col-md-6'),
                ),
                Row(
                    Column('length_info', css_class='col-md-6'),
                    Column('toll_info', css_class='col-md-6'),
                ),
            ),
            Fieldset(
                'Media & Display',
                'image',
                Row(
                    Column('is_published', css_class='col-md-6'),
                    Column('order', css_class='col-md-6'),
                ),
            ),
            Div(
                Submit('submit', 'Save Tunnel', css_class='btn-primary'),
                HTML('<a href="{% url \'cms:tunnel_list\' %}" class="btn btn-secondary ms-2">Cancel</a>'),
                css_class='mt-4'
            )
        )


class VacationDestinationForm(forms.ModelForm):
    """Form for creating/editing vacation destinations."""

    class Meta:
        model = VacationDestination
        fields = [
            'name', 'slug', 'description', 'distance_description',
            'highlights', 'website', 'image', 'is_published', 'order'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'highlights': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Fieldset(
                'Destination Information',
                Row(
                    Column('name', css_class='col-md-6'),
                    Column('slug', css_class='col-md-6'),
                ),
                'description',
                'distance_description',
                'highlights',
                'website',
            ),
            Fieldset(
                'Media & Display',
                'image',
                Row(
                    Column('is_published', css_class='col-md-6'),
                    Column('order', css_class='col-md-6'),
                ),
            ),
            Div(
                Submit('submit', 'Save Destination', css_class='btn-primary'),
                HTML('<a href="{% url \'cms:destination_list\' %}" class="btn btn-secondary ms-2">Cancel</a>'),
                css_class='mt-4'
            )
        )


class VendorUtilityForm(forms.ModelForm):
    """Form for creating/editing vendor utilities."""

    class Meta:
        model = VendorUtility
        fields = [
            'city', 'category', 'name', 'phone', 'website',
            'notes', 'is_published', 'order'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Vendor Information',
                Row(
                    Column('city', css_class='col-md-6'),
                    Column('category', css_class='col-md-6'),
                ),
                'name',
                Row(
                    Column('phone', css_class='col-md-6'),
                    Column('website', css_class='col-md-6'),
                ),
                'notes',
            ),
            Fieldset(
                'Settings',
                Row(
                    Column('is_published', css_class='col-md-6'),
                    Column('order', css_class='col-md-6'),
                ),
            ),
            Div(
                Submit('submit', 'Save Vendor', css_class='btn-primary'),
                HTML('<a href="{% url \'cms:vendor_list\' %}" class="btn btn-secondary ms-2">Cancel</a>'),
                css_class='mt-4'
            )
        )


class TestimonialForm(forms.ModelForm):
    """Form for creating/editing testimonials."""

    class Meta:
        model = Testimonial
        fields = [
            'client_name', 'quote', 'client_location', 'photo',
            'is_featured', 'is_published', 'order'
        ]
        widgets = {
            'quote': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Fieldset(
                'Testimonial Details',
                'client_name',
                'quote',
                'client_location',
            ),
            Fieldset(
                'Media & Display',
                'photo',
                Row(
                    Column('is_featured', css_class='col-md-4'),
                    Column('is_published', css_class='col-md-4'),
                    Column('order', css_class='col-md-4'),
                ),
            ),
            Div(
                Submit('submit', 'Save Testimonial', css_class='btn-primary'),
                HTML('<a href="{% url \'cms:testimonial_list\' %}" class="btn btn-secondary ms-2">Cancel</a>'),
                css_class='mt-4'
            )
        )


class TeamMemberForm(forms.ModelForm):
    """Form for creating/editing team members."""

    class Meta:
        model = TeamMember
        fields = [
            'name', 'title', 'bio', 'photo',
            'email', 'phone', 'linkedin_url',
            'is_published', 'order'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Fieldset(
                'Personal Information',
                Row(
                    Column('name', css_class='col-md-6'),
                    Column('title', css_class='col-md-6'),
                ),
                'bio',
            ),
            Fieldset(
                'Contact Information',
                Row(
                    Column('email', css_class='col-md-6'),
                    Column('phone', css_class='col-md-6'),
                ),
                'linkedin_url',
            ),
            Fieldset(
                'Media & Display',
                'photo',
                Row(
                    Column('is_published', css_class='col-md-6'),
                    Column('order', css_class='col-md-6'),
                ),
            ),
            Div(
                Submit('submit', 'Save Team Member', css_class='btn-primary'),
                HTML('<a href="{% url \'cms:team_list\' %}" class="btn btn-secondary ms-2">Cancel</a>'),
                css_class='mt-4'
            )
        )


class DriveDestinationForm(forms.ModelForm):
    """Form for creating/editing drive time calculator destinations."""

    class Meta:
        model = DriveDestination
        fields = [
            'name', 'slug', 'category', 'address',
            'latitude', 'longitude', 'is_published', 'order'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Destination Information',
                Row(
                    Column('name', css_class='col-md-6'),
                    Column('slug', css_class='col-md-6'),
                ),
                'category',
                'address',
            ),
            Fieldset(
                'Coordinates',
                Row(
                    Column('latitude', css_class='col-md-6'),
                    Column('longitude', css_class='col-md-6'),
                ),
                HTML('<small class="text-muted">Tip: Find coordinates on <a href="https://www.google.com/maps" target="_blank">Google Maps</a> by right-clicking a location.</small>'),
            ),
            Fieldset(
                'Settings',
                Row(
                    Column('is_published', css_class='col-md-6'),
                    Column('order', css_class='col-md-6'),
                ),
            ),
            Div(
                Submit('submit', 'Save Destination', css_class='btn-primary'),
                HTML('<a href="{% url \'cms:drive_destination_list\' %}" class="btn btn-secondary ms-2">Cancel</a>'),
                css_class='mt-4'
            )
        )
