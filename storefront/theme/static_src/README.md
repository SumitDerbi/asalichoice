# `theme/static_src/` — Tailwind build pipeline

This directory holds the **Tailwind CSS** source for the storefront theme,
deliberately kept **standalone** (no `django-tailwind`) per
[`plans/phase-0-foundation/003-website-wagtail-setup.md`](../../../plans/phase-0-foundation/003-website-wagtail-setup.md)
step 2 — to avoid coupling Node to the Django project at runtime.

## Files

| File | Purpose |
|---|---|
| `package.json` | npm scripts + pinned `tailwindcss` (+ typography / forms plugins). |
| `tailwind.config.js` | JIT content globs and theme extensions. |
| `input.css` | Entry stylesheet (`@tailwind base/components/utilities`). |

## Build

From `storefront/theme/static_src/`:

```bash
npm install                 # one-time, installs Tailwind CLI locally
npm run tailwind:build      # one-shot, minified
npm run tailwind:watch      # local dev (rebuilds on save)
```

Output is written to `storefront/theme/static/theme/css/output.css`, which is
served by Django's `AppDirectoriesFinder` (the `theme` app is in
`INSTALLED_APPS`) and referenced from `base.html` via
`{% static 'theme/css/output.css' %}`.

`output.css` is intentionally **committed** so the storefront can be served
without a Node toolchain on the deploy host (cPanel). Regenerate it whenever
templates or `input.css` change, and commit the result.
