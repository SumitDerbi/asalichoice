"""DRF serializers for M01 Master Management."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from rest_framework import serializers

from apps.core.api.serializers import BaseModelSerializer

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
from .services import check_branch_depth, check_category_depth, validate_model

# ---------------------------------------------------------------------------
# Geographic
# ---------------------------------------------------------------------------


class CountrySerializer(BaseModelSerializer):
    class Meta:
        model = Country
        fields = ("id", "iso2", "iso3", "name", "phone_code", "currency", "is_active")


class StateSerializer(BaseModelSerializer):
    country_iso2 = serializers.CharField(source="country.iso2", read_only=True)

    class Meta:
        model = State
        fields = (
            "id",
            "country",
            "country_iso2",
            "code",
            "name",
            "gst_state_code",
            "is_active",
        )


class CitySerializer(BaseModelSerializer):
    state_code = serializers.CharField(source="state.code", read_only=True)

    class Meta:
        model = City
        fields = ("id", "state", "state_code", "name", "is_active")


class PincodeSerializer(BaseModelSerializer):
    class Meta:
        model = Pincode
        fields = ("id", "code", "city", "latitude", "longitude", "is_active")


# ---------------------------------------------------------------------------
# Organisation
# ---------------------------------------------------------------------------


class BranchSerializer(BaseModelSerializer):
    class Meta:
        model = Branch
        fields = (
            "id",
            "code",
            "name",
            "type",
            "parent",
            "address_json",
            "gstin",
            "phone",
            "email",
            "feature_flags_json",
            "is_active",
        )

    def validate(self, attrs):
        parent = attrs.get("parent") or (self.instance.parent if self.instance else None)
        check_branch_depth(parent)
        return attrs


class DepartmentSerializer(BaseModelSerializer):
    class Meta:
        model = Department
        fields = ("id", "code", "name", "is_active")


class DesignationSerializer(BaseModelSerializer):
    class Meta:
        model = Designation
        fields = ("id", "code", "name", "department", "is_active")


# ---------------------------------------------------------------------------
# Catalog support
# ---------------------------------------------------------------------------


class UnitOfMeasureSerializer(BaseModelSerializer):
    class Meta:
        model = UnitOfMeasure
        fields = (
            "id",
            "code",
            "name",
            "symbol",
            "decimals",
            "parent",
            "conversion_factor",
            "is_active",
        )


class HSNCodeSerializer(BaseModelSerializer):
    class Meta:
        model = HSNCode
        fields = ("id", "code", "description", "default_tax", "is_active")


class TaxSerializer(BaseModelSerializer):
    class Meta:
        model = Tax
        fields = (
            "id",
            "code",
            "name",
            "rate_total",
            "components_json",
            "hsn_codes",
            "is_active",
        )
        # ``rate_total`` is a denormalised cache of ``sum(components_json[*].rate)``;
        # the model's ``clean()`` enforces that equality. Clients only need to send
        # ``components_json`` — we derive ``rate_total`` from it in ``validate``.
        extra_kwargs = {"rate_total": {"required": False}}  # noqa: RUF012

    def validate(self, attrs):
        components = attrs.get("components_json")
        if components is None and self.instance is not None:
            components = self.instance.components_json
        if isinstance(components, list):
            try:
                derived = sum(
                    (Decimal(str(c.get("rate"))) for c in components if isinstance(c, dict)),
                    Decimal("0"),
                )
            except (InvalidOperation, TypeError):
                derived = None
            if derived is not None:
                attrs["rate_total"] = derived
        instance = Tax(
            **{
                **({"id": self.instance.id} if self.instance else {}),
                **{
                    k: v
                    for k, v in attrs.items()
                    if k != "hsn_codes"  # M2M not assignable on unsaved model
                },
            }
        )
        validate_model(instance)
        return attrs


class PaymentModeSerializer(BaseModelSerializer):
    class Meta:
        model = PaymentMode
        fields = (
            "id",
            "code",
            "name",
            "type",
            "is_online",
            "branches",
            "config_json",
            "is_active",
        )


class CategorySerializer(BaseModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "code", "name", "parent", "image", "seo_slug", "is_active")

    def validate(self, attrs):
        parent = attrs.get("parent") or (self.instance.parent if self.instance else None)
        check_category_depth(parent)
        return attrs


class BrandSerializer(BaseModelSerializer):
    class Meta:
        model = Brand
        fields = ("id", "code", "name", "logo", "description", "is_active")


class WarehouseSerializer(BaseModelSerializer):
    class Meta:
        model = Warehouse
        fields = ("id", "code", "name", "branch", "address_json", "is_active")


class ZoneSerializer(BaseModelSerializer):
    class Meta:
        model = Zone
        fields = (
            "id",
            "code",
            "name",
            "branch",
            "pincodes",
            "pincode_ranges_json",
            "is_active",
        )
