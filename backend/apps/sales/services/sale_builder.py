"""Sale builder — pure (no DB writes) computation of line + header totals.

Given a sale and its list of items (already populated with ``qty``,
``sale_price``, ``discount_amount``, ``tax``), recompute:

* per-line ``line_subtotal``, ``tax_breakup_json``, ``line_total``
* header ``subtotal``, ``tax_total``, ``grand_total``
* JSON snapshot stored in ``Sale.totals_json``

Caller persists the mutations afterwards (typically inside the
``sale_service`` transaction).
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from ..models import Sale, SaleItem
from . import tax_engine

_ZERO = Decimal("0")
_QUANT_MONEY = Decimal("0.0001")
_QUANT_BILL = Decimal("0.01")  # final grand_total rounded to paise


def _q(value: Decimal, *, places: Decimal = _QUANT_MONEY) -> Decimal:
    return value.quantize(places, rounding=ROUND_HALF_UP)


def recompute(sale: Sale, items: list[SaleItem]) -> dict:
    """Mutate ``sale`` + each item in place; return ``totals_json`` shape.

    The ``totals_json`` shape is::

        {
            "subtotal": "1000.0000",
            "line_discount_total": "50.0000",
            "header_discount_total": "100.0000",
            "discount_total": "150.0000",
            "tax_total": "153.0000",
            "grand_total": "1003.0000",
            "rounded_grand_total": "1003.00"
        }
    """

    subtotal = _ZERO
    line_discount_total = _ZERO
    tax_total = _ZERO

    for item in items:
        line_gross = item.qty * item.sale_price
        item.line_subtotal = _q(line_gross - item.discount_amount)
        line_discount_total += item.discount_amount

        breakup = tax_engine.compute_line(
            line_subtotal=item.line_subtotal,
            tax=item.tax,
            tax_mode=sale.tax_mode,
        )
        item.tax_breakup_json = breakup
        item_tax_total = Decimal(breakup["tax_total"])
        # In INCLUSIVE mode the line_subtotal already contains tax; we
        # store the same value as line_total so totals match the
        # printed bill exactly.
        item.line_total = _q(Decimal(breakup["grand_total"]))
        tax_total += item_tax_total
        subtotal += item.line_subtotal

    sale.subtotal = _q(subtotal)
    sale.tax_total = _q(tax_total)
    # ``sale.discount_total`` on entry carries any header-level discount
    # already applied by the service layer. Line-level discounts are
    # already baked into ``line_subtotal`` (and thus into ``subtotal``),
    # so only the header discount is subtracted again from grand_total.
    header_discount_total = sale.discount_total
    discount_total = header_discount_total + line_discount_total
    sale.discount_total = _q(discount_total)

    if sale.tax_mode == "INCLUSIVE":
        grand_total = sale.subtotal - header_discount_total
    else:
        grand_total = sale.subtotal + sale.tax_total - header_discount_total
    sale.grand_total = _q(grand_total)

    payload = {
        "subtotal": str(sale.subtotal),
        "line_discount_total": str(_q(line_discount_total)),
        "header_discount_total": str(_q(header_discount_total)),
        "discount_total": str(sale.discount_total),
        "tax_total": str(sale.tax_total),
        "grand_total": str(sale.grand_total),
        "rounded_grand_total": str(_q(sale.grand_total, places=_QUANT_BILL)),
        "tax_mode": sale.tax_mode,
    }
    sale.totals_json = payload
    return payload


__all__ = ["recompute"]
