#!/usr/bin/env bash
set -euo pipefail

# Run Django makemigrations, preferably inside Docker Compose 'web' service
# Usage examples:
#   bin/makemigrations.sh                # all apps
#   bin/makemigrations.sh configuration  # specific app

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

ARGS=("$@")

# Detect if running inside a container
IN_CONTAINER=0
if [ -f "/.dockerenv" ] || [ "${DOCKERIZED:-}" = "1" ]; then
  IN_CONTAINER=1
fi

# Find docker compose command if available
compose_cmd=""
if command -v docker >/dev/null 2>&1; then
  if docker compose version >/dev/null 2>&1; then
    compose_cmd="docker compose"
  elif command -v docker-compose >/dev/null 2>&1; then
    compose_cmd="docker-compose"
  fi
fi

run_local() {
  python manage.py makemigrations "${ARGS[@]}"
}

if [ "$IN_CONTAINER" -eq 1 ]; then
  echo "Detected container environment. Running makemigrations inside container..."
  run_local
elif [ -n "$compose_cmd" ] && [ -f "docker-compose.yml" ]; then
  echo "Detected Docker Compose. Ensuring services are up..."
  $compose_cmd up -d
  echo "Running makemigrations inside the 'web' service..."
  # Using sh -lc to support argument expansion inside the container
  $compose_cmd exec web sh -lc "python manage.py makemigrations ${ARGS[*]}"
else
  echo "Docker Compose not detected. Running makemigrations locally on host..."
  run_local
fi
