# Use Python 3.10 slim image
FROM python:3.12
# FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=3000

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

# Collect static files (don't fail if this errors)
RUN python manage.py collectstatic --noinput --clear 2>&1 || true

# Expose port
EXPOSE 3000

# Hello world test
CMD echo "Hello World"

# Run migrations and start gunicorn
CMD sh -c "python manage.py migrate --noinput && gunicorn CVBOOK.wsgi:application --bind 0.0.0.0:3000 --workers 3 --worker-class sync --timeout 120 --keep-alive 5 --access-logfile - --error-logfile - --log-level info"