# ADR-001 — Migration policy

- **Status**: Accepted
- **Date**: 2026-05-15
- **Decider**: backend team
- **Context plan**: `plans/phase-0-foundation/005-database-schema-baseline.md`

## Context

We are about to start shipping migrations across ~20 modules. Without a
shared policy we will hit two common failure modes: (1) sweeping
auto-squashes that hide intent and make rollbacks ambiguous, and (2)
data backfills entangled with schema changes that cannot be replayed
safely. Both have bitten previous teams on similar Django stacks.

## Decision

1. **One migration per logical change.** A migration corresponds to one
   reviewable unit of work — a new field, a new model, a backfill — not
   to a session's accumulated edits. `makemigrations` output that bundles
   unrelated tables must be split before commit.

2. **Squash only at module boundaries.** A module (e.g. M03 inventory)
   may run a `squashmigrations` pass immediately before its `module-merge`
   into `main`. After merge the squashed migration is frozen — no more
   squashing for that module unless a future ADR overrides this.

3. **Data migrations live in their own files.** Never mix a schema
   operation (`AddField`, `RemoveField`, `AlterField`) with a
   `RunPython` data backfill in the same migration. Generate the schema
   migration first, then a follow-up `makemigrations --empty` data
   migration that depends on it. Each `RunPython` must define both
   `forwards` and `reverse` callables; if the reverse is impossible,
   spell that out explicitly (`migrations.RunPython.noop` plus a comment).

4. **Never edit a merged migration.** Once a migration is on `main` it
   is immutable. Fix-forward with a new migration. The only exceptions
   are pre-merge rebases of your own branch.

5. **Migration names are descriptive.** Rename
   `0007_auto_20260515_1023.py` to `0007_add_invoice_idempotency_key.py`
   before commit. `auto_*` names are blocked by code review.

6. **Custom DB constraints survive `makemigrations`.** Constraints
   declared via `Meta.constraints` / `Meta.indexes` are mandatory for
   uniqueness, soft-delete uniqueness, and ledger immutability; never
   rely on application-only checks for invariants.

7. **Forward-only in production.** Production deploys run `migrate`
   without `--fake` or `--fake-initial`. Rollbacks are achieved by
   shipping a new migration that undoes the change, not by replaying
   `migrate <app> <previous>`.

## Consequences

- Reviewers can read a migration in isolation and reason about its
  effect.
- `migrate --plan` output stays readable as the platform grows.
- Squashing is bounded — we never end up with a 200-migration history
  per app.
- Data backfills can be re-run against a copy of production without
  re-executing schema changes.

## Alternatives considered

- _Auto-squash on every release branch_: rejected because it discards
  audit trail and makes hotfixes painful when a squash collides with an
  in-flight migration on a long-lived branch.
- _No squashing at all_: rejected because new contributors spend too
  long replaying hundreds of historical migrations on a fresh checkout.
