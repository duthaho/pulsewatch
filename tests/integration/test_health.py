"""
Integration tests for health check endpoints.

Tests the /healthz and /ready endpoints with real dependencies.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.integration
@pytest.mark.django_db
class TestHealthEndpoints:
    """Integration tests for health check endpoints."""
    
    def test_healthz_endpoint_returns_200(self, api_client: APIClient) -> None:
        """
        Test that /healthz endpoint returns 200 OK.
        
        Verifies liveness probe is working correctly.
        """
        url = reverse('healthz')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'healthy'
        assert 'timestamp' in response.data
        assert 'version' in response.data
        assert response.data['version'] == '0.1.0'
    
    def test_ready_endpoint_with_healthy_dependencies(
        self, 
        api_client: APIClient
    ) -> None:
        """
        Test that /ready endpoint returns 200 when all dependencies are healthy.
        
        Verifies readiness probe with healthy database and Redis.
        """
        url = reverse('ready')
        response = api_client.get(url)
        
        # Should return 200 OK with healthy status
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'ready'
        assert 'timestamp' in response.data
        assert 'version' in response.data
        assert 'checks' in response.data
        
        # Verify database check
        assert 'database' in response.data['checks']
        db_check = response.data['checks']['database']
        assert db_check['status'] == 'healthy'
        assert 'latency_ms' in db_check
        assert 'message' in db_check
        
        # Verify Redis check
        assert 'redis' in response.data['checks']
        redis_check = response.data['checks']['redis']
        assert redis_check['status'] == 'healthy'
        assert 'latency_ms' in redis_check
        assert 'message' in redis_check
    
    def test_ready_endpoint_with_unhealthy_database(
        self, 
        api_client: APIClient,
        monkeypatch
    ) -> None:
        """
        Test that /ready endpoint returns 503 when database is unhealthy.
        
        Simulates database failure and verifies proper error response.
        """
        # Mock database check to simulate failure
        def mock_db_check():
            return {
                'status': 'unhealthy',
                'latency_ms': 5000.0,
                'message': 'Database connection failed: Connection refused'
            }
        
        # Monkeypatch the function where it's used, not where it's defined
        monkeypatch.setattr(
            'core.health.views.database_health_check', 
            mock_db_check
        )
        
        url = reverse('ready')
        response = api_client.get(url)
        
        # Should return 503 Service Unavailable
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert response.data['status'] == 'not_ready'
        assert response.data['checks']['database']['status'] == 'unhealthy'
    
    def test_healthz_endpoint_does_not_require_authentication(
        self, 
        api_client: APIClient
    ) -> None:
        """
        Test that /healthz endpoint is accessible without authentication.
        
        Health checks must be public for load balancer probes.
        """
        url = reverse('healthz')
        # Don't authenticate the client
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_ready_endpoint_does_not_require_authentication(
        self, 
        api_client: APIClient
    ) -> None:
        """
        Test that /ready endpoint is accessible without authentication.
        
        Health checks must be public for load balancer probes.
        """
        url = reverse('ready')
        # Don't authenticate the client
        response = api_client.get(url)
        
        # Should work regardless of authentication
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_503_SERVICE_UNAVAILABLE
        ]
