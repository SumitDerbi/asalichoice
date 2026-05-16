# Deployment

AsliChoice deploys to a single cPanel host backed by Passenger. The full procedure is wired up in [plan 012](https://github.com/SumitDerbi/asalichoice/blob/main/plans/phase-0-foundation/012-deploy-sh.md) — this page tracks the pieces as they land.

## Target environment

- **Host**: cPanel + Passenger (mirror of `kimplaspiping` deploy pattern).
- **Python**: managed via cPanel Python Selector.
- **Node**: managed via cPanel Node Selector for any build steps.
- **Database**: MySQL on the same host.
- **Cache + broker**: Redis (or fallback to DB-based locks where Redis is unavailable).

## Pipeline (target)

1. `git pull` on the deploy branch.
2. Backend: install `requirements/production.txt`, run `python manage.py migrate --noinput`, collect static.
3. Admin UI: `npm ci --workspace admin-ui && npm run build --workspace admin-ui`, copy `dist/` into the served path.
4. Restart Passenger via `passenger_wsgi.py touch`.

## Status

> **In progress.** The actual `deploy.sh` ships in plan 012. This page becomes the operator-facing runbook once that lands.
