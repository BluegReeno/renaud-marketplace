# gmail-mcp

A Supabase Edge Function exposing an MCP server over Gmail (search, read, label,
draft) for the `mail-triage` and `briefing` skills. Deployed to Supabase project
`isdyvrwnxqcfalmlkzui`, authenticated with a static `GMAIL_API_KEY` bearer, or a
Supabase JWT (`user` mode, e.g. the claude.ai mobile connector's OAuth flow) gated
by the `GMAIL_ALLOWED_USER_IDS` allowlist below.

## Access control

`GMAIL_API_KEY` and `GMAIL_ALLOWED_USER_IDS` are the only two ways into this
mailbox — a valid Supabase JWT alone is not enough, since the project can host
more than one provisioned user:

- `GMAIL_API_KEY`: shared secret, no per-user identity. Sent as `?key=` (Cowork /
  claude.ai custom connectors, which cannot send custom headers) or as the
  `apikey` header (`secret:gmail_api_key` auth mode). Owner-only — rotate it if
  it's ever suspected to have leaked.
- `GMAIL_ALLOWED_USER_IDS`: comma-separated Supabase `auth.users.id` (UUID)
  allowlist for the `user` JWT auth mode. A JWT proves the caller is *some*
  provisioned user on `isdyvrwnxqcfalmlkzui` — not that they own this mailbox —
  so every `user`-mode request is checked against this allowlist. Unset or empty
  means **every** `user`-mode request is rejected (fail closed); it does not
  affect the `GMAIL_API_KEY` paths above.

Find your Supabase user_id in the dashboard: Authentication → Users, on the
`isdyvrwnxqcfalmlkzui` project.

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
`GMAIL_API_KEY` in Bitwarden — clients need it for bearer auth. The script also
prompts for `GMAIL_ALLOWED_USER_IDS` (see [Access control](#access-control)) —
leave it blank to skip `user`-mode access entirely and rely on `GMAIL_API_KEY` only.

**Upgrading an existing deployment:** before this version, any Supabase JWT for
`isdyvrwnxqcfalmlkzui` was accepted. After deploying it, `user`-mode callers
(e.g. an existing claude.ai mobile connector) are rejected until you push your
own user_id:

```bash
supabase secrets set --project-ref isdyvrwnxqcfalmlkzui GMAIL_ALLOWED_USER_IDS="<your-user-id>"
```

## Prerequisites

- Supabase CLI installed and logged in.
- Project linked: `supabase link --project-ref isdyvrwnxqcfalmlkzui`.
