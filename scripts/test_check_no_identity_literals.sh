#!/usr/bin/env bash
# Offline tests for scripts/check_no_identity_literals.sh.
#
# Each case builds an isolated temp git repo (mirroring this repo's
# scripts/ + plugins/ layout) so the guard runs against synthetic fixtures —
# never against this repo's own tracked content.
#
# Run: bash scripts/test_check_no_identity_literals.sh

set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REAL_SCRIPT="$HERE/check_no_identity_literals.sh"

pass=0
fail=0
tmp=""

setup() {
  tmp=$(mktemp -d)
  mkdir -p "$tmp/scripts"
  cp "$REAL_SCRIPT" "$tmp/scripts/check_no_identity_literals.sh"
  (cd "$tmp" && git init -q && git config user.email test@test.local && git config user.name test)
}

teardown() {
  rm -rf "$tmp"
}

commit_file() {  # commit_file <relative-path> <content>
  mkdir -p "$(dirname "$tmp/$1")"
  printf '%s\n' "$2" > "$tmp/$1"
  (cd "$tmp" && git add "$1" && git commit -q -m "fixture: $1")
}

check() {  # check <name> <expected-exit>
  local name="$1" expected="$2" actual out
  out=$(cd "$tmp" && bash scripts/check_no_identity_literals.sh 2>&1)
  actual=$?
  if [ "$actual" -eq "$expected" ]; then
    printf 'PASS: %s\n' "$name"
    pass=$((pass + 1))
  else
    printf 'FAIL: %s (expected exit %s, got %s)\n%s\n' "$name" "$expected" "$actual" "$out"
    fail=$((fail + 1))
  fi
  teardown
}

# ── Case 1: committed calendar id → fails ───────────────────────────────────
setup
commit_file "plugins/briefing/skills/x/SKILL.md" \
  'call list_events(calendar_id="abc123@group.calendar.google.com")'
check "calendar id literal fails" 1

# ── Case 2: gitignored personal data file → passes (no false positive) ─────
setup
commit_file ".gitignore" "plugins/jobsearch/data/contact.local.json"
mkdir -p "$tmp/plugins/jobsearch/data"
printf '{"email": "totally-real@example-private.test"}\n' > "$tmp/plugins/jobsearch/data/contact.local.json"
check "gitignored personal data file does not fail" 0

# ── Case 3: clean tree → passes ─────────────────────────────────────────────
setup
commit_file "plugins/improve/skills/x/SKILL.md" \
  'call whoami() then use w.workspace_slug; contact support@example.com if needed'
check "clean tree passes" 0

# ── Case 4: committed mail address → fails ──────────────────────────────────
setup
commit_file "plugins/mycoach/skills/x/SKILL.md" \
  'send to renaud@bluegreen.ai directly'
check "mail address literal fails" 1

# ── Case 5: committed workspace slug outside known-debt files → fails ──────
setup
commit_file "plugins/briefing/skills/x/SKILL.md" \
  'call list_tasks(workspace_slug="renaud")'
check "workspace slug literal fails outside known-debt files" 1

# ── Case 6: same literal inside a jobsearch known-debt file → passes ───────
# See #103 — tracked, narrowly-scoped exception, not a blanket pass for jobsearch.
setup
commit_file "plugins/jobsearch/skills/log-application/SKILL.md" \
  'call list_tasks(workspace_slug="renaud")'
check "workspace slug literal in jobsearch known-debt file is excluded" 0

# ── Case 7: same literal in a jobsearch file NOT on the known-debt list → fails
setup
commit_file "plugins/jobsearch/skills/jobsearch-vault/SKILL.md" \
  'call list_tasks(workspace_slug="renaud")'
check "workspace slug literal in a non-excluded jobsearch file still fails" 1

echo
echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ]
