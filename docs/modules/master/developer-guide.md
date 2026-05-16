# Master Management — Developer guide

This guide describes how to consume `apps.master` from other Django
apps and the admin UI. Read alongside [ADR-003](../../adr/003-branch-context.md)
and [ADR-004](../../adr/004-tax-components.md).

## Public seam

Other modules **must** import master models and helpers through
`apps.master.api_public`. The `services.py` module is internal and
will be refactored as the platform evolves.

```python
from apps.master.api_public import (
    compute_tax,
    get_current_branch,
    get_tax_by_code,
    is_payment_mode_enabled,
    resolve_zone_for_pincode,
)

branch = get_current_branch()           # Branch | None
tax = get_tax_by_code("GST-18")          # Tax | None
total = compute_tax(amount, tax)         # {"base": ..., "cgst": ..., ...}
allowed = is_payment_mode_enabled(branch, "CASH")  # bool
zone = resolve_zone_for_pincode("560001")  # Zone | None
```

These helpers honour soft-delete and active flags. They never raise —
missing data returns `None` / `False` and the **caller** decides what
envelope to surface.

## Branch context middleware

`apps.master.middleware.BranchContextMiddleware` reads `X-Branch-Id`
from the request, validates it against the authenticated session, and
binds it to a contextvar. Downstream code reads it via:

```python
from apps.core.context import current_branch_id
from apps.master.api_public import get_current_branch

bid = current_branch_id()        # int | None — fast path
branch = get_current_branch()    # Branch | None — DB hit, cached
```

Middleware ordering matters — `BranchContextMiddleware` **must** come
after `RequestContextMiddleware` in `settings.MIDDLEWARE`, otherwise
the audit middleware's `None` branch will shadow the explicit value.

The middleware itself is permissive at M01: any authenticated user can
select any active branch. Real branch-level ACLs come with M02.

## Caching

`apps.master.cache` exposes versioned helpers used by the public API:

```python
from apps.master.cache import cached_branch_list, cached_category_tree
```

The cache key namespace is `master:v{n}:<domain>:<key>`. The version
`{n}` lives in a `SiteSetting` keyed `master.cache_version`. On every
`post_save` / `post_delete` of Branch / Tax / HSNCode / Zone / Pincode
the version bumps (see `apps/master/signals.py`), which invalidates
every dependent entry without enumerating keys.

The current implementation is an in-process TTL dict. M18 replaces it
with Redis without changing the public surface.

## Error envelope

All M01 errors subclass `apps.core.api.exceptions.DomainError` and use
the `MST-*` code namespace. The service layer raises typed exceptions;
viewsets let the global DRF exception handler translate them. See
[Error codes](error-codes.md) for the full list.

```python
from apps.master.exceptions import BranchAccessDenied, TaxComponentsMismatch
```

The envelope shape is:

```json
{
  "error": {
    "code": "MST-020",
    "message": "Tax components do not match rate_total.",
    "details": null
  }
}
```

## Signals you can listen to

`apps.master.signals` re-emits the relevant `post_save` / `post_delete`
events without modification — subscribe with `dispatch_uid` to avoid
double-binding under runserver reload.

## Tests and fixtures

- `backend/tests/master/conftest.py` provides `branch_factory`,
  `tax_factory`, `category_tree` fixtures.
- For coverage-sensitive code, run
  `pytest tests/master/ --cov=apps.master --cov-report=term-missing`.
- Soft-delete assertions must use `Model.objects` (default manager
  hides soft-deleted rows) **and** `Model.all_objects` (full table).

## Admin-UI integration

Module dir: `admin-ui/src/modules/masters/` (registered as `id: masters`
in the module registry). MSW mock handlers for tests live at
`admin-ui/src/test/mocks/master-handlers.ts`.

The shared `MasterFormBody` component:

- Wraps TanStack Form with our error-mapping helper.
- Calls `mapApiErrorToFields(error)` on submit failure so server
  validation surfaces inline.
- Reads the active branch from `useBranchStore.getState().currentBranchId`
  and injects it as `X-Branch-Id`.

## Seeding

```bash
python manage.py seed_master           # idempotent; safe to re-run
python manage.py seed_all              # also seeds users / roles / etc.
```

Counts after a fresh seed: 1 country, 37 states/UTs, 95 curated cities,
8 UoMs, 5 GST slabs, 4 payment modes, 1 HQ branch.
