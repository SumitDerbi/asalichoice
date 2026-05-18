"""M04 Purchase — DRF viewsets and custom actions."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.api.exceptions import DomainError
from apps.core.api.viewsets import BaseModelViewSet

from .models import GRN, PurchaseInvoice, PurchaseOrder, PurchaseReturn, Vendor, VendorLedger
from .serializers import (
    GRNSerializer,
    PurchaseInvoiceSerializer,
    PurchaseOrderSerializer,
    PurchaseReturnSerializer,
    VendorLedgerSerializer,
    VendorSerializer,
)
from .services import (
    approve_grn,
    approve_po,
    cancel_po,
    create_grn,
    create_invoice_from_grns,
    create_po,
    create_return,
    deactivate_vendor,
    post_invoice,
    post_return,
    record_payment,
    reject_grn,
    submit_grn,
    submit_po,
    sync_offline_grn,
)

# ---------------------------------------------------------------------------
# Vendor
# ---------------------------------------------------------------------------


class VendorViewSet(BaseModelViewSet):
    queryset = Vendor.objects.prefetch_related("contacts", "bank_accounts", "branches").all()
    serializer_class = VendorSerializer
    required_perms = ("purchase.vendor.view",)

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        q = params.get("q")
        if q:
            qs = qs.filter(name__icontains=q) | qs.filter(code__icontains=q)
        return qs.distinct()

    @extend_schema(summary="Deactivate a vendor.")
    @action(detail=True, methods=["post"], url_path="deactivate")
    def deactivate(self, request, pk=None):
        vendor = self.get_object()
        deactivate_vendor(vendor)
        return Response(self.get_serializer(vendor).data)


# ---------------------------------------------------------------------------
# Purchase Order
# ---------------------------------------------------------------------------


def _envelope(exc: DomainError) -> Response:
    return Response(exc.to_envelope(), status=exc.status)


class PurchaseOrderViewSet(BaseModelViewSet):
    queryset = PurchaseOrder.objects.select_related("vendor", "branch").prefetch_related("items")
    serializer_class = PurchaseOrderSerializer
    required_perms = ("purchase.po.view",)

    def create(self, request, *args, **kwargs):
        data = request.data or {}
        items = data.get("items") or []
        try:
            vendor = Vendor.objects.get(pk=data["vendor"])
            from apps.master.models import Branch

            branch = Branch.objects.get(pk=data["branch"])
            po_no = data["po_no"]
        except (KeyError, Vendor.DoesNotExist):
            return Response(
                {"error": {"code": "API-400", "message": "vendor, branch and po_no are required."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Resolve product / variant / uom ids on incoming items.
        from apps.catalog.models import Product, ProductVariant
        from apps.master.models import UnitOfMeasure

        resolved_items: list[dict] = []
        for raw in items:
            row = dict(raw)
            if row.get("product") and not hasattr(row["product"], "pk"):
                row["product"] = Product.objects.filter(pk=row["product"]).first()
            if row.get("variant") and not hasattr(row["variant"], "pk"):
                row["variant"] = ProductVariant.objects.filter(pk=row["variant"]).first()
            if row.get("uom") and not hasattr(row["uom"], "pk"):
                row["uom"] = UnitOfMeasure.objects.filter(pk=row["uom"]).first()
            resolved_items.append(row)
        extras: dict = {}
        if data.get("expected_delivery"):
            extras["expected_delivery"] = data["expected_delivery"]
        if data.get("terms") is not None:
            extras["terms"] = data["terms"]
        try:
            po = create_po(
                vendor=vendor, branch=branch, po_no=po_no, items=resolved_items, **extras
            )
        except DomainError as exc:
            return _envelope(exc)
        return Response(self.get_serializer(po).data, status=status.HTTP_201_CREATED)

    @extend_schema(summary="Submit a draft PO for approval.")
    @action(detail=True, methods=["post"], url_path="submit")
    def submit(self, request, pk=None):
        po = self.get_object()
        try:
            submit_po(po)
        except DomainError as exc:
            return _envelope(exc)
        return Response(self.get_serializer(po).data)

    @extend_schema(summary="Approve a pending PO.")
    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        po = self.get_object()
        try:
            approve_po(po, actor=request.user)
        except DomainError as exc:
            return _envelope(exc)
        return Response(self.get_serializer(po).data)

    @extend_schema(summary="Cancel a PO that has not yet been received.")
    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        po = self.get_object()
        try:
            cancel_po(po)
        except DomainError as exc:
            return _envelope(exc)
        return Response(self.get_serializer(po).data)


# ---------------------------------------------------------------------------
# GRN
# ---------------------------------------------------------------------------


class GRNViewSet(BaseModelViewSet):
    queryset = GRN.objects.select_related("vendor", "branch", "po").prefetch_related("items")
    serializer_class = GRNSerializer
    required_perms = ("purchase.grn.view",)

    def create(self, request, *args, **kwargs):
        data = request.data or {}
        items = data.get("items") or []
        try:
            vendor = Vendor.objects.get(pk=data["vendor"])
            from apps.master.models import Branch

            branch = Branch.objects.get(pk=data["branch"])
            grn_no = data["grn_no"]
        except (KeyError, Vendor.DoesNotExist):
            return Response(
                {
                    "error": {
                        "code": "API-400",
                        "message": "vendor, branch and grn_no are required.",
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        po = None
        if data.get("po"):
            po = PurchaseOrder.objects.filter(pk=data["po"]).first()
        # Resolve product / variant / po_item / uom ids on incoming items.
        from apps.catalog.models import Product, ProductVariant

        from .models import POItem

        resolved_items: list[dict] = []
        for raw in items:
            row = dict(raw)
            if row.get("product") and not hasattr(row["product"], "pk"):
                row["product"] = Product.objects.filter(pk=row["product"]).first()
            if row.get("variant") and not hasattr(row["variant"], "pk"):
                row["variant"] = ProductVariant.objects.filter(pk=row["variant"]).first()
            if row.get("po_item") and not hasattr(row["po_item"], "pk"):
                row["po_item"] = POItem.objects.filter(pk=row["po_item"]).first()
            resolved_items.append(row)
        extras: dict = {}
        for k in ("received_at", "vehicle_no", "transporter"):
            if data.get(k) is not None:
                extras[k] = data[k]
        try:
            grn = create_grn(
                vendor=vendor, branch=branch, grn_no=grn_no, items=resolved_items, po=po, **extras
            )
        except DomainError as exc:
            return _envelope(exc)
        return Response(self.get_serializer(grn).data, status=status.HTTP_201_CREATED)

    @extend_schema(summary="Submit a GRN for approval.")
    @action(detail=True, methods=["post"], url_path="submit")
    def submit(self, request, pk=None):
        grn = self.get_object()
        try:
            submit_grn(grn)
        except DomainError as exc:
            return _envelope(exc)
        return Response(self.get_serializer(grn).data)

    @extend_schema(summary="Approve a GRN — writes stock + vendor ledger.")
    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        grn = self.get_object()
        try:
            approve_grn(grn, actor=request.user)
        except DomainError as exc:
            return _envelope(exc)
        return Response(self.get_serializer(grn).data)

    @extend_schema(summary="Reject a submitted GRN.")
    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        grn = self.get_object()
        try:
            reject_grn(grn, reason=request.data.get("reason", ""))
        except DomainError as exc:
            return _envelope(exc)
        return Response(self.get_serializer(grn).data)

    @extend_schema(
        summary="Idempotent offline GRN sync.",
        description=(
            "POST body: ``{offline_uuid, vendor, branch, grn_no, items: [...], po?}``. "
            "Re-sending the same ``offline_uuid`` returns the existing GRN."
        ),
    )
    @action(detail=False, methods=["post"], url_path="sync-offline")
    def sync_offline(self, request):
        body = request.data or {}
        try:
            offline_uuid = UUID(str(body["offline_uuid"]))
            vendor = Vendor.objects.get(pk=body["vendor"])
            branch_id = body["branch"]
            grn_no = body["grn_no"]
            items = body.get("items", [])
        except (KeyError, ValueError, Vendor.DoesNotExist):
            return Response(
                {
                    "error": {
                        "code": "API-400",
                        "message": "offline_uuid, vendor, branch, grn_no and items are required.",
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        po = None
        if body.get("po"):
            po = PurchaseOrder.objects.filter(pk=body["po"]).first()
        from apps.master.models import Branch

        branch = Branch.objects.filter(pk=branch_id).first()
        if branch is None:
            return Response(
                {"error": {"code": "API-400", "message": "Unknown branch."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Resolve product / variant / po_item / uom ids on incoming items.
        from apps.catalog.models import Product, ProductVariant

        from .models import POItem

        resolved_items: list[dict] = []
        for raw in items:
            row = dict(raw)
            if row.get("product") and not hasattr(row["product"], "pk"):
                row["product"] = Product.objects.filter(pk=row["product"]).first()
            if row.get("variant") and not hasattr(row["variant"], "pk"):
                row["variant"] = ProductVariant.objects.filter(pk=row["variant"]).first()
            if row.get("po_item") and not hasattr(row["po_item"], "pk"):
                row["po_item"] = POItem.objects.filter(pk=row["po_item"]).first()
            resolved_items.append(row)
        try:
            grn = sync_offline_grn(
                offline_uuid=offline_uuid,
                vendor=vendor,
                branch=branch,
                grn_no=grn_no,
                items=resolved_items,
                po=po,
            )
        except DomainError as exc:
            return _envelope(exc)
        return Response(self.get_serializer(grn).data, status=status.HTTP_201_CREATED)


# ---------------------------------------------------------------------------
# Purchase Invoice
# ---------------------------------------------------------------------------


class PurchaseInvoiceViewSet(BaseModelViewSet):
    queryset = PurchaseInvoice.objects.select_related("vendor", "branch").prefetch_related("grns")
    serializer_class = PurchaseInvoiceSerializer
    required_perms = ("purchase.invoice.view",)

    @extend_schema(summary="Create a draft PI from approved GRNs.")
    @action(detail=False, methods=["post"], url_path="from-grns")
    def from_grns(self, request):
        body = request.data or {}
        try:
            vendor = Vendor.objects.get(pk=body["vendor"])
            from apps.master.models import Branch

            branch = Branch.objects.get(pk=body["branch"])
            grn_ids = body.get("grn_ids") or []
            pi_no = body["pi_no"]
        except (KeyError, Vendor.DoesNotExist):
            return Response(
                {"error": {"code": "API-400", "message": "vendor, branch, pi_no required."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            pi = create_invoice_from_grns(
                vendor=vendor,
                branch=branch,
                pi_no=pi_no,
                grn_ids=grn_ids,
                invoice_no_vendor=body.get("invoice_no_vendor", ""),
                invoice_date=body.get("invoice_date"),
                due_date=body.get("due_date"),
                payment_terms=body.get("payment_terms", ""),
            )
        except DomainError as exc:
            return _envelope(exc)
        return Response(self.get_serializer(pi).data, status=status.HTTP_201_CREATED)

    @extend_schema(summary="Post a draft invoice.")
    @action(detail=True, methods=["post"], url_path="post")
    def post_action(self, request, pk=None):
        pi = self.get_object()
        post_invoice(pi)
        return Response(self.get_serializer(pi).data)

    @extend_schema(summary="Record a vendor payment against this invoice.")
    @action(detail=True, methods=["post"], url_path="pay")
    def pay(self, request, pk=None):
        pi = self.get_object()
        amount_raw = (request.data or {}).get("amount")
        try:
            amount = Decimal(str(amount_raw))
        except (ArithmeticError, TypeError, ValueError):
            return Response(
                {"error": {"code": "API-400", "message": "amount is required."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        record_payment(pi, amount=amount, remarks=(request.data or {}).get("remarks", ""))
        return Response(self.get_serializer(pi).data)


# ---------------------------------------------------------------------------
# Purchase Return
# ---------------------------------------------------------------------------


class PurchaseReturnViewSet(BaseModelViewSet):
    queryset = PurchaseReturn.objects.select_related("grn", "vendor", "branch")
    serializer_class = PurchaseReturnSerializer
    required_perms = ("purchase.return.view",)

    @extend_schema(summary="Create a draft purchase return from an approved GRN.")
    @action(detail=False, methods=["post"], url_path="create-from-grn")
    def create_from_grn(self, request):
        body = request.data or {}
        try:
            grn = GRN.objects.get(pk=body["grn"])
        except (KeyError, GRN.DoesNotExist):
            return Response(
                {"error": {"code": "API-400", "message": "grn id required."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            pr = create_return(
                grn=grn,
                pr_no=body["pr_no"],
                items=body.get("items", []),
                reason=body.get("reason", ""),
            )
        except DomainError as exc:
            return _envelope(exc)
        return Response(self.get_serializer(pr).data, status=status.HTTP_201_CREATED)

    @extend_schema(summary="Post a draft return — reverses stock + writes ledger debit.")
    @action(detail=True, methods=["post"], url_path="post")
    def post_action(self, request, pk=None):
        pr = self.get_object()
        post_return(pr)
        return Response(self.get_serializer(pr).data)


# ---------------------------------------------------------------------------
# Vendor Ledger (read-only)
# ---------------------------------------------------------------------------


class VendorLedgerViewSet(BaseModelViewSet):
    queryset = VendorLedger.objects.select_related("vendor").all()
    serializer_class = VendorLedgerSerializer
    required_perms = ("purchase.vendor.view",)
    http_method_names = ("get", "head", "options")

    def get_queryset(self):
        qs = super().get_queryset()
        vendor = self.request.query_params.get("vendor")
        branch = self.request.query_params.get("branch")
        if vendor:
            qs = qs.filter(vendor_id=vendor)
        if branch:
            qs = qs.filter(branch_id=branch)
        return qs
