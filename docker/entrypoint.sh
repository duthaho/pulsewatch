#!/bin/bash
# Docker entrypoint script for PulseWatch
# Handles database migrations and other initialization tasks

set -e

echo "🚀 Starting PulseWatch entrypoint script..."

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
python << END
import sys
import time
import os
from django.db import connections
from django.db.utils import OperationalError

max_retries = 30
retry_interval = 1

for i in range(max_retries):
    try:
        conn = connections['default']
        conn.cursor()
        print("✅ Database connection successful!")
        sys.exit(0)
    except OperationalError as e:
        if i < max_retries - 1:
            print(f"⏳ Database not ready yet (attempt {i+1}/{max_retries}). Waiting {retry_interval}s...")
            time.sleep(retry_interval)
        else:
            print(f"❌ Database connection failed after {max_retries} attempts: {e}")
            sys.exit(1)
END

# Run database migrations
echo "🔄 Running database migrations..."
python manage.py migrate --noinput

# Collect static files (for production)
if [ "$DJANGO_SETTINGS_MODULE" = "core.settings.prod" ]; then
    echo "📦 Collecting static files..."
    python manage.py collectstatic --noinput
fi

echo "✅ Entrypoint script completed successfully!"

# Execute the main command
exec "$@"
