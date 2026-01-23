"""
URL configuration for the About Hampton Roads guide app.
"""

from django.urls import path
from . import views

app_name = 'guide'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('city/<slug:slug>/', views.CityDetailView.as_view(), name='city_detail'),
    path('military/', views.MilitaryView.as_view(), name='military'),
    path('tunnels/', views.TunnelsView.as_view(), name='tunnels'),
    path('vacation/', views.VacationView.as_view(), name='vacation'),
    path('utilities/', views.UtilitiesView.as_view(), name='utilities'),
    path('testimonials/', views.TestimonialsView.as_view(), name='testimonials'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('drive-calculator/', views.DriveCalculatorView.as_view(), name='drive_calculator'),
    # Venue photos
    path('venue/<int:venue_id>/photo/', views.venue_photo, name='venue_photo'),
    path('venue/<int:venue_id>/photo/<int:photo_index>/', views.venue_photo, name='venue_photo_index'),
    # SEO
    path('sitemap.xml', views.sitemap_xml, name='sitemap'),
    path('robots.txt', views.robots_txt, name='robots'),
]
