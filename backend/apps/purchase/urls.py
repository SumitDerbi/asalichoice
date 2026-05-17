"""URL routes for M04 Purchase. Mounted under ``/api/v1/purchase/``."""

from __future__ import annotations

from rest_framework.routers import DefaultRouter

from .views import (
    GRNViewSet,
    PurchaseInvoiceViewSet,
    PurchaseOrderViewSet,
    PurchaseReturnViewSet,
    VendorLedgerViewSet,
    VendorViewSet,
)

app_name = "purchase"

router = DefaultRouter()
router.register("vendors", VendorViewSet, basename="vendor")
router.register("pos", PurchaseOrderViewSet, basename="po")
router.register("grns", GRNViewSet, basename="grn")
router.register("invoices", PurchaseInvoiceViewSet, basename="invoice")
router.register("returns", PurchaseReturnViewSet, basename="return")
router.register("ledger", VendorLedgerViewSet, basename="ledger")

urlpatterns = router.urls
