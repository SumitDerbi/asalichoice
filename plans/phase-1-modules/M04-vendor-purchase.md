# M04 — Vendor & Purchase

> **Phase**: phase-1-modules  **SRS ref**: Module 4  **Depends on**: M01, M02, M03  **Est. effort**: L

## Goal

End-to-end purchase cycle: Vendor master → PO → GRN (Goods Receipt Note, the **only** doc that writes stock) → Purchase Invoice → Vendor Ledger → Returns. Includes offline-capable GRN with sync queue and configurable approval thresholds.

## Steps

1. **Models** `apps/purchase/`:
   - `Vendor(code unique, name, contact, gstin, pan, addresses[], payment_terms_json, credit_limit, branches M2M, is_active)`.
   - `VendorContact(vendor FK, name, role, email, mobile)`.
   - `VendorBankAccount(vendor FK, account_no_masked, ifsc, bank_name, is_default)`.
   - `PurchaseOrder(po_no unique, vendor FK, branch FK, status=DRAFT|PENDING_APPROVAL|APPROVED|PARTIAL|RECEIVED|CLOSED|CANCELLED, expected_delivery, terms, totals_json, approval_chain_json, created_by, approved_by, approved_at)`.
   - `POItem(po FK, product/variant FK, qty, uom FK, rate, tax FK, discount, line_total)`.
   - `GRN(grn_no unique, po FK nullable, vendor FK, branch FK, status=DRAFT|SUBMITTED|APPROVED|REJECTED, received_at, vehicle_no, transporter, created_by, offline_uuid nullable)`.
   - `GRNItem(grn FK, po_item FK nullable, product/variant FK, qty_received, qty_accepted, qty_rejected, rejection_reason, batch_no, mfg_date, expiry_date, cost_price)`.
   - `PurchaseInvoice(pi_no unique, vendor FK, grns M2M, branch FK, invoice_no_vendor, invoice_date, due_date, totals_json, status=DRAFT|POSTED|PAID|PART_PAID|CANCELLED, payment_terms)`.
   - `PurchaseReturn(pr_no unique, grn FK, reason, status, items[], totals_json)`.
   - `VendorLedger(vendor, branch, ref_type, ref_id, debit, credit, balance_after, ts, remarks)` — subclass of `LedgerEntry`.
2. **Services**:
   - `po_service.create/submit/approve/cancel`.
   - `grn_service.create/submit/approve/reject` — **on approve**: write `InventoryLedger` rows (M05), upsert Batch (M05), update vendor outstanding.
   - `purchase_invoice_service.create_from_grns(grn_ids)` (auto-aggregate).
   - `purchase_return_service.create/post` — reverses inventory + creates debit note.
   - `approval_service.required_approvers(doc)` — reads thresholds from SystemSetting (no hardcoding).
3. **Offline GRN**:
   - Mobile/PWA can create GRN with client-generated `offline_uuid` → server dedupes on uuid.
   - Sync queue + conflict resolution: if PO already closed → reject sync with `PUR-040`; if partial → server merges.
4. **Error prefix**: `VEN-*` for vendor master, `PUR-*` for transactional.
5. **Endpoints**: `/api/v1/purchase/vendors|pos|grns|invoices|returns|ledger`.
6. **Admin-UI**:
   - `src/modules/vendors/` — list, drawer-edit.
   - `src/modules/purchase/` — PO wizard (multi-step), GRN entry with batch/expiry, PI auto-create modal, returns flow.
   - Approval inbox widget (top-bar bell counts pending approvals).
   - Vendor 360 page: outstanding, ledger, POs, GRNs.
7. **Permissions**: `purchase.po.view/create/approve`, `purchase.grn.view/create/approve`, `purchase.invoice.*`, `purchase.return.*`, plus per-branch scoping.
8. **Stock policy**: PO never writes stock. GRN approval writes stock. Hard-block negative receipt qty.
9. **Tests/Postman/Playwright**: end-to-end PO → GRN → PI happy path; partial GRN; offline GRN sync conflict.
10. **Docs**: `docs/modules/purchase/*` + ADR `007-grn-only-stock-write.md`.
11. Commit: `feat(M04): vendor + purchase cycle`.

## Verification

### Manual
1. Approve PO → DOES NOT touch stock. GRN approved → stock increases. PR posted → stock decreases.
2. Configure threshold "PO > ₹50k requires Manager approval" → submit PO ₹60k → routes to manager.
3. Offline GRN from mobile (simulate) → sync → no duplicate.

### Automated
- `pytest backend/tests/purchase/ -q` ≥ 85%.
- UI + Playwright + Newman green.

## Definition of Done

- [ ] Full cycle works.
- [ ] Approval thresholds configurable via SystemSetting.
- [ ] Offline sync verified.
- [ ] `_state.md` advanced.

## Next step

→ [`M05-inventory.md`](./M05-inventory.md)

## Previous step

← [`M03-catalog.md`](./M03-catalog.md)
