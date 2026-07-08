#!/usr/bin/env bash
# Verify the plugin version invariant.
#
# Two enforced fields per plugin (both must be identical):
#   - plugins/<plugin>/.claude-plugin/plugin.json      version
#   - .claude-plugin/marketplace.json                  plugins[].version
#
# Plus: CHANGELOG.md must document each plugin's current version
# (heading `## <plugin> <version>`).
#
# The top-level marketplace.json version is a monotonic release counter; it is a
# process rule (bump +0.0.1 on every release) and is not statically checked here.
#
# Usage: ./scripts/check_version_sync.sh
# Exit 0 = invariant holds. Exit 1 = any mismatch or missing CHANGELOG entry.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MARKETPLACE="$REPO_ROOT/.claude-plugin/marketplace.json"
CHANGELOG="$REPO_ROOT/CHANGELOG.md"
ERRORS=0

if [ ! -f "$CHANGELOG" ]; then
  echo "MISSING  CHANGELOG.md not found at repo root"
  exit 1
fi

for plugin_json in "$REPO_ROOT"/plugins/*/.claude-plugin/plugin.json; do
  plugin_dir="$(dirname "$(dirname "$plugin_json")")"
  plugin_name="$(basename "$plugin_dir")"
  plugin_ver="$(python3 -c "import json; print(json.load(open('$plugin_json'))['version'])")"

  # Invariant 1: plugin.json version must match the marketplace.json plugin entry.
  market_ver="$(python3 -c "
import json
data = json.load(open('$MARKETPLACE'))
plugins = data.get('plugins', data) if isinstance(data, dict) else data
entry = next((p for p in plugins if p.get('name','').lower() == '$plugin_name' or p.get('id','').lower() == '$plugin_name'), None)
print(entry['version'] if entry else 'NOT_FOUND')
" 2>/dev/null || echo "NOT_FOUND")"

  if [ "$market_ver" = "NOT_FOUND" ]; then
    echo "MISSING  [$plugin_name] not found in marketplace.json"
    ERRORS=$((ERRORS + 1))
  elif [ "$market_ver" != "$plugin_ver" ]; then
    echo "MISMATCH [$plugin_name] plugin.json=$plugin_ver marketplace.json=$market_ver"
    ERRORS=$((ERRORS + 1))
  else
    echo "OK       [$plugin_name] v$plugin_ver"
  fi

  # Invariant 2: CHANGELOG.md must have an entry for the current version.
  ver_re="${plugin_ver//./\\.}"
  if grep -qE "^##[[:space:]]+${plugin_name}[[:space:]]+${ver_re}([[:space:]]|\$)" "$CHANGELOG"; then
    echo "OK       [$plugin_name] CHANGELOG entry for v$plugin_ver"
  else
    echo "MISSING  [$plugin_name] CHANGELOG.md has no entry for v$plugin_ver"
    ERRORS=$((ERRORS + 1))
  fi
done

if [ "$ERRORS" -gt 0 ]; then
  echo ""
  echo "FAIL: $ERRORS invariant violation(s)."
  exit 1
fi

echo ""
echo "OK: plugin.json/marketplace.json in sync; CHANGELOG.md documents all current versions."
