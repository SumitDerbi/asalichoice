"""Discount engine — applies :class:`apps.sales.models.Discount` rows
to a :class:`apps.sales.models.Sale`.

The engine is **pure** with respect to the database: it mutates the
in-memory ``Sale`` and ``SaleItem`` instances (their ``discount_amount``
field) but never calls ``.save()``. The orchestrating service
(:mod:`sale_service`) persists results once everything is recomputed.

Two scopes:

* ``LINE`` discounts attach to each :class:`SaleItem` whose product
  matches the condition. Percent or flat per line, capped at line
  subtotal.
* ``HEADER`` discounts apply to the sale total after line discounts.
  Percent or flat at header, capped at remaining subtotal.

``condition_json`` keys honoured here (best-effort; unknown keys are
ignored so older payloads keep working):

* ``min_subtotal`` (Decimal-string): require ``subtotal >= value``
* ``applies_to_products`` / ``applies_to_variants`` (list[int])
* ``valid_from`` / ``valid_to`` (ISO date strings)
"""

from __future__ import annotations

import datetime as _dt
from collections.abc import Iterable
from decimal import Decimal

from ..exceptions import DiscountNotApplicable, DiscountRequiresApproval
from ..models import Discount, DiscountKind, DiscountScope, Sale, SaleItem

_ZERO = Decimal("0")


def _to_decimal(value) -> Decimal:
    return Decimal(str(value)) if value is not None else _ZERO


def _parse_iso_date(value: str | None) -> _dt.date | None:
    if not value:
        return None
    try:
        return _dt.date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def is_applicable(
    discount: Discount,
    *,
    sale: Sale,
    items: Iterable[SaleItem],
    today: _dt.date | None = None,
) -> bool:
    """Return ``True`` iff *discount* may be applied to *sale*.

    ``today`` is injectable for deterministic tests.
    """

    if not discount.is_active:
        return False

    today = today or _dt.date.today()
    cond = discount.condition_json or {}

    valid_from = _parse_iso_date(cond.get("valid_from"))
    if valid_from is not None and today < valid_from:
        return False
    valid_to = _parse_iso_date(cond.get("valid_to"))
    if valid_to is not None and today > valid_to:
        return False

    min_subtotal = cond.get("min_subtotal")
    if min_subtotal is not None and sale.subtotal < _to_decimal(min_subtotal):
        return False

    products_filter = set(cond.get("applies_to_products") or [])
    variants_filter = set(cond.get("applies_to_variants") or [])
    if products_filter or variants_filter:
        # At least one matching line must exist for line-scope
        # discounts; header scope just needs the sale to touch a
        # qualifying product.
        for item in items:
            if item.product_id and item.product_id in products_filter:
                return True
            if item.variant_id and item.variant_id in variants_filter:
                return True
        return False

    return True


def _apply_value(*, base: Decimal, discount: Discount) -> Decimal:
    if discount.kind == DiscountKind.PERCENT:
        amount = base * discount.value / Decimal("100")
    else:
        amount = discount.value
    return min(max(amount, _ZERO), base)


def apply_line(
    discount: Discount,
    *,
    sale: Sale,
    items: list[SaleItem],
    approved: bool = False,
    today: _dt.date | None = None,
) -> Decimal:
    """Apply a ``LINE``-scope discount, distributing across matching items.

    Returns the total discount applied (sum of ``SaleItem.discount_amount``
    deltas). Items are mutated in place; the caller is responsible for
    persisting them.
    """

    if discount.scope != DiscountScope.LINE:
        raise DiscountNotApplicable(
            f"Discount {discount.code!r} is not a LINE scope discount.",
        )
    if discount.requires_approval and not approved:
        raise DiscountRequiresApproval(
            f"Discount {discount.code!r} requires approval.",
        )
    if not is_applicable(discount, sale=sale, items=items, today=today):
        raise DiscountNotApplicable(
            f"Discount {discount.code!r} is not applicable to this sale.",
        )

    cond = discount.condition_json or {}
    products_filter = set(cond.get("applies_to_products") or [])
    variants_filter = set(cond.get("applies_to_variants") or [])

    total_applied = _ZERO
    for item in items:
        if products_filter or variants_filter:
            if not (
                (item.product_id and item.product_id in products_filter)
                or (item.variant_id and item.variant_id in variants_filter)
            ):
                continue
        line_base = (item.qty * item.sale_price) - item.discount_amount
        if line_base <= _ZERO:
            continue
        line_disc = _apply_value(base=line_base, discount=discount)
        item.discount_amount += line_disc
        total_applied += line_disc
    return total_applied


def apply_header(
    discount: Discount,
    *,
    sale: Sale,
    items: list[SaleItem],
    approved: bool = False,
    today: _dt.date | None = None,
) -> Decimal:
    """Apply a ``HEADER`` discount to ``sale.discount_total``.

    Returns the amount added to ``sale.discount_total``. Caller must
    persist.
    """

    if discount.scope != DiscountScope.HEADER:
        raise DiscountNotApplicable(
            f"Discount {discount.code!r} is not a HEADER scope discount.",
        )
    if discount.requires_approval and not approved:
        raise DiscountRequiresApproval(
            f"Discount {discount.code!r} requires approval.",
        )
    if not is_applicable(discount, sale=sale, items=items, today=today):
        raise DiscountNotApplicable(
            f"Discount {discount.code!r} is not applicable to this sale.",
        )

    base = sale.subtotal - sale.discount_total
    if base <= _ZERO:
        return _ZERO
    delta = _apply_value(base=base, discount=discount)
    sale.discount_total += delta
    return delta


__all__ = ["apply_header", "apply_line", "is_applicable"]
