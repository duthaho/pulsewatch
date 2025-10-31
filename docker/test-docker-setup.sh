#!/bin/bash
# Docker validation script for Phase 4 testing
# Tests T076-T079: Docker Compose setup validation

set -e

echo "🐳 Starting Docker Compose validation tests..."
echo "================================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
PASSED=0
FAILED=0

# Helper functions
pass_test() {
    echo -e "${GREEN}✓ PASS:${NC} $1"
    ((PASSED++))
}

fail_test() {
    echo -e "${RED}✗ FAIL:${NC} $1"
    ((FAILED++))
}

info() {
    echo -e "${YELLOW}ℹ INFO:${NC} $1"
}

# Cleanup function
cleanup() {
    echo ""
    echo "🧹 Cleaning up..."
    docker-compose down -v > /dev/null 2>&1 || true
}

# Set trap to cleanup on exit
trap cleanup EXIT

echo ""
echo "📋 Test T076: docker compose up starts all services successfully"
echo "----------------------------------------------------------------"

info "Starting services with docker-compose up -d..."
if docker-compose up -d; then
    pass_test "Docker Compose started successfully"
else
    fail_test "Docker Compose failed to start"
    exit 1
fi

# Wait for services to be healthy
info "Waiting for services to be healthy (max 60 seconds)..."
TIMEOUT=60
ELAPSED=0
while [ $ELAPSED -lt $TIMEOUT ]; do
    WEB_HEALTHY=$(docker-compose ps web | grep "healthy" || echo "")
    DB_HEALTHY=$(docker-compose ps db | grep "healthy" || echo "")
    
    if [ -n "$WEB_HEALTHY" ] && [ -n "$DB_HEALTHY" ]; then
        pass_test "All services are healthy"
        break
    fi
    
    sleep 2
    ((ELAPSED+=2))
    
    if [ $ELAPSED -ge $TIMEOUT ]; then
        fail_test "Services did not become healthy within ${TIMEOUT}s"
        docker-compose ps
        docker-compose logs --tail=50
        exit 1
    fi
done

# Check if all containers are running
info "Verifying all containers are running..."
RUNNING_CONTAINERS=$(docker-compose ps | grep "Up" | wc -l)
if [ "$RUNNING_CONTAINERS" -ge 3 ]; then
    pass_test "All containers are running (count: $RUNNING_CONTAINERS)"
else
    fail_test "Not all containers are running (expected >= 3, got $RUNNING_CONTAINERS)"
    docker-compose ps
fi

# Test health endpoints
info "Testing health endpoints..."
sleep 5  # Give the web server a moment to fully start

if curl -f http://localhost:8000/healthz > /dev/null 2>&1; then
    pass_test "Health endpoint /healthz is accessible"
else
    fail_test "Health endpoint /healthz is not accessible"
    docker-compose logs web --tail=50
fi

if curl -f http://localhost:8000/ready > /dev/null 2>&1; then
    pass_test "Readiness endpoint /ready is accessible"
else
    fail_test "Readiness endpoint /ready is not accessible"
    docker-compose logs web --tail=50
fi

echo ""
echo "📋 Test T077: docker compose exec web python manage.py migrate runs migrations"
echo "-------------------------------------------------------------------------------"

info "Running database migrations..."
if docker-compose exec -T web python manage.py migrate --noinput; then
    pass_test "Database migrations completed successfully"
else
    fail_test "Database migrations failed"
fi

# Verify migrations were applied
info "Verifying migrations were applied..."
MIGRATION_COUNT=$(docker-compose exec -T web python manage.py showmigrations --plan | wc -l)
if [ "$MIGRATION_COUNT" -gt 0 ]; then
    pass_test "Migrations were applied (count: $MIGRATION_COUNT)"
else
    fail_test "No migrations found"
fi

echo ""
echo "📋 Test T078: docker compose down stops services gracefully without data loss"
echo "------------------------------------------------------------------------------"

# Create a test record in the database
info "Creating test data in database..."
docker-compose exec -T web python manage.py shell << 'PYTHON'
from django.contrib.auth import get_user_model
User = get_user_model()
user, created = User.objects.get_or_create(
    username='docker_test_user',
    defaults={'email': 'test@docker.local'}
)
print(f"User created: {created}, User ID: {user.id}")
PYTHON

TEST_USER_EXISTS=$(docker-compose exec -T web python manage.py shell << 'PYTHON'
from django.contrib.auth import get_user_model
User = get_user_model()
exists = User.objects.filter(username='docker_test_user').exists()
print("1" if exists else "0")
PYTHON
)

if [ "$TEST_USER_EXISTS" = "1" ]; then
    pass_test "Test user created successfully"
else
    fail_test "Failed to create test user"
fi

info "Stopping services with docker-compose down..."
if docker-compose down; then
    pass_test "Services stopped gracefully"
else
    fail_test "Services did not stop gracefully"
fi

# Verify containers are stopped
info "Verifying containers are stopped..."
RUNNING_COUNT=$(docker-compose ps | grep "Up" | wc -l || echo "0")
if [ "$RUNNING_COUNT" -eq 0 ]; then
    pass_test "All containers are stopped"
else
    fail_test "Some containers are still running (count: $RUNNING_COUNT)"
fi

echo ""
echo "📋 Test T079: docker compose up after down restores database state"
echo "--------------------------------------------------------------------"

info "Starting services again..."
if docker-compose up -d; then
    pass_test "Services restarted successfully"
else
    fail_test "Failed to restart services"
fi

# Wait for services to be ready
info "Waiting for services to be healthy again..."
ELAPSED=0
while [ $ELAPSED -lt $TIMEOUT ]; do
    WEB_HEALTHY=$(docker-compose ps web | grep "healthy" || echo "")
    DB_HEALTHY=$(docker-compose ps db | grep "healthy" || echo "")
    
    if [ -n "$WEB_HEALTHY" ] && [ -n "$DB_HEALTHY" ]; then
        pass_test "Services are healthy after restart"
        break
    fi
    
    sleep 2
    ((ELAPSED+=2))
    
    if [ $ELAPSED -ge $TIMEOUT ]; then
        fail_test "Services did not become healthy after restart"
        exit 1
    fi
done

# Verify data persisted
info "Verifying database state persisted..."
TEST_USER_PERSISTED=$(docker-compose exec -T web python manage.py shell << 'PYTHON'
from django.contrib.auth import get_user_model
User = get_user_model()
exists = User.objects.filter(username='docker_test_user').exists()
print("1" if exists else "0")
PYTHON
)

if [ "$TEST_USER_PERSISTED" = "1" ]; then
    pass_test "Database state persisted after restart"
else
    fail_test "Database state was lost after restart"
fi

# Test that we can create new data after restart
info "Testing database write after restart..."
docker-compose exec -T web python manage.py shell << 'PYTHON'
from django.contrib.auth import get_user_model
User = get_user_model()
user, created = User.objects.get_or_create(
    username='docker_test_user_2',
    defaults={'email': 'test2@docker.local'}
)
print(f"Second user created: {created}")
PYTHON

if [ $? -eq 0 ]; then
    pass_test "Database writes work after restart"
else
    fail_test "Database writes failed after restart"
fi

# Print summary
echo ""
echo "================================================"
echo "📊 Test Summary"
echo "================================================"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All Docker tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some Docker tests failed!${NC}"
    exit 1
fi
