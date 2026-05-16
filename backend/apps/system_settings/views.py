"""Admin-only API for system-settings resources.

All endpoints require Super Admin; the secret values on
:class:`IntegrationKey` are masked by default and an explicit
``GET <pk>/reveal/`` action (audit-logged) returns the plaintext.
"""

from __future__ import annotations

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.api.permissions import IsSuperAdmin
from apps.core.api.viewsets import BaseModelViewSet
from apps.core.audit import audit
from apps.core.audit.models import AuditAction

from .models import ContactInfo, FeatureToggle, IntegrationKey, SiteSetting, SocialLink
from .serializers import (
    ContactInfoSerializer,
    FeatureToggleSerializer,
    IntegrationKeySerializer,
    SiteSettingSerializer,
    SocialLinkSerializer,
)


class _SuperAdminBaseViewSet(BaseModelViewSet):
    """Common config: super-admin only, no per-permission gating yet."""

    permission_classes = (IsAuthenticated, IsSuperAdmin)
    required_perms: tuple[str, ...] = ()


class SiteSettingViewSet(_SuperAdminBaseViewSet):
    queryset = SiteSetting.objects.all()
    serializer_class = SiteSettingSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        # Reveal secrets only on the explicit detail-with-?reveal=1 query
        # — list responses always mask.
        if self.action == "retrieve" and self.request.query_params.get("reveal") in (
            "1",
            "true",
            "yes",
        ):
            ctx["reveal_secret"] = True
            instance = self.get_object()
            if instance.is_secret:
                audit(
                    instance=instance, action=AuditAction.OTHER, before=None, after={"reveal": True}
                )
        return ctx


class FeatureToggleViewSet(_SuperAdminBaseViewSet):
    queryset = FeatureToggle.objects.all()
    serializer_class = FeatureToggleSerializer


class IntegrationKeyViewSet(_SuperAdminBaseViewSet):
    queryset = IntegrationKey.objects.all()
    serializer_class = IntegrationKeySerializer

    @action(detail=True, methods=["get"], url_path="reveal")
    def reveal(self, request, pk=None):
        instance = self.get_object()
        audit(
            instance=instance,
            action=AuditAction.OTHER,
            before=None,
            after={"reveal": True},
        )
        serializer = self.get_serializer(
            instance,
            context={
                **self.get_serializer_context(),
                "reveal_secret": True,
            },
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class SocialLinkViewSet(_SuperAdminBaseViewSet):
    queryset = SocialLink.objects.all()
    serializer_class = SocialLinkSerializer


class ContactInfoViewSet(_SuperAdminBaseViewSet):
    queryset = ContactInfo.objects.all()
    serializer_class = ContactInfoSerializer
