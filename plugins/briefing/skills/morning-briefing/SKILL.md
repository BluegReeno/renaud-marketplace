---
name: morning-briefing
description: >
  Produce one morning briefing covering today's calendars (Pro Blue Green,
  perso, family), current-sprint hal tasks across the `blue-green` and `renaud`
  workspaces, Obsidian jobsearch state, both Gmail inboxes (perso + pro),
  job-offer scoring from LinkedIn digests, and CRM/vault cross-reference —
  then writes one daily-log entry per HAL workspace. Renders 6 blocks + an
  ordered plan du jour. Use when the user asks "what's up for today",
  "ma journée", "briefing du jour", "quel est mon planning", or any similar
  daily-overview trigger.
allowed-tools: "mcp__plugin_hal_hal-mcp__whoami mcp__plugin_hal_hal-mcp__list_sprints mcp__plugin_hal_hal-mcp__list_tasks mcp__plugin_hal_hal-mcp__get_document mcp__plugin_hal_hal-mcp__save_document mcp__claude_ai_Google_Calendar__list_calendars mcp__claude_ai_Google_Calendar__list_events mcp__plugin_jobsearch_gmail-mcp__search_emails mcp__plugin_jobsearch_gmail-mcp__read_email mcp__claude_ai_Gmail__search_threads mcp__claude_ai_Gmail__get_thread mcp__brightdata__web_data_linkedin_job_listings Skill(jobsearch-vault) Agent(cv-log-worker)"
---

# Morning Briefing — Skill Instructions

## What this skill does

Produce one morning briefing that merges **six sources** into a single structured view: hal tasks (two workspaces, sprint-aware), Obsidian jobsearch state, three Google Calendars, and two Gmail inboxes — then cross-references mails against the vault and CRM to update in-flight process status. It also runs a scoring pipeline on LinkedIn job alerts found in the perso inbox, surfaces the best 2-3 offers with fit rationale, and generates an **ordered plan du jour** as the final block. The rendered brief is read-only except for one daily-log write per hal workspace at the end of the run (Step 4).

Any backend that is unreachable renders a loud `⚠️ <source> DOWN — <reason>` line instead of silently omitting data. Silent omission is a critical failure.

---

## Invocation modes — interactive vs `--headless`

This skill runs in two modes. **Interactive** (default, no flag) is the full behaviour described in the steps below, run inside a live session with a human present. **`--headless`** is an explicit, unattended-safe mode for scheduled / `claude -p` runs (e.g. a nightly scheduler that has no one to answer prompts or validate output).

`/briefing --headless` differs from interactive exactly as follows — every difference is a **visible** change in the rendered brief, never a silent one:

| Aspect | Interactive (no flag) | `--headless` |
|--------|-----------------------|--------------|
| **Step 1h — CV fan-out** | Runs (spawns `cv-log-worker` sub-agents for 🔥 offers) | **Skipped entirely.** The brief renders the literal line `CV pre-generation: skipped (headless mode)` in the "CVs préparés ce run" section. Omission is visible, never silent. |
| **Plan du jour** | Prompt the user to validate/modify before writing | Rendered with the `[proposé — non validé]` marker and **NOT written to hal**. |
| **Daily-log writes (Step 4)** | Happen | **Still happen** — they are the whole point of the headless run. |
| **Connector failure** (calendar, gmail, brightdata) | `⚠️ <source> DOWN — <reason>` line, run continues | Block states `<source>: UNAVAILABLE (<error>)`, run continues — visible degradation. |
| **hal unreachable** | `hal:DOWN`, Steps 1a/1b/4 skipped, brief still renders | **ABORT with an error** — the daily-log write is the run's purpose, so a headless run with no hal has nothing to deliver. |

The flag toggles only the five rows above. Everything else — sources pulled, block layout, scoring, ordering — is identical in both modes. Interactive behaviour is unchanged by the presence of this contract.

---

## Step 0 — Pre-flight (probe every source before pulling)

Probe each backend independently. Do NOT bail on the first failure — all probes run regardless.

In **`--headless`** mode: a failing **hal** probe ⇒ **abort the run** (raise an error; do not render a partial brief — see Invocation modes). Any **other** failing probe ⇒ its block renders `<source>: UNAVAILABLE (<error>)` instead of the interactive `⚠️ <source> DOWN` line, and the run continues.

- **hal-mcp probe**: call `mcp__plugin_hal_hal-mcp__whoami`. Expected: `renaud@bluegreen.ai` with workspaces including `blue-green` and `renaud`. On failure → mark `hal:DOWN <reason>`, skip Steps 1a, 1b, 4. If workspace slugs differ, fail loud with actual slugs.
- **jobsearch-vault probe**: attempt a small read (list active candidatures). On failure → mark `jobsearch:DOWN <reason>`, skip Step 1c.
- **Google Calendar probe**: call `mcp__claude_ai_Google_Calendar__list_calendars`. On failure → mark `gcal:DOWN <reason>`, skip Step 1d. If the error suggests OAuth failure, include "reconnect at claude.ai/connectors" in the message.
- **Gmail perso probe**: call `mcp__plugin_jobsearch_gmail-mcp__search_emails` with a minimal query (e.g. `after:2000/01/01 maxResults:1`). On failure → mark `gmail-perso:DOWN <reason>`, skip Step 1e.
- **Gmail pro probe**: call `mcp__claude_ai_Gmail__search_threads` with a minimal query. On failure → mark `gmail-pro:DOWN <reason>`, skip Step 1f.

---

## Step 0.5 — Read yesterday's daily logs (cross-session context)

If `hal:UP`: for each workspace returned by `whoami`, call:

```
mcp__plugin_hal_hal-mcp__get_document(workspace_slug=<slug>, slug="daily-log-<YYYY-MM-DD of yesterday>")
```

When the document exists, extract its `## Notes` section and keep it as **silent internal context** — do NOT echo it in the rendered brief. It is a hand-off from the previous day for the agent's own awareness, not user-facing output.

If the document does not exist (404 or empty), ignore silently — first-day-of-use and skipped days are normal.

If `hal:DOWN`, skip entirely.

---

## Step 1 — Pull data (all sources — run in parallel where possible)

No inter-step dependencies after Step 0. Issue tool calls in parallel for maximum speed.

### 1a — hal tasks for `blue-green` workspace

```
mcp__plugin_hal_hal-mcp__list_sprints(workspace_slug="blue-green", status="actuel")
  → take the first entry's id
if sprint.id is not None:
  mcp__plugin_hal_hal-mcp__list_tasks(workspace_slug="blue-green", sprint_id=<id>)
else:
  mcp__plugin_hal_hal-mcp__list_tasks(workspace_slug="blue-green")
  → note "(no active sprint — showing open tasks)"
```

Label every task `[business]`.

### 1b — hal tasks for `renaud` workspace

Identical flow with `workspace_slug="renaud"`. Label every task `[perso]`.

**Tag grouping (renaud only).** Group returned tasks by their **first** tag. Tasks with no tag land under `other`. Fixed order:

1. `jobsearch` 2. `rosaslaborbe` 3. `personal` 4. `finance` 5. `hr` 6. `laborbe` 7. `other`

Skip groups with zero tasks.

### 1c — Obsidian jobsearch (via `jobsearch-vault` skill)

Invoke `jobsearch-vault` and ask for:
1. Upcoming interviews in the next 7 days.
2. Relances due today or overdue.
3. Count and list of active candidatures (company + role + current stage).

READ-ONLY — do not write the vault.

### 1d — Google Calendars (three calendars, merged)

For each calendar, call `mcp__claude_ai_Google_Calendar__list_events(calendarId=<id>, timeMin=<today 00:00 Europe/Paris>, timeMax=<tomorrow 00:00 Europe/Paris>)`:

- `renaud@bluegreen.ai` — pro Blue Green
- `rlaborbe@gmail.com` — perso / job search
- `hah0feg81cofndkov7derd6g00@group.calendar.google.com` — family

`timeMin` and `timeMax` MUST be Europe/Paris local time, not UTC. If all three calendars return zero events, extend `timeMax` to +7 days to surface "next upcoming". Merge results, sort by `start`. Tag each event (`pro`, `perso`, `famille`).

Do not implement pagination — the default page is enough for a daily window.

### 1e — Gmail perso `rlaborbe@gmail.com` (via `mcp__plugin_jobsearch_gmail-mcp__*`)

Skip if `gmail-perso:DOWN`.

Issue up to three parallel searches:

1. **LinkedIn digests (last 24h)**:
   ```
   mcp__plugin_jobsearch_gmail-mcp__search_emails(
     query="from:jobalerts-noreply@linkedin.com OR from:jobs-listings@linkedin.com newer_than:1d",
     maxResults=20
   )
   ```
   For each matching email, call `mcp__plugin_jobsearch_gmail-mcp__read_email(id=<email_id>)` and extract **all** job title + company + location + snippet pairs from the digest body. Do NOT stop at the first offer — parse the entire digest.

   **Job ID extraction**: apply regex `jobs/view/(\d+)` on the plain-text email body. Each match yields a `job_id`. Build the LinkedIn URL as `https://www.linkedin.com/jobs/view/<job_id>`. Store these alongside each parsed offer for use in Step 1g.

2. **Active candidature threads** (match against vault's active candidature list from Step 1c):
   For each active candidature, search:
   ```
   mcp__plugin_jobsearch_gmail-mcp__search_emails(query="<company_name> newer_than:7d", maxResults=5)
   ```
   Run one search per active candidature (parallel). Read matching threads for context.

3. **Inbound recruiters (last 48h)**:
   ```
   mcp__plugin_jobsearch_gmail-mcp__search_emails(
     query="(recruteur OR recruiter OR opportunité OR opportunity OR poste OR position) newer_than:2d -from:jobalerts-noreply@linkedin.com",
     maxResults=10
   )
   ```
   Read threads that look like genuine recruiter outreach (not automated digests).

Collect results into: `linkedin_offers[]` (raw, all offers), `candidature_threads[]` (matched to active process), `inbound_recruiters[]`.

### 1f — Gmail pro `renaud@bluegreen.ai` (via `mcp__claude_ai_Gmail__*`)

Skip if `gmail-pro:DOWN`.

Issue two parallel searches:

1. **Commercial responses** (match against active BG opportunities from Step 1a):
   ```
   mcp__claude_ai_Gmail__search_threads(query="newer_than:7d -label:newsletters", maxResults=20)
   ```
   Cross-reference thread subjects/senders against active BG opportunities from the hal CRM context. Read threads that match.

2. **Inbound (new contacts, calls for tender)**:
   ```
   mcp__claude_ai_Gmail__search_threads(
     query="newer_than:2d -label:newsletters -label:promotional",
     maxResults=10
   )
   ```
   Flag threads that look like new commercial inbound not matched to any existing CRM entry.

Collect into: `bg_commercial_replies[]` (matched to CRM), `bg_inbound[]` (new).

### 1g — Job-offer scoring pipeline

Skip if `linkedin_offers[]` is empty.

**Dedup**: Remove any offer whose company + role already exists in the vault's active candidatures list (from Step 1c). Do not re-surface already-logged offers.

**Score each remaining offer** using title + company + location + snippet (cheap score — no full JD at this stage):

| Score | Criteria |
|-------|----------|
| 🔥 | Solution Architect IA / Solutions Engineer / FDE / Applied AI Architect / Head of AI Eng — at AI lab / IA editor / scale-up, Paris, ≥85K, builder hands-on |
| 🟡 | CTO / EM / Senior AI Eng / Head of Data&AI depending on context — Paris or remote-ok |
| ❌ | Outside Paris (strict), no AI, <80K, pure PM, governance without hands-on |

Aspiration axis: prefer **builder AI-native** over COMEX direction.

**BrightData enrichment** (🔥/🟡 only — max 5 calls per run):

For each 🔥 and 🟡 offer that has a `job_id` (extracted in Step 1e), call:
```
mcp__brightdata__web_data_linkedin_job_listings(
  url="https://www.linkedin.com/jobs/view/<job_id>"
)
```
Extract the `job_summary` field from the JSON response. Use this full JD text (inline, no external model call) to refine the score and write the "pourquoi" line.

**Cap at 5 BrightData calls per run** — if there are more than 5 🔥/🟡 offers, prioritise 🔥 first, then 🟡 by closest location match. Offers beyond the cap are scored from title+snippet only (no annotation needed — just surface fewer offers).

If `web_data_linkedin_job_listings` returns an error for a specific offer, skip that offer silently and move to the next — do not fail the whole pipeline.

Surface the **top 2-3 offers** (🔥 before 🟡) with: title, company, score emoji, and a **one-line "pourquoi"** that references a concrete signal from the JD (or title+snippet if BrightData failed for that offer).

### 1h — CV fan-out (spawn sub-agents for 🔥 offers)

**In `--headless` mode, skip this entire step** (no fan-out — see Invocation modes). Step 3 then renders the single `CV pre-generation: skipped (headless mode)` line for this block, keyed on the mode (not on an empty `cv_fanout_results[]`).

Skip if there are no 🔥 offers after the Step 1g dedup pass.

For each 🔥 offer **not already in the vault**, up to a **cap of 3 per run**, spawn one `cv-log-worker` sub-agent **in parallel** using the `Agent` tool:

```
Agent(cv-log-worker, prompt="""
JOB_TITLE: <title>
COMPANY: <company>
JD_TEXT: <full JD text from BrightData response if available; digest snippet otherwise>
SENDER_EMAIL: <from address of the LinkedIn digest email that contained this offer>
JOB_URL: <https://www.linkedin.com/jobs/view/<job_id> or empty string if no job_id>
DATE: <YYYY-MM-DD today, Europe/Paris>
""")
```

If more than 3 🔥 deduped offers exist, select the top 3 by: score (🔥 first) then closest location to Paris.

Collect each sub-agent's result — one line per offer:
- Success: `CV_préparé | <JOB_TITLE> — <COMPANY> | Profil : P<n> | CV : <filename> | Source : <source>`
- Failure: `ÉCHEC | <JOB_TITLE> — <COMPANY> | <reason>`

Store these in `cv_fanout_results[]` for use in Step 3 rendering.

---

## Step 2 — Merge and label

Assemble one ordered structure from all pulls:
- hal tasks: `[business]` / `[perso]` labels per workspace
- Calendar events: `[pro]` / `[perso]` / `[famille]` tags
- LinkedIn offers: scored list from Step 1g
- Candidature cross-reference: vault stage + mail context from Step 1e
- BG commercial: CRM stage + mail context from Step 1f
- Sources DOWN: `⚠️` line in the relevant section

---

## Step 3 — Render the brief

Render in **French** (Renaud's working language). Use the 6-block template below verbatim, substituting actual data. All 6 blocks are mandatory — a DOWN source renders its `⚠️` line, it does not remove the block.

```
# Briefing — <date in French, e.g. mercredi 11 juin 2026>

## 📅 RDV du jour (3 agendas fusionnés)
HH:MM–HH:MM — <event title> [pro|perso|famille]
...
(aucun événement aujourd'hui — prochain : HH:MM <date> — <title> [<cal>])
(or: ⚠️ Google Calendar DOWN — <reason>)

## ✅ Sprint en cours
### Blue Green [business]
- [<status>] <title> · échéance <date>
...
(⚠️ hal DOWN — <reason>  /  aucun sprint actif — tâches ouvertes : ...)

### Renaud [perso]
#### 🎯 jobsearch
- [<status>] <title>
...
#### 🏡 rosaslaborbe / 🧍 personal / 💶 finance / 📋 hr / 👨‍👩‍👧 laborbe / 📌 other
...
(skip empty subsections)

## 🎯 Jobsearch — Nouvelles offres
🔥 <title> — <company> — <location>
   → <pourquoi — one line referencing aspiration axis>
   → <pourquoi — one line referencing a concrete JD signal or aspiration-axis criterion>
🟡 <title> — <company>
   → <pourquoi>
   → <pourquoi — one line referencing a concrete JD signal or aspiration-axis criterion>
...
(aucune nouvelle offre aujourd'hui)
(or: ⚠️ Gmail perso DOWN — <reason>)

CVs préparés ce run :
- ✅ <JOB_TITLE> — <COMPANY> (P<n>) → <cv_filename> · loggé (📝 À postuler)
- ⚠️ ÉCHEC <JOB_TITLE> — <COMPANY> → <reason>
(aucun CV généré — 0 offre 🔥 non loguée  /  or: ⚠️ cv-log-worker skipped — Step 1h cap atteint ou gmail-perso DOWN)

**In `--headless` mode, replace this entire "CVs préparés ce run" block with the single line `CV pre-generation: skipped (headless mode)`** — the omission is visible, never silent (see Invocation modes).

## 🔄 Jobsearch — Process en cours
- **<company>** (<role>) — stage : <vault stage>
  → Mail récent : <subject> [<date>] — <1-line summary>
  → Relance due : <date|"non due"|"en retard">
...
Entretiens à venir : <list or "aucun cette semaine">
Autres mails jobsearch à regarder : <subjects not matched to active process, sorted by relevance>
(or: ⚠️ jobsearch:DOWN — <reason>  /  ⚠️ Gmail perso DOWN — <reason>)

## 💼 Blue Green — Commercial
- **<company/contact>** — <opportunity title> — stage : <CRM stage>
  → Mail récent : <subject> [<date>] — <1-line summary>
...
Nouveaux inbound : <list of new commercial contacts/AOs, or "aucun">
Autres mails pro à regarder : <subjects not matched to CRM, sorted by relevance>
(or: ⚠️ hal DOWN — <reason>  /  ⚠️ Gmail pro DOWN — <reason>)

## 📋 Plan du jour
- HH:MM (≈Xmin) — <task title>
  → <context brief : one sentence — who, what, why, where to find context>
...

## Source status
hal-mcp : ✅  |  ⚠️ DOWN (<reason>)
jobsearch-vault : ✅  |  ⚠️ DOWN (<reason>)
Google Calendar : ✅  |  ⚠️ DOWN (<reason>)
Gmail perso (rlaborbe@gmail.com) : ✅  |  ⚠️ DOWN (<reason>)
Gmail pro (renaud@bluegreen.ai) : ✅  |  ⚠️ DOWN (<reason>)
```

The "Source status" footer is mandatory and ALWAYS renders all five lines — even when all sources are healthy.

### Plan du jour — ordering rules

Build the plan from: calendar events (anchors), hal sprint tasks, vault relances, mail follow-ups. Each task includes a **one-sentence context brief** so it is actionable in a fresh session.

Apply ordering rules in priority order:

1. **MAR–VEN : jobsearch block 08:30–10:30 first** — if today is Tuesday–Friday and the slot is free, put jobsearch tasks first: vault relances, mail replies to recruiters, new 🔥/🟡 offer follow-ups. Exception: on Monday, the IC meeting comes first.
2. **Calendar events as anchors** — add prep task 15–30 min before each event; add post-meeting follow-up immediately after.
3. **Deep-work in open windows** — assign hal sprint tasks to remaining free slots, `[business]` (revenue-generating) before `[perso]`.
4. **Revenue priority** — job + revenue tasks before admin before personal.

**Plan du jour write policy (flag-driven — see Invocation modes).** In **`--headless`** mode, mark the plan `[proposé — non validé]` and do NOT write it to hal. In **interactive** mode (no flag), prompt the user to validate or modify before writing.

---

## Step 4 — Write today's daily logs to HAL

If `hal:DOWN` (Step 0 failed), skip this step entirely.

If `hal:UP`: for **each** workspace returned by `whoami` (do NOT hardcode slugs — iterate on what `whoami` actually returns), call `mcp__plugin_hal_hal-mcp__save_document` with:

- `workspace_slug`: the workspace's slug
- `slug`: `daily-log-<YYYY-MM-DD>` (today's date, Europe/Paris)
- `domain`: `"memory"`
- `kind`: `"daily-log"`
- `title`: `"Daily log — <workspace-slug> — <date in French>"`
- `content_md`: structured markdown (see templates below)

The upsert key is `(workspace_slug, slug)` — re-running the brief overwrites the existing log. These are the **only** write calls allowed in this skill.

If `save_document` fails for a workspace, render a loud line after the source-status footer:
```
⚠️ Daily log <workspace-slug> — write failed: <reason>
```

A write failure for one workspace MUST NOT block the write for the other(s).

### Content templates

#### Workspace `blue-green`

```markdown
# Daily log — blue-green — <date in French>

## Sprint en cours [business]
- [ ] <task title> · priorité : <priority|none>
...
(or "(aucune tâche en cours)")

## Agenda du jour [pro]
HH:MM — <event title> [pro]
...
(or "(aucun événement pro aujourd'hui)")

## Notes
(vide — à compléter en cours de journée)
```

#### Workspace `renaud`

Group sprint tasks by first tag (same order as Step 3). Skip empty groups. Tasks with no tag → `other`.

```markdown
# Daily log — renaud — <date in French>

## Sprint en cours [perso]

### 🎯 jobsearch
- [ ] <task title>
...

### 🏡 rosaslaborbe / 🧍 personal / 💶 finance / 📋 hr / 👨‍👩‍👧 laborbe / 📌 other
- [ ] <task title>
...
(skip empty subsections — or "(aucune tâche en cours)" if all empty)

## Agenda du jour [perso + famille]
HH:MM — <event title> [perso|famille]
...
(or "(aucun événement perso/famille aujourd'hui)")

## Notes
(vide — à compléter en cours de journée)
```

#### Any other workspace returned by `whoami`

Fall back to the `renaud` shape. Never crash on an unknown workspace — write a minimal log with whatever data is available, or skip with:
```
⚠️ Daily log <workspace-slug> — skipped: unknown workspace shape
```

---

## Step 5 — Constraints (load-bearing)

- **Read-only for Gmail, calendar, and vault** — no draft, send, label, or delete calls on mail.
- **One `save_document` write per hal workspace** — the only permitted write in the entire skill. No other `create_*`, `update_*`, or `delete_*`.
- **Never write if `hal:DOWN`**.
- **Never silently omit a source** — any probe or Step 1 call failure renders `⚠️` in the section AND in the source-status footer.
- **Parse all offers in a LinkedIn digest** — do not stop at the first offer.
- **Dedup offers against vault** — never surface an offer already logged as an active candidature.
- **BrightData cap** — max 5 `web_data_linkedin_job_listings` calls per run. Prioritise 🔥 then 🟡 by location. Per-offer errors are silent — skip and continue.
- **Label every hal task** — `[business]` for `blue-green`, `[perso]` for `renaud`, every time.
- **Local time** — all calendar windows and daily log slugs use Europe/Paris, not UTC.
- **Compose, do not reimplement** — call `jobsearch-vault` and MCP tools. Never read the Obsidian filesystem directly, never bypass hal-mcp.
- **Agent fan-out cap** — max 3 `cv-log-worker` sub-agents per run. If >3 🔥 deduped offers exist, take the top 3 by score×proximity. Never spawn more than 3 Agent calls in Step 1h.
- **Sub-agent failures are loud** — if a `cv-log-worker` returns `ÉCHEC`, surface `⚠️ CV non généré — <company> : <reason>` in the "CVs préparés ce run" section. Never silently drop a sub-agent failure.
- **No auto-apply, no cover letter** — sub-agents generate CVs and log applications only. They never submit applications, send messages, or generate cover letters.
- **Status `📝 À postuler`** — the sub-agent logs applications with this status, NOT `✉️ Candidature envoyée`. Renaud moves the card to « Candidature envoyée » when he actually submits.
- **Relationship with `mail-triage`** — Steps 1e/1f do a lightweight, context-integrated mail pass for the daily briefing. The `mail-triage` skill (also in this plugin) provides a deeper, on-demand triage with explicit per-thread classification. Do NOT call `Skill(mail-triage)` from inside this skill — the shallow pass here is intentionally faster and context-lighter. Users who want full triage run `/mail` separately.
