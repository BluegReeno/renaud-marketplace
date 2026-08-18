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
| `briefing` | `gmail-mcp` | `isdyvrwnxqcfalmlkzui` | **Two paths**: shared API key (`?key=` / `apikey` header) **or** OAuth 2.1 user JWT, gated by the `GMAIL_ALLOWED_USER_IDS` allowlist |
| `briefing` | `hal-mcp` | `zgkvbjqlvebttbnkklpo` | **OAuth 2.1** (full discovery + DCR) — shared with bluegreen-marketplace |

Both projects run a Supabase OAuth server. Verified on 2026-08-05 against
`https://isdyvrwnxqcfalmlkzui.supabase.co/auth/v1/.well-known/oauth-authorization-server`:
issuer, authorization/token/userinfo endpoints and a `registration_endpoint` (dynamic
client registration) are all live, and `gmail-mcp` advertises it through
`/.well-known/oauth-protected-resource`. An MCP client that follows discovery — Claude Code
does — completes the OAuth flow and calls in **`user` mode with a Supabase JWT**, never
touching `GMAIL_API_KEY`.

⚠️ **This document previously claimed `gmail-mcp` had no OAuth server. That was wrong**, and
the error was not cosmetic: it made the `#80` allowlist look like it could not affect any
client, when in fact it governs the path the `briefing` plugin actually uses. A JWT proves
only that the caller is *some* provisioned user on the project — `GMAIL_ALLOWED_USER_IDS`
is what proves they own this mailbox. Unset or empty ⇒ every `user`-mode call is rejected
(fail closed). See `servers/gmail-mcp/README.md` §Access control.

The remaining difference between the two servers:

- **`hal-mcp`** — OAuth is the only path in.
- **`gmail-mcp`** — OAuth *or* the shared `GMAIL_API_KEY`. The key path carries no per-user
  identity and is therefore owner-only by construction; it exists because the claude.ai /
  Cowork connector UI cannot send custom headers.

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

Installing a plugin registers its skills **and** its connector. `plugins/briefing/.mcp.json`
declares the bare URL with **no header and no `?key=`**, so Claude Code follows OAuth
discovery and authenticates as a user — run `/mcp` to complete the browser flow, exactly as
for `hal-mcp`. Your Supabase `user_id` must be in `GMAIL_ALLOWED_USER_IDS` or every call
returns `403 This Supabase account is not authorized for this mailbox`.

The header path stays available for a manual registration outside the plugin:

```
claude mcp add --transport http gmail-mcp \
  https://isdyvrwnxqcfalmlkzui.supabase.co/functions/v1/gmail-mcp \
  --header "apikey: <GMAIL_API_KEY>"
```

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
- **`gmail-mcp`**: the blocker written here — "no OAuth server" — no longer holds; project
  `isdyvrwnxqcfalmlkzui` runs one. What remains is the same limit as `hal-mcp`: Gemini
  Enterprise cannot do dynamic registration, so it needs a **pre-registered** Supabase OAuth
  client with Google's redirect URI. ⚠️ Never actually attempted against gmail-mcp — treat as
  plausible, not verified.

**Workspace Admin enablement:** `admin.google.com` → Menu → **Generative AI** → **Gemini app**
→ **Apps** → allow access (Gemini Settings administrator privilege; up to 24 h to propagate).

### 2b. Gemini CLI — connectors + skills

OAuth **discovery** (no manual endpoints) and the `SKILL.md` standard. Edit
`~/.gemini/settings.json` `mcpServers` with an `httpUrl` + `"oauth": { "enabled": true }`
entry, then `/mcp auth <server>`. Skills live in `~/.gemini/skills/` (alias `~/.agents/skills/`),
so the §4 symlinks apply. Both servers advertise OAuth discovery, so both should connect by
URL alone (`gmail-mcp` still requires the caller's `user_id` in the allowlist); the keyed URL
remains the fallback. ⚠️ Not verified for `gmail-mcp`.

---

## 3. OpenAI / ChatGPT — connectors only (no skills in the chat app)

Needs **Developer Mode** for write tools.

1. `Settings → Apps & Connectors → Advanced settings → Developer mode` → **ON**.
2. `Settings → Apps & Connectors → Add new connector`.
3. URL + **Authentication = OAuth** → **Create**.

- **`hal-mcp` works**: ChatGPT discovers the auth server and self-registers (PKCE).
- **`gmail-mcp`**: ChatGPT **rejects API keys in query params as unsafe**, so the keyed URL is
  out — but the OAuth path exists (project `isdyvrwnxqcfalmlkzui` supports discovery + DCR),
  and the caller would additionally have to be in `GMAIL_ALLOWED_USER_IDS`. ⚠️ Never attempted.
  Use Claude Code / Cowork for gmail-mcp until someone tries it.

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

| | `hal-mcp` (OAuth) | `gmail-mcp` (OAuth + key) | Skills? |
|---|---|---|---|
| **Claude Code / Cowork** | ✅ OAuth or header | ✅ OAuth (what the plugin uses) or `apikey` header | ✅ native |
| **Claude Desktop / claude.ai** | ✅ paste URL | ✅ paste `?key=` URL | ❌ |
| **Gemini Enterprise** | ✅ manual OAuth fields | ⚠️ pre-registered OAuth client — untried | ❌ |
| **Gemini CLI** | ✅ by URL | ⚠️ OAuth by URL (untried) or keyed URL | ✅ via `.agents/skills/` |
| **ChatGPT (Dev Mode)** | ✅ OAuth | ⚠️ OAuth untried; query-key rejected as unsafe | ❌ |
| **OpenAI Codex** | ✅ | ⚠️ keyed URL | ✅ via `.agents/skills/` |

**Takeaway:** `gmail-mcp` is only *proven* on Claude Code / Cowork (OAuth) and claude.ai
(keyed URL). Everything marked ⚠️ became plausible the day the OAuth server was enabled on
`isdyvrwnxqcfalmlkzui`, and nobody has tried any of it. Two callers on the OAuth path are
never equivalent: authentication says *who*, `GMAIL_ALLOWED_USER_IDS` says *whether*.

---

## 6. Verify a server is connectable (from a machine with network access)

```bash
# OAuth discovery (hal-mcp) — must return JSON with authorization_servers
curl https://zgkvbjqlvebttbnkklpo.supabase.co/functions/v1/hal-mcp/.well-known/oauth-protected-resource

# gmail-mcp key mode — keyed URL should reach the MCP initialize (200), wrong key → 401
npx @modelcontextprotocol/inspector \
  "https://isdyvrwnxqcfalmlkzui.supabase.co/functions/v1/gmail-mcp?key=<GMAIL_API_KEY>"

# gmail-mcp OAuth path — the authorization server must answer with a registration_endpoint
curl https://isdyvrwnxqcfalmlkzui.supabase.co/auth/v1/.well-known/oauth-authorization-server

# gmail-mcp allowlist — a JWT for a user NOT in GMAIL_ALLOWED_USER_IDS must return 403
# (401 instead means the deployed build predates the allowlist)
curl -s -o /dev/null -w '%{http_code}\n' -X POST \
  https://isdyvrwnxqcfalmlkzui.supabase.co/functions/v1/gmail-mcp \
  -H "Authorization: Bearer <supabase-user-jwt>" -H "content-type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
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
