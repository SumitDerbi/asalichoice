# M08 — Invoice & Print

> **Phase**: phase-1-modules  **SRS ref**: Module 8  **Depends on**: M01, M11, M07, M06  **Est. effort**: M

## Goal

Branch-wise invoice numbering (FY-aware reset + prefix), GST-compliant invoice PDF, print template management, e-invoice (IRN) integration stub, duplicate prevention.

## Steps

1. **Models** `apps/invoice/`:
   - `InvoiceSequence(branch FK, fy_start, prefix, current_number, padding)` — atomic increment.
   - `Invoice(sale FK 1:1, invoice_no unique-per-branch-fy, invoice_date, branch FK, customer_snapshot_json, items_snapshot_json, totals_snapshot_json, tax_breakup_json, printed_count, irn nullable, qr_code nullable, status=ACTIVE|CANCELLED)`.
   - `PrintTemplate(code unique, kind=INVOICE|RECEIPT|GRN|PO|TRANSFER, format=A4|A5|80MM|58MM, html, css, is_default per kind+format)`.
2. **Services**:
   - `invoice_service.issue(sale)` — atomic next-number per (branch, FY), snapshots all data. Idempotent on `sale_id`.
   - `invoice_service.regenerate_pdf(invoice)` — uses chosen template.
   - `irn_service.request(invoice)` — calls GSP (provider TBD, configurable via M18). Stores IRN + QR.
   - `template_service.render(template, invoice) -> html` then headless Chrome → PDF (use `playwright` or `weasyprint`; pick weasyprint for speed/footprint).
3. **Endpoints**: `/api/v1/invoices/`, `/api/v1/invoices/{id}/pdf/`, `/api/v1/invoices/{id}/regenerate-irn/`, `/api/v1/print-templates/`.
4. **Admin-UI**:
   - Invoice list (filter by date, branch, status).
   - Invoice detail with "Download PDF", "Reprint", "Email", "Cancel" actions.
   - Print template editor (HTML + live preview) — Super Admin only.
5. **Sale → Invoice flow**: M11 Sale.post() triggers `invoice_service.issue` for billable origins (POS/ONLINE auto; manual for B2B).
6. **Cancellation**: cancels Invoice + Sale + reverses inventory/ledger atomically. Cancelled invoice retained for audit; number not reused.
7. **Error prefix**: `INV-*` (distinct from inventory's `INV-` — disambiguate: use `INVC-*` for invoice to avoid collision; **update** `_conventions.md` §5 accordingly).
8. **Tests**: concurrency test for `InvoiceSequence` (two parallel issues never collide), FY rollover, IRN happy + retry, PDF render.
9. **Docs**: `docs/modules/invoice/*` + ADR `011-invoice-numbering.md`.
10. Commit: `feat(M08): invoice issue, print templates, e-invoice stub`.

## Verification

### Manual
1. Two concurrent sales same branch → invoices have consecutive numbers, no gaps, no dupes.
2. April 1 FY rollover → number resets to 1, new prefix if configured.
3. Cancel invoice → status changes; PDF watermarked "CANCELLED"; ledgers reversed.
4. Configure new print template → preview reflects changes → print on POS uses new template.

### Automated
- `pytest backend/tests/invoice/ -q` including concurrency test, ≥ 85%.
- UI + Playwright + Newman green.

## Definition of Done

- [ ] Numbering atomic, FY-aware, branch-wise.
- [ ] PDFs render correctly on A4 + 80mm.
- [ ] IRN stub returns + stored.
- [ ] `_state.md` advanced.

> **Action item:** update `_conventions.md` §5 error-prefix table to rename invoice prefix to `INVC-` (avoid collision with inventory `INV-`). Record in `_state.md` Decisions.

## Next step

→ [`M09-customer-wallet-loyalty.md`](./M09-customer-wallet-loyalty.md)

## Previous step

← [`M06-online-order.md`](./M06-online-order.md)
