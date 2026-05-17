"""Catalog service layer — public seam.

Other apps must import from here, not from individual modules.
"""

from __future__ import annotations

from .catalog_service import archive_product, create_product, update_product
from .import_service import import_products_csv
from .pricing_service import bulk_lookup, get_effective_price, set_price

__all__ = [
    "archive_product",
    "bulk_lookup",
    "create_product",
    "get_effective_price",
    "import_products_csv",
    "set_price",
    "update_product",
]
