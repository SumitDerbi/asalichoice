"""Django admin registration for M01 master models."""

from __future__ import annotations

from django.contrib import admin

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

for model in (
    Country,
    State,
    City,
    Pincode,
    Branch,
    Department,
    Designation,
    UnitOfMeasure,
    HSNCode,
    Tax,
    PaymentMode,
    Category,
    Brand,
    Warehouse,
    Zone,
):
    admin.site.register(model)
