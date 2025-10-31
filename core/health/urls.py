"""
URL configuration for health check endpoints.

Provides /healthz (liveness) and /ready (readiness) endpoints.
"""

from django.urls import path

from core.health.views import healthz_view, ready_view

urlpatterns = [
    path("healthz/", healthz_view, name="healthz"),
    path("ready/", ready_view, name="ready"),
]
