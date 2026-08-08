---
name: book-appointment
description: >
  Book an appointment — create one Google Calendar event on the calendar
  resolved from a hal workspace, never from a literal, never from a task's
  tag. Always proposes title/date/time/duration/calendar and waits for
  confirmation before writing. Create-only (no update, no delete) and
  interactive-only (never runs in a scheduled/headless context). Use when the
  user asks to "book an appointment", "prends rendez-vous", "schedule the
  visit", "crée un événement dans mon agenda", "ajoute ce rendez-vous au
  calendrier", or names a concrete appointment (e.g. ophthalmologist, site
  visit) that should land on a specific workspace's calendar.
allowed-tools: "mcp__claude_ai_hal-mcp__whoami mcp__claude_ai_Google_Calendar__list_calendars mcp__claude_ai_Google_Calendar__list_events mcp__claude_ai_Google_Calendar__create_event"
---

# Book Appointment — Skill Instructions

## What this skill does

Creates one Google Calendar event on the calendar resolved from a **hal workspace** —
never a hardcoded calendar ID, never inferred from a task's tags (a task tagged for
the household can legitimately live in a personal workspace). The workspace comes
from the user's request or from asking — never guessed from a tag. Given that
workspace, the destination calendar resolves in strict priority order: the
workspace's shared `calendar_id` first, then its `member_calendar_id`; if neither is
declared, the skill stops and says so rather than falling back to the Google
"primary" calendar.

This skill always proposes title, date, start/end time, and the resolved calendar,
and waits for explicit confirmation before calling `create_event` — see Step 2. It
never creates an event from a single-turn request, however unambiguous.

Create-only in this version: no `update_event`, no `delete_event` call anywhere in
this skill (neither tool is in `allowed-tools`) — see Step 4.

---

## Interactive only — never `--headless` / scheduled

This skill has no unattended mode. If invoked from a scheduled or `--headless`
context (e.g. a `claude -p` scheduled run, or any caller that identifies itself as
headless), **stop immediately, before Step 0**, with: `Booking an appointment
requires interactive confirmation — not available in headless mode.` A wrongly
created event is visible to every member of a shared calendar, so there is no safe
unattended default here. This differs from `morning-briefing`, whose headless
contract covers its own read-mostly writes — booking an appointment is a different
class of risk and gets no such contract.

---

## Step 0 — Resolve the workspace

The workspace decides the calendar (Step 1) — never a task's tag. Resolve it from:

1. **Explicit in the request** — the user names the workspace, or something that
   maps to it unambiguously (e.g. "the household calendar", "my Blue Green agenda").
2. **Single membership** — if `whoami.workspaces[]` has exactly one entry, use it
   without asking.
3. **Ask** — otherwise, list the candidate workspaces (`whoami.workspaces[].name`)
   and ask which one this appointment belongs to. Do not guess.

Call `mcp__claude_ai_hal-mcp__whoami`. On failure, stop: `hal unreachable — cannot
resolve a calendar without a workspace: <reason>`.

---

## Step 1 — Resolve the calendar

Given the resolved workspace `w` (a row from `whoami.workspaces[]`):

1. `w.calendar_id` set → target calendar = `w.calendar_id`. This is the calendar
   **shared** by every member of the workspace — the right destination for a concern
   the other members should see (e.g. a household appointment).
2. else `w.member_calendar_id` set → target calendar = `w.member_calendar_id` — this
   member's own agenda within that workspace.
3. else → **stop**: `Workspace "<w.name>" has no calendar declared (calendar_id and
   member_calendar_id both null) — cannot book without a destination.` Do not guess
   and do not fall back to `list_calendars`' "primary" entry.

Never call `create_event` without an explicit, resolved `calendarId`. Omitting it
silently defaults to the Google-account primary calendar — the exact failure mode
this skill exists to prevent.

---

## Step 2 — Propose and confirm

Extract from the request: title, date, start time, and either an end time or a
duration. Ask for anything missing rather than guessing a time; default to a 1h
duration only if the user gives neither an end time nor a duration and does not
object when the default is shown.

Present the proposal and wait for confirmation before doing anything else:

```
Je propose de créer :
- Titre : <summary>
- Quand : <date> <HH:MM>–<HH:MM> (Europe/Paris)
- Calendrier : <workspace name> (<partagé|personnel>)

Je crée ce rendez-vous ?
```

Do not call `create_event` until the user confirms. A short affirmative
("oui", "vas-y", "yes") is sufficient; any requested change restarts this step with
the corrected proposal.

---

## Step 3 — Duplicate check

Before creating, call `mcp__claude_ai_Google_Calendar__list_events(calendarId=<target
calendar from Step 1>, startTime=<proposed date 00:00 Europe/Paris>,
endTime=<proposed date +1 day 00:00 Europe/Paris>)` and compare titles and time
windows against the proposal.

`search_events` is not usable for this check — it only searches the account's
primary calendar, never a workspace's shared or member calendar.

If an event with a matching title overlaps the proposed window, surface it and ask
whether to proceed anyway (e.g. two genuinely distinct visits the same day) or
cancel. Never silently skip the check, never silently create a second event.

---

## Step 4 — Create the event

Once confirmed (Step 2) and clear of an unacknowledged duplicate (Step 3), call:

```
mcp__claude_ai_Google_Calendar__create_event(
  calendarId=<resolved calendar from Step 1>,
  summary=<title>,
  startTime=<ISO 8601, Europe/Paris>,
  endTime=<ISO 8601, Europe/Paris>,
  timeZone="Europe/Paris"
)
```

Report the created event back to the user (title, time, calendar/workspace name). On
failure, surface the exact error — never retry silently, never fall back to a
different calendar.

**Create-only.** Updating or deleting an existing event is out of scope for this
version. If the user asks to change or cancel an appointment, say so explicitly and
stop — do not call `update_event` or `delete_event`; neither is in this skill's
`allowed-tools`.

---

## Step 5 — Constraints (load-bearing)

- **Never infer the workspace from a tag** — resolve it from an explicit user
  statement, a single membership, or by asking (Step 0).
- **Never call `create_event` without an explicit `calendarId`** — an omitted
  `calendarId` silently defaults to the Google-account primary calendar.
- **Priority is `calendar_id` then `member_calendar_id`, never the reverse** — a
  shared concern belongs on the calendar the other workspace members see.
- **No calendar declared → stop, never guess** — name the workspace with no
  declared calendar and stop; never fall back to `list_calendars`' primary entry.
- **Always confirm before writing** — title, date, time, duration, and the resolved
  calendar are proposed and confirmed (Step 2) before any `create_event` call, even
  for an unambiguous single-turn request.
- **Check for duplicates before creating** — `list_events` on the target calendar's
  day window (Step 3); `search_events` cannot be used here (primary-calendar only).
- **Never run in `--headless` / scheduled mode** — stop before Step 0 (see above).
- **Create-only** — no `update_event`, no `delete_event` call in this version.
- **No literal calendar ID anywhere in this file or elsewhere in this repository** —
  every ID is resolved at run time from `whoami`.
- **Local time** — all proposed and queried windows use Europe/Paris, not UTC.
