"""URL routes for M03 Catalog. Mounted under ``/api/v1/catalog/``."""

from __future__ import annotations

from rest_framework.routers import DefaultRouter

from .views import (
    AttributeViewSet,
    BarcodeViewSet,
    BundleComponentViewSet,
    BundleViewSet,
    ImportViewSet,
    ProductAttributeValueViewSet,
    ProductBranchAvailabilityViewSet,
    ProductImageViewSet,
    ProductPriceViewSet,
    ProductVariantViewSet,
    ProductViewSet,
)

app_name = "catalog"

router = DefaultRouter()
router.register("products", ProductViewSet, basename="product")
router.register("variants", ProductVariantViewSet, basename="variant")
router.register("images", ProductImageViewSet, basename="image")
router.register("availability", ProductBranchAvailabilityViewSet, basename="availability")
router.register("prices", ProductPriceViewSet, basename="price")
router.register("bundles", BundleViewSet, basename="bundle")
router.register("bundle-components", BundleComponentViewSet, basename="bundle-component")
router.register("barcodes", BarcodeViewSet, basename="barcode")
router.register("attributes", AttributeViewSet, basename="attribute")
router.register("attribute-values", ProductAttributeValueViewSet, basename="attribute-value")
router.register("import", ImportViewSet, basename="import")

urlpatterns = router.urls
