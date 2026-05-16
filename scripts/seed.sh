#!/usr/bin/env bash
# Run every phase-0 seeder via the Django orchestrator command.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR/backend"
python manage.py seed_all "$@"
