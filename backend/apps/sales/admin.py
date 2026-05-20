"""Admin registrations for M11 Sales."""

from __future__ import annotations

from django.contrib import admin

from .models import Discount, PriceOverride, Sale, SaleItem, SalePayment


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    fields = (
        "product",
        "variant",
        "uom",
        "qty",
        "sale_price",
        "discount_amount",
        "line_subtotal",
        "tax",
        "line_total",
    )
    readonly_fields = ("line_subtotal", "line_total")


class SalePaymentInline(admin.TabularInline):
    model = SalePayment
    extra = 0
    fields = ("payment_mode", "amount", "ref_no", "gateway_txn", "status", "at")
    readonly_fields = ("at",)


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = (
        "sale_no",
        "branch",
        "origin",
        "status",
        "grand_total",
        "payment_total",
        "billed_at",
    )
    list_filter = ("status", "origin", "branch", "tax_mode")
    search_fields = ("sale_no", "notes")
    readonly_fields = (
        "subtotal",
        "discount_total",
        "tax_total",
        "grand_total",
        "payment_total",
        "totals_json",
        "billed_at",
        "cancelled_at",
    )
    inlines = (SaleItemInline, SalePaymentInline)


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ("id", "sale", "product", "variant", "qty", "sale_price", "line_total")
    list_filter = ("sale__status",)
    search_fields = ("sale__sale_no",)


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "scope", "kind", "value", "is_active", "requires_approval")
    list_filter = ("scope", "kind", "is_active", "requires_approval")
    search_fields = ("code", "name")


@admin.register(PriceOverride)
class PriceOverrideAdmin(admin.ModelAdmin):
    list_display = ("sale_item", "original_price", "new_price", "by", "perm_check_passed")
    list_filter = ("perm_check_passed",)
    readonly_fields = ("sale_item", "original_price", "new_price", "by", "perm_check_passed")
