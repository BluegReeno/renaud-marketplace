#!/usr/bin/env bash
# Validate the structure of .claude-plugin/marketplace.json.
#
# For each entry in plugins[]:
#   1. All required top-level fields are present and non-empty
#   2. author.name and author.email are present and non-empty
#   3. source points to an existing directory
#   4. At least one skill is discoverable (source/skills/*/SKILL.md)
#
# Usage: ./scripts/check_marketplace_schema.sh
# Exit 0 = valid. Exit 1 = any violation.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MARKETPLACE="$REPO_ROOT/.claude-plugin/marketplace.json"
ERRORS=0

REQUIRED_FIELDS="name version description source homepage repository"

plugin_count="$(python3 -c "import json; d=json.load(open('$MARKETPLACE')); print(len(d.get('plugins', [])))")"

if [ "$plugin_count" -eq 0 ]; then
  echo "ERROR  marketplace.json has no plugins[] entries"
  exit 1
fi

for i in $(seq 0 $((plugin_count - 1))); do
  plugin_name="$(python3 -c "
import json
d = json.load(open('$MARKETPLACE'))
print(d['plugins'][$i].get('name', '(unnamed #$i)'))
")"

  # 1. Required scalar fields
  for field in $REQUIRED_FIELDS; do
    value="$(python3 -c "
import json
d = json.load(open('$MARKETPLACE'))
v = d['plugins'][$i].get('$field', '')
print(v if v else '')
")"
    if [ -z "$value" ]; then
      echo "MISSING  [$plugin_name] required field: $field"
      ERRORS=$((ERRORS + 1))
    fi
  done

  # 2. author sub-fields
  for subfield in name email; do
    value="$(python3 -c "
import json
d = json.load(open('$MARKETPLACE'))
author = d['plugins'][$i].get('author', {})
print(author.get('$subfield', '') if isinstance(author, dict) else '')
")"
    if [ -z "$value" ]; then
      echo "MISSING  [$plugin_name] required field: author.$subfield"
      ERRORS=$((ERRORS + 1))
    fi
  done

  # 3. source must be an existing directory
  source_rel="$(python3 -c "
import json
d = json.load(open('$MARKETPLACE'))
print(d['plugins'][$i].get('source', ''))
")"
  # Resolve relative to repo root (strip leading ./)
  source_abs="$REPO_ROOT/${source_rel#./}"
  if [ -z "$source_rel" ]; then
    : # already caught above as missing field
  elif [ ! -d "$source_abs" ]; then
    echo "INVALID  [$plugin_name] source does not exist: $source_rel"
    ERRORS=$((ERRORS + 1))
  else
    echo "OK       [$plugin_name] source exists: $source_rel"

    # 4. At least one SKILL.md discoverable under source/skills/
    skills_dir="$source_abs/skills"
    if [ ! -d "$skills_dir" ]; then
      echo "MISSING  [$plugin_name] no skills/ directory under $source_rel"
      ERRORS=$((ERRORS + 1))
    else
      skill_count=0
      while IFS= read -r -d '' skill_md; do
        skill_count=$((skill_count + 1))
      done < <(find "$skills_dir" -mindepth 2 -maxdepth 2 -name "SKILL.md" -print0 2>/dev/null)

      if [ "$skill_count" -eq 0 ]; then
        echo "MISSING  [$plugin_name] no SKILL.md found under $source_rel/skills/"
        ERRORS=$((ERRORS + 1))
      else
        echo "OK       [$plugin_name] $skill_count skill(s) discoverable"
      fi
    fi
  fi
done

if [ "$ERRORS" -gt 0 ]; then
  echo ""
  echo "FAIL: $ERRORS marketplace schema violation(s)."
  exit 1
fi

echo ""
echo "OK: all $plugin_count plugin entries pass schema validation."
