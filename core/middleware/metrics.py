"""
Custom Prometheus metrics middleware for PulseWatch.

Implements application-specific metrics on top of django-prometheus baseline.
"""
import time
from typing import Callable

from django.http import HttpRequest, HttpResponse
from prometheus_client import Counter, Gauge, Histogram

# Custom application metrics

# Application info metric (always 1, used for version labeling)
app_info = Gauge(
    'pulsewatch_app_info',
    'Application information',
    ['version']
)

# Application start time
app_start_time = Gauge(
    'pulsewatch_app_start_time_seconds',
    'Unix timestamp of application start'
)

# Health check metrics
health_check_duration = Histogram(
    'pulsewatch_health_check_duration_seconds',
    'Health check execution time',
    ['check_name'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

health_check_status = Gauge(
    'pulsewatch_health_check_status',
    'Health check status (1=healthy, 0=unhealthy)',
    ['check_name']
)

# Request metrics (additional to django-prometheus)
active_requests = Gauge(
    'pulsewatch_active_requests',
    'Number of requests currently being processed'
)

# Initialize app metrics
from pulsewatch import __version__

app_info.labels(version=__version__).set(1)
app_start_time.set(time.time())


class MetricsMiddleware:
    """
    Middleware for custom application metrics.
    
    Tracks active requests and provides hooks for custom metrics.
    Works alongside django-prometheus for comprehensive observability.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """Initialize middleware with the next middleware/view in the chain."""
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Process request and update metrics.
        
        Args:
            request: The Django HTTP request object
            
        Returns:
            HttpResponse: The response from downstream middleware/view
        """
        # Track active requests
        active_requests.inc()
        
        try:
            response = self.get_response(request)
            return response
        finally:
            # Decrement active requests counter
            active_requests.dec()
