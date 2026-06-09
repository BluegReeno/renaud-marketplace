# Plan — gmail-mcp (Supabase Edge MCP server for Gmail perso)

## Feature Description

`gmail-mcp` is a remote MCP server hosted on Supabase Edge Functions that exposes 4 Gmail tools to Claude Code and claude.ai. It provides read-and-draft access to Renaud's personal Gmail account (`rlaborbe@gmail.com`) via the Gmail REST API, scoped to `gmail.modify` (no send). The server lives entirely in `servers/gmail-mcp/` inside `renaud-marketplace` — no separate repo.

The server replicates the exact auth architecture of HAL (the pro MCP server): `verifyAuth` from `@supabase/server` v1.1.0 with two modes — Supabase JWT (full OAuth 2.1 for claude.ai) and named API key bearer (for Claude Code / CLI). OAuth discovery is exposed via `/.well-known/oauth-protected-resource` pointing at Supabase Auth as the Authorization Server. No Supabase database is involved: the only runtime state is a Google access token obtained by refreshing `GOOGLE_REFRESH_TOKEN` from Supabase secrets on every request.

## Scope limits (non-goals — mandatory)

- no `send_email` in v1 — drafts only via `draft_email`
- no mcp-lite — `WebStandardStreamableHTTPServerTransport` from `@modelcontextprotocol/sdk@1.25.3` only
- no separate repo — everything in `renaud-marketplace/servers/gmail-mcp/`
- no scope expansion beyond `gmail.modify` — no `gmail.send`, no `gmail.compose`
- no Supabase DB — no tables, no migrations, no RLS
- no snippet from `messages.list` — `messages.list` never returns snippets; use `messages.get?format=METADATA` per message
- no pagination in v1 — `maxResults` capped at 50, no `nextPageToken` handling
- no Claude Code skill (`.claude-plugin/`) in this PR — server only

## Files to create

```
servers/gmail-mcp/supabase/config.toml
servers/gmail-mcp/supabase/functions/gmail-mcp/deno.json
servers/gmail-mcp/supabase/functions/gmail-mcp/index.ts
servers/gmail-mcp/scripts/setup_secrets.sh
```

## Files to modify

- `.gitignore` — append `servers/gmail-mcp/supabase/.env`

---

## Implementation Tasks

### Task 1 — supabase/config.toml + .gitignore

**What:** Create Supabase project config with `verify_jwt = false` for the function (mandatory — `verifyAuth` handles auth manually). Append `.env` entry to root `.gitignore`.

**File:** `servers/gmail-mcp/supabase/config.toml`

**Content (exact):**
```toml
project_id = "isdyvrwnxqcfalmlkzui"

[functions.gmail-mcp]
verify_jwt = false
```

**File:** `.gitignore` — append this line at the end of the file:
```
servers/gmail-mcp/supabase/.env
```

**Commit:** `chore(gmail-mcp): add supabase config and gitignore entry`

---

### Task 2 — deno.json (imports)

**What:** Create `deno.json` with exact same dependency versions as HAL. Copy verbatim — no additions, no removals.

**File:** `servers/gmail-mcp/supabase/functions/gmail-mcp/deno.json`

**Content (exact):**
```json
{
  "compilerOptions": {
    "noImplicitAny": false
  },
  "imports": {
    "@modelcontextprotocol/sdk": "npm:@modelcontextprotocol/sdk@1.25.3",
    "@supabase/server/core": "npm:@supabase/server@1.1.0/core",
    "zod": "npm:zod@3.25.28",
    "@supabase/supabase-js": "npm:@supabase/supabase-js@2.47.10"
  }
}
```

**Commit:** `chore(gmail-mcp): add deno.json`

---

### Task 3 — index.ts: auth skeleton + refreshGmailToken()

**What:** Full `index.ts` with HAL auth pattern replicated exactly, plus `refreshGmailToken()` helper and `getGmailToken()` context extractor. No tools yet — those are Tasks 5–8.

**File:** `servers/gmail-mcp/supabase/functions/gmail-mcp/index.ts`

**Required sections in order:**

#### 1. Imports
```typescript
import * as supabaseServer from "@supabase/server/core";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { WebStandardStreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/webStandardStreamableHttp.js";
import { z } from "zod";
```

#### 2. Constants
```typescript
const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const RESOURCE_BASE_URL = `${SUPABASE_URL}/functions/v1/gmail-mcp`;
const AUTH_SERVER_URL = `${SUPABASE_URL}/auth/v1`;
const RESOURCE_METADATA_URL = `${RESOURCE_BASE_URL}/.well-known/oauth-protected-resource`;
```

#### 3. CORS headers — copy verbatim from HAL
```typescript
const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type, accept, mcp-session-id, mcp-protocol-version, last-event-id",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
};
```

#### 4. `refreshGmailToken()` helper
```typescript
async function refreshGmailToken(): Promise<string> {
  const res = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "refresh_token",
      refresh_token: Deno.env.get("GOOGLE_REFRESH_TOKEN")!,
      client_id: Deno.env.get("GOOGLE_CLIENT_ID")!,
      client_secret: Deno.env.get("GOOGLE_CLIENT_SECRET")!,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(`Gmail token refresh failed: ${(err as any).error} — ${(err as any).error_description}`);
  }
  const data = await res.json();
  return (data as any).access_token as string;
}
```

Note: `refresh_token` is NOT returned in the response — only `access_token`. Do not try to store or rotate it.

#### 5. `getGmailToken()` context extractor — mirrors HAL's `getDb()`
```typescript
function getGmailToken(extra: unknown): string {
  const token = (extra as any)?.authInfo?.extra?.gmailToken;
  if (!token) throw new Error("missing gmailToken in authInfo.extra");
  return token;
}
```

#### 6. MCP Server instance (empty — tools added in Tasks 5–8)
```typescript
const server = new McpServer({ name: "gmail-mcp", version: "0.1.0" });
// deno-lint-ignore no-explicit-any
const registerTool: (...args: any[]) => void = server.registerTool.bind(server);
```

#### 7. Deno.serve handler — auth + OAuth discovery + MCP dispatch
```typescript
Deno.serve(async (req) => {
  const url = new URL(req.url);

  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });

  if (url.pathname.endsWith("/.well-known/oauth-protected-resource")) {
    return Response.json(
      { resource: RESOURCE_BASE_URL, authorization_servers: [AUTH_SERVER_URL], bearer_methods_supported: ["header"] },
      { status: 200, headers: corsHeaders },
    );
  }

  const { data: auth, error: authErr } = await supabaseServer.verifyAuth(req, {
    auth: ["user", "secret:gmail_api_key"],
  });
  if (authErr) {
    return Response.json(
      { error: authErr.message },
      {
        status: authErr.status,
        headers: { ...corsHeaders, "WWW-Authenticate": `Bearer resource_metadata="${RESOURCE_METADATA_URL}"` },
      },
    );
  }

  const gmailToken = await refreshGmailToken();
  const transport = new WebStandardStreamableHTTPServerTransport();
  await server.connect(transport);
  return transport.handleRequest(req, {
    authInfo: { token: auth.token ?? "", clientId: "gmail-mcp", scopes: [], extra: { gmailToken } },
  });
});
```

**Commit:** `feat(gmail-mcp): auth skeleton + refreshGmailToken + OAuth discovery`

---

### Task 4 — setup_secrets.sh

**What:** Shell script to set all 4 required secrets on the Supabase project via CLI. Values come from env vars the operator exports before running — no secrets hardcoded in the script.

**File:** `servers/gmail-mcp/scripts/setup_secrets.sh`

**Content (exact):**
```bash
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
```

Make executable: the executor must run `chmod +x servers/gmail-mcp/scripts/setup_secrets.sh` after creating the file.

**Commit:** `chore(gmail-mcp): add setup_secrets.sh`

---

### Task 5 — tool: search_emails

**What:** Register `search_emails` tool. `messages.list` returns only `{ id, threadId }` — fetch per-message metadata via `messages.get?format=METADATA` to get Subject, From, Date, and snippet.

**File:** `servers/gmail-mcp/supabase/functions/gmail-mcp/index.ts` — add before `Deno.serve`

**Implementation:**
```typescript
registerTool(
  "search_emails",
  {
    title: "Search Emails",
    description: "Search Gmail messages using a Gmail query string. Returns id, threadId, subject, from, date, snippet.",
    inputSchema: z.object({
      query: z.string().describe("Gmail search query (e.g. 'from:recruiter is:unread')"),
      max_results: z.number().int().min(1).max(50).default(20).optional(),
    }),
  },
  async ({ query, max_results }, extra: unknown) => {
    const token = getGmailToken(extra);
    const maxResults = max_results ?? 20;
    const listRes = await fetch(
      `https://gmail.googleapis.com/gmail/v1/users/me/messages?q=${encodeURIComponent(query)}&maxResults=${maxResults}`,
      { headers: { Authorization: `Bearer ${token}` } },
    );
    if (!listRes.ok) throw new Error(`Gmail list failed: ${listRes.status} ${await listRes.text()}`);
    const listData = await listRes.json() as any;
    const messages: Array<{ id: string; threadId: string }> = listData.messages ?? [];
    const results = await Promise.all(
      messages.map(async (m) => {
        const metaRes = await fetch(
          `https://gmail.googleapis.com/gmail/v1/users/me/messages/${m.id}?format=METADATA&metadataHeaders=Subject&metadataHeaders=From&metadataHeaders=Date`,
          { headers: { Authorization: `Bearer ${token}` } },
        );
        if (!metaRes.ok) return { id: m.id, threadId: m.threadId, subject: "", from: "", date: "", snippet: "" };
        const meta = await metaRes.json() as any;
        const hdrs: Record<string, string> = {};
        for (const h of meta.payload?.headers ?? []) hdrs[h.name] = h.value;
        return { id: m.id, threadId: m.threadId, subject: hdrs["Subject"] ?? "", from: hdrs["From"] ?? "", date: hdrs["Date"] ?? "", snippet: meta.snippet ?? "" };
      }),
    );
    return { content: [{ type: "text" as const, text: JSON.stringify(results, null, 2) }] };
  }
);
```

**Commit:** `feat(gmail-mcp): tool search_emails`

---

### Task 6 — tool: read_email

**What:** Register `read_email` tool. Fetches full message with `format=full`. Extracts headers + plain text body. Handles both flat (`payload.body.data`) and multipart (`payload.parts`) MIME trees — `payload.parts` is absent on non-multipart messages.

**File:** `servers/gmail-mcp/supabase/functions/gmail-mcp/index.ts` — add `extractBody` helper near top (after imports, before `server =`), add tool registration before `Deno.serve`

**`extractBody()` helper:**
```typescript
function extractBody(payload: any): string {
  if (!payload) return "";
  if (payload.mimeType === "text/plain" && payload.body?.data) {
    return atob(payload.body.data.replace(/-/g, "+").replace(/_/g, "/"));
  }
  for (const part of payload.parts ?? []) {
    const result = extractBody(part);
    if (result) return result;
  }
  return "";
}
```

**Implementation:**
```typescript
registerTool(
  "read_email",
  {
    title: "Read Email",
    description: "Read a Gmail message by ID. Returns subject, from, to, date, snippet, and plain text body.",
    inputSchema: z.object({
      message_id: z.string().describe("Gmail message ID (from search_emails results)"),
    }),
  },
  async ({ message_id }, extra: unknown) => {
    const token = getGmailToken(extra);
    const res = await fetch(
      `https://gmail.googleapis.com/gmail/v1/users/me/messages/${message_id}?format=full`,
      { headers: { Authorization: `Bearer ${token}` } },
    );
    if (!res.ok) throw new Error(`Gmail get failed: ${res.status} ${await res.text()}`);
    const data = await res.json() as any;
    const hdrs: Record<string, string> = {};
    for (const h of data.payload?.headers ?? []) hdrs[h.name] = h.value;
    return {
      content: [{
        type: "text" as const,
        text: JSON.stringify({
          id: data.id, threadId: data.threadId,
          subject: hdrs["Subject"] ?? "", from: hdrs["From"] ?? "",
          to: hdrs["To"] ?? "", date: hdrs["Date"] ?? "",
          snippet: data.snippet ?? "", body: extractBody(data.payload),
        }, null, 2),
      }],
    };
  }
);
```

**Commit:** `feat(gmail-mcp): tool read_email`

---

### Task 7 — tool: draft_email

**What:** Register `draft_email` tool. Builds RFC 2822 message, base64url-encodes it (`btoa` then replace `+→-`, `/→_`, strip `=`), POSTs to `/gmail/v1/users/me/drafts`. Optional `reply_to_message_id` adds `In-Reply-To` and `References` headers.

**File:** `servers/gmail-mcp/supabase/functions/gmail-mcp/index.ts` — add `buildRfc2822` helper near top, add tool registration before `Deno.serve`

**`buildRfc2822()` helper:**
```typescript
function buildRfc2822(to: string, subject: string, body: string, replyToId?: string): string {
  const lines = [
    `To: ${to}`,
    `Subject: ${subject}`,
    "Content-Type: text/plain; charset=UTF-8",
    "MIME-Version: 1.0",
  ];
  if (replyToId) {
    lines.push(`In-Reply-To: <${replyToId}>`);
    lines.push(`References: <${replyToId}>`);
  }
  lines.push("", body);
  return lines.join("\r\n");
}
```

**Implementation:**
```typescript
registerTool(
  "draft_email",
  {
    title: "Draft Email",
    description: "Create a Gmail draft. Returns draft_id, message_id, thread_id.",
    inputSchema: z.object({
      to: z.string().describe("Recipient email address"),
      subject: z.string().describe("Email subject"),
      body: z.string().describe("Plain text email body"),
      reply_to_message_id: z.string().optional().describe("Gmail message ID to reply to (adds In-Reply-To/References headers)"),
    }),
  },
  async ({ to, subject, body, reply_to_message_id }, extra: unknown) => {
    const token = getGmailToken(extra);
    const raw = btoa(buildRfc2822(to, subject, body, reply_to_message_id))
      .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
    const res = await fetch("https://gmail.googleapis.com/gmail/v1/users/me/drafts", {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify({ message: { raw } }),
    });
    if (!res.ok) throw new Error(`Gmail draft failed: ${res.status} ${await res.text()}`);
    const data = await res.json() as any;
    return {
      content: [{ type: "text" as const, text: JSON.stringify({ draft_id: data.id, message_id: data.message?.id, thread_id: data.message?.threadId }, null, 2) }],
    };
  }
);
```

**Commit:** `feat(gmail-mcp): tool draft_email`

---

### Task 8 — tool: list_labels

**What:** Register `list_labels` tool. Simple GET to `/gmail/v1/users/me/labels`, maps response to `{ id, name, type }` array.

**File:** `servers/gmail-mcp/supabase/functions/gmail-mcp/index.ts` — add before `Deno.serve`

**Implementation (no input schema — empty object):**
```typescript
registerTool(
  "list_labels",
  {
    title: "List Labels",
    description: "List all Gmail labels. Returns id, name, type.",
    inputSchema: z.object({}),
  },
  async (_input, extra: unknown) => {
    const token = getGmailToken(extra);
    const res = await fetch("https://gmail.googleapis.com/gmail/v1/users/me/labels", {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error(`Gmail labels failed: ${res.status} ${await res.text()}`);
    const data = await res.json() as any;
    const labels = (data.labels ?? []).map((l: any) => ({ id: l.id, name: l.name, type: l.type }));
    return { content: [{ type: "text" as const, text: JSON.stringify(labels, null, 2) }] };
  }
);
```

**Commit:** `feat(gmail-mcp): tool list_labels`

---

## Testing / Validation

- [ ] `supabase functions deploy --no-verify-jwt gmail-mcp --project-ref isdyvrwnxqcfalmlkzui`
- [ ] `npx @modelcontextprotocol/inspector https://isdyvrwnxqcfalmlkzui.supabase.co/functions/v1/gmail-mcp` — list shows exactly 4 tools: `search_emails`, `read_email`, `draft_email`, `list_labels`
- [ ] `search_emails` with query `"from:recruiter"` — returns JSON array (may be empty, no error)
- [ ] `read_email` with a valid message_id — returns object with `subject`, `body`, `from` fields
- [ ] `draft_email` with to/subject/body — returns `{ draft_id, message_id, thread_id }`
- [ ] `list_labels` — returns array containing at least `INBOX`, `SENT`, `DRAFT` entries
- [ ] Bearer mode: `curl -H "apikey: $GMAIL_API_KEY" https://isdyvrwnxqcfalmlkzui.supabase.co/functions/v1/gmail-mcp/.well-known/oauth-protected-resource` — returns JSON with `authorization_servers: ["https://isdyvrwnxqcfalmlkzui.supabase.co/auth/v1"]`
- [ ] No secrets in git: `git log --all -p | grep -E "GOOGLE_CLIENT|GOOGLE_REFRESH|gmail_api_key\s*="` returns nothing

## Acceptance criteria

- 4 tools registered and callable via MCP Inspector
- Bearer auth works: `apikey` header passes `verifyAuth` with `"secret:gmail_api_key"` mode
- OAuth discovery endpoint returns correct `authorization_servers` URL (`${SUPABASE_URL}/auth/v1`)
- `--no-verify-jwt` present in both deploy command and `config.toml` (`verify_jwt = false`)
- No Google credentials or `gmail_api_key` value committed anywhere in `servers/gmail-mcp/`
