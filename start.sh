#!/bin/bash
set -e

echo "Starting CV Book deployment..."

echo "Step 1: Running migrations..."
python manage.py migrate --noinput || echo "Migrations failed, continuing..."

echo "Step 2: Collecting static files..."
python manage.py collectstatic --noinput || echo "Collectstatic failed, continuing..."

echo "Step 3: Starting Gunicorn..."
exec gunicorn CVBOOK.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 3 \
    --timeout 120 \
    --log-level info \
    --access-logfile - \
    --error-logfile -















