#!/usr/bin/env bash
# Open a PR with test evidence in its body, scoped to what the PR changed.
#   scripts/pr-open.sh [--dry-run] [gh pr create args...]   (--title/--body/--body-file/--base honoured)
#   scripts/pr-open.sh --update <n> [--dry-run]              rewrite the evidence block of PR <n> after new pushes
# Env: SHOT_ROUTES="/notes,/chat" overrides the auto-derived screenshot routes.
# backend/ changed  -> ruff, mypy, pytest + regression vs base
# frontend/ changed -> eslint, tsc, vitest + regression vs base + before/after screenshots
set -uo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
OUT="$ROOT/.test-report"
START='<!-- evidence:start -->'
END='<!-- evidence:end -->'

DRY=0; UPDATE=""; BASE_BRANCH="main"; TITLE=""; BODY=""; BODY_FILE=""; PASS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY=1 ;;
    --update) UPDATE="$2"; shift ;;
    --base|-B) BASE_BRANCH="$2"; PASS+=("$1" "$2"); shift ;;
    --title|-t) TITLE="$2"; PASS+=("$1" "$2"); shift ;;
    --body|-b) BODY="$2"; shift ;;
    --body-file|-F) BODY_FILE="$2"; shift ;;
    *) PASS+=("$1") ;;
  esac
  shift
done

if [ -n "$UPDATE" ]; then
  BASE_BRANCH="$(gh pr view "$UPDATE" --json baseRefName -q .baseRefName)" || exit 1
fi
BASE_REF="origin/$BASE_BRANCH"
git fetch -q origin "$BASE_BRANCH" || true

CHANGED="$(git diff --name-only "$BASE_REF...HEAD")"
SUITES=""
echo "$CHANGED" | grep -q '^backend/' && SUITES="backend"
FE=0; echo "$CHANGED" | grep -q '^frontend/' && { FE=1; SUITES="$SUITES frontend"; }
SUITES="${SUITES# }"
mkdir -p "$OUT"

EVID="$OUT/evidence.md"
{
  echo "$START"
  if [ -z "$SUITES" ]; then
    echo "## Test results"
    echo
    echo "No backend/ or frontend/ changes vs \`$BASE_REF\`; suites not run."
  else
    SUITES="$SUITES" "$ROOT/scripts/test-report.sh" "$BASE_REF" >&2 || { echo "test-report failed" >&2; exit 1; }
    echo "## Test results"
    echo
    cat "$OUT/report.md"
  fi
  echo
  echo "## Screenshots"
  echo
  if [ "$FE" = 1 ]; then
    ROUTES="${SHOT_ROUTES:-$(echo "$CHANGED" | python3 "$ROOT/scripts/shot_routes.py")}"
    ROUTES="${ROUTES:-/}"
    if SHOT_ROUTES="$ROUTES" "$ROOT/scripts/ui-shots.sh" "$BASE_REF" >&2; then
      echo "Routes: \`$ROUTES\`"
      echo
      if [ "$DRY" = 0 ]; then
        BR="$(git rev-parse --abbrev-ref HEAD | tr '/' '-')"
        PREFIX="$("$ROOT/scripts/push-assets.sh" "$OUT/shots" "pr-$BR-$(git rev-parse --short HEAD)")" || PREFIX=""
      else
        PREFIX=""
      fi
      if [ -n "$PREFIX" ]; then
        sed "s#(shots/#($PREFIX/#g" "$OUT/shots.md"
        if [ "$(gh repo view --json isPrivate -q .isPrivate 2>/dev/null)" = true ]; then
          echo
          echo "_Repo is private: images render only for viewers logged in to GitHub with access (raw URLs)._"
        fi
      else
        cat "$OUT/shots.md"
        echo
        echo "_(dry run or upload failed: images are local under .test-report/shots/)_"
      fi
    else
      echo "_Screenshot run failed; see .test-report/shots-*.log_"
    fi
  else
    echo "N/A (no frontend/ changes)"
  fi
  echo "$END"
} > "$EVID"

if [ -n "$UPDATE" ]; then
  gh pr view "$UPDATE" --json body -q .body > "$OUT/old-body.md" || exit 1
  python3 - "$OUT/old-body.md" "$EVID" "$OUT/pr-body.md" <<'PY'
import sys
old, evid, out = (open(p).read() for p in sys.argv[1:4])
S, E = "<!-- evidence:start -->", "<!-- evidence:end -->"
evid = evid.strip()
if S in old and E in old:
    a, b = old.index(S), old.index(E) + len(E)
    new = old[:a] + evid + old[b:]
else:
    new = old.rstrip() + "\n\n" + evid + "\n"
open(sys.argv[3], "w").write(new)
PY
  if [ "$DRY" = 1 ]; then echo "dry run: $OUT/pr-body.md"; else gh pr edit "$UPDATE" --body-file "$OUT/pr-body.md"; fi
  exit $?
fi

# Summary: --body, --body-file, or commit subjects
if [ -n "$BODY_FILE" ]; then SUMMARY="$(cat "$BODY_FILE")"
elif [ -n "$BODY" ]; then SUMMARY="$BODY"
else SUMMARY="$(git log --format='- %s' "$BASE_REF..HEAD")"; fi

{
  echo "## Summary"
  echo
  echo "$SUMMARY"
  echo
  cat "$EVID"
  echo
  echo "## Flag"
  echo
  echo "Reviewers: block if evidence block above is missing/stale or lists newly failing tests."
} > "$OUT/pr-body.md"

if [ "$DRY" = 1 ]; then echo "dry run: $OUT/pr-body.md"; exit 0; fi
git rev-parse --abbrev-ref '@{u}' >/dev/null 2>&1 || git push -u origin HEAD || exit 1
if [ -z "$TITLE" ]; then PASS+=(--title "$(git log -1 --format=%s)"); fi
gh pr create --base "$BASE_BRANCH" --body-file "$OUT/pr-body.md" "${PASS[@]}"
