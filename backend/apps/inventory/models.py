"""M05 Inventory — core models (step 2).

Schema overview
---------------
``InventoryLedger``  — immutable append-only subclass of
    :class:`apps.core.ledger.models.LedgerEntry`. The **only writer** of
    stock movements. ``LedgerEntry`` already provides the numeric
    ``amount`` / ``balance_before`` / ``balance_after`` columns and the
    ``reference_type`` / ``reference_id`` envelope; we reuse those for
    ``qty_change`` / ``qty_before`` / ``qty_after`` / ``ref_type`` /
    ``ref_id`` so reporting can union with VendorLedger and friends.

``Stock``            — derived per-(item, branch, [warehouse]) snapshot
    recomputed by ``ledger_service.post``. Carries ``qty_on_hand``,
    ``qty_reserved`` and ``qty_in_transit`` for availability queries.

``Batch``            — per-(item, branch) lot with mfg/expiry, cost and
    remaining qty. Drained FIFO by services in later steps.

``Reservation``      — soft-block on stock used by M06/M11 before
    payment is captured. Counts toward ``Stock.qty_reserved`` until it
    is consumed, released or expires.

Transfers (``BranchTransfer*``), Adjustments (``StockAdjustment*``),
Counts (``PhysicalCount*``) and Wastage land in steps 5-6.
"""

from __future__ import annotations

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from apps.catalog.models import Product, ProductVariant
from apps.core.ledger.models import LedgerEntry
from apps.core.models import BaseModel
from apps.master.models import Branch, Warehouse

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class InventoryRefType(models.TextChoices):
    """Origin document for an ``InventoryLedger`` row.

    Mirrors the ``ref_type`` values listed in the M05 plan. Strings stay
    short so ``LedgerEntry.reference_type`` (CharField max_length=64)
    has plenty of headroom.
    """

    GRN = "GRN", "Goods Receipt Note"
    SALE = "SALE", "Sale"
    TRANSFER = "TRANSFER", "Branch transfer"
    ADJUSTMENT = "ADJUSTMENT", "Stock adjustment"
    RETURN = "RETURN", "Return (purchase or sales)"
    WASTAGE = "WASTAGE", "Wastage / damage / expiry"
    OPENING = "OPENING", "Opening stock import"
    COUNT = "COUNT", "Physical count finalisation"


class BatchStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    EXPIRED = "EXPIRED", "Expired"
    CONSUMED = "CONSUMED", "Consumed"


class ReservationRefType(models.TextChoices):
    ORDER = "ORDER", "Sales order"
    HOLD = "HOLD", "Manual hold"


class ReservationStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    CONSUMED = "CONSUMED", "Consumed"
    RELEASED = "RELEASED", "Released"
    EXPIRED = "EXPIRED", "Expired"


# Decimal precision: 14 / 3 matches POItem.qty (and is consistent across
# the platform for quantities). Costs use 14 / 4 like POItem.rate.
QTY_KW = {"max_digits": 14, "decimal_places": 3}
COST_KW = {"max_digits": 14, "decimal_places": 4}


# ---------------------------------------------------------------------------
# Stock — derived per-(item, branch[, warehouse]) snapshot
# ---------------------------------------------------------------------------


class Stock(BaseModel):
    """On-hand snapshot for a (product/variant, branch[, warehouse]).

    Exactly one of ``product`` / ``variant`` must be set — same XOR
    pattern used by :class:`apps.catalog.models.ProductPrice`. All
    numeric fields are recomputed by ``ledger_service.post``; do **not**
    write them directly from views or admin.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="stock_rows",
        null=True,
        blank=True,
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="stock_rows",
        null=True,
        blank=True,
    )
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="stock_rows")
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="stock_rows",
        null=True,
        blank=True,
    )

    qty_on_hand = models.DecimalField(
        default=Decimal("0"), validators=(MinValueValidator(Decimal("0")),), **QTY_KW
    )
    qty_reserved = models.DecimalField(
        default=Decimal("0"), validators=(MinValueValidator(Decimal("0")),), **QTY_KW
    )
    qty_in_transit = models.DecimalField(
        default=Decimal("0"), validators=(MinValueValidator(Decimal("0")),), **QTY_KW
    )
    last_movement_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        verbose_name = "stock row"
        verbose_name_plural = "stock rows"
        ordering = ("branch_id", "product_id", "variant_id")
        constraints = (
            models.CheckConstraint(
                name="inventory_stock_xor_target",
                check=(
                    models.Q(product__isnull=False, variant__isnull=True)
                    | models.Q(product__isnull=True, variant__isnull=False)
                ),
            ),
            models.UniqueConstraint(
                fields=("product", "branch", "warehouse"),
                condition=models.Q(product__isnull=False),
                name="inventory_stock_unique_product",
            ),
            models.UniqueConstraint(
                fields=("variant", "branch", "warehouse"),
                condition=models.Q(variant__isnull=False),
                name="inventory_stock_unique_variant",
            ),
        )
        indexes = (
            models.Index(fields=("branch", "product")),
            models.Index(fields=("branch", "variant")),
            models.Index(fields=("last_movement_at",)),
        )

    def __str__(self) -> str:  # pragma: no cover
        target = self.variant_id or self.product_id
        return f"Stock<branch={self.branch_id} item={target} on_hand={self.qty_on_hand}>"


# ---------------------------------------------------------------------------
# Batch — lot tracking for products with mfg/expiry
# ---------------------------------------------------------------------------


class Batch(BaseModel):
    """A receipted lot of a product/variant at a branch."""

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="batches",
        null=True,
        blank=True,
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name="batches",
        null=True,
        blank=True,
    )
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="batches")

    batch_no = models.CharField(max_length=64)
    mfg_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True, db_index=True)
    cost_price = models.DecimalField(
        default=Decimal("0"), validators=(MinValueValidator(Decimal("0")),), **COST_KW
    )
    qty_received = models.DecimalField(
        default=Decimal("0"), validators=(MinValueValidator(Decimal("0")),), **QTY_KW
    )
    qty_remaining = models.DecimalField(
        default=Decimal("0"), validators=(MinValueValidator(Decimal("0")),), **QTY_KW
    )
    status = models.CharField(
        max_length=16, choices=BatchStatus.choices, default=BatchStatus.ACTIVE, db_index=True
    )

    class Meta:
        ordering = ("expiry_date", "id")
        constraints = (
            models.CheckConstraint(
                name="inventory_batch_xor_target",
                check=(
                    models.Q(product__isnull=False, variant__isnull=True)
                    | models.Q(product__isnull=True, variant__isnull=False)
                ),
            ),
            models.UniqueConstraint(
                fields=("product", "branch", "batch_no"),
                condition=models.Q(product__isnull=False),
                name="inventory_batch_unique_product",
            ),
            models.UniqueConstraint(
                fields=("variant", "branch", "batch_no"),
                condition=models.Q(variant__isnull=False),
                name="inventory_batch_unique_variant",
            ),
        )
        indexes = (
            models.Index(fields=("branch", "product", "status")),
            models.Index(fields=("branch", "variant", "status")),
            models.Index(fields=("status", "expiry_date")),
        )

    def __str__(self) -> str:  # pragma: no cover
        return f"Batch<{self.batch_no} branch={self.branch_id}>"


# ---------------------------------------------------------------------------
# Reservation — soft-block before payment
# ---------------------------------------------------------------------------


class Reservation(BaseModel):
    """Soft-block on stock held against a sales order or manual hold.

    Counts toward :attr:`Stock.qty_reserved` while ``status=ACTIVE``.
    M06/M11 consume these to confirm or release stock; expired rows
    are swept by a periodic task (step 4).
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="reservations",
        null=True,
        blank=True,
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name="reservations",
        null=True,
        blank=True,
    )
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="reservations")

    qty = models.DecimalField(validators=(MinValueValidator(Decimal("0.001")),), **QTY_KW)
    ref_type = models.CharField(max_length=16, choices=ReservationRefType.choices)
    ref_id = models.CharField(max_length=64)
    expires_at = models.DateTimeField(null=True, blank=True, db_index=True)
    status = models.CharField(
        max_length=16,
        choices=ReservationStatus.choices,
        default=ReservationStatus.ACTIVE,
        db_index=True,
    )

    class Meta:
        ordering = ("-id",)
        constraints = (
            models.CheckConstraint(
                name="inventory_reservation_xor_target",
                check=(
                    models.Q(product__isnull=False, variant__isnull=True)
                    | models.Q(product__isnull=True, variant__isnull=False)
                ),
            ),
        )
        indexes = (
            models.Index(fields=("ref_type", "ref_id")),
            models.Index(fields=("branch", "status")),
            models.Index(fields=("status", "expires_at")),
        )

    def __str__(self) -> str:  # pragma: no cover
        return f"Reservation<{self.ref_type}:{self.ref_id} qty={self.qty}>"


# ---------------------------------------------------------------------------
# InventoryLedger — single writer of stock movements
# ---------------------------------------------------------------------------


class InventoryLedger(LedgerEntry):
    """Immutable append-only stock movement.

    Field mapping vs. the inherited :class:`LedgerEntry`:

    =================  ========================
    Plan field         Inherited / new
    =================  ========================
    ``qty_change``     ``amount``       (signed)
    ``qty_before``     ``balance_before``
    ``qty_after``      ``balance_after``
    ``ref_type``       ``reference_type``
    ``ref_id``         ``reference_id``
    ``actor``          ``actor``
    ``ts``             ``timestamp``
    =================  ========================

    New domain columns: ``product``, ``variant``, ``batch`` (nullable),
    ``branch``, ``warehouse`` (nullable), ``reason_code`` (nullable).

    Listed in :data:`apps.core.checks.BASE_MODEL_EXEMPTIONS` because
    ``LedgerEntry`` is the deliberate non-``BaseModel`` ancestor for
    immutable financial / quantity postings.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="inventory_ledger_entries",
        null=True,
        blank=True,
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name="inventory_ledger_entries",
        null=True,
        blank=True,
    )
    batch = models.ForeignKey(
        Batch,
        on_delete=models.PROTECT,
        related_name="ledger_entries",
        null=True,
        blank=True,
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.PROTECT,
        related_name="inventory_ledger_entries",
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="inventory_ledger_entries",
        null=True,
        blank=True,
    )
    reason_code = models.CharField(max_length=32, blank=True, default="", db_index=True)

    class Meta(LedgerEntry.Meta):
        abstract = False
        constraints = (
            models.CheckConstraint(
                name="inventory_ledger_xor_target",
                check=(
                    models.Q(product__isnull=False, variant__isnull=True)
                    | models.Q(product__isnull=True, variant__isnull=False)
                ),
            ),
        )
        indexes = list(LedgerEntry.Meta.indexes) + [
            models.Index(fields=("branch", "product", "timestamp")),
            models.Index(fields=("branch", "variant", "timestamp")),
        ]


class BranchTransferStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    DISPATCHED = "DISPATCHED", "Dispatched"
    IN_TRANSIT = "IN_TRANSIT", "In Transit"
    RECEIVED = "RECEIVED", "Received"
    CANCELLED = "CANCELLED", "Cancelled"


class BranchTransfer(BaseModel):
    tr_no = models.CharField(max_length=32, unique=True)
    from_branch = models.ForeignKey(
        Branch, on_delete=models.PROTECT, related_name="outgoing_transfers"
    )
    to_branch = models.ForeignKey(
        Branch, on_delete=models.PROTECT, related_name="incoming_transfers"
    )
    status = models.CharField(
        max_length=16,
        choices=BranchTransferStatus.choices,
        default=BranchTransferStatus.DRAFT,
        db_index=True,
    )
    dispatched_at = models.DateTimeField(null=True, blank=True)
    received_at = models.DateTimeField(null=True, blank=True)
    vehicle = models.CharField(max_length=64, blank=True, default="")

    class Meta:
        ordering = ("-id",)

    def __str__(self):
        return (
            f"BranchTransfer<{self.tr_no} {self.from_branch_id}->{self.to_branch_id} {self.status}>"
        )


class BranchTransferItem(BaseModel):
    transfer = models.ForeignKey(BranchTransfer, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True, blank=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, null=True, blank=True)
    batch = models.ForeignKey("Batch", on_delete=models.PROTECT, null=True, blank=True)
    qty_sent = models.DecimalField(max_digits=14, decimal_places=3)
    qty_received = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    qty_lost = models.DecimalField(max_digits=14, decimal_places=3, default=0)

    def __str__(self):
        return f"TransferItem<{self.product_id or self.variant_id} sent={self.qty_sent} received={self.qty_received}>"


# ---------------------------------------------------------------------------
# Document status (shared by Adjustment / Wastage / Count)
# ---------------------------------------------------------------------------


class DocumentStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    POSTED = "POSTED", "Posted"
    CANCELLED = "CANCELLED", "Cancelled"


# ---------------------------------------------------------------------------
# Stock Adjustment — manual signed correction
# ---------------------------------------------------------------------------


class StockAdjustment(BaseModel):
    adj_no = models.CharField(max_length=32, unique=True)
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="stock_adjustments")
    reason_code = models.CharField(max_length=32)
    status = models.CharField(
        max_length=16,
        choices=DocumentStatus.choices,
        default=DocumentStatus.DRAFT,
        db_index=True,
    )
    posted_at = models.DateTimeField(null=True, blank=True)
    remarks = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        ordering = ("-id",)

    def __str__(self):
        return f"StockAdjustment<{self.adj_no} {self.status}>"


class StockAdjustmentItem(BaseModel):
    adjustment = models.ForeignKey(StockAdjustment, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True, blank=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, null=True, blank=True)
    batch = models.ForeignKey("Batch", on_delete=models.PROTECT, null=True, blank=True)
    qty_change = models.DecimalField(max_digits=14, decimal_places=3)  # signed

    class Meta:
        constraints = (
            models.CheckConstraint(
                name="inventory_stockadjitem_xor_target",
                check=(
                    models.Q(product__isnull=False, variant__isnull=True)
                    | models.Q(product__isnull=True, variant__isnull=False)
                ),
            ),
        )


# ---------------------------------------------------------------------------
# Wastage — always-negative
# ---------------------------------------------------------------------------


class Wastage(BaseModel):
    wastage_no = models.CharField(max_length=32, unique=True)
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="wastages")
    reason_code = models.CharField(max_length=32)
    status = models.CharField(
        max_length=16,
        choices=DocumentStatus.choices,
        default=DocumentStatus.DRAFT,
        db_index=True,
    )
    posted_at = models.DateTimeField(null=True, blank=True)
    remarks = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        ordering = ("-id",)

    def __str__(self):
        return f"Wastage<{self.wastage_no} {self.status}>"


class WastageItem(BaseModel):
    wastage = models.ForeignKey(Wastage, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True, blank=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, null=True, blank=True)
    batch = models.ForeignKey("Batch", on_delete=models.PROTECT, null=True, blank=True)
    qty = models.DecimalField(
        max_digits=14,
        decimal_places=3,
        validators=(MinValueValidator(Decimal("0.001")),),
    )

    class Meta:
        constraints = (
            models.CheckConstraint(
                name="inventory_wastageitem_xor_target",
                check=(
                    models.Q(product__isnull=False, variant__isnull=True)
                    | models.Q(product__isnull=True, variant__isnull=False)
                ),
            ),
        )


# ---------------------------------------------------------------------------
# Physical Count — cycle counting
# ---------------------------------------------------------------------------


class PhysicalCountStatus(models.TextChoices):
    OPEN = "OPEN", "Open"
    COUNTED = "COUNTED", "Counted"
    POSTED = "POSTED", "Posted"
    CANCELLED = "CANCELLED", "Cancelled"


class PhysicalCount(BaseModel):
    count_no = models.CharField(max_length=32, unique=True)
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="physical_counts")
    status = models.CharField(
        max_length=16,
        choices=PhysicalCountStatus.choices,
        default=PhysicalCountStatus.OPEN,
        db_index=True,
    )
    posted_at = models.DateTimeField(null=True, blank=True)
    remarks = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        ordering = ("-id",)

    def __str__(self):
        return f"PhysicalCount<{self.count_no} {self.status}>"


class PhysicalCountItem(BaseModel):
    count = models.ForeignKey(PhysicalCount, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True, blank=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, null=True, blank=True)
    qty_expected = models.DecimalField(max_digits=14, decimal_places=3, default=Decimal("0"))
    qty_counted = models.DecimalField(max_digits=14, decimal_places=3, default=Decimal("0"))

    class Meta:
        constraints = (
            models.CheckConstraint(
                name="inventory_countitem_xor_target",
                check=(
                    models.Q(product__isnull=False, variant__isnull=True)
                    | models.Q(product__isnull=True, variant__isnull=False)
                ),
            ),
        )


__all__ = [
    "Batch",
    "BatchStatus",
    "InventoryLedger",
    "InventoryRefType",
    "Reservation",
    "ReservationRefType",
    "ReservationStatus",
    "Stock",
    "BranchTransfer",
    "BranchTransferItem",
    "BranchTransferStatus",
    "DocumentStatus",
    "StockAdjustment",
    "StockAdjustmentItem",
    "Wastage",
    "WastageItem",
    "PhysicalCount",
    "PhysicalCountItem",
    "PhysicalCountStatus",
]
