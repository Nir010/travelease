"""
TravelEase - Accounts App Views
views.py - User authentication, registration, OTP verification

Handles:
- User Registration (with OTP email verification)
- User Login / Logout
- OTP sending and verification
- User Profile display/update
- Booking History for logged-in users
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import UserProfile, OTPVerification
from booking.models import Booking
import datetime


# =============================================
# USER REGISTRATION VIEW
# =============================================
def register_view(request):
    """
    User Registration with OTP Email Verification.

    FLOW:
    1. User fills registration form (username, email, password, confirm password)
    2. Account is created BUT marked as email_verified=False
    3. OTP is generated and sent to user's email
    4. User is redirected to OTP verification page
    5. User enters OTP → account is verified → auto-login

    WHY OTP? Prevents fake accounts, verifies email ownership
    """
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        phone = request.POST.get('phone', '').strip()

        # --- VALIDATION ---
        errors = []

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            errors.append('Username already taken.')
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            errors.append('Email already registered.')
        # Check passwords match
        if password != password2:
            errors.append('Passwords do not match.')
        # Check password length
        if len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        # Check username length
        if len(username) < 3:
            errors.append('Username must be at least 3 characters.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'accounts/register.html', {
                'username': username, 'email': email, 'phone': phone
            })

        # --- CREATE USER ---
        # Django's create_user() automatically hashes the password
        # NEVER store plain-text passwords - this is crucial for security
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=request.POST.get('first_name', '').strip(),
            last_name=request.POST.get('last_name', '').strip(),
        )

        # Create UserProfile (extended info)
        UserProfile.objects.create(
            user=user,
            phone_number=phone,
            email_verified=False,
        )

        # --- GENERATE OTP ---
        otp = OTPVerification.generate_otp(
            user=user,
            expiry_minutes=getattr(settings, 'OTP_EXPIRY_MINUTES', 10)
        )

        # --- SEND OTP EMAIL ---
        try:
            send_mail(
                subject='TravelEase - Email Verification OTP',
                message=f'Your OTP for TravelEase registration is: {otp.otp_code}\n\n'
                        f'This OTP expires in {settings.OTP_EXPIRY_MINUTES} minutes.\n\n'
                        f'Thank you for choosing TravelEase!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception:
            pass  # Console backend or SMTP failure — OTP shown on-page below

        messages.success(request, f'Account created! Please verify your email to continue.')
        # Show OTP directly on the verification page so demo users don't need real email
        messages.info(request, f'Your verification OTP is: {otp.otp_code}')

        # Store user ID in session so OTP page knows which user to verify
        request.session['pending_verification_user_id'] = user.id
        return redirect('accounts:verify_otp')

    return render(request, 'accounts/register.html')


# =============================================
# OTP VERIFICATION VIEW
# =============================================
def verify_otp_view(request):
    """
    OTP Verification Page.

    User enters the 6-digit OTP sent to their email.
    If valid: marks email as verified, auto-logs in user.
    If invalid/expired: shows error, allows resend.
    """
    # Get the user ID from session
    user_id = request.session.get('pending_verification_user_id')
    if not user_id:
        messages.warning(request, 'No pending verification found. Please register first.')
        return redirect('accounts:register')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'Invalid verification session. Please register again.')
        return redirect('accounts:register')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp', '').strip()

        # Find the latest unused OTP for this user
        try:
            otp_record = OTPVerification.objects.filter(
                user=user, is_used=False
            ).latest('created_at')
        except OTPVerification.DoesNotExist:
            messages.error(request, 'No OTP found. Please request a new one.')
            return redirect('accounts:verify_otp')

        # Check if OTP matches and is still valid
        if otp_record.otp_code == entered_otp and otp_record.is_valid():
            # OTP is correct → verify the user
            otp_record.is_used = True
            otp_record.save()

            # Mark profile as email verified
            user.profile.email_verified = True
            user.profile.save()

            # Auto-login the user (no need to re-enter credentials after verification)
            login(request, user)

            # Clear the session
            del request.session['pending_verification_user_id']

            messages.success(request, 'Email verified successfully! Welcome to TravelEase!')
            return redirect('booking:home')
        else:
            if not otp_record.is_valid():
                messages.error(request, 'OTP has expired. Please request a new one.')
            else:
                messages.error(request, 'Invalid OTP. Please try again.')

    return render(request, 'accounts/verify_otp.html', {'email': user.email})


# =============================================
# RESEND OTP VIEW
# =============================================
def resend_otp_view(request):
    """
    Resend OTP to user's email.
    Invalidates previous OTP, creates new one, sends email.
    """
    user_id = request.session.get('pending_verification_user_id')
    if not user_id:
        messages.warning(request, 'No pending verification found.')
        return redirect('accounts:register')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('accounts:register')

    # Generate new OTP (old ones get invalidated in generate_otp)
    otp = OTPVerification.generate_otp(
        user=user,
        expiry_minutes=getattr(settings, 'OTP_EXPIRY_MINUTES', 10)
    )

    # Send email
    send_mail(
        subject='TravelEase - New Email Verification OTP',
        message=f'Your new OTP for TravelEase is: {otp.otp_code}\n\n'
                f'This OTP expires in {settings.OTP_EXPIRY_MINUTES} minutes.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

    messages.success(request, f'New OTP sent to {user.email}.')
    return redirect('accounts:verify_otp')


# =============================================
# LOGIN VIEW
# =============================================
def login_view(request):
    """
    User Login.

    Uses Django's built-in authenticate() and login().
    authenticate() checks username + password against the database.
    Django stores passwords as hashes - NEVER as plain text.
    The password entered is hashed and compared to stored hash.
    """
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # authenticate() returns User object if credentials match, None otherwise
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # login() creates the session for this user
            login(request, user)

            # Check if there's a 'next' parameter (redirect after login)
            next_url = request.GET.get('next', '')
            if next_url:
                return redirect(next_url)

            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('booking:home')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')


# =============================================
# LOGOUT VIEW
# =============================================
def logout_view(request):
    """
    User Logout.
    Django's logout() clears the session, removing all session data.
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('booking:home')


# =============================================
# USER PROFILE / DASHBOARD VIEW
# =============================================
@login_required
def profile_view(request):
    """
    User Dashboard / Profile Page.

    Shows:
    - User profile information
    - Booking history (all bookings by this user)
    - Quick stats (total bookings, upcoming trips)

    @login_required decorator ensures only logged-in users can access this.
    If not logged in, redirects to LOGIN_URL (accounts:login).
    """
    # Get user's bookings, ordered by most recent first
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')

    # Count active (confirmed/pending) bookings
    active_bookings = bookings.filter(status__in=['CONFIRMED', 'PENDING']).count()
    completed_bookings = bookings.filter(status='COMPLETED').count()
    cancelled_bookings = bookings.filter(status='CANCELLED').count()

    context = {
        'bookings': bookings[:20],  # Show latest 20 bookings
        'total_bookings': bookings.count(),
        'active_bookings': active_bookings,
        'completed_bookings': completed_bookings,
        'cancelled_bookings': cancelled_bookings,
    }
    return render(request, 'accounts/profile.html', context)


# =============================================
# EDIT PROFILE VIEW
# =============================================
@login_required
def edit_profile_view(request):
    """
    Edit User Profile.
    Allows updating phone, address, date of birth, avatar.

    Uses get_or_create to ensure a UserProfile always exists.
    This handles the case where the admin superuser (created via
    createsuperuser) doesn't have a UserProfile yet.
    """
    profile, _created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'email_verified': request.user.is_staff}
    )

    if request.method == 'POST':
        profile.phone_number = request.POST.get('phone', '').strip()
        profile.address = request.POST.get('address', '').strip()

        dob_str = request.POST.get('date_of_birth', '')
        if dob_str:
            try:
                profile.date_of_birth = datetime.datetime.strptime(dob_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        # Handle avatar upload
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']

        profile.save()

        # Update User model fields
        request.user.first_name = request.POST.get('first_name', '').strip()
        request.user.last_name = request.POST.get('last_name', '').strip()
        request.user.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts:profile')

    return render(request, 'accounts/edit_profile.html')
