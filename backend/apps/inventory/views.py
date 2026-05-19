"""DRF viewsets for M05 Inventory.

Read endpoints (Stock / Batch / InventoryLedger) are listed via
``ReadOnlyModelViewSet`` subclasses — the ledger is append-only and the
two snapshots are recomputed by ``ledger_service``. Write endpoints
(reservation, transfer, adjustment, wastage, count) gate per-action on
``inventory.*`` permission codes seeded by ``seed_permissions``.
"""

from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.api.exceptions import DomainError
from apps.core.api.filters import BaseSearchFilterBackend
from apps.core.api.pagination import DefaultPageNumberPagination
from apps.core.api.permissions import HasAnyPermission
from apps.core.api.viewsets import BaseModelViewSet

from .models import (
    Batch,
    BranchTransfer,
    InventoryLedger,
    PhysicalCount,
    Reservation,
    Stock,
    StockAdjustment,
    Wastage,
)
from .pagination import InventoryLedgerCursorPagination
from .serializers import (
    BatchSerializer,
    BranchTransferSerializer,
    InventoryLedgerSerializer,
    PhysicalCountSerializer,
    ReservationSerializer,
    StockAdjustmentSerializer,
    StockSerializer,
    WastageSerializer,
)
from .services import (
    adjustment_service,
    availability_service,
    count_service,
    transfer_service,
    wastage_service,
)


def _envelope(exc: DomainError) -> Response:
    return Response(exc.to_envelope(), status=exc.status)


class _ReadOnlyInventoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Shared base for Stock / Batch / Ledger — view-only, view perm."""

    permission_classes = (IsAuthenticated, HasAnyPermission)
    pagination_class = DefaultPageNumberPagination
    filter_backends = (BaseSearchFilterBackend,)
    required_perms = ("inventory.view",)


# ---------------------------------------------------------------------------
# Stock
# ---------------------------------------------------------------------------


class StockViewSet(_ReadOnlyInventoryViewSet):
    queryset = Stock.objects.select_related("product", "variant", "branch", "warehouse").all()
    serializer_class = StockSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        if params.get("branch"):
            qs = qs.filter(branch_id=params["branch"])
        if params.get("product"):
            qs = qs.filter(product_id=params["product"])
        if params.get("variant"):
            qs = qs.filter(variant_id=params["variant"])
        return qs


# ---------------------------------------------------------------------------
# Batches
# ---------------------------------------------------------------------------


class BatchViewSet(_ReadOnlyInventoryViewSet):
    queryset = Batch.objects.select_related("product", "variant", "branch").all()
    serializer_class = BatchSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        if params.get("branch"):
            qs = qs.filter(branch_id=params["branch"])
        if params.get("product"):
            qs = qs.filter(product_id=params["product"])
        if params.get("variant"):
            qs = qs.filter(variant_id=params["variant"])
        if params.get("status"):
            qs = qs.filter(status=params["status"])
        return qs


# ---------------------------------------------------------------------------
# Ledger — cursor-paginated, filterable
# ---------------------------------------------------------------------------


class InventoryLedgerViewSet(_ReadOnlyInventoryViewSet):
    queryset = InventoryLedger.objects.select_related(
        "product", "variant", "branch", "warehouse", "batch"
    ).all()
    serializer_class = InventoryLedgerSerializer
    pagination_class = InventoryLedgerCursorPagination
    # The ledger model is not a BaseModel — disable the is_active filter.
    filter_backends = ()

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        if params.get("branch"):
            qs = qs.filter(branch_id=params["branch"])
        if params.get("product"):
            qs = qs.filter(product_id=params["product"])
        if params.get("variant"):
            qs = qs.filter(variant_id=params["variant"])
        if params.get("ref_type"):
            qs = qs.filter(reference_type=params["ref_type"])
        if params.get("reason_code"):
            qs = qs.filter(reason_code=params["reason_code"])
        if params.get("actor"):
            qs = qs.filter(actor_id=params["actor"])
        if params.get("timestamp_from"):
            qs = qs.filter(timestamp__gte=params["timestamp_from"])
        if params.get("timestamp_to"):
            qs = qs.filter(timestamp__lt=params["timestamp_to"])
        return qs


# ---------------------------------------------------------------------------
# Reservations
# ---------------------------------------------------------------------------


class ReservationViewSet(BaseModelViewSet):
    queryset = Reservation.objects.select_related("product", "variant", "branch").all()
    serializer_class = ReservationSerializer
    required_perms = ("inventory.view",)
    required_perms_write = ("inventory.manage",)
    http_method_names = ("get", "post", "head", "options")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        item = data.get("product") or data.get("variant")
        try:
            reservation = availability_service.reserve(
                item=item,
                branch=data["branch"],
                qty=data["qty"],
                ref_type=data["ref_type"],
                ref_id=data["ref_id"],
                expires_at=data.get("expires_at"),
            )
        except DomainError as exc:
            return _envelope(exc)
        return Response(self.get_serializer(reservation).data, status=status.HTTP_201_CREATED)

    @extend_schema(summary="Release an active reservation.")
    @action(detail=True, methods=["post"], url_path="release")
    def release(self, request, pk=None):
        reservation = self.get_object()
        try:
            availability_service.release(reservation)
        except DomainError as exc:
            return _envelope(exc)
        return Response(self.get_serializer(reservation).data)

    @extend_schema(summary="Mark an active reservation as consumed.")
    @action(detail=True, methods=["post"], url_path="consume")
    def consume(self, request, pk=None):
        reservation = self.get_object()
        try:
            availability_service.consume(reservation)
        except DomainError as exc:
            return _envelope(exc)
        return Response(self.get_serializer(reservation).data)


# ---------------------------------------------------------------------------
# Branch transfers
# ---------------------------------------------------------------------------


class BranchTransferViewSet(BaseModelViewSet):
    queryset = BranchTransfer.objects.select_related("from_branch", "to_branch").prefetch_related(
        "items"
    )
    serializer_class = BranchTransferSerializer
    required_perms = ("inventory.view",)
    required_perms_write = ("inventory.transfer",)

    @extend_schema(summary="Dispatch a DRAFT transfer — posts negative ledger at source.")
    @action(detail=True, methods=["post"], url_path="dispatch")
    def dispatch_action(self, request, pk=None):
        transfer = self.get_object()
        try:
            transfer = transfer_service.dispatch(transfer, actor=request.user)
        except DomainError as exc:
            return _envelope(exc)
        return Response(self.get_serializer(transfer).data)

    @extend_schema(summary="Receive an IN_TRANSIT transfer — posts positive ledger at destination.")
    @action(detail=True, methods=["post"], url_path="receive")
    def receive(self, request, pk=None):
        transfer = self.get_object()
        try:
            transfer = transfer_service.receive(transfer, actor=request.user)
        except DomainError as exc:
            return _envelope(exc)
        return Response(self.get_serializer(transfer).data)

    @extend_schema(summary="Cancel a DRAFT transfer.")
    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        transfer = self.get_object()
        try:
            transfer = transfer_service.cancel(transfer)
        except DomainError as exc:
            return _envelope(exc)
        return Response(self.get_serializer(transfer).data)


# ---------------------------------------------------------------------------
# Stock adjustments
# ---------------------------------------------------------------------------


class StockAdjustmentViewSet(BaseModelViewSet):
    queryset = StockAdjustment.objects.select_related("branch").prefetch_related("items")
    serializer_class = StockAdjustmentSerializer
    required_perms = ("inventory.view",)
    required_perms_write = ("inventory.adjust",)

    @extend_schema(summary="Post a DRAFT stock adjustment — writes signed ledger.")
    @action(detail=True, methods=["post"], url_path="post")
    def post_action(self, request, pk=None):
        adj = self.get_object()
        try:
            adj.refresh_from_db()
            adjustment_service.post(adj, actor=request.user)
            adj.refresh_from_db()
        except DomainError as exc:
            return _envelope(exc)
        return Response(self.get_serializer(adj).data)


# ---------------------------------------------------------------------------
# Wastage
# ---------------------------------------------------------------------------


class WastageViewSet(BaseModelViewSet):
    queryset = Wastage.objects.select_related("branch").prefetch_related("items")
    serializer_class = WastageSerializer
    required_perms = ("inventory.view",)
    required_perms_write = ("inventory.wastage",)

    @extend_schema(summary="Post a DRAFT wastage — writes negative ledger.")
    @action(detail=True, methods=["post"], url_path="post")
    def post_action(self, request, pk=None):
        w = self.get_object()
        try:
            wastage_service.post(w, actor=request.user)
            w.refresh_from_db()
        except DomainError as exc:
            return _envelope(exc)
        return Response(self.get_serializer(w).data)


# ---------------------------------------------------------------------------
# Physical counts
# ---------------------------------------------------------------------------


class PhysicalCountViewSet(BaseModelViewSet):
    queryset = PhysicalCount.objects.select_related("branch").prefetch_related("items")
    serializer_class = PhysicalCountSerializer
    required_perms = ("inventory.view",)
    required_perms_write = ("inventory.count",)

    @extend_schema(summary="Snapshot expected qty from Stock — OPEN → COUNTED.")
    @action(detail=True, methods=["post"], url_path="mark-counted")
    def mark_counted(self, request, pk=None):
        count = self.get_object()
        try:
            count_service.mark_counted(count)
            count.refresh_from_db()
        except DomainError as exc:
            return _envelope(exc)
        return Response(self.get_serializer(count).data)

    @extend_schema(summary="Post a COUNTED physical count — writes diff ledger.")
    @action(detail=True, methods=["post"], url_path="post")
    def post_action(self, request, pk=None):
        count = self.get_object()
        try:
            count_service.post(count, actor=request.user)
            count.refresh_from_db()
        except DomainError as exc:
            return _envelope(exc)
        return Response(self.get_serializer(count).data)


__all__ = [
    "StockViewSet",
    "BatchViewSet",
    "InventoryLedgerViewSet",
    "ReservationViewSet",
    "BranchTransferViewSet",
    "StockAdjustmentViewSet",
    "WastageViewSet",
    "PhysicalCountViewSet",
]
