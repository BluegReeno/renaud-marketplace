# Loop 3 — `morning-briefing` skill (the daily dashboard, pro + perso)

> **Repo**: `renaud-marketplace` · **Target**: new plugin `plugins/briefing/` (decided at terrain-prep).
> **Depends on**: Loops 1 & 2 — the hal task surface is stable and **frozen at hal-mcp v38**.
> Relocated from `hal/docs/features/loop-3-morning-briefing.md` (Archon runs from this repo).
> A legacy `morning-briefing` exists on SynologyDrive (reads Notion + 3 Google Calendars) —
> **reference only**. This is a fresh skill for the hal-cloud + Obsidian architecture; Notion is dropped.

> 🛠️ **Decisions locked at terrain-prep (2026-06-11)** — these were left "decide at launch" in the
> original brief and are now settled (see `RESUME-LOOP3.md` for the rationale):
> - **Host**: a **new plugin `briefing`** in this repo (not a skill bolted onto `jobsearch`).
> - **hal-mcp wiring**: the `briefing` plugin **declares `hal-mcp`** in its own `.mcp.json`
>   (same http URL as `bluegreen-marketplace/plugins/hal`). Claude Code **deduplicates MCP servers
>   by name + endpoint** → one connection even when both marketplaces are installed. Declaring it
>   makes the briefing self-contained (no silent "tool not found" if the hal plugin is absent).

## Objective

One skill, one view: Renaud's **entire day** — business (Blue Green), perso, and jobsearch —
merged from the three backends, read-only. This is the single pane of glass that makes the
"data in two places, view in one" architecture pay off. It is the most-used skill of the whole
plan: if this is good, the daily loop works.

## Data sources (read-only — no writes)

1. **hal tasks** (via `hal-mcp`): current-sprint tasks for `blue-green` **and** `renaud`
   — `list_sprints(status:"actuel")` then `list_tasks(sprint_id:…)` per workspace. Both run under
   the `renaud@bluegreen.ai` identity (member of both → RLS lets it read both).
2. **Obsidian jobsearch** (via the `obsidian-crm` skill, dual-mode REST/filesystem): upcoming
   interviews, pending relances, active candidatures.
3. **3 Google Calendars** (Google Calendar MCP): `renaud@bluegreen.ai`, `rlaborbe@gmail.com`,
   family calendar — merged for today + next event.

## Output

A single morning brief: today's merged agenda (3 calendars), what's due / in the current sprint
across business + perso, and jobsearch actions (interviews to prep, relances due). Sectioned and
prioritized per `~/.claude/CLAUDE.md` priorities (job + revenue first).

## Non-goals

- **Read-only.** No task creation, no calendar writes, no CRM mutation.
- No Notion (CRM moved to hal + Obsidian).
- No auto-scheduling or auto-replanning.
- Does not re-implement `/hal tasks` or `obsidian-crm` — it **composes** them.

## Acceptance criteria

1. Running the skill produces one brief covering the 3 calendars + hal tasks (both workspaces) +
   Obsidian jobsearch, with no manual workspace juggling.
2. A perso task (workspace `renaud`) and a business task (`blue-green`) both appear, correctly labelled.
3. If a source is unreachable, the brief **says which one failed loudly** and still renders the rest
   — but never silently omits a source as if it were empty.

## After Loop 3 → Loop 4 (same repo)

Loop 4 = systematize jobsearch in `renaud-marketplace` + Obsidian: a **`log-application`** skill
(annonce + source → Obsidian note + follow-up task) and an **`interview-prep`** skill (fixed
structure, wired to the 5 CV profiles). The briefing *reads* what Loop 4 *writes*. Deadline
**Sun 2026-06-14 → STOP**. Brief: `hal/docs/features/loop-4-jobsearch-systematization.md`
(relocate into this repo when Loop 4 runs). Master plan: `hal/docs/lastdev-plan.md`.
