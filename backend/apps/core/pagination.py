"""Backwards-compatible re-exports.

The canonical home for pagination classes is :mod:`apps.core.api.pagination`
(added in plan 008). Keep this module for legacy imports and the
``REST_FRAMEWORK`` settings string — both resolve to the same classes.
"""

from __future__ import annotations

import importlib

_mod = importlib.import_module("apps.core.api.pagination")
DefaultPageNumberPagination = _mod.DefaultPageNumberPagination
LedgerCursorPagination = _mod.LedgerCursorPagination
del importlib, _mod

__all__ = ["DefaultPageNumberPagination", "LedgerCursorPagination"]
