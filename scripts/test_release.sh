#!/usr/bin/env bash
# Offline smoke test for scripts/release.sh refusal paths.
#
# release.sh's entire value is refusing to release when something is wrong, so
# the refusal paths are the higher-value half to pin (the happy path is already
# exercised by every real release commit). This builds a throwaway fixture repo
# in a mktemp dir and drives each bad input.
#
# release.sh derives REPO_ROOT from its own path ($(dirname "$0")/..), so a copy
# placed in the fixture's scripts/ operates on the fixture — not this repo. Each
# refusal asserts BOTH a non-zero exit AND that the tree is untouched (no file
# changed, no new commit): the "all validation runs before any write" promise is
# only proven by a before/after check. One happy-path case proves the fixture is
# actually releasable, so the refusals cannot pass trivially on a script that
# always exits non-zero.
#
# Pure coreutils + git + python3 stdlib — no new dependency. Mirrors
# check_version_sync.sh's ERRORS-counter idiom.
#
# Usage: ./scripts/test_release.sh   (exit 0 = all pass, exit 1 = any failure)

set -uo pipefail

SRC_DIR="$(cd "$(dirname "$0")" && pwd)"
ERRORS=0
PASS=0

FIXTURE="$(mktemp -d)"
trap 'rm -rf "$FIXTURE"' EXIT

# Build a minimal, in-sync fixture repo: one plugin `foo` at 0.1.0, a
# marketplace with a monotonic top-level counter, and a matching CHANGELOG entry.
build_fixture() {
  rm -rf "$FIXTURE"
  mkdir -p "$FIXTURE/scripts" \
           "$FIXTURE/plugins/foo/.claude-plugin" \
           "$FIXTURE/.claude-plugin"
  cp "$SRC_DIR/release.sh" "$SRC_DIR/check_version_sync.sh" "$FIXTURE/scripts/"

  cat > "$FIXTURE/plugins/foo/.claude-plugin/plugin.json" <<'JSON'
{ "name": "foo", "version": "0.1.0" }
JSON

  cat > "$FIXTURE/.claude-plugin/marketplace.json" <<'JSON'
{ "version": "1.0.0", "plugins": [ { "name": "foo", "version": "0.1.0" } ] }
JSON

  cat > "$FIXTURE/CHANGELOG.md" <<'MD'
# Changelog

## foo 0.1.0

- init
MD

  git -C "$FIXTURE" init -q
  git -C "$FIXTURE" config user.email test@example.com
  git -C "$FIXTURE" config user.name  test
  git -C "$FIXTURE" add -A
  git -C "$FIXTURE" commit -qm init
}

# assert_refusal <description> [release.sh args...]
# Passes when release.sh exits non-zero AND leaves the tree byte-identical.
assert_refusal() {
  local desc="$1"; shift
  local before after status dirty
  before="$(git -C "$FIXTURE" rev-parse HEAD)"
  ( cd "$FIXTURE" && bash scripts/release.sh "$@" ) >/dev/null 2>&1
  status=$?
  after="$(git -C "$FIXTURE" rev-parse HEAD)"
  dirty="$(git -C "$FIXTURE" status --porcelain)"

  if [ "$status" -eq 0 ]; then
    echo "FAIL     $desc — expected non-zero exit, got 0"
    ERRORS=$((ERRORS + 1))
  elif [ "$before" != "$after" ]; then
    echo "FAIL     $desc — a commit was made (before=$before after=$after)"
    ERRORS=$((ERRORS + 1))
  elif [ -n "$dirty" ]; then
    echo "FAIL     $desc — working tree was modified"
    ERRORS=$((ERRORS + 1))
    git -C "$FIXTURE" checkout -q -- . 2>/dev/null
    git -C "$FIXTURE" clean -fdq 2>/dev/null
  else
    echo "OK       $desc — refused, tree clean"
    PASS=$((PASS + 1))
  fi
}

# --- Refusal paths (tree must stay clean) ------------------------------------
build_fixture

assert_refusal "no args"                              # 0 positional -> usage+die
assert_refusal "unknown plugin"        bar 0.2.0 "x"  # no plugins/bar/...plugin.json
assert_refusal "non-increasing (equal)" foo 0.1.0 "x" # not strictly greater
assert_refusal "non-increasing (lower)" foo 0.0.9 "x" # not strictly greater
assert_refusal "malformed semver"      foo 1.2   "x"  # not X.Y.Z
assert_refusal "empty changelog line"  foo 0.2.0 ""   # empty summary
assert_refusal "--mcp-version no value" foo 0.2.0 "x" --mcp-version  # flag needs a value

# --- Dirty tree (special: we intentionally dirty, then restore) --------------
{
  local_before="$(git -C "$FIXTURE" rev-parse HEAD)"
  printf '\nscratch\n' >> "$FIXTURE/CHANGELOG.md"
  ( cd "$FIXTURE" && bash scripts/release.sh foo 0.2.0 "x" ) >/dev/null 2>&1
  status=$?
  local_after="$(git -C "$FIXTURE" rev-parse HEAD)"
  if [ "$status" -ne 0 ] && [ "$local_before" = "$local_after" ]; then
    echo "OK       dirty tree — refused, no commit"
    PASS=$((PASS + 1))
  else
    echo "FAIL     dirty tree — status=$status commit_changed=$([ "$local_before" != "$local_after" ] && echo yes || echo no)"
    ERRORS=$((ERRORS + 1))
  fi
  git -C "$FIXTURE" checkout -q -- .
  git -C "$FIXTURE" clean -fdq
}

# --- Duplicate CHANGELOG heading (commit the heading so the tree is clean) ----
printf '\n## foo 0.2.0\n\n- placeholder\n' >> "$FIXTURE/CHANGELOG.md"
git -C "$FIXTURE" commit -qam "pre-existing 0.2.0 heading"
assert_refusal "duplicate CHANGELOG heading" foo 0.2.0 "x"

# --- Happy path (proves the fixture is releasable) ---------------------------
build_fixture
before="$(git -C "$FIXTURE" rev-parse HEAD)"
( cd "$FIXTURE" && bash scripts/release.sh foo 0.2.0 "new feature" ) >/dev/null 2>&1
status=$?
after="$(git -C "$FIXTURE" rev-parse HEAD)"
newver="$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['version'])" \
          "$FIXTURE/plugins/foo/.claude-plugin/plugin.json" 2>/dev/null)"
dirty="$(git -C "$FIXTURE" status --porcelain)"
if [ "$status" -eq 0 ] && [ "$before" != "$after" ] && [ "$newver" = "0.2.0" ] && [ -z "$dirty" ]; then
  echo "OK       happy path — released 0.2.0, committed, tree clean"
  PASS=$((PASS + 1))
else
  echo "FAIL     happy path — status=$status newver=$newver commit_made=$([ "$before" != "$after" ] && echo yes || echo no) dirty='$dirty'"
  ERRORS=$((ERRORS + 1))
fi

# --- Summary -----------------------------------------------------------------
echo ""
if [ "$ERRORS" -gt 0 ]; then
  echo "FAIL: $ERRORS failure(s), $PASS passed."
  exit 1
fi
echo "OK: all $PASS release.sh guard(s) hold."
