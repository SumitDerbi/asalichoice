# M01 / 01 — API

> **Parent**: [`index.md`](./index.md)

## Goal

Land all master models, services, serializers, viewsets, and endpoints under `/api/v1/master/` with full audit + soft-delete + permission gating.

## Steps

1. Create `apps/master/` app. Sub-packages: `models/`, `services/`, `api/`, `seeders/`.
2. **Models** (each inheriting `BaseModel` from 005):
   - `Branch(code unique, name, type=HQ|STORE|WAREHOUSE|DARK_STORE, parent FK self, address_json, gstin, phone, email, is_active, feature_flags_json)`.
   - `Department(code unique, name)`.
   - `Designation(code unique, name, department FK)`.
   - `UnitOfMeasure(code unique, name, symbol, decimals, parent FK self null, conversion_factor decimal)`.
   - `Tax(code unique, name, rate_total decimal, components_json: [{type:CGST|SGST|IGST|CESS, rate}], hsn_codes M2M to HSNCode)`.
   - `HSNCode(code unique, description, default_tax FK)`.
   - `PaymentMode(code unique, name, type=CASH|UPI|CARD|WALLET|COD|BANK, is_online bool, branches M2M, config_json)`.
   - `Category(code unique, name, parent FK self null, depth_check_max=4, image, seo_slug)`.
   - `Brand(code unique, name, logo, description)`.
   - `Warehouse(code unique, name, branch FK, address_json)`.
   - `Zone(code unique, name, branch FK, pincode_ranges_json | pincodes M2M Pincode)`.
   - `Country(iso2 unique, name, phone_code, currency)`.
   - `State(country FK, code, name)` + `City(state FK, name)` + `Pincode(code unique, city FK, latitude, longitude)`.
3. **Services** (`apps/master/services/<entity>.py`):
   - One service module per aggregate. All writes go via services. Each service: validate → save → audit.
   - `branch_service.create/update/deactivate/reactivate`.
   - `tax_service.compute_breakup(amount, tax_id, inclusive: bool) -> {base, components: [...], total}` — used by M07/M08/M11.
   - `zone_service.resolve_zone_for_pincode(pincode) -> Zone | None`.
4. **Serializers**: one per entity using `BaseModelSerializer`. Read-many trimmed (nested name+code); read-detail full.
5. **Viewsets**: `BaseModelViewSet` per entity with filters (search, is_active, parent), ordering, pagination.
6. **Permissions**: define perms in `apps/master/permissions.py` — `master.view_branch`, `master.manage_branch`, etc. M02 will assign to roles.
7. **URLs**: `/api/v1/master/branches/`, `/departments/`, `/designations/`, `/uom/`, `/taxes/`, `/hsn/`, `/payment-modes/`, `/categories/`, `/brands/`, `/warehouses/`, `/zones/`, `/countries/`, `/states/`, `/cities/`, `/pincodes/`.
8. **Error codes**: prefix `MST-` (e.g. `MST-001 branch_code_duplicate`, `MST-010 category_depth_exceeded`, `MST-020 tax_components_mismatch_total`). Register in error catalog.
9. **OpenAPI**: tag `Master`. One-line summaries per endpoint.
10. **Seeder** `apps/master/management/commands/seed_master.py`:
    - Country (India only Phase 1).
    - All Indian States.
    - Major cities (top 100; full pincode dataset comes later via data migration).
    - Default UoMs: PCS, KG, GRAM, LITRE, ML, METER, BOX, PACK.
    - Default tax slabs: 0%, 5%, 12%, 18%, 28% with CGST/SGST split.
    - Default payment modes (CASH, UPI, CARD, COD).
    - Default branch (Head Office) — replace placeholder from Phase 0.
11. **Migrations**: split — schema migration, then data seeder (don't bake seed data into migrations).
12. Commit: `feat(M01): master management api`.

## Deliverables

- `apps/master/` with all models, services, viewsets, urls.
- Migrations.
- Seeder.
- Error code registry entries.

## Verification

### Manual
1. `python manage.py migrate && python manage.py seed_master` → all defaults present.
2. `GET /api/v1/master/branches/` returns Head Office.
3. `POST /api/v1/master/categories/` with `parent` depth 4 → returns `MST-010`.

### Automated
- `pytest backend/tests/master/ -q` ≥ 85% coverage on services.

## Definition of Done

- [ ] All endpoints CRUD-able.
- [ ] Audit + soft-delete verified.
- [ ] Seeder idempotent.
- [ ] OpenAPI tag `Master` populated.

## Next step

→ [`02-ui.md`](./02-ui.md)

## Previous step

← [`index.md`](./index.md)
