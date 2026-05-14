# 203 — Observability

> **Phase**: phase-2-hardening  **Depends on**: 200, 201  **Est. effort**: M

## Goal

Logging, metrics, error tracking, and uptime monitoring so we can see problems before users report them and debug fast when they do.

## Steps

1. **Structured logging**:
   - Backend: `python-json-logger` formatter. Fields: `ts, level, logger, msg, request_id, user_id, branch_id, module`.
   - `RequestIdMiddleware` assigns/propagates `X-Request-Id`.
   - Storefront same.
2. **Log shipping**: cPanel constraints — keep local rotating files + optional Logtail / BetterStack / Papertrail via syslog or HTTP appender. Document choice in `docs/operations/logging.md`.
3. **Error tracking**: Sentry (or self-hosted GlitchTip). DSN via env. Source maps uploaded for admin-ui on build.
4. **Metrics**:
   - `django-prometheus` exporter (where Passenger allows; else a pull endpoint behind auth).
   - Custom counters: sales_posted_total, sales_failed_total, pos_offline_quarantined_total, payment_webhook_failures_total, otp_sent_total, notification_failures_total.
   - Histograms for p95s.
5. **Uptime monitoring**: ping `/api/v1/health/` and storefront `/` every 60s. Provider: UptimeRobot / BetterStack. Pager: PagerDuty / Opsgenie / WhatsApp via M17.
6. **Health endpoint depth**: extend `/health/` with `?deep=true` checking DB, Redis, Celery broker, storage write.
7. **Tracing** (optional Phase 2): OpenTelemetry with OTLP exporter — note as future-work if not in scope here.
8. **Dashboards** (Grafana Cloud free tier or hosted Sentry):
   - Service health, error rate, sales rate, OTP success rate, queue depth, slow-query top 10.
9. **Alert rules**:
   - 5xx > 1% over 5min.
   - p95 latency above SLA over 10min.
   - Celery queue depth > 1000.
   - Notification provider failover triggered.
   - Backup job failed.
10. **Audit-log → SIEM (future)**: noted in roadmap.
11. **Runbooks** `docs/operations/runbooks/`: per-alert "what to check, how to fix, who to call".
12. Commit: `feat(observability): logging, metrics, error tracking, alerts`.

## Verification

### Manual
1. Trigger a deliberate exception → appears in Sentry within 1 min.
2. Trigger Celery backlog → alert fires.
3. Health deep check returns all green.

### Automated
- Synthetic test hits `/health/?deep=true` from external monitor.

## Definition of Done

- [ ] All alerts wired to a pager.
- [ ] Runbooks for each alert.
- [ ] Dashboards live.
- [ ] **Phase 2 COMPLETE**.
- [ ] `_state.md` advanced to Phase 3.

## Next step

→ [`../phase-3-launch/300-uat-checklist.md`](../phase-3-launch/300-uat-checklist.md)

## Previous step

← [`202-accessibility-and-seo.md`](./202-accessibility-and-seo.md)
