# Execution State Tracker

> **Mutable.** Every agent updates this file at the start and end of its work.
> Format is deliberately simple so any agent (or human) can parse it.

## Current

- **Phase**: `phase-0-foundation`
- **Current step**: [`phase-0-foundation/002-frontend-react-setup.md`](./phase-0-foundation/002-frontend-react-setup.md)
- **Status**: `not-started`
- **Owner**: _unassigned_
- **Last updated**: 2026-05-15

## Next 3 steps (preview)

1. [`phase-0-foundation/002-frontend-react-setup.md`](./phase-0-foundation/002-frontend-react-setup.md)
2. [`phase-0-foundation/004-tooling-linting-husky.md`](./phase-0-foundation/004-tooling-linting-husky.md)
3. [`phase-0-foundation/005-database-schema-baseline.md`](./phase-0-foundation/005-database-schema-baseline.md)

## History (append-only, newest at top)

| Date | Step | Status | Actor | Notes |
|------|------|--------|-------|-------|
| 2026-05-15 | [`phase-0-foundation/003-website-wagtail-setup.md`](./phase-0-foundation/003-website-wagtail-setup.md) | done | copilot | Scaffolded Wagtail 6.3.1 (Django 5.1.15) storefront under `storefront/` with split settings (`config/settings/{base,development,production}.py`) loaded via `django-environ`. Pinned three requirements files (`base.txt`, `development.txt`, `production.txt`). Apps: `apps/website/` (`HomePage` with hero fields + JSON `banner` StreamField — heading, paragraph, banner image, featured-products placeholder; plus `ContentPage`), `apps/blog/` placeholder (`BlogIndexPage`), `apps/core/` (`backend_health` server-side probe of `${BACKEND_API_URL}/health/`, allow-all `robots.txt` referencing the sitemap, `site_meta` context processor), and a `theme/` app holding shared templates + Tailwind-built static assets. Tailwind pipeline is **standalone** (no `django-tailwind`) in `theme/static_src/` with pinned `tailwindcss@3.4.17` + `@tailwindcss/typography` + `@tailwindcss/forms`; built CSS is committed to `theme/static/theme/css/output.css` so cPanel deploys don't need Node. `base.html` is semantic + mobile-responsive, with title/description/canonical/OG/Twitter (`wagtail-seo` page-level via `{% include "wagtailseo/meta.html" %}` and `struct_data.html`), favicon, and a site-wide `Organization` JSON-LD block. SEO: `wagtail-seo` 3.1.1 wired, Wagtail `sitemap.xml` mounted at `/sitemap.xml`, `/robots.txt` view, `WhiteNoise` for compressed manifest static files. `manage.py bootstrap_homepage` creates the default HomePage and points the default Site at it (plan 003 step 8); cPanel `passenger_wsgi.py` stub added (full wiring deferred to 012). Appended storefront env keys (`SITE_NAME`, `SITE_DESCRIPTION`, `BACKEND_API_URL`, `BACKEND_API_TIMEOUT`, `WAGTAILADMIN_BASE_URL`, `DB_*`) to root `.env.example`. Added `[tool.ruff.lint.isort] known-first-party = ["config","apps","theme"]` to root `pyproject.toml` so ruff and isort agree on import grouping across the monorepo. Verified end-to-end: `pytest` (5/5 — homepage renders 200 with hero + Organization JSON-LD, `/robots.txt` and `/sitemap.xml` 200, backend-health probe reachable/unreachable both covered), `ruff check`, `black --check`, `isort --check-only` all green; `runserver 8001` serves `/`, `/admin/`, `/sitemap.xml`, `/robots.txt`, `/internal/backend-health/`. |
| 2026-05-15 | [`phase-0-foundation/001-backend-django-setup.md`](./phase-0-foundation/001-backend-django-setup.md) | done | copilot | Scaffolded Django 5.1.15 + DRF 3.15.2 backend with split settings (`config/settings/{base,development,production}.py`) loaded via `django-environ`. Created three pinned requirements files (`base.txt`, `development.txt`, `production.txt`). Added `apps/core/` app with public `GET /api/v1/health/` view, `pagination.py` (default page-number + ledger cursor), and `exceptions.py` (custom DRF exception handler producing the `{error: {code, message, details}}` envelope from `_conventions.md` §5). Wired SimpleJWT (argon2 first), `django-filter`, `drf-spectacular` (`/api/v1/schema/` + `/api/v1/docs/`, title "AsliChoice API" v1.0.0). MySQL is the primary DB engine; `DB_ENGINE=sqlite` (or empty `DB_PASSWORD` in dev) triggers a SQLite fallback so first-time setup works without MySQL. Added `manage.py`, `wsgi.py`, `asgi.py`, `Procfile`, and a `passenger_wsgi.py` stub (full cPanel wiring deferred to plan 012). Appended the backend env keys to root `.env.example`. Verified: `pytest` (3/3 pass — `test_health.py`), `ruff check`, `black --check`, `isort --check-only` all green; `runserver` returns `{status: ok, version, time}` on health and the error envelope on a 405. |
| 2026-05-14 | [`phase-0-foundation/000-repo-bootstrap.md`](./phase-0-foundation/000-repo-bootstrap.md) | done | copilot | Bootstrapped monorepo: created `backend/`, `admin-ui/`, `storefront/`, `qa/{postman,playwright}/`, `docs/`, `docs/adr/` (with `.gitkeep`). Added root `.gitignore` (Python+Node+IDE+env), `.editorconfig`, `.env.example`, `package.json` (private, workspaces `["admin-ui"]`), tooling-only `pyproject.toml` (ruff/black/isort), `LICENSE` placeholder, `CODE_OF_CONDUCT.md` placeholder. README already had project name, description, and links to `plans/README.md` and `doc/PROJECT_DETAILS.md`. |
| 2026-05-14 | _scaffold-complete_ | done | planning | Full plans/ scaffolding complete: 8 meta + 15 phase-0 + 1 M01 folder (6 files) + 19 single M-files (M02-M20) + 4 phase-2 + 4 phase-3 = **57 plan files**. Ready to execute starting at `phase-0-foundation/000-repo-bootstrap.md`. |
| 2026-05-14 | _bootstrap_ | done | planning | Plans directory scaffolded. |

## Blockers

_(none)_

## Decisions log

Record any decision that deviates from `_conventions.md` or `_meta.yaml`.

| Date | Decision | Rationale | Affected plans |
|------|----------|-----------|----------------|

## Update protocol

When you start a step:

```markdown
- **Current step**: <link>
- **Status**: in-progress
- **Owner**: <agent or human name>
- **Last updated**: <YYYY-MM-DD>
```

When you finish a step:

1. Append a row to **History**.
2. Move **Current step** to the file's `next_step` (declared at the bottom of every plan).
3. Update the **Next 3 steps** preview.
4. If a blocker exists, list it under **Blockers** with date + description.
5. Commit: `chore(plans): advance state to <next-step-id>`
