# Docker Setup Testing Guide

This guide provides step-by-step instructions to validate the Docker Compose setup for Phase 4 (Tasks T076-T079).

## Prerequisites

- Docker Desktop installed and running
- Docker Compose V2 (included with Docker Desktop)
- Repository cloned and `.env` file configured

## Test T076: Docker Compose Starts All Services Successfully

### Steps:

1. **Start services:**
   ```bash
   cd /path/to/pulsewatch
   docker-compose up -d
   ```

2. **Verify all containers are running:**
   ```bash
   docker-compose ps
   ```
   
   Expected output:
   ```
   NAME                 STATUS              PORTS
   pulsewatch_web       Up (healthy)        0.0.0.0:8000->8000/tcp
   pulsewatch_db        Up (healthy)        0.0.0.0:3306->3306/tcp
   pulsewatch_redis     Up (healthy)        0.0.0.0:6379->6379/tcp
   ```

3. **Check service health:**
   ```bash
   # Wait for health checks to pass (may take 30-60 seconds)
   docker-compose ps
   
   # All services should show "(healthy)" status
   ```

4. **View logs to verify startup:**
   ```bash
   docker-compose logs web
   docker-compose logs db
   docker-compose logs redis
   ```

5. **Test health endpoints:**
   ```bash
   # Test liveness endpoint
   curl http://localhost:8000/healthz
   # Expected: {"status": "healthy", "timestamp": "...", "version": "0.1.0"}
   
   # Test readiness endpoint
   curl http://localhost:8000/ready
   # Expected: {"status": "ready", ...}
   ```

### ✅ Success Criteria:
- All 3 containers running
- Health checks passing (healthy status)
- Health endpoints return 200 OK
- No error messages in logs

---

## Test T077: Migrations Run Successfully

### Steps:

1. **Run database migrations:**
   ```bash
   docker-compose exec web python manage.py migrate
   ```
   
   Expected output:
   ```
   Operations to perform:
     Apply all migrations: admin, auth, contenttypes, sessions
   Running migrations:
     Applying contenttypes.0001_initial... OK
     Applying auth.0001_initial... OK
     ...
   ```

2. **Verify migrations were applied:**
   ```bash
   docker-compose exec web python manage.py showmigrations
   ```
   
   All migrations should have `[X]` checkmarks.

3. **Test Django ORM access:**
   ```bash
   docker-compose exec web python manage.py shell
   ```
   
   In the shell, run:
   ```python
   from django.contrib.auth import get_user_model
   User = get_user_model()
   print(User.objects.count())
   exit()
   ```

### ✅ Success Criteria:
- Migrations complete without errors
- All migrations marked as applied
- Django ORM can query database

---

## Test T078: Services Stop Gracefully Without Data Loss

### Steps:

1. **Create test data:**
   ```bash
   docker-compose exec web python manage.py shell
   ```
   
   In the shell:
   ```python
   from django.contrib.auth import get_user_model
   User = get_user_model()
   user = User.objects.create_user(
       username='testuser',
       email='test@example.com',
       password='testpass123'
   )
   print(f"Created user with ID: {user.id}")
   exit()
   ```

2. **Verify data exists:**
   ```bash
   docker-compose exec web python manage.py shell
   ```
   
   In the shell:
   ```python
   from django.contrib.auth import get_user_model
   User = get_user_model()
   exists = User.objects.filter(username='testuser').exists()
   print(f"User exists: {exists}")
   exit()
   ```

3. **Stop services gracefully:**
   ```bash
   docker-compose down
   ```
   
   Expected output:
   ```
   [+] Running 4/4
    ✔ Container pulsewatch_web    Removed
    ✔ Container pulsewatch_redis  Removed
    ✔ Container pulsewatch_db     Removed
    ✔ Network pulsewatch_network  Removed
   ```

4. **Verify containers are stopped:**
   ```bash
   docker-compose ps
   ```
   
   Should show no running containers or "no services" message.

5. **Verify volumes still exist:**
   ```bash
   docker volume ls | grep pulsewatch
   ```
   
   Should show `pulsewatch_mysql_data` and `pulsewatch_redis_data` volumes.

### ✅ Success Criteria:
- All containers stop cleanly (no errors)
- No containers left running
- Data volumes persist (not deleted)

---

## Test T079: Data Persists After Restart

### Steps:

1. **Restart services:**
   ```bash
   docker-compose up -d
   ```

2. **Wait for services to be healthy:**
   ```bash
   # Watch status until all show (healthy)
   watch -n 2 docker-compose ps
   # Press Ctrl+C when all healthy
   ```

3. **Verify test data persisted:**
   ```bash
   docker-compose exec web python manage.py shell
   ```
   
   In the shell:
   ```python
   from django.contrib.auth import get_user_model
   User = get_user_model()
   user = User.objects.get(username='testuser')
   print(f"User found: {user.username} ({user.email})")
   print(f"User ID: {user.id}")
   exit()
   ```

4. **Test creating new data:**
   ```bash
   docker-compose exec web python manage.py shell
   ```
   
   In the shell:
   ```python
   from django.contrib.auth import get_user_model
   User = get_user_model()
   user2 = User.objects.create_user(
       username='testuser2',
       email='test2@example.com',
       password='testpass123'
   )
   print(f"Created second user with ID: {user2.id}")
   print(f"Total users: {User.objects.count()}")
   exit()
   ```

5. **Verify both users exist:**
   ```bash
   docker-compose exec web python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(f'Total users: {User.objects.count()}')"
   ```

### ✅ Success Criteria:
- Services restart successfully
- Original test data still exists (testuser)
- Can create new data after restart (testuser2)
- Database operations work normally

---

## Cleanup After Testing

```bash
# Stop services and remove volumes
docker-compose down -v

# Verify cleanup
docker-compose ps
docker volume ls | grep pulsewatch

# If needed, manually remove volumes
docker volume rm pulsewatch_mysql_data
docker volume rm pulsewatch_redis_data
```

---

## Automated Testing

For automated validation, run the test script:

```bash
chmod +x docker/test-docker-setup.sh
./docker/test-docker-setup.sh
```

This script automatically runs all four tests (T076-T079) and reports pass/fail status.

---

## Troubleshooting

### Containers fail to start
```bash
# Check logs
docker-compose logs

# Rebuild images
docker-compose build --no-cache
docker-compose up -d
```

### Database connection errors
```bash
# Check database logs
docker-compose logs db

# Verify database is healthy
docker-compose ps db

# Wait longer for healthcheck
sleep 30
docker-compose ps
```

### Port conflicts
```bash
# Check what's using the ports
netstat -an | grep "8000\|3306\|6379"

# Change ports in docker-compose.yml or stop conflicting services
```

### Data loss after restart
```bash
# Ensure you're using `docker-compose down` without `-v` flag
# The `-v` flag removes volumes!

# Check volumes exist
docker volume ls | grep pulsewatch

# If volumes are missing, you may need to recreate test data
```

---

## Marking Tasks Complete

After successfully completing all tests:

1. Mark tasks T076-T079 as complete in `specs/001-project-bootstrap/tasks.md`
2. Commit the changes
3. Proceed to Phase 5 (CI/CD Pipeline)
