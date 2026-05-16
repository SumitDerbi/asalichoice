<#
.SYNOPSIS
  AsliChoice unified test runner for Windows / PowerShell.

.DESCRIPTION
  Order: ruff -> ruff format --check -> isort -> pytest+cov -> eslint -> vitest+cov -> postman -> playwright.

.PARAMETER NoE2E
  Skip Playwright.

.PARAMETER NoPostman
  Skip Newman.

.PARAMETER BackendOnly
  Only Python lints + pytest.

.PARAMETER FrontendOnly
  Only ESLint + Vitest.

.EXAMPLE
  ./scripts/test-all.ps1 -NoE2E
#>

[CmdletBinding()]
param(
  [switch]$NoE2E,
  [switch]$NoPostman,
  [switch]$BackendOnly,
  [switch]$FrontendOnly
)

$ErrorActionPreference = 'Stop'
$root = Resolve-Path (Join-Path $PSScriptRoot '..')
Set-Location $root

function Write-Section($name) {
  Write-Host ''
  Write-Host "== $name ==" -ForegroundColor Cyan
}

$runBackend  = -not $FrontendOnly
$runFrontend = -not $BackendOnly
$runPostman  = -not ($NoPostman -or $BackendOnly)
$runE2E      = -not ($NoE2E -or $BackendOnly)
if ($FrontendOnly) { $runPostman = $false }

if ($runBackend) {
  Write-Section 'ruff (lint)'
  python -m ruff check .

  Write-Section 'ruff (format check)'
  python -m ruff format --check .

  Write-Section 'isort'
  python -m isort --check-only .

  Write-Section 'pytest (backend) + coverage'
  Push-Location backend
  try {
    python -m pytest --cov=apps --cov-report=term-missing --cov-config=.coveragerc
  } finally { Pop-Location }
}

if ($runFrontend) {
  Write-Section 'eslint'
  npm run lint --workspaces --if-present

  Write-Section 'vitest + coverage'
  npm run test:coverage --workspace admin-ui
}

if ($runPostman) {
  Write-Section 'postman / newman'
  try {
    node scripts/postman-run.mjs
  } catch {
    Write-Warning "postman run failed (non-blocking if backend isn't running): $($_.Exception.Message)"
  }
}

if ($runE2E) {
  Write-Section 'playwright'
  npm run e2e --workspace admin-ui
}

Write-Section 'OK'
