"""URL routes for M05 Inventory. Mounted under ``/api/v1/inventory/``."""

from __future__ import annotations

from rest_framework.routers import DefaultRouter

from .views import (
    BatchViewSet,
    BranchTransferViewSet,
    InventoryLedgerViewSet,
    PhysicalCountViewSet,
    ReservationViewSet,
    StockAdjustmentViewSet,
    StockViewSet,
    WastageViewSet,
)

app_name = "inventory"

router = DefaultRouter()
router.register("stock", StockViewSet, basename="stock")
router.register("batches", BatchViewSet, basename="batch")
router.register("ledger", InventoryLedgerViewSet, basename="ledger")
router.register("reservations", ReservationViewSet, basename="reservation")
router.register("transfers", BranchTransferViewSet, basename="transfer")
router.register("adjustments", StockAdjustmentViewSet, basename="adjustment")
router.register("wastage", WastageViewSet, basename="wastage")
router.register("counts", PhysicalCountViewSet, basename="count")

urlpatterns = router.urls
