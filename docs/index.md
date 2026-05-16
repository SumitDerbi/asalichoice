# AsliChoice Documentation

Welcome to the **AsliChoice** internal documentation. This site is the single source of truth for engineers, operators, and stakeholders working on the platform.

## What lives here

- **Architecture** — system shape, module boundaries, conventions.
- **API** — REST conventions and the live OpenAPI reference.
- **Modules** — one page per Mxx module (catalog, inventory, sales, …).
- **UI Guide** — admin-UI patterns: forms, shortcuts, components.
- **User Guide** — role-based how-tos for branch staff, managers, accountants, super-admins.
- **Deployment** — cPanel + Passenger deploy via `deploy.sh`.
- **Operations** — runbooks, on-call procedures.
- **Quality** — testing strategy and runner.
- **Media Spec** — image/document constraints.
- **ADRs** — architecture decision records.

## Getting started

```powershell
# Serve docs locally with live reload
python -m mkdocs serve -f docs/mkdocs.yml

# Build a static site (output in ./site)
python -m mkdocs build -f docs/mkdocs.yml --strict
```

> The API reference embeds Swagger UI from `docs/api/openapi.json`. Re-fetch it any time the backend schema changes:
>
> ```powershell
> python docs/scripts/fetch-openapi.py
> ```

## Where to start reading

- New to the codebase? Start with [Architecture](architecture.md).
- Building a feature? See [API conventions](api/conventions.md) and [UI forms](ui/forms.md).
- Shipping to production? Read the [Deployment guide](deployment/index.md).
