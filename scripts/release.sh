#!/usr/bin/env bash
# One-command release for a renaud-marketplace plugin.
#
# Bumps every version location in one validated pass, refreshes the CHANGELOG, enforces the
# version-sync invariant, then commits. It never pushes, merges, or tags — the
# human does that after review.
#
# Usage: ./scripts/release.sh <plugin> <new-version> "<changelog line>" [--mcp-version <v>]
#   <plugin>         plugin dir name under plugins/ (jobsearch | briefing | improve | myspy)
#   <new-version>    SemVer, MUST be strictly greater than the current one
#   <changelog line> one-line summary for the CHANGELOG entry
#   --mcp-version    optional: also bump plugins/<plugin>/.mcp.json server version
#
# This repo keeps a SINGLE root CHANGELOG.md with `## <plugin> <version>` headings
# (NOT a per-plugin CHANGELOG). `scripts/check_version_sync.sh` enforces that shape.
#
# All validation runs BEFORE any file is written — a failed check writes nothing.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MARKETPLACE="$REPO_ROOT/.claude-plugin/marketplace.json"
CHANGELOG="$REPO_ROOT/CHANGELOG.md"

usage() {
  cat <<'EOF'
Usage: ./scripts/release.sh <plugin> <new-version> "<changelog line>" [--mcp-version <v>]

  <plugin>          plugin dir name under plugins/ (jobsearch | briefing | improve | myspy)
  <new-version>     SemVer, must be strictly greater than the current version
  <changelog line>  one-line summary for the CHANGELOG entry
  --mcp-version <v> optional: also bump plugins/<plugin>/.mcp.json server version

Example:
  ./scripts/release.sh improve 0.2.0 "generated skill→repo map"
EOF
}

die() { echo "ERROR    $*" >&2; exit 1; }

# --- Parse args (positional + optional --mcp-version anywhere) ---------------
PLUGIN=""
NEW_VERSION=""
CHANGELOG_LINE=""
MCP_VERSION=""
POSITIONAL=()

while [ $# -gt 0 ]; do
  case "$1" in
    --mcp-version)
      { [ $# -ge 2 ] && [ -n "$2" ]; } || { usage >&2; die "--mcp-version requires a non-empty value"; }
      MCP_VERSION="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      POSITIONAL+=("$1")
      shift
      ;;
  esac
done

if [ "${#POSITIONAL[@]}" -ne 3 ]; then
  usage >&2
  die "expected <plugin> <new-version> \"<changelog line>\" (got ${#POSITIONAL[@]} positional arg(s))"
fi

PLUGIN="${POSITIONAL[0]}"
NEW_VERSION="${POSITIONAL[1]}"
CHANGELOG_LINE="${POSITIONAL[2]}"

[ -n "$CHANGELOG_LINE" ] || { usage >&2; die "changelog line must not be empty"; }

PLUGIN_JSON="$REPO_ROOT/plugins/$PLUGIN/.claude-plugin/plugin.json"
MCP_JSON="$REPO_ROOT/plugins/$PLUGIN/.mcp.json"

# --- Validation (all checks pass before any write) ---------------------------

[ -f "$PLUGIN_JSON" ] || die "unknown plugin '$PLUGIN' (no $PLUGIN_JSON)"
[ -f "$CHANGELOG" ] || die "no root CHANGELOG.md at $CHANGELOG"

# Working tree must be clean.
if [ -n "$(git -C "$REPO_ROOT" status --porcelain)" ]; then
  die "working tree is dirty — commit or stash before releasing"
fi

CURRENT_VERSION="$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['version'])" "$PLUGIN_JSON")" \
  || die "cannot read 'version' from $PLUGIN_JSON"

# New version must be a valid X.Y.Z (three-part numeric) and strictly greater
# than the current one. Python owns the message so a malformed version is never
# misreported as "not greater".
python3 - "$CURRENT_VERSION" "$NEW_VERSION" <<'PY' || exit 1
import re, sys

def parse(v, label):
    m = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", v.strip())
    if not m:
        sys.exit(f"ERROR    {label} version '{v}' is not a valid X.Y.Z (three-part numeric)")
    return tuple(int(x) for x in m.groups())

cur = parse(sys.argv[1], "current")
new = parse(sys.argv[2], "new")
if new <= cur:
    sys.exit(f"ERROR    new version '{sys.argv[2]}' is not strictly greater than current '{sys.argv[1]}'")
PY

# Root CHANGELOG must not already carry this plugin+version heading (mirror the
# regex in check_version_sync.sh: `^## <plugin> <version>` followed by ws/EOL).
VER_RE="${NEW_VERSION//./\\.}"
if grep -qE "^##[[:space:]]+${PLUGIN}[[:space:]]+${VER_RE}([[:space:]]|\$)" "$CHANGELOG"; then
  die "CHANGELOG.md already has a '## $PLUGIN $NEW_VERSION' entry"
fi

if [ -n "$MCP_VERSION" ]; then
  [ -f "$MCP_JSON" ] || die "--mcp-version given but no $MCP_JSON"
fi

# --- Actions (only reached once every validation passed) ---------------------

# JSON edits use a targeted regex on the version value so surrounding formatting
# (inline objects, indentation) stays byte-identical — no full re-dump.

# 1. plugin.json version (single top-level "version" key).
python3 - "$PLUGIN_JSON" "$NEW_VERSION" <<'PY'
import re, sys
path, ver = sys.argv[1], sys.argv[2]
text = open(path).read()
m = re.search(r'"version"\s*:\s*"[^"]*"', text)
if not m:
    sys.exit(f"no 'version' key found in {path}")
text = text[:m.start()] + f'"version": "{ver}"' + text[m.end():]
open(path, "w").write(text)
PY

# 2 + 3. marketplace.json: matching plugin entry + monotonic top-level bump.
python3 - "$MARKETPLACE" "$PLUGIN" "$NEW_VERSION" <<'PY'
import json, re, sys
path, plugin, ver = sys.argv[1], sys.argv[2], sys.argv[3]
text = open(path).read()
data = json.loads(text)

# Confirm a matching entry exists (name/id, case-insensitive — mirrors check_version_sync.sh).
entry = next((p for p in data.get("plugins", [])
              if p.get("name", "").lower() == plugin.lower()
              or p.get("id", "").lower() == plugin.lower()), None)
if entry is None:
    sys.exit(f"no matching '{plugin}' entry in marketplace.json")

# Compute the monotonic top-level PATCH +1.
m = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", data["version"].strip())
if not m:
    sys.exit(f"top-level marketplace version '{data['version']}' is not X.Y.Z")
major, minor, patch = (int(x) for x in m.groups())
new_top = f"{major}.{minor}.{patch + 1}"

ver_pat = re.compile(r'"version"\s*:\s*"[^"]*"')

# Top-level version is the first "version" key (precedes the plugins array).
vm = ver_pat.search(text)
if vm is None:
    sys.exit("no top-level 'version' key found in marketplace.json")
text = text[:vm.start()] + f'"version": "{new_top}"' + text[vm.end():]

# Plugin entry version: the first "version" key after this plugin's name/id.
name_pat = re.compile(r'"(?:name|id)"\s*:\s*"%s"' % re.escape(plugin), re.IGNORECASE)
nm = name_pat.search(text)
if nm is None:
    sys.exit(f"could not locate '{plugin}' name/id in marketplace.json text")
vm = ver_pat.search(text, nm.end())
if vm is None:
    sys.exit(f"no 'version' key found after '{plugin}' entry in marketplace.json")
text = text[:vm.start()] + f'"version": "{ver}"' + text[vm.end():]

open(path, "w").write(text)
PY

# 4. Insert a `## <plugin> <version>` CHANGELOG entry, keeping per-plugin grouping
#    (newest version first). Inserted above this plugin's most recent entry, or
#    above the first heading if the plugin has none yet.
python3 - "$CHANGELOG" "$PLUGIN" "$NEW_VERSION" "$CHANGELOG_LINE" <<'PY'
import re, sys
path, plugin, ver, line = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
text = open(path).read()
entry = f"## {plugin} {ver}\n\n- {line}\n\n"
m = re.search(rf"^##\s+{re.escape(plugin)}\s", text, re.MULTILINE)
if m is None:
    m = re.search(r"^## ", text, re.MULTILINE)
if m is None:
    text = text.rstrip("\n") + "\n\n" + entry
else:
    text = text[:m.start()] + entry + text[m.start():]
open(path, "w").write(text)
PY

# 5. Optional MCP server version bump.
if [ -n "$MCP_VERSION" ]; then
  python3 - "$MCP_JSON" "$MCP_VERSION" <<'PY'
import re, sys
path, ver = sys.argv[1], sys.argv[2]
text = open(path).read()
m = re.search(r'"version"\s*:\s*"[^"]*"', text)
if not m:
    sys.exit(f"no 'version' key found in {path}")
text = text[:m.start()] + f'"version": "{ver}"' + text[m.end():]
open(path, "w").write(text)
PY
fi

# 6. Enforce the invariant before committing.
if ! bash "$REPO_ROOT/scripts/check_version_sync.sh"; then
  die "version-sync check failed — no commit made (edits left in working tree for inspection)"
fi

# 7. Commit only — never push, merge, or tag.
git -C "$REPO_ROOT" add -A
git -C "$REPO_ROOT" commit -m "chore($PLUGIN): release v$NEW_VERSION" >/dev/null

echo ""
echo "OK: released $PLUGIN v$NEW_VERSION — committed (not pushed). Review, then 'git push'."
