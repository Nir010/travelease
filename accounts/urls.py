"""
TravelEase - Accounts App URLs
urls.py - URL routing for user authentication

URL PATTERNS:
/accounts/register/ → Registration
/accounts/verify-otp/ → OTP verification
/accounts/resend-otp/ → Resend OTP
/accounts/login/ → Login
/accounts/logout/ → Logout
/accounts/profile/ → User dashboard
/accounts/profile/edit/ → Edit profile
"""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('resend-otp/', views.resend_otp_view, name='resend_otp'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
]