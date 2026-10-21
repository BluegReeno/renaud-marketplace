---
name: morning-briefing
description: >
  Produce one morning briefing: today's calendars (declared by your hal
  workspaces), current-sprint hal tasks across every live workspace you belong to,
  a job-search paragraph (applications to do with offer link, CV path and judge
  score; every offer of every LinkedIn digest received since the last briefing,
  read in full through read-job-offer and scored on the job description; a judged
  CV for each 🔥 offer; processes in flight), the Blue Green commercial pass, an
  ordered plan du jour — then one daily-log document per workspace that has a task
  or an appointment today. The enrichment and the CV fan-out run in scheduled
  (`--headless`) runs too. On weekends it runs a personal-only variant. Use when
  the user asks "what's up for today", "ma journée", "briefing du jour", "quel est
  mon planning", or any similar daily-overview trigger.
allowed-tools: "Bash mcp__plugin_hal_hal-mcp__whoami mcp__plugin_hal_hal-mcp__list_sprints mcp__plugin_hal_hal-mcp__list_tasks mcp__plugin_hal_hal-mcp__list_projects mcp__plugin_hal_hal-mcp__list_documents mcp__plugin_hal_hal-mcp__get_document mcp__plugin_hal_hal-mcp__save_document mcp__plugin_hal_hal-mcp__update_task mcp__claude_ai_Google_Calendar__list_calendars mcp__claude_ai_Google_Calendar__list_events mcp__plugin_briefing_gmail-mcp__search_emails mcp__plugin_briefing_gmail-mcp__read_email mcp__claude_ai_Gmail__search_threads mcp__claude_ai_Gmail__get_thread Skill(read-job-offer) Skill(jobsearch-vault) Skill(offer-to-cv) Agent(cv-judge)"
---

# Morning Briefing

One read-only view of the day, then one daily-log write per workspace that has something that day.
The only writes in this skill are the `save_document` daily logs (Step 4) and a description-only
`update_task` append when routing idea capture (Step 5).

A session that reviews or cleans up this skill's daily log or hal tasks is **log-only**: it lists,
logs and updates bookkeeping, and never executes a task inline (no LinkedIn draft, no CR). Execution
happens in its own session.

Any unreachable source renders `⚠️ <source> DOWN — <reason>`. Silent omission is a critical failure.
A block that is **out of scope** (see Step 0) is not a failure: it is omitted and the header line says
why.

---

## Modes

**Interactive** (default) and **`--headless`** (scheduled or `claude -p` runs, nobody to answer).
`--headless` differs in exactly these rows, each visible in the brief:

| Aspect | Interactive | `--headless` |
|---|---|---|
| Plan du jour | user validates or edits it | marked `[proposé — non validé]`, not asked about |
| hal unreachable | `hal:DOWN`, brief still renders | **abort with an error** — the daily log is the run's purpose |
| Connector failure | `⚠️ <source> DOWN — <reason>` | `<source>: UNAVAILABLE (<error>)`, run continues |

Everything else is identical — in particular the job-search pipeline of Step 2c: the offers are
enriched through `read-job-offer` and every 🔥 gets a judged CV through `offer-to-cv` **in both
modes**. Until briefing 0.24.0 a scheduled run skipped the fan-out, because it had no vault; since
2026-10-21 « Briefing quotidien » is a local Claude Desktop scheduled task (Auto
permissions, Synology folder mounted), so the run reads and writes the vault through
`jobsearch-vault` Case B exactly like an interactive one (renaud#175). A headless run whose vault
is unreadable still skips the fan-out, for the reason 2c.1 prints — never silently.

**Week-end variant** — Saturday and Sunday, Europe/Paris, in either mode. Personal only: see Step 0.
Nothing in it asks for validation: the daily log is written as soon as the brief is built.

---

## Step 0 — Pre-flight and scope

Call `whoami` once. It must answer with at least one workspace; otherwise `hal:DOWN no workspace —
whoami returned <payload>` and skip every hal step (headless: abort). Never assert an email or a slug.

Build the scope from `whoami` alone, never from a literal:

- **live** = workspaces with `archived: false`. An archived workspace is never read for the brief,
  never written (hal refuses writes by name). It stays out of every block and every log.
- **weekday scope** = all live workspaces (both of Renaud's — personal and job search — are read: the
  planner sees one picture).
- **week-end scope** = live workspaces with `type: "personal"`. Pro mail, the Blue Green commercial
  pass and everything about job offers are out of scope; so are calendars declared only by
  out-of-scope workspaces.
- **job-search block** exists only when a live workspace has `type: "jobsearch"` (weekday only). No
  such workspace, or it is archived → the block is absent, no `⚠️`, no vault probe, no LinkedIn digest
  search.

Probe the remaining sources independently; one failure never stops the others:

- **Google Calendar**: `list_calendars`. Failure → `gcal:DOWN <reason>` (OAuth error → add
  "reconnect at claude.ai/connectors").
- **Gmail perso** (`mcp__plugin_briefing_gmail-mcp__*`) and **Gmail pro** (`mcp__claude_ai_Gmail__*`),
  weekday only: a minimal search each. The server called decides the inbox, never an address string.
- **Vault**, only when the job-search block exists: a small `jobsearch-vault` read.

Print one header line under the title: `Mode : semaine` or `Mode : week-end perso (<names of the
workspaces in scope>)`.

---

## Step 1 — Context from hal (silent, never echoed)

For each live in-scope workspace, `get_document` (404 / empty is normal):

- `daily-log-<today>` — keep its **entire** `content_md` verbatim: Step 4 must append to it, never
  replace it (on 2026-09-04 an interactive run destroyed the morning's automatic log).
- `daily-log-<yesterday>` — keep its `## Notes` section only.
- `soul` and `memory` — the fixed blocks (below) and the workspace's own priorities.

**Fixed blocks come from hal, never from this file.** Nothing about time is written in this skill: no
meeting day, no school run, no job-search slot, no day start. They are the lines of a section titled
`## Blocs fixes` in the workspace's `soul` or `memory` document, one per line:
`- <days> HH:MM–HH:MM — <label>`, plus optionally `- <days> — début de journée HH:MM`. Read the section
from every in-scope workspace and merge them. If none declares any, render `⚠️ aucun bloc fixe déclaré
dans soul/memory` once in the plan block and plan without hours.

---

## Step 2 — Pull data (parallel where independent)

### 2a — Tasks, per live in-scope workspace

```
if w.sprints_enabled:
  list_sprints(workspace_slug, status="actuel")
    0 entries → unfiltered list_tasks + loud line
    1 entry   → filter by its id only if ends_at is null or today-or-later
    2+        → unfiltered list_tasks + loud line
else: list_tasks(workspace_slug)        # no sprint note at all
```

`list_tasks` returns `{tasks, total, returned, truncated}`. `truncated: true` → read again with the
same filters and `limit=<total>`: the brief works on the whole list, never on its newest page. Show open
tasks (not `done`, not `cancelled`).

A sprint is declarative (hal enforces nothing about its dates), so never guess it silently. Each case
renders a loud line in the workspace block **and** the footer, and never falls back quietly:

| Condition | Line |
|---|---|
| 0 sprints `actuel` | `⚠️ <ws> — aucun sprint actuel : la semaine n'a pas été planifiée. Tâches ouvertes affichées à défaut.` |
| 1 sprint, `ends_at` < today | `⚠️ <ws> — sprint « <name> » toujours actuel mais clos depuis le <ends_at> (J+<n>). Restes, pas un sprint vivant. Tâches ouvertes affichées à défaut.` |
| 2+ sprints `actuel` | `⚠️ <ws> — <n> sprints marqués actuel (<names>) : sélection ambiguë, aucun filtre appliqué.` |

A closed sprint **never filters** (on 2026-09-03 one surfaced 6 tasks out of some fifty open). When the current sprint
is closed, look for its successor: `list_sprints(status="suivant")`, then `"a_venir"`; keep the one
whose interval contains today and append `→ « <name> » couvre aujourd'hui mais est resté « <status> » :
transition_sprint(workspace_slug="<slug>", incoming_sprint_id="<full id>").`, or `→ aucun sprint ne
couvre aujourd'hui : /sprint-planner.` Diagnostic only: never call `transition_sprint`.

Label every task with the workspace `name` (fallback slug). Keep each task's **full** id.
Group by **first tag**, in the workspace's `allowed_tags` order, untagged under `other` last, empty
groups skipped; no `allowed_tags` → flat list.

### 2b — Calendars

Union of every non-null `calendar_id` and `member_calendar_id` of the in-scope live workspaces,
deduplicated. Calendars no workspace declares are not read. None declared → `⚠️ Aucun calendrier
déclaré sur tes workspaces`. For each id: `list_events(calendarId, timeMin=<today 00:00 Europe/Paris>,
timeMax=<tomorrow 00:00 Europe/Paris>)` — Paris local time, never UTC. All empty → extend to +7 days
for a "prochain". Merge, sort by start, tag each event with the first workspace that declared its
calendar, keep `hangoutLink`.

### 2c — Job search (weekday, only when the job-search block exists)

**1. Vault** via `Skill(jobsearch-vault)`, read-only: interviews in the next 7 days; relances due or
overdue (the candidatures' `date_relance`; relance tasks are hal tasks, already read in 2a — never
`Taches/`); active candidatures (always `--limit 500`; active = any status not in `❌ Refus`, `🗄️ Sans
suite` / `❌ Sans suite (mort)`, `⛔ Abandonné` / `❌ Abandonné`, `✅ Offre reçue` / `Gagné`); and every
candidature at `📝 À postuler`, with its `lien_offre`, the `Fichier` and `Juge` lines of its `## CV
généré` section, and its note path (for the `obsidian://open?vault=SecondLife&file=<url-encoded
path>` link).

The vault not read is never a footer detail: it opens the brief (Step 3, `⚠️ Vault`). Two cases,
named by `jobsearch-vault` (its Case C), never merged into one vague line:
- **not mounted** — no linked device, or the Synology folder is absent: `⚠️ vault non monté —
  <what the skill printed>`;
- **mounted but not read** — the vault was found and the call failed, or `CRM-JobSearch` came back
  with unreadable files: `⚠️ vault monté mais illisible — <the error or the unreadable count,
  verbatim>`.

Either way skip the vault parts, and the 2c.2 per-candidature mail searches with them.

**2. Mail (perso inbox)** — first the window, then three searches, skipped on `gmail-perso:DOWN`.

**The window is « since the last briefing », never `newer_than:1d`.** Compute `SINCE` once, before
any search, from the job-search workspace's own logs:

- `list_documents(workspace_slug=<job-search workspace>, kind="daily-log")` → the highest
  `daily-log-<YYYY-MM-DD>` slug. `get_document` it (when it is `daily-log-<yesterday>`, Step 1
  already holds it) and take its **`created_at`**: `SINCE` = that instant, as UTC epoch seconds.
  `created_at` and not `updated_at`: a second run the same day must start where the morning run
  started, not where a cleanup session appended.
- No daily-log at all → `SINCE` = now − 3 days.
- Say which in the brief: `Fenêtre : depuis le daily-log du <date> <HH:MM> (Europe/Paris)` or
  `Fenêtre : 3 jours (aucun daily-log)`.

Why: `newer_than:1d` is « the last 24 hours on the run's clock » (checked on 2026-10-21: it is
rolling, not midnight-aligned). It only holds while every run happens, on time, every day: a run
that slips, fails or is skipped loses what arrived in the gap, and nothing records what the
previous run actually saw. On 2026-10-21 the 06:19 UTC run could not see the six-offer digest
carrying HappyRobot (07:40 UTC); the next run would have — only because it ran within 24 hours,
and without knowing those offers were new to it (renaud#175). `after:<SINCE>` ties the window to
the last log actually written: whatever arrived after it is read by the next run, however late
that run comes, and the log's `Offres vues ce run` line (Step 4) says what was seen. Only the
job-search workspace's logs count, and Step 0 writes none for it on a week-end, so Monday's window
spans Friday → Monday; a run that failed to write its log widens the next window instead of losing
mail.

- LinkedIn digests: `(from:jobalerts-noreply@linkedin.com OR from:jobs-listings@linkedin.com OR
  from:jobs-noreply@linkedin.com) after:<SINCE>`, `maxResults=50`. Gmail's `after:` accepts epoch
  seconds, which is what gives the window its precision. 50 results back → `⚠️ digests tronqués à
  50` (the search tool has no next page). `read_email` **each** digest and work on its plain-text
  **body**, never on its subject: the subject names one offer, the body carries up to six. The job
  ids are **every** match of the regex `jobs/view/(\d+)` on the body (the digest links read
  `linkedin.com/comm/jobs/view/<id>/?trackingId=…`, and the same id repeats in the footer's
  `originToLandingJobPostings=` list — deduplicate inside the digest). For each id keep the title,
  the company and the location: the three lines above its `View job:` line. The URL is
  `https://www.linkedin.com/jobs/view/<id>`. On 2026-10-21 the 07:40 UTC digest's subject said
  « MLabs »; its body carried six ids, HappyRobot and OpenAI among them.
- Active-candidature threads: company names of the active candidatures, **OR-groups of at most 10**
  (a 20-name query returns `[]` without an error), `newer_than:14d -from:*linkedin.com
  -from:*substack.com -from:*skool.com`, `maxResults=25` — a 14-day look-back on purpose: this
  search reads the *state* of a process from its last mail, it does not look for new mail.
  `read_email` the **newest** message of each matched thread and keep its id. `fetchError:true` is a
  partial read, kept and marked degraded. Skipped, with `⚠️ recherches mails par candidature NON
  exécutées`, when the vault is unreadable.
- Inbound recruiters: `(recruteur OR recruiter OR opportunité OR opportunity OR poste OR position)
  after:<SINCE> -from:jobalerts-noreply@linkedin.com`, `maxResults=10`; keep genuine outreach only.

**A process's stage comes from its last mail, never from a hal task description.** When they disagree,
the mail wins and the gap is written out: `⚠️ tâche hal désynchro : <task says> vs <last mail says>`.

**3. Dedup, enrich, score** — in that order, so no BrightData call is spent on a known offer.

**Dedup on the job id, before any enrichment.** An id is already known when:
- a vault candidature's `lien_offre` carries it — the Opportunites list read in 2c.1 (`--limit 500`),
  compared on the id (`jobs/view/(\d+)` on `lien_offre`), never on the URL string; or
- it appears in the `Offres vues ce run :` line of a daily-log of the last 7 days: the latest log is
  in hand from the window computation, the others come from the same `list_documents` answer
  (slugs dated within 7 days, `get_document` each). LinkedIn repeats an offer across digests for
  days — HappyRobot was in both the 07:40 and the 13:40 digests of 2026-10-21.

A known id is counted (`K déjà vues`), never enriched, never scored again; when its vault status is
active it is a process in flight, shown there as usual. A **company** match without an id match is
not a dedup: the offer stays, scored on its own JD, with `⚠️ <company> : <vault status> sur
<role> (<date>)` so Renaud sees the history (on 2026-10-22: monday.com refused the Forward Deployed
Consultant application two weeks before posting a Forward Deployed Engineer).

**Title pre-screen, no BrightData.** An offer is **in target** when its digest title names a role
family of the 🔥 or 🟡 rows below and its digest location is Paris, Île-de-France or remote.
Anything else is **hors cible**: counted (`H hors cible`), listed by title in one line, never
enriched — a 3-day window after a week-end carries dozens of « ingénieur SCADA Montpellier » lines
that no JD read would turn into a candidature.

**Enrich every in-target offer** with `Skill(read-job-offer)` (job id in; `jd_text`, `location`,
`freshness`, `applicant_count` out), in both modes, 🔥-looking titles first, then 🟡 by closest
location. Never read a LinkedIn JD any other way (no scrape, no built-in browser: the login wall
raises a keychain prompt). `status: unavailable` → that offer is scored on title+snippet and marked
`(JD non lue)`. **Safety bound: 20 invocations per run.** It was 8 — set on 2026-09-04 for a one-day
window and a three-offer product cap; with a window that can span a week-end and a fan-out that
runs every day, the pre-screen leaves 5–10 in-target offers on an ordinary morning, so 20 covers
a long window with margin and still caps a runaway digest day. Offers beyond the bound are scored
on title+snippet and surfaced **without a CV**; say `N offres enrichies, M scorées sur titre seul`.

**Score on the full JD.** Read the two data files — never write a figure or a disqualifier here:

```bash
# The plugin as loaded first (jobsearch is briefing's sibling), the install paths after.
cat "${CLAUDE_PLUGIN_ROOT}/../jobsearch/data/comp-thresholds.json" 2>/dev/null \
  || cat ~/Projects/renaud-marketplace/plugins/jobsearch/data/comp-thresholds.json 2>/dev/null \
  || cat ~/.claude/plugins/cache/renaud-marketplace/jobsearch/*/data/comp-thresholds.json 2>/dev/null
cat "${CLAUDE_PLUGIN_ROOT}/../jobsearch/data/role-criteria.json" 2>/dev/null \
  || cat ~/Projects/renaud-marketplace/plugins/jobsearch/data/role-criteria.json 2>/dev/null \
  || cat ~/.claude/plugins/cache/renaud-marketplace/jobsearch/*/data/role-criteria.json 2>/dev/null
```

`fire_tier_min_eur` and `comp_floor_eur` from the first, `disqualifiers[]` from the second; an
unreadable file renders `⚠️ seuils rému illisibles` / `⚠️ critères qualitatifs illisibles` and the
related tier is not applied — never a remembered value.

The location, the compensation and the disqualifier read come from the JD, not from the digest line:

| Score | Criteria |
|---|---|
| 🔥 | builder role — Solution Architect IA / Solutions Engineer / FDE / Applied AI Engineer or Architect / Head of AI Eng — at an AI lab, an AI vendor or an AI-native scale-up; Paris or hybrid Paris; the JD asks for hands-on building; no disqualifier; stated comp ≥ `fire_tier_min_eur` **or no figure stated** |
| 🟡 | the same families at a consultancy, an ESN, a recruitment intermediary or a corporate; CTO / EM / Senior AI Eng / Head of Data&AI depending on context; remote-ok from outside Paris; a contract / CDD; or stated comp between `comp_floor_eur` and `fire_tier_min_eur` |
| ❌ | stated comp < `comp_floor_eur`, or the JD clearly matches a `disqualifiers[]` entry |
| — | hors cible (pre-screen): neither family, or outside Paris with no remote |

No stated compensation is never ❌, and never a downgrade from 🔥 either: an unstated figure is
neutral (HappyRobot wrote « competitive salary + equity » and is 🔥). Prefer builder AI-native over
COMEX roles. An offer scored on title+snippet only (bound reached, JD unavailable) is marked so.

Order: tier first, never crossed; inside a tier, fresher (< 24 h) and less contested (< 30 applicants)
first. Surface the top 2-3 with a one-line "pourquoi" citing a concrete JD signal.

**4. CV fan-out** — in both modes. For **every** 🔥 offer not already in the vault and
enriched, in the order above, invoke the `offer-to-cv` skill **inline, one offer after the
other** — it runs in this context, so it has the `Agent` tool and spawns `cv-judge` itself. Until
2026-10-21 this step spawned a `cv-log-worker` agent per offer; the runtime launched it in the
background, where no `Agent` tool exists, and the CV was logged « ⚠️ CV non jugé » (renaud#176).
Sequential is the price of a judged CV every time. A scheduled run generates and logs exactly
like an interactive one: the candidature lands at `📝 À postuler` and Renaud finds it in the
morning's « À postuler » list. A 🔥 whose company carries a `⚠️` history line still gets its CV —
the decision to send is Renaud's, at the « À postuler » stage, with the history in front of him.

```
Skill(offer-to-cv)
JOB_TITLE: <title>
COMPANY: <company>
JD_TEXT: <jd_text from read-job-offer>
SENDER_EMAIL: <from address of the digest that carried the offer>
JOB_URL: <https://www.linkedin.com/jobs/view/<id> or empty>
DATE: <YYYY-MM-DD Europe/Paris>
```

The judge runs after every generation, Tour 1 then Tour 2: that is the skill's own contract,
nothing to add here. Never invoke it without a real `jd_text` (a CV built on a digest snippet is
plausible, hollow and unmarked). Safety bound 8 CVs per run (each one costs a generation and two
judge spawns; the enrichment bound above is the separate, cheaper one), never silent: `11 offres
🔥 — 8 traitées, 3 listées sans CV`. Collect each returned line verbatim (`CV_préparé | … | Juge :
<v1>→<v2>/10`, or with a trailing `| ⚠️ …`, or `ÉCHEC | …`) — never strip a marker.

### 2d — Blue Green commercial pass (weekday, per live `company` workspace)

Only when `opportunity` is in the workspace's `kinds_enabled` (a disabled kind is refused by name):
`list_projects(workspace_slug, kind="opportunity")`, `truncated: true` → again with `limit=<total>`,
keeping stages in `kind_stages.opportunity.active`.
Pro inbox, two searches: `newer_than:7d -label:newsletters` (`maxResults=20`) matched against the
projects' `company` / `contact` (name, email domain) and read; `newer_than:2d -label:newsletters
-label:promotional` (`maxResults=10`) for new commercial inbound matching nothing. Keep every thread
id. Skipped on `gmail-pro:DOWN`.

---

## Step 3 — Render (French)

Blocks in this order. A block in scope is mandatory (its `⚠️` replaces its content); a block out of
scope is omitted.

```
# Briefing — <date en français>
Mode : <semaine | week-end perso (…)>

> ⚠️ Vault : <vault non monté | vault monté mais illisible> — <detail, verbatim>   ← only when 2c.1 did not read it
> Candidatures, entretiens et relances ci-dessous incomplets.

## 📅 RDV du jour
HH:MM–HH:MM — <title> [<workspace>]
(aucun événement aujourd'hui — prochain : HH:MM <date> — <title> [<workspace>])

## ✅ Tâches en cours
### <workspace name>
<⚠️ sprint line, when any>
#### <tag>
- [<status>] <title> · échéance <date>

## 🎯 Jobsearch                                   ← only with a live type=jobsearch workspace, weekday
### À postuler
- **<company> — <role>** · Offre <JD link> · CV <path> · Juge <v1>→<v2>/10
  (one line per application to do: every vault note at 📝 À postuler plus this run's new CVs; a missing
   judge score is written `Juge : non noté`, a missing CV `CV : à générer`, a missing link `Offre : —`)
(aucune candidature à faire)
### Nouvelles offres
Fenêtre : depuis le daily-log du <date> <HH:MM> (Europe/Paris) | 3 jours (aucun daily-log) · <n> digests
🔥|🟡 <title> — <company> — <location> · <freshness>, <applicant_count> candidats
   → <pourquoi>
   ⚠️ <company> : <vault status> sur <role> (<date>)          ← only on a company match
Hors cible : <title — company>, …
N offres enrichies, M scorées sur titre seul, K déjà vues, H hors cible
### Process en cours
- **<company>** (<role>) — stage : <vault stage>
  → Mail récent : <subject> [<date>] — <one line, from the LAST message>
  → Relance : <date | non due | en retard>
Entretiens à venir : <list | aucun cette semaine>
Autres mails jobsearch : <subjects not matched>
### CVs préparés ce run
- ✅ <title> — <company> (P<n>) → <cv> · Juge <v1>→<v2>/10
- ⚠️ ÉCHEC <title> — <company> → <reason>
(aucune offre 🔥 ce run)

## 💼 Commercial                                  ← only with a live company workspace, weekday
- **<company/contact>** — <opportunity> — stage : <stage>
  → Mail récent : <subject> [<date>] — <summary>
Nouveaux inbound : <list | aucun>   ·   Autres mails pro : <subjects>

## 📋 Plan du jour
- HH:MM (≈Xmin) — <task>
  → <one sentence: who, what, why, where the context is>

## Source status
hal-mcp : ✅ | ⚠️ …   ·   Google Calendar : ✅ | ⚠️ …
jobsearch-vault : ✅ | ⚠️ …   ·   Gmail perso : ✅ | ⚠️ …   ·   Gmail pro : ✅ | ⚠️ …
(only the sources in scope; a source out of scope is listed as « hors périmètre (week-end) »)
```

`Gmail perso : ✅` requires the three searches of 2c.2 to have run; name the sub-steps that did not
(`⚠️ sous-étapes non exécutées : 2c.2 candidatures`), and `⚠️ lecture partielle (fetchError sur <n>
mail(s))` when a result carried `fetchError`.

### Plan du jour

Built from: calendar events, the fixed blocks of Step 1, open tasks, vault relances, mail follow-ups.

1. **Fixed blocks** from Step 1 are placed first; day start from the same section.
2. **Calendar events are anchors**: a prep task 15-30 min before, a follow-up right after.
3. **Open windows** take the tasks, ordered by the priority each workspace states in its `soul`, then
   by `priority` and `due_date`. With a job-search block, the applications to do and the due relances
   come before the rest unless a `soul` says otherwise.
4. Week-end: only the personal scope's tasks and events; no job-search item, no pro item.

Interactive weekday: ask the user to validate or modify the plan. Headless and week-end: mark it
`[proposé — non validé]` and do not ask.

---

## Step 4 — Daily logs

Skipped on `hal:DOWN`. One document per workspace that is **live, in scope, and has a task in today's
selection or an appointment today** (an event on a calendar it declares, or — job-search workspace — an
interview or a relance due in the vault). No task and no appointment → no log. An archived workspace
never gets one.

`save_document(workspace_slug, slug="daily-log-<YYYY-MM-DD>", domain="memory", kind="daily-log",
title="Daily log — <workspace slug> — <date en français>", content_md)`.

**Never overwrite a log written earlier today** (`save_document` replaces silently). Today's log
absent → write. Present → send its existing `content_md` back **verbatim and whole**, then append:

```
---

## Run <HH:MM> (Europe/Paris)

<what this run would have written>
```

A write failure on one workspace renders `⚠️ Daily log <slug> — write failed: <reason>` after the
footer and never blocks the others.

The log is a **hand-off document**: tomorrow's fresh session must not re-search anything. So every
entry carries a `Liens` line and a `▶️ prochaines actions` line.

- **The log carries the selection, never the state.** Tasks are a **numbered list, never `- [ ]`**.
  Status lives in hal alone (`update_task_status`); a checkbox here is a copy that rots within the hour.
- **One line = one task**, never several `réf. hal` refs on one line; the id is the **full** 32
  characters, never abbreviated — the Command Center joins on `<workspace_slug>/<id>`.
- **Liens**: only links actually captured, space-separated, no placeholder: Gmail
  `https://mail.google.com/mail/#all/<messageId>` (no `?authuser=`: the address stays out of this public
  repo), Offre `https://www.linkedin.com/jobs/view/<jobId>`, Vault `<path>` (+ `obsidian://` link),
  Meet `<hangoutLink>`, `réf. hal <workspace_slug>/<id>`. Never fabricate one.

```markdown
# Daily log — <workspace name> — <date en français>

## Sprint en cours [<workspace name>]
<⚠️ sprint line, if any>

### <tag>
1. <task title> · priorité : <priority|none> · échéance <date, (**en retard**) when past>
  Liens : réf. hal `<workspace_slug>/<full id>` …
  ▶️ prochaines actions : <one sentence>

## Agenda du jour [<workspace name>]
HH:MM — <event>  · Meet : `<hangoutLink>`
(aucun événement aujourd'hui)

## 🎯 Jobsearch — Offres & process        ← only in the type=jobsearch workspace's log
<per application to do: Offre / CV / Juge, then 🔥/🟡 offers, then processes in flight —
 each with Liens + ▶️ prochaines actions>
Offres vues ce run : <id> <id> <id> …

## Notes
(vide — idea captured during the day: a reference to a dedicated hal task, not the text)
```

Commercial threads matched in 2d render as extra entries under the company workspace's sprint section,
with their `Gmail` / `réf. hal` links.

**`Offres vues ce run :`** — the job-search log carries, on one line, **every** job id extracted
from the window's digests (in target or not, enriched or not, 🔥 to hors cible), space-separated,
bare ids. It is the dedup memory of 2c.3: the next runs read it back with `\d{9,}` on that line and
never enrich those ids again. Until 2026-10-21 the log listed only the surfaced offers, by Gmail
message id, so nothing told the next run which offers it had already seen (renaud#175). The line
is written even when the run surfaced nothing; the log's `## Notes` stays reserved for ideas.

---

## Step 5 — Constraints

- **Read-only** for Gmail, calendar and vault. No draft, send, label or delete.
- **Writes**: the Step 4 `save_document` calls, and description-only `update_task` appends below. No
  `create_*`, no `update_task_status`, no `transition_sprint`, no `delete_*`.
- **Never write if `hal:DOWN`.** Never write to an archived workspace.
- **Never silently omit a source in scope**: `⚠️` in the block and in the footer.
- **Local time**: calendar windows and log slugs are Europe/Paris, not UTC.
- **Compose, do not reimplement**: `jobsearch-vault` and hal MCP tools only; never read the Obsidian
  filesystem, never bypass hal-mcp.
- **No auto-apply, no cover letter, no message sent**: workers produce a CV and log a `📝 À postuler`
  candidature; Renaud moves it to « Candidature envoyée » when he submits.
- **`mail-triage` is a separate on-demand skill**: do not call it from here.
- **Route idea capture to a dedicated hal task**: when a cleanup session surfaces an idea, find the
  dedicated task by `list_tasks` filtered on an allowed tag, matched on title client-side (no full-text
  search). Found → `update_task` appends to its `description` (append, never overwrite) and the log's
  Notes references only `réf. hal <workspace>/<id>`. Not found → say so and ask; `create_task` is not
  allowed here.
- **Tags** mean functional domain: only values of the workspace's `allowed_tags`, `other` when nothing
  fits; hal-mcp enforces it.
