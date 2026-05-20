# Sales — Developer guide

## Layout

```
apps/sales/
├── apps.py                — SalesConfig
├── models.py              — Sale, SaleItem, SalePayment, Discount, PriceOverride
├── exceptions.py          — SAL-* DomainErrors
├── permissions.py         — SALES_PERMISSIONS tuple
├── signals.py             — sale_posted, sale_cancelled (django.dispatch.Signal)
├── admin.py               — Django admin
├── serializers.py         — DRF serializers + SaleCreateSerializer
├── views.py               — SaleViewSet, DiscountViewSet
├── urls.py                — DefaultRouter mounted at /api/v1/
└── services/
    ├── tax_engine.py      — thin wrapper over apps.master.api_public.compute_tax
    ├── discount_engine.py — applicability + apply_line / apply_header
    ├── sale_builder.py    — pure recompute() (no DB writes)
    └── sale_service.py    — create_draft, post, cancel, recompute, add_payment
```

## Permissions (seed via `python manage.py seed_permissions`)

| Code                     | Used for                                   |
| ------------------------ | ------------------------------------------ |
| `sales.view`             | read-only API access                       |
| `sales.manage`           | create / post drafts                       |
| `sales.cancel`           | cancel a posted sale                       |
| `sales.price.override`   | line price below master price              |
| `sales.discount.apply`   | apply a discount at sale time              |
| `sales.discount.approve` | apply discounts marked `requires_approval` |
| `sales.b2b.create`       | manual B2B entry                           |

## Public service surface

`apps.sales.services.sale_service`:

- `create_draft(*, branch, origin='POS', customer=None, cashier=None,
tax_mode='EXCLUSIVE', notes='', offline_uuid=None, items=(),
payments=(), actor=None) -> Sale`
- `post(sale, *, actor=None, allow_partial_payment=False,
reason_code='', remarks='') -> Sale`
- `cancel(sale, *, actor=None, reason='') -> Sale`
- `recompute(sale) -> Sale`
- `_add_payment(sale, *, payment_mode, amount, ...) -> SalePayment`

All write paths are wrapped in `@transaction.atomic`. `post` and
`cancel` call `ledger_service.post(...)` — they never touch
`Stock.qty_*` directly.

## Signals

Imported from `SalesConfig.ready()`; receivers register via
`@receiver` with a `dispatch_uid`:

```python
from apps.sales.signals import sale_posted, sale_cancelled

@receiver(sale_posted, dispatch_uid="loyalty_on_sale_posted")
def _award_loyalty(sender, sale, actor, **kwargs):
    ...
```

## Error envelope

All sales failures inherit from `apps.core.api.exceptions.DomainError`
and map to:

```json
{ "error": { "code": "SAL-010", "message": "...", "details": {} } }
```

See [error-codes.md](error-codes.md).

## Tax mode

- `EXCLUSIVE` — `sale_price` does not include tax. `line_total =
line_subtotal + line_tax`. `grand_total = subtotal + tax_total -
header_discount`.
- `INCLUSIVE` — `sale_price` already includes tax. The backend unwraps
  base + tax for breakup but does not add tax to the bill.

Line discounts are baked into `line_subtotal` (so they're already in
`Sale.subtotal`); only header-level discounts are subtracted again in
`grand_total`.

## Tests

```
backend/tests/sales/
├── conftest.py             — branch, uom, product, gst18, cash_mode, grn_in
├── test_tax_engine.py
├── test_sale_builder.py
├── test_discount_engine.py
└── test_sale_service.py    — create_draft, offline_uuid dedup,
                              post writes ledger + PAID + Stock,
                              empty sale blocked, mismatch blocked,
                              cancel reverses + refunds, signal emit
```

26 tests, all green.

## ADR

See [ADR-014: Single Sale aggregate](../../adr/014-single-sale-aggregate.md).
