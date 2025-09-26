# syntax=docker/dockerfile:1
FROM python:3.13-slim

# Environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.3

# Build-time args to create a non-root user matching host UID/GID
ARG APP_USER=app
ARG APP_UID=1000
ARG APP_GID=1000

WORKDIR /app

# Install system dependencies (curl for health/debug, build deps kept minimal)
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

# Copy dependency manifests first for layer caching
COPY pyproject.toml poetry.lock* ./

# Configure Poetry to install into the system (no virtualenv inside container) and install deps
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copy project source
COPY . .

# Create a non-root user and group, and set ownership of the workdir
RUN groupadd -g ${APP_GID} ${APP_USER} \
    && useradd -m -u ${APP_UID} -g ${APP_GID} -s /bin/bash ${APP_USER} \
    && chown -R ${APP_UID}:${APP_GID} /app

# Switch to non-root user for runtime
USER ${APP_UID}:${APP_GID}

EXPOSE 8000

# Default command (can be overridden by docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
