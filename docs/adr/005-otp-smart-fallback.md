# ADR-005 — OTP smart fallback

- **Status**: Accepted
- **Date**: 2026-05-24
- **Decider**: backend team
- **Context plan**: `plans/phase-1-modules/M02-user-role.md`

## Context

Users in our target market authenticate by **email**, **mobile**, or
**employee code** — and any one of those three identifiers must reach
the same account. For OTP-based flows (login, password reset, phone
verification) we have three delivery channels:

- **SMS** — cheapest, most reliable in-country, requires a mobile.
- **EMAIL** — cheapest globally, slowest delivery, requires an email.
- **WHATSAPP** — best UX when available, costs more, depends on
  provider configuration.

A naive design would pin OTP delivery to the channel matching the
identifier the user typed:

- email identifier → email OTP
- mobile identifier → SMS OTP
- employee-code identifier → ???

…but this breaks down quickly:

1. Employee-code login has no associated channel by definition.
2. SMS providers occasionally outage; users get stuck waiting for an
   OTP that will never arrive.
3. A user might have an email on file but no mobile (or vice versa).
4. We want WhatsApp to be a _preference_, not a hard requirement.

## Decision

OTP delivery uses a **smart fallback chain** computed per request,
implemented in `apps.users.services.auth_service._channel_priority`:

```
1. preferred_channel (if supplied AND the user has that contact)
2. SMS      (if user.mobile is set)
3. EMAIL    (if user.email is set)
4. WHATSAPP (if user.mobile is set)
```

The first channel in the chain that the user has a contact for AND
the provider accepts is the channel used. If a channel raises a
delivery error, the service walks to the next channel. If every
channel in the chain fails (or the user has zero usable contacts),
`OTPDeliveryFailed` is raised (`AUTH-014`, HTTP 503).

`OTPLog` records the channel actually used (not the preference), so
audit trails reflect reality.

## Why this order

- **SMS first** — empirically the highest deliverability for our
  target geography. Mobile is also the most common identifier.
- **EMAIL second** — universal fallback. A user with no mobile still
  has email. Latency is acceptable for OTP (we use a 10-minute TTL).
- **WHATSAPP last** — phase-1 has no WhatsApp Business API provider
  wired in; the stub always returns a "not configured" error so the
  fallback is exercised in tests. Once a provider is integrated, we
  promote WhatsApp ahead of EMAIL via the future
  `SiteSetting('otp.fallback_chain')` knob (see Follow-ups).

## Why not store a per-user preference?

We do — sort of. The optional `preferred_channel` argument to
`request_otp()` lets the calling client (admin UI today, customer app
later) suggest a channel. The server still validates the user has
that contact and silently falls back if not — clients never see "you
preferred SMS but we used email", only the actual `channel` value in
the response. This avoids leaking which contacts the user has
configured.

A `User.preferred_otp_channel` column was rejected because it
duplicates the runtime decision (the user might add / remove contacts)
and creates a stale-data risk.

## Consequences

- OTP throughput is robust to a single channel outage.
- Tests can deterministically force fallback via
  `settings.OTP_FORCE_FAIL_CHANNELS = {"SMS"}` — no provider mocking
  required.
- Audit (`OTPLog.channel`) reflects the channel actually used, so
  cost-allocation reports against the SMS / WhatsApp gateways are
  accurate.
- The user-facing `AUTH-014` error is rare (no usable channels) and
  triggers a clear toast in the UI telling the user to contact
  support.
- Branch / tenant-level overrides are deferred to phase-2 — see
  Follow-ups.

## Alternatives considered

- **Hard-coded per-identifier rule** (email→EMAIL, mobile→SMS):
  rejected because employee-code login has no defined channel, and
  one-channel outages strand users.
- **User-chosen channel only**: rejected for the new-user case —
  the user has no idea which channel was configured for them and
  every wrong choice burns a rate-limit slot (`AUTH-013`).
- **Round-robin across channels**: rejected because it triples
  delivery cost and confuses the audit trail.

## Follow-ups

- Introduce `SiteSetting('otp.fallback_chain')` (M02.5 or M16) so
  ops can reorder the chain per environment without a code change.
  The setting will accept a JSON list, e.g. `["WHATSAPP","SMS","EMAIL"]`,
  and `_channel_priority` will read it as the seed before applying
  per-user availability filtering.
- Once a WhatsApp Business provider is wired up, remove the
  always-fail stub in `notify_service.send_otp` and re-run the
  fallback tests with the new provider mocked.
- Phase-2: per-tenant chains keyed on the branch context, for
  multi-region tenants.
