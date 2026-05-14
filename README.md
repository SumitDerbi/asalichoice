# AsliChoice

Omnichannel retail & commerce platform — POS, online storefront, inventory, finance, HR, and more — built as an agent-executable project.

## What this repo holds

- **`doc/`** — product & business documents:
  - [`PROJECT_DETAILS.md`](doc/PROJECT_DETAILS.md) — single-page architecture & scope summary (planning-ready).
  - [`SOFTWARE_REQUIREMENT_SPECIFICATION_ASLI_CHOICE.md`](doc/SOFTWARE_REQUIREMENT_SPECIFICATION_ASLI_CHOICE.md) — full SRS (20 modules + appendices).
  - [`old.arechitecture.md`](doc/old.arechitecture.md) — legacy reference.
- **`plans/`** — the agent execution plan. Start here:
  - [`plans/README.md`](plans/README.md) — directory map + execution rules.
  - [`plans/_state.md`](plans/_state.md) — current step / next 3 / history (mutable).
  - [`plans/_meta.yaml`](plans/_meta.yaml) — machine-readable project context (stack, conventions, security, module order, state).
  - [`plans/_conventions.md`](plans/_conventions.md) — code, API, UI, testing, docs, security, error-code conventions.
  - [`plans/_agent-routing.md`](plans/_agent-routing.md) — which agent role handles which phase.
  - [`plans/_glossary.md`](plans/_glossary.md) — shared terminology.
- **`backend/`, `admin-ui/`, `storefront/`, `qa/`, `docs/`, `deploy.sh`** — created during Phase 0 (see [`plans/phase-0-foundation/000-repo-bootstrap.md`](plans/phase-0-foundation/000-repo-bootstrap.md)).

## Stack (summary)

- **Backend**: Django 5 + DRF, Python 3.11, MySQL (SQLite dev fallback), Redis, Celery, SimpleJWT, argon2.
- **Admin UI**: React + Vite + TypeScript (strict), Tailwind + shadcn/ui, TanStack Query/Form, Zod, cmdk command-palette.
- **Storefront**: Wagtail (Django) + Tailwind, SSR-first for SEO.
- **Testing**: pytest + pytest-django + factory_boy, Vitest + RTL, Playwright, Postman/newman.
- **Deploy**: cPanel + Phusion Passenger; `deploy.sh` pattern mirrored from `E:\extra\kimplaspiping\kp\deploy.sh` with `~/deploy_config/<env>/` configs.

Full machine-readable detail in [`plans/_meta.yaml`](plans/_meta.yaml).

## Execution model

The project ships in three phases, executed top-to-bottom:

1. **Phase 0 — Foundation** ([`plans/phase-0-foundation/`](plans/phase-0-foundation/)) — repo, backend, frontend, storefront, tooling, deploy script, baseline DB, auth skeleton, admin shell, API conventions, forms, testing, docs, site settings, seeders. (15 plans.)
2. **Phase 1 — Modules** ([`plans/phase-1-modules/`](plans/phase-1-modules/)) — M01 → M20 in the order declared in `_meta.yaml > module_order`. M01 is the multi-file reference template; M02-M20 follow the same structure.
3. **Phase 2 — Hardening** ([`plans/phase-2-hardening/`](plans/phase-2-hardening/)) — security, performance, accessibility/SEO, observability.
4. **Phase 3 — Launch** ([`plans/phase-3-launch/`](plans/phase-3-launch/)) — UAT, data migration, go-live runbook, post-launch operations.

Every plan file follows the same shape: **Goal → Inputs → Steps → Deliverables → Verification (Manual + Automated) → Definition of Done → Next/Previous links.**

## For agents

When starting work, in order:

1. Read [`plans/_state.md`](plans/_state.md) → find the **Current step**.
2. Read [`plans/_conventions.md`](plans/_conventions.md) + [`plans/_meta.yaml`](plans/_meta.yaml).
3. Open the current-step plan file and follow it end-to-end.
4. Update [`plans/_state.md`](plans/_state.md) **History** on completion; move **Current step** to that plan's declared `next_step`.
5. Never skip ahead — order is intentional (e.g. masters → vendors → purchase → inventory).

## For humans

Open [`plans/README.md`](plans/README.md) for the directory map, then [`doc/PROJECT_DETAILS.md`](doc/PROJECT_DETAILS.md) for what's being built and why.
