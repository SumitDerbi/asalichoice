"""M05 Inventory — stock adjustment service (step 6).

DRAFT → POSTED. On post, translates each :class:`StockAdjustmentItem`
into a signed :class:`InventoryLedger` line via :func:`ledger_service.post`.
Reason code is validated against :mod:`apps.inventory.reason_codes`.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from ..exceptions import InvalidDocumentState, UnknownReasonCode
from ..models import DocumentStatus, InventoryRefType, StockAdjustment
from ..reason_codes import is_valid_reason_code
from . import ledger_service


@transaction.atomic
def post(adj: StockAdjustment, *, actor=None) -> StockAdjustment:
    locked = StockAdjustment.all_objects.select_for_update().get(pk=adj.pk)
    if locked.status != DocumentStatus.DRAFT:
        raise InvalidDocumentState()
    if not is_valid_reason_code(locked.reason_code, "ADJUSTMENT"):
        raise UnknownReasonCode()

    items: list[dict[str, Any]] = []
    for it in locked.items.all():
        qty = Decimal(str(it.qty_change))
        if qty == 0:
            continue
        line: dict[str, Any] = {"qty_change": qty}
        if it.product_id is not None:
            line["product_id"] = it.product_id
        else:
            line["variant_id"] = it.variant_id
        if it.batch_id is not None:
            line["batch"] = it.batch
        items.append(line)

    if items:
        ledger_service.post(
            ref_type=InventoryRefType.ADJUSTMENT,
            ref_id=locked.pk,
            items=items,
            branch=locked.branch_id,
            actor=actor,
            reason_code=locked.reason_code,
            remarks=f"ADJ {locked.adj_no} posted",
        )

    locked.status = DocumentStatus.POSTED
    locked.posted_at = timezone.now()
    locked.save(update_fields=["status", "posted_at", "updated_at"])
    return locked


__all__ = ["post"]
