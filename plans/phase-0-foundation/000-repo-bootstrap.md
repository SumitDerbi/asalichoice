# 000 — Repository Bootstrap

> **Phase**: phase-0-foundation  **Depends on**: none  **Module**: --  **Est. effort**: S

## Goal

Initialise the monorepo layout defined in [`_conventions.md` §1](../_conventions.md#1-repository-layout) with placeholder folders, root tooling, and base documentation. No application code yet.

## Inputs (prerequisites)

- [ ] Read `_conventions.md`, `_meta.yaml`, `_state.md`.
- [ ] Git installed; remote `origin` (`SumitDerbi/asalichoice`) configured.

## Steps

1. Create top-level folders: `backend/`, `admin-ui/`, `storefront/`, `qa/postman/`, `qa/playwright/`, `docs/`, `docs/adr/`. Add `.gitkeep` in each empty one.
2. Create `.gitignore` (Python + Node + IDE + env files). Reference: standard `github/gitignore` Python + Node templates concatenated.
3. Create `.editorconfig` at repo root (LF, UTF-8, 2-space JS/TS, 4-space Python, final newline).
4. Create `.env.example` at repo root listing **all** environment variables agents will introduce later (start empty header, modules append). Add a note: real `.env` lives under `~/deploy_config/<env>/`.
5. Create `package.json` at repo root (private, workspaces: `["admin-ui"]`). Add scripts: `lint`, `format`, `test`, `e2e` (delegate to workspaces). Do **not** install yet.
6. Create root `pyproject.toml` for tooling-only (`ruff`, `black`, `isort`, `pre-commit`) — actual Python project lives in `backend/`.
7. Create `LICENSE` placeholder (TBD with owner) and `CODE_OF_CONDUCT.md` placeholder.
8. Update root `README.md` with: project name, one-line description, link to `plans/README.md`, link to `doc/PROJECT_DETAILS.md`.
9. Commit: `chore: bootstrap repository structure`.

## Deliverables

- Folders + `.gitkeep`s as listed.
- `.gitignore`, `.editorconfig`, `.env.example`.
- Root `package.json`, `pyproject.toml`.
- Updated `README.md`.

## Verification

### Manual
1. `git status` clean after commit.
2. Folder tree matches `_conventions.md` §1.

### Automated
- `git ls-files | wc -l` returns expected count (≥ the new files).

## Definition of Done

- [ ] All folders present.
- [ ] Root tooling configs in place.
- [ ] README links to plans.
- [ ] PR merged.
- [ ] `_state.md` advanced.

## Next step

→ [`001-backend-django-setup.md`](./001-backend-django-setup.md)

## Previous step

← _none_
