"""
Django production settings.

For production deployment with:
- PostgreSQL database
- HTTPS enforced
- Enhanced security headers
- Restricted CORS origins
- Production-grade logging
"""
import os
from .base import *

# Debug mode - MUST be False in production
DEBUG = False

# Allowed hosts - only allow specific production domains
ALLOWED_HOSTS = [
    'karts.tiago-coutinho.com',
    'www.karts.tiago-coutinho.com',
]

# CSRF trusted origins - must match ALLOWED_HOSTS
CSRF_TRUSTED_ORIGINS = [
    'https://karts.tiago-coutinho.com',
    'https://www.karts.tiago-coutinho.com',
]

# Session and Cookie settings for production
# All cookies must be secure (HTTPS only) in production
SESSION_COOKIE_SECURE = True     # Require HTTPS
SESSION_COOKIE_SAMESITE = 'Lax'  # Protection against CSRF
SESSION_COOKIE_HTTPONLY = True   # Prevent JavaScript access
CSRF_COOKIE_SECURE = True        # Require HTTPS
CSRF_COOKIE_SAMESITE = 'Lax'     # Protection against CSRF
CSRF_COOKIE_HTTPONLY = False     # Allow JavaScript to read CSRF token

# Database - PostgreSQL for production
# All credentials should be set via environment variables
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'karts_db'),
        'USER': os.getenv('DB_USER', 'karts_user'),
        'PASSWORD': os.getenv('DB_PASSWORD'),  # REQUIRED in production
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,  # Keep connections alive for 10 minutes
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}

# CORS - Only allow specific trusted frontend origins
# NEVER use CORS_ALLOW_ALL_ORIGINS in production
CORS_ALLOWED_ORIGINS = [
    'https://karts.tiago-coutinho.com',
    'https://www.karts.tiago-coutinho.com',
]

# Static files - served by Nginx in production
STATIC_ROOT = '/app/staticfiles'
STATIC_URL = '/static/'

# Media files (user uploads)
MEDIA_ROOT = '/app/media'
MEDIA_URL = '/media/'

# Security settings - enforce HTTPS and secure headers
# SSL is handled by Cloudflare, so we don't redirect here
SECURE_SSL_REDIRECT = False                                       # Cloudflare handles SSL
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')   # Trust X-Forwarded-Proto from Cloudflare
SECURE_HSTS_SECONDS = 31536000                                   # Enable HSTS for 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True                            # Apply HSTS to all subdomains
SECURE_HSTS_PRELOAD = True                                       # Allow preloading in browsers
SECURE_BROWSER_XSS_FILTER = True                                 # Enable XSS filter
SECURE_CONTENT_TYPE_NOSNIFF = True                               # Prevent MIME sniffing
X_FRAME_OPTIONS = 'DENY'                                         # Prevent clickjacking

# Logging - change to WARNING level for production
LOGGING['loggers']['speed_champion']['level'] = 'INFO'
LOGGING['loggers']['django']['level'] = 'INFO'
