#!/bin/bash
# sync-deliverables-snapshot.sh — copy the canonical deliverables table from
# ~/ai-config (private) into tests/deliverables-snapshot.md (this repo, used by
# CI). Run this whenever the canonical table changes; commit the snapshot.
#
# The audit uses the in-repo snapshot by default (so CI works without access
# to ai-config). Local runs can use --table to override.

set -euo pipefail
SRC="$HOME/ai-config/darlison/coaching-deliverables.md"
DST="$(cd "$(dirname "$0")/.." && pwd)/tests/deliverables-snapshot.md"

if [[ ! -f "$SRC" ]]; then
  echo "ERROR: canonical table not found at $SRC" >&2
  exit 1
fi

cp "$SRC" "$DST"
echo "synced: $SRC -> $DST"
echo "        $(wc -c < "$DST" | tr -d ' ') bytes"

if git -C "$(dirname "$DST")" diff --quiet -- "$DST" 2>/dev/null; then
  echo "no changes"
else
  echo "changed — review with 'git diff $DST' and commit"
fi
