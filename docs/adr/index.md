# Architecture Decision Records

Short, dated records of architectural decisions and their context. Inspired by [Michael Nygard's original template](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions).

## Index

| #                            | Title                  | Status   |
| ---------------------------- | ---------------------- | -------- |
| [000](000-template.md)       | Template               | n/a      |
| [001](001-migrations.md)     | Migrations conventions | Accepted |
| [002](002-service-layer.md)  | Service layer          | Accepted |
| [003](003-branch-context.md) | Branch context         | Accepted |
| [004](004-tax-components.md) | Tax components         | Accepted |

## Process

1. Copy `000-template.md` to `NNN-short-title.md` (next free number, kebab-case).
2. Fill in Context, Decision, Consequences, Alternatives.
3. Open a PR. The ADR is **Proposed** until merged, then **Accepted**.
4. To revise: add a new ADR that supersedes the old one; mark the old as **Superseded by NNN**.
