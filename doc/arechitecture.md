# AsliChoice — System Architecture

> Companion to [PROJECT_DETAILS.md](PROJECT_DETAILS.md). This document defines the technical architecture, including the **public website (online store)**, admin panel, POS app, mobile apps, backend services, data layer, and integrations.

---

## 1. Architecture Goals

Derived directly from the SRS finalized principles:

1. **API-first** — every client (website, admin, POS, mobile) consumes the same backend contracts.
2. **Omnichannel unified engine** — one inventory, one customer, one wallet, one offers engine, one referral engine.
3. **Branch-aware + pincode-aware** — every transactional surface scopes by branch and (for online) by pincode.
4. **Ledger-driven** — inventory, wallet, vendor, customer, accounting are append-only ledgers.
5. **Offline-capable** — POS billing and attendance must function during connectivity loss; sync later.
6. **Configurable, not hardcoded** — feature toggles + global/branch overrides.
7. **Audit-everywhere** — immutable audit logs on critical actions.
8. **Security by design** — RBAC + permission middleware + device restrictions + rate limiting.
9. **Cloud-storage-independent** — file layer abstracts S3 / GCS / Azure / local.

---

## 2. High-Level System Diagram

```
                       ┌──────────────────────────────────────────────┐
                       │                  CLIENTS                     │
                       ├──────────────┬──────────────┬────────────────┤
                       │  Public Web  │  Admin Web   │   POS App      │
                       │  (Storefront)│  (Back-Office)│ (Electron/PWA)│
                       ├──────────────┼──────────────┼────────────────┤
                       │  Customer    │  Partner App │  Delivery App  │
                       │  Mobile App  │  (future)    │  (future)      │
                       └──────┬───────┴──────┬───────┴────────┬───────┘
                              │              │                │
                              ▼              ▼                ▼
                       ┌───────────────────────────────────────────────┐
                       │        CDN  +  WAF  +  Load Balancer          │
                       └───────────────┬───────────────────────────────┘
                                       │
                                       ▼
              ┌────────────────────────────────────────────────────────┐
              │                  API GATEWAY                           │
              │  (Auth · Rate-limit · Routing · Versioning · Logging)  │
              └────┬─────────────┬──────────────┬─────────────┬────────┘
                   │             │              │             │
        ┌──────────▼───┐ ┌───────▼──────┐ ┌────▼─────────┐ ┌─▼──────────┐
        │  Auth/User   │ │  Storefront  │ │  Commerce    │ │  Admin     │
        │  Service     │ │  API         │ │  API         │ │  API       │
        └──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └────┬───────┘
               │                │                │              │
               └────────┬───────┴────────┬───────┴──────────────┘
                        │                │
                        ▼                ▼
        ┌───────────────────────────────────────────────────────┐
        │                 DOMAIN SERVICES (modular monolith)    │
        │                                                       │
        │  Master · Inventory · Pricing · Vendor · Purchase     │
        │  Sales · POS · OnlineStore · CRM · Wallet · Referral  │
        │  Finance · Fulfillment · Returns/QC · HR/Payroll      │
        │  Notifications · Documents · Settings · Audit         │
        └───────────────┬────────────┬─────────────┬────────────┘
                        │            │             │
                        ▼            ▼             ▼
        ┌────────────────┐  ┌─────────────┐  ┌────────────────┐
        │  PostgreSQL    │  │   Redis     │  │  Object Store  │
        │  (OLTP + RLS)  │  │ Cache/Queue │  │  (S3/GCS/Azure)│
        └────────┬───────┘  └──────┬──────┘  └────────────────┘
                 │                 │
                 ▼                 ▼
        ┌────────────────┐  ┌─────────────────────────────────┐
        │  Read Replica  │  │  Job Workers / Schedulers       │
        │  (Reports/BI)  │  │  (Sync · Cron · Notifications)  │
        └────────────────┘  └─────────────────────────────────┘

         ┌─────────────────── External Integrations ───────────────────┐
         │  Razorpay · PhonePe · Paytm · Shiprocket · Dunzo · Porter   │
         │  MSG91/Twilio (SMS) · SES/SendGrid (Email) · WhatsApp BSP   │
         │  ZKTeco / eSSL (Biometric) · Tally / Zoho Books (future)    │
         └────────────────────────────────────────────────────────────┘
```

---

## 3. Recommended Tech Stack

| Layer | Choice | Rationale |
|---|---|---|
| Public Website (Storefront) | **Next.js 14 (App Router) + TypeScript + Tailwind** | SEO (SSR/ISR), mobile-first, fast TTFB, PWA-ready |
| Admin Panel | **React + Vite + TypeScript + Tailwind + shadcn/ui** | SPA, no SEO needed, role-aware UI |
| POS App | **Electron + React** OR **PWA (offline-first)** | Local cache, offline billing, printer/barcode integration |
| Mobile (Customer / Delivery / Partner) | **React Native (Expo)** | Single codebase Android/iOS, push, offline storage |
| Backend | **Node.js (NestJS) + TypeScript** OR **Python (FastAPI)** | Modular, DI, OpenAPI, queues, scheduler |
| API Gateway | **Kong / Traefik** or **Nginx + custom JWT middleware** | Auth, rate-limit, routing |
| Primary DB | **PostgreSQL 16** (with Row-Level Security) | ACID, JSONB, partitioning, replication, branch isolation via RLS |
| Cache / Queue | **Redis** (cache) + **BullMQ / RabbitMQ** (queues) | Sessions, OTP, sync queue, scheduled jobs |
| Search | **Postgres FTS** initially → **Meilisearch / OpenSearch** later | Product search, customer lookup |
| Object Storage | **S3-compatible** (AWS S3 / Cloudflare R2 / MinIO) | Abstracted via provider-independent file service |
| Reporting / BI | Postgres read replica + **Metabase** (initial) → warehouse later | Analytics, scheduled reports |
| Realtime | **WebSocket (Socket.io)** or **Server-Sent Events** | Order tracking, dashboards, notifications |
| CI/CD | GitHub Actions | Tests, lint, build, deploy |
| Infra | Docker + Docker Compose (dev), Kubernetes or VM + systemd (prod) | Portability |
| Monitoring | Prometheus + Grafana + Loki (logs) + Sentry (errors) | Observability |
| Auth | **JWT (access + refresh)** + Redis session store | Stateless API + revocable sessions |

> If the team prefers PHP (CodeIgniter HMVC pattern from prior projects), the same module boundaries apply — see §15 for that variant.

---

## 4. Logical Architecture — Modular Monolith → Future Microservices

Start as a **modular monolith** with strict module boundaries:

```
/backend
├── modules/
│   ├── master/          (Module 1)
│   ├── identity/        (Module 2)
│   ├── vendor/          (Module 3)
│   ├── purchase/        (Module 4)
│   ├── inventory/       (Module 5)
│   ├── storefront/      (Module 6 — public-facing read-heavy APIs)
│   ├── pos/             (Module 7)
│   ├── sales/           (Module 8)
│   ├── crm/             (Module 9)
│   ├── referral-wallet/ (Module 10)
│   ├── notification/    (Module 11)
│   ├── finance/         (Module 12)
│   ├── reports/         (Module 13)
│   ├── fulfillment/     (Module 14)
│   ├── returns-qc/      (Module 15)
│   ├── hr-payroll/      (Module 16)
│   ├── documents/       (Module 17)
│   ├── settings/        (Module 18)
│   ├── security-audit/  (Module 19)
│   └── sync-api/        (Module 20)
├── shared/
│   ├── auth/            (JWT, RBAC middleware)
│   ├── db/              (Postgres client, migrations)
│   ├── cache/           (Redis)
│   ├── queue/           (BullMQ producers/consumers)
│   ├── storage/         (S3 adapter)
│   ├── events/          (Domain event bus)
│   └── audit/           (Audit logger)
└── api/
    ├── storefront/      (Public-facing — guest + customer)
    ├── customer/        (Authenticated customer APIs)
    ├── admin/           (Back-office)
    ├── pos/             (POS app + offline sync)
    ├── mobile/          (Mobile clients)
    └── webhook/         (Payment, delivery, biometric callbacks)
```

**Why modular monolith first**: simpler ops, single transaction boundary across modules (critical for ledger consistency), easier to evolve. Carve out microservices only when scale or team boundaries demand it (likely candidates first: Notifications, Sync, Reports).

---

## 5. Public Website (Online Store) Plan — Module 6 in Depth

### 5.1 Pages & Routes (Next.js)

| Route | Type | Notes |
|---|---|---|
| `/` | ISR | Home, banners, featured, categories |
| `/c/[category]` | ISR + client filter | Category listing, filters, sort |
| `/p/[slug]` | ISR | Product detail, variants, related products |
| `/search?q=` | SSR | Server-side search, faceted |
| `/cart` | Client | Cart, validates live stock |
| `/checkout` | SSR (auth required) | Address, delivery, payment |
| `/login`, `/register` | Client | OTP login, smart fallback |
| `/account` | SSR (auth) | Profile, addresses, orders, wallet, referrals |
| `/account/orders/[id]` | SSR (auth) | Order detail + tracking |
| `/account/wallet` | SSR (auth) | Wallet balance + ledger |
| `/account/referrals` | SSR (auth) | Referral code, link, earnings |
| `/wishlist` | SSR (auth) | Saved products |
| `/serviceability` | SSR | Pincode check landing (can be modal too) |
| `/offers/[slug]` | ISR | Offer/coupon landing |
| `/pages/[slug]` | ISR | CMS pages (about, contact, privacy, T&C, returns) |
| `/sitemap.xml`, `/robots.txt` | Dynamic | SEO |

### 5.2 Storefront Critical Flows

**Location Confirmation (gates everything)**
```
User lands → Detect last pincode → Show suggestion
  → User confirms / changes → Persist to cookie + customer profile
  → Storefront APIs include pincode → Inventory + delivery + MOV + offers load
```

**Add to Cart**
```
Client cart (localStorage for guests, DB for authenticated)
  → On add: POST /storefront/cart/validate {pincode, productId, qty}
  → Returns: stock available (yes/no), unit price, applicable offers
```

**Checkout**
```
Auth required → Address selection → Pincode serviceability check
  → Fulfillment branch resolved → MOV + delivery charge computed
  → Allowed payment methods (per fulfillment branch) loaded
  → Place Order → Reserve Inventory → Initiate Payment
  → Payment Webhook → Confirm Order → Notify
```

**Registration**
```
OTP verify → Capture pincode
  → Serviceable? → Auto-approve → Active
  → Non-serviceable? → status = PENDING_SERVICEABILITY → Generate admin request
```

### 5.3 Storefront APIs (public, read-heavy)

```
GET  /storefront/home                                 → banners, featured, categories
GET  /storefront/categories                           → tree
GET  /storefront/products?cat=&q=&page=&pincode=      → location-aware listings
GET  /storefront/product/:slug?pincode=               → detail + stock + price
POST /storefront/serviceability { pincode }           → zone, branch, MOV, ETA, COD allowed
POST /storefront/cart/validate                        → live stock + price
GET  /storefront/cms/:slug                            → CMS page
```

### 5.4 Customer APIs (authenticated)

```
POST /auth/otp/request { identifier }                 → smart channel resolution
POST /auth/otp/verify  { identifier, code }           → JWT access + refresh
POST /auth/register    { identifier, name, pincode }  → triggers serviceability flow

GET  /customer/me
GET  /customer/addresses · POST · PUT · DELETE
GET  /customer/cart · POST /add · PATCH /:id · DELETE /:id
POST /customer/checkout/quote                         → MOV, delivery, taxes, allowed payments
POST /customer/checkout/place                         → reserves stock, returns paymentIntent
POST /customer/checkout/confirm                       → after payment webhook (idempotent)
GET  /customer/orders · GET /:id
POST /customer/orders/:id/cancel
GET  /customer/wallet · GET /wallet/ledger
GET  /customer/referrals
POST /customer/wishlist/:productId · DELETE
```

### 5.5 SEO, Performance, PWA

- **SEO**: SSR + canonical URLs, OG tags, JSON-LD (Product, BreadcrumbList, Offer), `sitemap.xml`, server-rendered category/product pages with ISR (revalidate 5–15 min).
- **Performance budget**: LCP < 2.5s on 4G, TTFB < 600ms, image lazy + `next/image` AVIF/WebP, CDN cache for `/storefront/*` GETs (vary on pincode).
- **PWA**: manifest + service worker for offline catalog browse (read-only) and install prompt.
- **Accessibility**: WCAG 2.1 AA; semantic HTML; keyboard nav; aria labels.
- **Analytics**: GA4 / Plausible + custom server events for cart abandonment, checkout funnel.
- **Caching strategy**:
  - Edge cache GETs with `Cache-Control: s-maxage=300, stale-while-revalidate=600`.
  - Vary on `pincode` cookie for catalog APIs.
  - Bust cache via event on product/price/stock update.

### 5.6 Storefront ↔ Backend Inventory Contract

The storefront **never** sees raw global stock. It calls:

```http
POST /storefront/inventory/visibility
{
  "pincode": "411001",
  "productIds": ["...", "..."]
}
→
{
  "fulfillmentBranchId": "br_pune",
  "items": [
    { "productId": "...", "availability": "IN_STOCK" | "LOW_STOCK" | "OUT_OF_STOCK", "etaDays": 2 }
  ]
}
```

Server-side it resolves: pincode → fulfillment branch → online sellable qty (physical − reserved buffer) → returns coarse availability buckets only.

---

## 6. Admin Panel Architecture

Single SPA, role-aware. Navigation and routes generated from server permissions.

### 6.1 Layout
- Left nav: dynamic per role (Super Admin sees all; Branch Manager sees branch-scoped).
- Top bar: branch switcher (for multi-branch users), notifications, profile.
- Permission gates: every route + every action button wrapped with `<Can permission="...">`.

### 6.2 Module Screens (one workspace per backend module)

- **Masters**: products, variants, categories, brands, units, taxes, prices, branches, warehouses, payment modes, offers.
- **Vendors**: list, profile, contacts, products mapping, price history, documents, ledger.
- **Purchase**: requisitions, POs, GRN, invoices, returns, payments.
- **Inventory**: per-branch stock, ledger, transfers, adjustments, audits, batch/expiry, damaged.
- **Sales / Orders**: unified list (channel filter), order detail, returns, refunds, exchanges.
- **POS Ops**: shifts, cashier sessions, device registry, offline sync monitor.
- **CRM**: customer 360°, segmentation, communications, serviceability requests.
- **Referral / Wallet**: partners, commission rules, wallet ledger, future payouts.
- **Fulfillment**: picklists, packing, dispatch, delivery tracking, zones, charges.
- **Returns/QC**: return queue, QC inspections, quarantine, disposals, recalls.
- **HR/Payroll**: employees, attendance config, shifts, leaves, payroll cycles, payslips.
- **Finance**: COA, ledgers, expenses, P&L, GST, adjustments.
- **Reports**: role-based dashboards, exports, scheduled reports.
- **Documents**: media library, generated reports, employee/vendor docs.
- **Settings**: global + branch configs, feature toggles, automation rules, cron, approval workflows.
- **Security/Audit**: audit logs, sessions, devices, permission changes, failed logins.

---

## 7. POS Application Architecture

### 7.1 Deployment Options
- **Electron desktop** (recommended for cashiers using printers/scanners on Windows).
- **PWA** alternative for tablets.

### 7.2 Offline-First Stack
```
┌────────────────────────────────────────┐
│  React UI (billing screen, returns)    │
├────────────────────────────────────────┤
│  Local state (Redux Toolkit / Zustand) │
├────────────────────────────────────────┤
│  Local DB: SQLite / IndexedDB          │
│  - product_cache                       │
│  - inventory_cache (branch-scoped)     │
│  - customer_cache                      │
│  - offline_sale_queue                  │
│  - offline_invoice_numbers             │
├────────────────────────────────────────┤
│  Sync Worker (background)              │
│  - Watches network                     │
│  - POST queued sales (idempotent)      │
│  - Pulls master/inventory deltas       │
└────────────────────────────────────────┘
```

### 7.3 Offline Rules
- POS validates against **local** inventory cache and the **local offline sale queue** combined — billing hard-blocks if it would push stock below 0.
- Invoice numbering uses a **reserved range** per POS device (allocated at sync) to prevent collisions.
- Server **idempotency keys** on every offline-queued sale prevent duplicates.

### 7.4 Hardware Integrations
- Barcode scanner (USB HID — keyboard wedge).
- Thermal printer (ESC/POS via USB/network).
- Cash drawer trigger via printer.
- Customer display (future).

---

## 8. Mobile Apps

| App | Audience | Modules used |
|---|---|---|
| Customer App | End customers | Storefront, CRM, Wallet, Referral, Notifications |
| POS App | Cashiers | POS, Inventory, Sales, Returns |
| Delivery App (future) | Delivery agents | Fulfillment, Delivery tracking, OTP confirmation |
| Partner App (future) | Partners/Referrers | Referral, Wallet, Analytics |
| Admin App (future) | Managers on the go | Reports, Approvals, Alerts |

All apps consume `/mobile/*` versioned APIs through the gateway with device registration tokens.

---

## 9. Data Architecture

### 9.1 Database Strategy
- **Single Postgres cluster** (primary + read replica) for OLTP.
- **Row-Level Security (RLS)** enforces branch isolation: every transactional table carries `branch_id`; RLS policies tie to `current_setting('app.user_id')` + branch access list.
- **JSONB** for flexible config (settings, automation rules, template variables).
- **Partitioning** for high-volume tables: `inventory_ledger`, `audit_logs`, `notification_logs`, `sales_orders` (monthly range partitions).
- **Generated columns** for invoice numbers, SKU components.
- **Soft delete**: `is_active boolean` + `deleted_at timestamptz` (nullable).

### 9.2 Ledger Tables (append-only, immutable)

| Ledger | Purpose | Source Modules |
|---|---|---|
| `inventory_ledger` | Every stock change | Purchase, Sales, POS, Transfers, Returns, Adjustments |
| `wallet_ledger` | Every wallet change | Referral, Returns, Redemption, Payouts |
| `accounting_ledger` (`ledger_entries`) | Double-entry accounting | Finance integrates all |
| `customer_ledger` | Customer financial history | Sales, Returns, Wallet |
| `vendor_ledger` | Vendor outstanding | Purchase, Payments |
| `audit_log` | System-wide critical actions | All modules |

Rules:
- **No UPDATE / DELETE** on ledger rows (enforced via revoked privileges + DB trigger).
- Balances are projections — either materialized views refreshed on insert, or computed via window functions for small sets.
- Each ledger row carries: `id, created_at, branch_id, ref_type, ref_id, before, change, after, user_id, device_id, ip, remarks`.

### 9.3 Multi-Branch Isolation Pattern

```
users
  ↕ user_branches (M:N)        ← access scope
branches
  ↑
inventory          (branch_id + warehouse_id + product_id + variant_id)
inventory_ledger   (branch_id + warehouse_id + ...)
sales_orders       (branch_id)
pos_sales          (branch_id + pos_device_id)
employees          (branch_id)
expenses           (branch_id)
```

RLS policy template:
```sql
CREATE POLICY branch_isolation ON sales_orders
USING (
  branch_id = ANY(current_setting('app.branch_ids')::uuid[])
  OR current_setting('app.role') = 'SUPER_ADMIN'
);
```

### 9.4 Event Sourcing for Inventory & Wallet

Even though we use Postgres OLTP, **inventory** and **wallet** are conceptually event-sourced:
- The ledger is the source of truth.
- The `inventory` table is a **projection** (current quantity by branch+warehouse+product+variant).
- Projection updated atomically in the same transaction as the ledger insert (via trigger or service code).

This guarantees: `SUM(inventory_ledger.change) = inventory.quantity` always.

---

## 10. Cross-Cutting Concerns

### 10.1 Authentication & Authorization
- **JWT access token** (15 min) + **refresh token** (30 days, rotating) stored in Redis.
- Refresh token tied to `device_id` (mobile/POS).
- Permission check at three layers: gateway (coarse), service (fine), DB RLS (defense-in-depth).
- **MFA-ready** flag on user (future).

### 10.2 OTP / Smart Channel Resolution
```
POST /auth/otp/request { identifier }
  1. Detect identifier type (mobile vs email)
  2. Find user
  3. Read enabled auth methods + channels from settings
  4. Select best verified channel (system, not user, decides)
  5. Generate OTP (length per config), store in Redis with TTL
  6. Enqueue notification (SMS / Email)
  7. Return { sentTo: "masked recipient", channel: "SMS|EMAIL" }
```

### 10.3 Domain Event Bus
- In-process event bus for the modular monolith (synchronous handlers for ledger consistency, async via queue for notifications/reports).
- Examples:
  - `order.completed` → trigger referral commission evaluation
  - `grn.received` → update inventory ledger + vendor ledger
  - `sale.created` → inventory deduct + accounting entry + customer history
  - `wallet.credited` → notification

### 10.4 Job Workers & Schedulers
| Job | Type | Frequency |
|---|---|---|
| Notification dispatch (SMS/Email/WhatsApp) | Queue (BullMQ) | On demand |
| Offline POS sync ingestion | Queue | On demand |
| Daily sales report | Cron | 06:00 |
| Low stock alert sweep | Cron | Hourly |
| Reservation expiry cleanup | Cron | Every 5 min |
| Near-expiry batch alert | Cron | 09:00 |
| Payroll attendance roll-up | Cron | Monthly |
| Audit log archival | Cron | Daily |

### 10.5 Caching
| Cache | TTL | Invalidation |
|---|---|---|
| Product detail | 10 min | Product update event |
| Category tree | 1 hour | Category update event |
| Storefront home | 5 min | Manual + scheduled |
| Pincode serviceability | 1 hour | Settings update event |
| User session | Refresh TTL | On logout |
| OTP | 5 min | After use |

### 10.6 File / Media
- Service abstraction: `IFileStorage` with adapters (S3, GCS, Azure, local).
- All file rows carry: `entity_type, entity_id, category, mime, size, storage_provider, storage_key, is_public, uploaded_by`.
- Signed URLs for private files (employee docs, vendor agreements, payslips).
- Image pipeline: original → variants (thumbnail, gallery, banner) on upload via worker; WebP/AVIF served via CDN.

### 10.7 Audit
- Every mutation route writes an audit row (interceptor pattern).
- Sensitive ops also write to `approval_audit_logs` with before/after snapshots.

### 10.8 Notifications
- Single `Notification` service consumed by all modules:
  ```ts
  await notifications.send({
    event: 'ORDER_PLACED',
    recipient: { userId, channels: ['SMS','EMAIL'] },
    variables: { orderId, customerName, total }
  });
  ```
- Templates resolved per channel + language + active version.
- Retries with exponential backoff; failures land in DLQ.

---

## 11. Security Architecture

| Concern | Control |
|---|---|
| Transport | TLS 1.2+ everywhere, HSTS, secure cookies |
| Auth | JWT + refresh rotation, device binding, session revocation |
| RBAC | Permission-string-based; granular; checked at gateway + service + DB |
| Input | Validation via Zod / class-validator; parameterized queries only |
| OWASP A01–A10 | CSRF tokens (admin), CORS allow-list, XSS via output encoding, SSRF guard on outbound calls |
| Rate limiting | Per IP + per user + per route (login, OTP, checkout) |
| OTP | Max 5 retries; 5-min window; cooldown; bound to identifier |
| Webhooks | HMAC signature verification (payments, delivery) |
| Secrets | Vault / SSM; never in repo; rotated quarterly |
| Audit | Immutable logs; tamper detection (hash chain — future) |
| PII | Encryption at rest for sensitive columns (PAN, GST, bank details); masked in exports |
| Payment data | Never stored — only payment intent IDs and gateway refs |
| Device | POS billing restricted to registered devices; suspicious-login detection |
| Backups | Daily encrypted, off-site, restore-tested monthly |

---

## 12. Deployment & Environments

### 12.1 Environments
`local → dev → staging → production`

Each with its own DB + Redis + storage bucket; staging mirrors prod scale ÷ 10.

### 12.2 Reference Topology (Production)

```
              Cloudflare CDN + WAF
                       │
              ┌────────┴────────┐
              │   Load Balancer │
              └────────┬────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
   [Web Server]   [Web Server]   [Web Server]   ← Next.js (SSR)
        │              │              │
        └──────────────┼──────────────┘
                       │
                  [API Gateway]
                       │
        ┌──────────────┼──────────────┐
        │              │              │
   [API Node]    [API Node]    [API Node]       ← NestJS/FastAPI
        │              │              │
        └──────┬───────┴──────┬───────┘
               │              │
        [Postgres Primary]  [Redis Cluster]
               │
        [Postgres Replica] ← read-only (reports/storefront)
               │
        [Job Workers x N]
               │
        [S3-compatible Object Store]
```

### 12.3 CI/CD
- PR pipeline: lint, typecheck, unit tests, integration tests against ephemeral Postgres.
- Main branch: build images → push to registry → deploy to staging.
- Manual approval → production rollout (blue/green or rolling).
- DB migrations versioned (e.g. Prisma Migrate / Flyway / Alembic), forward-only.

### 12.4 Observability
- Logs: structured JSON → Loki / CloudWatch.
- Metrics: Prometheus + Grafana (RED method: rate, errors, duration per route).
- Traces: OpenTelemetry → Jaeger / Tempo.
- Errors: Sentry (web + backend).
- Synthetic checks: storefront home, checkout, OTP request every 1 min.
- Alerts: PagerDuty / on-call rotation for SLO breaches.

---

## 13. Integration Architecture

| Integration | Type | Module |
|---|---|---|
| Razorpay / PhonePe / Paytm | REST + webhook | Sales / Online Store |
| Shiprocket / Dunzo / Porter | REST + webhook | Fulfillment |
| ZKTeco / eSSL biometric | Device API / push | HR / Attendance |
| MSG91 / Twilio (SMS) | REST | Notifications |
| AWS SES / SendGrid (Email) | REST / SMTP | Notifications |
| WhatsApp Business API (BSP) | REST | Notifications |
| Tally / Zoho Books (future) | Scheduled export / API | Finance |
| GSTN e-invoice / e-way bill (future) | REST | Finance |
| FCM / APNS | Push | Notifications / Mobile |

**Adapter pattern**: each integration sits behind an interface (`IPaymentGateway`, `ILogisticsProvider`, `ISmsProvider`) so providers can be swapped without touching domain code.

---

## 14. Phased Delivery Plan

### Phase 1 — MVP (per SRS Phase 1 inclusions)
**Modules**: 1, 2, 3, 4, 5, 6 (basic storefront), 7 (POS with offline), 8, 9, 10, 11 (OTP+SMS+Email), 12 (basic accounting + GST), 13 (core reports), 14 (basic fulfillment), 15 (sales/purchase returns), 16 (incl. payroll), 17, 18, 19, 20 (POS offline + base APIs).

**Storefront scope**: catalog, location-aware visibility, cart, checkout, OTP login, registration with serviceability, orders, wallet, referrals, account.

### Phase 2 — Scale
- WhatsApp notifications, push notifications, mobile apps.
- Advanced reports + scheduled exports.
- Wholesale module.
- Delivery partner integrations.
- Loyalty program activation.
- Batch & expiry full UI.
- E-invoicing / e-way bill.

### Phase 3 — Intelligence
- Predictive demand forecasting.
- AI recommendations, smart reorder.
- OCR for vendor invoices.
- Multi-language storefront.
- IoT / smart scale integration.
- Public partner / payout system.

---

## 15. Alternate Stack — PHP Variant (if team continuity matters)

Given prior CodeIgniter 3 + HMVC experience:

| Layer | Choice |
|---|---|
| Storefront | **Next.js** (recommended) OR Laravel + Inertia + Vue |
| Admin / POS web | **Laravel 11** + Inertia + Vue 3 + Tailwind |
| POS desktop | Tauri + Vue (lighter than Electron) |
| Mobile | React Native / Flutter |
| DB | PostgreSQL (or MariaDB if Postgres unfamiliar) |
| Queue | Laravel Horizon + Redis |
| Scheduler | Laravel Scheduler |
| Auth | Sanctum (SPA) + Passport (mobile/3rd-party) |

Module boundaries identical to §4; Laravel packages or modular folder structure (e.g. `nwidart/laravel-modules`) per backend module.

> Avoid CI3 + HMVC for greenfield commerce: it lacks first-class queues, scheduler, migrations, and modern auth tooling, which all map directly to SRS requirements.

---

## 16. Open Architectural Decisions (require sign-off)

1. **Backend language**: NestJS (TS) vs FastAPI (Python) vs Laravel (PHP).
2. **POS shell**: Electron desktop vs PWA.
3. **Storefront hosting**: Vercel/Netlify vs self-hosted Next.js.
4. **Multi-tenancy**: single DB + RLS (recommended) vs schema-per-branch (overkill at this scale).
5. **Search engine**: Postgres FTS (start) vs Meilisearch (Phase 2).
6. **Payment gateway**: which to integrate first (Razorpay recommended).
7. **SMS/Email vendor**: MSG91 vs Twilio; SES vs SendGrid.
8. **CDN/WAF**: Cloudflare vs AWS CloudFront + WAF.
9. **File storage**: Cloudflare R2 (cheap egress) vs AWS S3.

---

## 17. Definition of Done (per Module)

A module ships only when:
- Schema migrations applied, indexed, partitioned where applicable.
- RLS policies in place for branch isolation.
- All routes covered by RBAC permissions.
- Audit logging on every mutation.
- Unit + integration tests ≥ 70% coverage on domain logic.
- OpenAPI spec generated.
- Admin UI screens implemented for the role-based permissions.
- Notifications wired for the documented events.
- Reports/exports implemented for the documented reports.
- Manual QA on at least one end-to-end happy path + one failure path.
- Documentation updated in `/doc`.
