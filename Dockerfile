FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==2.1.1

# Copy dependency files first for layer caching
COPY pyproject.toml poetry.lock ./

# Install dependencies (no virtualenv inside container)
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

# Install gunicorn as production server
RUN pip install --no-cache-dir gunicorn==23.0.0

# Copy application code
COPY . .

# Create required directories
RUN mkdir -p /app/logs /app/staticfiles

# Collect static files
RUN SECRET_KEY=build-placeholder \
    STATIC_ROOT=/app/staticfiles \
    python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "tallinnstartups.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--timeout", "120"]
