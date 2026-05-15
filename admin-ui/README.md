# Admin UI

React + Vite + TypeScript admin panel for AsliChoice. See [`../plans/phase-0-foundation/002-frontend-react-setup.md`](../plans/phase-0-foundation/002-frontend-react-setup.md).

## Scripts

```bash
npm install                  # from repo root or this folder
npm run dev      --prefix admin-ui
npm run build    --prefix admin-ui
npm run test     --prefix admin-ui
npm run lint     --prefix admin-ui
npm run typecheck --prefix admin-ui
```

The dev server runs on http://localhost:5173 and expects the backend at the URL declared in `VITE_API_BASE_URL` (default `http://localhost:8000/api/v1`).

## Layout

```
src/
├── app/            Router, shell, command palette, shortcuts overlay
├── components/
│   ├── ui/         shadcn-style primitives (button, input, dialog, command…)
│   └── shared/     composed components shared across modules
├── lib/
│   ├── api/        axios client, query client, typed error envelope
│   ├── auth/       zustand store for JWT (login flow wired in plan 006)
│   └── utils.ts    cn() helper
├── modules/        One folder per SRS module (M01-M20)
├── hooks/          shared hooks
└── styles/         globals.css (Tailwind + CSS variables)
```

## Conventions

See [`../plans/_conventions.md`](../plans/_conventions.md) §6 (UI). Highlights:

- shadcn-first; composites built from primitives.
- TanStack Query + Form + Zod for data/forms.
- Command palette (`Ctrl K`), shortcuts overlay (`?`).
- Tailwind only — handwritten CSS lives in `styles/globals.css`.
- Strict TypeScript; no `any` without a `// reason:` comment.
