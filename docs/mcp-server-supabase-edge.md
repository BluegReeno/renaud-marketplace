# MCP Server on Supabase Edge — Reference

Practical reference for building a remote MCP server on Supabase Edge Functions using
`@supabase/server`. Written from the gmail-mcp implementation and HAL production reference.

---

## 1. Documentation sources

| What | URL | How to access |
|------|-----|---------------|
| `@supabase/server` official docs | https://github.com/supabase/server/tree/main/docs | `gh api repos/supabase/server/contents/docs/<file>.md --jq '.content' \| base64 -d` |
| Auth modes reference | `docs/auth-modes.md` in the repo above | same |
| Core primitives | `docs/core-primitives.md` in the repo above | same |
| HAL production reference | `../hal/supabase/functions/hal-mcp/index.ts` | Read directly |
| HAL deno.json (dep versions) | `../hal/supabase/functions/hal-mcp/deno.json` | Read directly |
| Supabase blog (intro) | https://supabase.com/blog/introducing-supabase-server | WebFetch |
| MCP spec (transports) | https://modelcontextprotocol.io/docs/concepts/transports | WebFetch |
| Supabase Edge MCP guide | https://supabase.com/docs/guides/functions/examples/mcp-server-mcp-lite | WebFetch (uses mcp-lite — ignore stack, keep OAuth pattern) |

**Primary reference for any MCP server question: read `../hal/supabase/functions/hal-mcp/index.ts`.**
It is production code that works on mobile. Docs are secondary.

---

## 2. Stack (exact versions)

```json
{
  "@modelcontextprotocol/sdk": "npm:@modelcontextprotocol/sdk@1.25.3",
  "@supabase/server/core":     "npm:@supabase/server@1.1.0/core",
  "zod":                       "npm:zod@3.25.28",
  "@supabase/supabase-js":     "npm:@supabase/supabase-js@2.47.10"
}
```

These come from `../hal/supabase/functions/hal-mcp/deno.json`. Copy verbatim — do not use `mcp-lite`.

---

## 3. Import paths (critical — easy to get wrong)

```typescript
// @supabase/server — always /core for Edge Functions
import * as supabaseServer from "@supabase/server/core";

// MCP SDK — McpServer (high-level), NOT Server (low-level protocol)
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";

// Transport — webStandardStreamableHttp (not streamableHttp)
import { WebStandardStreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/webStandardStreamableHttp.js";

import { z } from "zod";
```

**Common mistakes:**
- `import { Server } from "…/server/index.js"` — wrong class, no `tool()` method
- `import … from "…/server/streamableHttp.js"` — wrong path, missing `webStandard` prefix
- `import { withSupabase } from "@supabase/server"` — Node/Hono adapter, not for Edge MCP

---

## 4. Auth pattern (downstream — client → server)

```typescript
const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const RESOURCE_BASE_URL = `${SUPABASE_URL}/functions/v1/<function-name>`;
const AUTH_SERVER_URL = `${SUPABASE_URL}/auth/v1`;
const RESOURCE_METADATA_URL = `${RESOURCE_BASE_URL}/.well-known/oauth-protected-resource`;

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type, accept, mcp-session-id, mcp-protocol-version, last-event-id",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
};
```

**verifyAuth call — two modes in one:**

```typescript
const { data: auth, error: authErr } = await supabaseServer.verifyAuth(req, {
  auth: ["user", "secret:<key-name>"],
  // Required when your key is stored as a regular env var (e.g. GMAIL_API_KEY).
  // See "SUPABASE_SECRET_KEYS gotcha" below.
  env: {
    secretKeys: { "<key-name>": Deno.env.get("MY_API_KEY")! },
  },
} as any);
if (authErr) {
  return Response.json(
    { error: authErr.message },
    { status: authErr.status, headers: { ...corsHeaders, "WWW-Authenticate": `Bearer resource_metadata="${RESOURCE_METADATA_URL}"` } },
  );
}
```

| Mode | Credential | Used by |
|------|-----------|---------|
| `"user"` | `Authorization: Bearer <supabase-jwt>` | claude.ai mobile/web (OAuth 2.1 full flow) |
| `"secret:<name>"` | `apikey: <secret-value>` header | Claude Code CLI, Desktop, OpenClaw, Dust, n8n |

**SUPABASE_SECRET_KEYS gotcha** — `secret:<name>` does NOT read your env var directly.
It reads from `SUPABASE_SECRET_KEYS` (a JSON env var: `{"<name>":"<value>"}`).
But the Supabase CLI blocks setting any `SUPABASE_*`-prefixed secret:

```
Env name cannot start with SUPABASE_, skipping: SUPABASE_SECRET_KEYS
```

**Fix:** pass `env.secretKeys` override directly in the `verifyAuth` call (as shown above).
The override reads your real env var (e.g. `GMAIL_API_KEY`) and passes it under the key name
that `secret:<name>` expects — no `SUPABASE_SECRET_KEYS` needed.

```typescript
// Your Supabase secret:  supabase secrets set GMAIL_API_KEY="..."
// Your verifyAuth call:
env: { secretKeys: { gmail_api_key: Deno.env.get("GMAIL_API_KEY")! } }
// Auth mode:            auth: ["user", "secret:gmail_api_key"]
```

Note: HAL (bluegreen project) sets `SUPABASE_SECRET_KEYS` via the dashboard (bypasses CLI restriction).
For personal projects use the `env` override — it's cleaner and avoids the restriction entirely.

**OAuth discovery endpoint (required for mobile):**

```typescript
if (url.pathname.endsWith("/.well-known/oauth-protected-resource")) {
  return Response.json(
    { resource: RESOURCE_BASE_URL, authorization_servers: [AUTH_SERVER_URL], bearer_methods_supported: ["header"] },
    { status: 200, headers: corsHeaders },
  );
}
```

This is what makes claude.ai discover Supabase Auth as the OAuth AS. Without it, the mobile connector cannot complete the OAuth flow.

---

## 5. MCP server + tool registration

```typescript
const server = new McpServer({ name: "my-server", version: "0.1.0" });

// type-erased wrapper to avoid TS2589 (same as HAL)
// deno-lint-ignore no-explicit-any
const registerTool: (...args: any[]) => void = server.registerTool.bind(server);

registerTool(
  "tool_name",
  {
    title: "Human Title",
    description: "What the tool does — shown to the LLM.",
    inputSchema: z.object({
      param: z.string().describe("Description of param"),
    }),
  },
  async ({ param }, extra: unknown) => {
    // extra.authInfo.extra contains what you injected in transport.handleRequest
    return { content: [{ type: "text" as const, text: "result" }] };
  }
);
```

**`registerTool` signature:** `(name, { title, description, inputSchema }, handler)`
- `inputSchema` = Zod schema (not `.shape` — the full `z.object(...)`)
- handler receives `(args, extra)` — `args` is typed from the schema, `extra` is `unknown`

---

## 6. Request handler

```typescript
const fetchHandler = async (req: Request): Promise<Response> => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });

  const url = new URL(req.url);
  if (url.pathname.endsWith("/.well-known/oauth-protected-resource")) {
    // ... (§4 above)
  }

  const { data: auth, error: authErr } = await supabaseServer.verifyAuth(req, {
    auth: ["user", "secret:my_api_key"],
    env: { secretKeys: { my_api_key: Deno.env.get("MY_API_KEY")! } },
  } as any);
  if (authErr) { /* ... */ }

  // Inject any context your tools need into `extra`
  const myContext = await buildContext(auth);

  const transport = new WebStandardStreamableHTTPServerTransport();
  await server.connect(transport);
  return transport.handleRequest(req, {
    authInfo: {
      token: auth.token ?? "",
      clientId: "my-server",
      scopes: [],
      extra: { myContext },   // ← available as extra.authInfo.extra.myContext in tools
    },
  });
};

export default { fetch: fetchHandler };
```

**Important:**
- Use `export default { fetch: fetchHandler }` — NOT `Deno.serve(...)`. HAL pattern, required for Supabase Edge.
- `server.connect(transport)` is called per-request (new transport instance each time).
  `server` itself is a module-level singleton — it holds the tool registry only. This is the stateless pattern.

---

## 7. config.toml (mandatory)

```toml
project_id = "<supabase-ref>"

[functions.<function-name>]
verify_jwt = false
```

`verify_jwt = false` is required whenever auth mode is anything other than `"user"`.
With it `false`, `verifyAuth` handles all credential checking manually.

Without this, Supabase's platform layer rejects requests with `apikey` header before
they reach your function.

---

## 8. Secrets setup

```bash
# Generate and push a random bearer key
supabase secrets set \
  MY_API_KEY="$(openssl rand -hex 24)" \
  --project-ref <ref>
```

The env var name (e.g. `MY_API_KEY`) is what you use in `Deno.env.get("MY_API_KEY")`.
The key name in the `env.secretKeys` override (e.g. `my_api_key`) must match the `secret:<name>` in `auth:`.
These two names are independent — the env var name and the key name don't have to match.

```typescript
// supabase secrets set GMAIL_API_KEY="..."   ← env var name (can be anything)
env: { secretKeys: { gmail_api_key: Deno.env.get("GMAIL_API_KEY")! } }
//                   ^^^^^^^^^^^^ key name     ^^^^^^^^^^^^^^^^^^^^^^ reads the env var
auth: ["user", "secret:gmail_api_key"]
//                     ^^^^^^^^^^^^ must match key name above
```

**Do NOT try to set `SUPABASE_SECRET_KEYS` via CLI** — it is blocked by design.
Use the `env` override in `verifyAuth` instead (§4).

---

## 9. Claude Code CLI connection (bearer mode)

```bash
claude mcp add <server-name> -t http https://<ref>.supabase.co/functions/v1/<function> \
  --header "apikey: <MY_API_KEY>"
```

Note: `apikey:` header (not `Authorization: Bearer`). The `secret` auth mode reads from `apikey`.

---

## 10. claude.ai custom connector (mobile/web/desktop)

### 10a. OAuth mode (requires Supabase OAuth 2.1 server)

1. claude.ai → Settings → Connectors → Add custom connector
2. Enter URL: `https://<ref>.supabase.co/functions/v1/<function>`
3. No Client ID / Secret needed — OAuth discovery is automatic via `/.well-known/oauth-protected-resource`
4. Connector syncs to mobile automatically after authorizing on web

**Prerequisites on the Supabase project** (this is what HAL/bluegreen has and gmail-mcp-perso does NOT):
- Dashboard → Authentication → OAuth Server → enable (beta) + dynamic client registration
- A consent page hosted outside Supabase (see "HTML limitation" below)
- Check: `curl https://<ref>.supabase.co/auth/v1/.well-known/oauth-authorization-server` —
  `{"error_code":"feature_disabled"}` means the OAuth flow can never complete

**Two gotchas in the Claude OAuth dance:**
- The browser's claude.ai session must be logged in with the SAME account as the Claude app,
  otherwise: "Account mismatch / Incompatibilité de compte". This check is Claude-side.
- The "OAuth Client ID/Secret" fields in the connector dialog configure a pre-registered OAuth
  client — they do NOT bypass the interactive browser flow. There is no headless option there.

**HTML limitation of Edge Functions — use GitHub Pages for the consent page**

Edge Functions cannot serve interactive HTML to browsers. Supabase/Cloudflare forces:
- `Content-Type: text/plain` regardless of what you set
- `CSP: default-src 'none'; sandbox` — no scripts, no external resources

Any attempt to build a consent page as an Edge Function results in a blank or broken page.

**Solution:** host the consent page on GitHub Pages (or any static host) and point Supabase
`authorization_url_path` at it.

Setup for `renaud-marketplace`:
1. Consent page: `oauth/consent/index.html` at the repo root → `https://BluegReeno.github.io/renaud-marketplace/oauth/consent`
2. GitHub → Settings → Pages → Source: branch `main`, folder `/ (root)`
3. Supabase → Authentication → URL Configuration:
   - Site URL: `https://BluegReeno.github.io/renaud-marketplace`
   - Additional Redirect URLs: `https://BluegReeno.github.io/renaud-marketplace/**`
4. Authentication → OAuth Server → Authorization Path: `/oauth/consent`
5. The consent page calls `auth/v1/oauth/authorizations/{id}` and `…/consent` directly via `fetch` —
   the `@supabase/supabase-js` SDK handles only `signInWithOAuth` and `getSession`;
   authorization endpoints must be called as raw REST.

Test the page alone first (should show "authorization_id manquant" error, not a blank page):
```
https://BluegReeno.github.io/renaud-marketplace/oauth/consent
```

### 10b. Query-param key mode (no OAuth — single-user servers)

The claude.ai/Cowork connector UI cannot send custom headers, so `secret:<name>` mode is
unusable there. Fallback: accept the API key as a `?key=` query param **before** `verifyAuth`:

```typescript
let authToken = "";
const queryKey = url.searchParams.get("key");
if (queryKey !== null) {
  if (queryKey !== Deno.env.get("MY_API_KEY")) {
    // Plain 401 WITHOUT WWW-Authenticate — a wrong key must fail fast, not trigger OAuth.
    return Response.json({ error: "Invalid key" }, { status: 401, headers: corsHeaders });
  }
} else {
  // ... verifyAuth path (§4) — header clients (Claude Code CLI) keep working
  authToken = auth.token ?? "";
}
```

Connector URL: `https://<ref>.supabase.co/functions/v1/<function>?key=<MY_API_KEY>`
Since the server returns 200 on initialize, Claude never sees a 401 and never starts OAuth.

**Never commit the keyed URL** (`.mcp.json` keeps the bare URL — the key is pasted manually
in the connector dialog). Trade-off: the key lives in the connector config/URL — acceptable
for a personal single-user server, not for multi-user.

---

## 11. Deploy

```bash
supabase functions deploy --no-verify-jwt <function-name> --project-ref <ref>
```

`--no-verify-jwt` = CLI-level flag that mirrors `verify_jwt = false` in config.toml.
Both must be set consistently.

---

## 12. Test checklist

```bash
# 1. OAuth discovery (should return JSON with authorization_servers)
curl https://<ref>.supabase.co/functions/v1/<fn>/.well-known/oauth-protected-resource

# 2. Bearer auth + tool list (MCP Inspector)
npx @modelcontextprotocol/inspector \
  --header "apikey: <MY_API_KEY>" \
  https://<ref>.supabase.co/functions/v1/<fn>

# 3. No secrets in git
git log --all -p | grep -E "MY_API_KEY\s*=|client_secret"
```
