"""M01/03 integration tests: middleware, public API, signals, health."""

from __future__ import annotations

from decimal import Decimal

import pytest

from apps.core.context import current_branch_id
from apps.master import api_public
from apps.master.models import Branch, BranchType, PaymentMode, PaymentModeType, Tax
from apps.master.signals import CACHE_VERSION_KEY
from apps.system_settings.models import SettingScope, SiteSetting
from apps.system_settings.services import get_setting, invalidate_setting_cache

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _branch(code: str = "HQ", **overrides) -> Branch:
    defaults = {"name": f"{code} branch", "type": BranchType.HQ}
    defaults.update(overrides)
    return Branch.objects.create(code=code, **defaults)


def _gst18() -> Tax:
    return Tax.objects.create(
        code="GST18",
        name="GST 18%",
        rate_total=Decimal("18"),
        components_json=[
            {"type": "CGST", "rate": "9"},
            {"type": "SGST", "rate": "9"},
        ],
    )


def _super(user_factory):
    return user_factory(is_staff=True, is_superuser=True)


# ---------------------------------------------------------------------------
# BranchContextMiddleware
# ---------------------------------------------------------------------------


def test_middleware_binds_branch_from_header(api_client, user_factory):
    branch = _branch("HQ-MW")
    client = api_client(_super(user_factory))
    resp = client.get("/api/v1/health/", **{"HTTP_X_BRANCH_ID": str(branch.pk)})
    assert resp.status_code == 200
    # current_branch_id() should now be None — middleware resets after response.
    assert current_branch_id() is None


def test_middleware_invalid_header_returns_403_envelope(api_client, user_factory):
    client = api_client(_super(user_factory))
    resp = client.get("/api/v1/health/", **{"HTTP_X_BRANCH_ID": "not-an-int"})
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "MST-002"


def test_middleware_unknown_branch_returns_403_envelope(api_client, user_factory):
    client = api_client(_super(user_factory))
    resp = client.get("/api/v1/health/", **{"HTTP_X_BRANCH_ID": "99999"})
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "MST-002"


def test_middleware_inactive_branch_returns_403(api_client, user_factory):
    branch = _branch("HQ-INACT", is_active=False)
    client = api_client(_super(user_factory))
    resp = client.get("/api/v1/health/", **{"HTTP_X_BRANCH_ID": str(branch.pk)})
    assert resp.status_code == 403


def test_middleware_missing_header_falls_back_to_default_setting(api_client, user_factory):
    branch = _branch("HQ-DEFAULT")
    SiteSetting.objects.create(
        key="default.branch_id",
        scope=SettingScope.GLOBAL,
        value_json=branch.pk,
    )
    invalidate_setting_cache("default.branch_id")
    client = api_client(_super(user_factory))
    resp = client.get("/api/v1/health/")
    assert resp.status_code == 200


def test_middleware_anonymous_passes_through_without_header(api_client):
    resp = api_client().get("/api/v1/health/")
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# api_public
# ---------------------------------------------------------------------------


def test_get_tax_by_code_returns_tax():
    tax = _gst18()
    assert api_public.get_tax_by_code("GST18").pk == tax.pk
    assert api_public.get_tax_by_code("NOPE") is None


def test_compute_tax_matches_service():
    tax = _gst18()
    result = api_public.compute_tax(Decimal("100.00"), tax.pk, inclusive=False)
    assert result["grand_total"] == Decimal("118.00")


def test_is_payment_mode_enabled_reflects_m2m():
    branch = _branch("PM-BR")
    mode = PaymentMode.objects.create(
        code="CASH",
        name="Cash",
        type=PaymentModeType.CASH,
    )
    assert api_public.is_payment_mode_enabled(branch, "CASH") is False
    mode.branches.add(branch)
    assert api_public.is_payment_mode_enabled(branch, "CASH") is True
    assert api_public.is_payment_mode_enabled(branch.pk, "CASH") is True


def test_get_current_branch_uses_contextvar(push_request_context):
    branch = _branch("CTX-BR")
    with push_request_context(branch_id=branch.pk):
        assert api_public.get_current_branch().pk == branch.pk


# ---------------------------------------------------------------------------
# Signals — cache version bump
# ---------------------------------------------------------------------------


def test_saving_tax_bumps_cache_version():
    invalidate_setting_cache(CACHE_VERSION_KEY)
    before = get_setting(CACHE_VERSION_KEY, default=0)
    _gst18()
    invalidate_setting_cache(CACHE_VERSION_KEY)
    after = get_setting(CACHE_VERSION_KEY, default=0)
    assert int(after or 0) > int(before or 0)


def test_saving_branch_bumps_cache_version():
    invalidate_setting_cache(CACHE_VERSION_KEY)
    before = get_setting(CACHE_VERSION_KEY, default=0)
    _branch("BUMP-BR")
    invalidate_setting_cache(CACHE_VERSION_KEY)
    after = get_setting(CACHE_VERSION_KEY, default=0)
    assert int(after or 0) > int(before or 0)


# ---------------------------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------------------------


def test_health_reports_master_counts(api_client):
    _branch("HEALTH-BR")
    _gst18()
    resp = api_client().get("/api/v1/health/")
    assert resp.status_code == 200
    body = resp.json()
    assert "masters" in body
    assert body["masters"]["branches"] >= 1
    assert body["masters"]["taxes"] >= 1
