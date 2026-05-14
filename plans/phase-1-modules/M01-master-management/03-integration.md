# M01 / 03 — Integration

> **Parent**: [`index.md`](./index.md)  **Depends on**: [`01-api.md`](./01-api.md), [`02-ui.md`](./02-ui.md)

## Goal

Wire M01 into the rest of the system so downstream modules can rely on it without coupling tightly: branch context middleware, signal hooks, public service interfaces.

## Steps

1. **Branch context middleware** (`apps/master/middleware.py`):
   - Reads `X-Branch-Id` header → resolves to `Branch` → stores in `core.branch_context` thread-local.
   - Falls back to user's primary branch (M02) if header missing.
   - 403 with `MST-030 branch_access_denied` if user cannot access that branch.
2. **Public service API** (`apps/master/api_public.py` — imported by other apps):
   - `get_current_branch()`, `get_tax_by_code(code)`, `compute_tax(amount, tax_id, inclusive)`, `resolve_zone_for_pincode(pin)`, `is_payment_mode_enabled(branch, mode_code)`.
3. **Signals**:
   - On `Branch.save()` post-save: emit `branch_changed` signal → invalidate caches in downstream modules (placeholder receiver until M05/M07).
   - On `Tax.save()`: bump a settings counter so M03/M08 caches can invalidate.
4. **System settings hooks**:
   - Default branch ID stored as `default.branch_id` in `SiteSetting`.
   - Default tax slab IDs stored similarly.
   - Default payment mode for POS.
5. **Permission scaffolding**: declare all `master.*` perms; M02 will create role bindings.
6. **Health endpoint extension** (`/api/v1/health/`) now also reports masters: counts of branches, taxes, categories, brands — gives quick "is master seeded?" signal.
7. **Caching**:
   - Use `django.core.cache` with per-key TTLs (taxes 5min, branches 1min, zones 10min).
   - Cache keys versioned by a `master.cache_version` setting bumped on writes.
8. Commit: `feat(M01): branch context middleware + public service api`.

## Deliverables

- Middleware registered.
- `api_public.py` documented and imported by no module yet (placeholder).
- Signals + caches.

## Verification

### Manual
1. Send a request without `X-Branch-Id` as a multi-branch user → middleware picks primary branch.
2. Send `X-Branch-Id` for a branch the user can't access → 403 `MST-030`.

### Automated
- `pytest backend/tests/master/test_integration.py -q` covers middleware paths and `api_public` functions.

## Next step

→ [`04-tests.md`](./04-tests.md)

## Previous step

← [`02-ui.md`](./02-ui.md)
