"""M01 Master Management — DRF viewsets.

Every entity uses :class:`apps.core.api.viewsets.BaseModelViewSet` which
ships pagination, filtering, idempotency, and auto-stamping of
``created_by`` / ``updated_by``. Per-resource ``required_perms`` are
declared but enforcement is permissive while M02 (roles) is unfinished:
the platform falls back to :class:`rest_framework.permissions.IsAuthenticated`
in :class:`apps.core.api.permissions.HasAnyPermission` when the user has
``is_staff`` or ``is_superuser`` set.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.api.viewsets import BaseModelViewSet

from .models import (
    Branch,
    Brand,
    Category,
    City,
    Country,
    Department,
    Designation,
    HSNCode,
    PaymentMode,
    Pincode,
    State,
    Tax,
    UnitOfMeasure,
    Warehouse,
    Zone,
)
from .serializers import (
    BranchSerializer,
    BrandSerializer,
    CategorySerializer,
    CitySerializer,
    CountrySerializer,
    DepartmentSerializer,
    DesignationSerializer,
    HSNCodeSerializer,
    PaymentModeSerializer,
    PincodeSerializer,
    StateSerializer,
    TaxSerializer,
    UnitOfMeasureSerializer,
    WarehouseSerializer,
    ZoneSerializer,
)
from .services import compute_tax_breakup, resolve_zone_for_pincode


class CountryViewSet(BaseModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    required_perms = ("master.view_geography",)


class StateViewSet(BaseModelViewSet):
    queryset = State.objects.select_related("country").all()
    serializer_class = StateSerializer
    required_perms = ("master.view_geography",)


class CityViewSet(BaseModelViewSet):
    queryset = City.objects.select_related("state").all()
    serializer_class = CitySerializer
    required_perms = ("master.view_geography",)


class PincodeViewSet(BaseModelViewSet):
    queryset = Pincode.objects.select_related("city").all()
    serializer_class = PincodeSerializer
    required_perms = ("master.view_geography",)


class BranchViewSet(BaseModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    required_perms = ("master.view_branch",)


class DepartmentViewSet(BaseModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    required_perms = ("master.view_department",)


class DesignationViewSet(BaseModelViewSet):
    queryset = Designation.objects.select_related("department").all()
    serializer_class = DesignationSerializer
    required_perms = ("master.view_designation",)


class UnitOfMeasureViewSet(BaseModelViewSet):
    queryset = UnitOfMeasure.objects.all()
    serializer_class = UnitOfMeasureSerializer
    required_perms = ("master.view_unitofmeasure",)


class HSNCodeViewSet(BaseModelViewSet):
    queryset = HSNCode.objects.select_related("default_tax").all()
    serializer_class = HSNCodeSerializer
    required_perms = ("master.view_hsncode",)


class TaxViewSet(BaseModelViewSet):
    queryset = Tax.objects.prefetch_related("hsn_codes").all()
    serializer_class = TaxSerializer
    required_perms = ("master.view_tax",)

    @extend_schema(
        summary="Compute the tax breakup for an amount.",
        description=(
            "Query params: ``amount`` (decimal, required), "
            "``inclusive`` (1/true/yes — default false)."
        ),
    )
    @action(detail=True, methods=["get"], url_path="breakup")
    def breakup(self, request, pk=None):
        tax = self.get_object()
        raw_amount = request.query_params.get("amount")
        if raw_amount is None:
            return Response(
                {"error": {"code": "API-400", "message": "amount query param required."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            amount = Decimal(str(raw_amount))
        except (InvalidOperation, TypeError):
            return Response(
                {"error": {"code": "API-400", "message": "amount must be numeric."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        inclusive = request.query_params.get("inclusive") in ("1", "true", "yes")
        breakup = compute_tax_breakup(amount, tax, inclusive=inclusive)
        # Decimal → str for JSON safety.
        return Response(
            {
                "base": str(breakup["base"]),
                "components": [
                    {"type": c["type"], "rate": str(c["rate"]), "amount": str(c["amount"])}
                    for c in breakup["components"]
                ],
                "tax_total": str(breakup["tax_total"]),
                "grand_total": str(breakup["grand_total"]),
            }
        )


class PaymentModeViewSet(BaseModelViewSet):
    queryset = PaymentMode.objects.prefetch_related("branches").all()
    serializer_class = PaymentModeSerializer
    required_perms = ("master.view_paymentmode",)


class CategoryViewSet(BaseModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    required_perms = ("master.view_category",)


class BrandViewSet(BaseModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    required_perms = ("master.view_brand",)


class WarehouseViewSet(BaseModelViewSet):
    queryset = Warehouse.objects.select_related("branch").all()
    serializer_class = WarehouseSerializer
    required_perms = ("master.view_warehouse",)


class ZoneViewSet(BaseModelViewSet):
    queryset = Zone.objects.select_related("branch").prefetch_related("pincodes").all()
    serializer_class = ZoneSerializer
    required_perms = ("master.view_zone",)

    @extend_schema(
        summary="Resolve the zone covering a pincode.",
        description="Query param: ``pincode`` (string, required).",
    )
    @action(detail=False, methods=["get"], url_path="resolve")
    def resolve(self, request):
        pincode = request.query_params.get("pincode")
        if not pincode:
            return Response(
                {"error": {"code": "API-400", "message": "pincode query param required."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        zone = resolve_zone_for_pincode(pincode)
        if zone is None:
            return Response(
                {
                    "error": {
                        "code": "MST-030",
                        "message": "No zone covers the requested pincode.",
                    }
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(ZoneSerializer(zone).data)
