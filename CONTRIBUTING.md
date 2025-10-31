# Contributing to PulseWatch

Thank you for your interest in contributing to PulseWatch! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Style Guidelines](#code-style-guidelines)
- [Commit Message Conventions](#commit-message-conventions)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Architecture Guidelines](#architecture-guidelines)
- [Common Tasks](#common-tasks)

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain a welcoming environment

## Getting Started

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- Git
- Make (optional but recommended)

### Initial Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/pulsewatch.git
   cd pulsewatch
   ```

2. **Set up development environment**:
   ```bash
   # Option A: Using Docker (recommended)
   cp .env.example .env
   make docker-up

   # Option B: Local development
   make setup  # Creates venv, installs dependencies, sets up pre-commit
   ```

3. **Verify installation**:
   ```bash
   make test
   curl http://localhost:8000/healthz
   ```

## Development Workflow

### 1. Create a Feature Branch

```bash
# Update main branch
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### Branch Naming Conventions

- `feature/` - New features (e.g., `feature/add-email-alerts`)
- `fix/` - Bug fixes (e.g., `fix/health-check-timeout`)
- `docs/` - Documentation only (e.g., `docs/update-readme`)
- `refactor/` - Code refactoring (e.g., `refactor/simplify-middleware`)
- `test/` - Test additions/changes (e.g., `test/add-integration-tests`)
- `chore/` - Maintenance tasks (e.g., `chore/update-dependencies`)

### 2. Make Your Changes

**Before coding**, check relevant instruction files:
- **Clean Architecture**: `.github/instructions/clean-architecture.instructions.md`
- **Domain-Driven Design**: `.github/instructions/domain-driven-design.instructions.md`
- **Python Style**: `.github/instructions/coding-style-python.instructions.md`
- **Testing**: `.github/instructions/unit-and-integration-tests.instructions.md`

**Follow TDD** when possible:
1. Write failing test
2. Implement minimal code to pass
3. Refactor
4. Repeat

### 3. Run Quality Checks Locally

**Before every commit**:
```bash
make check  # Runs lint + test (recommended)
```

**Individual checks**:
```bash
make format              # Auto-fix formatting issues
make lint                # Check code quality
make test                # Run test suite
make test-unit           # Unit tests only
make test-integration    # Integration tests only
```

**Comprehensive check (before pushing)**:
```bash
make pre-commit-ci      # Run all CI-level checks
```

### 4. Commit Your Changes

Follow [Conventional Commits](#commit-message-conventions):

```bash
git add .
git commit -m "feat: add user authentication"
```

Pre-commit hooks will run automatically. If they fail:
```bash
make format              # Fix formatting
git add .
git commit --amend --no-edit
```

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Code Style Guidelines

### Python Style

We follow **PEP 8** with the following configurations:

- **Line length**: 100 characters
- **Formatter**: Black
- **Import sorter**: isort (black-compatible profile)
- **Linter**: Flake8
- **Type checker**: MyPy

### Automated Formatting

```bash
# Auto-format all code
make format

# Or manually
black --line-length=100 .
isort --profile=black --line-length=100 .
```

### Code Quality Rules

1. **Type hints required** for all function signatures:
   ```python
   def calculate_total(items: list[Item]) -> Money:
       ...
   ```

2. **Docstrings required** for public APIs:
   ```python
   def send_notification(user: User, message: str) -> None:
       """Send notification to user.

       Args:
           user: The user to notify
           message: The notification message

       Raises:
           NotificationError: If notification fails
       """
   ```

3. **No wildcard imports**:
   ```python
   # Bad
   from django.conf import *

   # Good
   from django.conf import settings
   ```

4. **Use dataclasses or Pydantic models** for data structures:
   ```python
   from dataclasses import dataclass

   @dataclass
   class UserProfile:
       username: str
       email: str
       is_active: bool = True
   ```

5. **Prefer composition over inheritance**

6. **Use context managers** for resource management:
   ```python
   with open('file.txt') as f:
       data = f.read()
   ```

### Security Guidelines

Follow `.github/instructions/security-and-owasp.instructions.md`:

- **Never commit secrets** (pre-commit hooks will catch this)
- **Validate all inputs**
- **Use parameterized queries** (Django ORM handles this)
- **Implement proper authentication and authorization**
- **Use HTTPS in production**

## Commit Message Conventions

We use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation only
- **style**: Code style changes (formatting, no logic change)
- **refactor**: Code refactoring
- **perf**: Performance improvement
- **test**: Adding or updating tests
- **build**: Build system or dependencies
- **ci**: CI/CD configuration
- **chore**: Maintenance tasks

### Examples

```bash
feat: add email notification system
feat(auth): implement JWT token refresh
fix: resolve health check timeout issue
fix(api): handle null values in JSON response
docs: update API documentation
docs(readme): add Docker troubleshooting section
test: add integration tests for user service
refactor: simplify middleware logic
perf: optimize database queries in health checks
ci: add Python 3.11 to test matrix
```

### Breaking Changes

Add `BREAKING CHANGE:` in the commit body:

```bash
git commit -m "feat: redesign authentication API

BREAKING CHANGE: The /api/auth/login endpoint now returns a different response format."
```

## Testing Requirements

### Coverage Requirements

- **Minimum**: 80% (CI will fail below this)
- **Target**: 85%
- **Ideal**: 90%+

### Test Types

1. **Unit Tests** (`tests/unit/`)
   - Test individual components in isolation
   - No external dependencies (mock databases, APIs)
   - Fast execution (<100ms per test)

2. **Integration Tests** (`tests/integration/`)
   - Test interactions between components
   - Use real database (test database)
   - Can use Docker containers

3. **Contract Tests** (`tests/contract/`)
   - Test API contracts (request/response formats)
   - Verify endpoints match OpenAPI specs

### Writing Tests

Follow `.github/instructions/unit-and-integration-tests.instructions.md`:

```python
import pytest
from domain.order import Order, Money

class TestOrder:
    """Test domain logic without dependencies"""

    def test_add_item_to_pending_order(self):
        # Arrange
        order = Order(id=uuid4(), customer_id=uuid4())
        price = Money(10.0, "USD")

        # Act
        order.add_item("product-1", quantity=2, price=price)

        # Assert
        assert len(order.items) == 1
        assert order.items[0].quantity == 2
```

### Running Tests

```bash
# All tests with coverage
make test

# Specific test types
make test-unit
make test-integration
make test-contract

# Specific test file
pytest tests/unit/test_health.py -v

# Specific test function
pytest tests/unit/test_health.py::test_healthz_endpoint -v

# With coverage report
pytest --cov --cov-report=html
open htmlcov/index.html
```

## Pull Request Process

### Before Submitting

1. ✅ All tests pass locally
2. ✅ Coverage ≥80%
3. ✅ No linting errors
4. ✅ Type checking passes
5. ✅ Documentation updated
6. ✅ Commit messages follow conventions
7. ✅ Branch is up to date with main

```bash
# Check everything
make check
make pre-commit-ci

# Update branch
git checkout main
git pull origin main
git checkout feature/your-feature
git rebase main
```

### PR Template

Use this template for your PR description:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #123

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass locally
- [ ] Coverage ≥80%
```

### Review Process

1. **Automated checks** run (CI pipeline)
2. **Code review** by maintainer
3. **Address feedback** by pushing new commits
4. **Approval** from at least one maintainer
5. **Merge** (squash and merge preferred)

### Addressing Review Feedback

```bash
# Make changes
git add .
git commit -m "refactor: address review feedback"
git push origin feature/your-feature
```

CI will automatically re-run.

## Architecture Guidelines

PulseWatch follows **Clean Architecture** and **Domain-Driven Design** principles.

### Layered Structure

```
pulsewatch/
├── domain/           # Business logic (pure Python)
│   ├── entities/     # Domain entities
│   ├── value_objects/# Value objects
│   └── repositories/ # Repository interfaces
├── application/      # Use cases
│   └── use_cases/    # Application services
├── infrastructure/   # External concerns
│   ├── repositories/ # Repository implementations
│   ├── db/          # Database models
│   └── external/    # External service integrations
└── interface/       # Controllers, serializers
    ├── api/         # REST API
    └── cli/         # CLI commands
```

### Key Principles

1. **Domain Independence**: Domain layer has no external dependencies
2. **Dependency Inversion**: Dependencies point inward
3. **Single Responsibility**: Each module has one reason to change
4. **Interface Segregation**: Small, focused interfaces
5. **Bounded Contexts**: Clear boundaries between subdomains

### Example: Adding a New Feature

```python
# 1. Domain layer (domain/entities/notification.py)
@dataclass
class Notification:
    id: NotificationId
    user_id: UserId
    message: str
    sent_at: datetime | None = None

    def mark_as_sent(self) -> None:
        if self.sent_at:
            raise AlreadySentError()
        self.sent_at = datetime.now(UTC)

# 2. Application layer (application/use_cases/send_notification.py)
class SendNotificationUseCase:
    def __init__(self, repo: NotificationRepository):
        self.repo = repo

    def execute(self, user_id: UserId, message: str) -> Notification:
        notification = Notification(id=NotificationId(), user_id=user_id, message=message)
        notification.mark_as_sent()
        self.repo.save(notification)
        return notification

# 3. Infrastructure layer (infrastructure/repositories/notification_repository.py)
class DjangoNotificationRepository(NotificationRepository):
    def save(self, notification: Notification) -> None:
        # Django ORM implementation
        pass

# 4. Interface layer (interface/api/views.py)
class NotificationViewSet(viewsets.ViewSet):
    def create(self, request):
        use_case = SendNotificationUseCase(DjangoNotificationRepository())
        notification = use_case.execute(user_id=request.user.id, message=request.data['message'])
        return Response({"id": str(notification.id)})
```

## Common Tasks

### Adding a New Dependency

```bash
# Add to requirements/prod.txt or requirements/dev.txt
echo "new-package==1.0.0" >> requirements/prod.txt

# Install
pip install -r requirements/dev.txt

# Update lockfile (if using pip-tools)
pip-compile requirements/prod.in
```

### Creating a New Migration

```bash
# Generate migration
python manage.py makemigrations

# Apply migration
python manage.py migrate

# Test migration is reversible
python manage.py migrate app_name zero
python manage.py migrate
```

### Adding a New App

```bash
# Create app
python manage.py startapp new_app apps/new_app

# Add to INSTALLED_APPS in core/settings/base.py
INSTALLED_APPS = [
    ...
    'apps.new_app',
]
```

### Updating Documentation

```bash
# Update relevant files
# - README.md for user-facing features
# - docs/*.md for technical documentation
# - Docstrings for API documentation

# Check links work
make check-links  # If available
```

### Running Makefile Commands

```bash
make help              # Show all available commands

# Development
make run               # Run development server
make shell             # Open Django shell
make dbshell           # Open database shell

# Docker
make docker-up         # Start Docker services
make docker-down       # Stop Docker services
make docker-logs       # View logs
make docker-shell      # Shell into web container

# Quality
make format            # Auto-format code
make lint              # Check code quality
make test              # Run tests
make check             # Run lint + test

# Database
make migrate           # Run migrations
make makemigrations    # Create new migrations

# Cleanup
make clean             # Remove generated files
```

## Getting Help

### Resources

- **Documentation**: `docs/` directory
- **Architecture**: `.github/instructions/` directory
- **API Specs**: `specs/001-project-bootstrap/contracts/`
- **CI/CD**: `.github/workflows/README.md`

### Support Channels

- Create an issue on GitHub
- Check existing issues and discussions
- Review closed issues for similar problems

### Debugging Tips

1. **Use Django debug toolbar** (dev environment)
2. **Check logs**: `docker-compose logs -f`
3. **Use pytest with verbose**: `pytest -vv`
4. **Enable debug logging**: Set `LOG_LEVEL=DEBUG` in `.env`

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

**Thank you for contributing to PulseWatch!** 🎉
