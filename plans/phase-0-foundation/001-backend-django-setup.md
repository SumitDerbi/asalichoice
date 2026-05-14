# 001 — Backend (Django) Setup

> **Phase**: phase-0-foundation  **Depends on**: 000  **Module**: --  **Est. effort**: M

## Goal

Stand up Django + DRF with split settings, split requirements, MySQL connectivity, OpenAPI schema, JWT auth wiring (no real users yet), and a single `health/` endpoint. Production-shape from day 1.

## Inputs

- [ ] 000 complete.
- [ ] Local Python 3.11 + virtualenv.
- [ ] MySQL local instance (or Docker) with a dev DB.

## Steps

1. `cd backend && python -m venv .venv && . .venv/Scripts/activate` (Windows) or `source .venv/bin/activate`.
2. Install initial packages, pin versions:
   - base: `django`, `djangorestframework`, `django-environ`, `django-cors-headers`, `djangorestframework-simplejwt`, `drf-spectacular`, `django-filter`, `mysqlclient`, `argon2-cffi`.
   - dev: `pytest`, `pytest-django`, `factory-boy`, `ruff`, `black`, `isort`, `pre-commit`, `ipython`.
   - prod: `gunicorn` (local-only; cPanel uses Passenger), `whitenoise` (optional for static).
3. Write `requirements/{base,development,production}.txt` and freeze versions.
4. `django-admin startproject config .` (project folder = `config`).
5. Refactor `config/settings.py` → `config/settings/{__init__.py,base.py,development.py,production.py}`. Use `django-environ` to read `.env`.
6. Configure: `INSTALLED_APPS` (DRF, simplejwt, drf-spectacular, corsheaders, django_filters), `MIDDLEWARE` (security order), `AUTH_PASSWORD_VALIDATORS`, `PASSWORD_HASHERS` (argon2 first), `DEFAULT_AUTO_FIELD = BigAutoField`.
7. Wire DRF defaults: `DEFAULT_AUTHENTICATION_CLASSES` (JWT), `DEFAULT_PAGINATION_CLASS`, `DEFAULT_FILTER_BACKENDS`, custom exception handler producing the envelope from `_conventions.md` §5.
8. Wire `drf-spectacular`: `SPECTACULAR_SETTINGS` with title `AsliChoice API`, version `1.0.0`. Expose `/api/v1/schema/` + `/api/v1/docs/`.
9. Add `apps/core/` app: `health` view (`GET /api/v1/health/` → `{status: ok, version, time}`), `apps/core/exceptions.py` (envelope handler), `apps/core/pagination.py`.
10. `python manage.py migrate` against local MySQL. Add `pytest.ini` / `pyproject.toml` pytest config.
11. Add `backend/Procfile` (for clarity) and a `backend/passenger_wsgi.py` stub (will be configured in 012).
12. Add `.env.example` keys: `SECRET_KEY, DEBUG, ALLOWED_HOSTS, DB_*, CORS_ALLOWED_ORIGINS, JWT_*`.
13. Commit: `feat(backend): scaffold django + drf with split settings`.

## Deliverables

- `backend/` Django project with split settings.
- Three requirements files with pinned versions.
- `apps/core/` with health endpoint.
- OpenAPI schema served at `/api/v1/schema/`.
- Custom exception envelope.
- `pytest` configured (no tests yet beyond a smoke `test_health.py`).

## Verification

### Manual
1. `python manage.py runserver` → `curl localhost:8000/api/v1/health/` returns `{"status": "ok", ...}`.
2. Visit `/api/v1/docs/` — Swagger UI renders.
3. Trigger an invalid request to confirm error envelope shape.

### Automated
- `pytest backend/tests/core/test_health.py -q` passes.
- `ruff check backend && black --check backend && isort --check-only backend` clean.

## Definition of Done

- [ ] Health endpoint live.
- [ ] OpenAPI docs live.
- [ ] All three requirements files reproducible.
- [ ] Lint + test green.
- [ ] `_state.md` advanced.

## Next step

→ [`002-frontend-react-setup.md`](./002-frontend-react-setup.md)

## Previous step

← [`000-repo-bootstrap.md`](./000-repo-bootstrap.md)
