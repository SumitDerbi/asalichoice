"""
Abstract ``LedgerEntry`` model.

Concrete subclasses (``InventoryLedger``, ``WalletLedger`` …) are
defined in their owning module and add domain-specific FKs (item,
wallet, vendor, …). All of them inherit the same shape so reporting
can union across them.

Immutability is enforced at the application layer: ``save()`` refuses
to update an existing row, and ``delete()`` is blocked outright. The
``LEDGER_IMMUTABLE`` settings flag lets test suites flip this off
temporarily if absolutely necessary.
"""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models


class LedgerEntry(models.Model):
    """Append-only ledger row.

    Subclass and add domain FKs (``item``, ``vendor`` …). The numeric
    columns use ``DecimalField`` to avoid float drift; precision is
    18 / scale 4 which comfortably covers retail money and quantities
    (1e14 with four decimals).
    """

    reference_type = models.CharField(max_length=64, db_index=True)
    reference_id = models.CharField(max_length=64, db_index=True)
    amount = models.DecimalField(max_digits=18, decimal_places=4)
    balance_before = models.DecimalField(max_digits=18, decimal_places=4)
    balance_after = models.DecimalField(max_digits=18, decimal_places=4)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    branch_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    remarks = models.CharField(max_length=255, blank=True)

    class Meta:
        abstract = True
        ordering = ("-timestamp",)
        indexes = [
            models.Index(fields=["reference_type", "reference_id"]),
            models.Index(fields=["branch_id", "timestamp"]),
        ]

    # -- Immutability ----------------------------------------------------
    def save(self, *args, **kwargs):
        if self.pk is not None and getattr(settings, "LEDGER_IMMUTABLE", True):
            raise RuntimeError(
                f"{type(self).__name__} rows are immutable; create a new entry instead.",
            )
        # Compute balance_after if the caller only supplied balance_before
        # and amount. This is a convenience for ledger writers — they can
        # still override it explicitly.
        if self.balance_after is None and self.balance_before is not None:
            self.balance_after = Decimal(self.balance_before) + Decimal(self.amount or 0)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if getattr(settings, "LEDGER_IMMUTABLE", True):
            raise RuntimeError(
                f"{type(self).__name__} rows are immutable; deletion is restricted.",
            )
        return super().delete(*args, **kwargs)
