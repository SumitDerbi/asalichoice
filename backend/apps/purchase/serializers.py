"""DRF serializers for M04 purchase endpoints."""

from __future__ import annotations

from rest_framework import serializers

from apps.core.api.serializers import BaseModelSerializer

from .models import (
    GRN,
    GRNItem,
    POItem,
    PurchaseInvoice,
    PurchaseOrder,
    PurchaseReturn,
    Vendor,
    VendorBankAccount,
    VendorContact,
    VendorLedger,
)


class VendorContactSerializer(BaseModelSerializer):
    class Meta:
        model = VendorContact
        fields = ("id", "vendor", "name", "role", "email", "mobile", "is_active")


class VendorBankAccountSerializer(BaseModelSerializer):
    class Meta:
        model = VendorBankAccount
        fields = (
            "id",
            "vendor",
            "account_no_masked",
            "ifsc",
            "bank_name",
            "is_default",
            "is_active",
        )


class VendorSerializer(BaseModelSerializer):
    contacts = VendorContactSerializer(many=True, read_only=True)
    bank_accounts = VendorBankAccountSerializer(many=True, read_only=True)

    class Meta:
        model = Vendor
        fields = (
            "id",
            "code",
            "name",
            "contact_name",
            "contact_email",
            "contact_mobile",
            "gstin",
            "pan",
            "addresses_json",
            "payment_terms_json",
            "credit_limit",
            "branches",
            "contacts",
            "bank_accounts",
            "is_active",
            "created_at",
            "updated_at",
        )


class POItemSerializer(BaseModelSerializer):
    class Meta:
        model = POItem
        fields = (
            "id",
            "po",
            "product",
            "variant",
            "qty",
            "uom",
            "rate",
            "tax",
            "discount",
            "line_total",
            "is_active",
        )

    def validate(self, attrs):
        if bool(attrs.get("product")) == bool(attrs.get("variant")):
            raise serializers.ValidationError("Specify exactly one of product or variant.")
        return attrs


class PurchaseOrderSerializer(BaseModelSerializer):
    items = POItemSerializer(many=True, required=False)

    class Meta:
        model = PurchaseOrder
        fields = (
            "id",
            "po_no",
            "vendor",
            "branch",
            "status",
            "expected_delivery",
            "terms",
            "totals_json",
            "approval_chain_json",
            "approved_by",
            "approved_at",
            "items",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("status", "approved_by", "approved_at", "approval_chain_json")


class GRNItemSerializer(BaseModelSerializer):
    class Meta:
        model = GRNItem
        fields = (
            "id",
            "grn",
            "po_item",
            "product",
            "variant",
            "qty_received",
            "qty_accepted",
            "qty_rejected",
            "rejection_reason",
            "batch_no",
            "mfg_date",
            "expiry_date",
            "cost_price",
            "is_active",
        )

    def validate(self, attrs):
        if bool(attrs.get("product")) == bool(attrs.get("variant")):
            raise serializers.ValidationError("Specify exactly one of product or variant.")
        return attrs


class GRNSerializer(BaseModelSerializer):
    items = GRNItemSerializer(many=True, required=False)

    class Meta:
        model = GRN
        fields = (
            "id",
            "grn_no",
            "po",
            "vendor",
            "branch",
            "status",
            "received_at",
            "vehicle_no",
            "transporter",
            "offline_uuid",
            "totals_json",
            "items",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("status",)


class PurchaseInvoiceSerializer(BaseModelSerializer):
    class Meta:
        model = PurchaseInvoice
        fields = (
            "id",
            "pi_no",
            "vendor",
            "branch",
            "grns",
            "invoice_no_vendor",
            "invoice_date",
            "due_date",
            "totals_json",
            "status",
            "payment_terms",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("status",)


class PurchaseReturnSerializer(BaseModelSerializer):
    class Meta:
        model = PurchaseReturn
        fields = (
            "id",
            "pr_no",
            "grn",
            "vendor",
            "branch",
            "reason",
            "status",
            "items_json",
            "totals_json",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("status",)


class VendorLedgerSerializer(BaseModelSerializer):
    class Meta:
        model = VendorLedger
        fields = (
            "id",
            "vendor",
            "branch",
            "reference_type",
            "reference_id",
            "amount",
            "balance_before",
            "balance_after",
            "timestamp",
            "remarks",
        )
        read_only_fields = fields
