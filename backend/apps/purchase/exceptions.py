"""M04 Purchase — error catalog.

``VEN-*`` codes target the vendor master and ``PUR-*`` codes target the
purchase cycle (PO / GRN / PI / PR).
"""

from __future__ import annotations

from apps.core.api.exceptions import DomainError

# ---------------------------------------------------------------------------
# Vendor master
# ---------------------------------------------------------------------------


class VendorCodeDuplicate(DomainError):  # noqa: N818
    default_code = "VEN-001"
    default_message = "A vendor with this code already exists."
    default_status = 409


class VendorGSTINInvalid(DomainError):  # noqa: N818
    default_code = "VEN-002"
    default_message = "GSTIN format is invalid."
    default_status = 400


class VendorInactive(DomainError):  # noqa: N818
    default_code = "VEN-010"
    default_message = "Vendor is inactive."
    default_status = 400


# ---------------------------------------------------------------------------
# Purchase Order
# ---------------------------------------------------------------------------


class PODuplicate(DomainError):  # noqa: N818
    default_code = "PUR-001"
    default_message = "A purchase order with this number already exists."
    default_status = 409


class POInvalidTransition(DomainError):  # noqa: N818
    default_code = "PUR-009"
    default_message = "Purchase order is not in a state that allows this action."
    default_status = 400


class POAlreadyApproved(DomainError):  # noqa: N818
    default_code = "PUR-010"
    default_message = "Purchase order is already approved."
    default_status = 400


class POClosedForChanges(DomainError):  # noqa: N818
    default_code = "PUR-011"
    default_message = "Purchase order is closed and cannot be modified."
    default_status = 400


# ---------------------------------------------------------------------------
# GRN
# ---------------------------------------------------------------------------


class GRNDuplicate(DomainError):  # noqa: N818
    default_code = "PUR-020"
    default_message = "A GRN with this number already exists."
    default_status = 409


class GRNNegativeQty(DomainError):  # noqa: N818
    default_code = "PUR-021"
    default_message = "GRN quantities must be non-negative."
    default_status = 400


class GRNOverReceive(DomainError):  # noqa: N818
    default_code = "PUR-022"
    default_message = "GRN received quantity exceeds the open PO quantity."
    default_status = 400


class GRNInvalidTransition(DomainError):  # noqa: N818
    default_code = "PUR-023"
    default_message = "GRN is not in a state that allows this action."
    default_status = 400


# ---------------------------------------------------------------------------
# Purchase Invoice
# ---------------------------------------------------------------------------


class PIDuplicate(DomainError):  # noqa: N818
    default_code = "PUR-030"
    default_message = "A purchase invoice with this number already exists."
    default_status = 409


class PINoApprovedGRNs(DomainError):  # noqa: N818
    default_code = "PUR-031"
    default_message = "Cannot create a purchase invoice without at least one approved GRN."
    default_status = 400


# ---------------------------------------------------------------------------
# Offline sync
# ---------------------------------------------------------------------------


class OfflineGRNPOClosed(DomainError):  # noqa: N818
    default_code = "PUR-040"
    default_message = "Offline GRN rejected — the source PO is already closed."
    default_status = 409


class OfflineUUIDConflict(DomainError):  # noqa: N818
    default_code = "PUR-041"
    default_message = "Offline UUID payload does not match the existing GRN."
    default_status = 409


# ---------------------------------------------------------------------------
# Returns
# ---------------------------------------------------------------------------


class ReturnQtyExceedsReceipt(DomainError):  # noqa: N818
    default_code = "PUR-050"
    default_message = "Return quantity exceeds what was received on the GRN."
    default_status = 400


__all__ = [
    "GRNDuplicate",
    "GRNInvalidTransition",
    "GRNNegativeQty",
    "GRNOverReceive",
    "OfflineGRNPOClosed",
    "OfflineUUIDConflict",
    "PIDuplicate",
    "PINoApprovedGRNs",
    "POAlreadyApproved",
    "POClosedForChanges",
    "PODuplicate",
    "POInvalidTransition",
    "ReturnQtyExceedsReceipt",
    "VendorCodeDuplicate",
    "VendorGSTINInvalid",
    "VendorInactive",
]
