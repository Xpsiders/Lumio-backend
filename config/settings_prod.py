import os
from .settings import *

DEBUG = False

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# CORS Configuration - IMPROVED VERSION
CORS_ALLOW_ALL_ORIGINS = os.environ.get('CORS_ALLOW_ALL_ORIGINS', 'False') == 'True'

# Get CORS origins and properly validate them
CORS_ALLOWED_ORIGINS = []
if not CORS_ALLOW_ALL_ORIGINS:
    raw_origins = os.environ.get('CORS_ALLOWED_ORIGINS', '')
    if raw_origins:
        # Split by comma and clean up
        origins = [origin.strip() for origin in raw_origins.split(',') if origin.strip()]
        
        # Validate each origin has a scheme
        for origin in origins:
            if origin.startswith(('http://', 'https://')):
                CORS_ALLOWED_ORIGINS.append(origin)
            else:
                # Skip invalid origins to avoid errors
                print(f"Warning: Skipping invalid CORS origin (missing scheme): {origin}")

# If no valid origins and not allowing all, set a safe default
if not CORS_ALLOW_ALL_ORIGINS and not CORS_ALLOWED_ORIGINS:
    # Default to nothing in production (most secure)
    CORS_ALLOWED_ORIGINS = []
    print("Warning: No valid CORS_ALLOWED_ORIGINS set. CORS will block all cross-origin requests.")

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# CSRF Configuration - with validation
CSRF_TRUSTED_ORIGINS = []
raw_csrf_origins = os.environ.get('CSRF_TRUSTED_ORIGINS', '')
if raw_csrf_origins:
    csrf_origins = [origin.strip() for origin in raw_csrf_origins.split(',') if origin.strip()]
    for origin in csrf_origins:
        if origin.startswith(('http://', 'https://')):
            CSRF_TRUSTED_ORIGINS.append(origin)
        else:
            print(f"Warning: Skipping invalid CSRF origin (missing scheme): {origin}")

SECRET_KEY = os.environ.get('SECRET_KEY')

# database
import dj_database_url
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')

PAYSTACK_SECRET_KEY = os.environ.get('PAYSTACK_SECRET_KEY')
PAYSTACK_PUBLIC_KEY = os.environ.get('PAYSTACK_PUBLIC_KEY')

SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'