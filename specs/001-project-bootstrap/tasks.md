# Tasks: Project Bootstrap

**Input**: Design documents from `/specs/001-project-bootstrap/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: This feature specification does NOT explicitly request TDD or test generation. Tasks focus on infrastructure setup and verification. Integration tests for health endpoints are included as they validate the feature's success criteria.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Create foundational project structure and configuration files

- [X] T001 Create Django project structure with manage.py and pulsewatch/ package
- [X] T002 Create directory structure: core/, apps/, shared/, tests/, docker/, .github/workflows/
- [X] T003 [P] Initialize requirements/ directory with base.txt, dev.txt, prod.txt
- [X] T004 [P] Create .gitignore file excluding .env, __pycache__, *.pyc, .pytest_cache, htmlcov/
- [X] T005 [P] Create .env.example template with all required and optional environment variables per data-model.md
- [X] T006 [P] Create README.md with project overview and quickstart reference
- [X] T007 [P] Create Makefile with common development commands (up, down, test, migrate, etc.)
- [X] T008 [P] Create pyproject.toml with project metadata and tool configurations
- [X] T009 [P] Create pytest.ini with test discovery settings and coverage thresholds (85%)
- [X] T010 [P] Create mypy.ini with type checking strictness settings

---

## Phase 2: Foundational Infrastructure (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Dependencies Management

- [X] T011 [P] Add Django 5.x, djangorestframework 3.x to requirements/base.txt
- [X] T012 [P] Add django-environ, mysqlclient, redis, celery to requirements/base.txt
- [X] T013 [P] Add structlog, django-prometheus to requirements/base.txt for observability
- [X] T014 [P] Add pytest, pytest-django, pytest-cov, factory_boy to requirements/dev.txt
- [X] T015 [P] Add black, flake8, isort, mypy to requirements/dev.txt
- [X] T016 [P] Add gunicorn to requirements/prod.txt

### Django Configuration

- [X] T017 Create core/settings/base.py with django-environ setup and base Django settings
- [X] T018 Create core/settings/dev.py extending base.py with DEBUG=True and development overrides
- [X] T019 [P] Create core/settings/prod.py extending base.py with production-ready security settings
- [X] T020 Configure DATABASE_URL parsing in base.py using env.db() for MySQL connection
- [X] T021 Configure REDIS_URL parsing in base.py for cache and session backend
- [X] T022 [P] Add INSTALLED_APPS configuration with rest_framework, django_prometheus
- [X] T023 [P] Configure MIDDLEWARE with django_prometheus, security, logging middlewares
- [X] T024 [P] Configure TEMPLATES with Django template engine settings
- [X] T025 [P] Configure STATIC_FILES and MEDIA settings
- [X] T026 [P] Add REST_FRAMEWORK settings with JSON renderer and authentication classes

### Logging Infrastructure

- [X] T027 Create core/middleware/logging.py implementing structlog JSON logging middleware
- [X] T028 Configure structlog processors in core/settings/base.py (timestamp, log_level, context)
- [X] T029 Add request_id generation to logging middleware for request correlation

### Metrics Infrastructure

- [X] T030 Create core/middleware/metrics.py implementing custom Prometheus metrics
- [X] T031 Register custom metrics: pulsewatch_app_info, pulsewatch_app_start_time_seconds
- [X] T032 Register health check metrics: pulsewatch_health_check_duration_seconds, pulsewatch_health_check_status

### URL Configuration

- [X] T033 Create pulsewatch/urls.py with root URL configuration
- [X] T034 Include django_prometheus URLs at /metrics path
- [X] T035 Include health check URLs at /healthz and /ready paths (prepared for Phase 3)

### Shared Components

- [X] T036 [P] Create shared/base_models.py with TimestampedModel abstract base class
- [X] T037 [P] Create core/utils/validators.py for common validation functions
- [X] T038 [P] Create core/exceptions.py with custom exception classes for DRF

### Celery Configuration

- [X] T039 Create pulsewatch/celery.py with Celery app initialization
- [X] T040 Configure Celery broker_url and result_backend from environment variables
- [X] T041 Add Celery autodiscover_tasks configuration

### WSGI/ASGI Entry Points

- [X] T042 [P] Create pulsewatch/wsgi.py for production deployment
- [X] T043 [P] Create pulsewatch/asgi.py for future WebSocket support

### Test Configuration

- [X] T044 Create tests/conftest.py with pytest-django configuration and base fixtures
- [X] T045 [P] Create tests/unit/, tests/integration/, tests/contract/ directory structure

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Local Development Environment Setup (Priority: P1) 🎯 MVP

**Goal**: Enable developers to clone, setup, and run the application locally with database connectivity and health checks in under 15 minutes

**Independent Test**: Clone repository → run setup commands → verify health endpoints return 200 OK

### Health Check Infrastructure

- [x] T046 [P] [US1] Create core/health/ package with __init__.py
- [x] T047 [P] [US1] Create core/health/checks.py with database_health_check() function
- [x] T048 [P] [US1] Create core/health/checks.py with redis_health_check() function
- [x] T049 [US1] Create core/health/views.py with healthz_view() implementing /healthz endpoint per contracts/health.yaml
- [x] T050 [US1] Create core/health/views.py with ready_view() implementing /ready endpoint per contracts/health.yaml
- [x] T051 [US1] Add health check URL routing in pulsewatch/urls.py

### Integration Tests for Health Endpoints

- [x] T052 [P] [US1] Create tests/integration/test_health.py with test_healthz_endpoint_returns_200()
- [x] T053 [P] [US1] Create tests/integration/test_health.py with test_ready_endpoint_with_healthy_dependencies()
- [x] T054 [P] [US1] Create tests/integration/test_health.py with test_ready_endpoint_with_unhealthy_database()

### Contract Tests for Health API

- [x] T055 [P] [US1] Create tests/contract/test_health_api.py validating /healthz response schema matches contracts/health.yaml
- [x] T056 [P] [US1] Create tests/contract/test_health_api.py validating /ready response schema matches contracts/health.yaml

### Database Setup

- [x] T057 [US1] Create initial Django migrations: python manage.py makemigrations
- [x] T058 [US1] Run initial Django migrations: python manage.py migrate
- [x] T059 [US1] Verify database connectivity with Django ORM query test

### Pre-commit Hooks

- [x] T060 [P] [US1] Create .pre-commit-config.yaml with black, flake8, isort, mypy hooks
- [x] T061 [US1] Document pre-commit installation in README.md: pip install pre-commit && pre-commit install

### Development Documentation

- [x] T062 [US1] Copy quickstart.md content to README.md or create docs/quickstart.md with symbolic link
- [x] T063 [US1] Document optional HTTPS setup in README.md with self-signed certificate instructions for local development
- [x] T064 [US1] Verify all Makefile commands work: make up, make down, make test, make migrate

**Checkpoint**: Local development environment is fully functional. Developers can clone, setup, and run the application successfully.

---

## Phase 4: User Story 2 - Containerized Development Environment (Priority: P2)

**Goal**: Enable running the entire application stack (web + MySQL + Redis) in Docker containers for environment parity

**Independent Test**: Run docker compose up → verify all services healthy → access health endpoints → stop containers gracefully

### Docker Configuration

- [x] T065 [P] [US2] Create docker/Dockerfile with multi-stage build for Django application
- [x] T066 [P] [US2] Create docker-compose.yml with web, db, redis services per research.md
- [x] T067 [US2] Configure web service with volume mounts for code hot-reload: ./pulsewatch:/app
- [x] T068 [US2] Configure db service with MySQL 8.x image and persistent volume: mysql_data:/var/lib/mysql
- [x] T069 [US2] Configure redis service with Redis 7.x image (ephemeral data)
- [x] T070 [P] [US2] Add healthcheck for MySQL service: mysqladmin ping
- [x] T071 [P] [US2] Add depends_on configuration: web depends on db (service_healthy) and redis (service_started)
- [x] T072 [US2] Configure custom bridge network: pulsewatch_network

### Environment Integration

- [x] T073 [US2] Create docker-compose.override.yml for local development overrides (optional)
- [x] T074 [US2] Update .env.example with Docker-specific environment variables (MYSQL_HOST=db)
- [x] T075 [US2] Document Docker commands in Makefile: make docker-up, make docker-down, make docker-logs

### Docker Testing

**Testing Guide**: See `docker/TESTING.md` for detailed step-by-step manual testing instructions.
**Automated Testing**: Run `./docker/test-docker-setup.sh` for automated validation.

- [ ] T076 [US2] Test docker compose up starts all services successfully
- [ ] T077 [US2] Test docker compose exec web python manage.py migrate runs migrations
- [ ] T078 [US2] Test docker compose down stops services gracefully without data loss
- [ ] T079 [US2] Test docker compose up after down restores database state

### Docker Documentation

- [x] T080 [US2] Add Docker setup section to README.md with prerequisites (Docker, Docker Compose)
- [x] T081 [US2] Document troubleshooting for common Docker issues (port conflicts, permission errors)

**Checkpoint**: Containerized environment is production-parity. All services run in Docker with persistent data and graceful shutdown.

---

## Phase 5: User Story 3 - Automated Quality Checks and CI/CD (Priority: P3)

**Goal**: Automate code quality enforcement and testing through GitHub Actions pipeline on every push

**Independent Test**: Push code to feature branch → verify CI pipeline runs → check quality gates pass/fail → verify PR merge blocked on failure

### CI/CD Pipeline Configuration

- [ ] T082 [P] [US3] Create .github/workflows/ci.yml with GitHub Actions workflow
- [ ] T083 [P] [US3] Configure job: lint with Python 3.12, runs black --check, flake8, isort --check, mypy
- [ ] T084 [P] [US3] Configure job: test with matrix strategy (Python 3.11, 3.12)
- [ ] T085 [US3] Add MySQL service container to test job for database integration tests
- [ ] T086 [US3] Add Redis service container to test job for cache integration tests
- [ ] T087 [P] [US3] Configure test job to run pytest with coverage: pytest --cov --cov-report=xml --cov-report=html
- [ ] T088 [P] [US3] Add coverage upload to test job: actions/upload-artifact for coverage reports
- [ ] T089 [P] [US3] Configure job: docker to build Docker image and verify no build errors

### Branch Protection Rules

- [ ] T090 [US3] Document required branch protection settings in README.md: require CI checks before merge
- [ ] T091 [US3] Document manual re-run capability: "Re-run jobs" button in GitHub Actions UI

### CI/CD Documentation

- [ ] T092 [US3] Create .github/workflows/README.md documenting pipeline structure and jobs
- [ ] T093 [US3] Add CI/CD section to main README.md with badge displaying pipeline status
- [ ] T094 [US3] Document how to run CI checks locally: make check (runs all quality tools)

### Pipeline Testing

- [ ] T095 [US3] Push test commit to feature branch and verify lint job runs
- [ ] T096 [US3] Push test commit with failing lint and verify job fails with clear error messages
- [ ] T097 [US3] Verify test job runs with matrix strategy (both Python 3.11 and 3.12)
- [ ] T098 [US3] Verify coverage report is generated and uploaded as artifact
- [ ] T099 [US3] Verify Docker build job completes successfully

**Checkpoint**: CI/CD pipeline is operational. All code quality checks run automatically on every push with clear pass/fail feedback.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and documentation that affect multiple user stories

### Documentation Polish

- [ ] T100 [P] Review and update README.md with complete setup instructions from quickstart.md
- [ ] T101 [P] Create CONTRIBUTING.md with development workflow, code style, commit conventions
- [ ] T102 [P] Create docs/ directory with architecture.md documenting Clean Architecture structure

### Configuration Review

- [ ] T103 Review .env.example and ensure all environment variables are documented with examples
- [ ] T104 Review security settings in core/settings/prod.py per security-and-owasp.instructions.md
- [ ] T105 Verify SECRET_KEY generation uses strong random defaults in .env.example

### Validation Tests

- [ ] T106 Run complete quickstart.md validation following all 10 steps
- [ ] T107 Test new developer onboarding: clone → setup → verify (simulate fresh developer)
- [ ] T108 [P] Verify all Makefile commands work: up, down, test, migrate, lint, format, etc.

### Performance Baseline

- [ ] T109 Measure health check endpoint response time (target: <500ms per success criteria)
- [ ] T110 Measure code hot-reload time (target: <3 seconds per success criteria)
- [ ] T111 Measure CI pipeline duration (target: <5 minutes per success criteria)

### Final Cleanup

- [ ] T112 [P] Remove any TODO comments or placeholder code
- [ ] T113 [P] Run black, isort on all Python files for consistent formatting
- [ ] T114 [P] Run mypy and resolve any type checking warnings
- [ ] T115 Verify all tests pass: pytest with 85%+ coverage
- [ ] T116 Create git tag: v0.1.0-bootstrap

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - **BLOCKS all user stories**
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2) completion
- **User Story 2 (Phase 4)**: Depends on Foundational (Phase 2) completion - Can run parallel with US1 if team capacity
- **User Story 3 (Phase 5)**: Depends on Foundational (Phase 2) completion - Can run parallel with US1/US2 if team capacity
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

```
Foundational (Phase 2)
├── User Story 1 (Phase 3) - Local Development Environment ✅ MVP
├── User Story 2 (Phase 4) - Containerized Environment (independent, can run parallel)
└── User Story 3 (Phase 5) - CI/CD Pipeline (independent, can run parallel)
```

- **User Story 1 (P1)**: No dependencies on other stories - Can start immediately after Foundational
- **User Story 2 (P2)**: No dependencies on US1 - Can start after Foundational (parallel with US1)
- **User Story 3 (P3)**: No dependencies on US1/US2 - Can start after Foundational (parallel with US1/US2)

### Within Each User Story

**User Story 1 (Local Development)**:
1. Health check infrastructure (T046-T051)
2. Tests for validation (T052-T056) - can run parallel
3. Database setup (T057-T059) - migrations then connectivity test
4. Pre-commit hooks (T060-T061) - can run parallel with database
5. Documentation (T062-T064) - includes HTTPS setup instructions

**User Story 2 (Containerized Environment)**:
1. Docker configuration (T065-T072) - core Dockerfile and docker-compose.yml first
2. Environment integration (T073-T075) - can run parallel with Docker config
3. Docker testing (T076-T079) - sequential validation
4. Documentation (T080-T081)

**User Story 3 (CI/CD Pipeline)**:
1. Pipeline configuration (T082-T089) - lint and test jobs can be defined in parallel
2. Branch protection documentation (T090-T091)
3. CI/CD documentation (T092-T094) - can run parallel
4. Pipeline testing (T095-T099) - sequential validation

### Parallel Opportunities

**Phase 1 (Setup)**: All tasks T001-T010 marked [P] can run in parallel (different files)

**Phase 2 (Foundational)**:
- Dependencies (T011-T016): All parallel
- Django config (T017-T026): T019, T021-T026 parallel after T017-T018
- Infrastructure (T027-T043): T027+T028, T030-T032, T036-T038, T042-T043 can run in parallel groups
- Test setup (T044-T045): Parallel

**Phase 3 (User Story 1)**:
- Health checks: T046-T048 parallel, then T049-T051 depend on checks
- Tests: T052-T056 all parallel (different test files)
- Pre-commit: T059-T060 parallel with other tasks

**Phase 4 (User Story 2)**:
- Docker files: T063-T064 parallel
- Healthchecks: T070-T071 parallel

**Phase 5 (User Story 3)**:
- Pipeline jobs: T082-T089 can define lint, test, docker jobs in parallel
- Documentation: T092-T094 parallel

**Phase 6 (Polish)**:
- Documentation: T100-T102 parallel
- Validation: T108 parallel with other validation tasks
- Cleanup: T112-T114 parallel

---

## Parallel Example: Foundational Phase

```bash
# Dependencies (all parallel):
Task T011: Add Django 5.x, djangorestframework 3.x to requirements/base.txt
Task T012: Add django-environ, mysqlclient, redis, celery to requirements/base.txt
Task T013: Add structlog, django-prometheus to requirements/base.txt
Task T014: Add pytest, pytest-django, pytest-cov to requirements/dev.txt
Task T015: Add black, flake8, isort, mypy to requirements/dev.txt
Task T016: Add gunicorn to requirements/prod.txt

# After base settings created, these can run in parallel:
Task T019: Create core/settings/prod.py
Task T022: Add INSTALLED_APPS configuration
Task T023: Configure MIDDLEWARE
Task T024: Configure TEMPLATES
Task T025: Configure STATIC_FILES and MEDIA
Task T026: Add REST_FRAMEWORK settings
```

---

## Parallel Example: User Story 1

```bash
# Health check implementation (parallel):
Task T046: Create core/health/ package
Task T047: Create database_health_check() function
Task T048: Create redis_health_check() function

# All tests can run in parallel (different files):
Task T052: Create test_healthz_endpoint_returns_200()
Task T053: Create test_ready_endpoint_with_healthy_dependencies()
Task T054: Create test_ready_endpoint_with_unhealthy_database()
Task T055: Create contract test validating /healthz schema
Task T056: Create contract test validating /ready schema

# Pre-commit and database can run in parallel:
Task T057: Run initial migrations
Task T059: Create .pre-commit-config.yaml
```

---

## Implementation Strategy

### MVP First (User Story 1 Only - Recommended)

1. **Complete Phase 1**: Setup (T001-T010) → ~2 hours
2. **Complete Phase 2**: Foundational (T011-T045) → ~1 day (CRITICAL - blocks all stories)
3. **Complete Phase 3**: User Story 1 (T046-T062) → ~4 hours
4. **STOP and VALIDATE**:
   - Run quickstart.md steps 1-9
   - Test health endpoints: curl http://localhost:8000/healthz
   - Run test suite: pytest
   - Verify pre-commit hooks: git commit
5. **Deploy/Demo if ready**: MVP is functional local development environment

**Total MVP Time Estimate**: 1.5-2 days for a single developer

---

### Incremental Delivery (All User Stories)

1. **Complete Setup + Foundational** (Phase 1-2) → Foundation ready
2. **Add User Story 1** (Phase 3) → Test independently → **MVP delivered!**
3. **Add User Story 2** (Phase 4) → Test Docker environment → Deploy
4. **Add User Story 3** (Phase 5) → Test CI/CD pipeline → Deploy
5. **Polish** (Phase 6) → Final validation → Production ready

Each story adds value without breaking previous stories.

**Total Time Estimate**: 3-4 days for a single developer (with parallel work: 2-3 days with team)

---

### Parallel Team Strategy

With 3 developers:

1. **All team members**: Complete Setup + Foundational together (Phase 1-2) → ~1.5 days
2. **Once Foundational is complete, split**:
   - **Developer A**: User Story 1 (Phase 3) → ~4 hours
   - **Developer B**: User Story 2 (Phase 4) → ~3 hours
   - **Developer C**: User Story 3 (Phase 5) → ~4 hours
3. **All team members**: Polish together (Phase 6) → ~2 hours

**Total Time with Parallel Execution**: 2 days with 3 developers

---

## Task Summary

| Phase | Task Range | Count | Estimated Time |
|-------|------------|-------|----------------|
| Phase 1: Setup | T001-T010 | 10 | 2 hours |
| Phase 2: Foundational | T011-T045 | 35 | 1 day |
| Phase 3: User Story 1 | T046-T064 | 19 | 4.5 hours |
| Phase 4: User Story 2 | T065-T081 | 17 | 3 hours |
| Phase 5: User Story 3 | T082-T099 | 18 | 4 hours |
| Phase 6: Polish | T100-T116 | 17 | 2 hours |
| **Total** | **T001-T116** | **116** | **~2-3 days** |

**Parallel Opportunities**: 45+ tasks marked [P] can run in parallel (39% of all tasks)

**MVP Scope**: Phases 1-3 only (64 tasks, ~1.5-2 days) delivers functional local development environment

---

## Validation Checklist

Before marking feature complete:

- [ ] All 116 tasks completed and checked off
- [ ] Quickstart.md successfully validated (all 10 steps work)
- [ ] Health endpoints return correct JSON schema per contracts/
- [ ] Test suite passes with 85%+ coverage
- [ ] CI/CD pipeline runs successfully on feature branch
- [ ] Pre-commit hooks prevent commits with quality issues
- [ ] Docker environment starts/stops gracefully
- [ ] README.md accurately reflects setup process
- [ ] New developer can setup in <15 minutes (success criteria SC-001)
- [ ] All metrics appear on /metrics endpoint

---

## Notes

- **[P] tasks**: Different files, no dependencies - safe to parallelize
- **[Story] labels**: Track which user story each task serves
- **Each user story is independently completable**: Can deliver US1 as MVP, then add US2 and US3 incrementally
- **Foundational phase is BLOCKING**: Must complete before any user story work begins
- **Tests validate success criteria**: Health endpoint tests ensure SC-003, integration tests ensure SC-002
- **Follow TDD where specified**: Though not mandated, health endpoint tests should be written before implementation
- **Commit frequently**: After each task or logical group
- **Validate at checkpoints**: Stop after each phase to ensure story works independently
- **Use absolute paths**: Always reference full file paths in task descriptions
