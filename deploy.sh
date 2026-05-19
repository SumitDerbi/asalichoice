#!/bin/bash
#===============================================================================
# AsliChoice — cPanel + Phusion Passenger deployment script
#
# Two Python apps (backend API + Wagtail storefront) + one static SPA
# (admin-ui built React assets served via .htaccess).
#
# Usage:  ./deploy.sh [branch_name] [env_name]
# Example: ./deploy.sh main staging
#
#   - Config loaded from: ~/deploy_config/<env_name>/<env_name>.config
#   - Env files  loaded from:
#       ~/deploy_config/<env_name>/<env_name>.api.env
#       ~/deploy_config/<env_name>/<env_name>.site.env
#
# See deploy/config-templates/ for sample config + env files.
#===============================================================================

set -euo pipefail

#-------------------------------------------------------------------------------
# Colors / Logging
#-------------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()    { echo -e "${BLUE}[INFO]${NC}    $(date '+%F %T') - $1"; }
log_success() { echo -e "${GREEN}[OK]${NC}      $(date '+%F %T') - $1"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC}    $(date '+%F %T') - $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC}   $(date '+%F %T') - $1"; }

cleanup_on_error() {
    log_error "Deployment failed! See output above."
    if [ -n "${BACKUP_DIR:-}" ] && [ -d "$BACKUP_DIR" ]; then
        log_warn  "A backup exists at: $BACKUP_DIR"
        log_warn  "Restore manually if a service is broken."
    fi
    exit 1
}
trap cleanup_on_error ERR

#-------------------------------------------------------------------------------
# Arguments
#-------------------------------------------------------------------------------
DEFAULT_BRANCH="main"
DEFAULT_ENV_NAME="staging"
DEPLOY_CONFIG_BASE="$HOME/deploy_config"

BRANCH="${1:-$DEFAULT_BRANCH}"
ENV_NAME="${2:-$DEFAULT_ENV_NAME}"

CONFIG_PATH="${DEPLOY_CONFIG_BASE}/${ENV_NAME}/${ENV_NAME}.config"
API_ENV_PATH_DEFAULT="${DEPLOY_CONFIG_BASE}/${ENV_NAME}/${ENV_NAME}.api.env"
SITE_ENV_PATH_DEFAULT="${DEPLOY_CONFIG_BASE}/${ENV_NAME}/${ENV_NAME}.site.env"

#-------------------------------------------------------------------------------
# Config loader
#-------------------------------------------------------------------------------
load_config() {
    if [ ! -f "$CONFIG_PATH" ]; then
        log_error "Config file not found at: $CONFIG_PATH"
        log_info  "See deploy/config-templates/env.config.sample for the required variables."
        exit 1
    fi

    log_info "Loading configuration from: $CONFIG_PATH"
    # Strip CRLF to be safe (config may have been edited on Windows).
    CONFIG_CONTENT=$(tr -d '\r' < "$CONFIG_PATH")
    # shellcheck disable=SC2086
    eval "$CONFIG_CONTENT"

    API_ENV_FILE="${API_ENV_FILE:-$API_ENV_PATH_DEFAULT}"
    SITE_ENV_FILE="${SITE_ENV_FILE:-$SITE_ENV_PATH_DEFAULT}"

    local required_vars=(
        "GIT_DIR"
        "APP_DIR_BACKEND"
        "APP_DIR_STOREFRONT"
        "APP_DIR_ADMIN_UI"
        "ACTIVATE_BACKEND"
        "ACTIVATE_STOREFRONT"
        "REQUIREMENTS_FILE_BACKEND"
        "REQUIREMENTS_FILE_STOREFRONT"
    )
    for var in "${required_vars[@]}"; do
        if [ -z "${!var:-}" ]; then
            log_error "Required variable '$var' is not set in $CONFIG_PATH"
            exit 1
        fi
    done

    GIT_DIR=$(eval echo "$GIT_DIR" | sed 's:/*$::')
    APP_DIR_BACKEND=$(eval echo "$APP_DIR_BACKEND" | sed 's:/*$::')
    APP_DIR_STOREFRONT=$(eval echo "$APP_DIR_STOREFRONT" | sed 's:/*$::')
    APP_DIR_ADMIN_UI=$(eval echo "$APP_DIR_ADMIN_UI" | sed 's:/*$::')
    ACTIVATE_BACKEND=$(eval echo "$ACTIVATE_BACKEND")
    ACTIVATE_STOREFRONT=$(eval echo "$ACTIVATE_STOREFRONT")
    DB_BACKUP_PATH=$(eval echo "${DB_BACKUP_PATH:-$HOME/backups/$ENV_NAME}" | sed 's:/*$::')
    STATIC_ROOT_BACKEND=$(eval echo "${STATIC_ROOT_BACKEND:-}" | sed 's:/*$::')
    STATIC_ROOT_STOREFRONT=$(eval echo "${STATIC_ROOT_STOREFRONT:-}" | sed 's:/*$::')
    MEDIA_ROOT=$(eval echo "${MEDIA_ROOT:-}" | sed 's:/*$::')
    NODE_BIN=$(eval echo "${NODE_BIN:-}" | sed 's:/*$::')
    API_ENV_FILE=$(eval echo "$API_ENV_FILE")
    SITE_ENV_FILE=$(eval echo "$SITE_ENV_FILE")
    HEALTHCHECK_BACKEND_URL="${HEALTHCHECK_BACKEND_URL:-}"
    HEALTHCHECK_STOREFRONT_URL="${HEALTHCHECK_STOREFRONT_URL:-}"
    DJANGO_SETTINGS_BACKEND="${DJANGO_SETTINGS_BACKEND:-config.settings.production}"
    DJANGO_SETTINGS_STOREFRONT="${DJANGO_SETTINGS_STOREFRONT:-config.settings.production}"

    log_info "GIT_DIR             = $GIT_DIR"
    log_info "APP_DIR_BACKEND     = $APP_DIR_BACKEND"
    log_info "APP_DIR_STOREFRONT  = $APP_DIR_STOREFRONT"
    log_info "APP_DIR_ADMIN_UI    = $APP_DIR_ADMIN_UI"
    log_success "Configuration loaded."
}

#-------------------------------------------------------------------------------
# Pre-flight checks
#-------------------------------------------------------------------------------
preflight_checks() {
    log_info "Running pre-flight checks..."

    command -v git     >/dev/null 2>&1 || { log_error "git not found in PATH";     exit 1; }
    command -v rsync   >/dev/null 2>&1 || { log_error "rsync not found in PATH";   exit 1; }

    [ -d "$GIT_DIR/.git" ]      || { log_error "$GIT_DIR is not a git repository"; exit 1; }
    [ -f "$ACTIVATE_BACKEND" ]  || { log_error "Backend venv activate missing: $ACTIVATE_BACKEND"; exit 1; }
    [ -f "$ACTIVATE_STOREFRONT" ] || { log_error "Storefront venv activate missing: $ACTIVATE_STOREFRONT"; exit 1; }

    if [ -n "$NODE_BIN" ] && [ ! -d "$NODE_BIN" ]; then
        log_warn "NODE_BIN set to '$NODE_BIN' but directory does not exist."
    fi

    [ -f "$API_ENV_FILE" ]  || log_warn "Backend .env not found: $API_ENV_FILE"
    [ -f "$SITE_ENV_FILE" ] || log_warn "Storefront .env not found: $SITE_ENV_FILE"

    log_success "Pre-flight checks passed."
}

#-------------------------------------------------------------------------------
# Backup
#-------------------------------------------------------------------------------
create_backup() {
    log_info "Creating backup..."

    TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
    BACKUP_DIR="${DB_BACKUP_PATH}/backup_${TIMESTAMP}"
    mkdir -p "$BACKUP_DIR"

    for dir in "$APP_DIR_BACKEND" "$APP_DIR_STOREFRONT" "$APP_DIR_ADMIN_UI"; do
        if [ -d "$dir" ]; then
            local name
            name=$(basename "$dir")
            log_info "  Backing up $dir → $BACKUP_DIR/${name}/"
            rsync -a --delete \
                --exclude='node_modules' \
                --exclude='__pycache__' \
                "$dir/" "$BACKUP_DIR/${name}/"
        fi
    done

    # MySQL dump using backend .env. Tolerate missing keys (|| true) so the
    # pipeline failure under `set -e` / pipefail doesn't kill the deploy.
    # Accept both DATABASE_* and DB_* prefixes for compatibility.
    if [ -f "$API_ENV_FILE" ] && command -v mysqldump >/dev/null 2>&1; then
        local DB_NAME DB_USER DB_PASS DB_HOST
        DB_NAME=$( { grep -sE '^(DATABASE_NAME|DB_NAME)='         "$API_ENV_FILE" || true; } | head -n1 | cut -d'=' -f2- | tr -d '"' | tr -d "'")
        DB_USER=$( { grep -sE '^(DATABASE_USER|DB_USER)='         "$API_ENV_FILE" || true; } | head -n1 | cut -d'=' -f2- | tr -d '"' | tr -d "'")
        DB_PASS=$( { grep -sE '^(DATABASE_PASSWORD|DB_PASSWORD)=' "$API_ENV_FILE" || true; } | head -n1 | cut -d'=' -f2- | tr -d '"' | tr -d "'")
        DB_HOST=$( { grep -sE '^(DATABASE_HOST|DB_HOST)='         "$API_ENV_FILE" || true; } | head -n1 | cut -d'=' -f2- | tr -d '"' | tr -d "'")
        DB_HOST="${DB_HOST:-localhost}"

        if [ -n "$DB_NAME" ] && [ -n "$DB_USER" ]; then
            log_info "  Dumping MySQL database '$DB_NAME'..."
            if mysqldump -u "$DB_USER" -p"$DB_PASS" -h "$DB_HOST" "$DB_NAME" \
                > "$BACKUP_DIR/${DB_NAME}.sql" 2>/dev/null; then
                log_success "  Database dumped to $BACKUP_DIR/${DB_NAME}.sql"
            else
                log_warn "  mysqldump failed — continuing without DB backup."
                rm -f "$BACKUP_DIR/${DB_NAME}.sql"
            fi
        fi
    else
        log_warn "  Skipping DB dump (no .env or mysqldump unavailable)."
    fi

    # Rotate: keep last 5.
    log_info "  Pruning old backups (keep last 5)..."
    cd "$DB_BACKUP_PATH"
    # shellcheck disable=SC2012
    ls -1dt backup_*/ 2>/dev/null | tail -n +6 | xargs -r rm -rf

    log_success "Backup completed at: $BACKUP_DIR"
}

#-------------------------------------------------------------------------------
# Pull latest code
#-------------------------------------------------------------------------------
pull_latest_code() {
    log_info "Pulling latest code on branch '$BRANCH'..."
    cd "$GIT_DIR"
    git fetch --all --prune

    if ! git rev-parse --verify --quiet "origin/$BRANCH" >/dev/null; then
        log_error "Branch 'origin/$BRANCH' does not exist."
        git branch -a
        exit 1
    fi

    git checkout "$BRANCH"
    git reset --hard "origin/$BRANCH"
    LATEST_COMMIT=$(git log -1 --pretty=format:"%h - %s (%ci)")
    log_success "Code updated to: $LATEST_COMMIT"
}

#-------------------------------------------------------------------------------
# Build admin-UI (React + Vite)
#-------------------------------------------------------------------------------
build_admin_ui() {
    log_info "Building admin-ui..."

    # admin-ui is built locally and its dist/ is committed to the repo.
    # The server NEVER builds (cPanel shared hosting can't allocate WASM mem
    # for rollup). Set BUILD_ADMIN_UI=true in the config only if you ever
    # provision a host that can actually run the build.
    if [ "${BUILD_ADMIN_UI:-false}" = "false" ]; then
        log_info "  BUILD_ADMIN_UI=false → using committed admin-ui/dist."
        if [ ! -d "$GIT_DIR/admin-ui/dist" ] || [ ! -f "$GIT_DIR/admin-ui/dist/index.html" ]; then
            log_error "Committed admin-ui/dist is missing or empty."
            log_error "Run locally:  npm run build:admin-ui  &&  git add -f admin-ui/dist && git commit && git push"
            exit 1
        fi
    else
        local OLD_PATH="$PATH"
        if [ -n "$NODE_BIN" ] && [ -d "$NODE_BIN" ]; then
            export PATH="$NODE_BIN:$PATH"
        fi
        log_info "  Node: $(command -v node || echo 'not found') $(node --version 2>/dev/null || true)"
        log_info "  npm:  $(command -v npm  || echo 'not found') $(npm  --version 2>/dev/null || true)"

        cd "$GIT_DIR"
        # The repo declares `admin-ui` as an npm workspace at the root.
        # --ignore-scripts skips the root `prepare` -> husky hook (dev-only) so it
        # doesn't fail on the server where husky's binary isn't available.
        # --include=dev forces devDependencies (tsc, vite, vitest types) to install
        # even when the cPanel nodevenv sets NODE_ENV=production.
        # HUSKY=0 is belt-and-suspenders in case husky ever does run.
        HUSKY=0 NODE_ENV=development npm ci --include=dev --ignore-scripts --workspace admin-ui --include-workspace-root=false
        HUSKY=0 NODE_ENV=production  npm run build --workspace admin-ui

        export PATH="$OLD_PATH"
    fi

    mkdir -p "$APP_DIR_ADMIN_UI"
    rsync -a --delete \
        "$GIT_DIR/admin-ui/dist/" "$APP_DIR_ADMIN_UI/"

    # Ship the SPA .htaccess if one is committed.
    if [ -f "$GIT_DIR/deploy/htaccess/admin-ui.htaccess" ]; then
        cp "$GIT_DIR/deploy/htaccess/admin-ui.htaccess" "$APP_DIR_ADMIN_UI/.htaccess"
        log_info "  Installed admin-ui .htaccess"
    fi

    log_success "admin-ui synced to $APP_DIR_ADMIN_UI"
}

#-------------------------------------------------------------------------------
# Sync helper for Python app dirs
#-------------------------------------------------------------------------------
sync_python_app() {
    local SRC="$1"
    local DEST="$2"
    local NAME="$3"

    log_info "  Syncing $NAME: $SRC → $DEST"
    mkdir -p "$DEST"
    rsync -a --delete \
        --exclude='.git' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.env' \
        --exclude='.htaccess' \
        --exclude='db.sqlite3' \
        --exclude='media/' \
        --exclude='node_modules/' \
        --exclude='staticfiles/' \
        "$SRC/" "$DEST/"
    chmod 711 "$DEST"
}

#-------------------------------------------------------------------------------
# Deploy backend (Django REST API)
#-------------------------------------------------------------------------------
deploy_backend() {
    log_info "Deploying backend..."

    sync_python_app "$GIT_DIR/backend" "$APP_DIR_BACKEND" "backend"

    if [ -f "$API_ENV_FILE" ]; then
        cp "$API_ENV_FILE" "$APP_DIR_BACKEND/.env"
        log_info "  Installed backend .env"
    fi
    if [ -f "$GIT_DIR/deploy/htaccess/backend.htaccess" ]; then
        cp "$GIT_DIR/deploy/htaccess/backend.htaccess" "$APP_DIR_BACKEND/.htaccess"
        log_info "  Installed backend .htaccess"
    fi

    # shellcheck disable=SC1090
    source "$ACTIVATE_BACKEND"
    export DJANGO_SETTINGS_MODULE="$DJANGO_SETTINGS_BACKEND"
    log_info "  Python: $(python --version)  ($(which python))"
    log_info "  Settings: $DJANGO_SETTINGS_MODULE"

    cd "$APP_DIR_BACKEND"
    pip install --upgrade pip
    pip install -r "$REQUIREMENTS_FILE_BACKEND"
    python manage.py migrate --noinput
    if [ -n "$STATIC_ROOT_BACKEND" ]; then
        python manage.py collectstatic --noinput
    else
        log_warn "  STATIC_ROOT_BACKEND not set — skipping collectstatic"
    fi

    deactivate || true
    log_success "Backend deployed."
}

#-------------------------------------------------------------------------------
# Deploy storefront (Wagtail)
#-------------------------------------------------------------------------------
deploy_storefront() {
    log_info "Deploying storefront..."

    # Build Tailwind CSS bundle BEFORE rsync so the output lands in the synced dir.
    if [ -d "$GIT_DIR/storefront/theme/static_src" ]; then
        log_info "  Building Tailwind CSS..."
        local OLD_PATH="$PATH"
        if [ -n "$NODE_BIN" ] && [ -d "$NODE_BIN" ]; then
            export PATH="$NODE_BIN:$PATH"
        fi
        # storefront tailwind has no package-lock committed, so use `install`
        # instead of `ci`. Skip scripts/husky for the same reasons as admin-ui.
        # --include=dev forces tailwindcss + plugins (declared as devDependencies)
        # to install even when cPanel sets NODE_ENV=production.
        ( cd "$GIT_DIR/storefront/theme/static_src" \
            && HUSKY=0 NODE_ENV=development npm install --include=dev --ignore-scripts --no-audit --no-fund \
            && HUSKY=0 npm run tailwind:build )
        export PATH="$OLD_PATH"
    fi

    sync_python_app "$GIT_DIR/storefront" "$APP_DIR_STOREFRONT" "storefront"

    if [ -f "$SITE_ENV_FILE" ]; then
        cp "$SITE_ENV_FILE" "$APP_DIR_STOREFRONT/.env"
        log_info "  Installed storefront .env"
    fi
    if [ -f "$GIT_DIR/deploy/htaccess/storefront.htaccess" ]; then
        cp "$GIT_DIR/deploy/htaccess/storefront.htaccess" "$APP_DIR_STOREFRONT/.htaccess"
        log_info "  Installed storefront .htaccess"
    fi

    # shellcheck disable=SC1090
    source "$ACTIVATE_STOREFRONT"
    export DJANGO_SETTINGS_MODULE="$DJANGO_SETTINGS_STOREFRONT"
    log_info "  Python: $(python --version)  ($(which python))"
    log_info "  Settings: $DJANGO_SETTINGS_MODULE"

    cd "$APP_DIR_STOREFRONT"
    pip install --upgrade pip
    pip install -r "$REQUIREMENTS_FILE_STOREFRONT"
    python manage.py migrate --noinput
    if [ -n "$STATIC_ROOT_STOREFRONT" ]; then
        python manage.py collectstatic --noinput
    else
        log_warn "  STATIC_ROOT_STOREFRONT not set — skipping collectstatic"
    fi

    deactivate || true
    log_success "Storefront deployed."
}

#-------------------------------------------------------------------------------
# Restart Passenger apps
#-------------------------------------------------------------------------------
restart_apps() {
    log_info "Restarting Passenger apps..."
    for d in "$APP_DIR_BACKEND" "$APP_DIR_STOREFRONT"; do
        mkdir -p "$d/tmp"
        touch "$d/tmp/restart.txt"
        log_info "  Touched $d/tmp/restart.txt"
    done
    log_success "Restart signal sent."
}

#-------------------------------------------------------------------------------
# Health checks
#-------------------------------------------------------------------------------
health_checks() {
    if [ -z "$HEALTHCHECK_BACKEND_URL" ] && [ -z "$HEALTHCHECK_STOREFRONT_URL" ]; then
        log_warn "No HEALTHCHECK_* URLs configured — skipping health checks."
        return
    fi

    log_info "Running health checks (Passenger may need a few seconds to boot)..."
    sleep 5

    local failed=0
    if [ -n "$HEALTHCHECK_BACKEND_URL" ]; then
        log_info "  GET $HEALTHCHECK_BACKEND_URL"
        if curl -fsSL --max-time 15 "$HEALTHCHECK_BACKEND_URL" >/dev/null; then
            log_success "  Backend healthy."
        else
            log_error  "  Backend health check FAILED"
            failed=1
        fi
    fi
    if [ -n "$HEALTHCHECK_STOREFRONT_URL" ]; then
        log_info "  GET $HEALTHCHECK_STOREFRONT_URL"
        if curl -fsSL --max-time 15 "$HEALTHCHECK_STOREFRONT_URL" >/dev/null; then
            log_success "  Storefront healthy."
        else
            log_error  "  Storefront health check FAILED"
            failed=1
        fi
    fi

    if [ "$failed" -ne 0 ]; then
        log_error "One or more health checks failed. See backup at: ${BACKUP_DIR:-N/A}"
        exit 1
    fi
}

#-------------------------------------------------------------------------------
# Summary
#-------------------------------------------------------------------------------
print_summary() {
    echo ""
    echo "============================================================"
    echo -e "${GREEN}   AsliChoice deploy: SUCCESS${NC}"
    echo "============================================================"
    echo -e "  Environment:  ${YELLOW}$ENV_NAME${NC}"
    echo -e "  Branch:       ${YELLOW}$BRANCH${NC}"
    echo -e "  Commit:       ${YELLOW}${LATEST_COMMIT:-N/A}${NC}"
    echo -e "  Backend:      ${YELLOW}$APP_DIR_BACKEND${NC}"
    echo -e "  Storefront:   ${YELLOW}$APP_DIR_STOREFRONT${NC}"
    echo -e "  Admin UI:     ${YELLOW}$APP_DIR_ADMIN_UI${NC}"
    echo -e "  Backup:       ${YELLOW}${BACKUP_DIR:-N/A}${NC}"
    echo -e "  Timestamp:    ${YELLOW}$(date '+%F %T')${NC}"
    echo "============================================================"
    echo ""
}

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------
main() {
    echo ""
    echo "============================================================"
    echo -e "${BLUE}   AsliChoice — cPanel deploy${NC}"
    echo "============================================================"
    echo -e "  Environment: ${YELLOW}$ENV_NAME${NC}"
    echo -e "  Branch:      ${YELLOW}$BRANCH${NC}"
    echo -e "  Config:      ${YELLOW}$CONFIG_PATH${NC}"
    echo "============================================================"
    echo ""

    load_config
    preflight_checks
    create_backup
    pull_latest_code
    build_admin_ui
    deploy_backend
    deploy_storefront
    restart_apps
    health_checks
    print_summary
}

main
