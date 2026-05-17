"""M03 Catalog — DRF viewsets and custom actions."""

from __future__ import annotations

from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from apps.core.api.viewsets import BaseModelViewSet

from .exceptions import PriceNotFound
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
from .serializers import (
    AttributeSerializer,
    BarcodeSerializer,
    BundleComponentSerializer,
    BundleSerializer,
    ProductAttributeValueSerializer,
    ProductBranchAvailabilitySerializer,
    ProductImageSerializer,
    ProductPriceSerializer,
    ProductSerializer,
    ProductVariantSerializer,
)
from .services import get_effective_price, import_products_csv
from .services.catalog_service import archive_product


class ProductViewSet(BaseModelViewSet):
    """CRUD + search + archive for products."""

    queryset = Product.objects.select_related(
        "brand", "category", "hsn", "tax", "base_uom"
    ).prefetch_related("variants", "images")
    serializer_class = ProductSerializer
    required_perms = ("catalog.view",)

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        q = params.get("q")
        if q:
            qs = qs.filter(
                Q(name__icontains=q)
                | Q(sku__icontains=q)
                | Q(code__icontains=q)
                | Q(barcodes__value=q)
            ).distinct()
        status_param = params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)
        brand = params.get("brand")
        if brand:
            qs = qs.filter(brand_id=brand)
        category = params.get("category")
        if category:
            qs = qs.filter(category_id=category)
        return qs

    @extend_schema(summary="Archive a product (soft, status only).")
    @action(detail=True, methods=["post"], url_path="archive")
    def archive(self, request, pk=None):
        product = self.get_object()
        archive_product(product)
        return Response(self.get_serializer(product).data)

    @extend_schema(
        summary="Effective price for this product at a branch.",
        description="Query params: ``branch`` (required, int).",
    )
    @action(detail=True, methods=["get"], url_path="price")
    def price(self, request, pk=None):
        product = self.get_object()
        branch = request.query_params.get("branch")
        if not branch:
            return Response(
                {"error": {"code": "API-400", "message": "branch query param required."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            branch_id = int(branch)
        except (TypeError, ValueError):
            return Response(
                {"error": {"code": "API-400", "message": "branch must be integer."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            band = get_effective_price(product, branch_id)
        except PriceNotFound as exc:
            return Response(exc.to_envelope(), status=exc.status)
        return Response(
            {
                "mrp": str(band.mrp),
                "sale_price": str(band.sale_price),
                "cost_price": str(band.cost_price) if band.cost_price is not None else None,
                "band_id": band.band_id,
            }
        )


class ProductVariantViewSet(BaseModelViewSet):
    queryset = ProductVariant.objects.select_related("product").all()
    serializer_class = ProductVariantSerializer
    required_perms = ("catalog.view",)


class ProductImageViewSet(BaseModelViewSet):
    queryset = ProductImage.objects.select_related("product").all()
    serializer_class = ProductImageSerializer
    required_perms = ("catalog.view",)
    parser_classes = (MultiPartParser, FormParser)


class ProductBranchAvailabilityViewSet(BaseModelViewSet):
    queryset = ProductBranchAvailability.objects.select_related("product", "branch").all()
    serializer_class = ProductBranchAvailabilitySerializer
    required_perms = ("catalog.view",)


class ProductPriceViewSet(BaseModelViewSet):
    queryset = ProductPrice.objects.select_related("product", "variant", "branch").all()
    serializer_class = ProductPriceSerializer
    required_perms = ("catalog.view",)

    @extend_schema(
        summary="Bulk price lookup.",
        description=(
            'POST body: ``{"items": [{"product": id} | {"variant": id}, ' '...], "branch": id}``.'
        ),
    )
    @action(detail=False, methods=["post"], url_path="bulk-lookup")
    def bulk_lookup_action(self, request):
        from .services.pricing_service import bulk_lookup

        body = request.data or {}
        branch = body.get("branch")
        items = body.get("items", [])
        if not branch:
            return Response(
                {"error": {"code": "API-400", "message": "branch required."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        targets = []
        for entry in items:
            if "product" in entry:
                try:
                    targets.append((Product.objects.get(pk=entry["product"]), int(branch)))
                except Product.DoesNotExist:
                    continue
            elif "variant" in entry:
                try:
                    targets.append((ProductVariant.objects.get(pk=entry["variant"]), int(branch)))
                except ProductVariant.DoesNotExist:
                    continue
        result = bulk_lookup(targets)
        payload = {
            f"{kind}:{tid}": {
                "mrp": str(band.mrp),
                "sale_price": str(band.sale_price),
                "cost_price": str(band.cost_price) if band.cost_price is not None else None,
                "band_id": band.band_id,
            }
            for (kind, tid, _bid), band in result.items()
        }
        return Response({"prices": payload})


class BundleViewSet(BaseModelViewSet):
    queryset = Bundle.objects.prefetch_related("components").all()
    serializer_class = BundleSerializer
    required_perms = ("catalog.view",)


class BundleComponentViewSet(BaseModelViewSet):
    queryset = BundleComponent.objects.select_related("bundle", "product").all()
    serializer_class = BundleComponentSerializer
    required_perms = ("catalog.view",)


class BarcodeViewSet(BaseModelViewSet):
    queryset = Barcode.objects.select_related("product", "variant").all()
    serializer_class = BarcodeSerializer
    required_perms = ("catalog.view",)

    @extend_schema(summary="Resolve a barcode value to its product/variant.")
    @action(detail=False, methods=["get"], url_path="resolve")
    def resolve(self, request):
        value = request.query_params.get("value")
        if not value:
            return Response(
                {"error": {"code": "API-400", "message": "value query param required."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        barcode = Barcode.objects.filter(value=value).first()
        if barcode is None:
            return Response(
                {"error": {"code": "CAT-040", "message": "Barcode not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(self.get_serializer(barcode).data)


class AttributeViewSet(BaseModelViewSet):
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer
    required_perms = ("catalog.view",)


class ProductAttributeValueViewSet(BaseModelViewSet):
    queryset = ProductAttributeValue.objects.select_related("product", "attribute").all()
    serializer_class = ProductAttributeValueSerializer
    required_perms = ("catalog.view",)


class ImportViewSet(BaseModelViewSet):
    """CSV product import.

    Not a real CRUD set — only the ``create`` action is wired and the
    queryset is empty so listing returns 200/[]. Set
    ``required_perms = ("catalog.import",)``.
    """

    queryset = Product.objects.none()
    serializer_class = ProductSerializer
    required_perms = ("catalog.import",)
    parser_classes = (MultiPartParser, FormParser)
    http_method_names = ("post",)

    def create(self, request, *args, **kwargs):
        upload = request.FILES.get("file")
        if upload is None:
            return Response(
                {"error": {"code": "API-400", "message": "file upload required."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        dry_run = request.data.get("dry_run") in ("1", "true", "yes", True)
        result = import_products_csv(upload.read(), dry_run=dry_run)
        return Response(result, status=status.HTTP_200_OK)
