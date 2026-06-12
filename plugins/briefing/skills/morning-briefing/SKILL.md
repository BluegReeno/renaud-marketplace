---
name: morning-briefing
description: >
  Produce one read-only morning briefing covering today's calendars (Pro Blue Green,
  perso, family), current-sprint hal tasks across the `blue-green` and `renaud`
  workspaces (labelled business vs perso), and Obsidian jobsearch state (upcoming
  interviews, relances due, active candidatures). Use when the user asks "what's up
  for today", "ma journée", "briefing du jour", "quel est mon planning", or any
  similar daily-overview trigger.
version: 0.2.0
allowed-tools: "mcp__hal-mcp__whoami mcp__hal-mcp__list_sprints mcp__hal-mcp__list_tasks mcp__claude_ai_Google_Calendar__list_calendars mcp__claude_ai_Google_Calendar__list_events Skill(jobsearch-vault)"
---

# Morning Briefing — Skill Instructions

## What this skill does

Produce one read-only morning briefing that merges three backends into a single structured view: hal tasks across the `blue-green` and `renaud` workspaces (current sprint, with fallback to open tasks), Obsidian jobsearch state via the `jobsearch-vault` skill, and three Google Calendars via the claude.ai Google Calendar MCP connector. The skill never writes anywhere. When a backend is unreachable, the failing section renders a loud `⚠️ <source> DOWN — <reason>` line instead of silently rendering empty — silent omission would be a critical failure for a job-search-critical period.

## Step 0 — Pre-flight (probe every source before pulling)

Probe each backend independently. Do NOT bail on the first failure — all three probes run regardless, and the brief degrades section by section.

- **hal-mcp probe**: call `mcp__hal-mcp__whoami`. Expected response: `renaud@bluegreen.ai` with workspaces including `blue-green` and `renaud`. On any error, mark `hal:DOWN <reason>` and skip Steps 1a and 1b. If the workspace slugs reported by `whoami` differ from `blue-green` / `renaud`, fail loudly with the actual slugs in the error message rather than silently calling with a wrong slug.
- **jobsearch-vault probe**: invoke the `jobsearch-vault` skill in probe mode (or attempt a small read such as listing active candidatures). On any error, mark `jobsearch:DOWN <reason>` and skip Step 1c.
- **Google Calendar probe**: call `mcp__claude_ai_Google_Calendar__list_calendars`. On any error (most often unconnected OAuth), mark `gcal:DOWN <reason>` and skip Step 1d. The fallback message should mention reconnecting at `claude.ai/connectors` when the error indicates an OAuth or auth failure.

## Step 1 — Pull data (per source — Claude is free to run these in parallel)

The substeps are listed in priority order for the reader. There are no inter-step dependencies after Step 0, so Claude SHOULD issue these tool calls in parallel.

### 1a — hal tasks for `blue-green` workspace

```
mcp__hal-mcp__list_sprints(workspace_slug="blue-green", status="actuel")
  → take the first entry's id (response is a list; only ever one current sprint)
if sprint.id is not None:
  mcp__hal-mcp__list_tasks(workspace_slug="blue-green", sprint_id=<id>)
else:
  mcp__hal-mcp__list_tasks(workspace_slug="blue-green")
  → render the section with "(no active sprint — showing open tasks)"
```

Label every task returned `[business]`.

### 1b — hal tasks for `renaud` workspace

Identical flow with `workspace_slug="renaud"`. Label every task returned `[perso]`. Sprint resolution and open-tasks fallback are independent from 1a — one workspace having an active sprint does not imply the other does.

### 1c — Obsidian jobsearch (via the `jobsearch-vault` skill)

Invoke `jobsearch-vault` and ask it for:

1. Upcoming interviews in the next 7 days.
2. Relances due today or overdue.
3. Count of active candidatures.

READ-ONLY — explicitly do not write the vault. The `jobsearch-vault` skill reads the vault directly on the filesystem (no network, no API key) and handles vault-path resolution itself; this skill just consumes its output.

### 1d — Google Calendars (three calendars, merged)

For each of the three calendar IDs below, call `mcp__claude_ai_Google_Calendar__list_events(calendarId=<id>, timeMin=<today 00:00 Europe/Paris>, timeMax=<tomorrow 00:00 Europe/Paris>)`:

- `renaud@bluegreen.ai` — pro Blue Green
- `rlaborbe@gmail.com` — perso / job search
- `hah0feg81cofndkov7derd6g00@group.calendar.google.com` — family

`timeMin` and `timeMax` MUST be in Europe/Paris local time, not UTC. If today returns zero events for all three calendars, call `list_events` once more per calendar with a `timeMax` extended out to seven days ahead so the brief can surface the "next upcoming" event. Merge results, sort by `start`. Tag every event with its source calendar (`pro`, `perso`, `famille`).

Do not implement pagination — the default page is enough for a daily window.

## Step 2 — Merge and label

Assemble one ordered structure from the four pulls. Every task that came back from a hal call MUST carry the `[business]` or `[perso]` label based on the workspace it came from — no exceptions. Every calendar event MUST carry its source tag. If a source was marked DOWN in Step 0, its section in the brief is the corresponding `⚠️ … DOWN` line.

## Step 3 — Render the brief

Render the brief in French (Renaud's working language). Use the template below verbatim, substituting actual data. Jobsearch comes FIRST per `~/.claude/CLAUDE.md` "Job + revenu = survie de la famille."

```
# Briefing — <date in French, e.g. mercredi 11 juin 2026>

## 🎯 Jobsearch (priority — job + revenue)
- Entretiens à venir (7 prochains jours) : <list, or "aucun">
- Relances dues / en retard : <list, or "aucune">
- Candidatures actives : <count>
(or, if jobsearch:DOWN: ⚠️ Jobsearch DOWN — <reason>)

## 📅 Agenda du jour (3 calendriers fusionnés)
HH:MM–HH:MM — <event title> [pro|perso|famille]
...
(if no events today:)
(aucun événement aujourd'hui)
Prochain à venir : HH:MM <date> — <title> [<cal>]
(or, if gcal:DOWN: ⚠️ Google Calendar DOWN — <reason>)

## ✅ Sprint en cours — Blue Green [business]
- [<status>] <title> · échéance <date>
...
(or, if hal:DOWN: ⚠️ hal DOWN — <reason>)
(or, if no active sprint: "(aucun sprint actif — tâches ouvertes)" + the open-tasks list)

## 🏠 Sprint en cours — Renaud [perso]
- [<status>] <title> · échéance <date>
...
(or, if hal:DOWN: ⚠️ hal DOWN — <reason>)
(or, if no active sprint: "(aucun sprint actif — tâches ouvertes)" + the open-tasks list)

## Source status
hal-mcp: ✅  | ⚠️ DOWN (<reason>)
jobsearch-vault: ✅  | ⚠️ DOWN (<reason>)
Google Calendar: ✅  | ⚠️ DOWN (<reason>)
```

The "Source status" footer is mandatory and ALWAYS renders all three lines — even when all sources are healthy. It is the redundant check that makes acceptance criterion AC3 (loud failures, never silent omission) visually trivial to verify.

## Step 4 — Constraints (load-bearing)

- **READ-ONLY everywhere.** Never call any `create_*`, `update_*`, or `delete_*` MCP tool — neither hal nor calendar. The `allowed-tools` frontmatter excludes them; do not work around it.
- **Never silently omit a source.** Any probe failure in Step 0 MUST render as a `⚠️ <source> DOWN — <reason>` line in the corresponding section AND in the source-status footer.
- **Failures after a passing probe count too.** If any Step 1 tool call throws or returns an error (e.g. `list_sprints` for one workspace, `list_events` for one calendar, a `jobsearch-vault` sub-query), that section MUST render `⚠️ <source> DOWN — <reason>` and the footer line for that source MUST flip from `✅` to `⚠️ DOWN (<reason>)` — even if other calls to the same backend succeeded. When only a sub-source fails (one calendar of three, one workspace of two), render the healthy data and add a `⚠️ <sub-source> DOWN — <reason>` line for the failed one.
- **Label every hal task.** `[business]` for `blue-green`, `[perso]` for `renaud`, every time.
- **Local time.** All calendar windows are Europe/Paris, not UTC.
- **Compose, do not reimplement.** This skill calls `jobsearch-vault` and hal-mcp / calendar MCP tools. It never reads the Obsidian filesystem directly, never bypasses hal-mcp, never writes to any backend.
