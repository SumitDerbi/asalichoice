# Sales — User guide

## Creating a sale

1. Open **Sales → New sale** (or **New B2B sale** for manual B2B entry).
2. Pick the **branch** (must be one you have access to).
3. Add line items: each needs a product _or_ variant (XOR), a UoM, qty
   and sale price.
4. Optionally add a header note.
5. Either **Save sale** (creates a DRAFT — you can add payments later)
   or check **Auto-post** to post immediately.

## Adding a payment

From the sale detail screen, enter the **payment mode ID** and amount,
then click **Add**. Multiple tenders (split payments) are supported.

## Posting

A sale moves out of DRAFT only when posted:

- Click **Post sale**. The backend verifies that
  `sum(payments).SUCCESS == grand_total` unless your role allows partial
  payments (then the sale becomes `PARTIALLY_PAID`).
- Inventory is debited atomically via the inventory ledger.
- The sale enters status `PAID` (or `PARTIALLY_PAID` / `CONFIRMED`).

## Cancelling

Only posted sales (`CONFIRMED`, `PARTIALLY_PAID`, `PAID`) can be
cancelled. Cancellation:

- Writes a reversing ledger row (`ref_id = "CANCEL:<sale_id>"`) so stock
  returns.
- Flips all `SUCCESS` payments to `REFUNDED`.
- Sale status → `CANCELLED`.

## Discounts

Discounts are master records (`Sales → Discounts`). At sale time the
backend's `discount_engine` decides whether each one is applicable based
on its `condition_json` (min subtotal, product/variant whitelists, date
window). Some discounts require approval; the UI flags those.

## Price overrides

If a cashier sets `sale_price` lower than the product master price _and_
supplies a `price_override_reason`, the backend creates an immutable
`PriceOverride` row capturing the original price, the new price, who
approved it, and whether they had the `sales.price.override` permission.
