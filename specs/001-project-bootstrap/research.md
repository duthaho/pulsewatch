# Research: Project Bootstrap

**Feature**: Project Bootstrap  
**Date**: 2025-10-31  
**Status**: Complete

## Overview

This document consolidates research findings for technology choices, best practices, and architectural decisions for the PulseWatch project bootstrap phase.

---

## 1. Django Project Structure for Clean Architecture

### Decision: Modular Django with apps/ and core/ separation

**Rationale**:
- **apps/** directory for future bounded contexts aligns with DDD principles
- **core/** for shared infrastructure (settings, middleware) separates technical concerns from business domains
- **shared/** for reusable domain-agnostic components (base models, validators)
- Modular settings (base.py, dev.py, prod.py) support 12-factor config management
- Structure scales from monolith to microservices if needed

**Alternatives Considered**:
- **Flat Django structure** (all apps at root): Rejected - doesn't scale for 5+ bounded contexts
- **Separate repo per bounded context**: Rejected - premature for Phase 1, can extract later if needed
- **Django startproject default**: Rejected - doesn't support Clean Architecture layering

**Best Practices**:
- Use `django-admin startapp` but reorganize into domain/application/infrastructure/interface layers
- Keep manage.py at project root for conventional Django workflow
- Use absolute imports: `from core.settings import base`

**References**:
- Django documentation: Project structure
- "Two Scoops of Django" - settings organization patterns
- Clean Architecture in Python by Robert Martin (adapted for Django)

---

## 2. Environment Configuration Management

### Decision: django-environ with .env files

**Rationale**:
- **django-environ** provides type-safe environment variable parsing
- **.env.example** template documents required variables without exposing secrets
- Supports DATABASE_URL format (12-factor compliant)
- Works seamlessly with Docker Compose environment: directives
- Native support for boolean, list, and JSON env vars

**Alternatives Considered**:
- **python-decouple**: Rejected - less Django-specific, manual URL parsing
- **python-dotenv**: Rejected - no type conversion, manual parsing overhead
- **Hardcoded settings.py per environment**: Rejected - violates 12-factor, risk of committed secrets

**Best Practices**:
- Never commit .env files (add to .gitignore)
- Provide .env.example with placeholder values and comments
- Use env.str(), env.bool(), env.int() for type safety
- Set defaults for non-sensitive development values: `env.bool('DEBUG', default=False)`

**Configuration Structure**:
```python
# core/settings/base.py
import environ
env = environ.Env()
environ.Env.read_env()  # Reads .env file if present

SECRET_KEY = env('SECRET_KEY')
DEBUG = env.bool('DEBUG', default=False)
DATABASES = {'default': env.db('DATABASE_URL')}
```

---

## 3. Docker Compose Stack for Local Development

### Decision: Multi-container setup with web + db + redis

**Rationale**:
- **web (Django)**: Hot reload with volume mounts for rapid development
- **db (MySQL 8.x)**: InnoDB engine, persistent volumes for data retention
- **redis (7.x)**: Cache and Celery broker, ephemeral data OK for dev
- **networks**: Custom bridge network for service discovery
- **healthchecks**: Container-level health checks for reliable startup order

**Alternatives Considered**:
- **SQLite for dev**: Rejected - production uses MySQL, need parity for migrations/queries
- **Docker Compose v1**: Rejected - use v2 for improved networking and profiles
- **Kubernetes locally (minikube)**: Rejected - overkill for Phase 1, adds complexity

**Best Practices**:
- Use named volumes for database persistence: `mysql_data:/var/lib/mysql`
- Mount source code as volume for hot reload: `./pulsewatch:/app`
- Define depends_on with service_healthy condition (requires healthcheck)
- Use .env file for Docker Compose variables (separate from Django .env)
- Expose ports only for debugging (3306 for MySQL client access)

**Docker Compose Structure**:
```yaml
version: '3.9'
services:
  web:
    build: .
    volumes:
      - ./pulsewatch:/app
    env_file: .env
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    ports:
      - "8000:8000"
    
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE}
    volumes:
      - mysql_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  mysql_data:
```

---

## 4. Structured Logging with structlog

### Decision: structlog with JSON output for production

**Rationale**:
- **structlog** provides structured logging with context propagation
- JSON output enables log aggregation (CloudWatch, ELK, Datadog)
- Request ID tracking for distributed tracing correlation
- Consistent log format: timestamp, level, message, context fields
- Compatible with Django logging framework

**Alternatives Considered**:
- **Standard logging module**: Rejected - lacks structured output, context binding
- **python-json-logger**: Rejected - less feature-rich than structlog
- **loguru**: Rejected - not designed for production structured logging

**Best Practices**:
- Use processors: timestamp, stack_info, log_level
- Bind context: `logger.bind(user_id=user.id, request_id=request_id)`
- Configure different renderers for dev (ConsoleRenderer with colors) vs prod (JSONRenderer)
- Add middleware to inject request_id into all logs during request lifecycle

**Configuration**:
```python
# core/settings/base.py
import structlog

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': structlog.stdlib.ProcessorFormatter,
            'processor': structlog.processors.JSONRenderer(),
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)
```

---

## 5. Prometheus Metrics Integration

### Decision: django-prometheus with /metrics endpoint

**Rationale**:
- **django-prometheus** auto-instruments Django (requests, database queries, cache)
- Exposes /metrics endpoint in Prometheus text format
- Provides RED metrics (Rate, Errors, Duration) out of the box
- Minimal configuration, drop-in middleware
- Compatible with Grafana dashboards

**Alternatives Considered**:
- **prometheus_client directly**: Rejected - requires manual instrumentation
- **OpenTelemetry metrics**: Deferred - full observability stack in Phase 7
- **statsd + Prometheus exporter**: Rejected - extra moving parts

**Best Practices**:
- Add PrometheusMiddleware to middleware stack
- Use prometheus_client counters/histograms for custom metrics
- Set reasonable histogram buckets for latency: [0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
- Secure /metrics endpoint in production (IP whitelist or auth)

**Configuration**:
```python
# core/settings/base.py
INSTALLED_APPS = [
    'django_prometheus',
    # ... other apps
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    # ... other middleware
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

# urls.py
urlpatterns = [
    path('', include('django_prometheus.urls')),  # /metrics endpoint
]
```

---

## 6. Pre-commit Hooks and Code Quality Tools

### Decision: pre-commit framework with black, flake8, isort, mypy

**Rationale**:
- **pre-commit** manages git hooks declaratively via .pre-commit-config.yaml
- **black** enforces consistent formatting (line length 100)
- **flake8** catches style violations and common errors
- **isort** organizes imports (compatible with black profile)
- **mypy** enforces type hints with strict mode
- Hooks run locally before commit and in CI

**Alternatives Considered**:
- **Manual git hooks**: Rejected - not portable across developer machines
- **pylint instead of flake8**: Rejected - too opinionated, slower
- **ruff** (all-in-one linter): Deferred - still maturing, can replace flake8+isort later

**Best Practices**:
- Run `pre-commit install` during setup to enable hooks
- Use `pre-commit run --all-files` to check entire codebase
- Configure tools in pyproject.toml (single source of truth)
- Add `pre-commit autoupdate` to dependency update workflow

**.pre-commit-config.yaml**:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.10.0
    hooks:
      - id: black
        args: [--line-length=100]
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: [--profile=black]
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
        args: [--max-line-length=100, --extend-ignore=E203]
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.6.0
    hooks:
      - id: mypy
        args: [--strict, --ignore-missing-imports]
        additional_dependencies: [django-stubs, djangorestframework-stubs]
```

---

## 7. GitHub Actions CI/CD Pipeline

### Decision: Single workflow with matrix testing and required checks

**Rationale**:
- **Matrix testing**: Test against Python 3.11 and 3.12 for compatibility
- **Required checks**: Block PR merge if linting, types, or tests fail
- **Caching**: Cache pip dependencies to speed up builds (3-5 min target)
- **Docker build**: Validate Dockerfile builds successfully
- **Branch strategy**: Run on all branches (clarified in spec)

**Alternatives Considered**:
- **CircleCI**: Rejected - GitHub Actions native integration preferred
- **Jenkins**: Rejected - requires self-hosted infrastructure
- **Separate workflows per check**: Rejected - harder to manage, slower

**Best Practices**:
- Use actions/setup-python@v4 with dependency caching
- Run linting before tests (fail fast on formatting issues)
- Upload coverage reports to artifact storage
- Set timeout-minutes to prevent hung jobs
- Use concurrency groups to cancel outdated runs

**.github/workflows/ci.yml**:
```yaml
name: CI

on:
  push:
    branches: ["**"]  # All branches
  pull_request:
    branches: [main, develop]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
          cache: 'pip'
      - run: pip install -r requirements/dev.txt
      - run: black --check .
      - run: isort --check .
      - run: flake8 .
      - run: mypy .
  
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12']
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: test
          MYSQL_DATABASE: pulsewatch_test
        options: >-
          --health-cmd="mysqladmin ping"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'
      - run: pip install -r requirements/dev.txt
      - run: pytest --cov --cov-report=xml
      - uses: codecov/codecov-action@v3
        if: matrix.python-version == '3.12'
  
  docker:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t pulsewatch:test .
```

---

## 8. Testing Strategy and Pytest Configuration

### Decision: pytest with pytest-django, pytest-cov, factory_boy

**Rationale**:
- **pytest**: More Pythonic than unittest, powerful fixtures
- **pytest-django**: Django-specific fixtures (db, client, settings)
- **pytest-cov**: Integrated coverage reporting (target: 85%)
- **factory_boy**: Fixture factories for test data generation
- **Test organization**: unit/ (pure Python), integration/ (with DB), contract/ (API)

**Alternatives Considered**:
- **Django's unittest**: Rejected - less flexible, verbose
- **nose2**: Rejected - less actively maintained than pytest
- **Manual fixtures**: Rejected - factory_boy reduces boilerplate

**Best Practices**:
- Use conftest.py for shared fixtures
- Mark tests: @pytest.mark.django_db for database access
- Use `--reuse-db` flag for faster test runs during development
- Configure parallel execution with pytest-xdist once test suite grows

**pytest.ini**:
```ini
[pytest]
DJANGO_SETTINGS_MODULE = core.settings.test
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --cov=pulsewatch
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=85
    --strict-markers
    --tb=short
markers =
    unit: Pure Python tests (no Django)
    integration: Tests with database
    contract: API endpoint tests
    slow: Slow-running tests
```

---

## 9. Makefile for Developer Experience

### Decision: Makefile with common development commands

**Rationale**:
- **Discoverability**: `make` or `make help` shows available commands
- **Consistency**: Same commands work across developer machines
- **Simplicity**: Wraps complex commands (docker-compose, pytest, migrations)
- **Documentation**: Self-documenting with ## comments

**Best Practices**:
- Use `.PHONY` for targets that aren't files
- Add help target that parses ## comments
- Include setup, run, test, lint, clean commands
- Support both local (venv) and Docker workflows

**Makefile**:
```makefile
.PHONY: help setup run test lint clean migrate

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup:  ## Initial project setup (venv, dependencies, pre-commit)
	python3.12 -m venv venv
	. venv/bin/activate && pip install -r requirements/dev.txt
	pre-commit install
	cp .env.example .env

run:  ## Run development server (Docker)
	docker-compose up

test:  ## Run test suite with coverage
	pytest --cov --cov-report=term-missing

lint:  ## Run linters (black, isort, flake8, mypy)
	black .
	isort .
	flake8 .
	mypy .

migrate:  ## Run database migrations
	python manage.py migrate

clean:  ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov

docker-build:  ## Build Docker image
	docker-compose build

docker-down:  ## Stop and remove Docker containers
	docker-compose down -v
```

---

## 10. Secure Defaults for Development Environment

### Decision: .env.example with strong random defaults, secrets gitignored

**Rationale** (from clarification session):
- Balance security and developer productivity
- Developers learn secure patterns from day one
- .env.example documents required variables without exposing secrets
- Strong random defaults for passwords (not 'admin'/'password')
- Optional HTTPS with self-signed certs (documented but not mandatory)

**Best Practices**:
- Generate random SECRET_KEY with `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`
- Use random passwords for MySQL in .env.example (e.g., 'change_me_randomly_generated_XYZ123')
- Add comments explaining each variable
- Gitignore .env and *.env files (but not .env.example)

**.env.example**:
```bash
# Django Configuration
SECRET_KEY=django-insecure-change-this-to-random-50-char-string
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_SETTINGS_MODULE=core.settings.dev

# Database Configuration (MySQL)
MYSQL_HOST=db
MYSQL_PORT=3306
MYSQL_USER=pulsewatch
MYSQL_PASSWORD=change_me_securely_random_password_XYZ789
MYSQL_DATABASE=pulsewatch_dev
DATABASE_URL=mysql://${MYSQL_USER}:${MYSQL_PASSWORD}@${MYSQL_HOST}:${MYSQL_PORT}/${MYSQL_DATABASE}

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Celery Configuration
CELERY_BROKER_URL=${REDIS_URL}
CELERY_RESULT_BACKEND=${REDIS_URL}

# Observability
LOG_LEVEL=INFO
PROMETHEUS_METRICS_ENABLED=True

# Security (Development)
# Set to True for production
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
```

---

## Summary

All technical decisions for Phase 1 bootstrap are resolved:

✅ **Project Structure**: Modular Django with apps/ and core/ separation  
✅ **Configuration**: django-environ with .env files  
✅ **Containerization**: Docker Compose with web + db + redis  
✅ **Logging**: structlog with JSON output  
✅ **Metrics**: django-prometheus with /metrics endpoint  
✅ **Code Quality**: pre-commit with black, flake8, isort, mypy  
✅ **CI/CD**: GitHub Actions with matrix testing and required checks  
✅ **Testing**: pytest with pytest-django, factory_boy, 85% coverage  
✅ **Developer Experience**: Makefile with common commands  
✅ **Security**: Secure defaults with .env.example and gitignored secrets

**Next Phase**: Phase 1 (Design & Contracts) - Create data-model.md, quickstart.md, and /contracts/
