"""
Root URL configuration for PulseWatch project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),

    # Prometheus metrics endpoint
    path('', include('django_prometheus.urls')),

    # Health check endpoints
    path('', include('core.health.urls')),
]
