"""
TravelEase - Accounts Admin
admin.py - Admin configuration for accounts models
"""

from django.contrib import admin
from .models import UserProfile, OTPVerification


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin view for user profiles"""
    list_display = ['user', 'phone_number', 'email_verified', 'created_at']
    list_filter = ['email_verified', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    """Admin view for OTP records"""
    list_display = ['user', 'otp_code', 'created_at', 'expires_at', 'is_used']
    list_filter = ['is_used', 'created_at']
    search_fields = ['user__email', 'otp_code']
    readonly_fields = ['created_at']
