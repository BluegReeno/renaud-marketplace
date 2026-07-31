#!/usr/bin/env bash
# Guard: no personal identity literal may appear in the multi-user skills.
#
# These skills resolve their context at runtime from `whoami` (workspace slugs,
# calendars) and from which MCP server is called (mailboxes). A literal address,
# calendar ID or workspace slug means the skill was written for one specific
# person again — it breaks every other user, and this repository is public.
#
# See BluegReeno/renaud-marketplace#77 and #76.
# Exit 1 on any hit. No dependency beyond grep.

set -uo pipefail
cd "$(dirname "$0")/.."

SCOPE=(plugins/briefing plugins/mycoach)

# `author.email` in a plugin manifest is a published-on-purpose authorship field,
# not a runtime identifier — the only address allowed to survive here.
EXCLUDE_FILES='/\.claude-plugin/plugin\.json:'

# An address that is a service endpoint, a placeholder or a doc example is fine.
# Everything else that looks like an address is a personal identifier.
ALLOW='linkedin\.com|example\.(com|org|net)|noreply|no-reply|<[a-z][a-z0-9-]*>|\{[a-z_]+\}'

fail=0

report() {
  fail=1
  printf '✗ %s\n' "$1"
  printf '%s\n' "$2" | sed 's/^/    /'
  printf '\n'
}

scan() {  # scan <regex> <message> [extra-filter-regex-to-drop]
  local hits
  hits=$(grep -rnE "$1" "${SCOPE[@]}" 2>/dev/null | grep -vE "$EXCLUDE_FILES" || true)
  if [ -n "${3:-}" ]; then
    hits=$(printf '%s\n' "$hits" | grep -vE "$3" || true)
  fi
  [ -n "$hits" ] && report "$2" "$hits"
  return 0
}

# 1. Google Calendar IDs — a shared or imported calendar always carries this suffix.
scan '@(group|import)\.calendar\.google\.com' \
     'Calendar ID hardcoded — resolve it from whoami (calendar_id / member_calendar_id)'

# 2. Mail addresses, minus service endpoints and placeholders.
scan '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' \
     'Mail address hardcoded — which inbox is read is decided by which MCP server is called, never by an address string' \
     "$ALLOW"

# 3. Workspace slugs passed as literals. `workspace_slug=w.workspace_slug` and
#    `workspace_slug=<resolved>` are the correct forms and are not matched.
scan 'workspace_slug[[:space:]]*=[[:space:]]*("[a-z][a-z0-9-]*"|'"'"'[a-z][a-z0-9-]*'"'"')' \
     'Workspace slug hardcoded — iterate on what whoami returns'

if [ "$fail" -eq 0 ]; then
  echo "OK: no identity literal in ${SCOPE[*]}"
fi
exit "$fail"
