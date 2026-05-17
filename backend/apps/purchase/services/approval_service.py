"""Approval routing — reads thresholds from SystemSetting.

Setting key: ``purchase.po.approval_thresholds`` (GLOBAL by default,
optionally BRANCH-overridable). Schema::

    [
        {"min_amount": "50000", "approver_role": "MANAGER"},
        {"min_amount": "200000", "approver_role": "DIRECTOR"}
    ]

``required_approvers(po)`` returns the list of role codes (in order)
that must approve the supplied PO. Empty list = no approval required.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from apps.system_settings.services import get_setting

_SETTING_KEY = "purchase.po.approval_thresholds"


def _po_amount(po) -> Decimal:
    """Compute the gross amount of a PO from its totals_json or items."""

    totals = po.totals_json or {}
    if "grand_total" in totals:
        try:
            return Decimal(str(totals["grand_total"]))
        except (ArithmeticError, TypeError, ValueError):
            pass
    total = Decimal("0")
    for item in po.items.all():
        total += Decimal(str(item.line_total or 0))
    return total


def required_approvers(po, *, branch_id: int | None = None) -> list[str]:
    """Return ordered list of role codes whose approval is required."""

    raw: Any = get_setting(_SETTING_KEY, default=[], branch=branch_id)
    if not isinstance(raw, list):
        return []
    amount = _po_amount(po)
    matched: list[tuple[Decimal, str]] = []
    for tier in raw:
        if not isinstance(tier, dict):
            continue
        try:
            threshold = Decimal(str(tier.get("min_amount", "0")))
        except (ArithmeticError, TypeError, ValueError):
            continue
        role = str(tier.get("approver_role", "")).strip()
        if not role:
            continue
        if amount >= threshold:
            matched.append((threshold, role))
    matched.sort(key=lambda pair: pair[0])
    return [role for _threshold, role in matched]


__all__ = ["required_approvers"]
