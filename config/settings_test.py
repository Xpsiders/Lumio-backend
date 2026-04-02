from decouple import config
from .settings import *

REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = []
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

PAYSTACK_SECRET_KEY = 'sk_test_fake_key'
PAYSTACK_PUBLIC_KEY = 'pk_test_fake_key'

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]