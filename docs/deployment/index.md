# Deployment

AsliChoice deploys to a single **cPanel + Phusion Passenger** host running three
artifacts:

| App                           | Type                     | Served from                  |
| ----------------------------- | ------------------------ | ---------------------------- |
| `backend` (Django REST + DRF) | Passenger Python App     | `~/asalichoice_api/`         |
| `storefront` (Wagtail)        | Passenger Python App     | `~/public_html/<env>/`       |
| `admin-ui` (Vite + React)     | static SPA + `.htaccess` | `~/public_html/<env>/admin/` |

A single repo-root script — [`deploy.sh`](https://github.com/SumitDerbi/asalichoice/blob/main/deploy.sh) —
drives all three on every deploy.

## Prerequisites (one-time, per environment)

Performed in cPanel by an operator:

1. **Setup Python App** ×2 — one for the backend (`asalichoice_api`) and one
   for the storefront (`asalichoice_site`). Both on Python 3.11. Note the
   virtualenv paths shown by cPanel — they go into the config file below.
2. **Setup Node.js App** ×1 — Node 20, used during deploy to build the
   admin-ui and the storefront Tailwind bundle. Note the nodevenv `bin` path.
3. **MySQL Database** — create the DB + user, grant ALL PRIVILEGES.
4. **Domains** — typically:
   - `api.<domain>` → backend Passenger app
   - `<domain>` → storefront Passenger app
   - `<domain>/admin/` → admin-ui static folder
5. **Git repo** — `git clone` the AsliChoice repo into
   `~/repositories/<env_name>` (this is `GIT_DIR`). Add the deploy SSH key
   on GitHub.
6. **Server-side config dir** — create:
   ```
   ~/deploy_config/<env_name>/
       <env_name>.config
       <env_name>.api.env
       <env_name>.site.env
   ```
   Use the templates from
   [`deploy/config-templates/`](https://github.com/SumitDerbi/asalichoice/tree/main/deploy/config-templates)
   as a starting point.

## What `deploy.sh` does

```
load_config          # parse ~/deploy_config/<env>/<env>.config
preflight_checks     # git, rsync, both venvs, node bin, env files
create_backup        # rsync app dirs + mysqldump → ~/backups/<env>/backup_<ts>/
pull_latest_code     # git fetch + reset --hard origin/<branch>
build_admin_ui       # npm ci --workspace admin-ui && npm run build → rsync to APP_DIR_ADMIN_UI
deploy_backend       # rsync backend → pip install → migrate → collectstatic
deploy_storefront    # Tailwind build → rsync storefront → pip install → migrate → collectstatic
restart_apps         # touch tmp/restart.txt on both Passenger apps
health_checks        # curl HEALTHCHECK_* URLs (if configured)
print_summary
```

Backups are rotated automatically — the **last 5** are kept under
`$DB_BACKUP_PATH/backup_<timestamp>/`.

## Usage

```bash
cd ~/repositories/<env_name>
./deploy.sh main staging      # branch, env_name
./deploy.sh main production
```

Arguments default to `main` + `staging` when omitted.

## Config template summary

See [`deploy/config-templates/env.config.sample`](https://github.com/SumitDerbi/asalichoice/blob/main/deploy/config-templates/env.config.sample)
for the full template. Required variables:

| Variable                                                      | Purpose                                             |
| ------------------------------------------------------------- | --------------------------------------------------- |
| `GIT_DIR`                                                     | Where the repo was cloned (`~/repositories/<env>`). |
| `APP_DIR_BACKEND` / `APP_DIR_STOREFRONT` / `APP_DIR_ADMIN_UI` | Live app dirs.                                      |
| `ACTIVATE_BACKEND` / `ACTIVATE_STOREFRONT`                    | `…/bin/activate` for each venv.                     |
| `REQUIREMENTS_FILE_BACKEND` / `REQUIREMENTS_FILE_STOREFRONT`  | Relative to each app dir.                           |
| `STATIC_ROOT_BACKEND` / `STATIC_ROOT_STOREFRONT`              | `collectstatic` targets.                            |
| `DB_BACKUP_PATH`                                              | Where to write timestamped backups.                 |
| `NODE_BIN`                                                    | nodevenv `bin/` used during build.                  |
| `HEALTHCHECK_BACKEND_URL` / `HEALTHCHECK_STOREFRONT_URL`      | Optional; deploy aborts on non-200.                 |

`.env` files for each app live alongside the `.config` (templates:
[`env.api.env.sample`](https://github.com/SumitDerbi/asalichoice/blob/main/deploy/config-templates/env.api.env.sample),
[`env.site.env.sample`](https://github.com/SumitDerbi/asalichoice/blob/main/deploy/config-templates/env.site.env.sample)).

## .htaccess templates

Committed under
[`deploy/htaccess/`](https://github.com/SumitDerbi/asalichoice/tree/main/deploy/htaccess)
and copied automatically by `deploy.sh` when present:

| File                  | Installed to                                                                                |
| --------------------- | ------------------------------------------------------------------------------------------- |
| `admin-ui.htaccess`   | `APP_DIR_ADMIN_UI/.htaccess` — SPA fallback, fingerprinted-asset caching, security headers. |
| `storefront.htaccess` | `APP_DIR_STOREFRONT/.htaccess` — HTTPS redirect, cache hints, security headers.             |
| `backend.htaccess`    | `APP_DIR_BACKEND/.htaccess` — HTTPS redirect, deny `.env`/`.py`/etc.                        |

> **Do not delete the `PassengerAppRoot` block** that cPanel writes above
> these directives — Apache needs it to route requests to the WSGI app.

## First-time bootstrap

After the cPanel prerequisites are in place:

```bash
ssh USER@HOST
cd ~/repositories/<env_name>
chmod +x deploy.sh
./deploy.sh main <env_name>
```

The first run will:

1. Create `~/backups/<env>/` if missing.
2. Hard-reset the working tree to `origin/<branch>`.
3. Build the admin-ui and the storefront CSS bundle.
4. Run all pending migrations on both apps.
5. Collect static and trigger a Passenger restart.

## Rollback

`deploy.sh` does **not** auto-restore — failure halts the pipeline and
prints the backup path. To roll back manually:

```bash
# 1. Pick the backup
ls -lt ~/backups/<env>/

# 2. Restore the failing app dir (example: backend)
BACKUP=~/backups/<env>/backup_YYYYMMDD_HHMMSS
rsync -a --delete $BACKUP/asalichoice_api/ ~/asalichoice_api/

# 3. (If a migration was the culprit) restore the DB dump
mysql -u USER -p DBNAME < $BACKUP/<dbname>.sql

# 4. Restart Passenger
touch ~/asalichoice_api/tmp/restart.txt
touch ~/public_html/<env>/tmp/restart.txt
```

## Status

`deploy.sh` and the .htaccess + config templates ship in [plan 012](https://github.com/SumitDerbi/asalichoice/blob/main/plans/phase-0-foundation/012-deploy-sh.md).
Staging verification (live dry-run with rollback test) is tracked in
`plans/_state.md`.
