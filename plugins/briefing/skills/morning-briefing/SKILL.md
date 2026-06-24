---
name: morning-briefing
description: >
  Produce one read-only morning briefing covering today's calendars (Pro Blue Green,
  perso, family), current-sprint hal tasks across the `blue-green` and `renaud`
  workspaces (labelled business vs perso), and Obsidian jobsearch state (upcoming
  interviews, relances due, active candidatures). Use when the user asks "what's up
  for today", "ma journée", "briefing du jour", "quel est mon planning", or any
  similar daily-overview trigger.
version: 0.5.0
allowed-tools: "mcp__hal-mcp__whoami mcp__hal-mcp__list_sprints mcp__hal-mcp__list_tasks mcp__hal-mcp__get_document mcp__hal-mcp__save_document mcp__claude_ai_Google_Calendar__list_calendars mcp__claude_ai_Google_Calendar__list_events Skill(jobsearch-vault)"
---

# Morning Briefing — Skill Instructions

## What this skill does

Produce one morning briefing that merges three backends into a single structured view: hal tasks across the `blue-green` and `renaud` workspaces (current sprint, with fallback to open tasks), Obsidian jobsearch state via the `jobsearch-vault` skill, and three Google Calendars via the claude.ai Google Calendar MCP connector. The rendered brief is read-only, but the skill writes one daily log per workspace into hal at the end of the run (`mcp__hal-mcp__save_document`, `domain="memory"`, `kind="daily-log"`) — see Step 4. Those are the only writes; everything else is read-only. When a backend is unreachable, the failing section renders a loud `⚠️ <source> DOWN — <reason>` line instead of silently rendering empty — silent omission would be a critical failure for a job-search-critical period.

## Step 0 — Pre-flight (probe every source before pulling)

Probe each backend independently. Do NOT bail on the first failure — all three probes run regardless, and the brief degrades section by section.

- **hal-mcp probe**: call `mcp__hal-mcp__whoami`. Expected response: `renaud@bluegreen.ai` with workspaces including `blue-green` and `renaud`. On any error, mark `hal:DOWN <reason>` and skip Steps 1a and 1b. If the workspace slugs reported by `whoami` differ from `blue-green` / `renaud`, fail loudly with the actual slugs in the error message rather than silently calling with a wrong slug.
- **jobsearch-vault probe**: invoke the `jobsearch-vault` skill in probe mode (or attempt a small read such as listing active candidatures). On any error, mark `jobsearch:DOWN <reason>` and skip Step 1c.
- **Google Calendar probe**: call `mcp__claude_ai_Google_Calendar__list_calendars`. On any error (most often unconnected OAuth), mark `gcal:DOWN <reason>` and skip Step 1d. The fallback message should mention reconnecting at `claude.ai/connectors` when the error indicates an OAuth or auth failure.

## Step 0.5 — Read yesterday's daily logs (cross-session context)

If `hal:UP` (Step 0 probe passed): for each workspace returned by `whoami`, call:

```
mcp__hal-mcp__get_document(workspace_slug=<slug>, slug="daily-log-<YYYY-MM-DD of yesterday>")
```

When the document exists, extract its `## Notes` section and keep it as **silent internal context** for the rest of the run — do NOT echo it in the rendered brief. It is a hand-off from the previous day for the agent's own awareness, not user-facing output.

If the document does not exist (404, missing entry, or empty response), ignore silently — first-day-of-use and skipped days are normal, not errors.

If `hal:DOWN` (Step 0 failed), skip this step entirely. The brief still renders without yesterday's context.

This step is read-only and never affects which other steps run.

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

**Tag grouping (renaud only).** The `renaud` workspace tasks carry a `tags` field (array of strings, drawn from the workspace's `allowed_tags` vocabulary: `jobsearch`, `rosaslaborbe`, `laborbe`, `personal`, `finance`, `hr`, `other`). Group the returned tasks by their **first** tag — a task with multiple tags lands under its first tag only (no duplication across sections). Tasks with an empty/missing `tags` array land under `other` (the catch-all bucket).

Group ordering for the render in Step 3 (fixed, do NOT reorder):

1. `jobsearch` (always first — job + revenue priority per `~/.claude/CLAUDE.md`)
2. `rosaslaborbe`
3. `personal`
4. `finance`
5. `hr`
6. `laborbe`
7. `other` (untagged + any tag not in the list above — defensive against future vocabulary growth)

Skip any group with zero tasks — empty subsections clutter the brief. The `[perso]` label still applies to every task regardless of tag.

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

### 🎯 jobsearch
- [<status>] <title> · échéance <date>
...

### 🏡 rosaslaborbe
- [<status>] <title> · échéance <date>
...

### 🧍 personal
- [<status>] <title> · échéance <date>
...

### 💶 finance
- [<status>] <title> · échéance <date>
...

### 📋 hr
- [<status>] <title> · échéance <date>
...

### 👨‍👩‍👧 laborbe
- [<status>] <title> · échéance <date>
...

### 📌 other
- [<status>] <title> · échéance <date>
...

(only render subsections that have at least one task — skip empty groups)
(or, if hal:DOWN: ⚠️ hal DOWN — <reason>)
(or, if no active sprint: "(aucun sprint actif — tâches ouvertes)" + the open-tasks list grouped by tag as above)

## Source status
hal-mcp: ✅  | ⚠️ DOWN (<reason>)
jobsearch-vault: ✅  | ⚠️ DOWN (<reason>)
Google Calendar: ✅  | ⚠️ DOWN (<reason>)
```

The "Source status" footer is mandatory and ALWAYS renders all three lines — even when all sources are healthy. It is the redundant check that makes acceptance criterion AC3 (loud failures, never silent omission) visually trivial to verify.

## Step 4 — Write today's daily logs to HAL

If `hal:DOWN` (Step 0 failed), skip this step entirely — no error, the brief is still useful on its own.

If `hal:UP`: for **each** workspace returned by `whoami` (do NOT hardcode `blue-green` / `renaud` — iterate on what `whoami` actually returns), call `mcp__hal-mcp__save_document` with:

- `workspace_slug`: the workspace's slug
- `slug`: `daily-log-<YYYY-MM-DD>` (today's date, Europe/Paris)
- `domain`: `"memory"`
- `kind`: `"daily-log"`
- `title`: `"Daily log — <workspace-slug> — <date in French, e.g. mercredi 24 juin 2026>"`
- `content_md`: the structured markdown for that workspace (see templates below)

The upsert key is `(workspace_slug, slug)` — calling Step 4 twice on the same day overwrites the existing daily log for that workspace. That is intentional: re-running the brief refreshes the snapshot.

These are the **only** write calls allowed in this skill. No other `create_*`, `update_*`, or `delete_*` — see Step 5.

If `save_document` fails for a workspace, render a loud line in the brief output (after the source-status footer):

```
⚠️ Daily log <workspace-slug> — write failed: <reason>
```

A write failure for one workspace MUST NOT block the write for the other(s) — call them independently.

### Content templates

#### Workspace `blue-green` (or any workspace whose tasks are all `[business]`)

```markdown
# Daily log — blue-green — <date in French>

## Sprint en cours [business]
- [ ] <task title> · priorité: <priority|none>
...
(or "(aucune tâche en cours)" if the sprint is empty / no active sprint)

## Agenda du jour [pro]
HH:MM — <event title> [pro]
...
(or "(aucun événement pro aujourd'hui)")

## Notes
(vide — à compléter en cours de journée)
```

#### Workspace `renaud` (or any workspace whose tasks are tagged via `allowed_tags`)

Group the sprint tasks by their **first** tag using the same ordering as Step 3 (`jobsearch`, `rosaslaborbe`, `personal`, `finance`, `hr`, `laborbe`, `other`). Skip empty groups. Tasks with no tag land under `other`.

```markdown
# Daily log — renaud — <date in French>

## Sprint en cours [perso]

### 🎯 jobsearch
- [ ] <task title>
...

### 🏡 rosaslaborbe
- [ ] <task title>
...

### 🧍 personal / 💶 finance / 📋 hr / 👨‍👩‍👧 laborbe / 📌 other
- [ ] <task title>
...
(only render subsections that have at least one task)
(or "(aucune tâche en cours)" if every group is empty)

## Agenda du jour [perso + famille]
HH:MM — <event title> [perso|famille]
...
(or "(aucun événement perso/famille aujourd'hui)")

## Notes
(vide — à compléter en cours de journée)
```

#### Any other workspace returned by `whoami`

Fall back to the `renaud` shape (tag-grouped sprint + today's events) using whatever calendar / tag mapping makes sense. The skill must never crash when `whoami` returns a workspace it has never seen before — write a minimal daily log with whatever data is available, or skip that workspace with a loud `⚠️ Daily log <workspace-slug> — skipped: unknown workspace shape` line.

## Step 5 — Constraints (load-bearing)

- **Two writes allowed, no more.** `mcp__hal-mcp__save_document` for the `blue-green` daily log and `mcp__hal-mcp__save_document` for the `renaud` daily log (or as many workspaces as `whoami` returns — one write each). This is the only exception to the read-only principle. No other `create_*`, `update_*`, or `delete_*` MCP tool — neither hal, calendar, nor vault.
- **Never write if `hal:DOWN`.** Step 4 is conditional on a passing Step 0 hal probe. A failed probe means no daily log writes that run, period.
- **Never silently omit a source.** Any probe failure in Step 0 MUST render as a `⚠️ <source> DOWN — <reason>` line in the corresponding section AND in the source-status footer.
- **Failures after a passing probe count too.** If any Step 1 tool call throws or returns an error (e.g. `list_sprints` for one workspace, `list_events` for one calendar, a `jobsearch-vault` sub-query), that section MUST render `⚠️ <source> DOWN — <reason>` and the footer line for that source MUST flip from `✅` to `⚠️ DOWN (<reason>)` — even if other calls to the same backend succeeded. When only a sub-source fails (one calendar of three, one workspace of two), render the healthy data and add a `⚠️ <sub-source> DOWN — <reason>` line for the failed one.
- **Label every hal task.** `[business]` for `blue-green`, `[perso]` for `renaud`, every time.
- **Local time.** All calendar windows are Europe/Paris, not UTC. Daily log slugs (`daily-log-YYYY-MM-DD`) also use Europe/Paris dates.
- **Compose, do not reimplement.** This skill calls `jobsearch-vault` and hal-mcp / calendar MCP tools. It never reads the Obsidian filesystem directly, never bypasses hal-mcp, never writes to any backend other than the two `save_document` calls in Step 4.
