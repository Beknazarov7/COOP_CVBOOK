# Use Python 3.10 slim image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media/pdfs

# Collect static files
RUN python manage.py collectstatic --noinput --clear 2>&1 || true

# Expose port (Railway will override with $PORT)
EXPOSE $PORT

# Create entrypoint script
RUN echo '#!/bin/sh\n\
set -e\n\
echo "Running migrations..."\n\
python manage.py migrate --noinput\n\
echo "Starting gunicorn on port $PORT..."\n\
exec gunicorn CVBOOK.wsgi:application \\\n\
  --bind 0.0.0.0:$PORT \\\n\
  --workers 3 \\\n\
  --worker-class sync \\\n\
  --timeout 120 \\\n\
  --access-logfile - \\\n\
  --error-logfile - \\\n\
  --log-level info\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Run the entrypoint script
CMD ["/app/entrypoint.sh"]