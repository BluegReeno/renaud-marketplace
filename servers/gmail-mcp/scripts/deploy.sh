#!/usr/bin/env bash
# deploy.sh — One-command deploy + verification for the gmail-mcp Edge Function.
#
# Usage:
#   ./deploy.sh
#
# What it does:
#   1. Assert the linked Supabase project is isdyvrwnxqcfalmlkzui (parsed from
#      `supabase projects list`); otherwise abort with the exact link command.
#   2. Deploy: `supabase functions deploy gmail-mcp --no-verify-jwt`.
#   3. Verify: curl the function URL. 401/400/405 ⇒ alive and auth-rejecting (exit 0);
#      404/5xx/timeout ⇒ dead or misconfigured (exit 1, printing the code).
#
# Prerequisites:
#   - supabase CLI installed and logged in
#   - supabase link --project-ref isdyvrwnxqcfalmlkzui already done

set -euo pipefail

PROJECT_REF="isdyvrwnxqcfalmlkzui"
FUNCTION_NAME="gmail-mcp"
FUNCTION_URL="https://${PROJECT_REF}.supabase.co/functions/v1/${FUNCTION_NAME}"

# --- 1. Assert the linked project ---
# `supabase projects list` marks the linked project with a ● in the LINKED column.
echo "🔍 Checking linked Supabase project …"
LINKED_LINE=$(supabase projects list 2>/dev/null | grep '●' || true)

if [[ -z "$LINKED_LINE" ]]; then
  echo "❌ No Supabase project is linked in this directory."
  echo "   Fix: supabase link --project-ref $PROJECT_REF"
  exit 1
fi

# Project refs are 20 lowercase letters — pull the one on the linked line.
LINKED_REF=$(printf '%s\n' "$LINKED_LINE" | grep -oE '\b[a-z]{20}\b' | head -1 || true)

if [[ "$LINKED_REF" != "$PROJECT_REF" ]]; then
  echo "❌ Linked project is '${LINKED_REF:-unknown}', expected '$PROJECT_REF'."
  echo "   Fix: supabase link --project-ref $PROJECT_REF"
  exit 1
fi

echo "✅ Linked project: $PROJECT_REF"

# --- 2. Deploy ---
echo ""
echo "🚀 Deploying function '$FUNCTION_NAME' (--no-verify-jwt) …"
supabase functions deploy "$FUNCTION_NAME" --no-verify-jwt --project-ref "$PROJECT_REF"

# --- 3. Verify ---
echo ""
echo "🔎 Verifying $FUNCTION_URL …"
HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 "$FUNCTION_URL" || echo "000")

case "$HTTP_CODE" in
  400 | 401 | 405)
    echo "✅ Function is alive and auth-rejecting (HTTP $HTTP_CODE)."
    exit 0
    ;;
  000)
    echo "❌ Verification failed: no response (timeout or connection error)."
    exit 1
    ;;
  *)
    echo "❌ Verification failed: unexpected HTTP $HTTP_CODE (expected 400/401/405)."
    exit 1
    ;;
esac
