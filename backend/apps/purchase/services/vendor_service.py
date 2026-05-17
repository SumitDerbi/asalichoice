"""Vendor master CRUD service."""

from __future__ import annotations

import re
from typing import Any

from django.db import IntegrityError, transaction

from ..exceptions import VendorCodeDuplicate, VendorGSTINInvalid, VendorInactive
from ..models import Vendor

# GSTIN regex per Indian tax law: 2 digit state + 10 PAN + 1 entity + Z + 1 check.
_GSTIN_RE = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[0-9A-Z]{1}Z[0-9A-Z]{1}$")


def _validate_gstin(value: str | None) -> None:
    if not value:
        return
    if not _GSTIN_RE.match(value):
        raise VendorGSTINInvalid()


@transaction.atomic
def create_vendor(**fields: Any) -> Vendor:
    _validate_gstin(fields.get("gstin"))
    try:
        return Vendor.objects.create(**fields)
    except IntegrityError as exc:
        msg = str(exc).lower()
        if "code" in msg:
            raise VendorCodeDuplicate() from exc
        raise


@transaction.atomic
def update_vendor(vendor: Vendor, **fields: Any) -> Vendor:
    if "gstin" in fields:
        _validate_gstin(fields["gstin"])
    for key, value in fields.items():
        setattr(vendor, key, value)
    vendor.save()
    return vendor


@transaction.atomic
def deactivate_vendor(vendor: Vendor) -> Vendor:
    vendor.is_active = False
    vendor.save(update_fields=["is_active", "updated_at"])
    return vendor


def ensure_active(vendor: Vendor) -> None:
    if not vendor.is_active:
        raise VendorInactive()


__all__ = ["create_vendor", "deactivate_vendor", "ensure_active", "update_vendor"]
