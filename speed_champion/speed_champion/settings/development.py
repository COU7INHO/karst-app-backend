"""
Django development settings.

For local development with:
- SQLite database
- Debug mode enabled
- CORS allow all origins
- HTTP/HTTPS support for ngrok
"""
from .base import *

# Debug mode - NEVER set this to True in production
DEBUG = True

# Allowed hosts for development
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'nonlaminated-subliminally-latanya.ngrok-free.dev',  # ngrok tunnel
]

# CSRF trusted origins - add ngrok and any other dev domains
CSRF_TRUSTED_ORIGINS = [
    'https://nonlaminated-subliminally-latanya.ngrok-free.dev',
]

# Session and Cookie settings for development
# These allow cross-origin requests from frontend during development
SESSION_COOKIE_SAMESITE = None   # Allow cross-origin (needed for ngrok)
SESSION_COOKIE_SECURE = False    # Allow HTTP in development
SESSION_COOKIE_HTTPONLY = True   # Security: prevent JavaScript access
CSRF_COOKIE_SAMESITE = None      # Allow cross-origin
CSRF_COOKIE_SECURE = False       # Allow HTTP in development

# Database - SQLite for easy local development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# CORS - Allow all origins in development for easy frontend testing
CORS_ALLOW_ALL_ORIGINS = True

# Static files configuration
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'
