# <plan-id> — <Title>

> **Phase**: <phase>  **Depends on**: <prev-id or none>  **Module**: <Mxx or -->  **Est. effort**: <S/M/L>

## Goal

1–3 sentences. State the outcome, not the activity.

## Inputs (prerequisites)

- [ ] List of artefacts/state that must exist before starting.
- [ ] Link to relevant SRS section.

## Steps

1. Small, verifiable step. Mention files touched and commands run.
2. ...
3. ...

## Deliverables

- File(s) created/modified.
- Migrations.
- Endpoints.
- Tests.
- Docs page(s).

## Verification

### Manual
1. Steps a reviewer can click/curl to validate.

### Automated
- Commands to run + expected pass output.
  - `pytest backend/tests/<module>/ -q`
  - `pnpm --filter admin-ui test`
  - `pnpm --filter admin-ui e2e -- <spec>`
  - `newman run qa/postman/<module>/collection.json -e qa/postman/local.env.json`

## Definition of Done

- [ ] All Deliverables produced.
- [ ] All Verification steps pass.
- [ ] Code passes lint + type-check.
- [ ] PR opened, reviewed, merged.
- [ ] `plans/_state.md` updated.
- [ ] Docs updated.

## Next step

→ [`<next-plan-id>.md`](./<next-plan-id>.md)

## Previous step

← [`<prev-plan-id>.md`](./<prev-plan-id>.md)
