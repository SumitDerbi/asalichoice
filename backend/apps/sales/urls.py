"""URL routes for M11 Sales. Mounted under ``/api/v1/sales/``."""

from __future__ import annotations

from rest_framework.routers import DefaultRouter

from .views import DiscountViewSet, SaleViewSet

app_name = "sales"

router = DefaultRouter()
router.register("sales", SaleViewSet, basename="sale")
router.register("discounts", DiscountViewSet, basename="discount")

urlpatterns = router.urls
