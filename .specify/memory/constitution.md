<!--
SYNC IMPACT REPORT
==================
Version Change: Initial Constitution (0.0.0 → 1.0.0)

Modified Principles: N/A (Initial creation)

Added Sections:
  - Core Principles (7 principles)
  - Technology Stack Standards
  - Quality Gates & CI/CD
  - Governance

Removed Sections: N/A

Templates Requiring Updates:
  ✅ .specify/templates/plan-template.md (Updated: Django-specific Technical Context with PulseWatch tech stack)
  ✅ .specify/templates/spec-template.md (Verified: Aligned with clean architecture requirements)
  ✅ .specify/templates/tasks-template.md (Updated: Bounded context structure with Django layers)
  ✅ .specify/templates/checklist-template.md (Updated: 40 Django-specific compliance checks)

Follow-up TODOs: None - all critical fields populated

Commit Message: docs: establish PulseWatch constitution v1.0.0 (clean architecture + DDD for Django SaaS)
==================
-->

# PulseWatch Constitution

## Core Principles

### I. Clean Architecture (Layered Separation)

**MUST enforce strict architectural layering in every Django app (bounded context):**

- **Domain Layer** (`domain/`): Pure Python business entities, value objects, and domain events. MUST NOT import Django ORM, Django settings, or any framework code. Domain logic is framework-agnostic.
- **Application Layer** (`application/`): Use cases, services, and repository protocols (interfaces). MUST depend only on domain abstractions. Orchestrates business workflows.
- **Infrastructure Layer** (`infrastructure/`): Django ORM models, external API clients, database repositories, message queue adapters. MUST implement application layer protocols.
- **Interface Layer** (`interface/`): Django REST Framework views, serializers, URL routing, GraphQL resolvers. MUST depend on application use cases, not infrastructure directly.

**Dependency Rule**: Dependencies MUST point inward only (Interface → Application → Domain). Infrastructure implements domain contracts but domain never imports infrastructure.

**Rationale**: Enables testability, flexibility to swap frameworks, and clear separation of business rules from technical concerns.

### II. Domain-Driven Design (Bounded Contexts)

**MUST organize codebase into bounded contexts, each implemented as a Django app:**

- **Bounded Contexts**: `users`, `monitoring`, `notifications`, `team`, `billing`
- Each bounded context MUST contain: `/domain`, `/application`, `/infrastructure`, `/interface`
- **Domain Events**: MUST use domain events to decouple bounded contexts (e.g., `CheckDownDetected` event triggers notification service)
- **Ubiquitous Language**: Use business terminology in code (e.g., `Check`, `Ping`, `Grace Period`, not `Item`, `Record`, `Delay`)
- **Anti-Corruption Layer**: When integrating external services (Stripe, SendGrid), MUST wrap in adapters to translate external models to domain language

**Rationale**: Aligns code structure with business domains, reduces coupling, enables independent evolution of contexts.

### III. Test-First Development (NON-NEGOTIABLE)

**TDD is mandatory for all production code:**

1. **Write tests FIRST**: Contract tests for API endpoints, integration tests for use cases, unit tests for domain logic
2. **User approval**: Tests must reflect acceptance criteria from specs before implementation
3. **Red-Green-Refactor**: Tests MUST fail initially, then implementation makes them pass, then refactor
4. **Coverage Requirement**: Minimum 85% code coverage enforced in CI/CD (pytest-cov)
5. **Test Categories**:
   - **Unit Tests**: Domain entities and value objects (no mocks, pure logic)
   - **Integration Tests**: Use cases with test database (repository implementations)
   - **Contract Tests**: API endpoints with DRF TestClient (JSON contracts)
   - **E2E Tests**: Critical user flows (Selenium/Playwright for UI if applicable)

**Rationale**: TDD ensures correctness, prevents regressions, serves as living documentation, enables confident refactoring.

### IV. SOLID Principles & Clean Code

**MUST apply SOLID principles throughout Python codebase:**

- **Single Responsibility**: Each class/function has one reason to change (e.g., separate UserRegistrationService from EmailVerificationService)
- **Open/Closed**: Use dependency injection and protocols for extensibility without modification
- **Liskov Substitution**: Repository implementations must be substitutable (e.g., InMemoryCheckRepository for tests, DjangoCheckRepository for production)
- **Interface Segregation**: Define narrow repository protocols (e.g., CheckReader vs CheckWriter)
- **Dependency Inversion**: High-level modules (use cases) depend on abstractions (protocols), not concrete implementations

**Code Quality Standards**:

- Type hints on all public functions and class attributes (enforced by mypy)
- PEP 8 compliance (black formatter, line length 100)
- Docstrings using Google style for public APIs
- Avoid fat Django models (business logic in domain layer, not models)
- Use dataclasses or Pydantic for domain entities (not Django model instances in domain)

**Rationale**: Produces maintainable, testable, and extensible code that scales with team growth.

### V. 12-Factor App Methodology

**MUST adhere to 12-factor principles for production SaaS:**

1. **Codebase**: Single Git repository, one codebase per deployable service
2. **Dependencies**: Explicit (requirements.txt, pinned versions), isolated (virtualenv/Docker)
3. **Config**: Environment variables for secrets and environment-specific settings (django-environ), never hardcoded
4. **Backing Services**: MySQL, Redis, RabbitMQ as attached resources (URLs in env vars)
5. **Build/Release/Run**: Strict separation (Docker images, immutable releases)
6. **Processes**: Stateless Django app processes (state in MySQL/Redis, not memory)
7. **Port Binding**: Self-contained service (Gunicorn binds to PORT env var)
8. **Concurrency**: Horizontal scaling via process model (K8s HPA for web workers, Celery for background)
9. **Disposability**: Fast startup/shutdown, graceful termination (K8s readiness/liveness probes)
10. **Dev/Prod Parity**: Minimize gaps (Docker Compose for local dev, matches production stack)
11. **Logs**: Treat as event streams (structlog to stdout, aggregated by Fluentd/CloudWatch)
12. **Admin Processes**: Run as one-off processes (Django management commands)

**Rationale**: Ensures cloud-native, scalable, maintainable SaaS architecture.

### VI. Observability & Monitoring

**MUST instrument application for production debugging and performance tracking:**

- **Structured Logging**: Use structlog with JSON output (fields: timestamp, level, context, user_id, request_id)
- **Metrics**: Expose Prometheus metrics endpoint (`/metrics`) with RED metrics (Rate, Errors, Duration) for all API endpoints
- **Tracing**: Implement distributed tracing via OpenTelemetry (trace requests across Django → Celery → external APIs)
- **Health Checks**: Implement `/health` (liveness) and `/ready` (readiness) endpoints checked by Kubernetes
- **Alerts**: Define SLOs (Service Level Objectives) and alert on SLI (Service Level Indicators) breaches (e.g., p95 latency > 500ms)
- **Error Tracking**: Integrate Sentry for exception tracking and stack trace aggregation

**Required Observability Tools**:

- Structured logging: structlog
- Metrics: prometheus-client (Django middleware)
- Tracing: opentelemetry-instrumentation-django
- Dashboards: Grafana (pre-configured for Django + Celery metrics)

**Rationale**: Enables rapid incident response, performance optimization, and proactive issue detection in production.

### VII. Security-First Development

**MUST follow OWASP Top 10 and secure coding practices:**

- **Authentication**: JWT access tokens (15min expiry) + refresh tokens (7 days) via djangorestframework-simplejwt
- **Authorization**: Role-based access control (Owner, Member, Viewer) enforced at use case layer
- **Input Validation**: DRF serializers validate all inputs, reject malformed requests (400 Bad Request)
- **SQL Injection**: Use Django ORM exclusively (parameterized queries), never raw SQL with user input
- **XSS Prevention**: Django templates auto-escape by default, DRF sanitizes JSON responses
- **CSRF Protection**: Django CSRF middleware enabled for session-based endpoints
- **Secrets Management**: Use environment variables (12-factor), rotate secrets quarterly, never commit to Git
- **Dependency Scanning**: Run `safety check` and `pip-audit` in CI to detect vulnerable packages
- **HTTPS Only**: Force HTTPS in production (SECURE_SSL_REDIRECT=True), HSTS headers enabled
- **Rate Limiting**: Apply django-ratelimit on authentication endpoints (5 attempts/minute per IP)
- **Audit Logging**: Log all security events (login, logout, password reset, permission changes) with user context

**Rationale**: Protects user data, maintains trust, complies with security best practices, reduces attack surface.

## Technology Stack Standards

**Backend Framework**: Python 3.12 + Django 5.x + Django REST Framework 3.x

**Database**: MySQL 8.x (InnoDB engine) with read replicas for scaling

**Caching**: Redis 7.x for session storage, query caching, and rate limiting

**Background Jobs**: Celery 5.x with RabbitMQ 3.x as message broker

**API Documentation**: drf-spectacular (auto-generated OpenAPI 3.0 schema)

**Frontend**: Next.js 15 (React 18) for SPA, or Django templates for server-rendered pages

**Deployment**: Docker containers orchestrated by Kubernetes (AWS EKS or GKE)

**CI/CD**: GitHub Actions with automated testing, security scans, and deployment pipelines

**Monitoring**: Prometheus + Grafana + OpenTelemetry + Sentry

**Dependency Management**: pip-tools for requirements compilation, Dependabot for security updates

## Quality Gates & CI/CD

**All pull requests MUST pass these gates before merge:**

1. **Linting**: black (code formatting), isort (import sorting), flake8 (style checks) - zero violations
2. **Type Checking**: mypy with strict mode - zero type errors
3. **Security Scanning**: bandit (code security issues), safety (vulnerable dependencies) - zero high/critical findings
4. **Testing**: pytest with coverage ≥ 85% - all tests pass
5. **Database Migrations**: Django makemigrations check - no pending migrations, migrations are reversible
6. **Code Review**: Minimum 2 approvals from maintainers, all conversations resolved
7. **Performance**: No N+1 queries (django-silk in local dev), API endpoints < 500ms p95 latency

**Automated CI Pipeline (GitHub Actions)**:

- Run on every push to feature branches and PRs
- Matrix testing across Python 3.11 and 3.12
- Parallel execution of linting, type checking, and test suites
- Build Docker image on PR approval
- Auto-deploy to staging on merge to `develop` branch
- Manual approval gate for production deployment from `main` branch

**Deployment Process**:

1. Feature branch → PR → CI passes → 2 approvals → merge to `develop`
2. `develop` → auto-deploy to staging environment → smoke tests
3. `develop` → create release PR to `main` → approval → merge
4. `main` → manual approval → production deployment (blue-green or canary)
5. Post-deployment validation (health checks, metric dashboards)

## Governance

**This constitution is the supreme authority for PulseWatch development practices.**

**Amendment Process**:

1. Propose amendment via GitHub issue with rationale and impact analysis
2. Discuss with team, evaluate trade-offs and complexity justification
3. Require 75% maintainer approval for ratification
4. Update constitution version (MAJOR for breaking changes, MINOR for additions, PATCH for clarifications)
5. Propagate changes to templates (plan-template.md, spec-template.md, tasks-template.md)
6. Announce amendment to team with migration timeline

**Compliance Verification**:

- All PRs MUST include "Constitution Compliance" section in description
- Code reviews MUST verify adherence to layered architecture and bounded contexts
- Monthly architecture review meetings to assess compliance and refactor technical debt
- Quarterly dependency audits and security reviews

**Complexity Justification**:

- Any violation of constitutional principles MUST be documented in implementation plan
- Include: (1) Why complexity is unavoidable, (2) Simpler alternatives considered, (3) Mitigation plan
- Architecture Decision Records (ADRs) required for deviations affecting multiple bounded contexts

**Guidance for Developers**:

- Runtime development guidance: `.github/instructions/*.instructions.md` and `.github/copilot-instructions.md`
- Architecture diagrams and ERD: `docs/architecture/`
- API contracts and OpenAPI spec: `docs/api/`
- Bounded context boundaries: `docs/domains/bounded-contexts.md`

**Version**: 1.0.0 | **Ratified**: 2025-10-31 | **Last Amended**: 2025-10-31

