"""M05 Inventory — wastage service (step 6).

DRAFT → POSTED. Always-negative ledger lines (ref_type=WASTAGE).
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from ..exceptions import InvalidDocumentState, UnknownReasonCode
from ..models import DocumentStatus, InventoryRefType, Wastage
from ..reason_codes import is_valid_reason_code
from . import ledger_service


@transaction.atomic
def post(wastage: Wastage, *, actor=None) -> Wastage:
    locked = Wastage.all_objects.select_for_update().get(pk=wastage.pk)
    if locked.status != DocumentStatus.DRAFT:
        raise InvalidDocumentState()
    if not is_valid_reason_code(locked.reason_code, "WASTAGE"):
        raise UnknownReasonCode()

    items: list[dict[str, Any]] = []
    for it in locked.items.all():
        qty = Decimal(str(it.qty))
        if qty == 0:
            continue
        line: dict[str, Any] = {"qty_change": -qty}
        if it.product_id is not None:
            line["product_id"] = it.product_id
        else:
            line["variant_id"] = it.variant_id
        if it.batch_id is not None:
            line["batch"] = it.batch
        items.append(line)

    if items:
        ledger_service.post(
            ref_type=InventoryRefType.WASTAGE,
            ref_id=locked.pk,
            items=items,
            branch=locked.branch_id,
            actor=actor,
            reason_code=locked.reason_code,
            remarks=f"WASTAGE {locked.wastage_no} posted",
        )

    locked.status = DocumentStatus.POSTED
    locked.posted_at = timezone.now()
    locked.save(update_fields=["status", "posted_at", "updated_at"])
    return locked


__all__ = ["post"]
