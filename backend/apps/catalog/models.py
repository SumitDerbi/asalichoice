"""M03 Catalog — domain models.

Hierarchy:
    Product → variants, images, branch availability, prices, attribute values
    Bundle  → BundleComponent[]
    Barcode → unique value per product/variant

Pricing model: a single :class:`ProductPrice` row points at *either*
``product`` or ``variant`` (XOR via :class:`Meta.constraints`) and is
scoped to a branch with an effective-date window (``valid_from`` /
``valid_to``). See ADR-006 for the rationale.
"""

from __future__ import annotations

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from apps.core.models import BaseModel
from apps.master.models import Branch, Brand, Category, HSNCode, Tax, UnitOfMeasure


class ProductStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    ACTIVE = "ACTIVE", "Active"
    ARCHIVED = "ARCHIVED", "Archived"


class Product(BaseModel):
    """A top-level sellable item.

    When ``is_variant_parent`` is True the product is purely a parent
    for child :class:`ProductVariant` rows and cannot be sold by itself
    (POS picks a specific variant). Otherwise the product is sold
    directly using its own SKU.
    """

    code = models.CharField(max_length=64, unique=True)
    sku = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=240)
    slug = models.SlugField(max_length=260, unique=True)

    brand = models.ForeignKey(
        Brand, on_delete=models.PROTECT, related_name="products", null=True, blank=True
    )
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    hsn = models.ForeignKey(
        HSNCode, on_delete=models.PROTECT, related_name="products", null=True, blank=True
    )
    tax = models.ForeignKey(
        Tax, on_delete=models.PROTECT, related_name="products", null=True, blank=True
    )
    base_uom = models.ForeignKey(UnitOfMeasure, on_delete=models.PROTECT, related_name="products")

    description = models.TextField(blank=True, default="")
    attributes_json = models.JSONField(default=dict, blank=True)
    is_variant_parent = models.BooleanField(default=False)
    status = models.CharField(
        max_length=16, choices=ProductStatus.choices, default=ProductStatus.DRAFT
    )

    seo_title = models.CharField(max_length=240, blank=True, default="")
    seo_description = models.CharField(max_length=500, blank=True, default="")
    seo_image = models.ImageField(upload_to="catalog/seo/", null=True, blank=True)

    class Meta:
        ordering = ("code",)
        indexes = (
            models.Index(fields=("status",)),
            models.Index(fields=("brand",)),
            models.Index(fields=("category",)),
            models.Index(fields=("name",)),
        )

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.sku} — {self.name}"


class ProductVariant(BaseModel):
    """A buyable child of a variant-parent product."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    sku = models.CharField(max_length=64, unique=True)
    barcode = models.CharField(max_length=64, blank=True, default="")
    attributes_json = models.JSONField(default=dict, blank=True)
    image = models.ImageField(upload_to="catalog/variants/", null=True, blank=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ("product_id", "sku")
        indexes = (models.Index(fields=("product",)),)

    def __str__(self) -> str:  # pragma: no cover
        return self.sku


class ProductImage(BaseModel):
    """Ordered gallery image for a product."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="catalog/products/")
    position = models.PositiveSmallIntegerField(default=0)
    alt = models.CharField(max_length=240, blank=True, default="")

    class Meta:
        ordering = ("product_id", "position", "id")
        indexes = (models.Index(fields=("product", "position")),)


class ProductBranchAvailability(BaseModel):
    """Whether a product is listed/visible at a given branch."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="branch_availability"
    )
    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name="product_availability"
    )
    is_listed = models.BooleanField(default=True)

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=("product", "branch"),
                name="catalog_unique_product_branch",
            ),
        )
        indexes = (models.Index(fields=("branch", "is_listed")),)


class ProductPrice(BaseModel):
    """Effective-dated, branch-scoped price band.

    Exactly one of (``product``, ``variant``) must be set — enforced by
    a check constraint. The pricing service finds the row with the
    latest ``valid_from`` whose window covers ``at`` (or now).
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="prices",
        null=True,
        blank=True,
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="prices",
        null=True,
        blank=True,
    )
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="prices")

    mrp = models.DecimalField(
        max_digits=14, decimal_places=2, validators=(MinValueValidator(Decimal("0")),)
    )
    sale_price = models.DecimalField(
        max_digits=14, decimal_places=2, validators=(MinValueValidator(Decimal("0")),)
    )
    cost_price = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=(MinValueValidator(Decimal("0")),),
        null=True,
        blank=True,
    )

    valid_from = models.DateTimeField(db_index=True)
    valid_to = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        ordering = ("-valid_from",)
        constraints = (
            models.CheckConstraint(
                name="catalog_price_xor_target",
                check=(
                    models.Q(product__isnull=False, variant__isnull=True)
                    | models.Q(product__isnull=True, variant__isnull=False)
                ),
            ),
        )
        indexes = (
            models.Index(fields=("product", "branch", "valid_from")),
            models.Index(fields=("variant", "branch", "valid_from")),
        )


class BundleKind(models.TextChoices):
    COMBO = "COMBO", "Combo"
    MIX_AND_MATCH = "MIX_AND_MATCH", "Mix & Match"


class BundlePricePolicy(models.TextChoices):
    FIXED = "FIXED", "Fixed bundle price"
    SUM = "SUM", "Sum of components"


class Bundle(BaseModel):
    """A group of products sold as a unit."""

    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=240)
    kind = models.CharField(max_length=20, choices=BundleKind.choices, default=BundleKind.COMBO)
    price_policy = models.CharField(
        max_length=10,
        choices=BundlePricePolicy.choices,
        default=BundlePricePolicy.SUM,
    )
    fixed_price = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ("code",)


class BundleComponent(BaseModel):
    """One line of a :class:`Bundle`."""

    bundle = models.ForeignKey(Bundle, on_delete=models.CASCADE, related_name="components")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="+")
    quantity = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal("1"))

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=("bundle", "product"),
                name="catalog_unique_bundle_product",
            ),
        )


class BarcodeType(models.TextChoices):
    EAN13 = "EAN13", "EAN-13"
    UPC = "UPC", "UPC"
    CODE128 = "CODE128", "Code128"
    CUSTOM = "CUSTOM", "Custom"


class Barcode(BaseModel):
    """Scannable barcode pointing at a product or variant (XOR)."""

    value = models.CharField(max_length=64, unique=True)
    type = models.CharField(max_length=16, choices=BarcodeType.choices, default=BarcodeType.EAN13)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="barcodes", null=True, blank=True
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="barcodes",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ("value",)
        constraints = (
            models.CheckConstraint(
                name="catalog_barcode_xor_target",
                check=(
                    models.Q(product__isnull=False, variant__isnull=True)
                    | models.Q(product__isnull=True, variant__isnull=False)
                ),
            ),
        )


class AttributeType(models.TextChoices):
    TEXT = "TEXT", "Text"
    NUMBER = "NUMBER", "Number"
    BOOL = "BOOL", "Boolean"
    SELECT = "SELECT", "Select"


class Attribute(BaseModel):
    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=120)
    type = models.CharField(
        max_length=16, choices=AttributeType.choices, default=AttributeType.TEXT
    )
    options_json = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ("code",)


class ProductAttributeValue(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="attribute_values")
    attribute = models.ForeignKey(Attribute, on_delete=models.PROTECT, related_name="values")
    value = models.CharField(max_length=500)

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=("product", "attribute"),
                name="catalog_unique_product_attribute",
            ),
        )


__all__ = [
    "Attribute",
    "AttributeType",
    "Barcode",
    "BarcodeType",
    "Bundle",
    "BundleComponent",
    "BundleKind",
    "BundlePricePolicy",
    "Product",
    "ProductAttributeValue",
    "ProductBranchAvailability",
    "ProductImage",
    "ProductPrice",
    "ProductStatus",
    "ProductVariant",
]
