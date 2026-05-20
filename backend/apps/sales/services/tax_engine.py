"""Tax engine — thin wrapper around :func:`apps.master.api_public.compute_tax`.

Sale lines may carry a :class:`apps.master.models.Tax` reference. The
master service already knows how to break an amount into IGST/CGST/SGST
components and respects ``Tax.components_json``. We only:

* default the ``inclusive`` flag from the sale's ``tax_mode``;
* aggregate component sums into ``tax_total``;
* return a stable, JSON-serialisable shape that ``SaleItem.tax_breakup_json``
  can store verbatim.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from apps.master.api_public import compute_tax
from apps.master.models import Tax

from ..models import TaxMode

_ZERO = Decimal("0")


def compute_line(
    *,
    line_subtotal: Decimal,
    tax: Tax | None,
    tax_mode: str,
) -> dict[str, Any]:
    """Return the breakup payload for a single sale line.

    The shape matches what we want to store in
    :attr:`apps.sales.models.SaleItem.tax_breakup_json`::

        {
            "base": "100.0000",
            "tax_total": "18.0000",
            "grand_total": "118.0000",
            "components": [
                {"type": "IGST", "rate": "18.000", "amount": "18.0000"}
            ]
        }
    """

    if tax is None or line_subtotal == _ZERO:
        return {
            "base": str(line_subtotal),
            "tax_total": "0",
            "grand_total": str(line_subtotal),
            "components": [],
        }

    inclusive = tax_mode == TaxMode.INCLUSIVE
    breakup = compute_tax(line_subtotal, tax.pk, inclusive=inclusive)

    return {
        "base": str(breakup["base"]),
        "tax_total": str(breakup["tax_total"]),
        "grand_total": str(breakup["grand_total"]),
        "components": [
            {
                "type": comp["type"],
                "rate": str(comp["rate"]),
                "amount": str(comp["amount"]),
            }
            for comp in breakup["components"]
        ],
    }


__all__ = ["compute_line"]
