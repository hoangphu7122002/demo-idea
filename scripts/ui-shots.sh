#!/usr/bin/env bash
# Before/after UI screenshots -> .test-report/shots/{base,head}/<route>.png and .test-report/shots.md
# Usage: [SHOT_ROUTES="/notes,/chat"] scripts/ui-shots.sh [base_ref=origin/main]
# Needs only the frontend; API calls are not proxied, so screens show their empty/error state unless the
# backend is running on API_PORT (vite preview proxy is not configured; shots are of the static build).
set -uo pipefail

BASE_REF="${1:-origin/main}"
ROUTES="${SHOT_ROUTES:-/}"
ROOT="$(git rev-parse --show-toplevel)"
OUT="$ROOT/.test-report"
free_port() { python3 -c "import socket; s=socket.socket(); s.bind((\"127.0.0.1\",0)); print(s.getsockname()[1])"; }
BASE_PORT="${SHOT_BASE_PORT:-$(free_port)}"
HEAD_PORT="${SHOT_HEAD_PORT:-$(free_port)}"
BASE_SHA="$(git rev-parse "$BASE_REF^{commit}")"
mkdir -p "$OUT"
rm -rf "$OUT/shots"; mkdir -p "$OUT/shots/base" "$OUT/shots/head"

TMP="$(mktemp -d "${TMPDIR:-/tmp}/ui-shots.XXXXXX")"
PIDS=""
cleanup() {
  for p in $PIDS; do kill "$p" 2>/dev/null; done
  git -C "$ROOT" worktree remove --force "$TMP/base" >/dev/null 2>&1
  rm -rf "$TMP"
}
trap cleanup EXIT

deps() { # tree
  if [ ! -d "$1/frontend/node_modules" ]; then
    if [ "$1" != "$ROOT" ] && [ -d "$ROOT/frontend/node_modules" ] && cmp -s "$1/frontend/package-lock.json" "$ROOT/frontend/package-lock.json"; then
      ln -s "$ROOT/frontend/node_modules" "$1/frontend/node_modules"
    else
      (cd "$1/frontend" && npm ci --no-audit --no-fund --loglevel=error) >&2
    fi
  fi
}
build_serve() { # tree outdir port
  (cd "$1/frontend" && npx vite build --outDir "$2" --emptyOutDir >"$TMP/build-$3.log" 2>&1) || { echo "build failed ($1), see log:" >&2; tail -20 "$TMP/build-$3.log" >&2; return 1; }
  (cd "$1/frontend" && exec node node_modules/vite/bin/vite.js preview --outDir "$2" --host 127.0.0.1 --port "$3" --strictPort >"$TMP/preview-$3.log" 2>&1) &
  PIDS="$PIDS $!"
}
wait_port() { for _ in $(seq 1 60); do curl -sf "http://127.0.0.1:$1/" >/dev/null && return 0; sleep 1; done; return 1; }

deps "$ROOT"
(cd "$ROOT/frontend" && npx playwright install chromium >&2) || { echo "playwright browser install failed" >&2; exit 1; }

git -C "$ROOT" worktree add --detach "$TMP/base" "$BASE_SHA" >/dev/null 2>&1 || { echo "worktree add failed" >&2; exit 1; }
[ -f "$ROOT/.env" ] && cp "$ROOT/.env" "$TMP/base/.env"
deps "$TMP/base"

build_serve "$ROOT" "$TMP/dist-head" "$HEAD_PORT" || exit 1
build_serve "$TMP/base" "$TMP/dist-base" "$BASE_PORT" || exit 1
wait_port "$HEAD_PORT" && wait_port "$BASE_PORT" || { echo "preview did not start" >&2; exit 1; }

# Always run the spec from head's tree (base may predate it).
rc=0
for side in base head; do
  port="$HEAD_PORT"; [ "$side" = base ] && port="$BASE_PORT"
  (cd "$ROOT/frontend" && SHOT_ROUTES="$ROUTES" SHOT_BASE_URL="http://127.0.0.1:$port" SHOT_OUT_DIR="$OUT/shots/$side" \
    npx playwright test e2e/screenshots.spec.ts >"$OUT/shots-$side.log" 2>&1) || { echo "screenshots failed for $side (see $OUT/shots-$side.log)" >&2; rc=1; }
done

slug() { if [ "$1" = "/" ]; then echo index; else echo "$1" | sed -e 's#^/*##' -e 's#[^a-zA-Z0-9]\{1,\}#_#g'; fi; }
{
  echo "| route | before (base \`${BASE_SHA:0:7}\`) | after (head) |"
  echo "|---|---|---|"
  IFS=','; for r in $ROUTES; do
    s="$(slug "$(echo "$r" | tr -d ' ')")"
    echo "| \`$r\` | ![base $r](shots/base/$s.png) | ![head $r](shots/head/$s.png) |"
  done
} > "$OUT/shots.md"
echo "wrote $OUT/shots.md and $OUT/shots/"
exit $rc
