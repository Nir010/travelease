"""
TravelEase - Booking App URLs
urls.py - URL routing for the booking app

URL PATTERNS:
/ → Homepage
/search/buses/ → Bus search results
/search/flights/ → Flight search results
/bus/<id>/ → Bus detail page
/flight/<id>/ → Flight detail page
/book/ → Create booking (POST only)
/booking/<id>/ → Booking detail
/booking/<id>/confirm/ → Booking confirmation
/booking/<id>/cancel/ → Cancel booking
/buses/ → All buses list
/flights/ → All flights list
/api/seats/<type>/<id>/ → AJAX seat availability
"""

from django.urls import path
from . import views

# app_name is required for namespaced URL reversing
# Example: {% url 'booking:home' %} → '/'
app_name = 'booking'

urlpatterns = [
    # Homepage
    path('', views.home, name='home'),

    # Search
    path('search/buses/', views.search_buses, name='search_buses'),
    path('search/flights/', views.search_flights, name='search_flights'),

    # Bus routes
    path('bus/<int:bus_id>/', views.bus_detail, name='bus_detail'),
    path('buses/', views.all_buses, name='all_buses'),

    # Flight routes
    path('flight/<int:flight_id>/', views.flight_detail, name='flight_detail'),
    path('flights/', views.all_flights, name='all_flights'),

    # Booking
    path('book/', views.book_ticket, name='book_ticket'),
    path('booking/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('booking/<int:booking_id>/confirm/', views.booking_confirmation, name='booking_confirmation'),
    path('booking/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),

    # API
    path('api/seats/<str:transport_type>/<int:transport_id>/', views.get_available_seats, name='get_seats'),
]