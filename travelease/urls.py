"""
TravelEase - Main URL Configuration
urls.py - Master URL router

This file defines ALL URL patterns for the entire project.
It acts as a central dispatcher:
- /admin/ → Django admin panel
- / → booking app (homepage, search, booking, tickets)
- /accounts/ → accounts app (register, login, OTP, profile)
- /payment/ → payment app (dummy Khalti/eSewa)
- /media/ → serves uploaded files (bus/flight photos)

The include() function delegates URL matching to each app's urls.py
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django Admin Panel (/admin/)
    path('admin/', admin.site.urls),

    # Booking App (/)
    path('', include('booking.urls')),

    # Accounts App (/accounts/)
    path('accounts/', include('accounts.urls')),

    # Payment App (/payment/)
    path('payment/', include('payment.urls')),

    # django-allauth social auth (/auth/)
    # Google login will be at /auth/google/login/
    path('auth/', include('allauth.urls')),
]

# In DEBUG mode, Django serves media files directly
# This is for development ONLY - in production, use nginx/Apache
# MEDIA_URL = '/media/', MEDIA_ROOT = 'media/' folder
# This allows images uploaded for buses/flights to be displayed
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
