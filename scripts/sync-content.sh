#!/usr/bin/env bash
# Pulls content/*.json from the mobile app repo (the single source of truth
# for PlainWater's 78 features) into a local, gitignored staging dir. Run
# this before build-modules.py whenever the mobile repo's content changes.
#
# Assumes the standard sibling-checkout layout used on this machine:
#   ~/coding_common/os/plainwater-site   (this repo)
#   ~/coding_common/pvt/plainwater       (the mobile app repo, content/*.json)
# Override with PLAINWATER_MOBILE_REPO if your checkout differs.
set -euo pipefail
cd "$(dirname "$0")/.."

SRC="${PLAINWATER_MOBILE_REPO:-../../pvt/plainwater}/content"
DEST=".content-src"

if [ ! -d "$SRC" ]; then
  echo "error: mobile repo content/ not found at $SRC" >&2
  echo "set PLAINWATER_MOBILE_REPO to the plainwater mobile repo's path" >&2
  exit 1
fi

rm -rf "$DEST"
mkdir -p "$DEST"
cp "$SRC"/module-*.json "$DEST"/

echo "Synced $(ls "$DEST"/module-*.json | wc -l | tr -d ' ') module files into $DEST/ (gitignored, build input only)."
echo "Next: python3 scripts/build-modules.py"
