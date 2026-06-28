"""
TravelEase - Online Bus & Flight Ticket Booking System
settings.py - Core Django configuration

This file contains ALL Django settings including:
- Database configuration (PostgreSQL)
- Installed apps
- Template and static file paths
- Email configuration (for OTP + booking confirmations)
- Authentication settings
- Media file handling (for bus/flight images)
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# BASE_DIR = the root folder of the project (TravelEase/)
# Every file path in Django is built relative to this
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
# This key is used for cryptographic signing (sessions, CSRF tokens, password resets)
SECRET_KEY = 'django-insecure-travelease-dev-key-change-in-production-2024'

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG=True shows detailed error pages during development
DEBUG = True

# ALLOWED_HOSTS lists which domains/IPs Django can serve
# '*' means any host can access this during development
ALLOWED_HOSTS = ['*']

# Trust Replit's proxy for CSRF
CSRF_TRUSTED_ORIGINS = [
    'https://*.replit.dev',
    'https://*.repl.co',
    'https://*.replit.app',
    'https://*.kirk.replit.dev',
]

# Ensure CSRF cookie works through proxy
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False


# =============================================
# APPLICATION DEFINITION
# =============================================
# INSTALLED_APPS tells Django which apps are active in the project
# Each app is a Python package that handles a specific feature
INSTALLED_APPS = [
    # Django built-in apps
    'django.contrib.admin',          # Admin dashboard (/admin)
    'django.contrib.auth',           # User authentication system
    'django.contrib.contenttypes',    # Content type framework
    'django.contrib.sessions',       # Session management
    'django.contrib.messages',       # Flash messages framework
    'django.contrib.staticfiles',    # Static file handling (CSS, JS, images)
    'django.contrib.sites',          # Required by django-allauth

    # django-allauth (Google OAuth)
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    # Custom apps
    'booking',    # Main booking app: buses, flights, search, booking, tickets
    'accounts',   # User accounts: register, login, OTP verification, profile
    'payment',    # Payment app: dummy Khalti/eSewa payment simulation
]

# MIDDLEWARE = a pipeline of hooks that process requests/responses
# Each middleware component runs in order on every request
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',          # Security headers
    'django.contrib.sessions.middleware.SessionMiddleware',   # Session support
    'django.middleware.common.CommonMiddleware',              # URL rewriting, etc.
    'django.middleware.csrf.CsrfViewMiddleware',              # CSRF protection
    'django.contrib.auth.middleware.AuthenticationMiddleware',# User authentication
    'django.contrib.messages.middleware.MessageMiddleware',   # Flash messages
    'django.middleware.clickjacking.XFrameOptionsMiddleware', # Clickjacking protection
    'allauth.account.middleware.AccountMiddleware',           # allauth session management
]

# ROOT_URLCONF points to the main URL routing file
ROOT_URLCONF = 'travelease.urls'


# =============================================
# TEMPLATE CONFIGURATION
# =============================================
# Templates are HTML files rendered by Django's template engine
# DIRS: additional directories where Django looks for templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Global templates folder
        'APP_DIRS': True,  # Also look inside each app's templates/ folder
        'OPTIONS': {
            'context_processors': [
                # These add variables to every template context automatically
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI = Web Server Gateway Interface - entry point for production servers
WSGI_APPLICATION = 'travelease.wsgi.application'


# =============================================
# DATABASE - PostgreSQL Configuration
# =============================================
# PostgreSQL handles:
# - Storing user credentials securely
# - Storing bus/flight schedule data (200+ records)
# - Storing booking records, payment records
# - Storing seat allocation data
# - Can handle BLOB data (bus photos as binary or file paths)
#
# ENGINE: The database backend (postgresql)
# NAME: Database name we created
# USER/PASSWORD: Database credentials
# HOST: localhost (same machine)
# PORT: 5432 (PostgreSQL default)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('PGDATABASE', 'traveleasedb'),
        'USER': os.environ.get('PGUSER', 'travelease'),
        'PASSWORD': os.environ.get('PGPASSWORD', 'travelease123'),
        'HOST': os.environ.get('PGHOST', 'localhost'),
        'PORT': os.environ.get('PGPORT', '5432'),
    }
}


# =============================================
# PASSWORD VALIDATION
# =============================================
# These validators enforce password strength during registration
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        # Prevents password from being too similar to username/email
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        # Enforces minimum password length (default: 8 characters)
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        # Prevents use of commonly known passwords
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        # Prevents all-numeric passwords
    },
]


# =============================================
# INTERNATIONALIZATION
# =============================================
LANGUAGE_CODE = 'en-us'          # English (US)
TIME_ZONE = 'Asia/Kathmandu'     # Nepal timezone (UTC+5:45)
USE_I18N = True                  # Internationalization support
USE_TZ = True                    # Timezone-aware datetimes


# =============================================
# STATIC FILES (CSS, JavaScript, Images)
# =============================================
# STATIC_URL: URL prefix for static files
# STATICFILES_DIRS: additional directories where static files are stored
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'  # For collectstatic in production


# =============================================
# MEDIA FILES (User-uploaded content)
# =============================================
# MEDIA_URL: URL prefix for media files
# MEDIA_ROOT: filesystem path where uploaded files are stored
# This handles bus photos, flight images uploaded by admin
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# =============================================
# DEFAULT PRIMARY KEY FIELD TYPE
# =============================================
# Sets the default type for auto-generated primary keys
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# =============================================
# AUTHENTICATION SETTINGS
# =============================================
# LOGIN_URL: where unauthenticated users are redirected
# LOGIN_REDIRECT_URL: where users go after successful login
# LOGOUT_REDIRECT_URL: where users go after logout
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'booking:home'
LOGOUT_REDIRECT_URL = 'booking:home'


# =============================================
# EMAIL CONFIGURATION (for OTP + Booking Emails)
# =============================================
# Django sends real emails through Gmail's SMTP server.
# Uses an App Password (not the account password) for security.
#
# How it works:
#   - Registration OTP → sent to the user's email
#   - Booking confirmation → sent to the user's email
#   - Sender is always travelease.np@gmail.com

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '').strip()
# Sanitize password: strip spaces (Gmail App Passwords might be provided as 'abcd efgh ijkl mnop')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '').strip().replace(' ', '')

# Fallback to console email backend when in DEBUG mode if credentials are not configured
if DEBUG and not (EMAIL_HOST_USER and EMAIL_HOST_PASSWORD):
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Default "from" address for all outgoing emails
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER or 'noreply@travelease.np')


# =============================================
# OTP SETTINGS
# =============================================
# OTP expiry time in minutes
OTP_EXPIRY_MINUTES = 10
# OTP length (number of digits)
OTP_LENGTH = 6


# =============================================
# DJANGO-ALLAUTH (Google OAuth)
# =============================================
SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'OAUTH_PKCE_ENABLED': True,
    }
}

# allauth account settings
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_LOGIN_ON_GET = True
