"""Chunked CSV import for products with row-level error reporting.

The endpoint accepts a CSV with header row. Expected columns:

    code, sku, name, slug, category_code, brand_code, hsn_code,
    tax_code, base_uom_code, status, description

``dry_run=True`` validates each row without persisting. The return
shape is::

    {
        "total": 1000,
        "created": 995,
        "errors": [{"row": 12, "error": "...", "data": {...}}],
        "committed": True,
    }

Designed for 10k+ rows: rows are processed in chunks of 500 inside a
single transaction (commit mode) so a late failure rolls everything
back.
"""

from __future__ import annotations

import csv
import io
from typing import IO, Any

from django.db import transaction

from apps.master.models import Brand, Category, HSNCode, Tax, UnitOfMeasure

from ..models import Product, ProductStatus

_REQUIRED = ("code", "sku", "name", "slug", "category_code", "base_uom_code")
_CHUNK = 500


def _load_master_index() -> dict[str, dict[str, int]]:
    return {
        "category": {c.code: c.pk for c in Category.all_objects.all()},
        "brand": {b.code: b.pk for b in Brand.all_objects.all()},
        "hsn": {h.code: h.pk for h in HSNCode.all_objects.all()},
        "tax": {t.code: t.pk for t in Tax.all_objects.all()},
        "uom": {u.code: u.pk for u in UnitOfMeasure.all_objects.all()},
    }


def _validate_row(
    row: dict[str, str], index: dict[str, dict[str, int]]
) -> tuple[dict[str, Any] | None, str | None]:
    for key in _REQUIRED:
        if not row.get(key):
            return None, f"Missing required column: {key}"

    category_id = index["category"].get(row["category_code"])
    if category_id is None:
        return None, f"Unknown category_code: {row['category_code']}"

    uom_id = index["uom"].get(row["base_uom_code"])
    if uom_id is None:
        return None, f"Unknown base_uom_code: {row['base_uom_code']}"

    payload: dict[str, Any] = {
        "code": row["code"].strip(),
        "sku": row["sku"].strip(),
        "name": row["name"].strip(),
        "slug": row["slug"].strip(),
        "category_id": category_id,
        "base_uom_id": uom_id,
        "description": row.get("description", "").strip(),
        "status": row.get("status", "").strip() or ProductStatus.DRAFT,
    }
    if row.get("brand_code"):
        brand_id = index["brand"].get(row["brand_code"])
        if brand_id is None:
            return None, f"Unknown brand_code: {row['brand_code']}"
        payload["brand_id"] = brand_id
    if row.get("hsn_code"):
        hsn_id = index["hsn"].get(row["hsn_code"])
        if hsn_id is None:
            return None, f"Unknown hsn_code: {row['hsn_code']}"
        payload["hsn_id"] = hsn_id
    if row.get("tax_code"):
        tax_id = index["tax"].get(row["tax_code"])
        if tax_id is None:
            return None, f"Unknown tax_code: {row['tax_code']}"
        payload["tax_id"] = tax_id

    if payload["status"] not in ProductStatus.values:
        return None, f"Invalid status: {payload['status']}"
    return payload, None


def import_products_csv(
    source: IO[bytes] | IO[str] | bytes | str,
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Parse + validate + (optionally) persist a product CSV."""

    if isinstance(source, bytes):
        text = source.decode("utf-8-sig")
    elif isinstance(source, str):
        text = source
    else:
        raw = source.read()
        text = raw.decode("utf-8-sig") if isinstance(raw, bytes) else raw

    reader = csv.DictReader(io.StringIO(text))
    index = _load_master_index()

    valid_rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    total = 0
    for line_no, row in enumerate(reader, start=2):  # header is line 1
        total += 1
        payload, err = _validate_row(row, index)
        if err:
            errors.append({"row": line_no, "error": err, "data": row})
            continue
        valid_rows.append(payload)

    if dry_run:
        return {
            "total": total,
            "created": 0,
            "valid": len(valid_rows),
            "errors": errors,
            "committed": False,
        }

    created = 0
    with transaction.atomic():
        for start in range(0, len(valid_rows), _CHUNK):
            batch = valid_rows[start : start + _CHUNK]
            Product.objects.bulk_create(
                [Product(**payload) for payload in batch],
                batch_size=_CHUNK,
            )
            created += len(batch)

    return {
        "total": total,
        "created": created,
        "valid": len(valid_rows),
        "errors": errors,
        "committed": True,
    }
