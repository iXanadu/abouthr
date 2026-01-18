"""
Django Admin registration for Guide models.
Basic admin as backup for the CMS interface.
"""

from django.contrib import admin
from .models import (
    Region, City, Venue, MilitaryBase, Tunnel,
    VacationDestination, VendorUtility, Testimonial, TeamMember
)


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name', 'order']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'region', 'has_beaches', 'is_published', 'order']
    list_filter = ['region', 'is_published', 'has_beaches']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['region__order', 'order', 'name']


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'venue_type', 'is_featured', 'is_published', 'order']
    list_filter = ['venue_type', 'city', 'is_published', 'is_featured']
    search_fields = ['name', 'description']
    ordering = ['city', 'venue_type', 'order', 'name']


@admin.register(MilitaryBase)
class MilitaryBaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'branch', 'city', 'is_published', 'order']
    list_filter = ['branch', 'city', 'is_published']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']


@admin.register(Tunnel)
class TunnelAdmin(admin.ModelAdmin):
    list_display = ['name', 'connects_from', 'connects_to', 'is_published', 'order']
    list_filter = ['is_published']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']


@admin.register(VacationDestination)
class VacationDestinationAdmin(admin.ModelAdmin):
    list_display = ['name', 'distance_description', 'is_published', 'order']
    list_filter = ['is_published']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']


@admin.register(VendorUtility)
class VendorUtilityAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'category', 'is_published', 'order']
    list_filter = ['city', 'category', 'is_published']
    ordering = ['city', 'category', 'order', 'name']


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['client_name', 'is_featured', 'is_published', 'order']
    list_filter = ['is_featured', 'is_published']
    ordering = ['-is_featured', 'order', '-created_at']


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'title', 'is_published', 'order']
    list_filter = ['is_published']
    ordering = ['order', 'name']
