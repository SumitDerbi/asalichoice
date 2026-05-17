"""Django admin registrations for the purchase app."""

from __future__ import annotations

from django.contrib import admin

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


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "gstin", "is_active")
    search_fields = ("code", "name", "gstin", "pan")
    list_filter = ("is_active",)


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ("po_no", "vendor", "branch", "status", "approved_at")
    list_filter = ("status", "branch")
    search_fields = ("po_no",)


@admin.register(GRN)
class GRNAdmin(admin.ModelAdmin):
    list_display = ("grn_no", "vendor", "branch", "status", "received_at")
    list_filter = ("status", "branch")
    search_fields = ("grn_no", "offline_uuid")


@admin.register(PurchaseInvoice)
class PurchaseInvoiceAdmin(admin.ModelAdmin):
    list_display = ("pi_no", "vendor", "branch", "status", "invoice_date", "due_date")
    list_filter = ("status",)
    search_fields = ("pi_no", "invoice_no_vendor")


@admin.register(PurchaseReturn)
class PurchaseReturnAdmin(admin.ModelAdmin):
    list_display = ("pr_no", "grn", "vendor", "status")
    list_filter = ("status",)
    search_fields = ("pr_no",)


@admin.register(VendorLedger)
class VendorLedgerAdmin(admin.ModelAdmin):
    list_display = ("id", "vendor", "branch", "amount", "balance_after", "timestamp")
    list_filter = ("branch",)
    search_fields = ("reference_id",)


for model in (POItem, GRNItem, VendorContact, VendorBankAccount):
    admin.site.register(model)
