import * as supabaseServer from "@supabase/server/core";
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { WebStandardStreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { z } from "zod";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const RESOURCE_BASE_URL = `${SUPABASE_URL}/functions/v1/gmail-mcp`;
const AUTH_SERVER_URL = `${SUPABASE_URL}/auth/v1`;
const RESOURCE_METADATA_URL = `${RESOURCE_BASE_URL}/.well-known/oauth-protected-resource`;

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type, accept, mcp-session-id, mcp-protocol-version, last-event-id",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
};

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

function getGmailToken(extra: unknown): string {
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

const SearchEmailsInput = z.object({
  query: z.string().describe("Gmail search query (e.g. 'from:recruiter is:unread')"),
  max_results: z.number().int().min(1).max(50).default(20).optional(),
});

const ReadEmailInput = z.object({
  message_id: z.string().describe("Gmail message ID (from search_emails results)"),
});

const DraftEmailInput = z.object({
  to: z.string().describe("Recipient email address"),
  subject: z.string().describe("Email subject"),
  body: z.string().describe("Plain text email body"),
  reply_to_message_id: z.string().optional().describe("Gmail message ID to reply to (adds In-Reply-To/References headers)"),
});

const server = new Server(
  { name: "gmail-mcp", version: "0.1.0" },
  { capabilities: { tools: {} } },
);

server.tool("search_emails", SearchEmailsInput.shape, async (input, extra) => {
  const token = getGmailToken(extra);
  const maxResults = input.max_results ?? 20;
  const listRes = await fetch(
    `https://gmail.googleapis.com/gmail/v1/users/me/messages?q=${encodeURIComponent(input.query)}&maxResults=${maxResults}`,
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
  return { content: [{ type: "text", text: JSON.stringify(results, null, 2) }] };
});

server.tool("read_email", ReadEmailInput.shape, async (input, extra) => {
  const token = getGmailToken(extra);
  const res = await fetch(
    `https://gmail.googleapis.com/gmail/v1/users/me/messages/${input.message_id}?format=full`,
    { headers: { Authorization: `Bearer ${token}` } },
  );
  if (!res.ok) throw new Error(`Gmail get failed: ${res.status} ${await res.text()}`);
  const data = await res.json() as any;
  const hdrs: Record<string, string> = {};
  for (const h of data.payload?.headers ?? []) hdrs[h.name] = h.value;
  return {
    content: [{
      type: "text",
      text: JSON.stringify({
        id: data.id,
        threadId: data.threadId,
        subject: hdrs["Subject"] ?? "",
        from: hdrs["From"] ?? "",
        to: hdrs["To"] ?? "",
        date: hdrs["Date"] ?? "",
        snippet: data.snippet ?? "",
        body: extractBody(data.payload),
      }, null, 2),
    }],
  };
});

server.tool("draft_email", DraftEmailInput.shape, async (input, extra) => {
  const token = getGmailToken(extra);
  const raw = btoa(buildRfc2822(input.to, input.subject, input.body, input.reply_to_message_id))
    .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  const res = await fetch("https://gmail.googleapis.com/gmail/v1/users/me/drafts", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    body: JSON.stringify({ message: { raw } }),
  });
  if (!res.ok) throw new Error(`Gmail draft failed: ${res.status} ${await res.text()}`);
  const data = await res.json() as any;
  return {
    content: [{
      type: "text",
      text: JSON.stringify({
        draft_id: data.id,
        message_id: data.message?.id,
        thread_id: data.message?.threadId,
      }, null, 2),
    }],
  };
});

server.tool("list_labels", {}, async (_input, extra) => {
  const token = getGmailToken(extra);
  const res = await fetch("https://gmail.googleapis.com/gmail/v1/users/me/labels", {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`Gmail labels failed: ${res.status} ${await res.text()}`);
  const data = await res.json() as any;
  const labels = (data.labels ?? []).map((l: any) => ({ id: l.id, name: l.name, type: l.type }));
  return { content: [{ type: "text", text: JSON.stringify(labels, null, 2) }] };
});

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
