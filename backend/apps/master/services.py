"""Service layer for M01 Master Management.

Per ADR-002 (view → service → ORM), all writes route through services so
audit, validation, and business rules live in one place.

Public surface:
* :func:`compute_tax_breakup` — used by M07/M08/M11 for pricing.
* :func:`resolve_zone_for_pincode` — used by M06/M14 for routing.
* :func:`check_category_depth` — enforces the 4-level cap.
* :func:`check_branch_depth` — guards self-referential hierarchies.
* :func:`activate_payment_mode_for_branch` / :func:`deactivate_*` — toggle
  the M2M without leaking signal calls into views.
"""

from __future__ import annotations

from collections.abc import Iterable
from decimal import ROUND_HALF_UP, Decimal

from django.core.exceptions import ValidationError

from apps.core.api.exceptions import DomainError

from .models import Branch, Category, PaymentMode, Pincode, Tax, TaxComponentType, Zone

CATEGORY_MAX_DEPTH = 4
BRANCH_MAX_DEPTH = 4


# ---------------------------------------------------------------------------
# Branch / Category hierarchy guards
# ---------------------------------------------------------------------------


def check_branch_depth(parent: Branch | None) -> int:
    """Return the depth a new child of ``parent`` would occupy.

    Raises :class:`DomainError` ``MST-011`` if the chain would exceed
    :data:`BRANCH_MAX_DEPTH`.
    """

    depth = 1
    node = parent
    seen: set[int] = set()
    while node is not None:
        if node.pk in seen:
            raise DomainError(
                "Branch parent chain is cyclic.",
                code="MST-012",
                status=400,
            )
        seen.add(node.pk)
        depth += 1
        node = node.parent
    if depth > BRANCH_MAX_DEPTH:
        raise DomainError(
            f"Branch hierarchy exceeds the maximum depth of {BRANCH_MAX_DEPTH}.",
            code="MST-011",
            status=400,
        )
    return depth


def check_category_depth(parent: Category | None) -> int:
    """Return the depth a new child of ``parent`` would occupy.

    Raises :class:`DomainError` ``MST-010`` if the chain would exceed
    :data:`CATEGORY_MAX_DEPTH`.
    """

    depth = 1
    node = parent
    seen: set[int] = set()
    while node is not None:
        if node.pk in seen:
            raise DomainError(
                "Category parent chain is cyclic.",
                code="MST-013",
                status=400,
            )
        seen.add(node.pk)
        depth += 1
        node = node.parent
    if depth > CATEGORY_MAX_DEPTH:
        raise DomainError(
            f"Category hierarchy exceeds the maximum depth of {CATEGORY_MAX_DEPTH}.",
            code="MST-010",
            status=400,
        )
    return depth


# ---------------------------------------------------------------------------
# Tax breakup
# ---------------------------------------------------------------------------


_QUANT = Decimal("0.01")


def _q(value: Decimal) -> Decimal:
    return value.quantize(_QUANT, rounding=ROUND_HALF_UP)


def compute_tax_breakup(
    amount: Decimal | float | int | str,
    tax: Tax,
    *,
    inclusive: bool = False,
) -> dict:
    """Return ``{base, components: [...], tax_total, grand_total}``.

    * If ``inclusive`` is True, ``amount`` already contains tax — we back out
      the base then re-apply each component.
    * Component rates are pulled from ``tax.components_json``; if no
      components are defined the function falls back to ``tax.rate_total``
      and emits a single ``IGST`` entry.
    """

    amount_dec = Decimal(str(amount))
    rate_total = Decimal(str(tax.rate_total))

    if inclusive:
        # base + base * (rate/100) = amount  →  base = amount / (1 + rate/100)
        divisor = Decimal("1") + (rate_total / Decimal("100"))
        base = amount_dec / divisor
    else:
        base = amount_dec

    components: list[dict] = []
    components_meta: Iterable[dict] = (
        tax.components_json
        if tax.components_json
        else [{"type": TaxComponentType.IGST.value, "rate": rate_total}]
    )
    tax_total = Decimal("0")
    for comp in components_meta:
        rate = Decimal(str(comp["rate"]))
        component_amount = base * rate / Decimal("100")
        components.append(
            {
                "type": comp["type"],
                "rate": rate,
                "amount": _q(component_amount),
            }
        )
        tax_total += component_amount

    return {
        "base": _q(base),
        "components": components,
        "tax_total": _q(tax_total),
        "grand_total": _q(base + tax_total),
    }


# ---------------------------------------------------------------------------
# Zone resolution
# ---------------------------------------------------------------------------


def resolve_zone_for_pincode(pincode: str | Pincode) -> Zone | None:
    """Return the active :class:`Zone` covering ``pincode`` or ``None``.

    Resolution order:
    1. Direct M2M membership via :class:`Pincode`.
    2. Numeric range matching against ``Zone.pincode_ranges_json``.
    """

    code = pincode.code if isinstance(pincode, Pincode) else str(pincode).strip()
    if not code:
        return None

    zone = Zone.objects.filter(pincodes__code=code, is_active=True).select_related("branch").first()
    if zone is not None:
        return zone

    try:
        numeric = int(code)
    except ValueError:
        return None

    for zone in Zone.objects.filter(is_active=True):
        for r in zone.pincode_ranges_json or []:
            try:
                lo = int(r["from"])
                hi = int(r["to"])
            except (KeyError, TypeError, ValueError):
                continue
            if lo <= numeric <= hi:
                return zone
    return None


# ---------------------------------------------------------------------------
# Branch ↔ PaymentMode toggle helpers
# ---------------------------------------------------------------------------


def activate_payment_mode_for_branch(mode: PaymentMode, branch: Branch) -> None:
    mode.branches.add(branch)


def deactivate_payment_mode_for_branch(mode: PaymentMode, branch: Branch) -> None:
    mode.branches.remove(branch)


# ---------------------------------------------------------------------------
# Convenience for serializers — surface ``model.clean()`` errors as DRF errors.
# ---------------------------------------------------------------------------


def validate_model(instance) -> None:
    """Run ``instance.clean()`` and re-raise Django ``ValidationError`` as-is.

    DRF serializers will catch the raised exception and translate to the
    standard API envelope via ``envelope_exception_handler``.
    """

    try:
        instance.clean()
    except ValidationError:
        raise


__all__ = [
    "BRANCH_MAX_DEPTH",
    "CATEGORY_MAX_DEPTH",
    "activate_payment_mode_for_branch",
    "check_branch_depth",
    "check_category_depth",
    "compute_tax_breakup",
    "deactivate_payment_mode_for_branch",
    "resolve_zone_for_pincode",
    "validate_model",
]
