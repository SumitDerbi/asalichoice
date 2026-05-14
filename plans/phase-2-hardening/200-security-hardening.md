# 200 — Security Hardening

> **Phase**: phase-2-hardening  **Depends on**: Phase 1 complete  **Est. effort**: M

## Goal

Take the system from "working" to "ready to face the internet." Verify every OWASP Top 10 control, run an internal pen-test pass, fix all findings.

## Steps

1. **OWASP Top 10 audit** — produce a checklist file `docs/security/owasp-checklist.md` with status per control:
   - A01 Broken Access Control: re-verify every endpoint has `permission_classes`; run automated scanner that hits every URL anonymously and as low-perm user.
   - A02 Cryptographic Failures: confirm TLS-only, HSTS, argon2 hashing, secrets at rest encrypted (M18 IntegrationKey, M16 documents).
   - A03 Injection: ensure ORM-only, parameterised queries; ban `raw()` without review; XSS audit on storefront templates and admin-ui (React default escapes — audit `dangerouslySetInnerHTML` usages).
   - A04 Insecure Design: re-review threat model docs.
   - A05 Misconfiguration: production settings reviewed (DEBUG=False, ALLOWED_HOSTS strict, CSP, X-Frame DENY, Referrer-Policy, Permissions-Policy).
   - A06 Vulnerable Components: `pip-audit`, `pnpm audit`, `safety check`. Fix or document.
   - A07 Auth Failures: confirm OTP rate limits, password lockout, session timeout 30min idle, MFA roadmap noted.
   - A08 Software & Data Integrity: signed migrations? At minimum SHA hash in CHANGELOG; verify `pip install --require-hashes`.
   - A09 Logging Failures: confirm M19 audit covers all writes; security events (login fail, perm denied, admin actions) flagged.
   - A10 SSRF: validate any URL fetcher (3PL, webhooks) against allowlist.
2. **Internal pen-test pass** (manual + tools):
   - `nikto`, `zap-baseline`, `nuclei`.
   - Manual: IDOR on every resource (try other users' ids), CSRF on cookie-auth endpoints (we use JWT in headers — confirm no cookie-auth surface), JWT none-alg, refresh token reuse, role escalation.
   - Storefront: form CSRF tokens present, XSS via product reviews/notes.
3. **Dependency lockfile audit**: `pnpm audit --prod`, `pip-audit` — zero high/critical at release.
4. **Secrets scan**: `gitleaks` over history → if any found, rotate.
5. **CSP**: production CSP report-only first → observe → enforce. Document allowed origins in `docs/security/csp.md`.
6. **Rate limit verification**: hit OTP, login, API endpoints at the boundary; confirm 429 returns.
7. **Backup/restore drill**: run `deploy.sh` rollback, restore DB from backup, validate. Record RPO/RTO actuals.
8. **Incident response runbook** `docs/operations/incident-response.md`.

## Deliverables

- `docs/security/owasp-checklist.md` complete.
- Findings + fixes in `docs/security/findings.md`.
- CSP enforced in production.
- Backup/restore drill report.

## Verification

### Manual
1. Re-run scanners after fixes → zero high/critical.
2. Restore from yesterday's backup into staging → app boots clean.

### Automated
- `scripts/security-scan.sh` (pnpm audit + pip-audit + gitleaks + zap-baseline) exits 0.

## Definition of Done

- [ ] OWASP checklist 100% green.
- [ ] All findings closed or risk-accepted in writing.
- [ ] Incident runbook published.
- [ ] `_state.md` advanced.

## Next step

→ [`201-performance-and-caching.md`](./201-performance-and-caching.md)

## Previous step

← [`../phase-1-modules/M20-mobile-api-sync.md`](../phase-1-modules/M20-mobile-api-sync.md)
