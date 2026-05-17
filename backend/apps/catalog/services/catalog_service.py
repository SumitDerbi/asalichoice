"""Product / variant / bundle write operations.

Wraps a thin business-rule layer so viewsets stay declarative.
"""

from __future__ import annotations

from typing import Any

from django.db import IntegrityError, transaction

from ..exceptions import ProductArchived, ProductCodeDuplicate, ProductSKUDuplicate
from ..models import Product, ProductStatus


@transaction.atomic
def create_product(**fields: Any) -> Product:
    """Create a product, normalising duplicate-key errors into typed
    domain exceptions for the standard error envelope.
    """

    try:
        return Product.objects.create(**fields)
    except IntegrityError as exc:
        msg = str(exc).lower()
        if "sku" in msg:
            raise ProductSKUDuplicate() from exc
        if "code" in msg:
            raise ProductCodeDuplicate() from exc
        raise


@transaction.atomic
def update_product(product: Product, **fields: Any) -> Product:
    """Update mutable fields on a product.

    Archived products cannot be edited beyond an explicit
    ``status`` flip back to ACTIVE/DRAFT.
    """

    if product.status == ProductStatus.ARCHIVED and "status" not in fields:
        raise ProductArchived()
    for key, value in fields.items():
        setattr(product, key, value)
    product.save()
    return product


@transaction.atomic
def archive_product(product: Product) -> Product:
    """Set ``status=ARCHIVED``. Historical sales remain queryable."""

    product.status = ProductStatus.ARCHIVED
    product.save(update_fields=["status", "updated_at"])
    return product
