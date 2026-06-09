import * as supabaseServer from "@supabase/server/core";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { WebStandardStreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/webStandardStreamableHttp.js";
import { z } from "zod";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const RESOURCE_BASE_URL = `${SUPABASE_URL}/functions/v1/gmail-mcp`;
const RESOURCE_METADATA_URL = `${RESOURCE_BASE_URL}/.well-known/oauth-protected-resource`;
const AUTH_SERVER_URL = `${SUPABASE_URL}/auth/v1`;

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type, accept, mcp-session-id, mcp-protocol-version, last-event-id",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
};

let cachedToken: { value: string; expiresAt: number } | null = null;

// Token cached per isolate; cold starts refresh once, warm requests reuse until expiry.
async function getOrRefreshGmailToken(): Promise<string> {
  const now = Date.now();
  if (cachedToken && now < cachedToken.expiresAt) return cachedToken.value;
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
    const body = await res.text().catch(() => "<unreadable>");
    let parsed: any = {};
    try { parsed = JSON.parse(body); } catch { /* not JSON */ }
    throw new Error(`Gmail token refresh failed: ${parsed.error ?? res.status} — ${parsed.error_description ?? body}`);
  }
  const data = await res.json() as any;
  cachedToken = { value: data.access_token as string, expiresAt: now + (data.expires_in - 60) * 1000 };
  return cachedToken.value;
}

// deno-lint-ignore no-explicit-any
function getGmailToken(extra: unknown): string {
  // deno-lint-ignore no-explicit-any
  const token = (extra as any)?.authInfo?.extra?.gmailToken;
  if (!token) throw new Error("missing gmailToken in authInfo.extra");
  return token;
}

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

function sanitizeHeader(value: string, field: string): string {
  if (/[\r\n]/.test(value)) throw new Error(`Header injection attempt in ${field}`);
  return value;
}

function buildRfc2822(to: string, subject: string, body: string, replyToId?: string): string {
  const lines = [
    `To: ${sanitizeHeader(to, "to")}`,
    `Subject: ${sanitizeHeader(subject, "subject")}`,
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

function toUrlSafeBase64(str: string): string {
  const bytes = new TextEncoder().encode(str);
  let binary = "";
  for (const b of bytes) binary += String.fromCharCode(b);
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function okResult(data: unknown) {
  return { content: [{ type: "text" as const, text: JSON.stringify(data, null, 2) }] };
}

// MCP server created once at module level — tools registered once per cold start
const server = new McpServer({ name: "gmail-mcp", version: "0.1.0" });

// deno-lint-ignore no-explicit-any
const registerTool: (...args: any[]) => void = server.registerTool.bind(server);

registerTool(
  "search_emails",
  {
    title: "Search Emails",
    description: "Search Gmail messages using a query string. Returns message metadata (id, subject, from, date, snippet).",
    inputSchema: z.object({
      query: z.string().describe("Gmail search query (e.g. 'from:recruiter is:unread')"),
      max_results: z.number().int().min(1).max(50).default(20).optional(),
    }),
  },
  async ({ query, max_results }: { query: string; max_results?: number }, extra: unknown) => {
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
        if (!metaRes.ok) {
          console.error(`Gmail metadata fetch failed for message ${m.id}: ${metaRes.status}`);
          return { id: m.id, threadId: m.threadId, subject: "", from: "", date: "", snippet: "", fetchError: true };
        }
        const meta = await metaRes.json() as any;
        const hdrs: Record<string, string> = {};
        for (const h of meta.payload?.headers ?? []) hdrs[h.name] = h.value;
        return {
          id: m.id,
          threadId: m.threadId,
          subject: hdrs["Subject"] ?? "",
          from: hdrs["From"] ?? "",
          date: hdrs["Date"] ?? "",
          snippet: meta.snippet ?? "",
        };
      }),
    );
    return okResult(results);
  }
);

registerTool(
  "read_email",
  {
    title: "Read Email",
    description: "Fetch the full content of a Gmail message by its ID.",
    inputSchema: z.object({
      message_id: z.string().describe("Gmail message ID (from search_emails results)"),
    }),
  },
  async ({ message_id }: { message_id: string }, extra: unknown) => {
    const token = getGmailToken(extra);
    const res = await fetch(
      `https://gmail.googleapis.com/gmail/v1/users/me/messages/${message_id}?format=full`,
      { headers: { Authorization: `Bearer ${token}` } },
    );
    if (!res.ok) throw new Error(`Gmail get failed: ${res.status} ${await res.text()}`);
    const data = await res.json() as any;
    const hdrs: Record<string, string> = {};
    for (const h of data.payload?.headers ?? []) hdrs[h.name] = h.value;
    return okResult({
      id: data.id,
      threadId: data.threadId,
      subject: hdrs["Subject"] ?? "",
      from: hdrs["From"] ?? "",
      to: hdrs["To"] ?? "",
      date: hdrs["Date"] ?? "",
      snippet: data.snippet ?? "",
      body: extractBody(data.payload),
    });
  }
);

registerTool(
  "draft_email",
  {
    title: "Draft Email",
    description: "Create a Gmail draft. Optionally threads it as a reply by providing reply_to_message_id.",
    inputSchema: z.object({
      to: z.string().describe("Recipient email address"),
      subject: z.string().describe("Email subject"),
      body: z.string().describe("Plain text email body"),
      reply_to_message_id: z.string().optional().describe("Gmail message ID to reply to"),
    }),
  },
  async ({ to, subject, body, reply_to_message_id }: { to: string; subject: string; body: string; reply_to_message_id?: string }, extra: unknown) => {
    const token = getGmailToken(extra);
    const raw = toUrlSafeBase64(buildRfc2822(to, subject, body, reply_to_message_id));
    const res = await fetch("https://gmail.googleapis.com/gmail/v1/users/me/drafts", {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify({ message: { raw } }),
    });
    if (!res.ok) throw new Error(`Gmail draft failed: ${res.status} ${await res.text()}`);
    const data = await res.json() as any;
    return okResult({
      draft_id: data.id,
      message_id: data.message?.id,
      thread_id: data.message?.threadId,
    });
  }
);

registerTool(
  "list_labels",
  {
    title: "List Labels",
    description: "List all Gmail labels (system and user-created).",
    inputSchema: z.object({}),
  },
  async (_input: Record<string, never>, extra: unknown) => {
    const token = getGmailToken(extra);
    const res = await fetch("https://gmail.googleapis.com/gmail/v1/users/me/labels", {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error(`Gmail labels failed: ${res.status} ${await res.text()}`);
    const data = await res.json() as any;
    const labels = (data.labels ?? []).map((l: any) => ({ id: l.id, name: l.name, type: l.type }));
    return okResult(labels);
  }
);

const fetchHandler = async (req: Request): Promise<Response> => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });

  const url = new URL(req.url);
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

  let gmailToken: string;
  try {
    gmailToken = await getOrRefreshGmailToken();
  } catch (err) {
    return Response.json(
      { error: `OAuth token refresh failed: ${(err as Error).message}` },
      { status: 502, headers: corsHeaders },
    );
  }

  const transport = new WebStandardStreamableHTTPServerTransport();
  await server.connect(transport);
  return transport.handleRequest(req, {
    authInfo: { token: auth.token ?? "", clientId: "gmail-mcp", scopes: [], extra: { gmailToken } },
  });
};

export default { fetch: fetchHandler };
