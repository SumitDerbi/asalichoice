# Run every phase-0 seeder via the Django orchestrator command.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Push-Location (Join-Path $root "backend")
try {
    python manage.py seed_all @args
} finally {
    Pop-Location
}
