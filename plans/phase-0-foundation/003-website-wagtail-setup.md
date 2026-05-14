# 003 — Website (Wagtail) Setup

> **Phase**: phase-0-foundation  **Depends on**: 001  **Module**: --  **Est. effort**: M

## Goal

Stand up `storefront/` as a Wagtail site (separate Django project, **shares MySQL DB read-only with backend later via API; not direct DB**) with Tailwind theme, mobile-responsive base template, SEO basics, and a homepage placeholder.

## Inputs

- [ ] 001 complete.
- [ ] Python venv (`storefront/.venv`) separate from backend venv.

## Steps

1. `cd storefront && python -m venv .venv && . .venv/Scripts/activate`.
2. Install: `wagtail`, `django-environ`, `whitenoise`, `gunicorn` (local only), `django-tailwind` (or run Tailwind CLI standalone — prefer standalone to avoid node-in-django).
3. `wagtail start website .` → tidy structure: `apps/website/`, `apps/blog/` (placeholder), `theme/` for templates + Tailwind assets.
4. Tailwind: init `theme/static_src/` with `package.json` + `tailwind.config.js` + `input.css`; build to `theme/static/css/output.css`. Add `make tailwind-watch` / npm script.
5. Base template `theme/templates/base.html`: semantic, mobile-responsive, meta tags (title, description, OG, canonical), favicon links, JSON-LD `Organization`.
6. Wagtail settings split: `config/settings/{base,development,production}.py` mirroring backend.
7. `apps/website/models.py`: `HomePage(Page)` with hero, featured products block, banner streamfield (simple text + image blocks initially).
8. Migrate + create superuser + create homepage.
9. SEO defaults: `wagtail-seo` package, `robots.txt` view, `sitemap.xml` (Wagtail built-in).
10. Add `.env.example` for storefront (`SECRET_KEY, DB_*, ALLOWED_HOSTS, BACKEND_API_URL`).
11. Add a placeholder route fetching `${BACKEND_API_URL}/health/` server-side to confirm cross-app reachability (no UI surfacing yet).
12. Commit: `feat(storefront): scaffold wagtail with tailwind theme`.

## Deliverables

- `storefront/` runnable via `python manage.py runserver 8001`.
- Wagtail admin at `/admin/`.
- Homepage with hero rendering at `/`.
- Tailwind build pipeline.

## Verification

### Manual
1. `python manage.py runserver 8001` → `/` renders homepage.
2. `/sitemap.xml` and `/robots.txt` load.
3. Lighthouse mobile score ≥ 80 on placeholder.

### Automated
- `pytest storefront/tests/test_homepage.py -q` passes (renders 200).

## Definition of Done

- [ ] Wagtail admin reachable.
- [ ] Homepage renders, mobile-responsive.
- [ ] SEO files present.
- [ ] `_state.md` advanced.

## Next step

→ [`004-tooling-linting-husky.md`](./004-tooling-linting-husky.md)

## Previous step

← [`002-frontend-react-setup.md`](./002-frontend-react-setup.md)
