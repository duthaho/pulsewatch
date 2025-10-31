---
description: "Generate Django application with best practices"
---

# Django Application Setup

## Overview

This prompt helps you create a Django application following clean architecture and DDD principles.

## Project Structure

```
project/
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── domain/
│   ├── __init__.py
│   ├── entities/
│   ├── value_objects/
│   └── events.py
├── application/
│   ├── __init__.py
│   ├── use_cases/
│   └── repositories.py
├── infrastructure/
│   ├── __init__.py
│   ├── django_models/
│   ├── repositories/
│   └── middleware/
├── api/
│   ├── __init__.py
│   ├── views/
│   ├── serializers/
│   ├── urls.py
│   └── permissions.py
├── tests/
├── manage.py
├── requirements.txt
└── README.md
```

## settings/base.py

```python
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'infrastructure.middleware.security.SecurityHeadersMiddleware',
]

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'pulsewatch'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
}

# CORS
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]
```

## API View Example

```python
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from uuid import UUID

from api.serializers.order import CreateOrderSerializer, OrderSerializer
from application.use_cases.create_order import CreateOrderUseCase
from infrastructure.repositories.order_repository import DjangoOrderRepository

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request: Request) -> Response:
    """
    Create a new order for a customer.
    
    Request body:
    - customer_id: UUID of the customer
    - items: List of order items
    """
    serializer = CreateOrderSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Inject dependencies
        repository = DjangoOrderRepository()
        use_case = CreateOrderUseCase(repository)
        
        order = use_case.execute(
            customer_id=UUID(serializer.validated_data['customer_id']),
            items=serializer.validated_data['items']
        )
        
        response_serializer = OrderSerializer.from_domain(order)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order(request: Request, order_id: str) -> Response:
    """Get order by ID."""
    try:
        repository = DjangoOrderRepository()
        use_case = CreateOrderUseCase(repository)
        
        order = use_case.get_by_id(UUID(order_id))
        if not order:
            return Response(
                {'error': f'Order {order_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = OrderSerializer.from_domain(order)
        return Response(serializer.data)
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
```

## DRF Serializers

```python
from rest_framework import serializers
from typing import List
from datetime import datetime
from domain.order import Order

class OrderItemSerializer(serializers.Serializer):
    """Serializer for order items."""
    product_id = serializers.CharField(
        help_text="Product UUID",
        max_length=255
    )
    quantity = serializers.IntegerField(
        min_value=1,
        help_text="Item quantity"
    )
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        help_text="Item price"
    )

class CreateOrderSerializer(serializers.Serializer):
    """Serializer for creating orders."""
    customer_id = serializers.UUIDField(
        help_text="Customer UUID"
    )
    items = OrderItemSerializer(
        many=True,
        required=False,
        default=list
    )

class OrderSerializer(serializers.Serializer):
    """Serializer for order responses."""
    id = serializers.UUIDField(read_only=True)
    customer_id = serializers.UUIDField()
    status = serializers.CharField()
    total_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    created_at = serializers.DateTimeField()

    @classmethod
    def from_domain(cls, order: Order) -> 'OrderSerializer':
        """Convert domain entity to serializer."""
        return cls({
            'id': str(order.id),
            'customer_id': str(order.customer_id),
            'status': order.status,
            'total_amount': order.calculate_total().amount,
            'created_at': order.created_at
        })
```

## URL Configuration

```python
# api/urls.py
from django.urls import path
from api.views import orders, customers

app_name = 'api'

urlpatterns = [
    # Order endpoints
    path('orders/', orders.create_order, name='create_order'),
    path('orders/<str:order_id>/', orders.get_order, name='get_order'),
    
    # Customer endpoints
    path('customers/', customers.list_customers, name='list_customers'),
    path('customers/<str:customer_id>/', customers.get_customer, name='get_customer'),
    
    # Health check
    path('health/', orders.health_check, name='health_check'),
]

# config/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls')),
]
```

## Testing

```python
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from uuid import uuid4

class OrderAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create test user and authenticate
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_order(self):
        """Test creating a new order."""
        response = self.client.post(
            '/api/v1/orders/',
            {
                'customer_id': str(uuid4()),
                'items': [
                    {'product_id': 'p1', 'quantity': 2, 'price': '10.00'}
                ]
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['status'], 'PENDING')
    
    def test_get_order(self):
        """Test retrieving an order by ID."""
        # First create an order
        create_response = self.client.post(
            '/api/v1/orders/',
            {'customer_id': str(uuid4()), 'items': []},
            format='json'
        )
        order_id = create_response.data['id']
        
        # Then retrieve it
        response = self.client.get(f'/api/v1/orders/{order_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], order_id)
```

## Running the Application

```bash
# Install dependencies
pip install django djangorestframework django-cors-headers psycopg2-binary

# Create migrations
python manage.py makemigrations

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Development mode with auto-reload
python manage.py runserver 0.0.0.0:8000

# Production with gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

## Environment Variables

```python
# config/settings/development.py
from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Disable security features for development
CORS_ALLOW_ALL_ORIGINS = True
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# config/settings/production.py
from .base import *

DEBUG = False

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Enable security features for production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

```bash
# .env
DJANGO_SETTINGS_MODULE=config.settings.development
SECRET_KEY=your-secret-key-here
DB_NAME=pulsewatch
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```
