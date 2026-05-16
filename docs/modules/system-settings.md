# System Settings (M18 — early slice)

The system-settings module groups runtime configuration that operators tune
without redeploying:

| Resource         | Purpose                                            |
| ---------------- | -------------------------------------------------- |
| `SiteSetting`    | Typed key/value config (global or branch-scoped).  |
| `FeatureToggle`  | On/off flags with optional rollout %.              |
| `IntegrationKey` | Encrypted credentials (Razorpay, MSG91, etc.).     |
| `SocialLink`     | Storefront social URLs.                            |
| `ContactInfo`    | Business contact rows displayed on the storefront. |

## API (all endpoints require super-admin)

| Method | Path                                    | Notes                                      |
| ------ | --------------------------------------- | ------------------------------------------ |
| GET    | `/api/v1/system-settings/`              | Secret rows return `value_json == "***"`.  |
| POST   | `/api/v1/system-settings/`              | `key`, `value_json`, `scope`, `branch_id`. |
| GET    | `/api/v1/feature-toggles/`              | CRUD.                                      |
| GET    | `/api/v1/integration-keys/`             | `value` masked unless revealed.            |
| GET    | `/api/v1/integration-keys/{id}/reveal/` | Returns plaintext; **audit-logged**.       |
| GET    | `/api/v1/social-links/`                 | CRUD.                                      |
| GET    | `/api/v1/contact-info/`                 | CRUD.                                      |

## Encryption

`IntegrationKey.value_encrypted` is sealed with Fernet (AES-128-CBC + HMAC).
The key is resolved in this order:

1. `SETTINGS_FERNET_KEY` environment variable (urlsafe-base64, 32-byte).
2. Dev fallback derived deterministically from `SECRET_KEY`
   (`urlsafe_b64encode(sha256(SECRET_KEY).digest())`).

**Production must set `SETTINGS_FERNET_KEY` explicitly.** Generate a fresh key:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Rotating `SECRET_KEY` without setting `SETTINGS_FERNET_KEY` will invalidate
every stored secret.

## Caching

`apps.system_settings.services` keeps a 60-second in-process TTL cache for
settings and toggles. `post_save` / `post_delete` signals evict matching
entries. Multi-process deployments may see up to 60 s of stale reads on
non-saving workers — acceptable for phase-0; M18 swaps this for Redis.

## Feature rollouts

`is_feature_enabled(key, user)` is deterministic:

```
bucket = sha256(f"{key}:{user.pk or 'anon'}").digest()[:4] -> int -> %100
enabled if bucket < rollout_percentage
```

Anonymous callers all hash to the same `"anon"` bucket, so 50 % rollout is
effectively 0 % or 100 % for unauthenticated traffic.

## Seeder

`python manage.py seed_settings` is idempotent: it creates baseline rows for
OTP length/expiry, default currency/timezone, COD toggle, social links, and
a primary contact. Pass `--overwrite` to reset values to defaults.

## Admin UI

`/system-settings` (super-admin only) renders tabbed read-only tables for all
five resources. The integration-keys tab has a reveal-eye button that calls
the reveal endpoint and surfaces plaintext inline; every reveal emits an
`AuditLog` row.
