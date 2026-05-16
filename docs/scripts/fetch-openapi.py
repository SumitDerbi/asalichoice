"""Fetch the live OpenAPI schema from a running AsliChoice backend.

Saves the JSON to ``docs/api/openapi.json`` so the docs site can render it via
``swagger-ui-tag``. Safe to run in CI before ``mkdocs build``.

Usage::

    python docs/scripts/fetch-openapi.py
    python docs/scripts/fetch-openapi.py --url http://localhost:8000/api/v1/schema/

If the backend is not reachable the script exits 0 (leaves the existing
placeholder in place) so docs builds never block on a missing dev server.
Use ``--strict`` to make a failure exit non-zero.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_URL = "http://localhost:8000/api/v1/schema/?format=json"
OUTPUT = Path(__file__).resolve().parent.parent / "api" / "openapi.json"


def fetch(url: str, *, timeout: float = 5.0) -> dict:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})  # noqa: S310
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL, help="Schema URL")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero on fetch failure (default: keep placeholder, exit 0).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT,
        help="Where to write the schema JSON.",
    )
    args = parser.parse_args()

    try:
        schema = fetch(args.url)
    except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
        msg = f"[fetch-openapi] could not reach {args.url}: {exc}"
        print(msg, file=sys.stderr)
        if args.strict:
            return 1
        print("[fetch-openapi] keeping existing placeholder", file=sys.stderr)
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(schema, indent=2), encoding="utf-8")
    print(f"[fetch-openapi] wrote {args.output} ({args.output.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
