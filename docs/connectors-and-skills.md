# Installing connectors & skills — Claude, Gemini, OpenAI

How to connect this marketplace's MCP servers (**connectors**) and `SKILL.md` files
(**skills**) across the three major AI providers.

Read this first: **a connector and a skill are two different things with different reach.**

| | What it is | Where it installs |
|---|---|---|
| **Connector** | A remote **MCP server** (Supabase Edge Function) exposing tools | **Every** surface: Claude (Code / Desktop / claude.ai), Gemini (Enterprise / CLI), ChatGPT |
| **Skill** | A `SKILL.md` capability file (`cv-generator`, `morning-briefing`, …) | **Only the agent/CLI surfaces**: Claude Code, Gemini **CLI**, OpenAI **Codex** — via the [agentskills.io](https://agentskills.io) standard. **Not** the chat apps. |

The full skill experience (CV generation, interview prep, briefing) lives in **Claude Code /
Cowork**. The chat apps only call a connector's tools — they can't run a skill.

---

## Our servers — the facts that drive everything below

| Plugin | MCP server | Project ref | Auth model |
|--------|-----------|-------------|-----------|
| `jobsearch` | `gmail-mcp` | `isdyvrwnxqcfalmlkzui` | **API key** via `?key=` query param + `apikey` header — **no OAuth server** |
| `briefing` | `hal-mcp` | `zgkvbjqlvebttbnkklpo` | **OAuth 2.1** (full discovery + DCR) — shared with bluegreen-marketplace |

This split matters:

- **`hal-mcp`** runs a full OAuth server → connects to **every** provider (Claude, ChatGPT,
  Gemini CLI by URL alone; Gemini Enterprise with manual endpoints).
- **`gmail-mcp`** has **no OAuth server** → it authenticates with a shared secret passed as
  `?key=<GMAIL_API_KEY>`. That works for Claude Code and claude.ai, but **limits the other
  providers** (see §6).

URLs:
- `gmail-mcp`: `https://isdyvrwnxqcfalmlkzui.supabase.co/functions/v1/gmail-mcp`
- `hal-mcp`: `https://zgkvbjqlvebttbnkklpo.supabase.co/functions/v1/hal-mcp`

---

## 1. Claude — primary, fully supported

### 1a. Claude Code / Cowork (full skills + connectors)

```
/plugin marketplace add BluegReeno/renaud-marketplace jobsearch
/plugin marketplace add BluegReeno/renaud-marketplace briefing
```

Installing a plugin registers its skills **and** its connector. For `gmail-mcp` the `apikey`
header carries the secret:

```
claude mcp add --transport http gmail-mcp \
  https://isdyvrwnxqcfalmlkzui.supabase.co/functions/v1/gmail-mcp \
  --header "apikey: <GMAIL_API_KEY>"
```

`hal-mcp` (briefing) authenticates via OAuth — run `/mcp` to complete the browser flow.

### 1b. Claude Desktop / claude.ai (connectors only — no skills)

`Settings → Connectors` → **Add custom connector** → paste the URL.

- **`hal-mcp`**: paste the bare URL — OAuth discovery is automatic.
- **`gmail-mcp`**: the claude.ai/Cowork connector UI can't send custom headers, so paste the
  **keyed URL**: `…/functions/v1/gmail-mcp?key=<GMAIL_API_KEY>`. The server returns 200 and
  never starts an OAuth flow. ⚠️ Never commit the keyed URL — paste it only in the dialog.

---

## 2. Gemini

### 2a. Gemini Enterprise — connector via "Custom MCP Server" data store

Classic OAuth: you paste endpoints manually (no discovery / no dynamic registration).
Status: **Preview** — UI labels drift.

- **`hal-mcp` works** here. Google Cloud console → Gemini Enterprise → **Data stores** →
  **Create data store** → search **Custom MCP Server** → enter the `hal-mcp` URL, **Streamable
  HTTP** transport, and the OAuth fields:
  - Authorization URI: `https://zgkvbjqlvebttbnkklpo.supabase.co/auth/v1/authorize`
  - Token URI: `https://zgkvbjqlvebttbnkklpo.supabase.co/auth/v1/token`
  - Client ID / Secret: from a **pre-registered** Supabase OAuth client (Gemini can't do
    dynamic registration). Register Google's redirect URI
    `https://vertexaisearch.cloud.google.com/oauth-redirect` on the Supabase side.
  - Then **Login** to verify, **Continue**, and **enable the tools** (disabled by default).
- **`gmail-mcp` does NOT work** here as-is: Gemini Enterprise's *only* auth mechanism is OAuth,
  and gmail-mcp has no OAuth server (key mode only). To support it you'd first enable the
  Supabase OAuth server on project `isdyvrwnxqcfalmlkzui` (same setup as hal-mcp).

**Workspace Admin enablement:** `admin.google.com` → Menu → **Generative AI** → **Gemini app**
→ **Apps** → allow access (Gemini Settings administrator privilege; up to 24 h to propagate).

### 2b. Gemini CLI — connectors + skills

OAuth **discovery** (no manual endpoints) and the `SKILL.md` standard. Edit
`~/.gemini/settings.json` `mcpServers` with an `httpUrl` + `"oauth": { "enabled": true }`
entry, then `/mcp auth <server>`. Skills live in `~/.gemini/skills/` (alias `~/.agents/skills/`),
so the §4 symlinks apply. `hal-mcp` connects by URL; `gmail-mcp` would need the keyed URL or an
OAuth server.

---

## 3. OpenAI / ChatGPT — connectors only (no skills in the chat app)

Needs **Developer Mode** for write tools.

1. `Settings → Apps & Connectors → Advanced settings → Developer mode` → **ON**.
2. `Settings → Apps & Connectors → Add new connector`.
3. URL + **Authentication = OAuth** → **Create**.

- **`hal-mcp` works**: ChatGPT discovers the auth server and self-registers (PKCE).
- **`gmail-mcp`**: ⚠️ ChatGPT **rejects API keys in query params as unsafe** and prefers header
  bearer auth, which the connector UI can't send. So gmail-mcp is **not reliably installable**
  on ChatGPT until it has an OAuth server. Use Claude Code / Cowork for gmail-mcp.

Available on Plus / Pro / Business / Enterprise / Edu — web only, beta (Free excluded).
⚠️ ChatGPT's dynamic registration is unstable mid-2026 — keep a static Supabase OAuth client
as a fallback `client_id`.

> The job-search *skills* run in **Codex** (which adopted `SKILL.md`) via `.agents/skills/`,
> not in the ChatGPT chat app.

---

## 4. Skills cross-client (Claude Code / Gemini CLI / Codex)

The `SKILL.md` files comply with the [agentskills.io](https://agentskills.io/specification)
standard. To expose them to Gemini CLI and Codex, symlink them under `.agents/skills/` at the
repo root, e.g.:

```bash
mkdir -p .agents/skills
ln -sf "$(pwd)/plugins/jobsearch/skills/cv-generator"  .agents/skills/cv-generator
ln -sf "$(pwd)/plugins/jobsearch/skills/interview-prep" .agents/skills/interview-prep
# …one symlink per skill
```

No frontmatter change needed. Chat apps ignore `.agents/skills/`.

---

## 5. Provider matrix (cheat sheet)

| | `hal-mcp` (OAuth) | `gmail-mcp` (key) | Skills? |
|---|---|---|---|
| **Claude Code / Cowork** | ✅ OAuth or header | ✅ `apikey` header | ✅ native |
| **Claude Desktop / claude.ai** | ✅ paste URL | ✅ paste `?key=` URL | ❌ |
| **Gemini Enterprise** | ✅ manual OAuth fields | ❌ needs OAuth server | ❌ |
| **Gemini CLI** | ✅ by URL | ⚠️ keyed URL | ✅ via `.agents/skills/` |
| **ChatGPT (Dev Mode)** | ✅ OAuth | ❌ query-key rejected as unsafe | ❌ |
| **OpenAI Codex** | ✅ | ⚠️ keyed URL | ✅ via `.agents/skills/` |

**Takeaway:** for full multi-provider reach, `gmail-mcp` would need its own Supabase OAuth
server (same setup as `hal-mcp`). Until then, treat `gmail-mcp` as a **Claude Code / Cowork**
connector.

---

## 6. Verify a server is connectable (from a machine with network access)

```bash
# OAuth discovery (hal-mcp) — must return JSON with authorization_servers
curl https://zgkvbjqlvebttbnkklpo.supabase.co/functions/v1/hal-mcp/.well-known/oauth-protected-resource

# gmail-mcp key mode — keyed URL should reach the MCP initialize (200), wrong key → 401
npx @modelcontextprotocol/inspector \
  "https://isdyvrwnxqcfalmlkzui.supabase.co/functions/v1/gmail-mcp?key=<GMAIL_API_KEY>"
```

Server-side OAuth / Edge Function implementation reference:
[`mcp-server-supabase-edge.md`](mcp-server-supabase-edge.md).

---

## Sources

- Claude — connectors & MCP: <https://support.claude.com/en/articles/11503834-build-custom-connectors-via-remote-mcp-servers>, <https://code.claude.com/docs/en/mcp>
- Gemini Enterprise custom MCP: <https://docs.cloud.google.com/gemini/enterprise/docs/connectors/custom-mcp-server/set-up-custom-mcp-server>
- Gemini Workspace admin: <https://support.google.com/a/answer/15293691>
- OpenAI developer mode / connectors: <https://help.openai.com/en/articles/12584461-developer-mode-apps-and-full-mcp-connectors-in-chatgpt-beta>
- MCP authorization spec: <https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization>
- Agent Skills standard: <https://agentskills.io/specification>
</content>
