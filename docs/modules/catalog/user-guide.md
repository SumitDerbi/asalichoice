# Catalog — User guide

Open **Catalog Management** from the sidebar (category _Catalog_).
The module renders a 2-column shell: section nav on the left,
content on the right.

## Sections

### Products

- **Search** matches name, SKU, code, and barcode.
- **Status filter** narrows the list to `DRAFT`, `ACTIVE`, or
  `ARCHIVED`.
- **Show inactive** is _not_ shown here — products use a separate
  `status` field instead of the generic `is_active` flag. Archived
  rows always appear; filter them out with the status dropdown.
- **Create** opens a right-side drawer. Required fields: `code`,
  `sku`, `slug`, `name`, `category`, `base_uom`. Brand is optional.
  `status` defaults to `DRAFT` — promote to `ACTIVE` when ready to
  sell.
- **Edit** opens the same drawer prefilled. Saving issues a `PATCH`.
- **Archive** sets `status=ARCHIVED` (no destructive delete). The
  product disappears from POS lists but historical sales remain
  queryable.

### Bundles

- `code` + `name` + `kind` (`COMBO` or `MIX_AND_MATCH`).
- **Price policy** = `SUM` (computed from component prices at sale
  time) or `FIXED` (uses `fixed_price`). The drawer requires
  `fixed_price` only when policy is `FIXED`.
- Component lines (the actual products inside the bundle) live on
  `/api/v1/catalog/bundle-components/` — phase-1 admin-UI exposes
  only the bundle header; the drag-drop builder lands in a follow-up.

### Prices

Every row is an effective-date band. Two important constraints:

1. A band targets **exactly one** of `product` or `variant`. Setting
   both is rejected with `CAT-021`.
2. `valid_from` must be before `valid_to` (when both are set).

The list shows raw band rows. To see the **effective** price for a
product right now, hit `GET /api/v1/catalog/products/{id}/price/?branch={id}`
or the POS bulk-lookup endpoint.

### Import

1. Click **Choose CSV file** and select a UTF-8 CSV with this header
   (the field order doesn't matter; the importer reads named columns):

   ```text
   code,sku,name,slug,category_code,brand_code,hsn_code,tax_code,base_uom_code,status,description
   ```

2. **Dry run** is on by default. The server validates every row and
   returns a `valid / total / errors[]` summary without writing
   anything.
3. Untick Dry run and re-upload to commit. The importer batches with
   `bulk_create(chunk_size=500)`.
4. The error table lists the **1-based row number** and the original
   `CAT-*` validation message. Fix the CSV and re-upload.

> ℹ️ `category_code` / `brand_code` / `base_uom_code` are looked up
> against the master tables. Unknown codes cause `CAT-001` per row.

## Troubleshooting

| Symptom                                     | Likely cause                                                                  |
| ------------------------------------------- | ----------------------------------------------------------------------------- |
| **Save** disabled in the drawer             | You don't have `catalog.manage` permission. Ask an admin.                     |
| Price form rejects with "Pick exactly one…" | You filled both `product` and `variant`. Clear one.                           |
| Import shows `CAT-001` for every row        | The header row likely has a typo (`category` instead of `category_code`).     |
| Product archived but still in POS           | POS caches catalog data; clear the per-(item, branch) cache or wait ≤60 s.    |
| `404` toast on barcode resolve              | Unknown barcode — `CAT-040`. Check for trailing whitespace or wrong encoding. |
