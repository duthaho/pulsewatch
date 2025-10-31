# 🚀 PulseWatch Quick Start Guide

**Last Updated**: 2025-10-31  
**Target Audience**: New developers setting up local development environment  
**Time to Complete**: 15-20 minutes

---

## Prerequisites

Before you begin, ensure you have the following installed:

| Tool | Minimum Version | Installation |
|------|-----------------|--------------|
| **Python** | 3.11+ | [python.org](https://python.org) or `pyenv install 3.12` |
| **Docker** | 20.10+ | [docker.com/get-docker](https://docs.docker.com/get-docker/) |
| **Docker Compose** | 2.0+ | Included with Docker Desktop |
| **Git** | 2.30+ | [git-scm.com](https://git-scm.com/) |
| **Make** (optional) | Any | `sudo apt install make` or `brew install make` |

**Verify installations**:

```bash
python --version       # Python 3.12.0 or higher
docker --version       # Docker version 24.0.0 or higher
docker compose version # Docker Compose version v2.20.0 or higher
git --version          # git version 2.40.0 or higher
```

---

## Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/your-org/pulsewatch.git
cd pulsewatch

# Checkout the main branch
git checkout main
```

---

## Step 2: Environment Configuration

Create environment file from template:

```bash
# Copy the example environment file
cp .env.example .env
```

**Edit `.env`** with your preferred editor and review the default values:

```bash
# Default .env contents (most values work out-of-the-box)
DEBUG=True
SECRET_KEY=django-insecure-CHANGE-THIS-IN-PRODUCTION-abc123def456ghi789jkl
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (matches docker-compose.yml)
DATABASE_URL=mysql://pulsewatch:dev_password@db:3306/pulsewatch_dev
MYSQL_HOST=db
MYSQL_PORT=3306
MYSQL_USER=pulsewatch
MYSQL_PASSWORD=dev_password
MYSQL_DATABASE=pulsewatch_dev

# Redis
REDIS_URL=redis://redis:6379/0

# Django Settings
DJANGO_SETTINGS_MODULE=core.settings.dev
LOG_LEVEL=DEBUG

# Observability
PROMETHEUS_METRICS_ENABLED=True

# Security (development defaults - DO NOT use in production)
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
```

⚠️ **Important**: The default `SECRET_KEY` is intentionally insecure for local development. **Never commit your production `.env` file.**

---

## Step 3: Start Services with Docker Compose

PulseWatch uses Docker Compose to orchestrate multiple services:
- **web**: Django application server
- **db**: MySQL 8.x database
- **redis**: Redis cache/session store

### Option A: Using Make (Recommended)

```bash
# Start all services in detached mode
make up

# View logs
make logs

# Stop services
make down
```

### Option B: Using Docker Compose directly

```bash
# Start services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

**Wait for services to start** (30-60 seconds for first-time setup):

```bash
# Check service health
docker compose ps

# You should see:
# NAME                    STATUS
# pulsewatch-web-1        Up (healthy)
# pulsewatch-db-1         Up (healthy)
# pulsewatch-redis-1      Up
```

---

## Step 4: Run Database Migrations

Once services are running, apply database migrations:

```bash
# Option A: Using Make
make migrate

# Option B: Using Docker Compose
docker compose exec web python manage.py migrate
```

**Expected output**:
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
  Applying sessions.0001_initial... OK
```

---

## Step 5: Create Superuser (Optional)

Create an admin user to access Django admin:

```bash
# Interactive prompt
docker compose exec web python manage.py createsuperuser

# Follow prompts:
# Username: admin
# Email: admin@pulsewatch.io
# Password: <your-secure-password>
# Password (again): <your-secure-password>
```

---

## Step 6: Verify Installation

### 6.1 Health Checks

Test the application health endpoints:

```bash
# Liveness probe (basic process health)
curl http://localhost:8000/healthz

# Expected response:
# {"status":"healthy","timestamp":"2025-10-31T10:30:00.123456Z","version":"0.1.0"}

# Readiness probe (dependency checks)
curl http://localhost:8000/ready

# Expected response:
# {
#   "status":"ready",
#   "timestamp":"2025-10-31T10:30:00.123456Z",
#   "version":"0.1.0",
#   "checks":{
#     "database":{"status":"healthy","latency_ms":5.23,"message":"MySQL connection successful"},
#     "redis":{"status":"healthy","latency_ms":1.45,"message":"Redis connection successful"}
#   }
# }
```

### 6.2 Prometheus Metrics

Verify metrics endpoint:

```bash
# Fetch Prometheus metrics
curl http://localhost:8000/metrics

# You should see metrics like:
# django_http_requests_total_by_method{method="GET"} 150
# pulsewatch_app_info{version="0.1.0"} 1
# pulsewatch_health_check_status{check_name="database"} 1
```

### 6.3 Django Admin

Open your browser and navigate to:

```
http://localhost:8000/admin/
```

Log in with the superuser credentials you created in Step 5.

### 6.4 Run Tests

Execute the test suite to ensure everything is working:

```bash
# Option A: Using Make
make test

# Option B: Using Docker Compose
docker compose exec web pytest

# Expected output:
# ============================= test session starts ==============================
# collected 25 items
#
# tests/unit/core/test_health.py ........                                   [ 32%]
# tests/integration/test_health_endpoints.py .....                          [ 52%]
# ...
# ============================= 25 passed in 2.45s ===============================
```

---

## Step 7: Development Workflow

### Hot Reload

The `web` service has code hot-reload enabled. Edit Python files and see changes immediately:

```bash
# Watch logs for reload messages
docker compose logs -f web
```

### Run Management Commands

```bash
# Shell into the web container
docker compose exec web bash

# Now you can run Django commands:
python manage.py makemigrations
python manage.py migrate
python manage.py shell
python manage.py test
```

### Access Database Shell

```bash
# MySQL shell
docker compose exec db mysql -u pulsewatch -pdev_password pulsewatch_dev

# Example query:
# mysql> SHOW TABLES;
# mysql> SELECT * FROM django_migrations;
# mysql> EXIT;
```

### Access Redis CLI

```bash
# Redis CLI
docker compose exec redis redis-cli

# Example commands:
# 127.0.0.1:6379> PING
# PONG
# 127.0.0.1:6379> KEYS *
# 127.0.0.1:6379> EXIT
```

---

## Step 8: Code Quality Tools

### Pre-commit Hooks (Recommended)

Install pre-commit hooks to automatically check code before commits:

```bash
# Install pre-commit (once per developer machine)
pip install pre-commit

# Install hooks from .pre-commit-config.yaml
pre-commit install

# Manually run hooks on all files (optional)
pre-commit run --all-files
```

**Hooks configured**:
- ✅ **black**: Code formatting
- ✅ **flake8**: Linting
- ✅ **isort**: Import sorting
- ✅ **mypy**: Type checking

### Manual Code Quality Checks

```bash
# Format code with black
make format
# OR: docker compose exec web black .

# Lint with flake8
make lint
# OR: docker compose exec web flake8

# Type check with mypy
make typecheck
# OR: docker compose exec web mypy .

# Run all checks
make check
```

---

## Step 9: Running Tests with Coverage

```bash
# Run tests with coverage report
make test-cov
# OR: docker compose exec web pytest --cov=pulsewatch --cov-report=html --cov-report=term

# Open coverage report in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

**Coverage Requirements**:
- Minimum: 85% overall coverage
- Tests must pass before merging PRs

---

## Step 10: Stopping and Cleaning Up

### Stop Services

```bash
# Stop services (keep volumes)
make down
# OR: docker compose down

# Stop services and remove volumes (clean slate)
docker compose down -v
```

### Remove All Data

```bash
# Remove containers, volumes, and images
docker compose down -v --rmi all

# Remove dangling images
docker image prune -f
```

---

## Troubleshooting

### Issue: Port 8000 already in use

**Solution**: Stop the conflicting process or change the port in `docker-compose.yml`:

```yaml
services:
  web:
    ports:
      - "8001:8000"  # Change host port to 8001
```

### Issue: Database connection refused

**Symptoms**: Health checks fail with `Can't connect to MySQL server`

**Solution**:
1. Check MySQL container is running: `docker compose ps`
2. Wait for MySQL to initialize (first startup takes 30-60s)
3. Check MySQL logs: `docker compose logs db`
4. Verify `DATABASE_URL` in `.env` matches `docker-compose.yml`

### Issue: Permission denied errors

**Solution** (Linux):

```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Rebuild containers
docker compose down
docker compose up --build -d
```

### Issue: Tests failing

**Solution**:
1. Ensure migrations are applied: `make migrate`
2. Check test database configuration in `core/settings/test.py`
3. Run tests with verbose output: `docker compose exec web pytest -v`

### Issue: Pre-commit hooks failing

**Solution**:

```bash
# Update pre-commit hooks
pre-commit autoupdate

# Clear cache and re-run
pre-commit clean
pre-commit run --all-files
```

---

## Next Steps

Now that your development environment is set up:

1. **Explore the codebase**:
   - `pulsewatch/core/`: Core application settings and health checks
   - `tests/`: Unit and integration tests
   - `.github/instructions/`: Development guidelines

2. **Read the documentation**:
   - [Architecture Guide](../../.github/instructions/clean-architecture.instructions.md)
   - [Coding Style Guide](../../.github/instructions/coding-style-python.instructions.md)
   - [Testing Guide](../../.github/instructions/unit-and-integration-tests.instructions.md)

3. **Create a feature branch**:
   ```bash
   git checkout -b feature/my-awesome-feature
   ```

4. **Make your first change** and run tests:
   ```bash
   # Edit code
   make test
   make check
   git add .
   git commit -m "feat: add my awesome feature"
   git push origin feature/my-awesome-feature
   ```

5. **Open a Pull Request** following [Conventional Commits](../../.github/instructions/conventional-commits.instructions.md)

---

## Useful Commands Reference

| Command | Description |
|---------|-------------|
| `make up` | Start all services |
| `make down` | Stop all services |
| `make logs` | View service logs |
| `make shell` | Django shell |
| `make bash` | Bash shell in web container |
| `make test` | Run tests |
| `make test-cov` | Run tests with coverage |
| `make migrate` | Run database migrations |
| `make makemigrations` | Create new migrations |
| `make format` | Format code with black |
| `make lint` | Lint code with flake8 |
| `make typecheck` | Type check with mypy |
| `make check` | Run all quality checks |
| `make clean` | Remove all containers and volumes |

---

## Getting Help

- **Internal Documentation**: Check `.github/instructions/` for detailed guides
- **Django Docs**: [docs.djangoproject.com](https://docs.djangoproject.com/)
- **Docker Docs**: [docs.docker.com](https://docs.docker.com/)
- **Team Chat**: Slack #pulsewatch-dev channel

---

**Happy Coding! 🎉**
