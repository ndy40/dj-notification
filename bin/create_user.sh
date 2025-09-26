#!/usr/bin/env bash
set -euo pipefail

# Create or update a Django superuser with fixed credentials
# username: admin
# password: dj-notification-pass
# email: admin@example.com

# Ensure we run from the project root (directory that contains manage.py)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Reusable python snippet to create the superuser only if it does not exist
PY_SNIPPET=$(cat <<'PY'
from django.contrib.auth import get_user_model
from django.db import IntegrityError
User = get_user_model()
username = 'admin'
password = 'dj-notification-pass'
email = 'admin@example.com'
try:
    User.objects.get(username=username)
    print('Superuser already exists; no changes made')
except User.DoesNotExist:
    User.objects.create_superuser(username=username, email=email, password=password)
    print('Superuser created')
PY
)

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

# Helper to run the migration + user creation inside Django env
run_django_commands() {
  python manage.py migrate --noinput
  python manage.py shell -c "$PY_SNIPPET"
}

if [ "$IN_CONTAINER" -eq 1 ]; then
  echo "Detected container environment. Running inside container..."
  run_django_commands
elif [ -n "$compose_cmd" ] && [ -f "docker-compose.yml" ]; then
  echo "Detected Docker Compose. Ensuring services are up..."
  $compose_cmd up -d
  echo "Running management commands inside the 'web' service..."
  $compose_cmd exec web sh -lc "python manage.py migrate --noinput && python manage.py shell -c \"$PY_SNIPPET\""
else
  echo "Docker Compose not detected. Running locally on host..."
  run_django_commands
fi

echo "Done. Django superuser 'admin' is ready with the specified password."
