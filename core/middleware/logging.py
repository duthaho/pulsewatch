"""
Structured logging middleware for PulseWatch.

Implements JSON structured logging with request correlation IDs using structlog.
"""

import uuid
from typing import Callable

import structlog
from django.http import HttpRequest, HttpResponse

logger = structlog.get_logger(__name__)


class StructuredLoggingMiddleware:
    """
    Middleware that adds structured logging with request correlation.

    Generates a unique request_id for each request and binds it to the logger
    context for the duration of the request processing.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """Initialize middleware with the next middleware/view in the chain."""
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Process request and add structured logging context.

        Args:
            request: The Django HTTP request object

        Returns:
            HttpResponse: The response from downstream middleware/view
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.request_id = request_id  # type: ignore[attr-defined]

        # Bind request context to logger
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.path,
            ip_address=self._get_client_ip(request),
        )

        # Log request started
        logger.info(
            "request_started",
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

        # Process request
        response = self.get_response(request)

        # Log request completed
        logger.info(
            "request_completed",
            status_code=response.status_code,
        )

        # Add request ID to response headers for tracing
        response["X-Request-ID"] = request_id

        return response

    def _get_client_ip(self, request: HttpRequest) -> str:
        """
        Extract client IP address from request.

        Handles X-Forwarded-For header for proxied requests.

        Args:
            request: The Django HTTP request object

        Returns:
            str: Client IP address
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR", "")
        return ip
