# dj_notificattion

A minimal Django project configured for containerized development. This repository is intended to run via Docker so contributors and users do not need a local Python environment.

## Requirements

- Docker (Desktop on macOS/Windows, Engine on Linux) with Docker Compose v2
  - Install Docker: https://docs.docker.com/get-docker/

No local Python or Poetry setup is required for the basic workflow described below.

## Quickstart (Docker)

From the project root:

1) Start the services

   - Bring up the app and database in the background:

     docker compose up -d

   - The web service will run Django’s development server on http://localhost:8000

2) Create the Django superuser (admin)

   - Run the helper script from the host (recommended):

     bash bin/create_user.sh

   - The script will:
     - Ensure Docker Compose services are up
     - Run database migrations
     - Create or update a superuser with these credentials:
       - username: admin
       - password: dj-notification-pass

   - Alternatively, you can run the script from inside the running container:

     docker compose exec web bash -lc "bash bin/create_user.sh"

3) Access the site and admin

   - App: http://localhost:8000/
   - Admin: http://localhost:8000/admin/
   - Log in with the credentials above (admin / dj-notification-pass)

## API Docs (DRF + drf-spectacular)

Once the server is running, the OpenAPI schema and interactive docs are available at:

- Schema (YAML): http://localhost:8000/api/schema/
- Swagger UI: http://localhost:8000/api/docs/
- Redoc: http://localhost:8000/api/redoc/

## Notes

- The helper script bin/create_user.sh works in three contexts:
  - Inside the container (it will run migrations + create/update the user)
  - From the host with Docker Compose (it will exec into the `web` service)
  - From the host without Docker (it will run Django commands locally if you have Python set up)
- The development database runs in PostgreSQL via Docker; no local DB install is needed.

## Optional: Running without Docker (for contributors with Python installed)

If you prefer a local environment:

- Python 3.13 and Poetry are required
- Install dependencies:

  poetry install
- Apply migrations and run the dev server:

  python manage.py migrate
  python manage.py runserver
- Create the superuser locally using the same script:

  bash bin/create_user.sh

## Running tests with a different database/schema

You can run Django tests against a different database (and, for PostgreSQL, a specific schema) without changing your development DB. The settings module reads two environment variables when the test runner is invoked:

- DJANGO_TEST_DB_NAME — Overrides the test database name.
- DJANGO_TEST_DB_SCHEMA — For PostgreSQL only, sets the search_path so tests run in that schema (objects are created there). If not present, Django will use the default search_path.

Examples:

- SQLite in-memory (fast):

  DJANGO_TEST_DB_NAME=":memory:" python manage.py test

- PostgreSQL with custom DB and schema:

  POSTGRES_DB=appdb POSTGRES_USER=app POSTGRES_PASSWORD=secret POSTGRES_HOST=localhost \
  DJANGO_TEST_DB_NAME=test_appdb DJANGO_TEST_DB_SCHEMA=test_schema \
  python manage.py test --keepdb --parallel

Notes:
- These overrides only apply when running tests (python manage.py test). They do not affect development or production runs.
- For PostgreSQL, the schema is injected via connection options (search_path=<schema>,public).

## Troubleshooting

- If `docker compose` is not found, install or update Docker to a version that includes Compose v2 (see link above). On some systems the command may be `docker-compose`; the script supports both.
- On Windows, run commands in a Unix-like shell (e.g., Git Bash or WSL) for best compatibility with the script.
- If ports are in use, stop conflicting services or adjust port mappings in docker-compose.yml.

## Development tooling

This repo uses pre-commit with Ruff for linting/formatting and Django best-practice checks.

Install once (requires Poetry):

- poetry install
- poetry run pre-commit install
- To also run on push: poetry run pre-commit install -t pre-push

Run the hooks on all files manually:

- poetry run pre-commit run --all-files
