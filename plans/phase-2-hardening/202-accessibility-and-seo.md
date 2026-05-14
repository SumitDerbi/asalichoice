# 202 — Accessibility & SEO

> **Phase**: phase-2-hardening  **Depends on**: 201  **Est. effort**: S

## Goal

WCAG 2.1 AA compliance for admin-ui + storefront. SEO basics solid for storefront so we rank for branded + category queries from day 1.

## Steps

1. **Accessibility audit**:
   - Run `axe-core` (via `@axe-core/playwright`) over every screen; capture violations.
   - Manual keyboard nav over critical flows (login, POS sale, checkout).
   - Screen-reader pass (NVDA / VoiceOver) on top 10 screens.
   - Fix: alt text, ARIA labels, focus rings, contrast ratios, form labels, heading hierarchy, skip-links.
   - Document patterns in `docs/ui/accessibility.md` (shadcn components used; what to verify).
2. **Keyboard shortcuts overlay** (`?`) already from Phase 0 — ensure all module shortcuts listed.
3. **SEO storefront**:
   - Every product page: `<title>`, `<meta description>`, OG/Twitter cards, canonical, JSON-LD Product.
   - Category pages: BreadcrumbList JSON-LD, paginated rel=prev/next.
   - `sitemap.xml` auto-updates with publish; `robots.txt` correct per env.
   - Internal linking: related products, recently viewed.
   - Page speed (covered by 201).
4. **Image alt text**: enforce non-empty `alt` for `ProductImage`; admin-ui validates.
5. **i18n readiness**: storefront strings already key-driven; locale dropdown placeholder for future.
6. **Tests**:
   - Playwright + axe: zero serious/critical violations on top 20 screens.
   - Lighthouse SEO ≥ 95 on storefront top pages.
7. **Docs**: `docs/ui/accessibility.md`, `docs/seo/index.md`.
8. Commit: `feat(a11y,seo): WCAG AA + SEO basics`.

## Verification

### Manual
1. Tab through POS sale flow end-to-end without mouse.
2. Lighthouse SEO score ≥ 95 on product page.

### Automated
- `pnpm --filter admin-ui e2e -- a11y` zero violations.
- Storefront axe scan zero violations.

## Definition of Done

- [ ] WCAG AA met.
- [ ] SEO ≥ 95.
- [ ] Docs published.
- [ ] `_state.md` advanced.

## Next step

→ [`203-observability.md`](./203-observability.md)

## Previous step

← [`201-performance-and-caching.md`](./201-performance-and-caching.md)
