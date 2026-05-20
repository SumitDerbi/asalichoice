"""M11 Sales — core models.

Schema overview
---------------
``Sale``          — the order/bill aggregate. Headers carry origin
    (POS / ONLINE / B2B / MANUAL), branch, customer (optional), cashier,
    monetary totals (``totals_json``) and lifecycle ``status``. Offline
    POS replays are deduped via ``offline_uuid``.

``SaleItem``      — one line per product/variant on a sale. XOR between
    ``product`` and ``variant`` mirrors :class:`apps.catalog.ProductPrice`
    and :class:`apps.inventory.Stock`. Numeric columns use the platform
    14/3 (qty) and 14/4 (money) precision.

``SalePayment``   — one row per tender. ``status`` lets us record async
    online gateway flows (``PENDING`` → ``SUCCESS`` / ``FAILED``).

``Discount``      — reusable discount code definition (header or line
    scoped). ``condition_json`` is interpreted by ``discount_engine``.

``PriceOverride`` — audit trail for any line whose ``sale_price`` differs
    from the catalog price (one per SaleItem). Permission gating happens
    in the service layer; we store the decision so reports can reconcile.

Single-writer invariant
-----------------------
Stock totals are still recomputed exclusively by
``apps.inventory.services.ledger_service.post``. ``sale_service.post``
calls into it; nothing in this app touches ``Stock.qty_*`` directly.
"""

from __future__ import annotations

import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from apps.catalog.models import Product, ProductVariant
from apps.core.models import BaseModel
from apps.inventory.models import Batch
from apps.master.models import Branch, HSNCode, PaymentMode, Tax, UnitOfMeasure

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class SaleOrigin(models.TextChoices):
    POS = "POS", "Point of sale"
    ONLINE = "ONLINE", "Storefront / online"
    B2B = "B2B", "B2B / wholesale counter"
    MANUAL = "MANUAL", "Manual admin entry"


class SaleStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    HELD = "HELD", "Held / parked"
    CONFIRMED = "CONFIRMED", "Confirmed"
    PARTIALLY_PAID = "PARTIALLY_PAID", "Partially paid"
    PAID = "PAID", "Paid"
    CANCELLED = "CANCELLED", "Cancelled"
    REFUNDED = "REFUNDED", "Refunded"


class TaxMode(models.TextChoices):
    INCLUSIVE = "INCLUSIVE", "Tax inclusive"
    EXCLUSIVE = "EXCLUSIVE", "Tax exclusive"


class SalePaymentStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    SUCCESS = "SUCCESS", "Success"
    FAILED = "FAILED", "Failed"
    REFUNDED = "REFUNDED", "Refunded"


class DiscountScope(models.TextChoices):
    HEADER = "HEADER", "Header (cart-level)"
    LINE = "LINE", "Line (per item)"


class DiscountKind(models.TextChoices):
    PERCENT = "PERCENT", "Percent"
    FLAT = "FLAT", "Flat amount"


# Decimal precision — quantities (14/3) and money (14/4) match the
# inventory / purchase modules so cross-module arithmetic doesn't drift.
QTY_KW = {"max_digits": 14, "decimal_places": 3}
MONEY_KW = {"max_digits": 14, "decimal_places": 4}


# ---------------------------------------------------------------------------
# Sale aggregate root
# ---------------------------------------------------------------------------


class Sale(BaseModel):
    """The single sale aggregate (one row per bill).

    Lifecycle (see ADR-014):

    DRAFT ─▶ HELD ─▶ CONFIRMED ─▶ PARTIALLY_PAID ─▶ PAID
              │           │                            │
              ▼           ▼                            ▼
           CANCELLED  CANCELLED                    REFUNDED

    ``totals_json`` is populated by ``sale_service`` on every recompute
    and mirrored back into the structured columns (``subtotal``,
    ``discount_total``, ``tax_total``, ``grand_total``) so SQL queries
    can filter without JSON traversal.
    """

    sale_no = models.CharField(max_length=32, unique=True)
    origin = models.CharField(max_length=8, choices=SaleOrigin.choices)
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="sales")
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sales_as_customer",
    )
    cashier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sales_as_cashier",
    )
    # Terminal is forward-looking — M07 (POS) will introduce the actual
    # ``Terminal`` model. Until then we keep the slot as a free int
    # reference so offline POS replays can still tag their terminal.
    terminal_id_external = models.PositiveIntegerField(null=True, blank=True)

    status = models.CharField(
        max_length=16,
        choices=SaleStatus.choices,
        default=SaleStatus.DRAFT,
        db_index=True,
    )
    tax_mode = models.CharField(
        max_length=10,
        choices=TaxMode.choices,
        default=TaxMode.EXCLUSIVE,
    )

    billed_at = models.DateTimeField(null=True, blank=True, db_index=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    # Structured totals — derived columns kept in sync by
    # ``sale_service.recompute``. ``totals_json`` carries the full
    # breakup (per-component tax, rounding, etc.).
    subtotal = models.DecimalField(default=Decimal("0"), **MONEY_KW)
    discount_total = models.DecimalField(default=Decimal("0"), **MONEY_KW)
    tax_total = models.DecimalField(default=Decimal("0"), **MONEY_KW)
    grand_total = models.DecimalField(default=Decimal("0"), **MONEY_KW)
    payment_total = models.DecimalField(default=Decimal("0"), **MONEY_KW)

    totals_json = models.JSONField(default=dict, blank=True)
    payment_terms_json = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)

    # Idempotent offline replay key (POS clients send this when they
    # finally come back online). Unique nullable: a single ``NULL`` is
    # allowed many times in MariaDB, so server-side sales can omit it.
    offline_uuid = models.UUIDField(null=True, blank=True, unique=True)

    class Meta:
        verbose_name = "sale"
        verbose_name_plural = "sales"
        ordering = ("-billed_at", "-id")
        indexes = (
            models.Index(fields=("branch", "status")),
            models.Index(fields=("branch", "billed_at")),
            models.Index(fields=("origin", "status")),
        )

    def __str__(self) -> str:  # pragma: no cover
        return f"Sale<{self.sale_no} {self.status}>"

    # ------------------------------------------------------------------
    @staticmethod
    def make_offline_uuid() -> uuid.UUID:
        """Helper for tests/admin to mint a fresh offline uuid."""

        return uuid.uuid4()


# ---------------------------------------------------------------------------
# Sale line items
# ---------------------------------------------------------------------------


class SaleItem(BaseModel):
    """One line on a :class:`Sale`."""

    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="sale_items",
        null=True,
        blank=True,
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name="sale_items",
        null=True,
        blank=True,
    )
    uom = models.ForeignKey(UnitOfMeasure, on_delete=models.PROTECT, related_name="sale_items")
    batch = models.ForeignKey(
        Batch,
        on_delete=models.PROTECT,
        related_name="sale_items",
        null=True,
        blank=True,
    )
    hsn = models.ForeignKey(
        HSNCode,
        on_delete=models.PROTECT,
        related_name="sale_items",
        null=True,
        blank=True,
    )
    tax = models.ForeignKey(
        Tax,
        on_delete=models.PROTECT,
        related_name="sale_items",
        null=True,
        blank=True,
    )

    qty = models.DecimalField(validators=(MinValueValidator(Decimal("0")),), **QTY_KW)
    mrp = models.DecimalField(default=Decimal("0"), **MONEY_KW)
    sale_price = models.DecimalField(**MONEY_KW)

    discount_amount = models.DecimalField(default=Decimal("0"), **MONEY_KW)
    line_subtotal = models.DecimalField(default=Decimal("0"), **MONEY_KW)
    tax_breakup_json = models.JSONField(default=list, blank=True)
    line_total = models.DecimalField(default=Decimal("0"), **MONEY_KW)

    class Meta:
        verbose_name = "sale item"
        verbose_name_plural = "sale items"
        ordering = ("sale_id", "id")
        constraints = (
            models.CheckConstraint(
                name="sales_item_xor_target",
                check=(
                    models.Q(product__isnull=False, variant__isnull=True)
                    | models.Q(product__isnull=True, variant__isnull=False)
                ),
            ),
        )
        indexes = (
            models.Index(fields=("sale",)),
            models.Index(fields=("product",)),
            models.Index(fields=("variant",)),
        )

    def __str__(self) -> str:  # pragma: no cover
        target = self.variant_id or self.product_id
        return f"SaleItem<sale={self.sale_id} item={target} qty={self.qty}>"


# ---------------------------------------------------------------------------
# Payments
# ---------------------------------------------------------------------------


class SalePayment(BaseModel):
    """A single tender against a sale (cash, UPI, card, wallet, etc.)."""

    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="payments")
    payment_mode = models.ForeignKey(
        PaymentMode,
        on_delete=models.PROTECT,
        related_name="sale_payments",
    )
    amount = models.DecimalField(validators=(MinValueValidator(Decimal("0")),), **MONEY_KW)
    ref_no = models.CharField(max_length=64, blank=True)
    gateway_txn = models.CharField(max_length=128, blank=True)
    status = models.CharField(
        max_length=12,
        choices=SalePaymentStatus.choices,
        default=SalePaymentStatus.SUCCESS,
        db_index=True,
    )
    at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "sale payment"
        verbose_name_plural = "sale payments"
        ordering = ("sale_id", "at", "id")
        indexes = (
            models.Index(fields=("sale", "status")),
            models.Index(fields=("payment_mode", "status")),
        )

    def __str__(self) -> str:  # pragma: no cover
        return f"SalePayment<sale={self.sale_id} mode={self.payment_mode_id} {self.amount}>"


# ---------------------------------------------------------------------------
# Discounts
# ---------------------------------------------------------------------------


class Discount(BaseModel):
    """Reusable discount definition referenced by sales.

    ``condition_json`` is a free-form predicate evaluated by
    ``discount_engine.is_applicable``. Example shape::

        {
            "min_subtotal": "500.00",
            "applies_to_categories": [12, 17],
            "valid_from": "2025-01-01",
            "valid_to": "2025-12-31"
        }
    """

    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=128)
    scope = models.CharField(max_length=8, choices=DiscountScope.choices)
    kind = models.CharField(max_length=8, choices=DiscountKind.choices)
    value = models.DecimalField(validators=(MinValueValidator(Decimal("0")),), **MONEY_KW)
    condition_json = models.JSONField(default=dict, blank=True)
    requires_approval = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "discount"
        verbose_name_plural = "discounts"
        ordering = ("code",)
        indexes = (models.Index(fields=("is_active", "scope")),)

    def __str__(self) -> str:  # pragma: no cover
        return f"Discount<{self.code} {self.kind} {self.value}>"


# ---------------------------------------------------------------------------
# Price overrides (audit)
# ---------------------------------------------------------------------------


class PriceOverride(BaseModel):
    """Audit row for any line whose ``sale_price`` was manually overridden.

    The service layer is responsible for checking the
    ``sales.price.override`` permission *before* persisting; we still
    record ``perm_check_passed`` so downstream reports can flag anomalous
    rows (e.g. legacy data imports where the check wasn't enforced).
    """

    sale_item = models.OneToOneField(
        SaleItem,
        on_delete=models.CASCADE,
        related_name="price_override",
    )
    original_price = models.DecimalField(**MONEY_KW)
    new_price = models.DecimalField(**MONEY_KW)
    reason = models.CharField(max_length=255, blank=True)
    by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sale_price_overrides",
    )
    perm_check_passed = models.BooleanField(default=True)

    class Meta:
        verbose_name = "sale price override"
        verbose_name_plural = "sale price overrides"
        ordering = ("-id",)

    def __str__(self) -> str:  # pragma: no cover
        return f"PriceOverride<item={self.sale_item_id} {self.original_price}->{self.new_price}>"
