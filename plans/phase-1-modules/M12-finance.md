# M12 — Finance & Accounting

> **Phase**: phase-1-modules  **SRS ref**: Module 12  **Depends on**: M01, M02, M04, M05, M09, M11, M14  **Est. effort**: XL

## Goal

Double-entry general ledger fed by all transaction modules. Chart of Accounts, journal entries, AR/AP, expense entry, bank reconciliation, TDS, opening balances, year-end closing, P&L + Balance Sheet + Cash Flow + Trial Balance.

## Steps

1. **Models** `apps/finance/`:
   - `Account(code unique, name, type=ASSET|LIABILITY|EQUITY|INCOME|EXPENSE, parent FK self, is_postable bool, opening_balance, currency=INR)`.
   - `JournalEntry(je_no unique, date, narration, branch FK, source_type, source_id, status=DRAFT|POSTED|REVERSED, posted_at, posted_by)`.
   - `JournalLine(je FK, account FK, debit, credit, party_type nullable, party_id nullable, branch FK)`.
   - `Expense(exp_no unique, branch, category FK, vendor FK nullable, amount, tax_amount, tds_amount nullable, payment_mode FK, paid_at, receipts[], status, je FK nullable)`.
   - `BankAccount(code, name, account_no_masked, ifsc, branch FK, currency, opening_balance, is_active)`.
   - `BankTransaction(bank FK, date, amount, type=DEBIT|CREDIT, ref_no, narration, je FK nullable, status=UNRECONCILED|RECONCILED|IGNORED)`.
   - `TDSEntry(je FK, section, rate, base, amount, deductee_pan, period)`.
   - `FinancialPeriod(fy_start, fy_end, is_open, closed_at, closed_by)`.
2. **Services**:
   - `je_service.post(lines[])` — enforces sum(debit) = sum(credit); writes lines atomically.
   - `auto_posting`:
     - `sale.posted` → DR Cash/Bank/AR, CR Sales Income, CR Output Tax.
     - `grn.approved` → DR Inventory, CR AP.
     - `pi.posted` → adjusts AP; `payment` to vendor → DR AP, CR Bank.
     - `expense.create` → DR Expense + Input Tax, CR Cash/Bank/AP.
     - `cod.deposited` (M14) → DR Bank, CR Cash-in-Transit.
     - `wallet.topup` (M09) → DR Cash, CR Customer Wallet Liability.
     - `wallet.redeem` → DR Customer Wallet Liability, CR Sale (offset).
   - `bank_recon.match(bank_txn, je_lines[])` — manual + auto-match by amount+date window.
   - `closing_service.run_year_end(fy)` — close all P&L accounts into Retained Earnings; lock period.
   - `opening_balance.import_csv(file)`.
3. **Reports** (rendered as JSON; UI formats):
   - Trial Balance, P&L, Balance Sheet, Cash Flow, Account Ledger, Day Book, Aging (AR/AP), TDS Report.
4. **Error prefix**: `FIN-*`.
5. **Admin-UI**:
   - `src/modules/finance/` — CoA tree, JE list + manual JE entry, Expense entry, Bank Recon screen (side-by-side), Reports pages with date pickers + branch filters + CSV/PDF export.
   - Year-end closing wizard (confirm + lock).
6. **Permissions**: `finance.view/manage`, `finance.je.create/post/reverse`, `finance.expense.*`, `finance.bank.reconcile`, `finance.year_end_close`.
7. **Tests**: balanced JE invariant, auto-posting from every source module event, period lock prevents back-dated entries, year-end closing math.
8. **Docs**: `docs/modules/finance/*` + ADR `015-double-entry-auto-posting.md`.
9. Commit: `feat(M12): finance & accounting with auto-posting + reports`.

## Verification

### Manual
1. Run sample sale → JE auto-posted, Trial Balance balances.
2. Bank recon: import bank statement CSV → auto-match 80%+ → manual match the rest.
3. Year-end close → P&L accounts zero out, Retained Earnings updated, period locked.

### Automated
- `pytest backend/tests/finance/ -q` ≥ 90% with invariant property tests (debits=credits always).
- UI + Playwright + Newman green.

## Definition of Done

- [ ] Trial balance always balances (invariant test).
- [ ] Every source module event posts a JE.
- [ ] Year-end closing produces valid statements.
- [ ] `_state.md` advanced.

## Next step

→ [`M13-reports.md`](./M13-reports.md)

## Previous step

← [`M15-returns.md`](./M15-returns.md)
