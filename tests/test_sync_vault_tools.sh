#!/usr/bin/env bash
# Offline test for scripts/sync_vault_tools.sh.
#
# Builds a throwaway fixture repo (sync_vault_tools.sh derives REPO_ROOT from its own path, so a
# copy in the fixture's scripts/ operates on the fixture) and pins the three behaviours that
# matter: it syncs from a clean main, it refuses from any other branch without writing, and it
# fails on an absent mount.
#
# Usage: ./tests/test_sync_vault_tools.sh   (exit 0 = all pass, exit 1 = any failure)

set -uo pipefail

SRC_DIR="$(cd "$(dirname "$0")/../scripts" && pwd)"
ERRORS=0
PASS=0

FIXTURE="$(mktemp -d)"
MOUNT="$(mktemp -d)"
trap 'rm -rf "$FIXTURE" "$MOUNT"' EXIT

ok()   { echo "OK       $1"; PASS=$((PASS + 1)); }
fail() { echo "FAIL     $1"; ERRORS=$((ERRORS + 1)); }

build_fixture() {
  rm -rf "$FIXTURE" "$MOUNT"
  mkdir -p "$FIXTURE/scripts" "$FIXTURE/plugins/jobsearch/.claude-plugin" \
           "$FIXTURE/plugins/jobsearch/skills/jobsearch-vault/scripts" "$MOUNT"
  cp "$SRC_DIR/sync_vault_tools.sh" "$FIXTURE/scripts/"
  echo '{ "name": "jobsearch", "version": "0.3.0" }' \
    > "$FIXTURE/plugins/jobsearch/.claude-plugin/plugin.json"
  echo "print('dummy')" > "$FIXTURE/plugins/jobsearch/skills/jobsearch-vault/scripts/list_notes.py"
  git -C "$FIXTURE" init -q -b main
  git -C "$FIXTURE" config user.email test@example.com
  git -C "$FIXTURE" config user.name test
  git -C "$FIXTURE" add -A
  git -C "$FIXTURE" commit -qm init
}

run_sync() {
  JOBSEARCH_VAULT_SYNOLOGY_MOUNT="$1" bash "$FIXTURE/scripts/sync_vault_tools.sh" >/dev/null 2>&1
}

DEST_REL="_tools/jobsearch-vault/scripts"

# 1. Clean main: scripts copied, VERSION written, a stale file removed.
build_fixture
mkdir -p "$MOUNT/$DEST_REL" && echo old > "$MOUNT/$DEST_REL/removed_script.py"
if run_sync "$MOUNT" \
   && [ -f "$MOUNT/$DEST_REL/list_notes.py" ] \
   && [ "$(cat "$MOUNT/$DEST_REL/VERSION")" = "0.3.0" ] \
   && [ ! -e "$MOUNT/$DEST_REL/removed_script.py" ]; then
  ok "clean main — scripts + VERSION written, stale file removed"
else
  fail "clean main — sync did not produce the expected mirror"
fi

# 2. Feature branch: refused, nothing written.
build_fixture
git -C "$FIXTURE" checkout -qb fix/something
if ! run_sync "$MOUNT" && [ ! -e "$MOUNT/_tools" ]; then
  ok "feature branch — refused, nothing written"
else
  fail "feature branch — sync ran or wrote into the mount"
fi

# 3. Absent mount: fails.
build_fixture
if ! run_sync "$MOUNT/does-not-exist"; then
  ok "absent mount — fails"
else
  fail "absent mount — exited 0"
fi

echo "---"
echo "$PASS passed, $ERRORS failed"
[ "$ERRORS" -eq 0 ]
