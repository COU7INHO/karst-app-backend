"""
Settings module selector.

Automatically imports the correct settings based on DJANGO_ENV environment variable.

Usage:
    Development (default): No env variable needed
    Production: export DJANGO_ENV=production
"""
import os

env = os.environ.get('DJANGO_ENV', 'development')

if env == 'production':
    from .production import *
else:
    from .development import *

