"""DRF viewsets + actions for M11 Sales."""

from __future__ import annotations

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.api.exceptions import DomainError
from apps.core.api.viewsets import BaseModelViewSet

from .models import Discount, Sale
from .serializers import (
    DiscountSerializer,
    SaleCreateSerializer,
    SalePaymentSerializer,
    SaleSerializer,
)
from .services import sale_service


def _envelope(exc: DomainError) -> Response:
    return Response(exc.to_envelope(), status=exc.status)


class SaleViewSet(BaseModelViewSet):
    queryset = (
        Sale.objects.select_related("branch", "customer", "cashier")
        .prefetch_related("items", "payments")
        .all()
    )
    serializer_class = SaleSerializer
    required_perms = ("sales.view",)
    required_perms_write = ("sales.manage",)
    http_method_names = ("get", "post", "patch", "head", "options")

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        if params.get("branch"):
            qs = qs.filter(branch_id=params["branch"])
        if params.get("origin"):
            qs = qs.filter(origin=params["origin"])
        if params.get("status"):
            qs = qs.filter(status=params["status"])
        if params.get("cashier"):
            qs = qs.filter(cashier_id=params["cashier"])
        if params.get("customer"):
            qs = qs.filter(customer_id=params["customer"])
        return qs

    # -- create ---------------------------------------------------------
    def create(self, request, *args, **kwargs):
        serializer = SaleCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        auto_post = data.pop("auto_post", False)
        items = data.pop("items", [])
        payments = data.pop("payments", [])

        try:
            sale = sale_service.create_draft(
                items=items,
                payments=payments,
                actor=request.user if request.user.is_authenticated else None,
                **data,
            )
        except DomainError as exc:
            return _envelope(exc)

        if auto_post:
            try:
                sale_service.post(
                    sale,
                    actor=request.user if request.user.is_authenticated else None,
                )
            except DomainError as exc:
                return _envelope(exc)

        out = SaleSerializer(sale, context=self.get_serializer_context())
        return Response(out.data, status=status.HTTP_201_CREATED)

    # -- post -----------------------------------------------------------
    @action(detail=True, methods=["post"], url_path="post")
    def post_sale(self, request, pk=None):
        sale = self.get_object()
        try:
            sale_service.post(
                sale,
                actor=request.user if request.user.is_authenticated else None,
                allow_partial_payment=bool(request.data.get("allow_partial_payment", False)),
            )
        except DomainError as exc:
            return _envelope(exc)
        out = SaleSerializer(sale, context=self.get_serializer_context())
        return Response(out.data)

    # -- cancel ---------------------------------------------------------
    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        sale = self.get_object()
        if not request.user.has_perm("sales.cancel"):
            return Response(
                {
                    "error": {
                        "code": "API-403",
                        "message": "sales.cancel permission required.",
                        "details": {},
                    }
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            sale_service.cancel(
                sale,
                actor=request.user if request.user.is_authenticated else None,
                reason=request.data.get("reason", ""),
            )
        except DomainError as exc:
            return _envelope(exc)
        out = SaleSerializer(sale, context=self.get_serializer_context())
        return Response(out.data)

    # -- add payment ---------------------------------------------------
    @action(detail=True, methods=["post"], url_path="payments")
    def add_payment(self, request, pk=None):
        sale = self.get_object()
        payload = dict(request.data)
        try:
            payment_mode_id = int(payload.get("payment_mode"))
        except (TypeError, ValueError):
            return Response(
                {
                    "error": {
                        "code": "API-400",
                        "message": "payment_mode is required.",
                        "details": {},
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        from apps.master.models import PaymentMode

        try:
            mode = PaymentMode.objects.get(pk=payment_mode_id)
        except PaymentMode.DoesNotExist:
            return Response(
                {
                    "error": {
                        "code": "API-400",
                        "message": "Unknown payment_mode.",
                        "details": {"payment_mode": payment_mode_id},
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            payment = sale_service._add_payment(
                sale=sale,
                raw={
                    "payment_mode": mode,
                    "amount": payload.get("amount"),
                    "ref_no": payload.get("ref_no", ""),
                    "gateway_txn": payload.get("gateway_txn", ""),
                    "status": payload.get("status", "SUCCESS"),
                },
            )
        except DomainError as exc:
            return _envelope(exc)
        return Response(SalePaymentSerializer(payment).data, status=status.HTTP_201_CREATED)


class DiscountViewSet(BaseModelViewSet):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    required_perms = ("sales.view",)
    required_perms_write = ("sales.manage",)


__all__ = ["DiscountViewSet", "SaleViewSet"]
