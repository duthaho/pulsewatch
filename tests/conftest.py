"""
Pytest configuration and fixtures for PulseWatch test suite.

Provides common fixtures and test configuration for all test types.
"""
from typing import Generator

import pytest
from django.test import Client
from rest_framework.test import APIClient


@pytest.fixture
def django_client() -> Client:
    """Provide a Django test client."""
    return Client()


@pytest.fixture
def api_client() -> APIClient:
    """Provide a DRF API client."""
    return APIClient()


@pytest.fixture
def authenticated_client(api_client: APIClient, django_user_model) -> APIClient:
    """Provide an authenticated API client with a test user."""
    user = django_user_model.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def test_user(django_user_model):
    """Create a test user."""
    return django_user_model.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def superuser(django_user_model):
    """Create a superuser."""
    return django_user_model.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123'
    )


@pytest.fixture(scope='session')
def celery_config():
    """Celery configuration for testing (eager mode)."""
    return {
        'broker_url': 'memory://',
        'result_backend': 'cache+memory://',
        'task_always_eager': True,
        'task_eager_propagates': True,
    }


@pytest.fixture(autouse=True)
def _clear_cache(settings):
    """Clear cache before each test."""
    from django.core.cache import cache
    cache.clear()


@pytest.fixture
def mock_redis(monkeypatch):
    """Mock Redis connection for testing."""
    class MockRedis:
        def __init__(self):
            self.data = {}
        
        def ping(self):
            return True
        
        def get(self, key):
            return self.data.get(key)
        
        def set(self, key, value, ex=None):
            self.data[key] = value
            return True
        
        def delete(self, key):
            if key in self.data:
                del self.data[key]
            return True
    
    return MockRedis()
