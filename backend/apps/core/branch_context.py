"""
Branch context resolver.

Re-exports the branch-scoped helpers from :mod:`apps.core.context` under
the dotted path called out by plan 005 (``apps.core.branch_context``).
Module-specific querysets can call :func:`current_branch_id` to scope
reads/writes to the active branch without threading the value through
every signature.

The actual ``Branch`` model is defined in M02; until then ``branch_id``
is just an integer.
"""

from __future__ import annotations

from .context import current_branch_id, reset_current_branch, set_current_branch

__all__ = [
    "current_branch_id",
    "reset_current_branch",
    "set_current_branch",
]
