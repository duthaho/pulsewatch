# Data Model: Project Bootstrap

**Feature**: Project Bootstrap  
**Date**: 2025-10-31  
**Status**: Complete

## Overview

This document defines the data structures and schemas for the Project Bootstrap phase. Since this phase focuses on infrastructure setup without business logic, there are no domain entities. Instead, this document covers configuration schemas, health check responses, and metrics data formats.

---

## 1. Configuration Schema

### Environment Variables Schema

**Purpose**: Document all required and optional environment variables for application configuration.

**Required Variables**:

| Variable | Type | Description | Example | Validation |
|----------|------|-------------|---------|------------|
| `SECRET_KEY` | string | Django secret key (50+ chars) | `django-insecure-abc123...` | Length >= 50 |
| `DATABASE_URL` | string | MySQL connection URL | `mysql://user:pass@host:port/db` | Valid MySQL URL format |
| `REDIS_URL` | string | Redis connection URL | `redis://redis:6379/0` | Valid Redis URL format |
| `DJANGO_SETTINGS_MODULE` | string | Settings module path | `core.settings.dev` | Valid Python module path |

**Optional Variables**:

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DEBUG` | boolean | `False` | Enable debug mode |
| `ALLOWED_HOSTS` | comma-separated list | `localhost,127.0.0.1` | Allowed host headers |
| `LOG_LEVEL` | string | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `PROMETHEUS_METRICS_ENABLED` | boolean | `True` | Enable /metrics endpoint |
| `SECURE_SSL_REDIRECT` | boolean | `False` | Redirect HTTP to HTTPS |
| `SESSION_COOKIE_SECURE` | boolean | `False` | Require HTTPS for session cookies |
| `CSRF_COOKIE_SECURE` | boolean | `False` | Require HTTPS for CSRF cookies |
| `MYSQL_HOST` | string | `db` | MySQL hostname |
| `MYSQL_PORT` | integer | `3306` | MySQL port |
| `MYSQL_USER` | string | `pulsewatch` | MySQL username |
| `MYSQL_PASSWORD` | string | - | MySQL password |
| `MYSQL_DATABASE` | string | `pulsewatch_dev` | MySQL database name |
| `CELERY_BROKER_URL` | string | `${REDIS_URL}` | Celery broker URL |
| `CELERY_RESULT_BACKEND` | string | `${REDIS_URL}` | Celery result backend URL |

---

## 2. Health Check Response Schema

### `/healthz` Endpoint (Liveness Probe)

**Purpose**: Basic application liveness check (process is running).

**Response Format**:

```json
{
  "status": "healthy",
  "timestamp": "2025-10-31T10:30:00.123456Z",
  "version": "0.1.0"
}
```

**Fields**:

| Field | Type | Description | Possible Values |
|-------|------|-------------|-----------------|
| `status` | string | Overall health status | `healthy`, `unhealthy` |
| `timestamp` | string (ISO 8601) | Time of check | UTC timestamp |
| `version` | string (semver) | Application version | e.g., `0.1.0` |

**HTTP Status Codes**:
- `200 OK`: Service is healthy
- `503 Service Unavailable`: Service is unhealthy

---

### `/ready` Endpoint (Readiness Probe)

**Purpose**: Comprehensive readiness check (application can serve traffic).

**Response Format**:

```json
{
  "status": "ready",
  "timestamp": "2025-10-31T10:30:00.123456Z",
  "version": "0.1.0",
  "checks": {
    "database": {
      "status": "healthy",
      "latency_ms": 5.23,
      "message": "MySQL connection successful"
    },
    "redis": {
      "status": "healthy",
      "latency_ms": 1.45,
      "message": "Redis connection successful"
    }
  }
}
```

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Overall readiness status (`ready`, `not_ready`) |
| `timestamp` | string (ISO 8601) | Time of check |
| `version` | string (semver) | Application version |
| `checks` | object | Map of dependency checks |
| `checks[key].status` | string | Dependency status (`healthy`, `unhealthy`, `degraded`) |
| `checks[key].latency_ms` | float | Check execution time in milliseconds |
| `checks[key].message` | string | Human-readable status message |

**HTTP Status Codes**:
- `200 OK`: Service is ready
- `503 Service Unavailable`: Service is not ready (one or more checks failed)

**Dependency Check Keys**:
- `database`: MySQL connection and query test
- `redis`: Redis ping test
- `migrations` (future): Database migration status

---

## 3. Metrics Schema

### Prometheus Metrics Format

**Purpose**: Expose operational metrics in Prometheus text format via `/metrics` endpoint.

**Baseline Metrics** (provided by django-prometheus):

| Metric Name | Type | Description | Labels |
|-------------|------|-------------|--------|
| `django_http_requests_total_by_method` | Counter | Total HTTP requests by method | `method` (GET, POST, etc.) |
| `django_http_requests_total_by_view_transport_method` | Counter | Total requests by view and method | `view`, `method` |
| `django_http_responses_total_by_status` | Counter | Total responses by status code | `status` (200, 404, 500, etc.) |
| `django_http_request_duration_seconds` | Histogram | HTTP request latency distribution | `method`, `view` |
| `django_db_query_duration_seconds` | Histogram | Database query latency | `vendor` (mysql), `alias` (default) |
| `django_db_execute_total` | Counter | Total database queries executed | `vendor`, `alias` |
| `django_cache_get_total` | Counter | Total cache get operations | `backend` |
| `django_cache_hit_total` | Counter | Total cache hits | `backend` |

**Custom Application Metrics**:

| Metric Name | Type | Description | Labels |
|-------------|------|-------------|--------|
| `pulsewatch_app_info` | Gauge | Application information (always 1) | `version` |
| `pulsewatch_app_start_time_seconds` | Gauge | Unix timestamp of application start | - |
| `pulsewatch_health_check_duration_seconds` | Histogram | Health check execution time | `check_name` (database, redis) |
| `pulsewatch_health_check_status` | Gauge | Health check status (1=healthy, 0=unhealthy) | `check_name` |

**Example Metrics Output** (`/metrics`):

```text
# HELP django_http_requests_total_by_method Total HTTP requests by method
# TYPE django_http_requests_total_by_method counter
django_http_requests_total_by_method{method="GET"} 150
django_http_requests_total_by_method{method="POST"} 45

# HELP django_http_request_duration_seconds HTTP request latency
# TYPE django_http_request_duration_seconds histogram
django_http_request_duration_seconds_bucket{method="GET",view="health",le="0.1"} 120
django_http_request_duration_seconds_bucket{method="GET",view="health",le="0.5"} 150
django_http_request_duration_seconds_sum{method="GET",view="health"} 12.3
django_http_request_duration_seconds_count{method="GET",view="health"} 150

# HELP pulsewatch_app_info Application information
# TYPE pulsewatch_app_info gauge
pulsewatch_app_info{version="0.1.0"} 1

# HELP pulsewatch_health_check_status Health check status
# TYPE pulsewatch_health_check_status gauge
pulsewatch_health_check_status{check_name="database"} 1
pulsewatch_health_check_status{check_name="redis"} 1
```

---

## 4. Structured Log Schema

### Log Entry Format (JSON)

**Purpose**: Consistent structured logging format for all application logs.

**Required Fields**:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `timestamp` | string (ISO 8601) | Log entry time | `2025-10-31T10:30:00.123456Z` |
| `level` | string | Log level | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `logger` | string | Logger name | `pulsewatch.core.health` |
| `message` | string | Log message | `Health check completed successfully` |
| `event` | string | Event type/name | `health_check`, `database_query`, `api_request` |

**Optional Context Fields**:

| Field | Type | Description | When Present |
|-------|------|-------------|--------------|
| `request_id` | string (UUID) | Request correlation ID | During HTTP requests |
| `user_id` | string (UUID) | Authenticated user ID | When user is authenticated |
| `ip_address` | string | Client IP address | During HTTP requests |
| `method` | string | HTTP method | During HTTP requests |
| `path` | string | Request path | During HTTP requests |
| `status_code` | integer | HTTP response status | After request completion |
| `duration_ms` | float | Operation duration | For timed operations |
| `error` | string | Error message | When exception occurs |
| `stack_trace` | string | Exception stack trace | When exception occurs |

**Example Log Entries**:

```json
{
  "timestamp": "2025-10-31T10:30:00.123456Z",
  "level": "INFO",
  "logger": "pulsewatch.core.health",
  "message": "Health check completed",
  "event": "health_check",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "checks": {
    "database": "healthy",
    "redis": "healthy"
  },
  "duration_ms": 15.23
}
```

```json
{
  "timestamp": "2025-10-31T10:30:05.789012Z",
  "level": "ERROR",
  "logger": "pulsewatch.core.health",
  "message": "Database health check failed",
  "event": "health_check_failure",
  "request_id": "550e8400-e29b-41d4-a716-446655440001",
  "error": "OperationalError: (2003, \"Can't connect to MySQL server\")",
  "stack_trace": "Traceback (most recent call last):\n  File ...",
  "duration_ms": 5000.0
}
```

---

## 5. Docker Compose Configuration Schema

### Service Dependencies Graph

```
web (Django)
├── depends_on: db (service_healthy)
└── depends_on: redis (service_started)

db (MySQL)
└── healthcheck: mysqladmin ping

redis (Redis)
└── no dependencies
```

**Volume Mappings**:

| Service | Volume | Purpose |
|---------|--------|---------|
| web | `./pulsewatch:/app` | Code hot-reload |
| db | `mysql_data:/var/lib/mysql` | Persistent database storage |
| redis | (none) | Ephemeral cache data |

**Network Configuration**:
- Custom bridge network: `pulsewatch_network`
- Service discovery via service names (e.g., `db`, `redis`)

---

## 6. CI/CD Pipeline Schema

### GitHub Actions Job Dependencies

```
lint (Python 3.12)
└── runs independently

test (Python 3.11, 3.12)
├── depends_on: MySQL service
├── uploads: coverage report
└── matrix strategy

docker
└── runs independently
```

**Artifact Outputs**:

| Job | Artifact | Format | Retention |
|-----|----------|--------|-----------|
| test | Coverage report | XML (Cobertura) | 30 days |
| test | Coverage HTML | HTML bundle | 30 days |
| docker | Docker image | OCI image (not pushed) | Build-time only |

---

## Summary

Data structures defined for Project Bootstrap:

✅ **Configuration**: Environment variable schema with validation rules  
✅ **Health Checks**: /healthz and /ready response schemas  
✅ **Metrics**: Prometheus metrics format and custom application metrics  
✅ **Logging**: Structured JSON log format with required and optional fields  
✅ **Docker**: Service dependency graph and volume mappings  
✅ **CI/CD**: Pipeline job dependencies and artifact specifications

**No domain entities** in this phase (infrastructure setup only). Business domain entities will be introduced starting with Phase 2 (Users bounded context).
