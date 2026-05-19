"""DRF serializers for M05 Inventory endpoints.

Stock / Batch / InventoryLedger are read-only — they are recomputed
or appended via the service layer and never edited through REST. The
document serializers (transfer / adjustment / wastage / count) accept
nested ``items`` on create so callers can build a draft in one POST.
"""

from __future__ import annotations

from rest_framework import serializers

from apps.core.api.serializers import BaseModelSerializer

from .models import (
    Batch,
    BranchTransfer,
    BranchTransferItem,
    InventoryLedger,
    PhysicalCount,
    PhysicalCountItem,
    Reservation,
    Stock,
    StockAdjustment,
    StockAdjustmentItem,
    Wastage,
    WastageItem,
)

# ---------------------------------------------------------------------------
# Read-only — Stock / Batch / Ledger
# ---------------------------------------------------------------------------


class StockSerializer(BaseModelSerializer):
    class Meta:
        model = Stock
        fields = (
            "id",
            "product",
            "variant",
            "branch",
            "warehouse",
            "qty_on_hand",
            "qty_reserved",
            "qty_in_transit",
            "last_movement_at",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class BatchSerializer(BaseModelSerializer):
    class Meta:
        model = Batch
        fields = (
            "id",
            "product",
            "variant",
            "branch",
            "batch_no",
            "mfg_date",
            "expiry_date",
            "cost_price",
            "qty_received",
            "qty_remaining",
            "status",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class InventoryLedgerSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryLedger
        fields = (
            "id",
            "product",
            "variant",
            "batch",
            "branch",
            "warehouse",
            "reference_type",
            "reference_id",
            "amount",
            "balance_before",
            "balance_after",
            "reason_code",
            "actor",
            "timestamp",
            "remarks",
        )
        read_only_fields = fields


# ---------------------------------------------------------------------------
# Reservations
# ---------------------------------------------------------------------------


class ReservationSerializer(BaseModelSerializer):
    class Meta:
        model = Reservation
        fields = (
            "id",
            "product",
            "variant",
            "branch",
            "qty",
            "ref_type",
            "ref_id",
            "expires_at",
            "status",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("status", "is_active", "created_at", "updated_at")

    def validate(self, attrs):
        if bool(attrs.get("product")) == bool(attrs.get("variant")):
            raise serializers.ValidationError("Specify exactly one of product or variant.")
        return attrs


# ---------------------------------------------------------------------------
# Branch transfers
# ---------------------------------------------------------------------------


class BranchTransferItemSerializer(BaseModelSerializer):
    class Meta:
        model = BranchTransferItem
        fields = (
            "id",
            "product",
            "variant",
            "batch",
            "qty_sent",
            "qty_received",
            "qty_lost",
        )
        read_only_fields = ("qty_lost",)

    def validate(self, attrs):
        if bool(attrs.get("product")) == bool(attrs.get("variant")):
            raise serializers.ValidationError("Specify exactly one of product or variant.")
        return attrs


class BranchTransferSerializer(BaseModelSerializer):
    items = BranchTransferItemSerializer(many=True, required=False)

    class Meta:
        model = BranchTransfer
        fields = (
            "id",
            "tr_no",
            "from_branch",
            "to_branch",
            "status",
            "dispatched_at",
            "received_at",
            "vehicle",
            "items",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("status", "dispatched_at", "received_at")

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        transfer = BranchTransfer.objects.create(**validated_data)
        for item in items_data:
            BranchTransferItem.objects.create(transfer=transfer, **item)
        return transfer


# ---------------------------------------------------------------------------
# Stock adjustment
# ---------------------------------------------------------------------------


class StockAdjustmentItemSerializer(BaseModelSerializer):
    class Meta:
        model = StockAdjustmentItem
        fields = ("id", "product", "variant", "batch", "qty_change")

    def validate(self, attrs):
        if bool(attrs.get("product")) == bool(attrs.get("variant")):
            raise serializers.ValidationError("Specify exactly one of product or variant.")
        return attrs


class StockAdjustmentSerializer(BaseModelSerializer):
    items = StockAdjustmentItemSerializer(many=True, required=False)

    class Meta:
        model = StockAdjustment
        fields = (
            "id",
            "adj_no",
            "branch",
            "reason_code",
            "status",
            "posted_at",
            "remarks",
            "items",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("status", "posted_at")

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        adj = StockAdjustment.objects.create(**validated_data)
        for item in items_data:
            StockAdjustmentItem.objects.create(adjustment=adj, **item)
        return adj


# ---------------------------------------------------------------------------
# Wastage
# ---------------------------------------------------------------------------


class WastageItemSerializer(BaseModelSerializer):
    class Meta:
        model = WastageItem
        fields = ("id", "product", "variant", "batch", "qty")

    def validate(self, attrs):
        if bool(attrs.get("product")) == bool(attrs.get("variant")):
            raise serializers.ValidationError("Specify exactly one of product or variant.")
        return attrs


class WastageSerializer(BaseModelSerializer):
    items = WastageItemSerializer(many=True, required=False)

    class Meta:
        model = Wastage
        fields = (
            "id",
            "wastage_no",
            "branch",
            "reason_code",
            "status",
            "posted_at",
            "remarks",
            "items",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("status", "posted_at")

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        w = Wastage.objects.create(**validated_data)
        for item in items_data:
            WastageItem.objects.create(wastage=w, **item)
        return w


# ---------------------------------------------------------------------------
# Physical count
# ---------------------------------------------------------------------------


class PhysicalCountItemSerializer(BaseModelSerializer):
    class Meta:
        model = PhysicalCountItem
        fields = ("id", "product", "variant", "qty_expected", "qty_counted")
        read_only_fields = ("qty_expected",)

    def validate(self, attrs):
        if bool(attrs.get("product")) == bool(attrs.get("variant")):
            raise serializers.ValidationError("Specify exactly one of product or variant.")
        return attrs


class PhysicalCountSerializer(BaseModelSerializer):
    items = PhysicalCountItemSerializer(many=True, required=False)

    class Meta:
        model = PhysicalCount
        fields = (
            "id",
            "count_no",
            "branch",
            "status",
            "posted_at",
            "remarks",
            "items",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("status", "posted_at")

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        count = PhysicalCount.objects.create(**validated_data)
        for item in items_data:
            PhysicalCountItem.objects.create(count=count, **item)
        return count
