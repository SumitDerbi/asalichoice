"""URL routes for the master-management API.

Mounted by :mod:`config.urls` under ``/api/v1/master/``.
"""

from __future__ import annotations

from rest_framework.routers import DefaultRouter

from .views import (
    BranchViewSet,
    BrandViewSet,
    CategoryViewSet,
    CityViewSet,
    CountryViewSet,
    DepartmentViewSet,
    DesignationViewSet,
    HSNCodeViewSet,
    PaymentModeViewSet,
    PincodeViewSet,
    StateViewSet,
    TaxViewSet,
    UnitOfMeasureViewSet,
    WarehouseViewSet,
    ZoneViewSet,
)

app_name = "master"

router = DefaultRouter()
router.register("branches", BranchViewSet, basename="branch")
router.register("departments", DepartmentViewSet, basename="department")
router.register("designations", DesignationViewSet, basename="designation")
router.register("uom", UnitOfMeasureViewSet, basename="uom")
router.register("taxes", TaxViewSet, basename="tax")
router.register("hsn", HSNCodeViewSet, basename="hsn")
router.register("payment-modes", PaymentModeViewSet, basename="payment-mode")
router.register("categories", CategoryViewSet, basename="category")
router.register("brands", BrandViewSet, basename="brand")
router.register("warehouses", WarehouseViewSet, basename="warehouse")
router.register("zones", ZoneViewSet, basename="zone")
router.register("countries", CountryViewSet, basename="country")
router.register("states", StateViewSet, basename="state")
router.register("cities", CityViewSet, basename="city")
router.register("pincodes", PincodeViewSet, basename="pincode")

urlpatterns = router.urls
