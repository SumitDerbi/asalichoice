"""Master Management models (M01).

All concrete models here inherit :class:`apps.core.models.BaseModel`
(timestamps + soft-delete + audit fk's). Migrations are generated
schema-only; default data ships via ``seed_master``.

Layout (one file, alphabetised below the geo block) keeps related
constraints in one place — every later module FKs into this app.
"""

from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import BaseModel

# ---------------------------------------------------------------------------
# Geographic masters
# ---------------------------------------------------------------------------


class Country(BaseModel):
    iso2 = models.CharField(max_length=2, unique=True)
    iso3 = models.CharField(max_length=3, blank=True, default="")
    name = models.CharField(max_length=100)
    phone_code = models.CharField(max_length=8, blank=True, default="")
    currency = models.CharField(max_length=3, blank=True, default="")

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "countries"

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.name} ({self.iso2})"


class State(BaseModel):
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name="states")
    code = models.CharField(max_length=8)
    name = models.CharField(max_length=100)
    gst_state_code = models.CharField(
        max_length=2, blank=True, default="", help_text="Numeric GST state code (01-37 for India)."
    )

    class Meta:
        ordering = ("country__name", "name")
        constraints = [
            models.UniqueConstraint(fields=("country", "code"), name="uniq_state_country_code"),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.name}, {self.country.iso2}"


class City(BaseModel):
    state = models.ForeignKey(State, on_delete=models.PROTECT, related_name="cities")
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ("state__name", "name")
        constraints = [
            models.UniqueConstraint(fields=("state", "name"), name="uniq_city_state_name"),
        ]
        verbose_name_plural = "cities"

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.name}, {self.state.code}"


class Pincode(BaseModel):
    code = models.CharField(max_length=10, unique=True)
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name="pincodes")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        ordering = ("code",)

    def __str__(self) -> str:  # pragma: no cover
        return self.code


# ---------------------------------------------------------------------------
# Organisation masters
# ---------------------------------------------------------------------------


class BranchType(models.TextChoices):
    HQ = "HQ", "Head Office"
    STORE = "STORE", "Store"
    WAREHOUSE = "WAREHOUSE", "Warehouse"
    DARK_STORE = "DARK_STORE", "Dark Store"


class Branch(BaseModel):
    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=120)
    type = models.CharField(max_length=16, choices=BranchType.choices, default=BranchType.STORE)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT, related_name="children"
    )
    address_json = models.JSONField(default=dict, blank=True)
    gstin = models.CharField(max_length=20, blank=True, default="")
    phone = models.CharField(max_length=20, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    feature_flags_json = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("code",)
        verbose_name_plural = "branches"

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.code} - {self.name}"


class Department(BaseModel):
    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ("code",)

    def __str__(self) -> str:  # pragma: no cover
        return self.name


class Designation(BaseModel):
    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=100)
    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name="designations"
    )

    class Meta:
        ordering = ("code",)

    def __str__(self) -> str:  # pragma: no cover
        return self.name


# ---------------------------------------------------------------------------
# Catalog support masters (Products themselves land in M03)
# ---------------------------------------------------------------------------


class UnitOfMeasure(BaseModel):
    code = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=64)
    symbol = models.CharField(max_length=8, blank=True, default="")
    decimals = models.PositiveSmallIntegerField(default=0)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT, related_name="derived"
    )
    conversion_factor = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        default=Decimal("1.000000"),
        help_text="Multiplier to convert one of this unit into the parent unit.",
    )

    class Meta:
        ordering = ("code",)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.code} ({self.symbol})" if self.symbol else self.code


class HSNCode(BaseModel):
    code = models.CharField(max_length=12, unique=True)
    description = models.CharField(max_length=255, blank=True, default="")
    default_tax = models.ForeignKey(
        "master.Tax",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="default_for_hsn",
    )

    class Meta:
        ordering = ("code",)
        verbose_name = "HSN code"
        verbose_name_plural = "HSN codes"

    def __str__(self) -> str:  # pragma: no cover
        return self.code


class TaxComponentType(models.TextChoices):
    CGST = "CGST", "CGST"
    SGST = "SGST", "SGST"
    IGST = "IGST", "IGST"
    CESS = "CESS", "Cess"


class Tax(BaseModel):
    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=100)
    rate_total = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        help_text="Sum of component rates, denormalised for quick filters.",
    )
    components_json = models.JSONField(
        default=list,
        blank=True,
        help_text='List of {"type": "CGST|SGST|IGST|CESS", "rate": <decimal>} entries.',
    )
    hsn_codes = models.ManyToManyField(HSNCode, blank=True, related_name="taxes")

    class Meta:
        ordering = ("code",)
        verbose_name_plural = "taxes"

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.code} - {self.rate_total}%"

    def clean(self) -> None:
        if not isinstance(self.components_json, list):
            raise ValidationError({"components_json": "Must be a list of component dicts."})
        valid_types = {c.value for c in TaxComponentType}
        total = Decimal("0")
        for idx, comp in enumerate(self.components_json):
            if not isinstance(comp, dict):
                raise ValidationError({"components_json": f"Entry {idx} must be a dict."})
            ctype = comp.get("type")
            rate = comp.get("rate")
            if ctype not in valid_types:
                raise ValidationError(
                    {"components_json": f"Entry {idx} has invalid type {ctype!r}."}
                )
            try:
                rate_dec = Decimal(str(rate))
            except Exception as exc:
                raise ValidationError(
                    {"components_json": f"Entry {idx} rate is not numeric."}
                ) from exc
            total += rate_dec
        if total != Decimal(str(self.rate_total)):
            raise ValidationError(
                {
                    "rate_total": (
                        f"rate_total ({self.rate_total}) does not equal "
                        f"sum of components ({total})."
                    )
                }
            )


class PaymentModeType(models.TextChoices):
    CASH = "CASH", "Cash"
    UPI = "UPI", "UPI"
    CARD = "CARD", "Card"
    WALLET = "WALLET", "Wallet"
    COD = "COD", "Cash on Delivery"
    BANK = "BANK", "Bank Transfer"


class PaymentMode(BaseModel):
    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=16, choices=PaymentModeType.choices)
    is_online = models.BooleanField(default=False)
    branches = models.ManyToManyField(Branch, blank=True, related_name="payment_modes")
    config_json = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("code",)

    def __str__(self) -> str:  # pragma: no cover
        return self.name


class Category(BaseModel):
    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=120)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT, related_name="children"
    )
    image = models.ImageField(upload_to="masters/categories/", null=True, blank=True)
    seo_slug = models.SlugField(max_length=140, blank=True, default="")

    class Meta:
        ordering = ("code",)
        verbose_name_plural = "categories"

    def __str__(self) -> str:  # pragma: no cover
        return self.name


class Brand(BaseModel):
    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=120)
    logo = models.ImageField(upload_to="masters/brands/", null=True, blank=True)
    description = models.TextField(blank=True, default="")

    class Meta:
        ordering = ("code",)

    def __str__(self) -> str:  # pragma: no cover
        return self.name


class Warehouse(BaseModel):
    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=120)
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="warehouses")
    address_json = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("code",)

    def __str__(self) -> str:  # pragma: no cover
        return self.name


class Zone(BaseModel):
    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=120)
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="zones")
    pincodes = models.ManyToManyField(Pincode, blank=True, related_name="zones")
    pincode_ranges_json = models.JSONField(
        default=list,
        blank=True,
        help_text='List of {"from": "560001", "to": "560099"} ranges.',
    )

    class Meta:
        ordering = ("code",)

    def __str__(self) -> str:  # pragma: no cover
        return self.name


# Validators re-exported for serializer convenience.
__all__ = [
    "Branch",
    "BranchType",
    "Brand",
    "Category",
    "City",
    "Country",
    "Department",
    "Designation",
    "HSNCode",
    "PaymentMode",
    "PaymentModeType",
    "Pincode",
    "State",
    "Tax",
    "TaxComponentType",
    "UnitOfMeasure",
    "Warehouse",
    "Zone",
]
