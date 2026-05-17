# ADR-006 — Pricing bands

- **Status**: Accepted
- **Date**: 2026-05-25
- **Decider**: backend team
- **Context plan**: `plans/phase-1-modules/M03-catalog.md`

## Context

Phase-1 catalog needs to answer one question for every POS scan,
storefront page render, and cart update:

> What is the right price for this product (or variant) at this
> branch, **right now**?

The price must support:

1. **Branch scoping** — each store decides its own retail price. A
   single SKU may be ₹120 at the HQ store, ₹125 at a satellite, and
   ₹118 at a dark-store.
2. **Effective-date scheduling** — operations rolls out price hikes
   on a known date and reverts promo prices when an offer ends. They
   want to "queue" tomorrow's price today, without a midnight CRON.
3. **Variant-level overrides** — most products price uniformly across
   variants (size/color), but some (e.g. larger pack sizes) have a
   per-variant price that must override the parent product price.
4. **Audit & reversal** — every price write is logged with actor and
   IP; a wrong band must be revertible without rewriting history.

## Decision

`ProductPrice` is a **price band** scoped to (target, branch, date
window):

```python
class ProductPrice(BaseModel):
    product = FK(Product, null=True)
    variant = FK(ProductVariant, null=True)
    branch_id = PositiveIntegerField()
    mrp = Decimal(12, 2)
    sale_price = Decimal(12, 2)
    valid_from = DateTimeField()
    valid_to = DateTimeField(null=True)   # NULL = open-ended

    class Meta:
        constraints = [
            CheckConstraint(
                name="catalog_price_xor_target",
                check=Q(product__isnull=False) ^ Q(variant__isnull=False),
            ),
        ]
```

Resolution algorithm (in `pricing_service.get_effective_price`):

```text
1. at = at or now()
2. Filter bands:  target == (product | variant)
                  AND branch_id == requested
                  AND valid_from <= at
                  AND (valid_to IS NULL OR valid_to > at)
                  AND is_active = True
3. Order by -valid_from, take first.
4. If variant-target lookup misses, fall back to product-target lookup
   for the variant's parent product.
```

Bands are **never updated in place** — to change tomorrow's price,
deactivate the current band and insert a new one. This makes the
`AuditLog` row sequence read as a clean history.

Cache uses a versioned namespace
(`catalog:prices:v{version}:…`) with `bump_version()` called from a
`post_save` / `post_delete` signal — so a single price write
invalidates every cached read in O(1).

## Why not …

- **Per-branch override table** (`Product.base_price` +
  `BranchPriceOverride`): Two writeable surfaces, no audit trail of
  "what was the price last Friday", no way to schedule a future
  change without a CRON.
- **Single price column on `Product`**: Cannot price-differentiate
  per branch. Cannot schedule. Killed the design immediately.
- **Percent-discount layers** (base price + discount stack): Too much
  reasoning at read time. POS would need to recompute three rules per
  scan. Defer to phase-2 promotions, which sit _on top_ of the
  effective band.
- **Single combined `(product, variant)` FK with `NULL` allowed on
  one side**: We do this — but **with a DB `CheckConstraint` for
  XOR**, not just at serializer level. The DB enforces the invariant
  even for `bulk_create` paths (e.g. CSV import) that bypass DRF
  validation.

## Consequences

- POS / cart paths read one row per lookup; the bulk endpoint batches
  via `IN (...)` on `(target, branch)` tuples and stays single-query.
- "What was the price on 2026-04-10 at HQ?" is answered by re-running
  `get_effective_price(..., at=that_date)` — no time-travel migration
  needed.
- Promotional price rollback = deactivate the most recent band; the
  prior open-ended band auto-takes over because of the
  `order_by('-valid_from')` rule.
- Schema is denormalised (every band carries `branch_id` and
  redundant `mrp`/`sale_price` pairs), but the read pattern (always
  filtered by branch) makes that acceptable. Estimated 5–10 bands per
  product per branch over a year — well within row-count budgets.
- The XOR constraint surfaces as `CAT-021` from the serializer and
  `IntegrityError` from raw `bulk_create` — the import service
  translates the latter into a friendly per-row error.

## Follow-ups

- **Promotions layer** (phase-2): coupon/percent/BOGO rules that
  reference the effective band but don't mutate it.
- **Vendor cost bands** (M04): the same shape will be reused for
  `VendorPrice` with a `vendor_id` instead of `branch_id`. Considered
  factoring out a generic `PriceBand` abstract model — deferred
  because the join columns differ enough that the abstraction would
  leak.
- **Per-currency bands**: phase-3, when we open the marketplace.
  Currency is implied by `branch_id` today.
- **`ProductPrice.created_by` retention**: Audit already captures the
  actor; we may drop the column once the audit query path is in.
