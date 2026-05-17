"""M04 Purchase — domain models.

Hierarchy:
    Vendor → VendorContact[], VendorBankAccount[]
    PurchaseOrder (PO) → POItem[]   (transitions: DRAFT → PENDING_APPROVAL → APPROVED → PARTIAL/RECEIVED → CLOSED, or CANCELLED)
    GRN → GRNItem[]                 (transitions: DRAFT → SUBMITTED → APPROVED/REJECTED)
    PurchaseInvoice (PI)            (transitions: DRAFT → POSTED → PART_PAID → PAID, or CANCELLED)
    PurchaseReturn (PR)             (transitions: DRAFT → POSTED)
    VendorLedger                    (immutable append-only — subclass of ``LedgerEntry``)

Stock policy: PO never writes stock. **GRN approval is the only doc that
writes inventory** (see ADR-007). PR posting reverses the receipt.
"""

from __future__ import annotations

import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from apps.catalog.models import Product, ProductVariant
from apps.core.ledger.models import LedgerEntry
from apps.core.models import BaseModel
from apps.master.models import Branch, Tax, UnitOfMeasure

# ---------------------------------------------------------------------------
# Vendor master
# ---------------------------------------------------------------------------


class Vendor(BaseModel):
    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=240)
    contact_name = models.CharField(max_length=160, blank=True, default="")
    contact_email = models.EmailField(blank=True, default="")
    contact_mobile = models.CharField(max_length=20, blank=True, default="")
    gstin = models.CharField(max_length=20, blank=True, default="")
    pan = models.CharField(max_length=20, blank=True, default="")
    addresses_json = models.JSONField(default=list, blank=True)
    payment_terms_json = models.JSONField(default=dict, blank=True)
    credit_limit = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0"),
        validators=(MinValueValidator(Decimal("0")),),
    )
    branches = models.ManyToManyField(Branch, related_name="vendors", blank=True)

    class Meta:
        ordering = ("code",)
        indexes = (
            models.Index(fields=("name",)),
            models.Index(fields=("gstin",)),
        )

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.code} — {self.name}"


class VendorContact(BaseModel):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="contacts")
    name = models.CharField(max_length=160)
    role = models.CharField(max_length=80, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    mobile = models.CharField(max_length=20, blank=True, default="")

    class Meta:
        ordering = ("vendor_id", "name")


class VendorBankAccount(BaseModel):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="bank_accounts")
    account_no_masked = models.CharField(max_length=40)
    ifsc = models.CharField(max_length=20, blank=True, default="")
    bank_name = models.CharField(max_length=120, blank=True, default="")
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ("vendor_id", "-is_default", "id")


# ---------------------------------------------------------------------------
# Purchase Order
# ---------------------------------------------------------------------------


class POStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    PENDING_APPROVAL = "PENDING_APPROVAL", "Pending Approval"
    APPROVED = "APPROVED", "Approved"
    PARTIAL = "PARTIAL", "Partially Received"
    RECEIVED = "RECEIVED", "Received"
    CLOSED = "CLOSED", "Closed"
    CANCELLED = "CANCELLED", "Cancelled"


class PurchaseOrder(BaseModel):
    po_no = models.CharField(max_length=64, unique=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name="purchase_orders")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="purchase_orders")
    status = models.CharField(max_length=20, choices=POStatus.choices, default=POStatus.DRAFT)
    expected_delivery = models.DateField(null=True, blank=True)
    terms = models.TextField(blank=True, default="")
    totals_json = models.JSONField(default=dict, blank=True)
    approval_chain_json = models.JSONField(default=list, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-id",)
        indexes = (
            models.Index(fields=("status",)),
            models.Index(fields=("vendor", "branch")),
        )

    def __str__(self) -> str:  # pragma: no cover
        return self.po_no


class POItem(BaseModel):
    po = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="+", null=True, blank=True
    )
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.PROTECT, related_name="+", null=True, blank=True
    )
    qty = models.DecimalField(
        max_digits=14, decimal_places=3, validators=(MinValueValidator(Decimal("0")),)
    )
    uom = models.ForeignKey(UnitOfMeasure, on_delete=models.PROTECT, related_name="+")
    rate = models.DecimalField(
        max_digits=14, decimal_places=4, validators=(MinValueValidator(Decimal("0")),)
    )
    tax = models.ForeignKey(Tax, on_delete=models.PROTECT, related_name="+", null=True, blank=True)
    discount = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=Decimal("0"),
        validators=(MinValueValidator(Decimal("0")),),
    )
    line_total = models.DecimalField(max_digits=16, decimal_places=4, default=Decimal("0"))

    class Meta:
        ordering = ("po_id", "id")
        constraints = (
            models.CheckConstraint(
                name="purchase_poitem_xor_target",
                check=(
                    models.Q(product__isnull=False, variant__isnull=True)
                    | models.Q(product__isnull=True, variant__isnull=False)
                ),
            ),
            models.CheckConstraint(
                name="purchase_poitem_qty_nonneg",
                check=models.Q(qty__gte=Decimal("0")),
            ),
        )


# ---------------------------------------------------------------------------
# GRN
# ---------------------------------------------------------------------------


class GRNStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    SUBMITTED = "SUBMITTED", "Submitted"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"


class GRN(BaseModel):
    grn_no = models.CharField(max_length=64, unique=True)
    po = models.ForeignKey(
        PurchaseOrder, on_delete=models.PROTECT, related_name="grns", null=True, blank=True
    )
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name="grns")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="grns")
    status = models.CharField(max_length=16, choices=GRNStatus.choices, default=GRNStatus.DRAFT)
    received_at = models.DateTimeField(null=True, blank=True)
    vehicle_no = models.CharField(max_length=40, blank=True, default="")
    transporter = models.CharField(max_length=160, blank=True, default="")
    offline_uuid = models.UUIDField(null=True, blank=True, unique=True)
    totals_json = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("-id",)
        indexes = (
            models.Index(fields=("status",)),
            models.Index(fields=("vendor", "branch")),
        )

    def __str__(self) -> str:  # pragma: no cover
        return self.grn_no


class GRNItem(BaseModel):
    grn = models.ForeignKey(GRN, on_delete=models.CASCADE, related_name="items")
    po_item = models.ForeignKey(
        POItem, on_delete=models.PROTECT, related_name="grn_items", null=True, blank=True
    )
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="+", null=True, blank=True
    )
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.PROTECT, related_name="+", null=True, blank=True
    )
    qty_received = models.DecimalField(
        max_digits=14, decimal_places=3, validators=(MinValueValidator(Decimal("0")),)
    )
    qty_accepted = models.DecimalField(
        max_digits=14,
        decimal_places=3,
        default=Decimal("0"),
        validators=(MinValueValidator(Decimal("0")),),
    )
    qty_rejected = models.DecimalField(
        max_digits=14,
        decimal_places=3,
        default=Decimal("0"),
        validators=(MinValueValidator(Decimal("0")),),
    )
    rejection_reason = models.CharField(max_length=255, blank=True, default="")
    batch_no = models.CharField(max_length=64, blank=True, default="")
    mfg_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    cost_price = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=Decimal("0"),
        validators=(MinValueValidator(Decimal("0")),),
    )

    class Meta:
        ordering = ("grn_id", "id")
        constraints = (
            models.CheckConstraint(
                name="purchase_grnitem_xor_target",
                check=(
                    models.Q(product__isnull=False, variant__isnull=True)
                    | models.Q(product__isnull=True, variant__isnull=False)
                ),
            ),
            models.CheckConstraint(
                name="purchase_grnitem_qty_nonneg",
                check=(
                    models.Q(qty_received__gte=Decimal("0"))
                    & models.Q(qty_accepted__gte=Decimal("0"))
                    & models.Q(qty_rejected__gte=Decimal("0"))
                ),
            ),
        )


# ---------------------------------------------------------------------------
# Purchase Invoice
# ---------------------------------------------------------------------------


class PIStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    POSTED = "POSTED", "Posted"
    PART_PAID = "PART_PAID", "Partially Paid"
    PAID = "PAID", "Paid"
    CANCELLED = "CANCELLED", "Cancelled"


class PurchaseInvoice(BaseModel):
    pi_no = models.CharField(max_length=64, unique=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name="invoices")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="purchase_invoices")
    grns = models.ManyToManyField(GRN, related_name="invoices", blank=True)
    invoice_no_vendor = models.CharField(max_length=64, blank=True, default="")
    invoice_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    totals_json = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=16, choices=PIStatus.choices, default=PIStatus.DRAFT)
    payment_terms = models.CharField(max_length=120, blank=True, default="")

    class Meta:
        ordering = ("-id",)
        indexes = (models.Index(fields=("status",)),)

    def __str__(self) -> str:  # pragma: no cover
        return self.pi_no


# ---------------------------------------------------------------------------
# Purchase Return
# ---------------------------------------------------------------------------


class PRStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    POSTED = "POSTED", "Posted"
    CANCELLED = "CANCELLED", "Cancelled"


class PurchaseReturn(BaseModel):
    pr_no = models.CharField(max_length=64, unique=True)
    grn = models.ForeignKey(GRN, on_delete=models.PROTECT, related_name="returns")
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name="returns")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="purchase_returns")
    reason = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(max_length=16, choices=PRStatus.choices, default=PRStatus.DRAFT)
    items_json = models.JSONField(default=list, blank=True)
    totals_json = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("-id",)


# ---------------------------------------------------------------------------
# Vendor ledger (immutable, branch-scoped)
# ---------------------------------------------------------------------------


class VendorLedger(LedgerEntry):
    """Append-only vendor running balance.

    ``amount`` is signed: positive = credit (we owe vendor more, e.g. PI
    posted / GRN received), negative = debit (payment / return). The
    ``balance_after`` field carries the running outstanding.
    """

    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name="ledger_entries")
    branch = models.ForeignKey(
        Branch,
        on_delete=models.PROTECT,
        related_name="vendor_ledger_entries",
        null=True,
        blank=True,
    )

    class Meta(LedgerEntry.Meta):
        abstract = False
        indexes = list(LedgerEntry.Meta.indexes) + [
            models.Index(fields=("vendor", "branch", "timestamp")),
        ]


def new_offline_uuid() -> uuid.UUID:  # pragma: no cover - convenience helper
    return uuid.uuid4()


__all__ = [
    "GRN",
    "GRNItem",
    "GRNStatus",
    "PIStatus",
    "POItem",
    "POStatus",
    "PRStatus",
    "PurchaseInvoice",
    "PurchaseOrder",
    "PurchaseReturn",
    "Vendor",
    "VendorBankAccount",
    "VendorContact",
    "VendorLedger",
    "new_offline_uuid",
]
