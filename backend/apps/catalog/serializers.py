"""DRF serializers for the M03 Catalog API."""

from __future__ import annotations

from rest_framework import serializers

from apps.core.api.serializers import BaseModelSerializer

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

# ---------------------------------------------------------------------------
# Products & variants
# ---------------------------------------------------------------------------


class ProductImageSerializer(BaseModelSerializer):
    class Meta:
        model = ProductImage
        fields = ("id", "product", "image", "position", "alt", "is_active")


class ProductVariantSerializer(BaseModelSerializer):
    class Meta:
        model = ProductVariant
        fields = (
            "id",
            "product",
            "sku",
            "barcode",
            "attributes_json",
            "image",
            "is_default",
            "is_active",
        )


class ProductSerializer(BaseModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "code",
            "sku",
            "name",
            "slug",
            "brand",
            "category",
            "hsn",
            "tax",
            "base_uom",
            "description",
            "attributes_json",
            "is_variant_parent",
            "status",
            "seo_title",
            "seo_description",
            "seo_image",
            "variants",
            "images",
            "is_active",
            "created_at",
            "updated_at",
        )


# ---------------------------------------------------------------------------
# Availability + pricing
# ---------------------------------------------------------------------------


class ProductBranchAvailabilitySerializer(BaseModelSerializer):
    class Meta:
        model = ProductBranchAvailability
        fields = ("id", "product", "branch", "is_listed", "is_active")


class ProductPriceSerializer(BaseModelSerializer):
    class Meta:
        model = ProductPrice
        fields = (
            "id",
            "product",
            "variant",
            "branch",
            "mrp",
            "sale_price",
            "cost_price",
            "valid_from",
            "valid_to",
            "is_active",
        )

    def validate(self, attrs):
        product = attrs.get("product")
        variant = attrs.get("variant")
        if bool(product) == bool(variant):
            raise serializers.ValidationError("Specify exactly one of product or variant.")
        valid_from = attrs.get("valid_from")
        valid_to = attrs.get("valid_to")
        if valid_to is not None and valid_from is not None and valid_to <= valid_from:
            raise serializers.ValidationError("valid_to must be after valid_from.")
        return attrs


# ---------------------------------------------------------------------------
# Bundles
# ---------------------------------------------------------------------------


class BundleComponentSerializer(BaseModelSerializer):
    class Meta:
        model = BundleComponent
        fields = ("id", "bundle", "product", "quantity", "is_active")


class BundleSerializer(BaseModelSerializer):
    components = BundleComponentSerializer(many=True, read_only=True)

    class Meta:
        model = Bundle
        fields = (
            "id",
            "code",
            "name",
            "kind",
            "price_policy",
            "fixed_price",
            "components",
            "is_active",
        )

    def validate(self, attrs):
        from .models import BundlePricePolicy

        policy = attrs.get("price_policy", BundlePricePolicy.SUM)
        if policy == BundlePricePolicy.FIXED and attrs.get("fixed_price") is None:
            raise serializers.ValidationError("Bundle with FIXED policy requires fixed_price.")
        return attrs


# ---------------------------------------------------------------------------
# Barcodes & attributes
# ---------------------------------------------------------------------------


class BarcodeSerializer(BaseModelSerializer):
    class Meta:
        model = Barcode
        fields = ("id", "value", "type", "product", "variant", "is_active")

    def validate(self, attrs):
        if bool(attrs.get("product")) == bool(attrs.get("variant")):
            raise serializers.ValidationError("Specify exactly one of product or variant.")
        return attrs


class AttributeSerializer(BaseModelSerializer):
    class Meta:
        model = Attribute
        fields = ("id", "code", "name", "type", "options_json", "is_active")


class ProductAttributeValueSerializer(BaseModelSerializer):
    class Meta:
        model = ProductAttributeValue
        fields = ("id", "product", "attribute", "value", "is_active")
