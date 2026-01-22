"""
CMS URL Configuration

All CMS routes for content management.
"""

from django.urls import path

from cms.views import (
    # Dashboard
    DashboardView, HelpView,
    # Cities
    CityListView, CityDetailView, CityUpdateView,
    # Venues
    VenueCreateView, VenueUpdateView, VenueDeleteView,
    VenueTogglePublishView, VenueReorderView,
    # Military
    MilitaryListView, MilitaryBaseCreateView,
    MilitaryBaseUpdateView, MilitaryBaseDeleteView,
    # Tunnels
    TunnelListView, TunnelCreateView, TunnelUpdateView, TunnelDeleteView,
    # Vacation Destinations
    DestinationListView, DestinationCreateView,
    DestinationUpdateView, DestinationDeleteView,
    # Testimonials
    TestimonialListView, TestimonialCreateView,
    TestimonialUpdateView, TestimonialDeleteView,
    # Team Members
    TeamMemberListView, TeamMemberCreateView,
    TeamMemberUpdateView, TeamMemberDeleteView,
    # Settings
    SettingsView, ToggleAPIView, UpdateAPISettingsView,
    SyncVenuesView, RefreshVenueView, SyncCityVenuesView,
    # Drive Destinations
    DriveDestinationListView, DriveDestinationCreateView,
    DriveDestinationUpdateView, DriveDestinationDeleteView,
)
from cms.views.content import (
    VendorListView, VendorCreateView, VendorUpdateView, VendorDeleteView,
)
from cms.views.ai_settings import (
    AICostReportView, AIModelManagerView, update_operation_ajax,
)
from cms.views.pulse_dashboard import (
    PulseDashboardView, api_pulse_refresh, api_timer_action,
    api_timer_status, api_pulse_stats,
)

app_name = 'cms'

urlpatterns = [
    # Dashboard
    path('', DashboardView.as_view(), name='dashboard'),
    path('help/', HelpView.as_view(), name='help'),
    path('settings/', SettingsView.as_view(), name='settings'),

    # API Settings
    path('settings/api/<str:provider>/toggle/', ToggleAPIView.as_view(), name='api_toggle'),
    path('settings/api/<str:provider>/update/', UpdateAPISettingsView.as_view(), name='api_settings'),
    path('settings/sync/', SyncVenuesView.as_view(), name='sync_venues'),

    # Venue Enrichment
    path('venues/<int:pk>/refresh/', RefreshVenueView.as_view(), name='venue_refresh'),
    path('cities/<slug:slug>/sync/<str:venue_type>/', SyncCityVenuesView.as_view(), name='city_sync_venues'),

    # Cities
    path('cities/', CityListView.as_view(), name='city_list'),
    path('cities/<slug:slug>/', CityDetailView.as_view(), name='city_detail'),
    path('cities/<slug:slug>/edit/', CityUpdateView.as_view(), name='city_edit'),

    # Venues (nested under cities for create)
    path('cities/<slug:city_slug>/venues/add/<str:venue_type>/',
         VenueCreateView.as_view(), name='venue_create'),
    path('venues/<int:pk>/edit/', VenueUpdateView.as_view(), name='venue_edit'),
    path('venues/<int:pk>/delete/', VenueDeleteView.as_view(), name='venue_delete'),
    path('venues/<int:pk>/toggle/', VenueTogglePublishView.as_view(), name='venue_toggle_publish'),
    path('venues/reorder/', VenueReorderView.as_view(), name='venue_reorder'),

    # Military Bases
    path('military/', MilitaryListView.as_view(), name='military_list'),
    path('military/add/', MilitaryBaseCreateView.as_view(), name='military_create'),
    path('military/<slug:slug>/edit/', MilitaryBaseUpdateView.as_view(), name='military_edit'),
    path('military/<slug:slug>/delete/', MilitaryBaseDeleteView.as_view(), name='military_delete'),

    # Tunnels
    path('tunnels/', TunnelListView.as_view(), name='tunnel_list'),
    path('tunnels/add/', TunnelCreateView.as_view(), name='tunnel_create'),
    path('tunnels/<slug:slug>/edit/', TunnelUpdateView.as_view(), name='tunnel_edit'),
    path('tunnels/<slug:slug>/delete/', TunnelDeleteView.as_view(), name='tunnel_delete'),

    # Vacation Destinations
    path('vacation/', DestinationListView.as_view(), name='destination_list'),
    path('vacation/add/', DestinationCreateView.as_view(), name='destination_create'),
    path('vacation/<slug:slug>/edit/', DestinationUpdateView.as_view(), name='destination_edit'),
    path('vacation/<slug:slug>/delete/', DestinationDeleteView.as_view(), name='destination_delete'),

    # Vendors/Utilities
    path('vendors/', VendorListView.as_view(), name='vendor_list'),
    path('vendors/add/', VendorCreateView.as_view(), name='vendor_create'),
    path('vendors/<int:pk>/edit/', VendorUpdateView.as_view(), name='vendor_edit'),
    path('vendors/<int:pk>/delete/', VendorDeleteView.as_view(), name='vendor_delete'),

    # Testimonials
    path('testimonials/', TestimonialListView.as_view(), name='testimonial_list'),
    path('testimonials/add/', TestimonialCreateView.as_view(), name='testimonial_create'),
    path('testimonials/<int:pk>/edit/', TestimonialUpdateView.as_view(), name='testimonial_edit'),
    path('testimonials/<int:pk>/delete/', TestimonialDeleteView.as_view(), name='testimonial_delete'),

    # Team Members
    path('team/', TeamMemberListView.as_view(), name='team_list'),
    path('team/add/', TeamMemberCreateView.as_view(), name='team_create'),
    path('team/<int:pk>/edit/', TeamMemberUpdateView.as_view(), name='team_edit'),
    path('team/<int:pk>/delete/', TeamMemberDeleteView.as_view(), name='team_delete'),

    # Drive Destinations (Drive Time Calculator)
    path('drive-destinations/', DriveDestinationListView.as_view(), name='drive_destination_list'),
    path('drive-destinations/add/', DriveDestinationCreateView.as_view(), name='drive_destination_create'),
    path('drive-destinations/<slug:slug>/edit/', DriveDestinationUpdateView.as_view(), name='drive_destination_edit'),
    path('drive-destinations/<slug:slug>/delete/', DriveDestinationDeleteView.as_view(), name='drive_destination_delete'),

    # AI Services
    path('ai/costs/', AICostReportView.as_view(), name='ai_cost_report'),
    path('ai/models/', AIModelManagerView.as_view(), name='ai_model_manager'),
    path('ai/operation/<str:operation>/update/', update_operation_ajax, name='ai_update_operation'),

    # Pulse Dashboard
    path('pulse/', PulseDashboardView.as_view(), name='pulse_dashboard'),
    path('pulse/refresh/', api_pulse_refresh, name='pulse_refresh'),
    path('pulse/stats/', api_pulse_stats, name='pulse_stats'),
    path('pulse/timer/<str:timer_name>/<str:action>/', api_timer_action, name='pulse_timer_action'),
    path('pulse/timer/<str:timer_name>/status/', api_timer_status, name='pulse_timer_status'),
]
