#!/usr/bin/env bash
# setup_secrets.sh — Configure Supabase secrets for gmail-mcp from the Google OAuth client secret JSON.
#
# Usage:
#   ./setup_secrets.sh                          # interactive: prompts for refresh token
#   GOOGLE_REFRESH_TOKEN="1//xxx" ./setup_secrets.sh   # non-interactive
#
# Prerequisites:
#   - supabase CLI installed and logged in
#   - client_secret_*.apps.googleusercontent.com.json present at repo root
#   - supabase link --project-ref isdyvrwnxqcfalmlkzui already done

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
PROJECT_REF="isdyvrwnxqcfalmlkzui"

# --- Find the client secret JSON ---
CLIENT_SECRET_FILE=$(find "$REPO_ROOT" -maxdepth 1 -name "client_secret_*.apps.googleusercontent.com.json" | head -1)
if [[ -z "$CLIENT_SECRET_FILE" ]]; then
  echo "❌ No client_secret_*.apps.googleusercontent.com.json found in $REPO_ROOT"
  echo "   Download it from Google Cloud Console → APIs & Services → Credentials → your OAuth client"
  exit 1
fi

echo "✅ Found: $(basename "$CLIENT_SECRET_FILE")"

# --- Extract client_id and client_secret ---
GOOGLE_CLIENT_ID=$(python3 -c "import json,sys; d=json.load(open('$CLIENT_SECRET_FILE')); print(list(d.values())[0]['client_id'])")
GOOGLE_CLIENT_SECRET=$(python3 -c "import json,sys; d=json.load(open('$CLIENT_SECRET_FILE')); print(list(d.values())[0]['client_secret'])")

echo "   client_id  : $GOOGLE_CLIENT_ID"
echo "   client_secret : ${GOOGLE_CLIENT_SECRET:0:8}…"

# --- Refresh token (from env or prompt) ---
if [[ -z "${GOOGLE_REFRESH_TOKEN:-}" ]]; then
  echo ""
  echo "📋 Paste your Google refresh token (from OAuth Playground — scope gmail.modify):"
  read -r GOOGLE_REFRESH_TOKEN
fi

if [[ -z "$GOOGLE_REFRESH_TOKEN" ]]; then
  echo "❌ GOOGLE_REFRESH_TOKEN is empty. Aborting."
  exit 1
fi

# --- Generate a random API key for bearer auth (Claude Code / OpenClaw) ---
GMAIL_API_KEY=$(openssl rand -hex 24)

echo ""
echo "🔑 Generated GMAIL_API_KEY: $GMAIL_API_KEY"
echo "   (save this in Bitwarden — needed for Claude Code / OpenClaw config)"
echo ""

# --- Push secrets to Supabase ---
echo "🚀 Pushing secrets to Supabase project $PROJECT_REF …"
supabase secrets set \
  --project-ref "$PROJECT_REF" \
  GOOGLE_CLIENT_ID="$GOOGLE_CLIENT_ID" \
  GOOGLE_CLIENT_SECRET="$GOOGLE_CLIENT_SECRET" \
  GOOGLE_REFRESH_TOKEN="$GOOGLE_REFRESH_TOKEN" \
  GMAIL_API_KEY="$GMAIL_API_KEY"

echo ""
echo "✅ Done. Secrets set:"
echo "   GOOGLE_CLIENT_ID"
echo "   GOOGLE_CLIENT_SECRET"
echo "   GOOGLE_REFRESH_TOKEN"
echo "   GMAIL_API_KEY = $GMAIL_API_KEY"
echo ""
echo "📌 Next steps:"
echo "   1. Save GMAIL_API_KEY in Bitwarden (entry: gmail-mcp-perso)"
echo "   2. supabase functions deploy --no-verify-jwt gmail-mcp --project-ref $PROJECT_REF"
echo "   3. Test: npx @modelcontextprotocol/inspector https://isdyvrwnxqcfalmlkzui.supabase.co/functions/v1/gmail-mcp"
