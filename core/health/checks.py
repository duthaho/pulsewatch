"""
Health check functions for PulseWatch.

Provides health check implementations for various dependencies.
"""
import time
from typing import Any, Dict

import structlog
from django.conf import settings
from django.core.cache import cache
from django.db import connection

from core.middleware.metrics import health_check_duration, health_check_status

logger = structlog.get_logger(__name__)


def database_health_check() -> Dict[str, Any]:
    """
    Check database connectivity and responsiveness.
    
    Returns:
        Dict containing status, latency, and message.
    """
    start_time = time.time()
    
    try:
        # Simple query to verify database connectivity
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Update metrics
        health_check_duration.labels(check_name='database').observe(latency_ms / 1000)
        health_check_status.labels(check_name='database').set(1)
        
        logger.info(
            "database_health_check_success",
            latency_ms=latency_ms,
        )
        
        return {
            'status': 'healthy',
            'latency_ms': round(latency_ms, 2),
            'message': 'MySQL connection successful'
        }
    
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        
        # Update metrics
        health_check_duration.labels(check_name='database').observe(latency_ms / 1000)
        health_check_status.labels(check_name='database').set(0)
        
        logger.error(
            "database_health_check_failed",
            error=str(e),
            latency_ms=latency_ms,
        )
        
        return {
            'status': 'unhealthy',
            'latency_ms': round(latency_ms, 2),
            'message': f'Database connection failed: {str(e)}'
        }


def redis_health_check() -> Dict[str, Any]:
    """
    Check Redis connectivity and responsiveness.
    
    Returns:
        Dict containing status, latency, and message.
    """
    start_time = time.time()
    
    try:
        # Test Redis with a ping
        cache.set('health_check', 'ping', timeout=10)
        result = cache.get('health_check')
        
        if result != 'ping':
            raise Exception("Redis value mismatch")
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Update metrics
        health_check_duration.labels(check_name='redis').observe(latency_ms / 1000)
        health_check_status.labels(check_name='redis').set(1)
        
        logger.info(
            "redis_health_check_success",
            latency_ms=latency_ms,
        )
        
        return {
            'status': 'healthy',
            'latency_ms': round(latency_ms, 2),
            'message': 'Redis connection successful'
        }
    
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        
        # Update metrics
        health_check_duration.labels(check_name='redis').observe(latency_ms / 1000)
        health_check_status.labels(check_name='redis').set(0)
        
        logger.error(
            "redis_health_check_failed",
            error=str(e),
            latency_ms=latency_ms,
        )
        
        return {
            'status': 'unhealthy',
            'latency_ms': round(latency_ms, 2),
            'message': f'Redis connection failed: {str(e)}'
        }
