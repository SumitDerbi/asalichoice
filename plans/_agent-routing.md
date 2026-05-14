# Agent Routing

Which agent/model handles which kind of work, for optimal token & context use.

> If a single capable agent is doing everything, just default to **Default Implementer**.
> This table matters when orchestrating multiple subagents in parallel.

## Roles

| Role | Used for | Recommended invocation |
|---|---|---|
| **Default Implementer** | Most module work (API + UI + tests for a single module) | main agent |
| **Explorer (read-only)** | Codebase Q&A, "where is X?", impact analysis | `Explore` subagent (quick / medium / thorough) |
| **Schema Designer** | Drafting Django models + migrations for a module before code | Default Implementer; one plan file ahead of API plan |
| **API Implementer** | DRF viewsets, serializers, permissions, OpenAPI schema | Default Implementer scoped to `backend/apps/<module>/` |
| **UI Implementer** | React + shadcn screens, forms, tables, TanStack Query wiring | Default Implementer scoped to `admin-ui/src/modules/<module>/` |
| **Test Author** | Pytest + Vitest + Playwright + Postman | Default Implementer; runs after API/UI per module |
| **Doc Writer** | MkDocs pages, API docs, user guide section | Default Implementer; after tests pass |
| **Reviewer** | Pre-merge review against `_conventions.md` + plan's Definition of Done | Default Implementer in review mode (no edits, just findings) |
| **DevOps** | `deploy.sh`, cPanel config, htaccess, CI | Default Implementer; small focused plans (012, phase-3) |

## Per-module orchestration (recommended)

For each Mxx module:

1. **Schema/API agent** → execute `01-api.md` (models, migrations, serializers, viewsets, permissions, audit hooks, postman seed).
2. **UI agent** → execute `02-ui.md` (TanStack Query hooks, screens, forms, tables, shortcuts).
3. **Integration agent** → execute `03-integration.md` (wire UI → API end-to-end, error handling, optimistic updates).
4. **Test agent** → execute `04-tests.md` (unit + API + e2e + postman).
5. **Doc agent** → execute `05-docs.md` (MkDocs page + screenshots + API reference).

For modules without sub-files (M02–M20 single file), execute the file's numbered sections in the same order.

## Context-budget guidance

- Keep each plan file ≤ ~250 lines so an implementer can hold it + 2–3 source files + conventions in one context.
- When a plan exceeds 250 lines, split it (`<id>a-...`, `<id>b-...`) and update the chain.
- The **explorer** subagent should be preferred over loading many files into the main context.

## Parallelism

Independent modules with non-overlapping dependencies can run in parallel after Phase 0:

- **Parallel-safe pairs** (after M01 + M02 land):
  - M03 (Vendor) ⫼ M11 (Notifications)
  - M17 (Documents) ⫼ M18 (System Settings) ⫼ M19 (Super Admin)
- **Strictly sequential**: M01 → M02 → M05 path, and anything touching inventory/finance.
