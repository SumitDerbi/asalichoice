# M20 — Mobile API & Offline Sync

> **Phase**: phase-1-modules  **SRS ref**: Module 20  **Depends on**: all prior  **Est. effort**: L

## Goal

A consolidated mobile/offline-friendly surface across POS, GRN, delivery, attendance — single sync protocol, conflict resolution rules, device registration, throttling, secure pairing.

## Steps

1. **Sync protocol** `apps/mobile/`:
   - `Device(code unique, user FK, kind=POS|DRIVER|FIELD, fingerprint, public_key, status=ACTIVE|REVOKED, paired_at, last_seen)`.
   - `SyncOp(device FK, op_uuid unique, op_type, payload_json, client_ts, server_ts nullable, status=QUEUED|APPLIED|CONFLICT|REJECTED, conflict_reason)`.
   - Endpoint `POST /api/v1/mobile/sync/batch` — body: array of ops with client UUIDs. Server applies each in transaction; returns per-op result.
   - Endpoint `GET /api/v1/mobile/sync/snapshot?since=ts` — incremental pull for catalog/prices/permissions for offline cache.
2. **Pairing**:
   - Admin generates 6-digit code in UI → device enters code → device public key registered → server issues device-bound JWT (long-lived, revocable, scoped to user + branch).
3. **Conflict resolution rules** (per op_type):
   - POS sale → server-authoritative stock check; conflict → quarantine, surface to manager.
   - GRN → dedupe on offline_uuid; if PO closed → reject `PUR-040`.
   - Delivery event → last-write-wins by client_ts on same shipment, but status forward-only.
   - Attendance mark → idempotent on (employee, date).
4. **Compression**: gzip/br on all sync payloads; field whitelist serializers to minimise size.
5. **Rate limiting**: per-device 60 req/min, 1000 ops/batch max.
6. **Snapshot scope**: based on device kind + user permissions + current branch.
7. **Error prefix**: `API-*` for transport, op-specific codes reused.
8. **Admin-UI**:
   - Device pairing screen.
   - Device list with revoke, last-seen, queued-op count.
   - Quarantined sync ops review queue.
9. **Tests**: large batch (1000 ops), conflict scenarios per op type, replay safety, revocation effective immediately.
10. **Docs**: `docs/modules/mobile/*` + ADR `022-mobile-sync-protocol.md`.
11. Commit: `feat(M20): mobile sync protocol + pairing`.

## Verification

### Manual
1. Pair a POS device → run 100 offline sales → reconnect → all sync correctly or quarantine on stock conflict.
2. Pair driver device → record 20 shipment events offline → sync.
3. Revoke device → subsequent sync 401 immediately.

### Automated
- `pytest backend/tests/mobile/ -q` ≥ 85%.
- UI + Playwright + Newman green.
- Load test: 10 devices × 100 ops batch → server stable.

## Definition of Done

- [ ] All offline-capable modules use this single sync surface.
- [ ] Conflict rules documented per op_type.
- [ ] Pairing + revocation hardened.
- [ ] `_state.md` advanced — **Phase 1 COMPLETE**.

## Next step

→ [`../phase-2-hardening/200-security-hardening.md`](../phase-2-hardening/200-security-hardening.md)

## Previous step

← [`M19-audit-log.md`](./M19-audit-log.md)
