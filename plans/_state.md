# Execution State Tracker

> **Mutable.** Every agent updates this file at the start and end of its work.
> Format is deliberately simple so any agent (or human) can parse it.

## Current

- **Phase**: `phase-0-foundation`
- **Current step**: [`phase-0-foundation/001-backend-django-setup.md`](./phase-0-foundation/001-backend-django-setup.md)
- **Status**: `not-started`
- **Owner**: _unassigned_
- **Last updated**: 2026-05-14

## Next 3 steps (preview)

1. [`phase-0-foundation/001-backend-django-setup.md`](./phase-0-foundation/001-backend-django-setup.md)
2. [`phase-0-foundation/002-frontend-react-setup.md`](./phase-0-foundation/002-frontend-react-setup.md)
3. [`phase-0-foundation/003-website-wagtail-setup.md`](./phase-0-foundation/003-website-wagtail-setup.md)

## History (append-only, newest at top)

| Date | Step | Status | Actor | Notes |
|------|------|--------|-------|-------|
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
