"""M03 Catalog — error catalog (``CAT-*`` codes).

Each exception subclasses :class:`apps.core.api.exceptions.DomainError`
so it renders via the standard envelope handler.
"""

from __future__ import annotations

from apps.core.api.exceptions import DomainError


class ProductSKUDuplicate(DomainError):  # noqa: N818
    default_code = "CAT-001"
    default_message = "A product with this SKU already exists."
    default_status = 409


class ProductCodeDuplicate(DomainError):  # noqa: N818
    default_code = "CAT-002"
    default_message = "A product with this code already exists."
    default_status = 409


class VariantSKUDuplicate(DomainError):  # noqa: N818
    default_code = "CAT-003"
    default_message = "A variant with this SKU already exists."
    default_status = 409


class ProductArchived(DomainError):  # noqa: N818
    default_code = "CAT-010"
    default_message = "Cannot mutate an archived product."
    default_status = 400


class PriceNotFound(DomainError):  # noqa: N818
    default_code = "CAT-020"
    default_message = "No active price band for this item at the requested branch."
    default_status = 404


class PriceTargetInvalid(DomainError):  # noqa: N818
    default_code = "CAT-021"
    default_message = "Price must target exactly one of product or variant."
    default_status = 400


class PriceWindowInvalid(DomainError):  # noqa: N818
    default_code = "CAT-022"
    default_message = "valid_to must be after valid_from."
    default_status = 400


class BundleFixedPriceMissing(DomainError):  # noqa: N818
    default_code = "CAT-030"
    default_message = "Bundle with FIXED policy must declare fixed_price."
    default_status = 400


class BundleEmpty(DomainError):  # noqa: N818
    default_code = "CAT-031"
    default_message = "Bundle must contain at least one component."
    default_status = 400


class BarcodeTargetInvalid(DomainError):  # noqa: N818
    default_code = "CAT-040"
    default_message = "Barcode must target exactly one of product or variant."
    default_status = 400


class ImportRowsInvalid(DomainError):  # noqa: N818
    default_code = "CAT-050"
    default_message = "One or more import rows failed validation."
    default_status = 400


__all__ = [
    "BarcodeTargetInvalid",
    "BundleEmpty",
    "BundleFixedPriceMissing",
    "ImportRowsInvalid",
    "PriceNotFound",
    "PriceTargetInvalid",
    "PriceWindowInvalid",
    "ProductArchived",
    "ProductCodeDuplicate",
    "ProductSKUDuplicate",
    "VariantSKUDuplicate",
]
