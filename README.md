# renaud-marketplace

Personal Claude Code plugin marketplace — MCP servers and AI skills for daily productivity and job-search workflows.

Powered by [hal](https://github.com/BluegReeno/hal) — the AI foundation a small firm or a person
runs on (pipeline, work, memory, documents) — and gmail-mcp (email workflows). The plugins here
are **life-domains**, not hal pillars: a daily briefing, a job search, a weekly check-in. They
store into hal's pillars because that is where structured rows live, which is a storage fact and
not a statement about what they are for.

---

## Repository layout

```
renaud-marketplace/
├── .claude-plugin/
│   └── marketplace.json          ← Cowork entry point (top-level version = monotonic counter, +0.0.1 per release)
├── plugins/
│   ├── jobsearch/                ← job-search umbrella plugin
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json       ← (VERSION LIVES HERE)
│   │   ├── skills/                ← NO .mcp.json here: gmail-mcp belongs to the `briefing` plugin
│   │   │   ├── cv-generator/SKILL.md       ← skill (no version in the frontmatter)
│   │   │   ├── cover-letter/SKILL.md       ← skill
│   │   │   ├── log-application/SKILL.md    ← skill
│   │   │   ├── interview-prep/SKILL.md     ← skill
│   │   │   ├── log-cr/SKILL.md             ← post-interview debrief (BANT template)
│   │   │   ├── jobsearch-vault/SKILL.md    ← filesystem-only vault I/O (shared library)
│   │   │   ├── read-job-offer/SKILL.md     ← LinkedIn JD reader (shared primitive, no browser)
│   │   │   └── apply-to-offer/SKILL.md     ← manual offer → CV + logged candidature
│   │   ├── commands/             ← slash commands
│   │   │   ├── cover-letter.md
│   │   │   ├── interview-prep.md
│   │   │   └── log-application.md
│   │   ├── profiles/             ← p1-p5 narrative files (read by cv-generator + interview-prep)
│   │   ├── scripts/              ← Python - generate_cv.py, batch_validate.py
│   │   ├── data/                 ← cv-master.json, comp-thresholds.json (the only definition
│   │   │                            site of comp_floor_eur / target_comp_eur / fire_tier_min_eur,
│   │   │                            read by cv-log-worker and morning-briefing)
│   │   └── templates/            ← cv_template.html
│   ├── briefing/                 ← daily briefing plugin
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json       ← (VERSION LIVES HERE)
│   │   ├── .mcp.json             ← gmail-mcp MCP server declaration (url + MCP version) - hal-mcp stays with the `hal` plugin
│   │   ├── skills/
│   │   │   ├── morning-briefing/SKILL.md   ← skill (no version in the frontmatter)
│   │   │   ├── mail-triage/SKILL.md        ← skill
│   │   │   └── book-appointment/SKILL.md   ← calendar write (create-only, interactive)
│   │   ├── agents/
│   │   │   └── cv-log-worker.md  ← fan-out subagent called by morning-briefing
│   │   └── commands/
│   │       └── briefing.md       ← trigger slash command
│   ├── improve/                  ← capture an observation → GitHub Issue
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/improve/SKILL.md
│   ├── mycoach/                  ← weekly check-in (writes to hal)
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/mycoach/SKILL.md
│   └── session/                  ← wrap-up: close a session cleanly or hand it off
│       ├── .claude-plugin/plugin.json
│       └── skills/wrap-up/SKILL.md
├── servers/
│   └── gmail-mcp/               ← Supabase Edge Function (Deno/TypeScript)
│       ├── scripts/setup_secrets.sh
│       └── supabase/
│           ├── config.toml
│           └── functions/gmail-mcp/
│               ├── deno.json
│               └── index.ts     ← McpServer version lives here (independent of the plugin)
├── scripts/                     ← release tooling + CI guards
│   ├── release.sh               ← bump 4 fields + CHANGELOG in one pass
│   ├── check_version_sync.sh    ← drift plugin.json ↔ marketplace.json ↔ CHANGELOG
│   ├── check_marketplace_schema.sh
│   ├── check_no_identity_literals.sh  ← no hardcoded calendar_id / mail / workspace_slug
│   └── generate_improve_map.py  ← skill→plugin→repo table for the `improve` skill
├── probes/                      ← replayable runtime probes (hal-runtime-probe.html)
└── docs/
    ├── skill-marketplace-guide.md
    ├── connectors-and-skills.md
    └── mcp-server-supabase-edge.md
```

### Anatomy of a plugin

```
plugins/<plugin>/
├── .claude-plugin/plugin.json   ← name + version (= the plugins[] entry in marketplace.json)
├── .mcp.json                    ← optional - { "mcpServers": { "<name>": { "type":"http", "url":"...", "version":"..." } } }
├── skills/<skill>/SKILL.md      ← frontmatter: name, description (no version)
└── scripts/                     ← invoked from SKILL.md through uv run --with
```

⚠️ **Exactly one plugin declares a given MCP server.** Claude Code deduplicates by URL: two
`.mcp.json` files pointing at the same address mount one or the other arbitrarily, and the
resolved tool name becomes non-deterministic. `plugins/briefing/.mcp.json` was removed for that
reason on 2026-07-23 — `hal-mcp` belongs to the `hal` plugin in `bluegreen-marketplace`, and its
tools are named `mcp__plugin_hal_hal-mcp__*`.

### .mcp.json — exact format

```json
{
  "mcpServers": {
    "gmail-mcp": {
      "type": "http",
      "url": "https://<ref>.supabase.co/functions/v1/<function>",
      "version": "0.1.0"
    }
  }
}
```

Without this file, Cowork does not know an MCP server is attached to the plugin.

---

## Plugins

**Versions are deliberately absent from this table.** It carried them until 2026-09-08 and was
wrong on three of four — `jobsearch` 0.11.6 against 0.15.1, `briefing` 0.16.2 against 0.18.0,
`improve` 0.3.0 against 0.3.2 — with a warning that it was only a snapshot, which repaired
nothing. Read `.claude-plugin/marketplace.json` and `plugins/<plugin>/.claude-plugin/plugin.json`,
which `scripts/check_version_sync.sh` keeps identical.

| Plugin | Skills | MCP server | Description |
|--------|--------|-------------|-------------|
| `jobsearch` | `cv-generator`, `cover-letter`, `log-application`, `interview-prep`, `log-cr`, `jobsearch-vault`, `read-job-offer`, `apply-to-offer` | `gmail-mcp` **through the `briefing` plugin** | CV generation, cover letter, application logging, interview prep, debrief logging, job-search vault I/O (filesystem-only, shared library), LinkedIn job-description reading, and the manual offer→CV route |
| `briefing` | `morning-briefing`, `mail-triage`, `book-appointment` (+ agent `cv-log-worker`) | `gmail-mcp` (declared here), `hal-mcp` **through the `hal` plugin** | Daily briefing, mail triage and appointment booking (calendars resolved from the hal workspaces, hal tasks, jobsearch-vault). Since 0.12.0, `sprint-planner` and `sprint-review` live in `pm@bluegreen-marketplace` |
| `improve` | `improve` | — | Capture an observation about a skill → GitHub Issue in ≤30 s from Cowork (`/improve`) |
| `mycoach` | `mycoach` | `hal-mcp` **through the `hal` plugin** | Weekly personal-development check-in — a structured CBT/SFBT session backed by a private OKF knowledge base |

`briefing` and `mycoach` **require the `hal` plugin** (`bluegreen-marketplace`) to be installed
for their `mcp__plugin_hal_hal-mcp__*` calls — neither declares that server. `jobsearch` in turn
requires the `briefing` plugin for its single gmail-mcp call
(`cover-letter` → `mcp__plugin_briefing_gmail-mcp__draft_email`).

---

## Install

Public repository — no token needed. Add the marketplace, then install the plugins you want:

```bash
# 1. register the marketplace (once)
/plugin marketplace add BluegReeno/renaud-marketplace

# 2. install the plugins you want
/plugin install jobsearch@renaud-marketplace
/plugin install briefing@renaud-marketplace
/plugin install improve@renaud-marketplace
/plugin install mycoach@renaud-marketplace
```

### Connecting from Claude, Gemini, or OpenAI

The MCP servers (**connectors**) and the `SKILL.md` files (**skills**) install differently:
a connector works on all three providers, but skills only run on the agent/CLI surfaces
(Claude Code, Gemini CLI, Codex). Both servers run an OAuth 2.1 authorization server, so both
connect by URL alone; `gmail-mcp` additionally accepts a shared API key (`?key=`) for headerless
clients like claude.ai. The `briefing` plugin itself takes the **OAuth path** — its `.mcp.json`
carries the bare URL — and every caller, keyed or OAuth, is gated by the `GMAIL_ALLOWED_USER_IDS`
allowlist.

Full step-by-step per provider, the auth model, and the cross-client skills setup are in
[`docs/connectors-and-skills.md`](docs/connectors-and-skills.md).

---

## Deploy gmail-mcp

```bash
# 1. Configure the secrets (once)
bash servers/gmail-mcp/scripts/setup_secrets.sh

# 2. Deploy the function
cd servers/gmail-mcp
supabase link --project-ref isdyvrwnxqcfalmlkzui
supabase functions deploy --no-verify-jwt gmail-mcp
```

⚠️ **The Supabase account depends on the directory, through direnv.** `renaud-marketplace/.envrc`
carries the personal account's token, which owns `isdyvrwnxqcfalmlkzui`; running a `supabase`
command from `~/Projects/hal` would target the right project with the wrong account. If the CLI
refuses a `sbp_v0_…` PAT, see `servers/gmail-mcp/README.md` §*When the CLI refuses your token*.

See `docs/mcp-server-supabase-edge.md` for the full architecture, and
`docs/connectors-and-skills.md` for the per-client authentication model.

---

## Code conventions

- **No `pip install`** inside skills — `uv run --with <pkg>` only (a Cowork constraint)
- **No secrets in the clear** — `.gitignore` covers `tmp`, OAuth `*.json`, `.env`, `.temp/`
- Code, commits, filenames and docs: **English**. Conversations: French is fine.
