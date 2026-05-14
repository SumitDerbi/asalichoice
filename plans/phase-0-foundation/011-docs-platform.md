# 011 — Documentation Platform (MkDocs)

> **Phase**: phase-0-foundation  **Depends on**: 001, 002  **Module**: --  **Est. effort**: S

## Goal

One platform for **all** project docs (API, UI, user guides, technical guide, deployment guide, ADRs, media spec). Built with MkDocs Material. Auto-includes OpenAPI from backend.

## Inputs

- [ ] 001 complete (OpenAPI live).

## Steps

1. `docs/` already exists from 000.
2. Install (in a dedicated venv `docs/.venv` or use backend's): `mkdocs-material`, `mkdocs-mermaid2-plugin`, `mkdocs-redirects`, `mkdocs-swagger-ui-tag`, `mkdocs-awesome-pages-plugin`.
3. `docs/mkdocs.yml`:
   - `site_name: AsliChoice Docs`
   - `theme: material` (palette light + dark, instant nav, search).
   - Plugins: `search`, `awesome-pages`, `mermaid2`, `swagger-ui-tag`, `redirects`.
   - Nav (use awesome-pages `.pages` files):
     - Home
     - Architecture (link to `doc/PROJECT_DETAILS.md` mirror)
     - API (auto-rendered OpenAPI)
     - Modules (one page per Mxx)
     - UI Guide
     - User Guide (per role)
     - Deployment Guide
     - Operations Runbook
     - Media Spec (`media-spec.md`)
     - ADRs
4. Pull OpenAPI: pre-build script `docs/scripts/fetch-openapi.py` GETs `http://localhost:8000/api/v1/schema/?format=json` → `docs/api/openapi.json`. `swagger-ui-tag` renders it.
5. Seed pages:
   - `docs/index.md` — landing.
   - `docs/ui/forms.md`, `docs/ui/shortcuts.md`, `docs/ui/components.md`.
   - `docs/api/conventions.md` (from 008).
   - `docs/deployment/index.md` (stub; expanded in 012).
   - `docs/media-spec.md`:
     - Product thumbnail: 600×600 jpg/webp ≤ 150 KB.
     - Product gallery: 1200×1200, ≤ 500 KB.
     - Banner: 1920×640, ≤ 600 KB.
     - Brand logo: 512×512 png transparent, ≤ 100 KB.
     - Avatar: 256×256, ≤ 50 KB.
     - Document max upload: 10 MB (configurable per category).
   - `docs/adr/000-template.md`, `001-migrations.md` (from 005), `002-service-layer.md` (from 008).
6. CI/preview: `mkdocs serve` for local; `mkdocs build` produces `site/` (deployed in phase-3).
7. Commit: `docs: set up mkdocs material platform`.

## Deliverables

- `docs/mkdocs.yml` + seed pages.
- OpenAPI fetch script.
- Media spec page.
- ADR seeds.

## Verification

### Manual
1. `mkdocs serve` → `localhost:8000` shows site.
2. API page renders Swagger from the OpenAPI fetched at build time.
3. Search works.

### Automated
- `mkdocs build --strict` succeeds (no broken links/orphan pages).

## Definition of Done

- [ ] Site builds with `--strict`.
- [ ] Seed pages exist.
- [ ] ADR template available.
- [ ] `_state.md` advanced.

## Next step

→ [`012-deploy-sh.md`](./012-deploy-sh.md)

## Previous step

← [`010-testing-setup.md`](./010-testing-setup.md)
