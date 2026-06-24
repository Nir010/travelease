"""
TravelEase - Accounts App Models
models.py - User profile and OTP verification models

TABLES:
1. UserProfile - Extended user data (phone, address, avatar)
2. OTPVerification - Stores OTP codes for email verification
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random


class UserProfile(models.Model):
    """
    UserProfile Model:
    - Extends Django's built-in User model (One-to-One relationship)
    - Stores additional user information not in the default User model
    - WHY separate model? Django's User model only has username, email, password, first_name, last_name
      We need phone number, address, profile picture, and email verification status
    """

    # OneToOneField = each User has EXACTLY ONE UserProfile
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='profile',
        help_text="Linked Django User account"
    )

    # Phone number (for booking contact)
    phone_number = models.CharField(max_length=15, blank=True)

    # Address (for passenger information)
    address = models.TextField(blank=True)

    # Date of birth
    date_of_birth = models.DateField(null=True, blank=True)

    # Profile picture (stored in media/profiles/)
    avatar = models.ImageField(upload_to='profiles/', blank=True, null=True)

    # Email verified flag (set to True after OTP verification)
    email_verified = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile: {self.user.username}"


class OTPVerification(models.Model):
    """
    OTPVerification Model:
    - Stores One-Time Passwords for email verification
    - Each OTP is linked to a User and expires after X minutes
    - Used during registration to verify user's email is real
    - WHY OTP? Prevents fake account creation, ensures email ownership
    """

    # USER: Who this OTP is for
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # OTP_CODE: 6-digit random number
    otp_code = models.CharField(max_length=6)

    # CREATED_AT: When OTP was generated
    created_at = models.DateTimeField(auto_now_add=True)

    # EXPIRES_AT: When OTP becomes invalid
    expires_at = models.DateTimeField()

    # IS_USED: Prevent OTP reuse
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"OTP for {self.user.email}: {self.otp_code}"

    def is_valid(self):
        """
        Check if OTP is still valid:
        - Not expired (current time < expires_at)
        - Not already used
        """
        return (timezone.now() <= self.expires_at) and not self.is_used

    @classmethod
    def generate_otp(cls, user, expiry_minutes=10):
        """
        Generate a new OTP for a user.
        - Creates a 6-digit random code
        - Sets expiry time based on settings
        - Marks any previous unused OTPs as used
        """
        # Invalidate all previous OTPs for this user
        cls.objects.filter(user=user, is_used=False).update(is_used=True)

        # Generate 6-digit random OTP
        otp_code = str(random.randint(100000, 999999))

        # Calculate expiry time
        expires_at = timezone.now() + timezone.timedelta(minutes=expiry_minutes)

        # Create and return the OTP record
        otp = cls.objects.create(
            user=user,
            otp_code=otp_code,
            expires_at=expires_at,
        )
        return otp
