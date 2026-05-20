"""M11 Sales — error catalog (``SAL-*`` codes)."""

from __future__ import annotations

from apps.core.api.exceptions import DomainError


class InvalidSaleState(DomainError):  # noqa: N818
    """A lifecycle transition was attempted from a state that doesn't allow it."""

    default_code = "SAL-001"
    default_message = "Sale is not in a valid state for this action."
    default_status = 409


class EmptySale(DomainError):  # noqa: N818
    """A sale was posted with zero line items."""

    default_code = "SAL-002"
    default_message = "Cannot post a sale with no items."
    default_status = 400


class PaymentTotalMismatch(DomainError):  # noqa: N818
    """``sum(payments) != grand_total`` for a non-credit sale on post."""

    default_code = "SAL-010"
    default_message = "Sum of payments does not match grand total."
    default_status = 400


class DiscountNotApplicable(DomainError):  # noqa: N818
    """Discount code is unknown, inactive, or fails its condition."""

    default_code = "SAL-020"
    default_message = "Discount is not applicable to this sale."
    default_status = 400


class DiscountRequiresApproval(DomainError):  # noqa: N818
    """A discount flagged ``requires_approval`` was applied without one."""

    default_code = "SAL-021"
    default_message = "Discount requires approval before it can be applied."
    default_status = 403


class PriceOverrideForbidden(DomainError):  # noqa: N818
    """The caller lacks ``sales.price.override`` permission."""

    default_code = "SAL-030"
    default_message = "Caller is not permitted to override line price."
    default_status = 403


class DuplicateOfflineSale(DomainError):  # noqa: N818
    """A sale with the same ``offline_uuid`` already exists (idempotent replay)."""

    default_code = "SAL-040"
    default_message = "Offline sale UUID has already been posted."
    default_status = 409


class UnknownPaymentMode(DomainError):  # noqa: N818
    """The referenced payment mode is unknown or disabled for this branch."""

    default_code = "SAL-050"
    default_message = "Payment mode is not enabled for this branch."
    default_status = 400


__all__ = [
    "DiscountNotApplicable",
    "DiscountRequiresApproval",
    "DuplicateOfflineSale",
    "EmptySale",
    "InvalidSaleState",
    "PaymentTotalMismatch",
    "PriceOverrideForbidden",
    "UnknownPaymentMode",
]
