# Catalog — Error codes

Every error is rendered through the standard envelope (see
[API conventions](../../api/conventions.md)):

```json
{
  "error": {
    "code": "CAT-NNN",
    "message": "Human-readable summary.",
    "details": { "...": "..." }
  }
}
```

All `CAT-*` codes are declared as `DomainError` subclasses in
`apps/catalog/exceptions.py`.

## Catalogue

| Code      | HTTP | Exception                 | Raised when …                                                                        |
| --------- | ---- | ------------------------- | ------------------------------------------------------------------------------------ |
| `CAT-001` | 409  | `ProductSKUDuplicate`     | `Product.sku` collides with an existing (non-archived) product.                      |
| `CAT-002` | 409  | `ProductCodeDuplicate`    | `Product.code` collides with an existing product.                                    |
| `CAT-003` | 409  | `VariantSKUDuplicate`     | `ProductVariant.sku` collides under any product.                                     |
| `CAT-010` | 400  | `ProductArchived`         | Attempt to mutate / re-activate an `ARCHIVED` product without explicit un-archive.   |
| `CAT-020` | 404  | `PriceNotFound`           | `get_effective_price` has no active band for (product\|variant, branch, at).         |
| `CAT-021` | 400  | `PriceTargetInvalid`      | `ProductPrice.product` and `variant` both set, or both null.                         |
| `CAT-022` | 400  | `PriceWindowInvalid`      | `valid_from >= valid_to` on a `ProductPrice`.                                        |
| `CAT-030` | 400  | `BundleFixedPriceMissing` | `Bundle.price_policy='FIXED'` but `fixed_price IS NULL`.                             |
| `CAT-031` | 400  | `BundleEmpty`             | Attempt to publish a bundle with zero components.                                    |
| `CAT-040` | 400  | `BarcodeTargetInvalid`    | `Barcode` row has both `product` and `variant` set or neither.                       |
| `CAT-050` | 400  | `ImportRowsInvalid`       | CSV import committed but at least one row failed (raised only when `dry_run=False`). |

## Frontend handling

Admin-UI's drawer forms map `details.fields` to per-field errors via
`mapApiErrorToFields` (see [UI / forms](../../ui/forms.md)). Form-level
fallbacks toast through `sonner`.

| Code                              | UI surface                                                            |
| --------------------------------- | --------------------------------------------------------------------- |
| `CAT-001` / `CAT-002` / `CAT-003` | Inline error on the conflicting field (`sku` / `code`).               |
| `CAT-010`                         | Toast: "Product is archived — un-archive before editing."             |
| `CAT-020`                         | The price drawer surfaces "No active band for this branch."           |
| `CAT-021`                         | Inline error on `product` _and_ `variant` ("Pick exactly one").       |
| `CAT-022`                         | Inline error on `valid_to` ("Must be after start date").              |
| `CAT-030` / `CAT-031`             | Toast on bundle save.                                                 |
| `CAT-040`                         | Inline error on `value` of the barcode form (or scanner toast).       |
| `CAT-050`                         | Import wizard renders the per-row error table with HTTP 400 envelope. |

## Cross-module references

- `MST-002 branch_access_denied` (403) is raised by the
  [master](../master/error-codes.md) middleware before any catalog
  endpoint runs — a request with an unknown / inactive `X-Branch-Id`
  never reaches catalog code.
- `AUTH-*` codes are surfaced by [users](../users/error-codes.md) for
  the auth layer.
