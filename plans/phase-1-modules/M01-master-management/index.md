# M01 — Master Management (index)

> **Phase**: phase-1-modules  **Module**: M01  **SRS ref**: Module 1
> **Depends on**: Phase 0 complete  **Est. effort**: L

## Purpose

The spine of the system. Owns Branches, Departments, Designations, Units of Measure (UoM), Taxes (slabs, HSN/SAC), Payment Modes, Categories/Sub-categories, Brands, Warehouses, Zones, and Geographic masters (Country/State/City/PIN). Every downstream module FKs into M01.

## Scope (from SRS Module 1)

In-scope:
- Branch (HQ, store, warehouse, dark-store) with hierarchy + branch-wise feature flags.
- Department, Designation.
- UoM + UoM conversions (case-pack, kg↔g, etc.).
- Tax slabs (CGST/SGST/IGST/Cess) bound to HSN/SAC codes.
- Payment modes (cash, UPI, card, wallet, COD) with per-branch enablement.
- Category tree (parent/child, depth ≤ 4) + Brand.
- Warehouse (linked to branch), Zone (delivery pincode polygons/ranges).
- Country / State / City / Pincode masters (seeded for India).

Out-of-scope here:
- Products (M03).
- Users (M02).

## Sub-plans (execute in order)

1. [`01-api.md`](./01-api.md) — Models, services, viewsets, endpoints, OpenAPI.
2. [`02-ui.md`](./02-ui.md) — Admin-UI screens (list, drawer-edit, branch switcher wiring).
3. [`03-integration.md`](./03-integration.md) — Wire branch context into core, expose to all modules.
4. [`04-tests.md`](./04-tests.md) — Pytest, vitest, playwright, postman.
5. [`05-docs.md`](./05-docs.md) — MkDocs page + ADRs.

## Key design decisions

- **Soft-delete** all masters; never hard-delete (referenced by ledgers).
- **Branch hierarchy** via `parent_id` self-FK; depth check in service layer.
- **Tax components** stored as JSON list on `Tax` to support mixed CGST/SGST/IGST/Cess in one record.
- **Pincode → Zone** mapping table for delivery routing (used by M06 + M14).
- **No hardcoded** payment modes / branches anywhere in code — always FK to M01.

## Definition of Done

- [ ] All 5 sub-plans green.
- [ ] Seeders ship default Country=India, all States, major cities; default branch updated.
- [ ] Branch switcher in admin shell uses real branches.
- [ ] All later modules can FK to `master.Branch`, `master.Tax`, `master.PaymentMode`, etc.
- [ ] `_state.md` History row.

## Next step

→ [`01-api.md`](./01-api.md)

## Previous step

← [`../README.md`](../README.md)
