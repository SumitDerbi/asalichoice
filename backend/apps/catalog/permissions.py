"""M03 Catalog — permission codes.

Seeded by ``python manage.py seed_permissions``. Format follows the
``(code, name, description)`` triples expected by the seed command.
"""

from __future__ import annotations

CATALOG_PERMISSIONS: tuple[tuple[str, str, str], ...] = (
    (
        "catalog.view",
        "View catalog",
        "Read products, variants, bundles, barcodes, attributes, prices.",
    ),
    (
        "catalog.manage",
        "Manage catalog",
        "Create / update / archive products, variants, bundles, attributes.",
    ),
    (
        "catalog.price.manage",
        "Manage prices",
        "Create or update product / variant pricing bands.",
    ),
    (
        "catalog.import",
        "Import catalog data",
        "Run bulk CSV imports.",
    ),
)

__all__ = ["CATALOG_PERMISSIONS"]
