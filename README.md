# PulseWatch

[![CI](https://github.com/duthaho/pulsewatch/actions/workflows/ci.yml/badge.svg)](https://github.com/duthaho/pulsewatch/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen.svg)](https://github.com/duthaho/pulsewatch)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Real-time Health Monitoring SaaS Platform**

PulseWatch is a multi-tenant SaaS platform for monitoring website and API endpoint health with configurable checks, intelligent alerting, and team collaboration features.

## Project Status

🚧 **Phase 1: Project Bootstrap** - Infrastructure setup and development environment

## Quick Start

See [Quick Start Guide](docs/quickstart.md) for detailed setup instructions.

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- Git
- Make (optional, for convenience commands)

### Setup (5 minutes)

```bash
# 1. Clone repository
git clone <repository-url>
cd pulsewatch

# 2. Copy environment template
cp .env.example .env

# 3. Start services with Docker
make docker-up
# OR: docker-compose up -d

# 4. Run migrations
make migrate
# OR: docker-compose exec web python manage.py migrate

# 5. Create superuser
docker-compose exec web python manage.py createsuperuser

# 6. Verify installation
curl http://localhost:8000/healthz
curl http://localhost:8000/ready
curl http://localhost:8000/metrics
```

## Development

### Local Setup (without Docker)

```bash
# 1. Create virtual environment
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements/dev.txt

# 3. Setup pre-commit hooks
pre-commit install

# 4. Configure environment
cp .env.example .env
# Edit .env: Set MYSQL_HOST=localhost, REDIS_URL=redis://localhost:6379/0

# 5. Run migrations
python manage.py migrate

# 6. Start development server
python manage.py runserver
```

### Available Commands

```bash
make help              # Show all available commands
make docker-up         # Start all services with Docker
make docker-down       # Stop Docker services
make migrate           # Run database migrations
make test              # Run test suite with coverage
make lint              # Run linters (black, isort, flake8, mypy)
make format            # Auto-format code (black, isort)
make clean             # Clean up generated files
```

## Project Structure

```
pulsewatch/
├── pulsewatch/         # Main Django package
├── core/               # Shared infrastructure (settings, middleware, health)
├── apps/               # Bounded contexts (future: users, monitoring, notifications)
├── shared/             # Reusable components
├── tests/              # Test suite (unit, integration, contract)
├── docker/             # Docker configuration
├── requirements/       # Python dependencies
└── .github/workflows/  # CI/CD pipelines
```

## Architecture

PulseWatch follows **Clean Architecture** and **Domain-Driven Design** principles:

- **Layered structure**: Domain, Application, Infrastructure, Interface
- **Bounded contexts**: Separate domains (users, monitoring, notifications, team, billing)
- **12-Factor App**: Environment-based configuration, stateless processes
- **Observability**: Structured logging (JSON) + Prometheus metrics

## Testing

```bash
# Run all tests with coverage
pytest

# Run specific test types
pytest tests/unit/                 # Unit tests only
pytest tests/integration/          # Integration tests
pytest tests/contract/             # Contract tests

# Run with coverage report
pytest --cov --cov-report=html

# View coverage report
open htmlcov/index.html
```

**Coverage target**: ≥85%

## Code Quality

Pre-commit hooks run automatically on `git commit`:

- **black**: Code formatting (line length: 100)
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **bandit**: Security checks
- **detect-secrets**: Prevent committing secrets

**Performance optimized**: Hooks only run on changed files for faster commits.

Run manually:

```bash
make lint                    # Check all
make format                  # Auto-fix formatting
make pre-commit-fast         # Quick check on staged files
make pre-commit              # Full check on all files
make pre-commit-ci           # Comprehensive CI-level check
```

**Tip**: If pre-commit is slow, see [docs/pre-commit-performance.md](docs/pre-commit-performance.md) for optimization tips.

## CI/CD Pipeline

[![CI](https://github.com/duthaho/pulsewatch/actions/workflows/ci.yml/badge.svg)](https://github.com/duthaho/pulsewatch/actions/workflows/ci.yml)

The project uses GitHub Actions for continuous integration and deployment.

### Pipeline Jobs

- **Lint**: Code formatting, import sorting, linting, type checking, security checks
- **Test**: Unit, integration, and contract tests with coverage (Python 3.11 & 3.12)
- **Docker**: Build verification and image testing
- **Security**: Dependency scanning and comprehensive pre-commit checks

### Running CI Checks Locally

Before pushing, run the same checks that CI will run:

```bash
# Quick check (recommended before every commit)
make check              # Runs lint + test

# Individual checks
make lint               # Code quality checks
make test               # Test suite with coverage
make format             # Auto-fix formatting issues

# Comprehensive CI-level check (before pushing)
make pre-commit-ci      # All hooks, all files
```

### Branch Protection

The `main` branch requires:
- ✅ All lint checks pass
- ✅ All tests pass (Python 3.11 & 3.12)
- ✅ Docker build succeeds
- ✅ Code coverage ≥80%

See [.github/workflows/README.md](.github/workflows/README.md) for detailed pipeline documentation.

## API Endpoints

### Health & Metrics

- `GET /healthz` - Liveness probe (always returns 200 if process is running)
- `GET /ready` - Readiness probe (checks database and Redis connectivity)
- `GET /metrics` - Prometheus metrics in text format

See [contracts/health.yaml](specs/001-project-bootstrap/contracts/health.yaml) for API specifications.

## Environment Variables

See [.env.example](.env.example) for all configuration options.

**Required**:
- `SECRET_KEY` - Django secret key (50+ characters)
- `DATABASE_URL` - MySQL connection string
- `REDIS_URL` - Redis connection string

**Optional**:
- `DEBUG` - Enable debug mode (default: False)
- `LOG_LEVEL` - Logging level (default: INFO)
- `PROMETHEUS_METRICS_ENABLED` - Enable /metrics endpoint (default: True)

## Docker Services

```yaml
web    - Django application (port 8000)
db     - MySQL 8.0 (port 3306)
redis  - Redis 7.x (port 6379)
```

### Useful Docker Commands

```bash
docker-compose up -d              # Start in background
docker-compose logs -f web        # View Django logs
docker-compose exec web bash      # Shell into web container
docker-compose exec db mysql -u root -p  # MySQL shell
docker-compose down -v            # Stop and remove volumes
```

## Troubleshooting

### Port conflicts
```bash
# Check if ports 8000, 3306, 6379 are in use
netstat -an | grep "8000\|3306\|6379"

# Stop conflicting services or change ports in docker-compose.yml
```

### Database connection errors
```bash
# Wait for MySQL to be ready (healthcheck)
docker-compose logs db

# Verify DATABASE_URL in .env matches docker-compose.yml
```

### Permission errors (Linux)
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
```

### Container fails to start
```bash
# Check container logs
docker-compose logs web

# Check if all containers are running
docker-compose ps

# Restart specific service
docker-compose restart web

# Rebuild containers if code changes aren't reflected
docker-compose build --no-cache
docker-compose up -d
```

### Database initialization fails
```bash
# Remove volumes and start fresh
docker-compose down -v
docker-compose up -d

# Check database logs
docker-compose logs db

# Manually run migrations
docker-compose exec web python manage.py migrate
```

### Volume mount issues (Windows)
```bash
# Ensure Docker Desktop has access to the drive
# Settings → Resources → File Sharing → Add drive

# Use WSL 2 backend for better performance
# Settings → General → Use WSL 2 based engine
```

### Out of disk space
```bash
# Clean up unused Docker resources
docker system prune -a --volumes

# Remove specific volumes
docker volume ls
docker volume rm pulsewatch_mysql_data
```

## Optional: HTTPS for Local Development

For testing HTTPS locally (e.g., testing secure cookies, SSL redirects), you can generate self-signed certificates:

### Generate Self-Signed Certificate

```bash
# Create ssl directory
mkdir -p docker/ssl

# Generate certificate (valid for 365 days)
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout docker/ssl/key.pem \
  -out docker/ssl/cert.pem \
  -days 365 \
  -subj "/CN=localhost"

# Set permissions
chmod 600 docker/ssl/key.pem
chmod 644 docker/ssl/cert.pem
```

### Configure Django for HTTPS

Update your `.env` file:

```bash
USE_HTTPS=True
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Run with HTTPS

```bash
# Install django-sslserver (dev only)
pip install django-sslserver

# Add to INSTALLED_APPS in core/settings/dev.py
# 'sslserver',

# Run with SSL
python manage.py runsslserver --certificate docker/ssl/cert.pem --key docker/ssl/key.pem
```

Your browser will warn about the self-signed certificate. Click "Advanced" → "Proceed to localhost (unsafe)" to continue.

**Note**: Self-signed certificates are for local development only. Use proper certificates from Let's Encrypt or a CA in production.

## Branch Protection Rules

### Setting Up Branch Protection

To enforce CI checks before merging to `main`:

1. Navigate to: **Settings → Branches → Add branch protection rule**

2. **Branch name pattern**: `main`

3. **Required status checks**:
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - Select required checks:
     - `Lint (Python 3.12)`
     - `Test (Python 3.11)`
     - `Test (Python 3.12)`
     - `Docker Build`
     - `CI Success`

4. **Additional settings**:
   - ✅ Require conversation resolution before merging
   - ✅ Require linear history (optional, for clean history)
   - ✅ Include administrators (enforce rules for all)

5. **Save changes**

### Re-running Failed Checks

If a CI check fails:

1. Go to **Actions** tab in GitHub
2. Click on the failed workflow run
3. Click **Re-run jobs** dropdown
4. Select:
   - **Re-run all jobs**: Retry everything
   - **Re-run failed jobs**: Only retry failures

### Testing Branch Protection

```bash
# Create a test branch
git checkout -b test/branch-protection

# Make a change that will fail lint
echo "bad_code = 'not formatted'" >> test.py
git add test.py
git commit -m "test: intentional lint failure"
git push origin test/branch-protection

# Create a pull request
# Observe that CI fails and merge is blocked

# Fix the issue
make format
git add test.py
git commit -m "fix: format code"
git push

# Observe that CI passes and merge is now allowed
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development workflow and coding standards.

## License

Proprietary - All rights reserved

## Support

For issues or questions, open a GitHub issue or contact the development team.

---

**Tech Stack**: Python 3.12 | Django 5.x | MySQL 8.x | Redis 7.x | Docker | Kubernetes
