# PulseWatch Architecture

## Table of Contents

- [Overview](#overview)
- [Architectural Principles](#architectural-principles)
- [Clean Architecture Layers](#clean-architecture-layers)
- [Domain-Driven Design](#domain-driven-design)
- [Project Structure](#project-structure)
- [Key Components](#key-components)
- [Data Flow](#data-flow)
- [Technology Stack](#technology-stack)
- [Design Patterns](#design-patterns)
- [Scalability Considerations](#scalability-considerations)

## Overview

PulseWatch is built using **Clean Architecture** and **Domain-Driven Design (DDD)** principles to ensure:

- **Maintainability**: Clear separation of concerns
- **Testability**: Components can be tested in isolation
- **Flexibility**: Easy to swap implementations
- **Scalability**: Prepared for growth

## Architectural Principles

### 1. Separation of Concerns

Each layer has a distinct responsibility:
- **Domain**: Business logic
- **Application**: Use cases
- **Infrastructure**: Technical details
- **Interface**: User interactions

### 2. Dependency Inversion

Dependencies point inward:
```
Interface → Application → Domain
     ↓            ↓
Infrastructure ←--┘
```

The domain layer has **zero external dependencies**.

### 3. Explicit Architecture

File structure reflects architectural boundaries:
```
pulsewatch/
├── domain/           # Business rules (pure Python)
├── application/      # Use cases
├── infrastructure/   # Implementation details
└── interface/        # Controllers, views
```

### 4. Bounded Contexts

The system is divided into bounded contexts:
- **Health Monitoring**: Check endpoints, report status
- **Notifications**: Alert users about issues
- **User Management**: Authentication, authorization
- **Team Management**: Organizations, teams, permissions
- **Billing**: Subscriptions, usage tracking

## Clean Architecture Layers

### Layer 1: Domain (Innermost)

**Location**: `domain/`

**Purpose**: Core business logic and rules

**Characteristics**:
- Pure Python (no Django, no frameworks)
- No external dependencies
- Contains entities, value objects, domain services
- Business rules enforced here

**Example**:
```python
# domain/entities/health_check.py
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class CheckStatus(Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass
class HealthCheck:
    id: HealthCheckId
    url: str
    interval_seconds: int
    timeout_seconds: int
    status: CheckStatus = CheckStatus.UNKNOWN
    last_checked_at: datetime | None = None

    def mark_healthy(self) -> None:
        """Mark check as healthy."""
        self.status = CheckStatus.HEALTHY
        self.last_checked_at = datetime.now(UTC)

    def mark_unhealthy(self) -> None:
        """Mark check as unhealthy."""
        if self.status == CheckStatus.HEALTHY:
            # Trigger notification (via domain event)
            self._record_event(HealthCheckFailedEvent(self.id))
        self.status = CheckStatus.UNHEALTHY
        self.last_checked_at = datetime.now(UTC)
```

### Layer 2: Application

**Location**: `application/`

**Purpose**: Orchestrate use cases

**Characteristics**:
- Implements business use cases
- Coordinates domain objects
- Depends only on domain layer
- Defines repository interfaces

**Example**:
```python
# application/use_cases/perform_health_check.py
from domain.entities.health_check import HealthCheck, CheckStatus
from domain.repositories.health_check_repository import HealthCheckRepository

class PerformHealthCheckUseCase:
    def __init__(
        self,
        repository: HealthCheckRepository,
        http_client: HttpClient
    ):
        self.repository = repository
        self.http_client = http_client

    def execute(self, check_id: HealthCheckId) -> HealthCheck:
        # Fetch check
        check = self.repository.get_by_id(check_id)

        # Perform HTTP request
        try:
            response = self.http_client.get(
                check.url,
                timeout=check.timeout_seconds
            )
            if response.status_code == 200:
                check.mark_healthy()
            else:
                check.mark_unhealthy()
        except Exception:
            check.mark_unhealthy()

        # Save result
        self.repository.save(check)

        return check
```

### Layer 3: Infrastructure

**Location**: `infrastructure/`

**Purpose**: Technical implementation details

**Characteristics**:
- Django ORM models
- External service integrations
- Repository implementations
- Database access
- HTTP clients
- Message queues

**Example**:
```python
# infrastructure/repositories/django_health_check_repository.py
from domain.repositories.health_check_repository import HealthCheckRepository
from infrastructure.db.models import HealthCheckModel

class DjangoHealthCheckRepository(HealthCheckRepository):
    def get_by_id(self, check_id: HealthCheckId) -> HealthCheck:
        model = HealthCheckModel.objects.get(id=check_id.value)
        return self._to_entity(model)

    def save(self, check: HealthCheck) -> None:
        model = HealthCheckModel.objects.get(id=check.id.value)
        model.status = check.status.value
        model.last_checked_at = check.last_checked_at
        model.save()

    def _to_entity(self, model: HealthCheckModel) -> HealthCheck:
        return HealthCheck(
            id=HealthCheckId(model.id),
            url=model.url,
            interval_seconds=model.interval_seconds,
            timeout_seconds=model.timeout_seconds,
            status=CheckStatus(model.status),
            last_checked_at=model.last_checked_at
        )
```

### Layer 4: Interface (Outermost)

**Location**: `interface/`

**Purpose**: Handle external interactions

**Characteristics**:
- REST API endpoints
- CLI commands
- GraphQL resolvers (future)
- WebSocket handlers (future)

**Example**:
```python
# interface/api/views/health_check_views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from application.use_cases.perform_health_check import PerformHealthCheckUseCase

class HealthCheckViewSet(viewsets.ViewSet):
    def create(self, request):
        # Dependency injection (from DI container)
        use_case = PerformHealthCheckUseCase(
            repository=DjangoHealthCheckRepository(),
            http_client=RequestsHttpClient()
        )

        # Execute use case
        check = use_case.execute(
            check_id=HealthCheckId(request.data['id'])
        )

        # Serialize response
        serializer = HealthCheckSerializer(check)
        return Response(serializer.data, status=status.HTTP_200_OK)
```

## Domain-Driven Design

### Entities

Objects with identity that persist over time:
```python
@dataclass
class User:
    id: UserId
    email: str
    username: str
    created_at: datetime
```

### Value Objects

Immutable objects defined by their attributes:
```python
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str

    def add(self, other: Money) -> Money:
        if self.currency != other.currency:
            raise CurrencyMismatchError()
        return Money(self.amount + other.amount, self.currency)
```

### Aggregates

Cluster of entities and value objects:
```python
class HealthCheckAggregate:
    def __init__(self, check: HealthCheck):
        self._check = check
        self._history: list[HealthCheckResult] = []

    def add_result(self, result: HealthCheckResult) -> None:
        self._history.append(result)
        if result.is_failure:
            self._check.mark_unhealthy()
        else:
            self._check.mark_healthy()
```

### Domain Events

Capture important business events:
```python
@dataclass
class HealthCheckFailedEvent:
    check_id: HealthCheckId
    failed_at: datetime
    reason: str
```

### Repositories

Abstraction for data access:
```python
class HealthCheckRepository(ABC):
    @abstractmethod
    def get_by_id(self, check_id: HealthCheckId) -> HealthCheck:
        pass

    @abstractmethod
    def save(self, check: HealthCheck) -> None:
        pass

    @abstractmethod
    def find_due_checks(self) -> list[HealthCheck]:
        pass
```

## Project Structure

```
pulsewatch/
├── apps/                    # Django apps (bounded contexts)
│   ├── health/             # Health monitoring context
│   │   ├── domain/
│   │   │   ├── entities/
│   │   │   ├── value_objects/
│   │   │   └── repositories/
│   │   ├── application/
│   │   │   └── use_cases/
│   │   ├── infrastructure/
│   │   │   ├── db/
│   │   │   └── repositories/
│   │   └── interface/
│   │       └── api/
│   ├── notifications/      # Notification context
│   └── users/             # User management context
│
├── core/                   # Shared infrastructure
│   ├── settings/          # Django settings
│   ├── middleware/        # Custom middleware
│   ├── health/           # Health check endpoints
│   └── utils/            # Shared utilities
│
├── shared/                # Shared domain concepts
│   ├── domain/
│   │   └── value_objects/
│   └── infrastructure/
│
├── tests/                 # Test suite
│   ├── unit/
│   ├── integration/
│   └── contract/
│
└── docker/               # Docker configuration
```

## Key Components

### 1. Health Check System

**Purpose**: Monitor endpoint availability

**Components**:
- `HealthCheck` entity: Stores check configuration
- `HealthCheckResult` value object: Represents single check result
- `PerformHealthCheckUseCase`: Executes health check
- `HealthCheckScheduler`: Background task scheduler

### 2. Notification System

**Purpose**: Alert users about failures

**Components**:
- `Notification` entity: Notification record
- `NotificationChannel`: Email, SMS, Webhook, etc.
- `SendNotificationUseCase`: Sends notification
- `NotificationRouter`: Routes to appropriate channel

### 3. User Management

**Purpose**: Authentication and authorization

**Components**:
- `User` entity: User account
- `Team` entity: Organization/team
- `Permission` value object: Access control
- `AuthenticateUserUseCase`: Login logic

## Data Flow

### Request Flow (Read)

```
1. HTTP Request
   ↓
2. Interface Layer (View/Controller)
   ↓
3. Application Layer (Use Case)
   ↓
4. Domain Layer (Entity/Value Object)
   ↓
5. Infrastructure Layer (Repository)
   ↓
6. Database
   ↓
7. Response (reverse direction)
```

### Command Flow (Write)

```
1. HTTP Request (Command)
   ↓
2. Interface Layer (Validates input)
   ↓
3. Application Layer (Use Case)
   ↓
4. Domain Layer (Business rules enforced)
   ↓
5. Infrastructure Layer (Persist)
   ↓
6. Database
   ↓
7. Domain Events Published
   ↓
8. Event Handlers (Async)
```

## Technology Stack

### Backend

- **Language**: Python 3.12
- **Framework**: Django 5.x
- **API**: Django REST Framework 3.x
- **Task Queue**: Celery 5.x
- **Database**: MySQL 8.x (InnoDB)
- **Cache**: Redis 7.x
- **Testing**: pytest, pytest-django

### Infrastructure

- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus metrics
- **Logging**: Structured JSON logging

### Development

- **Code Formatting**: Black, isort
- **Linting**: Flake8, Bandit
- **Type Checking**: MyPy
- **Pre-commit Hooks**: pre-commit framework

## Design Patterns

### 1. Repository Pattern

Abstracts data access:
```python
class UserRepository(ABC):
    @abstractmethod
    def find_by_email(self, email: str) -> User | None:
        pass
```

### 2. Factory Pattern

Creates complex objects:
```python
class HealthCheckFactory:
    @staticmethod
    def create_http_check(url: str, interval: int) -> HealthCheck:
        return HealthCheck(
            id=HealthCheckId(),
            url=url,
            interval_seconds=interval,
            timeout_seconds=30
        )
```

### 3. Strategy Pattern

Varies behavior at runtime:
```python
class NotificationStrategy(ABC):
    @abstractmethod
    def send(self, notification: Notification) -> None:
        pass

class EmailStrategy(NotificationStrategy):
    def send(self, notification: Notification) -> None:
        # Send email
        pass

class SMSStrategy(NotificationStrategy):
    def send(self, notification: Notification) -> None:
        # Send SMS
        pass
```

### 4. Observer Pattern

Publish domain events:
```python
class DomainEventPublisher:
    def __init__(self):
        self._handlers: dict[Type, list[Callable]] = {}

    def subscribe(self, event_type: Type, handler: Callable) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    def publish(self, event: DomainEvent) -> None:
        for handler in self._handlers.get(type(event), []):
            handler(event)
```

### 5. Dependency Injection

Inject dependencies at runtime:
```python
# Using a simple DI container
class Container:
    def __init__(self):
        self._services = {}

    def register(self, interface: Type, implementation: Type):
        self._services[interface] = implementation

    def resolve(self, interface: Type):
        return self._services[interface]()
```

## Scalability Considerations

### Horizontal Scaling

- **Stateless application servers**: Can run multiple instances
- **Load balancer**: Distribute traffic (NGINX/AWS ELB)
- **Database read replicas**: Scale read operations
- **Redis cluster**: Distribute cache

### Vertical Scaling

- **Database**: Upgrade to larger instances
- **Application servers**: More CPU/RAM
- **Redis**: Larger memory allocation

### Performance Optimization

1. **Database Indexing**:
   ```python
   class HealthCheckModel(models.Model):
       url = models.URLField(db_index=True)
       next_check_at = models.DateTimeField(db_index=True)
   ```

2. **Query Optimization**:
   - Use `select_related()` and `prefetch_related()`
   - Avoid N+1 queries
   - Paginate large result sets

3. **Caching**:
   - Cache expensive queries
   - Use Redis for session storage
   - Implement cache invalidation

4. **Async Processing**:
   - Celery for background tasks
   - Message queues for decoupling
   - Event-driven architecture

### Monitoring

- **Prometheus metrics**: Track performance
- **Structured logging**: Debug issues
- **Health checks**: Monitor service health
- **Alerting**: Notify on anomalies

## Testing Strategy

### Unit Tests

Test domain logic in isolation:
```python
def test_health_check_marks_unhealthy():
    check = HealthCheck(...)
    check.mark_unhealthy()
    assert check.status == CheckStatus.UNHEALTHY
```

### Integration Tests

Test layer interactions:
```python
def test_perform_health_check_use_case(db, mock_http):
    use_case = PerformHealthCheckUseCase(...)
    result = use_case.execute(check_id)
    assert result.status == CheckStatus.HEALTHY
```

### Contract Tests

Test API contracts:
```python
def test_health_check_api_response_format(client):
    response = client.get('/api/health-checks/1')
    assert response.status_code == 200
    assert 'id' in response.json()
    assert 'url' in response.json()
```

## Future Enhancements

1. **Event Sourcing**: Store all state changes as events
2. **CQRS**: Separate read and write models
3. **GraphQL API**: Flexible querying
4. **WebSockets**: Real-time updates
5. **Multi-tenancy**: Isolated data per tenant
6. **Microservices**: Split into independent services

## References

- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design](https://martinfowler.com/tags/domain%20driven%20design.html)
- [Django Best Practices](https://django-best-practices.readthedocs.io/)
- [Twelve-Factor App](https://12factor.net/)

---

**Last Updated**: October 31, 2025
