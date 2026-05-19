"""M05 Inventory — error catalog.

``INV-*`` codes target inventory ledger / stock movements, transfers,
counts, and wastage. Full code stubs land alongside their services in
subsequent steps; only the ledger-boundary guard (``INV-010``) is
finalised at scaffolding time because services in later steps depend on
it.
"""

from __future__ import annotations

from apps.core.api.exceptions import DomainError


class InsufficientStock(DomainError):  # noqa: N818
    """Raised by ``ledger_service.post`` when ``qty_after < 0``.

    The negative-stock guard is the single hard block enforced at the
    ledger boundary; offline POS replays must also surface this code.
    """

    default_code = "INV-010"
    default_message = "Insufficient stock for the requested movement."
    default_status = 409


class InvalidTransferState(DomainError):  # noqa: N818
    """Raised when a BranchTransfer transition is invalid (e.g. dispatch on
    a non-DRAFT transfer, receive on a non-DISPATCHED transfer)."""

    default_code = "INV-020"
    default_message = "Branch transfer is not in a valid state for this action."
    default_status = 409


class InvalidDocumentState(DomainError):  # noqa: N818
    """Raised when a stock document (adjustment, wastage, physical count)
    is not in a state that permits the requested transition."""

    default_code = "INV-030"
    default_message = "Document is not in a valid state for this action."
    default_status = 409


class UnknownReasonCode(DomainError):  # noqa: N818
    """Raised when a referenced reason code is not registered in the
    reason-code seeder catalog."""

    default_code = "INV-031"
    default_message = "Unknown inventory reason code."
    default_status = 400


__all__ = [
    "InsufficientStock",
    "InvalidTransferState",
    "InvalidDocumentState",
    "UnknownReasonCode",
]
