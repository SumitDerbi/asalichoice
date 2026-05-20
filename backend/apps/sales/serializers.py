"""DRF serializers for M11 Sales."""

from __future__ import annotations

from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.catalog.models import Product, ProductVariant
from apps.core.api.serializers import BaseModelSerializer
from apps.inventory.models import Batch
from apps.master.models import Branch, HSNCode, PaymentMode, Tax, UnitOfMeasure

from .models import Discount, PriceOverride, Sale, SaleItem, SalePayment

_User = get_user_model()


class SaleItemSerializer(BaseModelSerializer):
    class Meta:
        model = SaleItem
        fields = (
            "id",
            "sale",
            "product",
            "variant",
            "uom",
            "batch",
            "hsn",
            "tax",
            "qty",
            "mrp",
            "sale_price",
            "discount_amount",
            "line_subtotal",
            "tax_breakup_json",
            "line_total",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "line_subtotal",
            "tax_breakup_json",
            "line_total",
            "created_at",
            "updated_at",
        )


class SalePaymentSerializer(BaseModelSerializer):
    class Meta:
        model = SalePayment
        fields = (
            "id",
            "sale",
            "payment_mode",
            "amount",
            "ref_no",
            "gateway_txn",
            "status",
            "at",
        )
        read_only_fields = ("at",)


class SaleSerializer(BaseModelSerializer):
    items = SaleItemSerializer(many=True, read_only=True)
    payments = SalePaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Sale
        fields = (
            "id",
            "sale_no",
            "origin",
            "branch",
            "customer",
            "cashier",
            "terminal_id_external",
            "status",
            "tax_mode",
            "billed_at",
            "cancelled_at",
            "subtotal",
            "discount_total",
            "tax_total",
            "grand_total",
            "payment_total",
            "totals_json",
            "payment_terms_json",
            "notes",
            "offline_uuid",
            "items",
            "payments",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "sale_no",
            "status",
            "billed_at",
            "cancelled_at",
            "subtotal",
            "discount_total",
            "tax_total",
            "grand_total",
            "payment_total",
            "totals_json",
            "items",
            "payments",
            "created_at",
            "updated_at",
        )


class _DraftItemSerializer(serializers.Serializer):
    """Inline shape accepted by the draft-creation endpoint."""

    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), required=False, allow_null=True
    )
    variant = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariant.objects.all(), required=False, allow_null=True
    )
    uom = serializers.PrimaryKeyRelatedField(queryset=UnitOfMeasure.objects.all())
    batch = serializers.PrimaryKeyRelatedField(
        queryset=Batch.objects.all(), required=False, allow_null=True
    )
    hsn = serializers.PrimaryKeyRelatedField(
        queryset=HSNCode.objects.all(), required=False, allow_null=True
    )
    tax = serializers.PrimaryKeyRelatedField(
        queryset=Tax.objects.all(), required=False, allow_null=True
    )
    qty = serializers.DecimalField(max_digits=14, decimal_places=3, min_value=Decimal("0"))
    mrp = serializers.DecimalField(max_digits=14, decimal_places=4, required=False)
    sale_price = serializers.DecimalField(max_digits=14, decimal_places=4)
    discount_amount = serializers.DecimalField(
        max_digits=14, decimal_places=4, required=False, default=Decimal("0")
    )
    price_override_reason = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if bool(attrs.get("product")) == bool(attrs.get("variant")):
            raise serializers.ValidationError(
                "Each item must set exactly one of product / variant."
            )
        return attrs


class _DraftPaymentSerializer(serializers.Serializer):
    payment_mode = serializers.PrimaryKeyRelatedField(queryset=PaymentMode.objects.all())
    amount = serializers.DecimalField(max_digits=14, decimal_places=4, min_value=Decimal("0"))
    ref_no = serializers.CharField(required=False, allow_blank=True)
    gateway_txn = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(required=False)


class SaleCreateSerializer(serializers.Serializer):
    """Input shape for ``POST /api/v1/sales/``."""

    origin = serializers.CharField(default="POS")
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())
    customer = serializers.PrimaryKeyRelatedField(
        queryset=_User.objects.all(), required=False, allow_null=True
    )
    cashier = serializers.PrimaryKeyRelatedField(
        queryset=_User.objects.all(), required=False, allow_null=True
    )
    tax_mode = serializers.CharField(default="EXCLUSIVE")
    notes = serializers.CharField(required=False, allow_blank=True)
    offline_uuid = serializers.UUIDField(required=False, allow_null=True)
    items = _DraftItemSerializer(many=True)
    payments = _DraftPaymentSerializer(many=True, required=False, default=list)
    auto_post = serializers.BooleanField(required=False, default=False)


class DiscountSerializer(BaseModelSerializer):
    class Meta:
        model = Discount
        fields = (
            "id",
            "code",
            "name",
            "scope",
            "kind",
            "value",
            "condition_json",
            "requires_approval",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")


class PriceOverrideSerializer(BaseModelSerializer):
    class Meta:
        model = PriceOverride
        fields = (
            "id",
            "sale_item",
            "original_price",
            "new_price",
            "reason",
            "by",
            "perm_check_passed",
            "created_at",
        )
        read_only_fields = fields


__all__ = [
    "DiscountSerializer",
    "PriceOverrideSerializer",
    "SaleCreateSerializer",
    "SaleItemSerializer",
    "SalePaymentSerializer",
    "SaleSerializer",
]
