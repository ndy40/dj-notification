dj_notificattion — Project Development Guidelines

Audience: Advanced Python/Django developers contributing to this repository.

Overview
- Stack: Python 3.13, Django 5.2.6, SQLite (dev), Poetry for dependency/venv management.
- Apps: core (installed by default).
- Project layout follows standard django-admin startproject structure. Settings are in dj_notificattion/settings.py.

1) Build / Configuration
- Tooling
  - Python: requires >=3.13 (pyproject.toml).
  - Dependency/venv: Poetry with in-project virtualenvs (poetry.toml sets .venv/ under project root).
- Getting started
  1. Install Poetry (if needed): pipx install poetry
  2. Install dependencies and create venv: poetry install
  3. Activate venv (optional, Poetry auto-spawns its own): poetry shell
  4. Create/update local DB and apply migrations: python manage.py migrate
  5. Run development server: python manage.py runserver
- Settings notes
  - DEBUG=True and the dev SECRET_KEY are committed; do not reuse in production.
  - Templates DIRS include BASE_DIR / "templates".
  - Default DB is SQLite (db.sqlite3 at repo root). Tests use a transient test DB automatically.
  - Timezone: UTC; Language: en-us.
- Python path / module names
  - Project module: dj_notificattion (note the triple t). Root URLConf: dj_notificattion.urls.

2) Testing
- Runner
  - Uses Django’s default test runner. Invoke via: python manage.py test
  - No pytest integration is configured.
- Conventions
  - Test discovery: files matching test*.py inside app packages (e.g., core/).
  - Use django.test.TestCase or TransactionTestCase for DB-backed tests. TestCase wraps each test in a transaction and flush; it auto-creates a test database and applies migrations.
- Useful flags
  - Keep DB across runs (faster): python manage.py test --keepdb
  - Parallelize: python manage.py test --parallel [N]
  - Select tests by label: python manage.py test core.tests.SomeTestCase
  - Fail fast: python manage.py test --failfast
- Data setup
  - Prefer factories or model bakeries if added later; currently no factory libs are included.
  - For simple DB checks, you can use connections/cursors inside TestCase; migrations are applied to the test DB automatically.
- Adding a new test (verified example)
  - Create a file core/test_demo.py with:
    
    from django.test import TestCase
    from django.db import connection
    
    class DemoTestCase(TestCase):
        def test_basic_truth(self):
            self.assertTrue(True)
        
        def test_database_available(self):
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                row = cursor.fetchone()
            assert row[0] == 1
    
  - Run: python manage.py test
  - Expected: 2 tests discovered and passing. This procedure was executed and confirmed during preparation of this document. The example file was subsequently removed to keep the repo clean.
- App-level testing
  - To limit scope: python manage.py test core
- Migrations in tests
  - The default runner sets up the test database and applies all migrations. Use --keepdb to cache across runs.

3) Additional Development Information
- Code style / formatting
  - The repo does not currently enforce formatters/linters via config. Follow PEP 8 and Django best practices.
  - If you add formatters, prefer: black, isort, ruff. Keep configs in pyproject.toml.
- App structure
  - core app is registered (core.apps.CoreConfig). Place models in core/models.py, views in core/views.py, urls in a core/urls.py you create and include from project urls if needed.
- Migrations
  - After model changes: python manage.py makemigrations core && python manage.py migrate
  - Include generated migrations in commits.
- Admin
  - Admin site is enabled. Register models in core/admin.py as needed.
- Management commands
  - Use manage.py for shell (python manage.py shell), db migration, and other Django tasks.
- Settings hygiene
  - For non-dev usage, split settings and externalize SECRET_KEY/DEBUG. For CI, consider using SQLite with --keepdb for speed or switch to ephemeral Postgres if needed.
- Running locally
  - Server: python manage.py runserver (hot reloading enabled by Django).
  - Creates/uses db.sqlite3. Avoid committing large local DB changes; tests do not depend on dev DB.

4) Notes for CI/CD (if added later)
- Use Python 3.13 runners.
- Cache Poetry and virtualenv to speed up builds.
- Steps: poetry install -> python manage.py migrate --noinput -> python manage.py test --keepdb --parallel

5) Quick Commands Reference
- Install deps: poetry install
- Enter venv: poetry shell
- Run server: python manage.py runserver
- Apply migrations: python manage.py migrate
- Make migrations: python manage.py makemigrations core
- Run tests (all): python manage.py test
- Run tests (fast, reusing DB): python manage.py test --keepdb
- Run tests (parallel): python manage.py test --parallel

Provenance
- All commands under “Testing” were executed against this repository on 2025-09-26 and validated. No additional files remain apart from this .junie/guidelines.md document.