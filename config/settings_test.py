from .settings import *

# disable throttling
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = []
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {}

# test database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'lumio_test_db',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# no real emails
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# fake payment keys
PAYSTACK_SECRET_KEY = 'sk_test_fake_key'
PAYSTACK_PUBLIC_KEY = 'pk_test_fake_key'

# faster password hashing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# no SSL in tests
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False