#!/usr/bin/env bash
# Fail if the built frontend bundle leaks secrets. Run after `npm run build`.
set -uo pipefail
DIST="${1:-frontend/dist}"
[ -d "$DIST" ] || { echo "check-secrets: $DIST not found (build first)"; exit 2; }
fail=0

# 1. API-key patterns in the bundle
PATTERNS='sk-ant-[A-Za-z0-9_-]{10,}|sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{30,}|gho_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|AIza[0-9A-Za-z_-]{35}|-----BEGIN [A-Z ]*PRIVATE KEY-----'
if grep -rEnI --exclude='*.map' -e "$PATTERNS" "$DIST"; then
  echo "check-secrets: API-key pattern found in $DIST"; fail=1
fi

# 2. VITE_* vars named KEY/SECRET/TOKEN (would be inlined into the bundle)
NAME='VITE_[A-Z0-9_]*(KEY|SECRET|TOKEN)[A-Z0-9_]*'
if grep -rEnoI --exclude='*.map' -e "$NAME" "$DIST"; then
  echo "check-secrets: secret-like VITE_ var referenced in $DIST"; fail=1
fi
envs=$(ls frontend/.env* .env* 2>/dev/null | grep -v '\.example$' || true)
if [ -n "$envs" ] && grep -EnH "^\s*(export\s+)?$NAME\s*=" $envs; then
  echo "check-secrets: secret-like VITE_ var defined in env file"; fail=1
fi

[ "$fail" -eq 0 ] && echo "check-secrets: ok"
exit "$fail"
