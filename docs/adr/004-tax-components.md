# ADR-004 — Tax components as JSON, not rows

- **Status**: Accepted
- **Date**: 2026-05-17
- **Decider**: backend team
- **Context plan**: `plans/phase-1-modules/M01-master-management/01-models.md`

## Context

GST in India breaks a single notional rate into 2–4 sub-components:

- Intra-state sales: CGST + SGST (each half the headline).
- Inter-state sales: IGST (the full headline).
- Some categories: an additional CESS row on top.

A tax row in the master is referenced by HSN codes, products, and
invoice lines. We need to store its breakdown in a way that:

1. Round-trips losslessly — the sum of components must equal the
   headline rate exactly.
2. Lets us add new component types in future (e.g. compensation cess
   variants) without a schema migration.
3. Renders as a single editable widget in the admin UI.
4. Reports cleanly — invoice prints itemise each component.

## Decision

`Tax` carries:

- `code` (unique) and `rate_total` (`DecimalField(max_digits=6, decimal_places=2)`).
- `components_json` — a JSON list, e.g.

  ```json
  [
    { "type": "CGST", "rate": "9.00" },
    { "type": "SGST", "rate": "9.00" }
  ]
  ```

Validation lives in `Tax.clean()` and is also called from the
serializer's `validate()` (DRF does not invoke `Model.clean()`
itself):

- `components_json` must be a list.
- Each entry must be a dict with `type ∈ {CGST, SGST, IGST, CESS}` and
  a numeric `rate`.
- The sum of `rate` values must equal `rate_total` to the cent.

Mismatches raise `TaxComponentsMismatch` (`MST-020`, 400).

## Consequences

- Adding a component type is a one-line edit to a constant tuple; no
  migration needed.
- Invoice rendering reads `tax.components_json` and produces one
  print line per component. No join. No N+1.
- The single-column representation prevents drift between "headline"
  and "breakdown" rows — by construction, they cannot disagree.
- Reports that aggregate by component type (e.g. monthly GSTR-3B
  inputs) use a JSON path expression on MySQL 8 (`JSON_EXTRACT`), which
  is acceptably fast because tax rows are few (tens, not millions) and
  the reports use the invoice-line ledger as the source of truth, not
  the tax master itself.
- The admin UI ships a small custom editor component
  (`admin-ui/src/modules/masters/forms/TaxComponentsEditor.tsx`) with
  a live total — purely advisory; the server is the truth.

## Alternatives considered

- **Separate `TaxComponent` table FK'd to `Tax`**: rejected because
  it required a join on every tax read, raised the cost of computing
  the headline rate at print time, and required a composite uniqueness
  constraint (one CGST row per tax). The JSON form encodes the same
  invariant declaratively.
- **Columns `cgst`, `sgst`, `igst`, `cess` on `Tax`**: rejected
  because adding new component types is a migration, and the
  unused-column pattern is brittle (we end up with `NULL` semantics
  meaning both "not configured" and "explicitly zero").
- **Compute components from `rate_total` on read**: rejected because
  some real-world taxes split asymmetrically (some products charge
  18 % as 12 + 6 IGST + CESS), so a deterministic formula doesn't
  cover the long tail.

## Follow-ups

- If the component set ever exceeds ~6 entries per tax, revisit the
  JSON path performance.
- A future component type (e.g. a regional cess) only requires
  appending to the `_COMPONENT_TYPES` constant in
  `apps/master/models.py` and a matching test in
  `tests/master/test_models.py::test_tax_clean_accepts_matching_components`.
