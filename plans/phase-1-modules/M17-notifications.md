# M17 — Notifications

> **Phase**: phase-1-modules  **SRS ref**: Module 17  **Depends on**: M02, M18  **Est. effort**: M

## Goal

Single notification backbone for SMS, Email, WhatsApp, in-app, and push. Templates, provider abstraction (multiple per channel with failover), event subscriptions, delivery tracking, opt-outs.

## Steps

1. **Models** `apps/notifications/`:
   - `NotificationTemplate(code unique, channel=SMS|EMAIL|WHATSAPP|INAPP|PUSH, kind=TRANSACTIONAL|MARKETING, subject nullable, body_html nullable, body_text, variables_json, is_active, locale=en)`.
   - `NotificationProvider(code, channel, config_json (encrypted), priority, is_active)` — Razorpay-MSG91/Gupshup for SMS, SES/SendGrid for email, Twilio/Gupshup for WhatsApp.
   - `EventSubscription(event_code, template FK, channel, audience=ROLE|USER|CUSTOMER, audience_filter_json, is_active)`.
   - `NotificationLog(template FK, channel, provider FK, recipient, status=QUEUED|SENT|DELIVERED|READ|FAILED|BOUNCED, sent_at, delivered_at, read_at, error, retry_count, ref_type, ref_id)`.
   - `OptOut(recipient_identifier, channel, reason, at)`.
   - `InAppNotification(user FK, title, body, link, is_read, ts)`.
2. **Services**:
   - `notify_service.send(template_code, recipient, vars, channel?)` — channel auto-picked per recipient prefs; provider selected by priority + health; opt-out respected.
   - `notify_service.send_otp(channel, identifier, code, purpose)` — used by M02.
   - `event_dispatcher.emit(event_code, payload)` — invoked by other modules (`sale.posted`, `delivery.out_for_delivery`, `payroll.payslip_ready`, etc.). Looks up subscriptions, renders template, queues sends.
   - Celery queues per channel for throughput control + rate limits per provider.
   - `webhook_handler.receive(provider, payload)` — for delivery/read receipts.
3. **Failover**: provider health tracked per (provider, channel). On consecutive failures (configurable threshold), mark unhealthy; next-priority used. Auto-recovery after cooldown.
4. **Error prefix**: `NTF-*`.
5. **Endpoints**: `/api/v1/notifications/templates/`, `/providers/`, `/subscriptions/`, `/logs/`, `/inbox/me/`, `/opt-outs/`.
6. **Admin-UI**:
   - Template editor with live variable preview + test-send.
   - Provider config (Super Admin).
   - Subscription matrix (events × audiences × channels).
   - Delivery logs dashboard with filters.
   - In-app inbox in top bar bell.
7. **Permissions**: `notifications.template.manage`, `notifications.provider.manage`, `notifications.subscription.manage`, `notifications.logs.view`.
8. **Tests**: template rendering, provider failover, opt-out honour, idempotency (same event id doesn't re-send), webhook signature verification.
9. **Docs**: `docs/modules/notifications/*` + ADR `020-notification-provider-failover.md`.
10. Commit: `feat(M17): notifications with multi-channel + failover`.

## Verification

### Manual
1. Place an online order → confirmation SMS + email + in-app fire.
2. Disable primary SMS provider → next sale uses fallback automatically; logs show provider switch.
3. Customer opts out of marketing → marketing campaign skips them; transactional still goes.

### Automated
- `pytest backend/tests/notifications/ -q` ≥ 85%.
- UI + Playwright + Newman green.

## Definition of Done

- [ ] All channels send via stubs locally; at least one real provider configured in staging.
- [ ] Failover proven.
- [ ] Opt-outs respected.
- [ ] `_state.md` advanced.

## Next step

→ [`M18-system-settings.md`](./M18-system-settings.md)

## Previous step

← [`M16-hr-payroll.md`](./M16-hr-payroll.md)
