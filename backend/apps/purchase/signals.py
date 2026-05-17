"""Purchase signals — audit logging for the transactional documents."""

from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.core.audit.models import AuditAction
from apps.core.audit.service import audit

from .models import GRN, PurchaseInvoice, PurchaseOrder, PurchaseReturn, Vendor


def _audit(instance, created: bool, fields: dict) -> None:
    audit(
        instance=instance,
        action=AuditAction.CREATE if created else AuditAction.UPDATE,
        after=fields,
    )


@receiver(post_save, sender=Vendor, dispatch_uid="purchase.audit.vendor")
def _audit_vendor(sender, instance, created, **_kwargs):
    _audit(
        instance,
        created,
        {"code": instance.code, "name": instance.name, "is_active": instance.is_active},
    )


@receiver(post_save, sender=PurchaseOrder, dispatch_uid="purchase.audit.po")
def _audit_po(sender, instance, created, **_kwargs):
    _audit(
        instance,
        created,
        {
            "po_no": instance.po_no,
            "status": instance.status,
            "vendor_id": instance.vendor_id,
            "branch_id": instance.branch_id,
        },
    )


@receiver(post_save, sender=GRN, dispatch_uid="purchase.audit.grn")
def _audit_grn(sender, instance, created, **_kwargs):
    _audit(
        instance,
        created,
        {
            "grn_no": instance.grn_no,
            "status": instance.status,
            "vendor_id": instance.vendor_id,
            "branch_id": instance.branch_id,
            "po_id": instance.po_id,
        },
    )


@receiver(post_save, sender=PurchaseInvoice, dispatch_uid="purchase.audit.pi")
def _audit_pi(sender, instance, created, **_kwargs):
    _audit(
        instance,
        created,
        {"pi_no": instance.pi_no, "status": instance.status, "vendor_id": instance.vendor_id},
    )


@receiver(post_save, sender=PurchaseReturn, dispatch_uid="purchase.audit.pr")
def _audit_pr(sender, instance, created, **_kwargs):
    _audit(
        instance,
        created,
        {"pr_no": instance.pr_no, "status": instance.status, "grn_id": instance.grn_id},
    )
