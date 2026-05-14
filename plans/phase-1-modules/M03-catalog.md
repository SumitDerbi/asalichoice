# M03 — Catalog Management

> **Phase**: phase-1-modules  **SRS ref**: Module 3  **Depends on**: M01, M02  **Est. effort**: L

## Goal

Products + variants + bundles + barcodes + media + per-branch pricing & availability + import/export. Catalog is the heart of every sale; design for **billions of price lookups** while keeping the admin UX fast.

## Steps

1. **Models** `apps/catalog/`:
   - `Product(code unique, sku unique, name, slug unique, brand FK, category FK, hsn FK, tax FK default, base_uom FK, description, attributes_json, is_variant_parent bool, status=DRAFT|ACTIVE|ARCHIVED, seo_title, seo_description, seo_image)`.
   - `ProductVariant(product FK, sku unique, barcode, attributes_json e.g. {size, color}, image, is_default bool)`.
   - `ProductImage(product FK, image, position, alt)`.
   - `ProductBranchAvailability(product FK, branch FK, is_listed bool)`.
   - `ProductPrice(product/variant FK, branch FK, mrp decimal, sale_price decimal, cost_price decimal, valid_from, valid_to, is_active)`.
   - `Bundle(code unique, name, kind=COMBO|MIX_AND_MATCH, price_policy=FIXED|SUM, fixed_price decimal nullable, components: BundleComponent[product, qty])`.
   - `Barcode(value unique, product/variant FK, type=EAN13|UPC|CODE128|CUSTOM)`.
   - `Attribute(code unique, name, type=TEXT|NUMBER|BOOL|SELECT, options_json)` + `ProductAttributeValue(product, attribute, value)`.
2. **Services**:
   - `pricing_service.get_effective_price(item, branch, at=now)` — picks most recent active price band; cached.
   - `pricing_service.bulk_lookup([(item, branch)…])` — single-query optimisation for POS/cart.
   - `catalog_service.create/update/archive`.
   - `import_service.import_csv(file)` — chunked, dry-run mode, row-level error report.
3. **Endpoints** `/api/v1/catalog/products/`, `/variants/`, `/bundles/`, `/barcodes/`, `/attributes/`, `/prices/`, `/import/`, `/export/`.
4. **Error prefix**: `MST-` for catalog reuses or new `CAT-*` (decide here — use `CAT-*` for product-specific to keep `MST` for module-1 masters).
5. **Search**: Postgres-style trigram index where possible (MySQL FULLTEXT fallback). Provide `?q=` returning products by name, sku, barcode.
6. **Admin-UI**:
   - `src/modules/catalog/` with list (image thumbnail, sku, brand, category, status, price-from), drawer-edit with tabbed sections (Basic / Variants / Media / Pricing / Availability / SEO).
   - **Image uploads**: chunked, resized client-side to media-spec sizes, lazy-loaded.
   - Bulk price editor (spreadsheet-style grid).
   - CSV import wizard with row-level error preview.
   - Bundle builder with drag-drop components.
7. **Caching**:
   - Per-product detail cache 5min, busted on save.
   - Price cache 1min per (item, branch).
8. **Audit**: every price change recorded with before/after (price changes are sensitive for analytics).
9. **Permissions**: `catalog.view`, `catalog.manage`, `catalog.price.manage`, `catalog.import`.
10. **Tests**: pytest (services, pricing math, import edge cases), vitest (variant form, bundle builder), playwright (create product → see in POS later), newman.
11. **Docs**: `docs/modules/catalog/*`, ADR `006-pricing-bands.md` (why effective-date ranges + branch scoping).
12. Commit: `feat(M03): catalog (products, variants, bundles, pricing)`.

## Verification

### Manual
1. Create product with 3 variants + branch-specific prices → POS later picks the correct one.
2. Import CSV with 1000 rows containing 5 bad rows → dry-run shows exactly those 5; commit imports the other 995.
3. Archive product → not selectable in POS but historical sales remain queryable.

### Automated
- `pytest backend/tests/catalog/ -q` ≥ 85% services.
- UI + Playwright + Newman green.

## Definition of Done

- [ ] All features above shipped.
- [ ] Coverage gate met.
- [ ] CSV import handles 10k rows without timeout.
- [ ] Docs + ADR.
- [ ] `_state.md` advanced.

## Next step

→ [`M04-vendor-purchase.md`](./M04-vendor-purchase.md)

## Previous step

← [`M02-user-role.md`](./M02-user-role.md)
