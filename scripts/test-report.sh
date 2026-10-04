#!/usr/bin/env bash
# Local test evidence: results table + regression diff vs base_ref -> .test-report/report.md
# Usage: [SUITES="backend frontend"] scripts/test-report.sh [base_ref=origin/main]
# SUITES scopes which halves run (default both). Marker-free body goes to report.md.
set -uo pipefail

BASE_REF="${1:-origin/main}"
SUITES="${SUITES:-backend frontend}"
ROOT="$(git rev-parse --show-toplevel)"
OUT="$ROOT/.test-report"
DIFF_PY="$ROOT/scripts/junit_diff.py"
mkdir -p "$OUT"

want() { case " $SUITES " in *" $1 "*) return 0 ;; esac; return 1; }

# .env: this checkout, else the main checkout (worktrees lack it)
ENV_FILE="$ROOT/.env"
if [ ! -f "$ENV_FILE" ]; then
  MAIN="$(cd "$(git rev-parse --git-common-dir)/.." && pwd)"
  ENV_FILE="$MAIN/.env"
  [ -f "$ENV_FILE" ] || ENV_FILE="$(cd "$MAIN/../../.." 2>/dev/null && pwd)/.env"
fi
[ -f "$ENV_FILE" ] || { echo "no .env found" >&2; exit 1; }
set -a; . "$ENV_FILE"; set +a
DB_PORT="${DB_PORT:-5432}"; REDIS_PORT="${REDIS_PORT:-6379}"
export TEST_DATABASE_URL="postgresql+psycopg://app:app@127.0.0.1:${DB_PORT}/app_test_report"
export REDIS_URL="redis://127.0.0.1:${REDIS_PORT}/0"
export DB_PORT REDIS_PORT

if want backend; then
  DB_CONTAINER="${DB_CONTAINER:-${PROJECT_NAME:-demo-idea}-db-1}"
  if ! docker exec "$DB_CONTAINER" psql -U app -d postgres -tAc "select 1 from pg_database where datname='app_test_report'" | grep -q 1; then
    docker exec "$DB_CONTAINER" psql -U app -d postgres -c "CREATE DATABASE app_test_report OWNER app" >/dev/null \
      || { echo "cannot create test db (is $DB_CONTAINER up?)" >&2; exit 1; }
  fi
fi

now() { python3 -c 'import time; print(f"{time.time():.3f}")'; }
elapsed() { python3 -c "print(f'{$2-$1:.1f}')"; }

# ensure_deps <tree>: install deps if missing (reuse head's node_modules when lockfile identical)
ensure_deps() {
  local t="$1"
  if want backend; then (cd "$t/backend" && uv sync --frozen -q) >&2 || true; fi
  if want frontend && [ ! -d "$t/frontend/node_modules" ]; then
    if [ "$t" != "$ROOT" ] && [ -d "$ROOT/frontend/node_modules" ] && cmp -s "$t/frontend/package-lock.json" "$ROOT/frontend/package-lock.json"; then
      ln -s "$ROOT/frontend/node_modules" "$t/frontend/node_modules"
    else
      (cd "$t/frontend" && npm ci --no-audit --no-fund --loglevel=error) >&2 || true
    fi
  fi
}

run_pytest() { (cd "$1/backend" && uv run pytest -q --junitxml="$2/backend.xml" >"$2/backend.log" 2>&1); }
run_vitest() { (cd "$1/frontend" && npx vitest run --reporter=default --reporter=junit --outputFile.junit="$2/frontend.xml" >"$2/frontend.log" 2>&1); }

ensure_deps "$ROOT"
HEAD_SHA="$(git rev-parse --short HEAD)"
HEAD_DIR="$OUT/head"; rm -rf "$HEAD_DIR"; mkdir -p "$HEAD_DIR"

ROWS=""
add_row() { # name rc time pass fail skip
  local st="PASS"; [ "$2" != 0 ] && st="FAIL"
  ROWS="$ROWS| $1 | $4 | $5 | $6 | ${3}s | $st |"$'\n'
}
test_suite() { # side name runner
  local side="$1" name="$2" runner="$3" s e rc p f k
  s=$(now); "$runner" "$ROOT" "$HEAD_DIR"; rc=$?; e=$(now)
  if [ -f "$HEAD_DIR/$side.xml" ]; then
    read -r p f k _ <<<"$(python3 "$DIFF_PY" summary "$HEAD_DIR/$side.xml")"
    [ "$rc" -ne 0 ] && [ "$f" = 0 ] && f="?"
  else
    p="?"; f="?"; k="?"; [ "$rc" = 0 ] && rc=1
  fi
  add_row "$name" "$rc" "$(elapsed "$s" "$e")" "$p" "$f" "$k"
}
lint_suite() { # name dir cmd...
  local name="$1" dir="$2" s e rc; shift 2
  s=$(now); (cd "$ROOT/$dir" && "$@" >"$HEAD_DIR/$name.log" 2>&1); rc=$?; e=$(now)
  add_row "$name" "$rc" "$(elapsed "$s" "$e")" - - -
}

if want backend; then
  test_suite backend "backend pytest" run_pytest
  lint_suite "backend ruff" backend uv run ruff check .
  lint_suite "backend mypy" backend uv run mypy app tests
fi
if want frontend; then
  test_suite frontend "frontend vitest" run_vitest
  lint_suite "frontend eslint" frontend npm run -s lint
  lint_suite "frontend tsc" frontend npm run -s typecheck
fi

# regression vs base
BASE_SHA="$(git rev-parse "$BASE_REF^{commit}")"
CACHE="$OUT/cache/$BASE_SHA"
need_base=0
for s in $SUITES; do [ -f "$CACHE/$s.xml" ] || need_base=1; done
if [ "$need_base" = 1 ]; then
  TMP="$(mktemp -d "${TMPDIR:-/tmp}/test-report.XXXXXX")"
  trap 'git -C "$ROOT" worktree remove --force "$TMP/base" >/dev/null 2>&1; rm -rf "$TMP"' EXIT
  git -C "$ROOT" worktree add --detach "$TMP/base" "$BASE_SHA" >/dev/null 2>&1 || echo "worktree add failed" >&2
  cp "$ENV_FILE" "$TMP/base/.env"
  ensure_deps "$TMP/base"
  mkdir -p "$TMP/out"
  want backend && run_pytest "$TMP/base" "$TMP/out"
  want frontend && run_vitest "$TMP/base" "$TMP/out"
  mkdir -p "$CACHE" "$OUT/base-logs"
  cp "$TMP/out/"*.xml "$CACHE/" 2>/dev/null
  cp "$TMP/out/"*.log "$OUT/base-logs/" 2>/dev/null
else
  echo "base ${BASE_SHA:0:7}: using cached JUnit" >&2
fi

REG=""
for s in $SUITES; do
  REG="$REG#### $s"$'\n'
  if [ -f "$CACHE/$s.xml" ] && [ -f "$HEAD_DIR/$s.xml" ]; then
    REG="$REG$(python3 "$DIFF_PY" diff "$CACHE/$s.xml" "$HEAD_DIR/$s.xml")"$'\n\n'
  else
    REG="${REG}_Diff unavailable: base or head run produced no JUnit (see .test-report/base-logs)_"$'\n\n'
  fi
done

{
  echo "head \`$HEAD_SHA\` vs base \`$BASE_REF\` (\`${BASE_SHA:0:7}\`), scope: $SUITES, generated locally $(date -u +%Y-%m-%dT%H:%MZ)"
  echo
  echo "#### Test results"
  echo
  echo "| suite | pass | fail | skip | time | status |"
  echo "|---|---|---|---|---|---|"
  printf '%s' "$ROWS"
  echo
  echo "### Regression vs $BASE_REF"
  echo
  printf '%s\n' "$REG"
} > "$OUT/report.md"

echo "wrote $OUT/report.md"
cat "$OUT/report.md"
