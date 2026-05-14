# M<NN> — <Module Name>

> SRS source: [`doc/SOFTWARE_REQUIREMENT_SPECIFICATION_ASLI_CHOICE.md` MODULE <NN>](../../doc/SOFTWARE_REQUIREMENT_SPECIFICATION_ASLI_CHOICE.md)
> Summary: [`doc/PROJECT_DETAILS.md` MODULE <NN>](../../doc/PROJECT_DETAILS.md)
> Depends on: <list>

## Goal

What this module delivers, in one paragraph.

## Scope

### In scope
- Submodules covered (list per SRS).

### Out of scope (deferred)
- Items the SRS marks "future".

## Data model (high-level)

- Tables: `…`
- Key constraints: soft delete, audit trail, ledger entries if applicable.

## API surface

`GET/POST/PATCH/DELETE /api/v1/<resource>/` — list endpoints to be created.

Error code prefix: `<XYZ>` (see `_conventions.md` §5).

## UI surface

Screens: List, Detail, Create/Edit (drawer), Bulk-action toolbar, Settings sub-page if any.

## Sequenced sub-plans

1. **API** — models, migrations, serializers, viewsets, permissions, audit, postman seed.
2. **UI** — TanStack Query hooks, list/detail/form screens, shortcuts.
3. **Integration** — wire UI to API, optimistic updates, error mapping.
4. **Tests** — pytest + vitest + playwright + postman/newman.
5. **Docs** — MkDocs module page, API reference, user guide section.

## Verification (module-level)

- [ ] All submodules accessible via UI.
- [ ] All endpoints documented in OpenAPI.
- [ ] Postman collection green.
- [ ] Playwright happy-path spec green.
- [ ] No `any` in TS; no missing type hints in Python service layer.
- [ ] Audit log entries verified for every mutating action.
- [ ] Soft-delete verified (no hard DELETE).
- [ ] Permissions enforced (see `_meta.yaml` security).

## Definition of Done

- [ ] All sub-plans completed.
- [ ] Coverage thresholds met (`_conventions.md` §9).
- [ ] Plan-level Verification fully checked.
- [ ] `plans/_state.md` advanced.

## Next module

→ <M<NN+1>>

## Previous module

← <M<NN-1>>
