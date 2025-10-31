"""
Health check views for PulseWatch.

Provides /healthz (liveness) and /ready (readiness) endpoints.
"""
from datetime import datetime, timezone
from typing import Any, Dict

import structlog
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from core.health.checks import database_health_check, redis_health_check
from pulsewatch import __version__

logger = structlog.get_logger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def healthz_view(request: Request) -> Response:
    """
    Liveness probe endpoint.

    Returns 200 OK if the application process is running.
    Does not check dependencies - only verifies the service is alive.

    Response schema (per contracts/health.yaml):
    {
        "status": "healthy",
        "timestamp": "2025-10-31T10:30:00.123456Z",
        "version": "0.1.0"
    }
    """
    response_data = {
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'version': __version__,
    }

    logger.info("healthz_check", status="healthy")

    return Response(response_data, status=200)


@api_view(['GET'])
@permission_classes([AllowAny])
def ready_view(request: Request) -> Response:
    """
    Readiness probe endpoint.

    Returns 200 OK if the application is ready to serve traffic.
    Checks all critical dependencies (database, Redis).

    Response schema (per contracts/health.yaml):
    {
        "status": "ready" | "not_ready",
        "timestamp": "2025-10-31T10:30:00.123456Z",
        "version": "0.1.0",
        "checks": {
            "database": {
                "status": "healthy" | "unhealthy",
                "latency_ms": 5.23,
                "message": "MySQL connection successful"
            },
            "redis": {
                "status": "healthy" | "unhealthy",
                "latency_ms": 1.45,
                "message": "Redis connection successful"
            }
        }
    }
    """
    # Run all health checks
    checks = {
        'database': database_health_check(),
        'redis': redis_health_check(),
    }

    # Determine overall status
    all_healthy = all(
        check['status'] == 'healthy'
        for check in checks.values()
    )

    overall_status = 'ready' if all_healthy else 'not_ready'
    http_status = 200 if all_healthy else 503

    response_data = {
        'status': overall_status,
        'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'version': __version__,
        'checks': checks,
    }

    logger.info(
        "ready_check",
        status=overall_status,
        database_status=checks['database']['status'],
        redis_status=checks['redis']['status'],
    )

    return Response(response_data, status=http_status)
