"""Django admin registrations for the catalog app."""

from __future__ import annotations

from django.contrib import admin

from .models import (
    Attribute,
    Barcode,
    Bundle,
    BundleComponent,
    Product,
    ProductAttributeValue,
    ProductBranchAvailability,
    ProductImage,
    ProductPrice,
    ProductVariant,
)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "code", "name", "status", "brand", "category")
    search_fields = ("sku", "code", "name")
    list_filter = ("status", "brand", "category")


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("sku", "product", "is_default")
    search_fields = ("sku", "barcode")


@admin.register(ProductPrice)
class ProductPriceAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "variant", "branch", "mrp", "sale_price", "valid_from")
    list_filter = ("branch",)


for model in (
    ProductImage,
    ProductBranchAvailability,
    Bundle,
    BundleComponent,
    Barcode,
    Attribute,
    ProductAttributeValue,
):
    admin.site.register(model)
