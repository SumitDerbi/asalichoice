# Sales & Billing (M11)

M11 ships the **Sale aggregate** — the canonical record of every bill
issued from any channel (POS, Online, B2B, Manual). It is the upstream
domain for M06 (online checkout) and M07 (POS terminals), both of which
ultimately call into the same `sale_service` to create and post sales.

## Scope

- `Sale` header + `SaleItem` lines + `SalePayment` tender
- `Discount` master + `PriceOverride` audit trail
- Tax (CGST/SGST/IGST/CESS) via `apps.master.api_public.compute_tax`
- Inventory deduction at post-time via
  [`ledger_service`](../inventory/developer-guide.md) — the single writer
  of `Stock.qty_*`
- Reversing ledger entries on cancel
- Offline-safe creation via `offline_uuid` deduplication
- In-process `sale_posted` / `sale_cancelled` signals for downstream
  modules (loyalty, accounting, notifications)

## Out of scope (handled by neighbouring modules)

- POS terminal sessions / cash drawer / holds → M07
- Online cart / web checkout → M06
- GST returns (R1, 3B) → M16
- Receipts printing / invoice PDFs → M18
- Loyalty earn / redemption → M19
