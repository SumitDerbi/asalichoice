# 010 — Testing Setup

> **Phase**: phase-0-foundation  **Depends on**: 006, 007  **Module**: --  **Est. effort**: M

## Goal

Wire all four test surfaces — Pytest (backend), Vitest (admin-ui), Playwright (e2e), Newman (Postman) — with shared fixtures, sample tests, and a unified `make test` flow.

## Inputs

- [ ] 006 + 007 complete.

## Steps

1. **Backend (pytest)**:
   - `backend/pytest.ini` or `pyproject.toml` config: `DJANGO_SETTINGS_MODULE=config.settings.development`, `addopts=-q --strict-markers --cov=apps --cov-report=term-missing --cov-fail-under=70`.
   - `tests/conftest.py`: db setup, authenticated API client factory, branch factory, audit-capturing context manager.
   - Factories: `factory_boy` `UserFactory`, `BranchFactory` (stub until M01).
   - Sample tests already from 005/006; verify they pass.
2. **Admin-UI (vitest)**:
   - `vitest.config.ts`: jsdom env, setup file with RTL + `@testing-library/jest-dom`.
   - `src/test/utils.tsx`: `renderWithProviders` (QueryClient, Router, theme).
   - MSW for API mocking; handlers under `src/test/mocks/`.
   - Coverage gate 70% via `pnpm test -- --coverage`.
3. **Playwright (e2e)**:
   - `admin-ui/playwright.config.ts`: 1 worker locally; trace on retry; baseURL from env.
   - `e2e/fixtures/auth.ts`: logged-in fixture seeding token via API.
   - `e2e/login.spec.ts` already from 006; add a `dashboard.spec.ts`.
4. **Postman (newman)**:
   - `qa/postman/local.env.json`, `qa/postman/staging.env.json`.
   - `qa/postman/auth/collection.json` already from 006.
   - Script `pnpm postman:run` invoking newman against all collections.
5. **CI script** `scripts/test-all.ps1` and `scripts/test-all.sh`:
   - Spin up MySQL test DB (or use SQLite for backend speed).
   - Run: ruff, black-check, isort-check, pytest, eslint, vitest, postman, playwright (last).
6. **Make targets** in `Makefile` mirroring above.
7. Document in `docs/quality/testing.md` and link from `_conventions.md` §9.
8. Commit: `chore(test): unify pytest + vitest + playwright + newman`.

## Deliverables

- All four test runners green on current codebase.
- Unified `make test` / `scripts/test-all.*`.
- Docs page.

## Verification

### Manual
1. Run `make test` (or `./scripts/test-all.sh`) — all four suites pass.
2. Break one test deliberately → suite fails loudly.

### Automated
- All commands above exit 0.

## Definition of Done

- [ ] Coverage gates configured.
- [ ] One sample test per surface green.
- [ ] CI-ready scripts available.
- [ ] `_state.md` advanced.

## Next step

→ [`011-docs-platform.md`](./011-docs-platform.md)

## Previous step

← [`009-forms-validation-zod.md`](./009-forms-validation-zod.md)
