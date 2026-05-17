# Catalog — Developer guide

## Layout

```
backend/apps/catalog/
├── __init__.py
├── admin.py
├── api_public.py            # stable seam for other modules
├── apps.py
├── exceptions.py            # CAT-* DomainError subclasses
├── migrations/
├── models.py
├── permissions.py           # CATALOG_PERMISSIONS tuple
├── serializers.py
├── services/
│   ├── __init__.py
│   ├── catalog_service.py   # create/update/archive
│   ├── import_service.py    # CSV importer + dry-run
│   └── pricing_service.py   # effective-date band lookup
├── signals.py               # post_save audit + cache invalidation
├── urls.py
└── views.py                 # DRF viewsets + custom actions
```

The convention follows `apps.master` and `apps.users`: models live in
`models.py`, the **view → service → ORM** layering from
[ADR-002](../../adr/002-service-layer.md) is enforced — viewsets stay
thin, services hold transactions, signals stay narrow.

## Public seam (`apps.catalog.api_public`)

Other modules (POS, cart, storefront, vendor purchase) **must** import
from `apps.catalog.api_public` rather than reaching into models or
services directly.

```python
from apps.catalog.api_public import (
    get_effective_price,
    resolve_barcode,
    bulk_price_lookup,
    is_product_listed,
)

price = get_effective_price(product=p, branch_id=request.branch_id)
result = resolve_barcode("8901234567890")  # -> {product, variant}
batched = bulk_price_lookup(branch_id=1, items=[("product", 7), ("variant", 9)])
```

This module owns its own export catalogue:

| Function                   | Returns                                                                  |
| -------------------------- | ------------------------------------------------------------------------ |
| `get_effective_price(...)` | `ProductPrice` (or raises `EffectivePriceMissing` → `CAT-030`).          |
| `bulk_price_lookup(...)`   | `dict[(kind, id), ProductPrice]` — single query.                         |
| `resolve_barcode(value)`   | `{"product": Product, "variant": ProductVariant\|None}` or 404 envelope. |
| `is_product_listed(p, b)`  | `bool` — checks `ProductBranchAvailability`.                             |

## Service patterns

### Pricing

`pricing_service.get_effective_price(item, branch_id, *, at=None)`:

1. `at = at or timezone.now()`.
2. Build cache key `catalog:prices:v{version}:{kind}{id}:b{branch}` and
   try `cache.get(...)` first.
3. On miss, query `ProductPrice` filtered to:
   - matching target (XOR product/variant),
   - `branch_id=branch`,
   - `valid_from <= at`,
   - `valid_to IS NULL OR valid_to > at`,
   - `is_active=True`.
4. Order by `-valid_from`, take the first row.
5. Cache (60 s TTL) and return.

The **version-bump** invalidation (rather than per-key deletes) keeps
cache writes cheap. A signal on `ProductPrice` post_save / post_delete
increments the version, which makes every previously cached key
unreachable on the next read.

### CSV import

`import_service.import_csv(file, *, dry_run, actor=None)`:

1. Decode UTF-8, parse with `csv.DictReader`. Reject files larger
   than `CATALOG_IMPORT_MAX_BYTES` (default 10 MB).
2. Stream rows; for each row run `validate_row(row) -> ProductInput`.
3. Collect `(row_index, error)` for every failed row.
4. If `dry_run`: return `{"total", "valid", "errors", "committed": False}`.
5. Otherwise wrap in `transaction.atomic()`, `bulk_create(products, chunk_size=500)`,
   emit one batched audit row, return `{"total", "valid", "created", "errors", "committed": True}`.

> ⚠️ `bulk_create` skips signals. The importer emits its own
> `audit(action=AuditAction.CREATE, ...)` row at the end of the commit
> path; per-row signals would dwarf the audit log on a 10 k-row file.

### Catalog service

`catalog_service.create_product(payload, *, actor)` /
`catalog_service.update_product(product, payload, *, actor)` /
`catalog_service.archive_product(product, *, actor)`:

- Wrap the corresponding ORM operations in `transaction.atomic()`.
- Pass through `catalog.api_public.signals` for audit (post-save
  handles the rest).
- Archive sets `status=ARCHIVED` rather than calling `.delete()`,
  preserving historical FKs from sales tables.

## Models — invariants

- `Product.code`, `Product.sku`, `Product.slug` — all `unique=True`.
- `ProductPrice` has a DB-level `CheckConstraint(name="catalog_price_xor_target", check=Q(product__isnull=False) ^ Q(variant__isnull=False))`.
- `Bundle.fixed_price` is `NULL` when `price_policy='SUM'` and a
  positive `Decimal(12,2)` when `price_policy='FIXED'` — enforced in
  the serializer.
- `Barcode.value` is `unique=True` with a B-tree index for scanner
  speed.

## Signals (`apps.catalog.signals`)

Wired in `CatalogConfig.ready()` via `dispatch_uid`:

| Sender           | Signal        | Handler                                      |
| ---------------- | ------------- | -------------------------------------------- |
| `Product`        | `post_save`   | `audit(...)`                                 |
| `ProductVariant` | `post_save`   | `audit(...)`                                 |
| `ProductPrice`   | `post_save`   | `audit(...)` + `_bump_price_cache_version()` |
| `ProductPrice`   | `post_delete` | `_bump_price_cache_version()`                |

## Permissions

`CATALOG_PERMISSIONS = ("catalog.view", "catalog.manage", "catalog.price.manage", "catalog.import")`.
Seed via `python manage.py seed_permissions` (which reads each app's
`PERMISSIONS` tuple).

Viewsets resolve required perms via:

```python
class ProductViewSet(BaseModelViewSet):
    required_perms = ("catalog.manage",)            # writes
    required_read_perms = ("catalog.view",)         # reads
```

`HasAnyPermission` (from `apps.core.api.permissions`) treats reads
and writes separately so a store-front service account can have
`catalog.view` without `catalog.manage`.

## Tests

```text
backend/tests/catalog/
├── conftest.py          # category/uom/branch/product/variant fixtures
├── test_services.py     # pricing math, import dry-run, CSV edge cases
└── test_api.py          # endpoint smoke + envelope assertions
```

- **27 cases** at M03 launch; full suite **189 passing**.
- The conftest seeds a `Category`, a `UnitOfMeasure`, and a `Branch`
  per test (transactional db). Avoid leaning on `seed_master` here —
  it loads ~140 master rows and slows the suite.
- Coverage target: `apps.catalog.services` ≥ 85 % (currently met).

## Admin-UI

```
admin-ui/src/modules/catalog/
├── api/
│   ├── hooks.ts        # TanStack Query factory + import mutation
│   └── types.ts
├── components/
│   ├── catalog-form-body.tsx
│   └── catalog-list-page.tsx
├── i18n/en.json
├── index.tsx           # module registration
├── lib/
│   ├── i18n.ts
│   └── use-permission.ts
├── pages/
│   ├── bundles-page.tsx
│   ├── import-page.tsx
│   ├── prices-page.tsx
│   └── products-page.tsx
└── schemas.ts          # zod schemas
```

`CatalogListPage<TRow, TInput>` is the shared list+drawer scaffold; it
mirrors `MasterListPage` but talks to `/catalog/` and supports the
following extras the masters scaffold doesn't need:

- `filters` array (renders extra `<select>` boxes wired to query
  params — used for the product status dropdown).
- `extraActions(row)` slot (used for the per-row Archive button).
- `hideStatus` (set for `Product`, which uses `status` instead of the
  generic `is_active`).

For FK pickers (brand / category / UoM / branch) we **reuse** the
masters module's `RemoteSelectField` rather than duplicate the
`useMasterList` hook — the cross-module import is intentional: the
masters module is the canonical FK registry.
