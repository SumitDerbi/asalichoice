# Conventions

Single source of truth for HOW we build. Plans REFERENCE this file rather than restating rules.

## 1. Repository layout

```
asalichoice/
├── backend/                       Django project root
│   ├── manage.py
│   ├── config/                    settings/{base,development,production}.py + urls + wsgi/asgi
│   ├── apps/                      one Django app per SRS module (master, users, vendor, ...)
│   ├── requirements/              base.txt, development.txt, production.txt
│   ├── tests/                     pytest tests mirroring apps/
│   └── manage.py
├── admin-ui/                      React + Vite + TS (shadcn) — operator/admin panel
│   ├── src/
│   │   ├── app/                   router, layout shell
│   │   ├── modules/               one folder per SRS module
│   │   ├── components/ui/         shadcn primitives
│   │   ├── components/shared/     shared composite components
│   │   ├── lib/                   api client, query keys, schemas
│   │   └── hooks/
│   ├── tests/                     vitest unit tests
│   └── e2e/                       playwright tests
├── storefront/                    Wagtail site (public website)
│   ├── apps/website/              Wagtail pages, blocks, snippets
│   └── theme/                     Tailwind theme
├── qa/
│   ├── postman/                   Postman collections + environments
│   └── playwright/                shared fixtures (if not co-located with admin-ui/e2e)
├── docs/                          MkDocs site (technical + user + deployment + api)
├── deploy.sh                      cPanel deploy script (see plans/phase-0-foundation/012)
├── plans/                         THIS DIRECTORY
└── doc/                           original SRS + planning summary (DO NOT mix with docs/)
```

## 2. Git & PR

- **Branches**: `feat/<module-id>-<short-slug>`, `fix/...`, `chore/...`, `docs/...`, `test/...`.
- **Commits**: Conventional Commits. Examples:
  - `feat(M01): add product variant CRUD endpoint`
  - `fix(M05): block negative stock on offline POS sync`
  - `docs(plans): advance state to 001`
- **PR template**: must include — Module ID, plan file link, verification checklist, screenshots/recordings for UI, postman run output for API.
- **Squash merge** to `main`. No force-push to `main`.

## 3. Code quality

- **Python**: `ruff` (lint), `black` (format), `isort` (imports), type hints required for new code.
- **TypeScript**: `eslint` + `prettier`. `strict: true` in tsconfig. No `any` without a `// reason:` comment.
- **CSS**: `stylelint` for any handwritten CSS (prefer Tailwind utilities).
- **Pre-commit**: `pre-commit` (python side) + `husky` + `lint-staged` (node side).
- **CI** (later): runs lint + tests + type-check on every PR.

## 4. Naming

| Thing | Style | Example |
|---|---|---|
| Python modules / packages | snake_case | `inventory_ledger` |
| Django apps | snake_case | `master_management` |
| Models | PascalCase singular | `ProductVariant` |
| DB tables | snake_case plural | `product_variants` |
| API routes | kebab-case, plural | `/api/v1/product-variants/` |
| TS files | kebab-case | `product-variant-form.tsx` |
| React components | PascalCase | `ProductVariantForm` |
| Hooks | `use` prefix | `useProductVariants` |
| Query keys | tuple-arrays | `['product-variants', { branchId }]` |
| ENV vars | UPPER_SNAKE | `DB_PASSWORD` |

## 5. API conventions

- **Versioned** under `/api/v1/`.
- **DRF ViewSets** by default; FunctionView only for one-off actions.
- **Pagination**: cursor pagination for ledgers, page-number for everything else. Default page size 25, max 200.
- **Filtering**: `django-filter`. Always document allowed filters in the endpoint docstring.
- **Errors**: standard envelope:
  ```json
  { "error": { "code": "INV-001", "message": "Insufficient stock", "details": {...} } }
  ```
- **Error code namespaces** (extend in this table as modules land):
  | Prefix | Domain |
  |---|---|
  | `AUTH` | authentication / OTP |
  | `USR`  | users / roles / permissions |
  | `MST`  | master data (products, taxes, units…) |
  | `VEN`  | vendor |
  | `PUR`  | purchase / GRN |
  | `INV`  | inventory |
  | `POS`  | retail POS |
  | `ONL`  | online store |
  | `SAL`  | sales / orders |
  | `CRM`  | customer / CRM |
  | `REF`  | referral / wallet |
  | `NTF`  | notifications |
  | `FIN`  | finance / ledger |
  | `RPT`  | reports |
  | `DEL`  | delivery / fulfillment |
  | `RET`  | returns / QC |
  | `HR`   | HR / payroll |
  | `DOC`  | documents / media |
  | `CFG`  | system settings |
  | `SEC`  | super admin / audit |
  | `API`  | api / sync / device |
- **Idempotency**: mutating endpoints accept `Idempotency-Key` header.
- **Audit**: every write goes through a service layer that emits an audit entry.

## 6. UI conventions (admin-ui)

- **shadcn first**. Build composites from shadcn primitives.
- **Compact, info-dense**. Tables over cards for list views. Inline edit where reasonable.
- **Drawers > modals** for forms longer than 4 fields.
- **Command palette** (`Ctrl+K`) global search across modules.
- **Keyboard shortcuts**: documented per page; visible via `?` overlay.
- **Optimistic updates** via TanStack Query when safe; rollback on error.
- **Forms**: TanStack Form + Zod schema co-located with the form component.
- **i18n keys** from day 1 (no hardcoded user strings) — English only Phase 1.
- **Loading**: skeleton screens, not spinners, for list views.
- **Errors**: surface `error.code` + `error.message` from API; never raw stack traces.
- **Animations**: Framer Motion for purposeful motion (drawer open, list reorder). No gratuitous animation.

## 7. No hardcoding

If a value can change without code changes, it lives in DB or `SystemSetting`:
- Taxes, currencies, payment modes, OTP length/expiry, delivery zones, MOV, fees, branch info, offer rules, role permissions, feature toggles, integration API keys.
- Admin panel exposes a **Settings** module (M18) for managing these.

## 8. Security baseline (OWASP)

- Input validation: server-side mandatory (Zod on client is UX, not security).
- Output encoding: Django auto-escape on; DRF serializers must not raw-render.
- Auth: JWT short-lived; refresh rotation; revocation list in Redis.
- Authorization: permission checked at view + service layer (defense in depth).
- Rate limit: see `_meta.yaml` → `security.rate_limits`.
- Secrets: env-only, never in repo. Sample `.env.example` committed; real `.env` never.
- File uploads: extension + MIME allowlist; antivirus scan hook in Phase 2.
- SQL: ORM only; raw SQL requires review + parameterization.
- CSRF: enabled on cookie-auth endpoints (admin UI uses JWT, so CSRF not required there but kept for Wagtail).
- Headers: HSTS, CSP, X-Content-Type-Options, X-Frame-Options DENY, Referrer-Policy.

## 9. Testing

- **Unit**: every service function + every serializer + every reducer/hook.
- **API**: Postman collection per module under `qa/postman/<module>/`, with `pre-request` setup and `tests` assertions; runnable via `newman` in CI.
- **E2E**: Playwright spec per critical user journey (login, POS bill, online order, GRN, refund).
- **Coverage gate**: 70% line coverage minimum per module. Tests for `services/` ≥ 85%.

## 10. Documentation

- **MkDocs Material** in `docs/`. One section per module: API, UI guide, user guide.
- **OpenAPI** auto-generated by `drf-spectacular`; published into the docs site.
- **ADRs** (Architecture Decision Records) in `docs/adr/NNN-title.md` for any non-trivial decision.
- **Image sizing** doc in `docs/media-spec.md` (product thumbnails, banners, etc.).

## 11. Plan file structure (every plan must follow this)

```markdown
# <plan-id> — <Title>

> Phase: <phase>  Depends on: <prev-id>  Module: <Mxx | -- >

## Goal
1–3 sentences.

## Inputs (prerequisites)
Bulleted artefacts that must already exist.

## Steps
Numbered, small (≤ 1 day each). Each step lists files touched / commands run.

## Deliverables
Concrete artefacts (files, endpoints, migrations, tests).

## Verification
- **Manual**: ordered list of click-throughs / curl commands.
- **Automated**: which test files must pass + commands.

## Definition of Done
Checklist of binary conditions.

## Next step
Link to the next plan file.

## Previous step
Link to the previous plan file.
```
