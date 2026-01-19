FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    python3-dev \
    musl-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy Django project
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    django>=6.0.1 \
    djangorestframework>=3.16.1 \
    python-dotenv>=1.0.0 \
    pillow>=11.1.0 \
    requests>=2.32.3 \
    django-cors-headers>=4.9.0 \
    pillow-heif>=1.1.1 \
    psycopg[binary]>=3.1.0 \
    gunicorn>=21.2.0

# Collect static files
RUN DJANGO_ENV=production python manage.py collectstatic --noinput --clear || true

# Expose port
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "4", "--timeout", "120", "speed_champion.wsgi:application"]
