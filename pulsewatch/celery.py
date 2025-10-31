"""
Celery configuration for PulseWatch.

This module initializes the Celery application and configures task discovery.
"""
import os

from celery import Celery

# Set default Django settings module for Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.dev')

# Create Celery app
app = Celery('pulsewatch')

# Load configuration from Django settings using CELERY_ namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed Django apps
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self) -> None:
    """Debug task for testing Celery setup."""
    print(f'Request: {self.request!r}')
