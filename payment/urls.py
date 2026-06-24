"""
TravelEase - Payment App URLs
urls.py - URL routing for dummy payment

URL PATTERNS:
/payment/<booking_id>/ → Payment page (choose method)
/payment/<booking_id>/process/ → Process payment (POST)
/payment/<booking_id>/failed/ → Payment failure page
"""

from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('<int:booking_id>/', views.make_payment, name='make_payment'),
    path('<int:booking_id>/process/', views.process_payment, name='process_payment'),
    path('<int:booking_id>/failed/', views.payment_failed, name='payment_failed'),
]