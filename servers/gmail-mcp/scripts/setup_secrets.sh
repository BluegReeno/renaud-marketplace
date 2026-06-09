#!/bin/bash
# Usage:
#   export GOOGLE_CLIENT_ID=...
#   export GOOGLE_CLIENT_SECRET=...
#   export GOOGLE_REFRESH_TOKEN=...
#   export GMAIL_API_KEY=...
#   bash servers/gmail-mcp/scripts/setup_secrets.sh

set -euo pipefail

PROJECT_REF="isdyvrwnxqcfalmlkzui"

supabase secrets set \
  GOOGLE_CLIENT_ID="$GOOGLE_CLIENT_ID" \
  GOOGLE_CLIENT_SECRET="$GOOGLE_CLIENT_SECRET" \
  GOOGLE_REFRESH_TOKEN="$GOOGLE_REFRESH_TOKEN" \
  gmail_api_key="$GMAIL_API_KEY" \
  --project-ref "$PROJECT_REF"

echo "Secrets set on project $PROJECT_REF"
