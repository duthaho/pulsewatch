"""PulseWatch SaaS Platform - Main Django Package."""

__version__ = "0.1.0"

# Import Celery app to ensure it's always available
from .celery import app as celery_app

__all__ = ("celery_app",)
