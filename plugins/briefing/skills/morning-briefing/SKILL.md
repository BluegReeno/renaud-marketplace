---
name: morning-briefing
description: >
  Produce one morning briefing covering today's calendars (declared by your hal
  workspaces), current-sprint hal tasks across every workspace you belong to,
  Obsidian jobsearch state, both Gmail inboxes (perso + pro), job-offer scoring
  from LinkedIn digests, and CRM/vault cross-reference — then writes one
  daily-log entry per HAL workspace. Renders 6 blocks + an ordered plan du jour.
  Use when the user asks "what's up for today", "ma journée", "briefing du
  jour", "quel est mon planning", or any similar daily-overview trigger.
allowed-tools: "mcp__plugin_hal_hal-mcp__whoami mcp__plugin_hal_hal-mcp__list_sprints mcp__plugin_hal_hal-mcp__list_tasks mcp__plugin_hal_hal-mcp__get_document mcp__plugin_hal_hal-mcp__save_document mcp__plugin_hal_hal-mcp__update_task mcp__claude_ai_Google_Calendar__list_calendars mcp__claude_ai_Google_Calendar__list_events mcp__plugin_briefing_gmail-mcp__search_emails mcp__plugin_briefing_gmail-mcp__read_email mcp__claude_ai_Gmail__search_threads mcp__claude_ai_Gmail__get_thread mcp__brightdata__web_data_linkedin_job_listings Skill(jobsearch-vault) Agent(cv-log-worker)"
---

# Morning Briefing — Skill Instructions

## What this skill does

Produce one morning briefing that merges **six sources** into a single structured view: hal tasks (every workspace you belong to, sprint-aware), Obsidian jobsearch state, the Google Calendars your workspaces declare, and two Gmail inboxes (perso + pro) — then cross-references mails against the vault and CRM to update in-flight process status. It also runs a scoring pipeline on LinkedIn job alerts found in the perso inbox, surfaces the best 2-3 offers with fit rationale, and generates an **ordered plan du jour** as the final block. The rendered brief is read-only except for one daily-log write per hal workspace at the end of the run (Step 4), plus description-only updates to a dedicated hal task when routing idea capture out of the daily log (Step 5).

Any session that reviews or cleans up this skill's daily log or hal tasks — reordering, cancelling, merging duplicates, updating descriptions — is **log-only**: it must never execute a task inline (e.g. draft a LinkedIn post, write a CR). See Step 5.

Any backend that is unreachable renders a loud `⚠️ <source> DOWN — <reason>` line instead of silently omitting data. Silent omission is a critical failure.

---

## Invocation modes — interactive vs `--headless`

This skill runs in two modes. **Interactive** (default, no flag) is the full behaviour described in the steps below, run inside a live session with a human present. **`--headless`** is an explicit, unattended-safe mode for scheduled / `claude -p` runs (e.g. a nightly scheduler that has no one to answer prompts or validate output).

`/morning-briefing --headless` differs from interactive exactly as follows — every difference is a **visible** change in the rendered brief, never a silent one:

| Aspect | Interactive (no flag) | `--headless` |
|--------|-----------------------|--------------|
| **Step 1h — CV fan-out** | Runs (spawns `cv-log-worker` sub-agents for 🔥 offers) | **Skipped entirely.** The brief renders the literal line `CV pre-generation: skipped (headless mode)` in the "CVs préparés ce run" section. Omission is visible, never silent. |
| **Plan du jour** | Prompt the user to validate/modify before writing | Rendered with the `[proposé — non validé]` marker and **NOT written to hal**. |
| **Daily-log writes (Step 4)** | Happen | **Still happen** — they are the whole point of the headless run. |
| **Connector failure** (calendar, gmail, brightdata) | `⚠️ <source> DOWN — <reason>` line, run continues | Block states `<source>: UNAVAILABLE (<error>)`, run continues — visible degradation. |
| **hal unreachable** | `hal:DOWN`, Steps 1a/4 skipped, brief still renders | **ABORT with an error** — the daily-log write is the run's purpose, so a headless run with no hal has nothing to deliver. |

The flag toggles only the five rows above. Everything else — sources pulled, block layout, scoring, ordering — is identical in both modes. Interactive behaviour is unchanged by the presence of this contract.

---

## Step 0 — Pre-flight (probe every source before pulling)

Probe each backend independently. Do NOT bail on the first failure — all probes run regardless.

In **`--headless`** mode: a failing **hal** probe ⇒ **abort the run** (raise an error; do not render a partial brief — see Invocation modes). Any **other** failing probe ⇒ its block renders `<source>: UNAVAILABLE (<error>)` instead of the interactive `⚠️ <source> DOWN` line, and the run continues.

- **hal-mcp probe**: call `mcp__plugin_hal_hal-mcp__whoami`. Assert **resolvability, not identity**: it must answer and return at least one workspace in `workspaces[]`. On call failure → mark `hal:DOWN <reason>`, skip Steps 1a, 4. If it answers but `workspaces[]` is empty → mark `hal:DOWN no workspace — whoami returned <the actual payload received>` and skip those steps; with no workspace there is nothing to brief. Never assert a specific email or slug — every downstream step iterates on whatever `whoami` returns.
- **jobsearch-vault probe**: attempt a small read (list active candidatures). On failure → mark `jobsearch:DOWN <reason>`, skip Step 1c.
- **Google Calendar probe**: call `mcp__claude_ai_Google_Calendar__list_calendars`. On failure → mark `gcal:DOWN <reason>`, skip Step 1d. If the error suggests OAuth failure, include "reconnect at claude.ai/connectors" in the message.
- **Gmail perso probe**: call `mcp__plugin_briefing_gmail-mcp__search_emails` with a minimal query (e.g. `after:2000/01/01 maxResults:1`). On failure → mark `gmail-perso:DOWN <reason>`, skip Step 1e.
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

### 1a — hal tasks (one loop over every workspace `whoami` returned)

Do NOT hardcode any slug. For **each** workspace `w` in `whoami.workspaces`:

```
if w.sprints_enabled:
  mcp__plugin_hal_hal-mcp__list_sprints(workspace_slug=w.workspace_slug, status="actuel")
    → 0 entries  : no current sprint          → unfiltered list_tasks + LOUD line (see below)
    → 1 entry    : the current sprint         → check ends_at, then filter by its id
    → 2+ entries : ambiguous                  → unfiltered list_tasks + LOUD line (see below)
  mcp__plugin_hal_hal-mcp__list_tasks(workspace_slug=w.workspace_slug, sprint_id=<id>)
else:
  mcp__plugin_hal_hal-mcp__list_tasks(workspace_slug=w.workspace_slug)
```

`list_tasks` returns `{tasks: [...], total: <n>, returned: <n>, truncated: <bool>}`, not a bare
array — read the task list from `.tasks`. When `truncated` is `true`, `.tasks` holds only the
newest `returned` of `total` matching tasks; render a loud line in that workspace's block —
`⚠️ <workspace> — hal a tronqué la lecture (<returned>/<total> tâches) : les plus anciennes
manquent.` — rather than silently briefing on a partial list. This matters most here: the tag
grouping below assumes it is grouping **every** open task in the workspace.

A workspace without `sprints_enabled` is **not** a workspace missing a sprint — pull its open tasks with no sprint filter and render **no** "(no active sprint)" note.

**The sprint is the selection — so never guess it silently.** `status="actuel"` is declarative: a
human sets it when they plan the week, and hal enforces nothing about its dates. The three
failure modes below each render a **loud line** in that workspace's block AND in the
source-status footer. Never fall back quietly to unfiltered tasks — a briefing that shows the
leftovers of a closed sprint while looking exactly like a normal one is the failure this rule
exists to prevent.

| Condition | Line to render | Tasks shown |
|---|---|---|
| 0 sprints `actuel` | `⚠️ <workspace> — aucun sprint actuel : la semaine n'a pas été planifiée. Tâches ouvertes affichées à défaut.` | unfiltered `list_tasks` |
| 1 sprint, `ends_at` < today | `⚠️ <workspace> — sprint « <name> » toujours actuel mais clos depuis le <ends_at> (J+<n>). Ce sont des restes, pas un sprint vivant.` | that sprint's tasks |
| 2+ sprints `actuel` | `⚠️ <workspace> — <n> sprints marqués actuel (<names>) : sélection ambiguë, aucun filtre appliqué.` | unfiltered `list_tasks` |

`ends_at` may be null — an undated sprint cannot be stale, so render no line for it.

If the enriched `whoami` payload does not carry `sprints_enabled` (phase 1 not yet deployed), render `⚠️ whoami sans champ sprints_enabled — sprint non résolu, tâches ouvertes affichées` for that workspace and fall back to the unfiltered `list_tasks`.

**Label** every task with the workspace's `name` (fall back to `workspace_slug` when `name` is null). Keep each task's **full** `id` — Step 4 daily-log entries reference it as `réf. hal : <workspace_slug>/<id>`, and that reference is the join key the Command Center uses to resolve the task's live state. Never abbreviate it (see Step 5).

**Tag grouping (every workspace).** Group each workspace's returned tasks by their **first** tag, ordered by that workspace's own `allowed_tags` (from `whoami`); tasks with no tag land last, under `other`. Skip groups with zero tasks. If a workspace carries no `allowed_tags`, list its tasks flat (no tag subsection). Never assume a fixed tag list — a second user's workspace has entirely different tags.

### 1c — Obsidian jobsearch (via `jobsearch-vault` skill)

Invoke `jobsearch-vault` and ask for:
1. Upcoming interviews in the next 7 days.
2. Relances due today or overdue.
3. Count and list of active candidatures (company + role + current stage).
4. For each item above, its vault-relative note path as returned by `jobsearch-vault` (e.g. `CRM-JobSearch/Entretiens/<Title>.md`) — needed to build the `obsidian://` link in Step 4.

READ-ONLY — do not write the vault.

The vault name for `obsidian://open?vault=<vault>&file=<path>` links is `SecondLife` (fixed — see the `jobsearch-vault` skill's vault-path resolution). Build the file part by URL-encoding the note path.

### 1d — Google Calendars (union declared by the workspaces)

Build the calendar set from `whoami`, never from literals: the **union of every non-null `calendar_id` and `member_calendar_id`** across all workspaces, deduplicated. `calendar_id` is the calendar shared by the whole workspace (a household or site agenda); `member_calendar_id` is this member's own agenda for that workspace. Calendars the user owns but that no workspace declares are not read — no `#holiday`/import heuristic.

If no workspace declares any calendar (all fields null or absent — e.g. phase 1 not yet deployed) → render `⚠️ Aucun calendrier déclaré sur tes workspaces` in the RDV block and skip the calendar pulls, but keep going. `mcp__claude_ai_Google_Calendar__list_calendars` stays the Step 0 health probe only; it never decides which calendars to read.

For each calendar id in the union, call `mcp__claude_ai_Google_Calendar__list_events(calendarId=<id>, timeMin=<today 00:00 Europe/Paris>, timeMax=<tomorrow 00:00 Europe/Paris>)`.

`timeMin` and `timeMax` MUST be Europe/Paris local time, not UTC. If every calendar returns zero events, extend `timeMax` to +7 days to surface "next upcoming". Merge results, sort by `start`. Tag each event with the **name of the workspace** that declared its calendar (a calendar declared by several workspaces is tagged with the first workspace that declared it).

Do not implement pagination — the default page is enough for a daily window.

Keep each event's `hangoutLink` field, when present — Step 4 links it as the Meet URL for prep/follow-up entries anchored on that event.

### 1e — Gmail perso (via `mcp__plugin_briefing_gmail-mcp__*`)

Which inbox is queried is decided by **which MCP server is called**, never by an address string. This block always targets the perso inbox because it calls the `mcp__plugin_briefing_gmail-mcp__*` server.

Skip if `gmail-perso:DOWN`.

Issue up to three parallel searches:

1. **LinkedIn digests (last 24h)**:
   ```
   mcp__plugin_briefing_gmail-mcp__search_emails(
     query="from:jobalerts-noreply@linkedin.com OR from:jobs-listings@linkedin.com newer_than:1d",
     maxResults=20
   )
   ```
   For each matching email, call `mcp__plugin_briefing_gmail-mcp__read_email(id=<email_id>)` and extract **all** job title + company + location + snippet pairs from the digest body. Do NOT stop at the first offer — parse the entire digest.

   **Job ID extraction**: apply regex `jobs/view/(\d+)` on the plain-text email body. Each match yields a `job_id`. Build the LinkedIn URL as `https://www.linkedin.com/jobs/view/<job_id>`. Store these alongside each parsed offer — this URL survives through Step 1g scoring and Step 1h fan-out all the way to the Step 4 daily log; do not discard it after Step 3 rendering.

2. **Active candidature threads** (match against vault's active candidature list from Step 1c):
   For each active candidature, search:
   ```
   mcp__plugin_briefing_gmail-mcp__search_emails(query="<company_name> newer_than:7d", maxResults=5)
   ```
   Run one search per active candidature (parallel). Read matching threads for context. Keep each matching email's `id` — Step 4 links it as `https://mail.google.com/mail/#all/<messageId>` (no `?authuser=` — see Step 4's Liens rule and the multi-account note there).

3. **Inbound recruiters (last 48h)**:
   ```
   mcp__plugin_briefing_gmail-mcp__search_emails(
     query="(recruteur OR recruiter OR opportunité OR opportunity OR poste OR position) newer_than:2d -from:jobalerts-noreply@linkedin.com",
     maxResults=10
   )
   ```
   Read threads that look like genuine recruiter outreach (not automated digests). Keep each matching email's `id` for the same Gmail-link purpose.

Collect results into: `linkedin_offers[]` (raw, all offers), `candidature_threads[]` (matched to active process, each carrying its Gmail message `id`), `inbound_recruiters[]` (each carrying its Gmail message `id`).

### 1f — Gmail pro (via `mcp__claude_ai_Gmail__*`)

This block always targets the pro inbox because it calls the `mcp__claude_ai_Gmail__*` server — the address is never named.

Skip if `gmail-pro:DOWN`.

Issue two parallel searches:

1. **Commercial responses** (match against active BG opportunities from Step 1a):
   ```
   mcp__claude_ai_Gmail__search_threads(query="newer_than:7d -label:newsletters", maxResults=20)
   ```
   Cross-reference thread subjects/senders against active BG opportunities from the hal CRM context. Read threads that match. Keep each matching thread's `id` — Step 4 links it as `https://mail.google.com/mail/#all/<messageId>` (no `?authuser=` — see Step 4's Liens rule).

2. **Inbound (new contacts, calls for tender)**:
   ```
   mcp__claude_ai_Gmail__search_threads(
     query="newer_than:2d -label:newsletters -label:promotional",
     maxResults=10
   )
   ```
   Flag threads that look like new commercial inbound not matched to any existing CRM entry. Keep each thread's `id` for the same Gmail-link purpose.

Collect into: `bg_commercial_replies[]` (matched to CRM, each carrying its Gmail message `id`), `bg_inbound[]` (new, each carrying its Gmail message `id`).

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
- hal tasks: labelled with each workspace's `name` (fallback `workspace_slug`)
- Calendar events: tagged with the name of the workspace that declared the calendar
- LinkedIn offers: scored list from Step 1g
- Candidature cross-reference: vault stage + mail context from Step 1e
- BG commercial: CRM stage + mail context from Step 1f
- Sources DOWN: `⚠️` line in the relevant section

**Link fields travel with each item.** Gmail message `id`, LinkedIn job URL, vault note path, `hangoutLink`, and hal task `id` collected in Step 1 are carried through this merge and into Step 4 — they are not rendering-only data to discard after Step 3. The rendered chat brief may stay synthetic; the daily log persisted in Step 4 is the one place these links must all surface.

---

## Step 3 — Render the brief

Render in **French** (Renaud's working language). Use the 6-block template below verbatim, substituting actual data. All 6 blocks are mandatory — a DOWN source renders its `⚠️` line, it does not remove the block.

```
# Briefing — <date in French, e.g. mercredi 11 juin 2026>

## 📅 RDV du jour (agendas déclarés par tes workspaces, fusionnés)
HH:MM–HH:MM — <event title> [<workspace name>]
...
(aucun événement aujourd'hui — prochain : HH:MM <date> — <title> [<workspace name>])
(or: ⚠️ Google Calendar DOWN — <reason>  /  ⚠️ Aucun calendrier déclaré sur tes workspaces)

## ✅ Sprint en cours
### <workspace name>
#### <tag>
- [<status>] <title> · échéance <date>
...
(one ### section per workspace `whoami` returned, in whoami's order; one #### subsection
 per first-tag group, ordered by that workspace's allowed_tags, untagged tasks under `other`
 last; skip empty tag subsections; if the workspace has no allowed_tags, list tasks flat
 with no #### subsection)
(⚠️ hal DOWN — <reason>  /  a `sprints_enabled` workspace with no active sprint shows its
 open tasks noted "aucun sprint actif — tâches ouvertes" ; a sprintless workspace shows its
 open tasks with no such note)

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
Gmail perso : ✅  |  ⚠️ DOWN (<reason>)
Gmail pro : ✅  |  ⚠️ DOWN (<reason>)
```

The "Source status" footer is mandatory and ALWAYS renders all five lines — even when all sources are healthy.

### Plan du jour — ordering rules

Build the plan from: calendar events (anchors), hal sprint tasks, vault relances, mail follow-ups. Each task includes a **one-sentence context brief** so it is actionable in a fresh session.

Apply ordering rules in priority order:

1. **MAR–VEN : jobsearch block 08:30–10:30 first** — if today is Tuesday–Friday and the slot is free, put jobsearch tasks first: vault relances, mail replies to recruiters, new 🔥/🟡 offer follow-ups. Exception: on Monday, the IC meeting comes first.
2. **Calendar events as anchors** — add prep task 15–30 min before each event; add post-meeting follow-up immediately after.
3. **Deep-work in open windows** — assign hal sprint tasks to remaining free slots; where the user's workspaces split into revenue-generating vs personal, schedule the revenue-generating workspace's tasks first (see rule 4).
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

The daily log is a **hand-off document**: Renaud opens a fresh session per task and must not have to re-search for context. Every task, offer, and process entry therefore carries a **Liens** sub-line and a **▶️ prochaines actions** sub-line — this is what makes the log exhaustive even though the chat-rendered brief (Step 3) stays synthetic.

**The log carries the selection, never the state.** Two different things used to be stacked in
this document: *which tasks today, in what order, and why* — which only this skill can produce,
from mails, calendar and sprint — and *todo / done*, which belongs to `halcrm_tasks` alone. The
first stays. The second is a copy that rots within the hour: the log is written once at dawn and
every action taken afterwards diverges from it, with nothing to detect it.

So the log lists tasks, with all their context, as a **numbered list — never a `- [ ]`
checkbox**. Ticking is done against hal (Command Center, or `update_task_status` in session),
and the Command Center resolves each line's live state by joining on the `réf. hal` id. Two
consequences, both load-bearing:

- **One line = exactly one task.** Never merge several tasks into a single entry carrying
  several `réf. hal` refs — such a line cannot be resolved, ticked, or counted. Related tasks
  get one line each; put the shared framing in `▶️ prochaines actions`.
- **The id is never abbreviated.** `renaud/7f8158bb` is not a task id; `renaud/7f8158bb…` is
  worse. Print the full 32-character id returned by `list_tasks`, always.

**Liens line — format and rule.** One `  Liens : ` sub-line per entry, listing only the links/refs actually available for that entry, space-separated. **Never fabricate an ID or URL that wasn't captured in Step 1** — omit a link type entirely (do not print a placeholder) when its source ID is missing. Available link types:

| Link type | Rendering |
|---|---|
| Gmail message | `` Gmail `https://mail.google.com/mail/#all/<messageId>` `` |
| LinkedIn offer | `` Offre `https://www.linkedin.com/jobs/view/<jobId>` `` |
| Vault note | `` Vault `<vault-relative path>` (`obsidian://open?vault=SecondLife&file=<path, URL-encoded>`) `` |
| Google Meet | `` Meet `<hangoutLink>` `` |
| hal task/project | `` réf. hal `<workspace_slug>/<id>` `` — full id, never truncated |

**Gmail link — multi-account limitation (accepted).** The Gmail link carries no `?authuser=<address>` parameter: the address must never be published in a public repo. Consequence: with several Google accounts signed into the same browser, the link opens the browser's *active* account, which may be the wrong tab. This is accepted — a wrong tab is cheaper than a published address.

**Prochaines actions line.** One `  ▶️ prochaines actions : <one sentence>` sub-line per entry — the concrete next step, reusing the Step 3 plan-du-jour context brief where the entry also appears there.

#### Uniform daily-log shape (every workspace `whoami` returned)

There is no reference workspace. Write the **same shape** for every workspace, substituting the workspace's `name` (fallback `workspace_slug`) in the title and headers, and driving the tag subsections off that workspace's own `allowed_tags` (from `whoami`). Group sprint tasks by first tag in `allowed_tags` order; tasks with no tag land under `other`, last; skip empty groups; if the workspace declares no `allowed_tags`, list tasks flat with no `###` subsection.

```markdown
# Daily log — <workspace name> — <date in French>

## Sprint en cours [<workspace name>]
<the ⚠️ sprint line from Step 1a, when the sprint is missing, stale or ambiguous — omit when the sprint is healthy>

### <tag>            ← one ### per first-tag group, allowed_tags order; untagged under `other`, last
1. <task title> · priorité : <priority|none> · échéance <due_date, with (**en retard**) when past>
  Liens : réf. hal `<workspace_slug>/<full 32-char task_id>` (+ Vault/Offre/Gmail/Meet when the task is tied to one — whichever were captured in Step 1)
  ▶️ prochaines actions : <one sentence>
2. <one entry per task — never several tasks on one line>
...
(skip empty subsections — or "(aucune tâche en cours)" if all empty)

## Agenda du jour [<workspace name>]
HH:MM — <event title><space>· Meet : `<hangoutLink>` (omit "· Meet :" entirely if none)
...
(or "(aucun événement aujourd'hui)")

## 🎯 Jobsearch — Offres & process   ← render this section ONLY for the workspace whose allowed_tags contains `jobsearch`; omit it entirely for every other workspace
🔥 <title> — <company>
  Liens : Offre `https://www.linkedin.com/jobs/view/<jobId>`
  ▶️ prochaines actions : <one sentence>
🟡 <title> — <company>
  Liens : Offre `https://www.linkedin.com/jobs/view/<jobId>`
  ▶️ prochaines actions : <one sentence>
...
- **<company>** (<role>) — stage : <vault stage>
  Liens : <Vault and/or Gmail — whichever are available>
  ▶️ prochaines actions : <one sentence — e.g. relance due date, mail to answer>
...
(or "(aucune offre ni process jobsearch aujourd'hui)")

## Notes
(vide — à compléter en cours de journée ; les idées/angles capturés en cours de journée référencent une tâche hal dédiée — `réf. hal <workspace>/<id>` — plutôt que d'y recopier le texte, voir Step 5)
```

The commercial process a workspace tracks (CRM opportunities matched to pro mails in Step 1f) renders as extra entries under **Sprint en cours** on that workspace's log, each carrying its `Gmail` / `réf. hal` links — there is no separate hardcoded "Commercial" section.

**Interview-prep example (illustrative, not a fixed schema).** A candidature entering interview prep — e.g. take-home + Meet scheduled — renders as one entry combining every link it has: `Liens : Vault \`CRM-JobSearch/Entretiens/<Title>.md\` (\`obsidian://open?vault=SecondLife&file=...\`) · Offre \`https://www.linkedin.com/jobs/view/<jobId>\` · Meet \`<hangoutLink>\` · réf. hal \`<workspace_slug>/<task_id>\`` followed by `▶️ prochaines actions : terminer le take-home avant le <date>, relire la prep vault, rappeler le recruteur sur Ashby si pas de nouvelles.` Only include the link types that were actually captured in Step 1 for that entry.

---

## Step 5 — Constraints (load-bearing)

- **Read-only for Gmail, calendar, and vault** — no draft, send, label, or delete calls on mail.
- **Writes are limited to two calls** — one `save_document` per hal workspace (Step 4), and a description-only `update_task` append when routing idea capture to a dedicated hal task (see the two bullets below). No other `create_*`, `update_task_status`, or `delete_*` call is permitted anywhere in this skill.
- **Never write if `hal:DOWN`**.
- **Never silently omit a source** — any probe or Step 1 call failure renders `⚠️` in the section AND in the source-status footer.
- **Parse all offers in a LinkedIn digest** — do not stop at the first offer.
- **Dedup offers against vault** — never surface an offer already logged as an active candidature.
- **BrightData cap** — max 5 `web_data_linkedin_job_listings` calls per run. Prioritise 🔥 then 🟡 by location. Per-offer errors are silent — skip and continue.
- **Label every hal task** — with the workspace's `name` (fallback `workspace_slug`), every time. No hardcoded `[business]`/`[perso]` label.
- **Local time** — all calendar windows and daily log slugs use Europe/Paris, not UTC.
- **Compose, do not reimplement** — call `jobsearch-vault` and MCP tools. Never read the Obsidian filesystem directly, never bypass hal-mcp.
- **Agent fan-out cap** — max 3 `cv-log-worker` sub-agents per run. If >3 🔥 deduped offers exist, take the top 3 by score×proximity. Never spawn more than 3 Agent calls in Step 1h.
- **Sub-agent failures are loud** — if a `cv-log-worker` returns `ÉCHEC`, surface `⚠️ CV non généré — <company> : <reason>` in the "CVs préparés ce run" section. Never silently drop a sub-agent failure.
- **No auto-apply, no cover letter** — sub-agents generate CVs and log applications only. They never submit applications, send messages, or generate cover letters.
- **Status `📝 À postuler`** — the sub-agent logs applications with this status, NOT `✉️ Candidature envoyée`. Renaud moves the card to « Candidature envoyée » when he actually submits.
- **Relationship with `mail-triage`** — Steps 1e/1f do a lightweight, context-integrated mail pass for the daily briefing. The `mail-triage` skill (also in this plugin) provides a deeper, on-demand triage with explicit per-thread classification. Do NOT call `Skill(mail-triage)` from inside this skill — the shallow pass here is intentionally faster and context-lighter. Users who want full triage run `/mail` separately.
- **Daily log is the hand-off, not the chat brief** — every task/offer/process entry written in Step 4 carries a `Liens` sub-line and a `▶️ prochaines actions` sub-line, so Renaud can work each entry in a fresh session without re-collecting context. The Step 3 chat brief can stay synthetic; Step 4 may not.
- **Never fabricate a link** — a `Liens` sub-line lists only link types whose source ID/URL was actually captured in Step 1 (Gmail message id, LinkedIn job id, vault note path, `hangoutLink`, hal task id). Omit a link type silently rather than guessing or printing a placeholder.
- **The daily log never carries task state** — no `- [ ]`, no `- [x]`, anywhere, in any section. `halcrm_tasks` is the single source of truth for status; the log holds the day's selection and its context. Writing a checkbox creates a second, editable copy of the state that nothing reconciles — the exact divergence this skill is forbidden from producing. Ticking happens via `update_task_status` (Command Center, or in session), never by editing this document.
- **One line = one task, with its full id** — never merge several tasks into one entry carrying several `réf. hal` refs, and never abbreviate an id. The `<workspace_slug>/<id>` pair is the join key the Command Center uses to resolve live state; a merged line or an 8-character prefix breaks it silently.
- **A missing, stale or ambiguous sprint is loud** — the sprint is the day's selection, and hal enforces nothing about it: `status="actuel"` is set by hand and stays until someone moves it. Zero `actuel`, several `actuel`, or one whose `ends_at` has passed each render the Step 1a `⚠️` line in the workspace's block AND in the source-status footer. Never present the leftovers of a closed sprint as if they were this week's plan.
- **Daily-log / task-cleanup sessions are log-only, never execution** — this applies whenever a session reviews or maintains this skill's daily log or hal tasks (updating status, cancelling, merging duplicates, editing a description), whether that happens inside a Step 4 run or in a later, separate conversation looking at the daily log / Command Center dashboard. In that context, only list, log, and update task bookkeeping — never execute a task (e.g. draft the LinkedIn post, write the CR) inline, and never offer "I'll do X now — which option do you want?". Executing a task happens in its own dedicated session, started separately.
- **Route idea capture to a dedicated hal task, not into the daily log** — when a task-cleanup session surfaces an idea/angle worth capturing (e.g. LinkedIn post angles with stats from the last post), first look for an existing dedicated hal task for that topic via `mcp__plugin_hal_hal-mcp__list_tasks`. There is no full-text search — filter by tag (use an allowed workspace tag such as `marketing`, never a hardcoded `linkedin` tag <!-- TODO: verify in Cowork: exact tag/title convention the workspace uses for the dedicated LinkedIn-idea task --> ) and match the title client-side. If found, call `mcp__plugin_hal_hal-mcp__update_task` to append the idea to that task's `description` (append, never overwrite prior content) and reference only `réf. hal <workspace>/<id>` from the daily log's Notes section — do not paste the narrative content into the daily log itself. If no dedicated task exists, say so and ask before creating one (`create_task` is not in this skill's allowed-tools).
