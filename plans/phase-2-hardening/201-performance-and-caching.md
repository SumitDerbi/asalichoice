# 201 — Performance & Caching

> **Phase**: phase-2-hardening  **Depends on**: 200  **Est. effort**: M

## Goal

Hit the SLA targets from `PROJECT_DETAILS.md` Appendix E:
- POS API p95 < 2s
- Dashboard load p95 < 5s
- OTP delivery p95 < 30s
- Storefront page render p95 < 2s (cached)

## Steps

1. **Profiling baseline**:
   - Run `locust` / `k6` scenarios mirroring production traffic patterns. Record p50/p95/p99 per endpoint.
   - Backend: `django-silk` in staging to find slow queries.
   - Frontend: Lighthouse + Web Vitals (LCP, INP, CLS) per top page.
2. **DB tuning**:
   - Add indices flagged by Silk slow-query report.
   - MySQL `slow_query_log` enabled; review weekly.
   - Query review: every `.filter()` in hot paths must hit an index. Add composite indices where needed.
   - Materialised summary tables for dashboards (M13 already started).
3. **Caching layers** (Redis):
   - Catalog product detail (5min).
   - Effective price (1min per item+branch).
   - User permissions (5min, busted on role change).
   - System settings (60s, busted on save).
   - Stock snapshot (30s, busted on ledger).
   - Use `versioned cache keys` so writes bump version (no manual invalidation everywhere).
4. **API response shapes**:
   - List endpoints return minimal fields; detail endpoints full.
   - `?fields=...` sparse fieldsets where helpful.
   - Cursor pagination for ledgers and audit log.
5. **Frontend perf**:
   - Code-split per module (Vite auto). Route-level lazy loading.
   - Heavy charts behind `<Suspense>` + skeleton.
   - Query stale-time tuning per resource.
   - Prefetch on hover for predictable navigations.
   - Web Vitals reporting to backend `/api/v1/internal/web-vitals/` (sampled 10%).
6. **Storefront**:
   - HTTP cache headers + CDN-friendly URLs for static.
   - Wagtail page caching middleware with smart invalidation on publish.
   - WebP/AVIF images with `<picture>` srcset.
7. **Celery / background**:
   - Ensure heavy ops (campaigns, reports, exports, payroll) are async with progress endpoints.
   - Beat schedules documented.
8. **Connection pooling**:
   - MySQL: enable persistent connections (`CONN_MAX_AGE`).
   - Redis: single pool per worker.
9. **Load test** post-tuning:
   - 50 concurrent POS terminals, 200 concurrent storefront browsers, 10 concurrent admin dashboards → confirm SLAs met on staging hardware spec.
10. **Docs**: `docs/operations/performance.md` with baseline + post-tuning numbers + tuning recipes.
11. Commit: `perf: caching, indices, query tuning to meet SLA`.

## Verification

### Manual
1. Load-test report shows all SLA targets met.
2. Lighthouse mobile ≥ 90 on storefront home + product page.

### Automated
- `scripts/load-test.sh` (k6) reports p95 within thresholds.

## Definition of Done

- [ ] SLAs met on staging.
- [ ] Web Vitals reporting live.
- [ ] Slow-query log clean.
- [ ] `_state.md` advanced.

## Next step

→ [`202-accessibility-and-seo.md`](./202-accessibility-and-seo.md)

## Previous step

← [`200-security-hardening.md`](./200-security-hardening.md)
