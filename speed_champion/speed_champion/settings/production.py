"""
Django production settings.

For Raspberry Pi deployment with PostgreSQL and HTTPS.
"""
import os
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    'karts.tiago-coutinho.com',
    'www.karts.tiago-coutinho.com',
]

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = [
    'https://karts.tiago-coutinho.com',
    'https://www.karts.tiago-coutinho.com',
]

# Session and Cookie settings for production (HTTPS)
SESSION_COOKIE_SECURE = True    # HTTPS only
SESSION_COOKIE_SAMESITE = 'Lax' # Same-domain (frontend on same domain)
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'Lax'

# Database - PostgreSQL for production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'karts_db'),
        'USER': os.getenv('DB_USER', 'karts_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'change-this-password'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,  # Connection pooling
    }
}

# CORS - Only allow specific frontend domain
CORS_ALLOWED_ORIGINS = [
    'https://karts.tiago-coutinho.com',  # Your Lovable frontend URL
    # Add Lovable domain when you have it:
    # 'https://your-lovable-app.lovable.dev',
]

# Static files
STATIC_ROOT = '/home/pi/karts-app/staticfiles'

# Security settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': '/home/pi/karts-app/django.log',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}
