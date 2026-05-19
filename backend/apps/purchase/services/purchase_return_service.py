"""Purchase Return service.

A return is always anchored to an approved GRN. Posting reverses the
inventory stub and writes a debit (negative) vendor-ledger entry.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable
from decimal import Decimal
from typing import Any

from django.db import transaction

from ..exceptions import GRNInvalidTransition, ReturnQtyExceedsReceipt
from ..models import GRNStatus, PRStatus, PurchaseReturn, VendorLedger
from .grn_service import _vendor_balance

logger = logging.getLogger(__name__)


def _items_total(items: Iterable[dict[str, Any]]) -> Decimal:
    total = Decimal("0")
    for item in items:
        qty = Decimal(str(item.get("qty", "0")))
        cost = Decimal(str(item.get("cost_price", "0")))
        total += qty * cost
    return total


@transaction.atomic
def create_return(
    *,
    grn,
    pr_no: str,
    items: list[dict[str, Any]],
    reason: str = "",
    **fields,
) -> PurchaseReturn:
    if grn.status != GRNStatus.APPROVED:
        raise GRNInvalidTransition()
    # Map GRN item -> received qty.
    received_by_target: dict[tuple[int | None, int | None], Decimal] = {}
    for grn_item in grn.items.all():
        key = (grn_item.product_id, grn_item.variant_id)
        received_by_target[key] = received_by_target.get(key, Decimal("0")) + Decimal(
            str(grn_item.qty_received)
        )
    for item in items:
        key = (
            item.get("product_id") or item.get("product"),
            item.get("variant_id") or item.get("variant"),
        )
        qty = Decimal(str(item.get("qty", "0")))
        # Normalise key for FK-instance inputs.
        norm = (
            getattr(key[0], "pk", key[0]) if key[0] is not None else None,
            getattr(key[1], "pk", key[1]) if key[1] is not None else None,
        )
        if qty > received_by_target.get(norm, Decimal("0")):
            raise ReturnQtyExceedsReceipt()
    pr = PurchaseReturn.objects.create(
        pr_no=pr_no,
        grn=grn,
        vendor=grn.vendor,
        branch=grn.branch,
        reason=reason,
        items_json=items,
        totals_json={"grand_total": str(_items_total(items))},
        status=PRStatus.DRAFT,
        **fields,
    )
    return pr


@transaction.atomic
def post_return(pr: PurchaseReturn) -> PurchaseReturn:
    if pr.status != PRStatus.DRAFT:
        return pr
    pr.status = PRStatus.POSTED
    pr.save(update_fields=["status", "updated_at"])

    # Inventory reversal via M05 ledger service: one negative line per
    # return item against the matching batch (if the GRN carried one).
    from apps.inventory.models import InventoryRefType
    from apps.inventory.services import ledger_service

    grn_items_by_target: dict[tuple[int | None, int | None], Any] = {}
    for grn_item in pr.grn.items.all():
        grn_items_by_target.setdefault((grn_item.product_id, grn_item.variant_id), grn_item)

    ledger_items: list[dict[str, Any]] = []
    for raw in pr.items_json or []:
        product = raw.get("product_id") or raw.get("product")
        variant = raw.get("variant_id") or raw.get("variant")
        product_id = getattr(product, "pk", product) if product is not None else None
        variant_id = getattr(variant, "pk", variant) if variant is not None else None
        qty = Decimal(str(raw.get("qty", "0")))
        if qty <= 0:
            continue
        payload: dict[str, Any] = {
            "product_id": product_id,
            "variant_id": variant_id,
            "qty_change": -qty,
        }
        source = grn_items_by_target.get((product_id, variant_id))
        if source is not None and source.batch_no:
            payload["batch_kwargs"] = {"batch_no": source.batch_no}
        ledger_items.append(payload)

    if ledger_items:
        ledger_service.post(
            ref_type=InventoryRefType.RETURN,
            ref_id=pr.pk,
            items=ledger_items,
            branch=pr.branch,
            remarks=f"PR {pr.pr_no} posted",
        )

    grand = Decimal(str((pr.totals_json or {}).get("grand_total", "0")))
    if grand > 0:
        before = _vendor_balance(pr.vendor_id, pr.branch_id)
        VendorLedger.objects.create(
            vendor_id=pr.vendor_id,
            branch_id=pr.branch_id,
            amount=-grand,
            balance_before=before,
            balance_after=before - grand,
            reference_type="purchase.PurchaseReturn",
            reference_id=str(pr.pk),
            remarks=f"PR {pr.pr_no} posted",
        )
    return pr


__all__ = ["create_return", "post_return"]
