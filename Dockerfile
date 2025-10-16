# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install setuptools first
RUN pip install --upgrade pip setuptools wheel

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create directories for static and media files
RUN mkdir -p /app/staticfiles
RUN mkdir -p /app/media

# Set environment variables for Django
ENV DJANGO_SETTINGS_MODULE=CVBOOK.settings

# Collect static files (skip if migrations fail)
RUN python manage.py collectstatic --noinput || echo "Static files collection failed, continuing..."

# Expose port
EXPOSE $PORT

# Run the application with debugging
CMD python manage.py check && python manage.py migrate && gunicorn CVBOOK.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120