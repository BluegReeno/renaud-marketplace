#!/usr/bin/env bash
# Verify plugin version sync across plugin.json and marketplace.json.
# Individual SKILL.md versions are per-skill and may lag the plugin — reported as INFO only.
# Usage: ./scripts/check_version_sync.sh
# Exit 0 = plugin.json/marketplace.json in sync. Exit 1 = mismatch found.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MARKETPLACE="$REPO_ROOT/.claude-plugin/marketplace.json"
ERRORS=0

for plugin_json in "$REPO_ROOT"/plugins/*/.claude-plugin/plugin.json; do
  plugin_dir="$(dirname "$(dirname "$plugin_json")")"
  plugin_name="$(basename "$plugin_dir")"
  plugin_ver="$(python3 -c "import json; print(json.load(open('$plugin_json'))['version'])")"

  # Critical: plugin.json must match marketplace.json
  market_ver="$(python3 -c "
import json
data = json.load(open('$MARKETPLACE'))
plugins = data.get('plugins', data) if isinstance(data, dict) else data
entry = next((p for p in plugins if p.get('name','').lower() == '$plugin_name' or p.get('id','').lower() == '$plugin_name'), None)
print(entry['version'] if entry else 'NOT_FOUND')
" 2>/dev/null || echo "NOT_FOUND")"

  if [ "$market_ver" = "NOT_FOUND" ]; then
    echo "WARNING  [$plugin_name] not found in marketplace.json"
  elif [ "$market_ver" != "$plugin_ver" ]; then
    echo "MISMATCH [$plugin_name] plugin.json=$plugin_ver marketplace.json=$market_ver"
    ERRORS=$((ERRORS + 1))
  else
    echo "OK       [$plugin_name] v$plugin_ver"
  fi

  # Informational: show individual skill versions (each skill tracks its own version)
  while IFS= read -r skill_md; do
    skill_name="$(basename "$(dirname "$skill_md")")"
    skill_ver="$(grep -m1 '^version:' "$skill_md" | awk '{print $2}')"
    echo "  INFO   [$plugin_name/$skill_name] SKILL.md v$skill_ver (plugin v$plugin_ver)"
  done < <(find "$plugin_dir/skills" -name "SKILL.md" 2>/dev/null)
done

if [ "$ERRORS" -gt 0 ]; then
  echo ""
  echo "FAIL: $ERRORS mismatch(es) found between plugin.json and marketplace.json."
  exit 1
fi

echo ""
echo "OK: all plugin.json/marketplace.json versions in sync."
