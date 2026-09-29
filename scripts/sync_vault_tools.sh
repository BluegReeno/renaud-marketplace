#!/usr/bin/env bash
# Sync jobsearch-vault's scripts into the read-only mirror on the mounted Synology folder.
#
# A cloud session linked to the Mac reaches the vault through `device_bash`, which runs on the
# Mac and cannot see the plugin's own (cloud-side) scripts. It runs the copy kept under
# `<mount>/_tools/jobsearch-vault/scripts/` instead, and compares that copy's VERSION file with
# the running plugin version to flag a stale mirror (see jobsearch-vault SKILL.md, Case A).
#
# Run this AFTER a jobsearch release is merged, from an up-to-date main — never from a feature
# branch: the mirror is what live sessions execute, so it must only ever hold reviewed code.
# That is why this is not a step of release.sh, which runs on the feature branch before review.
#
# Usage: ./scripts/sync_vault_tools.sh
#   JOBSEARCH_VAULT_SYNOLOGY_MOUNT  override the mounted folder
#                                   (default: ~/Library/CloudStorage/SynologyDrive-MyAssistant)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$REPO_ROOT/plugins/jobsearch/skills/jobsearch-vault/scripts"
PLUGIN_JSON="$REPO_ROOT/plugins/jobsearch/.claude-plugin/plugin.json"
MOUNT="${JOBSEARCH_VAULT_SYNOLOGY_MOUNT:-$HOME/Library/CloudStorage/SynologyDrive-MyAssistant}"
DEST="$MOUNT/_tools/jobsearch-vault/scripts"

die() { echo "ERROR    $*" >&2; exit 1; }

BRANCH="$(git -C "$REPO_ROOT" branch --show-current)"
[ "$BRANCH" = "main" ] || die "on branch '$BRANCH' — sync only from main, after the release is merged"
[ -z "$(git -C "$REPO_ROOT" status --porcelain)" ] || die "working tree not clean — commit or discard first"
[ -d "$MOUNT" ] || die "mounted folder not found: $MOUNT (set JOBSEARCH_VAULT_SYNOLOGY_MOUNT)"

VERSION="$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['version'])" "$PLUGIN_JSON")"

# Replace the mirror wholesale so a script deleted from the plugin disappears from it too.
mkdir -p "$DEST"
find "$DEST" -mindepth 1 -delete
find "$SRC" -maxdepth 1 -type f -name '*.py' -exec cp {} "$DEST/" \;
echo "$VERSION" > "$DEST/VERSION"

echo "OK       synced jobsearch-vault scripts to $DEST (VERSION $VERSION)"
