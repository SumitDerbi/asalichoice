# Phase 1 — Modules

This phase ships the 20 SRS modules. Each module has a plan file (or folder, for the reference module M01) under this directory.

## Execution order

Per [`../_meta.yaml`](../_meta.yaml) → `module_order`:

```
M01 → M02 → M03 → M04 → M05 → M11 → M07 → M06 → M08 → M09 → M10
    → M14 → M15 → M12 → M13 → M16 → M17 → M18 → M19 → M20
```

Rationale:
- **M01 (Master)** is the spine — every other module FKs into it.
- **M02 (User & Role)** unlocks permissions for everyone downstream.
- **M03 (Catalog)** + **M04 (Vendor & PO)** before **M05 (Inventory)** because POs/GRNs feed stock.
- **M11 (Sales & Billing core)** is pulled forward so **M07 (POS)** has a stable sale lifecycle to write into.
- **M06 (Online Order)** and **M14 (Delivery)** come once sale + inventory are in place.
- **M12 (Finance)** lands later — it consumes ledgers from M04/M05/M11/M14.

## Module file convention

- **M01** is the reference module → built as a folder `M01-master-management/` with `index.md`, `01-api.md`, `02-ui.md`, `03-integration.md`, `04-tests.md`, `05-docs.md`. **All future modules should mirror this split when they exceed the 250-line single-file budget.**
- **M02–M20** start as **single files** using [`../templates/module-template.md`](../templates/module-template.md). When a module's single file exceeds the context budget, split it into a folder following the M01 pattern.

## Parallelism

Once **M01** and **M02** have landed, the following can be worked in parallel by different agents (still landing through PRs sequentially):

- M03 ⫼ M11 (M11 needs only M02; M03 needs only M01)
- M17 ⫼ M18 ⫼ M19 (independent reporting/settings/docs slices)

Strictly sequential: **M01 → M02 → M05**, **M11 → M07**, **M06 → M14**, **M04 → M05**.

## Per-module gate

A module is "Done" only when:
- [ ] API tests ≥ 85% line coverage on services.
- [ ] UI screens have Vitest tests + at least one Playwright happy-path.
- [ ] Postman collection green via newman.
- [ ] User-guide page published in MkDocs.
- [ ] Module's seeder added to `seed_all`.
- [ ] No hardcoded values (all configurable via SystemSetting where applicable).
- [ ] Audit logs verified for every write path.
- [ ] `_state.md` History row appended.

## Index

| # | Module | Plan | Status |
|---|---|---|---|
| M01 | Master Management | [folder](./M01-master-management/index.md) | not-started |
| M02 | User & Role | [M02-user-role.md](./M02-user-role.md) | not-started |
| M03 | Catalog | [M03-catalog.md](./M03-catalog.md) | not-started |
| M04 | Vendor & Purchase | [M04-vendor-purchase.md](./M04-vendor-purchase.md) | not-started |
| M05 | Inventory & Branch Transfer | [M05-inventory.md](./M05-inventory.md) | not-started |
| M06 | Online Order | [M06-online-order.md](./M06-online-order.md) | not-started |
| M07 | POS | [M07-pos.md](./M07-pos.md) | not-started |
| M08 | Invoice & Print | [M08-invoice-print.md](./M08-invoice-print.md) | not-started |
| M09 | Customer Wallet & Loyalty | [M09-customer-wallet-loyalty.md](./M09-customer-wallet-loyalty.md) | not-started |
| M10 | CRM & Referral | [M10-crm-referral.md](./M10-crm-referral.md) | not-started |
| M11 | Sales & Billing Core | [M11-sales-billing.md](./M11-sales-billing.md) | not-started |
| M12 | Finance & Accounting | [M12-finance.md](./M12-finance.md) | not-started |
| M13 | Reports & Dashboards | [M13-reports.md](./M13-reports.md) | not-started |
| M14 | Delivery & Logistics | [M14-delivery.md](./M14-delivery.md) | not-started |
| M15 | Returns & RMA | [M15-returns.md](./M15-returns.md) | not-started |
| M16 | HR & Payroll | [M16-hr-payroll.md](./M16-hr-payroll.md) | not-started |
| M17 | Notifications | [M17-notifications.md](./M17-notifications.md) | not-started |
| M18 | System Settings (full) | [M18-system-settings.md](./M18-system-settings.md) | not-started |
| M19 | Audit & Activity Log (full) | [M19-audit-log.md](./M19-audit-log.md) | not-started |
| M20 | Mobile API & Offline Sync | [M20-mobile-api-sync.md](./M20-mobile-api-sync.md) | not-started |

## Next step

→ [`M01-master-management/index.md`](./M01-master-management/index.md)

## Previous step

← [`../phase-0-foundation/014-seeders-and-defaults.md`](../phase-0-foundation/014-seeders-and-defaults.md)
