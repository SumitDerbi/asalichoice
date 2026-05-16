"""M01 master-management error codes.

Each error subclasses :class:`apps.core.api.exceptions.DomainError` so it
renders via the standard error envelope.
"""

from __future__ import annotations

from apps.core.api.exceptions import DomainError


class BranchCodeDuplicate(DomainError):  # noqa: N818
    default_code = "MST-001"
    default_message = "Branch code already exists."
    default_status = 409


class CategoryDepthExceeded(DomainError):  # noqa: N818
    default_code = "MST-010"
    default_message = "Category hierarchy exceeds maximum depth."
    default_status = 400


class BranchDepthExceeded(DomainError):  # noqa: N818
    default_code = "MST-011"
    default_message = "Branch hierarchy exceeds maximum depth."
    default_status = 400


class TaxComponentsMismatch(DomainError):  # noqa: N818
    default_code = "MST-020"
    default_message = "Tax components do not match rate_total."
    default_status = 400


class PincodeNotInZone(DomainError):  # noqa: N818
    default_code = "MST-030"
    default_message = "No zone covers the requested pincode."
    default_status = 404


__all__ = [
    "BranchCodeDuplicate",
    "BranchDepthExceeded",
    "CategoryDepthExceeded",
    "PincodeNotInZone",
    "TaxComponentsMismatch",
]
