#!/usr/bin/env bash
# Push a directory of files to orphan branch test-evidence-assets under <dest>/ ; prints the raw URL prefix.
# Usage: scripts/push-assets.sh <src_dir> <dest_subdir>
set -euo pipefail
SRC="$1"; DEST="$2"
ROOT="$(git rev-parse --show-toplevel)"
BR="test-evidence-assets"
URL="$(git -C "$ROOT" remote get-url origin)"
SLUG="$(echo "$URL" | sed -E 's#^(git@github.com:|https://github.com/)##; s#\.git$##')"
TMP="$(mktemp -d "${TMPDIR:-/tmp}/assets.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT
git -C "$TMP" init -q
git -C "$TMP" remote add origin "$URL"
if git -C "$TMP" fetch -q --depth 1 origin "$BR" 2>/dev/null; then
  git -C "$TMP" checkout -q -b "$BR" FETCH_HEAD
else
  git -C "$TMP" checkout -q --orphan "$BR"
fi
rm -rf "${TMP:?}/$DEST"; mkdir -p "$TMP/$DEST"
cp -R "$SRC"/. "$TMP/$DEST"/
git -C "$TMP" add -A
if ! git -C "$TMP" diff --cached --quiet; then
  git -C "$TMP" -c user.name="test-evidence" -c user.email="test-evidence@users.noreply.github.com" commit -q -m "evidence: $DEST"
  git -C "$TMP" push -q origin "$BR"
fi
echo "https://raw.githubusercontent.com/$SLUG/$BR/$DEST"
