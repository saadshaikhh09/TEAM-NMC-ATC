#!/usr/bin/env bash
# Boots the whole demo stack (API + site + app) with one command.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_DIR="$REPO_ROOT/api"
SITE_DIR="$REPO_ROOT/web/site"
APP_DIR="$REPO_ROOT/web/app"
ENV_FILE="$REPO_ROOT/.env"

API_PORT=8000
SITE_PORT=5173
APP_PORT=5174
API_URL="http://localhost:${API_PORT}"
SITE_URL="http://localhost:${SITE_PORT}"
APP_URL="http://localhost:${APP_PORT}"

DEMO_EMAIL="demo@atc.local"
DEMO_PASSWORD="DemoPass!2026"

MODE="all" # all | api | web

# ---------- output helpers ----------
if [[ -t 1 ]]; then
  C_RED=$'\033[31m'; C_GREEN=$'\033[32m'; C_YELLOW=$'\033[33m'; C_BLUE=$'\033[34m'; C_RESET=$'\033[0m'
else
  C_RED=""; C_GREEN=""; C_YELLOW=""; C_BLUE=""; C_RESET=""
fi
info()  { printf '%s[start]%s %s\n' "$C_BLUE" "$C_RESET" "$*"; }
ok()    { printf '%s[start]%s %s\n' "$C_GREEN" "$C_RESET" "$*"; }
warn()  { printf '%s[start]%s %s\n' "$C_YELLOW" "$C_RESET" "$*" >&2; }
err()   { printf '%s[start]%s %s\n' "$C_RED" "$C_RESET" "$*" >&2; }

usage() {
  cat <<EOF
Usage: ./start.sh [--api-only|--web-only] [--help]

Boots the demo stack with one command:
  - FastAPI backend  (api/.venv/bin/uvicorn)        :${API_PORT}
  - Public site      (web/site, vite dev)           :${SITE_PORT}
  - Authenticated app (web/app, vite dev)           :${APP_PORT}

Options:
  --api-only   Start only the FastAPI backend.
  --web-only   Start only the site + app dev servers (skips API + DB checks).
  --help       Show this help and exit.

Ctrl-C stops everything and frees all ports.
EOF
}

for arg in "$@"; do
  case "$arg" in
    --api-only) MODE="api" ;;
    --web-only) MODE="web" ;;
    --help|-h) usage; exit 0 ;;
    *) err "Unknown option: $arg"; usage; exit 1 ;;
  esac
done

WANT_API=0; WANT_WEB=0
[[ "$MODE" == "all" || "$MODE" == "api" ]] && WANT_API=1
[[ "$MODE" == "all" || "$MODE" == "web" ]] && WANT_WEB=1

# ---------- env ----------
if [[ -f "$ENV_FILE" ]]; then
  info "Loading environment from .env"
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
else
  warn ".env not found at $ENV_FILE — using built-in defaults. Never auto-creating one."
fi
DATABASE_URL="${DATABASE_URL:-postgresql://concierge:concierge@localhost:5432/concierge}"

# ---------- preflight ----------
FAILED=0

check_api_venv() {
  if [[ ! -x "$API_DIR/.venv/bin/uvicorn" ]]; then
    err "api/.venv is missing (no api/.venv/bin/uvicorn)."
    err "  Fix: cd api && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
    return 1
  fi
  ok "api/.venv found."
}

check_node_modules() {
  local dir="$1" name="$2"
  if [[ -d "$dir/node_modules" ]]; then
    ok "$name node_modules present."
    return 0
  fi
  warn "$name node_modules missing — installing now (npm install in $dir)..."
  if (cd "$dir" && npm install); then
    ok "$name dependencies installed."
  else
    err "$name npm install failed."
    err "  Fix: cd ${dir#$REPO_ROOT/} && npm install"
    return 1
  fi
}

check_port_free() {
  local port="$1" name="$2"
  local pid
  pid=$(lsof -ti tcp:"$port" -sTCP:LISTEN 2>/dev/null | head -n1)
  if [[ -n "$pid" ]]; then
    local proc
    proc=$(ps -p "$pid" -o comm= 2>/dev/null | xargs -0 2>/dev/null)
    err "Port $port ($name) is already in use by PID $pid ($proc)."
    err "  Fix: kill $pid   (or: lsof -i :$port to inspect first)"
    return 1
  fi
  ok "Port $port ($name) is free."
}

check_postgres() {
  local url="$DATABASE_URL"
  if [[ ! "$url" =~ ^postgres(ql)?://([^:@]+):([^@]*)@([^:/]+):([0-9]+)/([A-Za-z0-9_]+)$ ]]; then
    warn "Could not parse DATABASE_URL, falling back to concierge@localhost:5432/concierge for checks."
    local pg_user="concierge" pg_pass="concierge" pg_host="localhost" pg_port="5432" pg_db="concierge"
  else
    local pg_user="${BASH_REMATCH[2]}" pg_pass="${BASH_REMATCH[3]}" pg_host="${BASH_REMATCH[4]}" pg_port="${BASH_REMATCH[5]}" pg_db="${BASH_REMATCH[6]}"
  fi

  if ! pg_isready -h "$pg_host" -p "$pg_port" -U "$pg_user" >/dev/null 2>&1; then
    err "PostgreSQL is not reachable at ${pg_host}:${pg_port}."
    err "  Fix: brew services start postgresql@16   (or) docker compose up -d"
    return 1
  fi
  ok "PostgreSQL is reachable at ${pg_host}:${pg_port}."

  local missing
  missing=$(PGPASSWORD="$pg_pass" psql -h "$pg_host" -p "$pg_port" -U "$pg_user" -d "$pg_db" -tAc \
    "select coalesce(nullif(to_regclass('public.api_quota')::text, '') is null, true)::int
       + coalesce(nullif(to_regclass('llm_cache.responses')::text, '') is null, true)::int
       + coalesce(nullif(to_regclass('public.users')::text, '') is null, true)::int;" 2>/dev/null)
  if [[ -z "$missing" || "$missing" != "0" ]]; then
    err "Database is reachable but migrations are not (fully) applied."
    err "  Fix: make reset"
    return 1
  fi
  ok "Migrations are applied."
}

info "Running preflight checks (mode: $MODE)..."

if [[ "$WANT_API" -eq 1 ]]; then
  check_api_venv || FAILED=1
  check_postgres || FAILED=1
  check_port_free "$API_PORT" "api" || FAILED=1
fi

if [[ "$WANT_WEB" -eq 1 ]]; then
  check_node_modules "$SITE_DIR" "web/site" || FAILED=1
  check_node_modules "$APP_DIR" "web/app" || FAILED=1
  check_port_free "$SITE_PORT" "site" || FAILED=1
  check_port_free "$APP_PORT" "app" || FAILED=1
fi

if [[ "$FAILED" -eq 1 ]]; then
  err "Preflight checks failed. Fix the issues above and re-run ./start.sh."
  exit 1
fi

# ---------- process management ----------
# Note: macOS ships bash 3.2 (no associative arrays), so service PIDs are
# tracked with one plain variable per service instead of `declare -A`.
LOG_DIR="$(mktemp -d "${TMPDIR:-/tmp}/travel-concierge-start.XXXXXX")"
API_PID=""
SITE_PID=""
APP_PID=""
STARTED_SERVICES=""
TAIL_PIDS=()
CLEANING_UP=0

# Sends a signal to a PID and everything descended from it (npm -> vite,
# uvicorn --reload -> its worker, etc). Do NOT rely on process-group kills
# here: this script's PID is only its own process-group leader when it is
# run as an interactive terminal's foreground job, which is not guaranteed
# (e.g. when launched via `make dev`, `nohup`, or a subshell).
kill_tree() {
  local pid="$1" sig="$2" child
  for child in $(pgrep -P "$pid" 2>/dev/null); do
    kill_tree "$child" "$sig"
  done
  kill -"$sig" "$pid" 2>/dev/null || true
}

cleanup() {
  if [[ "$CLEANING_UP" -eq 1 ]]; then return; fi
  CLEANING_UP=1
  trap '' TERM INT
  trap - EXIT
  echo ""
  info "Shutting down..."

  local pid
  for pid in "$API_PID" "$SITE_PID" "$APP_PID" "${TAIL_PIDS[@]:-}"; do
    [[ -n "$pid" ]] && kill_tree "$pid" TERM
  done

  local i alive
  for i in 1 2 3 4 5 6 7 8 9 10; do
    sleep 0.3
    alive=0
    for pid in "$API_PID" "$SITE_PID" "$APP_PID"; do
      [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null && alive=1
    done
    [[ "$alive" -eq 0 ]] && break
  done
  for pid in "$API_PID" "$SITE_PID" "$APP_PID" "${TAIL_PIDS[@]:-}"; do
    [[ -n "$pid" ]] && kill_tree "$pid" KILL
  done
  for pid in "$API_PID" "$SITE_PID" "$APP_PID" "${TAIL_PIDS[@]:-}"; do
    [[ -n "$pid" ]] && wait "$pid" 2>/dev/null
  done

  local port leftover
  for port in "$API_PORT" "$SITE_PORT" "$APP_PORT"; do
    leftover=$(lsof -ti tcp:"$port" 2>/dev/null || true)
    if [[ -n "$leftover" ]]; then
      # shellcheck disable=SC2086
      kill -KILL $leftover 2>/dev/null || true
    fi
  done

  rm -rf "$LOG_DIR" 2>/dev/null || true
  ok "All services stopped, ports released."
}
trap cleanup EXIT
trap 'cleanup; exit 130' INT
trap 'cleanup; exit 143' TERM

start_service() {
  local name="$1" dir="$2"; shift 2
  ( cd "$dir" && exec "$@" ) > "$LOG_DIR/$name.log" 2>&1 &
  local pid=$!
  disown "$pid" 2>/dev/null || true
  case "$name" in
    api) API_PID="$pid" ;;
    site) SITE_PID="$pid" ;;
    app) APP_PID="$pid" ;;
  esac
  STARTED_SERVICES="$STARTED_SERVICES $name"
  ( tail -n +1 -F "$LOG_DIR/$name.log" 2>/dev/null | sed -u "s/^/[$name] /" ) &
  disown "$!" 2>/dev/null || true
  TAIL_PIDS+=("$!")
}

if [[ "$WANT_API" -eq 1 ]]; then
  info "Starting API on :$API_PORT..."
  start_service "api" "$API_DIR" "$API_DIR/.venv/bin/uvicorn" main:app --reload --port "$API_PORT"
fi

if [[ "$WANT_WEB" -eq 1 ]]; then
  info "Starting site on :$SITE_PORT..."
  start_service "site" "$SITE_DIR" npm run dev

  info "Starting app on :$APP_PORT..."
  start_service "app" "$APP_DIR" npm run dev
fi

# ---------- readiness ----------
service_alive() {
  local pid=""
  case "$1" in
    api) pid="$API_PID" ;;
    site) pid="$SITE_PID" ;;
    app) pid="$APP_PID" ;;
  esac
  [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null
}

wait_for_url() {
  local name="$1" url="$2" max="$3" tries=0
  until curl -fsS "$url" >/dev/null 2>&1; do
    if ! service_alive "$name"; then
      err "[$name] process died during startup. Last log lines:"
      tail -n 20 "$LOG_DIR/$name.log" >&2 2>/dev/null
      return 1
    fi
    tries=$((tries + 1))
    if [[ "$tries" -ge "$max" ]]; then
      err "[$name] did not become ready within ${max}s (checked $url)."
      return 1
    fi
    sleep 1
  done
}

if [[ "$WANT_API" -eq 1 ]]; then
  info "Waiting for API health endpoint..."
  wait_for_url "api" "$API_URL/health" 60 || exit 1
  ok "API is healthy."
fi

if [[ "$WANT_WEB" -eq 1 ]]; then
  info "Waiting for site dev server..."
  wait_for_url "site" "$SITE_URL" 60 || exit 1
  ok "Site is up."

  info "Waiting for app dev server..."
  wait_for_url "app" "$APP_URL" 60 || exit 1
  ok "App is up."
fi

# ---------- ready ----------
echo ""
ok "Demo stack is ready."
echo ""
[[ "$WANT_WEB" -eq 1 ]] && printf '  Site   %s\n' "$SITE_URL"
[[ "$WANT_WEB" -eq 1 ]] && printf '  App    %s\n' "$APP_URL"
[[ "$WANT_API" -eq 1 ]] && printf '  API    %s/docs\n' "$API_URL"
if [[ "$WANT_API" -eq 1 ]]; then
  echo ""
  printf '  Demo login   %s / %s\n' "$DEMO_EMAIL" "$DEMO_PASSWORD"
fi
echo ""
info "Press Ctrl-C to stop everything."

# ---------- monitor ----------
while true; do
  for name in $STARTED_SERVICES; do
    if ! service_alive "$name"; then
      err "[$name] exited unexpectedly. Last log lines:"
      tail -n 20 "$LOG_DIR/$name.log" >&2 2>/dev/null
      exit 1
    fi
  done
  sleep 2
done
