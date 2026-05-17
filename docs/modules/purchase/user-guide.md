# User guide — Vendor & Purchase

This guide walks through the day-to-day flow for buyers, store
receivers, and accounts payable staff.

## Vendors

1. **Create a vendor**: open `/purchase/vendors`, click **Create**,
   enter at minimum `Code` and `Name`. GSTIN is validated against the
   standard 15-character format when supplied.
2. **Deactivate**: use the row action. Deactivated vendors stay in
   the ledger but cannot be selected for new POs.

## Purchase Orders

1. **Create a PO** (via API or future UI form) with vendor, branch,
   and one or more line items (product + UoM + qty + rate).
2. **Submit** to move from `DRAFT` → `PENDING_APPROVAL`.
3. **Approve**: a privileged user with `purchase.po.approve` clicks
   **Approve**. The approval threshold (configured at
   `purchase.po.approval_thresholds`) determines which approver tier
   is required.
4. **Cancel** is allowed up to and including `APPROVED`.

## Goods Receipts (GRN)

1. **Create a GRN** against an approved PO (or as a direct receipt).
   Fill in received / accepted / rejected quantities, batch number,
   manufacture / expiry dates, and per-line cost.
2. **Submit** moves the GRN to `SUBMITTED`.
3. **Approve** is the **single inventory-write moment** for the
   procure cycle — it bumps warehouse stock (M05 will land the write;
   today the seam logs the intended movement). Approval is
   irreversible.
4. **Reject** requires a free-text reason which is stored on the GRN
   and surfaced in audit reports.

### Offline GRN sync

Store devices can buffer GRNs offline and push a batch via
`POST /api/v1/purchase/grns/sync-offline/`. Each receipt carries a
client-generated `offline_uuid`; the server treats the call as
idempotent against that key.

## Purchase Invoices

1. **From GRNs**: once one or more GRNs against a vendor are approved
   (and not yet billed), call `POST /invoices/from-grns/` to draft a
   matching invoice. The system rolls up totals and ties the invoice
   to those GRNs.
2. **Post** the invoice (`DRAFT` → `POSTED`). This writes a **credit**
   entry to the vendor ledger.
3. **Pay** records a partial or full payment. Status moves to
   `PART_PAID` or `PAID`. Each payment writes a **debit** entry to the
   ledger.

## Returns

1. **Draft a return** referencing an approved GRN and the items being
   returned.
2. **Post** the return — writes a debit ledger entry (reducing what we
   owe the vendor) and triggers the M05 reverse-stock seam.

## Vendor ledger

`/purchase/ledger` is read-only. Filter by vendor ID to see all
entries in timestamp order. Every row carries `reference_type` and
`reference_id` so you can trace back to the source document.

The ledger is immutable: rows are never updated or deleted. Mistakes
are corrected by a compensating entry, not by editing history.
