"""Branch context middleware.

Resolves the ``X-Branch-Id`` request header into a real
:class:`~apps.master.models.Branch` and binds the id to
:func:`apps.core.context.set_current_branch` so services and querysets
can scope their work to the active branch without threading the value
through every signature.

Fallback rules (plan 03-integration §1):

* If the header is missing and the caller is authenticated, fall back to
  ``settings.default_branch_id`` (system_settings SiteSetting).  In M02
  this becomes the user's primary branch.
* Unauthenticated requests get no branch — public endpoints handle their
  own scoping.
* If the header points at a branch the user can't access we abort with
  ``MST-002 branch_access_denied`` (403).

Note: M02 introduces the real user→branch ACL.  Until then the only
enforcement is "branch must exist and be active"; superusers / staff
pass through unconditionally.
"""

from __future__ import annotations

from collections.abc import Callable

from django.http import HttpRequest, HttpResponse, JsonResponse

from apps.core.context import reset_current_branch, set_current_branch

from .exceptions import BranchAccessDenied
from .models import Branch

HEADER = "HTTP_X_BRANCH_ID"


def _resolve_default_branch_id() -> int | None:
    """Return the configured default branch id, or ``None`` when unset."""

    # Local import keeps the master app importable without system_settings
    # ready (e.g. during the first ``manage.py check`` of a fresh checkout).
    try:
        from apps.system_settings.services import get_setting
    except Exception:  # pragma: no cover - defensive
        return None
    value = get_setting("default.branch_id", default=None)
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _user_can_access(user, branch: Branch) -> bool:
    """User → branch ACL stub.

    The real ACL (``user.branches`` M2M / role scoping) lands in M02.
    For now we accept any caller for any active branch — the middleware
    only guards "branch exists and is active".  Authenticated callers
    do NOT get extra rights here; the check is deliberately permissive
    so that M01/03 can ship without the M02 user model.
    """

    return True


class BranchContextMiddleware:
    """Bind the active branch id to the contextvar for downstream code."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        branch_id = self._resolve(request)
        if isinstance(branch_id, HttpResponse):
            return branch_id  # error response (e.g. 403 envelope)
        token = set_current_branch(branch_id)
        try:
            return self.get_response(request)
        finally:
            reset_current_branch(token)

    def _resolve(self, request: HttpRequest) -> int | None | HttpResponse:
        header = request.META.get(HEADER, "").strip()
        user = getattr(request, "user", None)

        if not header:
            # No header: fall back to the configured default branch.  Note
            # ``request.user`` is still anonymous here because DRF auth
            # hasn't run yet — we deliberately don't gate the fallback on
            # auth state (M02 will revisit).
            return _resolve_default_branch_id()

        try:
            branch_id = int(header)
        except (TypeError, ValueError):
            return self._deny("Invalid X-Branch-Id header.")

        branch = Branch.objects.filter(pk=branch_id, is_active=True).first()
        if branch is None:
            return self._deny("Branch not found or inactive.")

        if not _user_can_access(user, branch):
            return self._deny("You cannot access this branch.")
        return branch.pk

    @staticmethod
    def _deny(message: str) -> HttpResponse:
        err = BranchAccessDenied(message)
        return JsonResponse(err.to_envelope(), status=err.status)
