# M01 / 04 — Tests

> **Parent**: [`index.md`](./index.md)

## Goal

Close out M01 testing across all four surfaces.

## Steps

1. **Pytest**:
   - `tests/master/test_models.py` — soft-delete, audit, validators.
   - `tests/master/test_services.py` — branch create/update/deactivate, tax breakup math (inclusive & exclusive), zone resolution, depth guard for categories.
   - `tests/master/test_api.py` — endpoint happy paths + permissions + filters.
   - `tests/master/test_seed.py` — `seed_master` idempotent.
   - Target coverage **≥ 85%** on `apps/master/services/`.
2. **Vitest** (admin-ui):
   - `modules/master/__tests__/branch-list.test.tsx`.
   - `modules/master/__tests__/tax-form.test.tsx` (component picker UI math).
   - `modules/master/__tests__/category-tree.test.tsx` (depth guard).
   - Schema unit tests for all Zod schemas.
3. **Playwright**:
   - `e2e/master/branch.spec.ts` — login → create branch → appears in switcher.
   - `e2e/master/tax.spec.ts` — create CGST+SGST 18% tax → save.
   - `e2e/master/category.spec.ts` — drag-reparent at allowed depth.
4. **Postman** `qa/postman/master/collection.json`:
   - Folders per entity, each with CRUD + filter + permission cases.
   - Env vars for tokens + base URL.
   - Pre-request scripts to log in and set token.
   - Newman runnable.
5. Add coverage badges (text only) to `docs/modules/master.md`.

## Verification

### Manual
1. Run each surface individually and confirm green.

### Automated
- `make test` from repo root green.
- Coverage gate met (≥ 85% services).

## Next step

→ [`05-docs.md`](./05-docs.md)

## Previous step

← [`03-integration.md`](./03-integration.md)
