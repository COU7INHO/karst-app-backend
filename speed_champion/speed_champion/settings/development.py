"""
Django development settings.

For local development on your Mac with ngrok.
"""
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'nonlaminated-subliminally-latanya.ngrok-free.dev',
    'localhost',
    '127.0.0.1',
]

# CSRF trusted origins for ngrok
CSRF_TRUSTED_ORIGINS = ['https://nonlaminated-subliminally-latanya.ngrok-free.dev']

# Session and Cookie settings for development
SESSION_COOKIE_SAMESITE = None  # Allow cross-origin (for ngrok)
SESSION_COOKIE_SECURE = False   # HTTP allowed in development
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = None
CSRF_COOKIE_SECURE = False

# Database - SQLite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# CORS - Allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True

# Add debug middleware for development
MIDDLEWARE.insert(2, 'speed_champion.debug_middleware.DebugRequestMiddleware')

# Static files
STATIC_ROOT = BASE_DIR / 'staticfiles'
