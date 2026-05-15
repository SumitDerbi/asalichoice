"""
Request and branch context primitives.

Both the audit middleware and the branch resolver need to surface
per-request values (actor, IP, user-agent, current branch) to deeper
layers — services, model save hooks, etc. — that don't have access to
the HTTP request object.

We use :mod:`contextvars` rather than thread-locals so the context is
correct under ASGI / async views as well as classic WSGI requests.

Public API:
    request_context()      -> RequestContext | None
    set_request_context()  -> token   (use with reset)
    reset_request_context(token)
    current_actor()        -> User | None
    current_branch_id()    -> int | None
    set_current_branch(branch_id) -> token
    reset_current_branch(token)
"""

from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from django.contrib.auth.models import AbstractBaseUser


@dataclass(frozen=True)
class RequestContext:
    """Snapshot of per-request data needed by the service layer."""

    actor: Any | None = None  # AUTH_USER_MODEL instance or None
    ip: str | None = None
    user_agent: str | None = None
    branch_id: int | None = None


_request_ctx: ContextVar[RequestContext | None] = ContextVar(
    "asalichoice_request_ctx",
    default=None,
)
_branch_ctx: ContextVar[int | None] = ContextVar(
    "asalichoice_branch_ctx",
    default=None,
)


# ---------------------------------------------------------------------------
# Request context
# ---------------------------------------------------------------------------
def request_context() -> RequestContext | None:
    """Return the currently-active :class:`RequestContext`, if any."""

    return _request_ctx.get()


def set_request_context(ctx: RequestContext) -> Token:
    """Bind ``ctx`` as the active request context. Returns a reset token."""

    return _request_ctx.set(ctx)


def reset_request_context(token: Token) -> None:
    """Reset the request context using the token from :func:`set_request_context`."""

    _request_ctx.reset(token)


def current_actor() -> AbstractBaseUser | None:
    """Return the actor (authenticated user) bound to the current request, if any."""

    ctx = _request_ctx.get()
    return ctx.actor if ctx is not None else None


# ---------------------------------------------------------------------------
# Branch context
#
# Branch scoping is set independently of the request context because some
# call sites (Celery tasks, management commands) need to set a branch
# without a full request. The request middleware will also push the branch
# into ``_branch_ctx`` for convenience.
# ---------------------------------------------------------------------------
def current_branch_id() -> int | None:
    """Return the branch id bound to the current execution context, if any."""

    # Prefer an explicit branch override; fall back to the request context's
    # branch_id so callers that only set the request context still get a value.
    explicit = _branch_ctx.get()
    if explicit is not None:
        return explicit
    ctx = _request_ctx.get()
    return ctx.branch_id if ctx is not None else None


def set_current_branch(branch_id: int | None) -> Token:
    """Bind ``branch_id`` as the active branch. Returns a reset token."""

    return _branch_ctx.set(branch_id)


def reset_current_branch(token: Token) -> None:
    """Reset the branch context using the token from :func:`set_current_branch`."""

    _branch_ctx.reset(token)
