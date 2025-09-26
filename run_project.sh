#!/usr/bin/env bash
set -euo pipefail

# Run the Dockerized project and ensure a superuser exists.
# - Starts (or restarts) docker compose services in the background
# - Ensures all migrations are applied
# - Creates the default superuser only if it does not already exist
#   Credentials: admin / dj-notification-pass

# Move to project root (where docker-compose.yml lives)
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

# Pick docker compose command
compose_cmd=""
if command -v docker >/dev/null 2>&1; then
  if docker compose version >/dev/null 2>&1; then
    compose_cmd="docker compose"
  elif command -v docker-compose >/dev/null 2>&1; then
    compose_cmd="docker-compose"
  fi
fi

if [ -z "$compose_cmd" ]; then
  echo "Error: Docker Compose not found. Please install Docker Desktop/Engine with Compose v2."
  exit 1
fi

echo "Starting Docker services in the background..."
$compose_cmd up -d

# Ensure migrations are applied and superuser exists by invoking the helper script.
echo "Applying migrations and ensuring superuser exists..."
bash bin/create_user.sh

# Show status and where to access the app
echo "Services are running. Access the app at: http://localhost:8000"
