# Operations Runbook

Operational procedures for keeping AsliChoice healthy in production. Expanded as phase-2 (hardening) and phase-3 (launch) plans land.

## Health checks

- `GET /api/v1/health/` — backend liveness.
- Admin UI: hitting any unauthenticated route renders the login screen, which itself smoke-tests the SPA.

## Daily

- Confirm the latest Celery beat run produced reports (once M12 ships).
- Check the audit log for any restored soft-deletes.

## Incident response

> Populated alongside on-call rotation in phase-3.
