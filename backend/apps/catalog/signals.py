"""Catalog signals — audit logging and price-cache invalidation."""

from __future__ import annotations

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.core.audit.models import AuditAction
from apps.core.audit.service import audit

from .models import Product, ProductPrice, ProductVariant
from .services.pricing_service import bump_version


@receiver(post_save, sender=ProductPrice)
def _invalidate_price_cache_on_save(sender, instance, **kwargs):
    bump_version()


@receiver(post_delete, sender=ProductPrice)
def _invalidate_price_cache_on_delete(sender, instance, **kwargs):
    bump_version()


@receiver(post_save, sender=ProductPrice)
def _audit_price_change(sender, instance, created, **kwargs):
    audit(
        model="catalog.ProductPrice",
        object_id=instance.pk,
        action=AuditAction.CREATE if created else AuditAction.UPDATE,
        after={
            "branch_id": instance.branch_id,
            "mrp": str(instance.mrp),
            "sale_price": str(instance.sale_price),
            "cost_price": str(instance.cost_price) if instance.cost_price else None,
            "valid_from": instance.valid_from.isoformat(),
            "valid_to": instance.valid_to.isoformat() if instance.valid_to else None,
            "product_id": instance.product_id,
            "variant_id": instance.variant_id,
        },
    )


@receiver(post_save, sender=Product)
def _audit_product_change(sender, instance, created, **kwargs):
    audit(
        model="catalog.Product",
        object_id=instance.pk,
        action=AuditAction.CREATE if created else AuditAction.UPDATE,
        after={"sku": instance.sku, "status": instance.status, "name": instance.name},
    )


@receiver(post_save, sender=ProductVariant)
def _audit_variant_change(sender, instance, created, **kwargs):
    audit(
        model="catalog.ProductVariant",
        object_id=instance.pk,
        action=AuditAction.CREATE if created else AuditAction.UPDATE,
        after={"sku": instance.sku, "product_id": instance.product_id},
    )
