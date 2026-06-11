# RESUME — Loop 3 (`morning-briefing`, the daily pro+perso dashboard) — start here

> Terrain prepared 2026-06-11 from the `bluegreen-marketplace` session that shipped Loop 2
> (`/hal tasks` v0.7.0). Loop 3 is **skills only**, in **this repo** (`renaud-marketplace`).
> hal-mcp is **frozen at v38** — you only *consume* its tools, never add or change one.

## What this loop is

One skill, one view: Renaud's **whole day** — business + perso + jobsearch — merged read-only from
three backends. It's the single pane of glass that makes the "two backends, one view" architecture
pay off, and the most-used skill of the plan.

- **Master plan**: `../hal/docs/lastdev-plan.md` (the 4 loops, freeze line, deadline Sun 2026-06-14).
- **Brief**: relocated here → [`docs/loop-3-morning-briefing.md`](docs/loop-3-morning-briefing.md)
  (Archon runs from this repo, so the brief lives here).

## Decisions already locked (don't re-litigate)

1. **Repo = `renaud-marketplace`.** Not bluegreen-marketplace — that one is the *client-facing*
   business marketplace; a perso briefing (family calendar, jobsearch, perso tasks) doesn't ship to
   clients. renaud-marketplace is "mes skills". Loops 3 **and** 4 both live here.
2. **Host = new plugin `briefing`** (not a skill bolted onto `jobsearch`). Clean separation: the
   briefing aggregates everything; `jobsearch` stays focused on CV + Gmail.
3. **hal-mcp is declared in `briefing/.mcp.json`** (self-contained), even though
   `bluegreen-marketplace/plugins/hal` also declares it. Claude Code **deduplicates MCP servers by
   name + endpoint** → one connection, no conflict, no tool collision. Declaring it means the
   briefing never silently breaks with "tool not found" if the hal plugin happens to be absent.
   *(Verified against Claude Code docs — MCP scope hierarchy: plugins/connectors match by endpoint.)*

## Pre-flight (do first — four sources, probe each)

The briefing composes four backends. Probe all four before building; the skill must degrade loudly
(criterion 3) if any is down.

1. **hal-mcp** (tasks) — OAuth-connected (http, URL only, no auth header). Call `whoami` → expect
   `renaud@bluegreen.ai` + workspaces `blue-green` (default), `ic-ingenieurs-conseils`, `renaud`.
   200 = reachable + provisioned. URL: `https://zgkvbjqlvebttbnkklpo.supabase.co/functions/v1/hal-mcp`.
2. **Obsidian jobsearch** — via the global `obsidian-crm` skill (dual-mode: REST when Obsidian runs,
   filesystem when the vault is mounted). It's a *skill*, not an MCP server — no `.mcp.json` entry.
3. **Google Calendar** — via the claude.ai Google Calendar MCP connector
   (`mcp__claude_ai_Google_Calendar__list_events` / `list_calendars`). Session-level connector, not a
   repo `.mcp.json`. Three calendars to merge:
   - `renaud@bluegreen.ai` (pro Blue Green)
   - `rlaborbe@gmail.com` (perso / job search)
   - `hah0feg81cofndkov7derd6g00@group.calendar.google.com` (famille)
4. **gmail-mcp** (optional, for jobsearch relances) — already wired in `jobsearch/.mcp.json`,
   URL `https://isdyvrwnxqcfalmlkzui.supabase.co/functions/v1/gmail-mcp`. Re-declare in
   `briefing/.mcp.json` if the briefing reads emails directly (else rely on `obsidian-crm` for
   relance state — decide during the loop).

## The exact data pulls (compose, don't reinvent)

- **hal tasks, both workspaces** — per workspace `w` in [`blue-green`, `renaud`]:
  `list_sprints(workspace_slug=w, status="actuel")` → take the sprint `id` →
  `list_tasks(workspace_slug=w, sprint_id=<id>)`. No current sprint → say so for that workspace,
  fall back to its open tasks (mirror the `/hal tasks` Loop 2 behavior — never a silent empty board).
  Label each task with its workspace (business vs perso).
- **Obsidian jobsearch** — through `obsidian-crm`: upcoming interviews, relances due, active
  candidatures. Do not write the vault.
- **3 calendars** — `list_events` per calendar id, merged for today + the next event.

## Plugin skeleton (Loop 3 creates this — not pre-scaffolded on purpose)

Let Loop 3 build it in one pass so versions + wiring land together:

```
plugins/briefing/
├── .claude-plugin/plugin.json          # name: "briefing", version: 0.1.0
├── .mcp.json                           # hal-mcp (+ gmail-mcp if used) — http URLs above
├── skills/morning-briefing/SKILL.md    # version: 0.1.0 frontmatter
├── commands/briefing.md                # optional /briefing slash command (self-contained)
└── CHANGELOG.md                        # [0.1.0] entry
```

Then register it in `.claude-plugin/marketplace.json`: add a second `plugins[]` entry
(`"name": "briefing"`, `"version": "0.1.0"`, `"source": "./plugins/briefing"`,
`"skills": ["./plugins/briefing/skills/morning-briefing"]`).

## Versioning (this repo's rule — stricter than bluegreen-marketplace)

Per `CLAUDE.md` + `README.md`: **4 fields in sync per plugin**, or Cowork won't detect updates —
`marketplace.json` top-level `version`, `marketplace.json` plugins[].version, `plugin.json` version,
`SKILL.md` frontmatter `version:`. New plugin `briefing` starts all at **0.1.0**.
> ⚠️ Open question for Loop 3: the marketplace now has **two** plugins (`jobsearch` 0.2.0 +
> `briefing` 0.1.0). The top-level `marketplace.json` version was single-plugin until now — decide
> whether it tracks the latest-changed plugin or gets its own line. Simplest: bump top-level on each
> release to the version of the plugin that changed.

## Acceptance criteria (from the brief)

1. One brief covering the 3 calendars + hal tasks (both workspaces) + Obsidian jobsearch, no manual
   workspace juggling.
2. A perso task (`renaud`) and a business task (`blue-green`) both appear, correctly labelled.
3. A source down → the brief **says which one failed, loudly**, and still renders the rest. Never a
   silent omission that reads as "empty".

## Guardrails

- **Read-only.** No task creation, no calendar writes, no CRM mutation. The briefing *composes*
  `/hal tasks` and `obsidian-crm`; it never reimplements them.
- **hal-mcp is frozen v38** — if you feel you need a new tool/param, you're doing Loop 3 wrong.
- Run Loop 3 via the **`archon` skill** from *this* repo, or hand-build — do not raw-`archon
  workflow run` from Bash.
- After merge, update this repo's `.claude/STATUS.md` (Loop 3 done) and delete this file.

## After Loop 3 — Loop 4 (same repo, then STOP)

Loop 4 = systematize jobsearch here + Obsidian: **`log-application`** (annonce + source → Obsidian
note + follow-up task) and **`interview-prep`** (fixed structure, wired to the 5 CV profiles). The
briefing *reads* what Loop 4 *writes*. Brief: `../hal/docs/features/loop-4-jobsearch-systematization.md`
(relocate here when it runs). **Deadline Sun 2026-06-14 → the LastDev chain STOPS.**
