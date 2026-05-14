# AsliChoice — Plans

Sequential, agent-executable plan library. **Read [`_meta.yaml`](./_meta.yaml) and [`_state.md`](./_state.md) first.**

## How to use

1. **Agent / human starts a session** → opens [`_state.md`](./_state.md) → identifies `current_step`.
2. Opens the referenced plan file → executes its **Steps** → completes **Verification** → marks **Definition of Done**.
3. Updates [`_state.md`](./_state.md): move `current_step` to the file's `next_step`, append entry to `history`.
4. Commits with the convention defined in [`_conventions.md`](./_conventions.md).
5. Never skip verification. Never declare a step done without artifacts listed in **Deliverables**.

## Directory map

```
plans/
├── README.md                 ← this file
├── _meta.yaml                ← machine-readable project context (agents read this)
├── _state.md                 ← current/next/previous tracker (mutable, agents update)
├── _conventions.md           ← coding, branching, commit, naming, security conventions
├── _agent-routing.md         ← which agent (model/subagent) for which kind of work
├── _glossary.md              ← short glossary (full glossary in doc/PROJECT_DETAILS.md Appendix F)
├── templates/
│   ├── plan-template.md      ← copy this for any new plan file
│   └── module-template.md    ← copy this for any new module plan
├── phase-0-foundation/       ← repo, stack, tooling, conventions, deploy script
│   ├── 000-repo-bootstrap.md
│   ├── 001-backend-django-setup.md
│   ├── 002-frontend-react-setup.md
│   ├── 003-website-wagtail-setup.md
│   ├── 004-tooling-linting-husky.md
│   ├── 005-database-schema-baseline.md
│   ├── 006-auth-skeleton.md
│   ├── 007-admin-shell-ui.md
│   ├── 008-api-conventions.md
│   ├── 009-forms-validation-zod.md
│   ├── 010-testing-setup.md
│   ├── 011-docs-platform.md
│   ├── 012-deploy-sh.md
│   ├── 013-site-settings-feature-toggles.md
│   └── 014-seeders-and-defaults.md
├── phase-1-modules/          ← one focused plan per SRS module (1–20)
│   ├── README.md             ← module index
│   ├── M01-master-management/    ← reference: broken into sub-tasks (template for others)
│   │   ├── index.md
│   │   ├── 01-api.md
│   │   ├── 02-ui.md
│   │   ├── 03-integration.md
│   │   ├── 04-tests.md
│   │   └── 05-docs.md
│   ├── M02-user-role.md
│   ├── M03-vendor.md
│   ├── … (M04–M20)
├── phase-2-hardening/        ← security, perf, a11y, SEO, observability
│   ├── 200-security-hardening.md
│   ├── 201-performance-and-caching.md
│   ├── 202-accessibility-and-seo.md
│   └── 203-observability.md
└── phase-3-launch/           ← UAT, data migration, go-live
    ├── 300-uat-checklist.md
    ├── 301-data-migration.md
    ├── 302-go-live-runbook.md
    └── 303-post-launch.md
```

## Hard rules (do not violate)

1. **One plan file at a time.** Each plan is sized to fit in a single agent context window without truncation.
2. **API → UI → Integration → Tests → Docs.** Always this order within a module.
3. **Verification is non-optional.** Manual + automated checks are part of "done".
4. **No hardcoding.** Any value that may vary (offers, taxes, payment modes, branches, OTP config, fees, MOV, zones, thresholds) lives in DB / admin settings — never in code.
5. **Update `_state.md` after every step.** This is how the next agent finds context.
6. **Reference, don't duplicate.** If a convention exists in `_conventions.md`, link to it. Do not re-state it in every plan.

## Source of truth

- Requirements: [`doc/SOFTWARE_REQUIREMENT_SPECIFICATION_ASLI_CHOICE.md`](../doc/SOFTWARE_REQUIREMENT_SPECIFICATION_ASLI_CHOICE.md)
- Planning summary: [`doc/PROJECT_DETAILS.md`](../doc/PROJECT_DETAILS.md)
- Architecture (draft): [`doc/old.arechitecture.md`](../doc/old.arechitecture.md)
