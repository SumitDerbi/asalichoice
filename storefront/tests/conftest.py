"""Pytest fixtures and Django configuration for the storefront test suite.

Ensures the storefront project root (``backend`` sibling) is importable so
that ``apps.*`` and ``config.*`` resolve regardless of where pytest is run
from.
"""

from __future__ import annotations

import sys
from pathlib import Path

# storefront/  (BASE_DIR) — the parent of `tests/`.
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
