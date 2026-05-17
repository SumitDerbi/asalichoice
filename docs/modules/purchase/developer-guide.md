# Developer guide — Vendor & Purchase

## Layout

```
backend/apps/purchase/
├── models.py              # Vendor, PO, GRN, PI, PR, VendorLedger
├── serializers.py         # DRF serializers (one per resource)
├── views.py               # ViewSets + custom actions
├── urls.py                # DefaultRouter
├── permissions.py         # purchase.* codenames
├── services/
│   ├── po_service.py             # create_po, submit_po, approve_po
│   ├── grn_service.py            # create_grn, approve_grn (+ M05 stub)
│   ├── invoice_service.py        # from_grns, post_invoice, pay_invoice
│   ├── purchase_return_service.py# post_return
│   └── ledger_service.py         # append_entry
└── migrations/0001_initial.py
```

## Services & invariants

- All state transitions go through the services — viewsets never
  mutate model fields directly. This keeps audit & ledger writes
  consistent.
- `LEDGER_IMMUTABLE = True` on `VendorLedger`. The model overrides
  `save()` / `delete()` to raise after the first insert.
- `VendorLedger` is exempt from the `apps.core.checks.W001`
  BaseModel rule via `BASE_MODEL_EXEMPTIONS` because financial
  postings must never be soft-deleted.
- All money fields are `Decimal(18, 4)`. Never coerce to `float`.

## Approval thresholds

`purchase.po.approval_thresholds` is a `system_settings` key of
shape:

```json
[
  { "max_value": "50000.00", "permission": "purchase.po.approve" },
  { "max_value": "500000.00", "permission": "purchase.po.approve_l2" },
  { "max_value": null, "permission": "purchase.po.approve_l3" }
]
```

`null` matches "no upper bound". Tiers are evaluated top-down.
`po_service.approve_po()` checks the calling user has the matched
tier's permission.

## Stock-write seam

See [ADR-007](../../adr/007-grn-only-stock-write.md). The only places
inventory is touched in this module are:

- `grn_service._write_inventory_movement(grn)` — called inside
  `approve_grn` (M05 will fill in the warehouse balance update).
- `purchase_return_service.post_return` — logs a reverse-movement
  intent which M05 will consume.

If you find yourself adding a stock write anywhere else, stop and
read the ADR.

## Offline GRN sync

`GRNViewSet.sync_offline` accepts a JSON array of GRN payloads where
foreign keys may be raw IDs (from a disconnected device). The view
resolves `product`, `variant`, and `po_item` IDs to instances before
delegating to `sync_offline_grn(items=...)` in the service. Pairing
is by `offline_uuid` — duplicate calls return the same GRN, not a
new row.

## Testing

```
backend/tests/purchase/
├── conftest.py        # branch/uom/category/product/vendor/po_factory fixtures
├── test_services.py   # 22 service-level tests (state machines, ledger math)
└── test_api.py        # 10 viewset tests (REST surface, permissions)
```

Run with `python -m pytest tests/purchase/` from `backend/`.
Total backend suite: **221 tests** (189 baseline + 32 purchase).

## Admin UI

```
admin-ui/src/modules/purchase/
├── api/{types.ts, hooks.ts}      # TS shapes + TanStack Query hooks
├── components/purchase-list-page.tsx
├── lib/{i18n.ts, use-permission.ts}
├── i18n/en.json
├── pages/{vendors,pos,grns,invoices,returns,ledger}-page.tsx
├── schemas.ts                     # zod validation
├── __tests__/schemas.test.ts
└── index.tsx                      # ModuleDef
```

The module is registered in `src/app/register-modules.ts` and shows
up under category `Operations`. Each document type has a list view
with status badges and row-level action buttons (`Submit` /
`Approve` / `Post` / `Pay` / etc.). Form-based creation for POs,
GRNs, invoices, and returns is API-first for M04 and gets richer
forms in M05+.
