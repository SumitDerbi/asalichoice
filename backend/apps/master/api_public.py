"""Public service API for the master app (M01/03 §2).

This module is the **stable seam** other modules import.  Internal
helpers live in :mod:`apps.master.services` and may change shape; the
functions here keep a documented signature so downstream modules
(POS, orders, finance, …) don't reach into private internals.

Anything not exported from this module is considered private.
"""

from __future__ import annotations

from decimal import Decimal

from apps.core.context import current_branch_id

from .models import Branch, PaymentMode, Tax, Zone
from .services import compute_tax_breakup
from .services import resolve_zone_for_pincode as _resolve_zone_for_pincode

__all__ = [
    "compute_tax",
    "get_current_branch",
    "get_tax_by_code",
    "is_payment_mode_enabled",
    "resolve_zone_for_pincode",
]


def get_current_branch() -> Branch | None:
    """Return the :class:`Branch` bound to this request, or ``None``."""

    branch_id = current_branch_id()
    if branch_id is None:
        return None
    return Branch.objects.filter(pk=branch_id, is_active=True).first()


def get_tax_by_code(code: str) -> Tax | None:
    """Return the active :class:`Tax` with the given code, else ``None``."""

    return Tax.objects.filter(code=code, is_active=True).first()


def compute_tax(
    amount: Decimal | float | int | str,
    tax_id: int,
    *,
    inclusive: bool = False,
) -> dict:
    """Compute the tax breakup for *amount* against the given tax id."""

    tax = Tax.objects.get(pk=tax_id)
    return compute_tax_breakup(amount, tax, inclusive=inclusive)


def is_payment_mode_enabled(branch: Branch | int, mode_code: str) -> bool:
    """Return ``True`` if *mode_code* is active for *branch*."""

    branch_id = branch.pk if isinstance(branch, Branch) else int(branch)
    return PaymentMode.objects.filter(
        code=mode_code,
        is_active=True,
        branches__id=branch_id,
    ).exists()


# Re-export for convenience.


def resolve_zone_for_pincode(pincode: str) -> Zone | None:
    """Resolve a pincode (string) to its :class:`Zone`."""

    return _resolve_zone_for_pincode(pincode)
