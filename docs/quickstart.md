# PulseWatch Quick Start Guide

This guide will get you up and running with PulseWatch in under 10 minutes.

## Prerequisites

Before starting, ensure you have:

- **Python 3.12+** installed ([python.org](https://www.python.org/downloads/))
- **Git** for version control
- **Docker & Docker Compose** (optional, for full stack development)
- **Redis** (optional, for local development without Docker)

## Option 1: Quick Start with Docker (Recommended)

Best for: Full-stack development with all services

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd pulsewatch

# Copy environment configuration
cp .env.example .env
```

### Step 2: Start Services

```bash
# Start all services (Django, MySQL, Redis)
docker-compose up -d

# Wait for services to be ready (~30 seconds)
docker-compose logs -f web
# Press Ctrl+C when you see "Application startup complete"
```

### Step 3: Initialize Database

```bash
# Run database migrations
docker-compose exec web python manage.py migrate

# Create admin user
docker-compose exec web python manage.py createsuperuser
```

### Step 4: Verify Installation

```bash
# Test health endpoints
curl http://localhost:8000/healthz
# Expected: {"status": "healthy", "timestamp": "...", "version": "0.1.0"}

curl http://localhost:8000/ready
# Expected: {"status": "ready", ...}

# View metrics
curl http://localhost:8000/metrics
```

### Step 5: Access the Application

- **API**: http://localhost:8000/
- **Admin**: http://localhost:8000/admin/
- **Health**: http://localhost:8000/healthz
- **Metrics**: http://localhost:8000/metrics

**✅ You're ready to develop!**

---

## Option 2: Local Development (Without Docker)

Best for: Lightweight development, testing, or when Docker is unavailable

### Step 1: Setup Python Environment

```bash
# Clone the repository
git clone <repository-url>
cd pulsewatch

# Create virtual environment
python3.12 -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### Step 2: Install Dependencies

```bash
# Install development dependencies
pip install -r requirements/dev.txt

# Verify installation
python --version  # Should be 3.12+
pip list | grep Django  # Should show Django 5.x
```

### Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file for local development
# Change these lines:
# DATABASE_URL=sqlite:///db.sqlite3  # Use SQLite instead of MySQL
# REDIS_URL=redis://localhost:6379/0  # Or comment out if no Redis
```

**Minimal .env for local development:**
```bash
SECRET_KEY=django-insecure-dev-key-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://localhost:6379/0
LOG_LEVEL=INFO
```

### Step 4: Setup Database

```bash
# Run migrations (creates db.sqlite3)
python manage.py migrate

# Create admin user
python manage.py createsuperuser
```

### Step 5: Install Pre-commit Hooks

```bash
# Setup git hooks for code quality
pre-commit install

# Test hooks (optional)
pre-commit run --all-files
```

### Step 6: Start Development Server

```bash
# Start Django development server
python manage.py runserver

# Server will start at http://127.0.0.1:8000/
```

### Step 7: Verify Installation

Open a new terminal and test:

```bash
# Test health endpoint
curl http://localhost:8000/healthz

# Expected response:
{
  "status": "healthy",
  "timestamp": "2025-10-31T10:30:00.123456Z",
  "version": "0.1.0"
}

# Test readiness endpoint
curl http://localhost:8000/ready

# Expected response (if Redis is running):
{
  "status": "ready",
  "timestamp": "2025-10-31T10:30:00.123456Z",
  "version": "0.1.0",
  "checks": {
    "database": {"status": "healthy", "latency_ms": 5.23, "message": "..."},
    "redis": {"status": "healthy", "latency_ms": 1.45, "message": "..."}
  }
}
```

**✅ You're ready to develop!**

---

## Running Tests

```bash
# Run all tests with coverage
pytest

# Run specific test types
pytest tests/unit/                 # Unit tests only
pytest tests/integration/          # Integration tests
pytest -m "not slow"               # Skip slow tests

# Run with coverage report
pytest --cov --cov-report=html
open htmlcov/index.html            # View coverage report
```

---

## Common Commands

### Development Server

```bash
# Start server
python manage.py runserver

# Start on different port
python manage.py runserver 8080

# Start with specific settings
DJANGO_SETTINGS_MODULE=core.settings.prod python manage.py runserver
```

### Database

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Open Django shell
python manage.py shell
```

### Code Quality

```bash
# Format code
black .
isort .

# Check linting
flake8
mypy .

# Or use Makefile shortcuts:
make format     # Format code
make lint       # Check all linters
```

### Docker Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f web

# Stop services
docker-compose down

# Rebuild images
docker-compose build

# Shell into container
docker-compose exec web bash

# Run Django commands
docker-compose exec web python manage.py <command>
```

---

## Troubleshooting

### Issue: Port 8000 already in use

```bash
# Find process using port 8000
# On macOS/Linux:
lsof -i :8000
# On Windows:
netstat -ano | findstr :8000

# Kill the process or use different port
python manage.py runserver 8080
```

### Issue: Database connection error

**With Docker:**
```bash
# Check if database is running
docker-compose ps

# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

**Without Docker (SQLite):**
```bash
# Verify DATABASE_URL in .env
cat .env | grep DATABASE_URL
# Should be: DATABASE_URL=sqlite:///db.sqlite3

# Delete and recreate database
rm db.sqlite3
python manage.py migrate
```

### Issue: Redis connection error

**Option 1: Install Redis locally**
```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis

# Windows
# Download from https://github.com/microsoftarchive/redis/releases
```

**Option 2: Use Docker for Redis only**
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

**Option 3: Disable Redis (testing only)**

Edit `core/settings/dev.py`:
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
```

### Issue: Pre-commit hooks fail

```bash
# Update hooks
pre-commit autoupdate

# Clear cache and reinstall
pre-commit clean
pre-commit install

# Skip hooks temporarily (not recommended)
git commit --no-verify
```

### Issue: Python version mismatch

```bash
# Check Python version
python --version

# Use specific Python version
python3.12 -m venv .venv
```

---

## Next Steps

Now that you're set up, check out:

1. **[Architecture Overview](architecture.md)** - Understand the system design
2. **[API Documentation](api.md)** - Explore available endpoints
3. **[Contributing Guide](../CONTRIBUTING.md)** - Learn the development workflow
4. **[Testing Guide](testing.md)** - Write and run tests

---

## Need Help?

- 📖 **Documentation**: Check the `docs/` directory
- 🐛 **Issues**: Open a GitHub issue
- 💬 **Chat**: Contact the development team

---

**Happy coding! 🚀**
