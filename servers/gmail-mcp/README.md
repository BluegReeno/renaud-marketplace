# gmail-mcp

A Supabase Edge Function exposing an MCP server over Gmail (search, read, label,
draft) for the `mail-triage` and `briefing` skills. Deployed to Supabase project
`isdyvrwnxqcfalmlkzui`, authenticated with a static `GMAIL_API_KEY` bearer.

## Layout

```
servers/gmail-mcp/
├── scripts/
│   ├── setup_secrets.sh   # one-time: push Google OAuth + GMAIL_API_KEY secrets
│   └── deploy.sh          # one-command deploy + liveness verification
└── supabase/
    ├── config.toml
    └── functions/gmail-mcp/
```

## Deploy

```bash
./scripts/deploy.sh
```

`deploy.sh` is the one-command path to production. It:

1. **Asserts the linked project** is `isdyvrwnxqcfalmlkzui` (parsed from
   `supabase projects list`). If nothing is linked or the wrong project is, it
   aborts (exit 1) printing the exact fix:
   `supabase link --project-ref isdyvrwnxqcfalmlkzui`.
2. **Deploys**: `supabase functions deploy gmail-mcp --no-verify-jwt`
   (`--no-verify-jwt` so the function does its own bearer auth).
3. **Verifies liveness**: curls the function URL. `400/401/405` ⇒ alive and
   auth-rejecting (exit 0); `404`, any `5xx`, or a timeout ⇒ dead or
   misconfigured (exit 1, printing the HTTP code).

It never pushes git, never sets secrets, and makes no change beyond the deploy —
re-runnable at will.

## First-time setup

Before the first deploy, push the secrets once:

```bash
./scripts/setup_secrets.sh          # interactive (prompts for the refresh token)
# or: GOOGLE_REFRESH_TOKEN="1//…" ./scripts/setup_secrets.sh
```

Requires `client_secret_*.apps.googleusercontent.com.json` at the repo root and
`supabase link --project-ref isdyvrwnxqcfalmlkzui` already done. Save the printed
`GMAIL_API_KEY` in Bitwarden — clients need it for bearer auth.

## Prerequisites

- Supabase CLI installed and logged in.
- Project linked: `supabase link --project-ref isdyvrwnxqcfalmlkzui`.
