"""
Production settings for PulseWatch project.

Extends base settings with production-specific security and performance configurations.
"""
from .base import *  # noqa: F403, F401

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Hosts/domain names that are valid for this site
# Must be set properly in production
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')  # noqa: F405

# Database - persistent connections for production
DATABASES['default']['CONN_MAX_AGE'] = 600  # noqa: F405
DATABASES['default']['OPTIONS'] = {  # noqa: F405
    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
    'charset': 'utf8mb4',
}

# Security settings
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=True)  # noqa: F405
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=True)  # noqa: F405
CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', default=True)  # noqa: F405
SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', default=31536000)  # noqa: F405
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# CSRF settings
CSRF_COOKIE_HTTPONLY = True
CSRF_USE_SESSIONS = True
CSRF_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_SAMESITE = 'Strict'

# Session security
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_SAVE_EVERY_REQUEST = True

# Email configuration for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')  # noqa: F405
EMAIL_PORT = env.int('EMAIL_PORT', default=587)  # noqa: F405
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)  # noqa: F405
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')  # noqa: F405
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')  # noqa: F405
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@pulsewatch.example.com')  # noqa: F405

# Celery - async execution for production
CELERY_TASK_ALWAYS_EAGER = False

# Cache - longer TTLs for production
CACHES['default']['TIMEOUT'] = 300  # noqa: F405

# Logging - JSON format for production (will be enhanced with structlog)
LOGGING['formatters']['json'] = {  # noqa: F405
    'format': '%(levelname)s %(asctime)s %(module)s %(message)s',
}
LOGGING['handlers']['console']['formatter'] = 'json'  # noqa: F405

# Admin site header
ADMIN_SITE_HEADER = 'PulseWatch Administration'
ADMIN_SITE_TITLE = 'PulseWatch Admin'
