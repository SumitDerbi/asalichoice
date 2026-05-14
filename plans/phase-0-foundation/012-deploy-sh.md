# 012 — deploy.sh (cPanel + Phusion Passenger)

> **Phase**: phase-0-foundation  **Depends on**: 001, 002, 003  **Module**: --  **Est. effort**: M

## Goal

Author `deploy.sh` at repo root mirroring the proven structure of `E:\extra\kimplaspiping\kp\deploy.sh`, adapted for a **two-app** deployment (Django backend + Wagtail storefront) plus a **built admin-UI** served as static assets via .htaccess.

## Inputs

- [ ] 001 backend, 002 admin-ui, 003 storefront all runnable locally.
- [ ] cPanel access details (host, user, virtualenv paths) — captured in `~/deploy_config/<env>/<env>.config` on the server.

## Steps

1. Copy structure from reference script: argument parsing (`branch`, `env_name`), color logging, `trap` rollback, config loader from `~/deploy_config/<env>/<env>.{config,env}`.
2. Required config variables (per app):
   ```
   GIT_DIR=~/repositories/<env>
   APP_DIR_BACKEND=~/asalichoice_api
   APP_DIR_STOREFRONT=~/public_html/<env>
   APP_DIR_ADMIN_UI=~/public_html/<env>/admin     # built React assets served via .htaccess
   VIRTUALENV_BACKEND=/home/<user>/virtualenv/<env>_api/3.11/
   VIRTUALENV_STOREFRONT=/home/<user>/virtualenv/<env>_site/3.11/
   ACTIVATE_BACKEND=$VIRTUALENV_BACKEND/bin/activate
   ACTIVATE_STOREFRONT=$VIRTUALENV_STOREFRONT/bin/activate
   DB_BACKUP_PATH=~/backups/<env>/
   STATIC_ROOT_BACKEND=~/public_html/<env>/static-api/
   STATIC_ROOT_STOREFRONT=~/public_html/<env>/static/
   MEDIA_ROOT=~/public_html/<env>/media/
   REQUIREMENTS_FILE_BACKEND=backend/requirements/production.txt
   REQUIREMENTS_FILE_STOREFRONT=storefront/requirements/production.txt
   NODE_BIN=/home/<user>/nodevenv/admin-ui/20/bin
   ```
3. Pre-flight checks: git, both virtualenvs, node bin (for admin-ui build), env files present.
4. Backup phase: backup both `APP_DIR_*`, dump MySQL DB via `mysqldump` reading creds from `.env`.
5. Pull phase: `git -C $GIT_DIR fetch && git -C $GIT_DIR reset --hard origin/$BRANCH`.
6. Build phase:
   - Admin-UI: `cd $GIT_DIR/admin-ui && pnpm install --frozen-lockfile && pnpm build` → copy `dist/` to `$APP_DIR_ADMIN_UI`.
   - Backend: `. $ACTIVATE_BACKEND && pip install -r $REQUIREMENTS_FILE_BACKEND && python manage.py migrate --noinput && python manage.py collectstatic --noinput`.
   - Storefront: `. $ACTIVATE_STOREFRONT && pip install -r $REQUIREMENTS_FILE_STOREFRONT && python manage.py migrate --noinput && python manage.py collectstatic --noinput`. Build Tailwind: `cd storefront/theme/static_src && $NODE_BIN/npm ci && $NODE_BIN/npm run build`.
7. Sync phase: `rsync -a --delete` source → each `APP_DIR_*` (excluding venv/node_modules/.git).
8. .htaccess files:
   - Storefront `public_html/<env>/.htaccess` (existing Passenger config).
   - Admin-UI `public_html/<env>/admin/.htaccess` — SPA fallback to `index.html` + far-future cache headers for hashed assets + no-cache for `index.html`.
   - Backend Passenger config in `passenger_wsgi.py`.
9. Touch `tmp/restart.txt` for both apps to restart Passenger.
10. Health check phase: `curl -fsSL` to backend `/api/v1/health/` and storefront `/` — abort + rollback if non-200.
11. Cleanup phase: keep last 5 backups, prune older.
12. Document usage in `docs/deployment/index.md`: prerequisites, cPanel Python App setup screenshots, env file template, first-time bootstrap commands, rollback procedure.
13. Sample `.htaccess` templates committed under `deploy/htaccess/`:
    - `admin-ui.htaccess`
    - `storefront.htaccess`
    - `backend.htaccess` (if needed)
14. Sample config templates under `deploy/config-templates/<env>.config.sample` and `<env>.env.sample`.
15. Commit: `feat(deploy): cPanel deploy.sh + htaccess templates`.

## Deliverables

- `deploy.sh` executable, with `set -euo pipefail`.
- `deploy/htaccess/*.htaccess`.
- `deploy/config-templates/`.
- `docs/deployment/index.md`.

## Verification

### Manual
1. Dry-run on a staging cPanel account: `./deploy.sh main staging`.
2. Verify both apps respond.
3. Trigger a deliberate failure (bad migration) → confirm rollback notice and backup directory.

### Automated
- `bash -n deploy.sh` parses cleanly.
- `shellcheck deploy.sh` clean (or annotated exceptions).

## Definition of Done

- [ ] Successful staging deploy.
- [ ] Rollback works.
- [ ] Docs page complete with screenshots.
- [ ] `_state.md` advanced.

## Next step

→ [`013-site-settings-feature-toggles.md`](./013-site-settings-feature-toggles.md)

## Previous step

← [`011-docs-platform.md`](./011-docs-platform.md)
