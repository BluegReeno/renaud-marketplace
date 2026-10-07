# Changelog

One file for every plugin in this marketplace. Entries are grouped per plugin, newest version
first. Heading format — parsed by `scripts/check_version_sync.sh`, written by
`scripts/release.sh`: `## <plugin> <version>`.

## Versioning

This section is the single definition of the version rule; `CLAUDE.md` points here.

Every plugin is pre-1.0 and versions as `0.MINOR.PATCH`:

- **MINOR** (`0.X+1.0`) — new behaviour or a changed contract: a skill, agent, command or MCP
  tool added, removed or renamed; a skill's inputs, outputs, statuses or write targets changed.
- **PATCH** (`0.x.Y+1`) — a fix, or a wording change, that leaves every caller's contract intact.
- **1.0** — not reached by any plugin: none has declared a stable interface yet.

Every functional change ships a bump, however small — Cowork detects updates by version number
alone, so an unbumped fix never reaches an installed plugin. The top-level `version` of
`.claude-plugin/marketplace.json` is a separate counter, +0.0.1 on every release.

Every version ever shipped has an entry below. A plugin keeps its history across a rename:
`jobsearch` 0.1.x shipped as `cv-generator`, `mycoach` 0.1.0–0.2.0 as `myspy`. Entries up to
`briefing` 0.4.1 and `jobsearch` 0.11.0 come from the per-plugin changelogs removed in `88cde3a`;
the versions those files never covered were written afterwards from their release commits
(renaud#102).

## session 0.1.0

- New plugin: `wrap-up` closes a session in one pass — inventory of what is not yet on the remote, then either a clean close or a per-branch handoff in `.git/claude-handoffs/` that the SessionStart hook injects into the next session

## briefing 0.21.1

- mail-triage: relance_possible no longer points at the retired /cover-letter

## briefing 0.21.0

- Step 1c requests --limit 500 and filters closed statuses; Step 1e.2 batches candidature searches in 10-name OR groups on newer_than:14d, reads each thread's last message, and the mail always wins over a stale hal task; Gmail perso footer is now conditional on all three 1e sub-steps having run

## briefing 0.20.1

- mail-triage reads the {contacts, companies} envelope hal-mcp returns since hal#171 and pages until truncated is false — the default page is 100 of 381 contacts

## briefing 0.20.0

- Add qualitative role gate (Step A.6) to cv-log-worker before CV generation

## briefing 0.19.0

- Judge-review CVs before logging (two-round cv-judge sub-agent) and order offers by fit×freshness instead of fit alone

## briefing 0.18.0

- cv-log-worker: unreadable comp thresholds abort the worker (no CV, no candidature) instead of skipping the gate — the documented fallback that came within one manual find of logging an application 33 % under target; the thresholds resolver now knows the Cowork synced/ layout; any @linkedin.com sender maps to linkedin-alert (renaud#125, #126)

## briefing 0.17.1

- morning-briefing: a second run of the day appends to the existing daily log instead of destroying it (Step 0.5 now reads today's too), and a closed `actuel` sprint no longer filters the task list — it shows every open task and names the transition_sprint that fixes the state (renaud#123, renaud#124)

## briefing 0.17.0

- cv-log-worker takes JOB_URL alone and reads its own JD; fan-out product cap removed (safety bound 8, announced when it bites); enrichment ceiling raised to match so no worker gets a snippet

## briefing 0.16.3

- morning-briefing Step 1g delegates the JD read to Skill(read-job-offer); no more silent skip on a fresh posting, no browser on LinkedIn

## briefing 0.16.2

- mail-triage, morning-briefing: the `Tags.` rule no longer promises a `hal://vocabulary` MCP resource — hal#135 decided it will never ship. The doctrine now lives in hal-mcp's server `instructions`; the skill carries a one-line enforceable pointer instead of the full paragraph (renaud#111)

## briefing 0.16.1

- morning-briefing, mail-triage: added the `Tags.` rule — `tags` is functional domain, picked only from the calling workspace's `allowed_tags` (via `whoami`), never invented, never used for what `company_id`/`role`/`channel`/`project_id` already carry (renaud#107)

## briefing 0.16.0

- the `/briefing` slash command is removed — `morning-briefing` is invoked directly as `/morning-briefing`. The command was a pass-through wrapper whose description had drifted (it still advertised "read-only, 3 sources" for a skill that reads 6 and writes one daily log per hal workspace). The `--headless` contract now reads `/morning-briefing --headless`; no step, source or rendering changed.

## briefing 0.15.1

- morning-briefing, mail-triage: `list_tasks` documented and handled as `{tasks, total, returned, truncated}`, not a bare array — matches hal#105/hal#107. Truncated reads now surface a loud line instead of silently under-counting a workspace's tasks (renaud#99)

## briefing 0.15.0

- gmail-mcp connector now declared here (moved from jobsearch, renaud#93) — briefing.mcp.json bundles gmail-mcp, tools resolve as mcp__plugin_briefing_gmail-mcp__*

## briefing 0.14.1

- plugin manifest description no longer advertises sprint-planner and sprint-review — both moved to `pm@bluegreen-marketplace` in 0.12.0. Metadata only: no skill, script or behaviour changed.

## briefing 0.14.0

`morning-briefing` — the daily log carries the day's selection, never task state.

- **Checkboxes removed from the daily log.** Sprint tasks render as a numbered list, one line
  per task. `halcrm_tasks` is the single source of truth for status; a `- [ ]` in the log was a
  second, editable copy that nothing reconciled — the log is written once at dawn and every
  later action diverged from it silently. Ticking goes through `update_task_status`.
- **hal task ids are never truncated.** Each entry carries the full 32-character id;
  `<workspace_slug>/<id>` is the join key the Command Center uses to resolve a line's live state
  and to tick it. The 2026-08-12 `renaud` log printed 8-character prefixes, unique across the
  current 311 rows by luck rather than by contract.
- **One line = one task.** Merging several tasks into a single entry carrying several `réf. hal`
  refs is forbidden — that line cannot be resolved, ticked or counted. The same log had one
  entry covering five tasks.
- **Step 1a guards the current sprint** instead of taking the first `actuel` entry returned.
  Zero `actuel`, several `actuel`, or one whose `ends_at` has passed each render a loud line in
  the workspace block and in the source-status footer. On 2026-08-13 `renaud #7` had been
  `actuel` for six days past its close, and the briefing presented its leftovers as the week's
  plan.

`status="actuel"` is declarative — a human sets it when planning the week and hal enforces
nothing about its dates. `hal#99` (sprint integrity) does not close this gap: a sprint left
`actuel` past its `ends_at` is still the sole `actuel` of its workspace, hence conformant. The
guard therefore belongs on the consumer side.

## briefing 0.13.0

- new skill `book-appointment`: create a Google Calendar event on the calendar resolved from a hal workspace (`calendar_id` shared → `member_calendar_id` own → stop if neither declared), never from a literal or a task tag. Always proposes title/date/time/duration/calendar and waits for explicit confirmation before writing. Dedup via `list_events` on the target calendar (`search_events` only covers the primary calendar, so it can't be used here). Create-only — no update/delete in this version. Interactive-only — refuses to run in `--headless`/scheduled mode, unlike `morning-briefing`'s read-mostly headless contract (#78)

## briefing 0.12.0

- drop sprint-planner and sprint-review — they move to pm@bluegreen-marketplace

## briefing 0.11.0

- multi-user: morning-briefing, mail-triage, sprint-planner and sprint-review now iterate over every workspace `whoami` returns instead of hardcoding workspace slugs; calendars are the union of the `calendar_id` / `member_calendar_id` each workspace declares; task labels use the workspace name; mailbox references are server-decided (Gmail perso/pro labels, no addresses). sprint-planner and sprint-review probe hal before loading any context document (fixes the hardcoded-slug `get_document` that ran before the probe). No workspace slug, calendar ID or mailbox address remains as a literal (#77, #76 partial)
- sprint-planner, sprint-review: a missing `sprints_enabled` field now stops before any write and asks which workspaces to process, instead of falling back to processing them all. Both skills write (sprints, tasks, statuses, reviews), so missing information must close the write perimeter, never widen it
- sprint-review: one sprint review per closed workspace, saved **in that workspace** with `domain="memory"` — replaces the single review routed to whichever workspace carried the `jobsearch` tag, with a fallback to the default workspace. A sprint belongs to a workspace, so its review does too; no destination is chosen, and jobsearch metrics only appear in the workspace where the job search lives

## briefing 0.10.2

- morning-briefing: daily-log / task-cleanup sessions are log-only — never propose executing a task inline; idea capture (e.g. LinkedIn post angles) routes into a dedicated hal task's description, referenced by id in the daily log instead of duplicated narrative (closes #72)

## briefing 0.10.1

- morning-briefing daily log embeds Gmail/LinkedIn/vault/Meet/hal links + next-actions per task entry (closes #70)

## briefing 0.10.0

- drop duplicate hal-mcp declaration; address hal-mcp tools as mcp__plugin_hal_hal-mcp__*

## briefing 0.9.2

- fix(cv-log-worker): comp gate — reject offers with an explicit salary below the 80k€ floor (closes #44)

## briefing 0.9.1

- sprint-review: compute week day names programmatically (Python) to prevent wrong day labels (e.g. "Ven 11/07" when 11/07 is Saturday)

## briefing 0.9.0

- explicit --headless mode

## briefing 0.8.0

- Daily morning briefing (`morning-briefing`), on-demand mail triage
  (`mail-triage`), weekly sprint review (`sprint-review`) and sprint planner
  (`sprint-planner`).

## briefing 0.7.1

- cv-log-worker logs with status `📝 À postuler` (an existing Kanban column) instead of `📋 CV préparé — à envoyer`, and passes the CV path and profile to log-application (#30)

## briefing 0.7.0

- morning-briefing Step 1h fans 🔥 offers out to the new `cv-log-worker` sub-agent (at most 3 in parallel), each generating a CV and logging the application (#25)

## briefing 0.6.0

- morning-briefing reads both Gmail inboxes, scores job offers from LinkedIn digests (JD fetched through BrightData), and renders six blocks plus an ordered plan du jour (#18)

## briefing 0.5.0

- morning-briefing writes one daily log per hal workspace (`save_document`, `domain="memory"`, `kind="daily-log"`) and reads yesterday's first (Step 0.5) — the skill is no longer read-only

## briefing 0.4.4

- sprint-planner closes every `actuel` sprint of a workspace before creating a new one — hal does not prevent two `actuel` sprints (#17)

## briefing 0.4.3

- sprint-planner, sprint-review: `update_sprint` allowed, so a sprint created with the wrong status can be corrected after creation

## briefing 0.4.2

- sprint-planner: the sprint it creates is `actuel` when run on the Monday the sprint starts, `suivant` otherwise; the idempotency check filters on the same status

## briefing 0.4.1

### Changed (sprint-planner capacity calibration)
- Job search blocs Mar–Ven : 08h30–10h30 → **09h30–11h30** (dépose Lalie à l'école 8h50)
- Post LinkedIn : 30min → **2h** (rédaction + illustration + publication — toujours plus long que prévu)
- Buffer : 30% → **40%** (marge pour les imprévus de la semaine)
- Capacity formula updated : `(22 - X) × 0.6` dispo sprint (was `(23.5 - X) × 0.7`)

## briefing 0.4.0

### Added (sprint-review + sprint-planner skills)
- `sprint-review` skill: full weekly sprint bilan — hal task completion rate across `blue-green` and `renaud` workspaces, jobsearch metrics (candidatures/week, conversion by profile, refus patterns, relances due next week), Blue Green active projects, prioritised shortlist for next sprint. Clôtures sprint in hal only after explicit user validation. Includes scheduled-mode support (fully autonomous steps 0–4, gate on step 5).
- `sprint-planner` skill: next-sprint builder — report/abandon decisions for unfinished tasks, jobsearch vault metrics + vault relances, LinkedIn job alert scan via gmail-mcp (Gmail perso), 3-calendar conflict detection with automatic bloc adjustment in schedule mode, capacity calculation (35h brute, 10h job-search blocs, IC meeting, 30% buffer), 4-tier MUST/SHOULD/COULD/BACKLOG plan, hal sprint creation with sprint_number auto-increment and idempotency check. Creates sprint + assigns tasks only after explicit user validation.
- `/sprint-review` and `/sprint-planner` slash commands.

### Notes
- Both skills are scheduled-mode-friendly (run autonomously on Friday afternoon, present output, gate writes on explicit validation).
- `sprint-planner` Step 3 (LinkedIn scan) requires the `jobsearch` plugin to be co-installed (uses `mcp__claude_ai_gmail-mcp__search_emails`). Degrades gracefully with `gmail:DOWN` if unavailable.
- `sprint_number` for `create_sprint` is auto-computed: `list_sprints(status="actuel").sprint_number + 1`, with idempotency check via `list_sprints(status="suivant")`.

## briefing 0.3.0

### Added (WP-D — tag-aware renaud section)
- `morning-briefing` Step 1b now groups `renaud` workspace hal tasks by their first tag (drawn from hal-mcp v39's `tags` field, vocabulary `jobsearch` / `rosaslaborbe` / `personal` / `finance` / `hr` / `laborbe` / `other`). Tasks with empty/missing `tags` land under `other`. Fixed group order: `jobsearch` first (job + revenue priority), then `rosaslaborbe` → `personal` → `finance` → `hr` → `laborbe` → `other`.
- Step 3 render template: `## 🏠 Sprint en cours — Renaud [perso]` is now split into per-tag `### 🎯 jobsearch` / `### 🏡 rosaslaborbe` / … subsections (empty groups skipped). The `[perso]` workspace label still applies to every task regardless of tag.

### Notes
- `blue-green` workspace rendering is unchanged — tags only affect `renaud`.
- Hermetic: no MCP schema change, no new tools in `allowed-tools` (existing `mcp__hal-mcp__list_tasks` already returns the `tags` field).

## briefing 0.2.0

### Changed
- `morning-briefing` re-pointed from the global `obsidian-crm` skill to the new `jobsearch-vault` skill (Option A — invoke via the `Skill` tool). Step 0 probe + Step 1c now address `jobsearch-vault`; `allowed-tools` swapped `Skill(obsidian-crm)` → `Skill(jobsearch-vault)` (hal-mcp + Google Calendar tools unchanged). READ-ONLY.
- AC3 loud-failure contract preserved: a `jobsearch-vault` failure renders `⚠️ Jobsearch DOWN — <reason>` in the jobsearch section and flips the `jobsearch-vault:` source-status footer line — never a silent empty.

## briefing 0.1.0

### Added
- Initial plugin structure: `.claude-plugin/plugin.json`, `.mcp.json`, `skills/morning-briefing/SKILL.md`, `commands/briefing.md`, `CHANGELOG.md`
- `hal-mcp` http MCP server declaration (deduped at name+endpoint level with `bluegreen-marketplace/plugins/hal`)
- `morning-briefing` skill: composes hal tasks (both workspaces, current sprint + fallback to open tasks), Obsidian jobsearch via the global `obsidian-crm` skill, and 3 Google Calendars via the claude.ai Google Calendar MCP connector — read-only, with loud per-source failure notices
- `/briefing` slash command (self-contained trigger)

## jobsearch 0.21.0

- cover-letter skill and command retired (hal audit q15); apply-to-offer drafts the short form-field answer on request, facts read from hal parcours — jobsearch no longer calls gmail-mcp

## jobsearch 0.20.0

- self-resolver adds a device_bash case for cloud sessions linked to the Mac, reading a version-checked _tools/ mirror refreshed by scripts/sync_vault_tools.sh

## jobsearch 0.19.0

- interview-prep and log-cr list each prep and CR in the opportunite's ## Entretiens section; one-shot backfill_entretien_links.py rebuilds it for older notes (renaud#119)

## jobsearch 0.18.0

- log-application/interview-prep/log-cr resolve the hal workspace via whoami+allowed_tags instead of hardcoding workspace_slug="renaud" (#103)

## jobsearch 0.17.0

- log-cr aggregates BANT onto the opportunite (jobsearch-vault upsert_section.py) instead of duplicating it per CR

## jobsearch 0.16.2

- Add role-criteria.json — single definition site for qualitative offer disqualifiers

## jobsearch 0.16.1

- fix: attach Artelia P&L to a business unit, not the renewables BU (#135)

## jobsearch 0.16.0

- log-cr: le CR se remplit depuis le transcript Granola (Step 1bis) — heure, interlocuteurs, BANT, questions, next steps ; feeling et Lecture Renaud restent demandés ; fallback déclaratif si pas de transcript ; granola_id en frontmatter ; docs/bant-cr-template.md resynchronisé (feeling 🔥/🟡/❌, 5 sections)

## jobsearch 0.15.1

- fix(jobsearch-vault): add missing statut enum values (Sans suite, Abandonné), drop dead alias

## jobsearch 0.15.0

- cv-generator: a missing contact.local.json now fails closed (exit 1, no PDF) with --allow-placeholder as the explicit demo escape hatch; .cv_temp moved to tempfile.mkdtemp() so generation into a mounted Drive stops raising PermissionError; new --container-items to override competency bullets without copying cv-master.json; DYLD_LIBRARY_PATH documented as macOS-only. interview-prep: new Step 4c writes prochain_rdv and « 📞 Entretien prévu » back onto the candidature under non-regression guards, and Step 2 now cross-checks profile career facts against the vault record — P4 no longer claims 15 yrs client-side. log-application: any @linkedin.com sender maps to linkedin-alert. All resolvers know the Cowork synced/ layout (renaud#125, #98, #106, #126, #121, #128)

## jobsearch 0.14.0

- cv-generator: p4×t5 rewritten against the parcours record (SAT-OCEAN, Open Ocean CTO, no borrowed sales cycles); competencies lead with Python/TypeScript/SQL; contact links clickable in the PDF plus a GitHub row

## jobsearch 0.13.0

- new skill apply-to-offer (pasted-URL path to a CV); comp thresholds get a single definition site in data/comp-thresholds.json; log-application accepts source=manual

## jobsearch 0.12.0

- new skill read-job-offer — LinkedIn JD read primitive (cached dataset, then the jobs-guest endpoint), shared by morning-briefing and the pasted-URL path

## jobsearch 0.11.6

- log-application, log-cr, interview-prep: the `Tags.` rule no longer promises a `hal://vocabulary` MCP resource — hal#135 decided it will never ship. The doctrine now lives in hal-mcp's server `instructions`; the skill carries a one-line enforceable pointer instead of the full paragraph (renaud#111)

## jobsearch 0.11.5

- log-application, log-cr, interview-prep: added the `Tags.` rule — `tags` is functional domain, picked only from the calling workspace's `allowed_tags` (via `whoami`), never invented, never used for what `company_id`/`role`/`channel`/`project_id` already carry (renaud#107)

## jobsearch 0.11.4

- log-application, log-cr, interview-prep and the `log-application` command now name `/morning-briefing` instead of the removed `/briefing` command (see briefing 0.16.0)

## jobsearch 0.11.3

- log-application, log-cr, interview-prep: `list_tasks` documented and handled as `{tasks, total, returned, truncated}`, not a bare array — matches hal#105/hal#107. A truncated idempotency pre-check now reports itself as partial instead of silently trusting an incomplete read (renaud#99)

## jobsearch 0.11.2

- cv-generator fails loud on a missing `contact.local.json`: `--require-contact`, always passed on the real-application path, exits non-zero before rendering; the unflagged fallback now warns (#92)

## jobsearch 0.11.1

- gmail-mcp connector no longer declared here — moved to briefing (renaud#93); cover-letter's draft_email call now resolves as mcp__plugin_briefing_gmail-mcp__draft_email

## jobsearch 0.11.0

- Personal data moved out of the plugin package and into the mounted Drive folder
  `SynologyDrive-MyAssistant/jobsearch/private/` — `contact.local.json` plus `profiles/p1..p5`.
  Both are untracked (this repository is public) and the plugin cache is version-numbered, so
  every `plugin update` silently wiped them. The failure mode was not an error: a CV rendered
  with placeholder contact details, and `interview-prep` produced an unpositioned pitch because
  its profile files had never reached the installed package at all. The mounted folder is
  readable from the workstation and from the Cowork sandbox, and survives updates
- `generate_cv.py`: `find_private_dir()` added; `load_contact_info()` now resolves
  `--data-dir` → mounted folder → plugin `data/`, and reports every path it searched when it
  falls back to placeholders
- `interview-prep`: PLUGIN_DIR resolver gained a mounted-folder tier ahead of the plugin tiers
- `cv-generator`: fixed a PLUGIN_DIR resolver that still probed the pre-rename `cv-generator`
  paths in both the marketplace cache and the dev checkout — every local tier missed, so the
  skill exited `PLUGIN_DIR_NOT_FOUND` on the workstation unless `CV_GENERATOR_DIR` was set

## jobsearch 0.10.0

- `log-cr`: reintroduce the `🪞 Lecture Renaud — Fit` body section (subjective read, distinct from the employer's BANT read) — was lost when the SynologyDrive `CLAUDE.md` was retired in favour of skill-owned content (#82)
- `log-cr`: rephrase the BANT body section as directive questions instead of blank fields, and rename it `🏢 Lecture employeur — BANT` (#82)
- `log-cr`: collect and write `format`/`heure` frontmatter fields (non-schematized, same warning contract as `prep`) (#82)
- `log-cr`: write `prochain_rdv` on the opportunité when the interview produces a confirmed next-step date (#82)
- `log-cr`: arbitrate the `feeling` enum to `🔥`/`🟡`/`❌` (intensity read, was `😊`/`😐`/`😟`); `type_entretien` stays `RH`/`Technique`/`Manager`/`Final` to match `interview-prep` (#82)
- `log-cr`: add `docs/bant-cr-template.md` as the canonical body template and single source of truth for these enums — was referenced but missing (#82)

## jobsearch 0.9.2

- cv-generator: drop personal email/phone/home-address (incl. a Google Maps street link) from the public repo — `cv-master.json` no longer carries them and `cv_template.html` renders them from a gitignored `data/contact.local.json` (schema in `data/contact.example.json`), with a placeholder fallback when that file is absent (#76)

## jobsearch 0.9.1

- gmail-mcp: allowlist Supabase user_id for JWT auth mode — closes security gap where any provisioned project user could read/draft from the mailbox (#80)

## jobsearch 0.9.0

- address hal-mcp and gmail-mcp tools by their plugin-bundled names

## jobsearch 0.8.4

- Fix P4 narrative in `cv-generator`: replace false "was the customer" framing with accurate founder/builder-on-vendor-side framing (15 years energy/offshore/engineering delivering to industrial clients).

## jobsearch 0.8.3

- CV generation (`cv-generator`), cover letters (`cover-letter`), application
  logging (`log-application`), interview prep (`interview-prep`), CR logging
  (`log-cr`), and job-search vault I/O (`jobsearch-vault`).

## jobsearch 0.8.2

### Changed (cv-generator SKILL.md)

- **Profile narrative files wired in** : Step 1 now points to `profiles/{profile}.md`
  (gitignored, personal — e.g. `profiles/p1_architecte.md`) when present, for real
  target-company examples per cell and finer-grained narrative rules than the
  in-file "Signal per profile" summary. Falls back silently if the file is absent.
  Covers P1-P5 only — no P6 profile exists yet.

## jobsearch 0.8.1

### Changed (cv-generator SKILL.md v0.5.3 → v0.8.1 / generate_cv.py)

- **Corporate-first order — reintroduced (refined scope)** : `CORPORATE_FIRST_CELLS` re-added
  with a narrower set of 3 cells: `(p1,t4)`, `(p2,t4)`, `(p5,t5)`. These cells output
  Artelia → Blue Green → Open Ocean to lead with corporate proof over solopreneur perception.
  All other cells remain chronological reverse (Blue Green → Artelia → Open Ocean).
- **SKILL.md** : frontmatter version aligned to 0.8.1 (sync with plugin.json).

## jobsearch 0.8.0

- new skill `log-cr`: BANT interview report note, moves the candidature to `🔄 Relance à faire`, closes the prep hal task and creates the post-interview relance; canonical template in `docs/bant-cr-template.md` (#38)

## jobsearch 0.7.0

- cover-letter Step 6 (optional): a Gmail draft with the CV attached, through gmail-mcp `draft_email`'s new `attachments` parameter, 25 MB cap (#33)

## jobsearch 0.6.2

- log-application accepts `📝 À postuler` (replaces `📋 CV préparé — à envoyer`) and writes a `## CV généré` section with the PDF path and profile when `cv_path` is given (#30)

## jobsearch 0.6.1

- log-application creates the relance task in hal's `renaud` workspace instead of the vault's `Taches/`; the candidature note stays in the vault (#27)

## jobsearch 0.6.0

- log-application: `source` becomes a taxonomy (`linkedin-alert`, `linkedin-inmail`, `wttj`, `freelance`, `direct-ats`, `headhunter`, `referral`, `other`) plus free-text `source_detail`, and accepts a `statut` so the `cv-log-worker` sub-agent can log a prepared, unsent CV (#25)

## jobsearch 0.5.2

- cv-generator auto-fit retries at three progressively compact CSS levels instead of one, so the P4×T5 EN default fits one page; uv cold start documented (#15)

## jobsearch 0.5.1

- cv-generator P4×T5 about leads with the technical work (HAL, BlueWind Companion) and drops the false "15 years client side" buyer claim; killer-CV overrides and EN readability rules (#14)

## jobsearch 0.5.0

- cv-generator P4×T5 (Solutions Engineer × AI SaaS vendor) rewritten: title, about, competency containers, and bullets for all three companies

## jobsearch 0.4.9

- cv-generator P4 narrative corrected against the record: Artelia IT-division insider, Open Ocean co-founder/CTO (not sales), BlueWind Companion described with its real figures (#12)

## jobsearch 0.4.8

### Changed (cv-generator SKILL.md v0.2.6 → v0.2.7 / generate_cv.py / cv-master.json)

- **Experience order — fixed, no exceptions** : removed `CORPORATE_FIRST_CELLS` logic (Artelia-first for T4/T5). All cells now output Blue Green → Artelia → Open Ocean (chronological reverse). Updated SKILL.md accordingly.
- **About FR — forme nominale** : all 15 `about.fr` sections rewritten to nominal form. No more bare infinitives (`"Livrer…"`, `"Maîtriser…"`, `"Apporter…"`). Added mandatory FR style rule in SKILL.md.
- **SKILL.md** : added "About section — FR style rule" block; replaced "Experience order rules" table with single fixed-order rule.
- **cv-master.json bullets** :
  - `open_ocean.p1.default.en[2]` : "Business Angels and VCs" → "institutional investors (Seventure Partners, Cap Décisif/FNA)"
  - `blue_green.p1.default.en[2]` : generic stack line → Edifice/IC Ingénieurs Conseils (€25M + €35M projects)
  - `artelia.p1.default` (en + fr) : replaced 3 vague bullets with specific P&L/portfolio/roadmap bullets (SBM Offshore, Nexans, ASN, Cadeler)

## jobsearch 0.4.7

### Fixed (cv-master.json / cv-generator v0.2.6)

- CPTEC title FR : "Analyste Données Climatiques" → "Analyste Climatique — Événements Extrêmes"
- CPTEC title EN : "Climate Data Analyst" → "Climate Data Analyst — Extreme Events"
- Open Ocean P1 title : added "Marine Data Intelligence" branding
- Artelia bullets : stripped P&L BU scope across all FR + EN bullets
- P1×T2 : trimmed about[0] + BG t2 bullet[0] for 1-page fit

## jobsearch 0.4.6

### Fixed (cv-master.json / cv-generator SKILL.md v0.2.5)

- FR quality pass — 14 corrections across P1–P5 : openers "Cumuler"/"Fort de" → nominal forms, infinitif passé P2×T1, "Manager" → "Diriger", "ventures" → "startups", bullet vague BG P1 → Edifice/IC Ingénieurs, "delivery agile" → "livraison agile", P5 20 ans → 15 ans (factuel), Artelia period 2019–2022 → 2019–2023 (factuel), CPTEC "Analyste Données" → "Analyste Climatique — Événements Extrêmes"
- P1×T2 about rewrite + BG t2 bullets override

## jobsearch 0.4.5

### Changed (cv-generator SKILL.md v0.2.3 → v0.2.4 / generate_cv.py)

- **`--company` + `--job-title`** — output filename auto-built: `CV_Renaud_Laborbe_{job_slug}_{company_slug}_{LANG}.pdf`. Falls back to `P{n}_T{n}_{LANG}` if omitted.
- **`--data-dir`** — load `cv-master.json` from a custom path (workaround for read-only plugin dir in Cowork).
- **`--container-titles`** — JSON array of 3 strings, overrides competency block titles for this generation only. Cell defaults apply when omitted. Agent can propose better titles if the offer signals a stronger angle.
- **`--bullet-overrides`** — JSON dict `{"company.profile.lang.index": "new bullet"}`, injects personalised bullets without touching cv-master.json. Wired into Step 3b of SKILL.md.
- **Auto 1-page check** — if `pikepdf` is available (`--with pikepdf`), script checks page count post-render and retries with compact CSS layout if overflow. Warns explicitly if still >1 page after compact.
- **P4×T5 FR container title defaults** updated: "Ingénierie IA terrain" → "Architecture & agents IA", "Succès & adoption client" → "Cycle client & déploiement".
- **SKILL.md Step 3b** updated to document `--bullet-overrides` key format + example.
- **SKILL.md Step 4** updated with all new flags, output filename format, and compact-layout note.

### Validated

All 30 CVs — 1 page each.

## jobsearch 0.4.4

### Changed (cv-generator SKILL.md v0.2.2 → v0.2.3)

- **FR verb convention — infinitif exclusivement** — All FR bullets and `about.fr` across P1–P5 × BG/Artelia/OO rewritten to start with an infinitive verb ("Déployer", "Piloter", "Construire"). Removes all past participles ("Déployé", "Construit") and conjugated present forms ("Conçoit", "Pilote"). Research-backed: CV Creator, JobImpact, TopCV, Zety all confirm infinitive as the only correct form for French CVs.
- **Cell labels** — Added `label.fr` + `label.en` to all 15 matrix cells in `cv-master.json`. SKILL.md Step 5 now outputs the cell label (e.g. "Solutions Engineer — éditeur SaaS IA") instead of the P/T code.
- **Step 3b — LLM personalization** — New step in SKILL.md between cell selection and PDF generation: the LLM reads the job offer, identifies 2–3 key signals, rewrites 1–2 bullets per company to mirror those signals — factual anchors always intact. Max 2 bullets changed per company.
- **Editorial rules updated** — Removed "past participle for past roles" and "present tense for current role" rules. Replaced with "infinitive for all roles, current and past".
- **Open Ocean P1 default FR** — Also fixed residual "Business Angels" → "Seventure Partners, Cap Décisif/FNA" and "DCNS" → "Naval Group (ex-DCNS)" in the default (P1×T1/T2) cell.

### Validated

All 30 CVs — 1 page each.

## jobsearch 0.4.3

### Added

- **`cover-letter` skill** (`skills/cover-letter/SKILL.md` v0.1.0) — LLM-native cover letter generator using the same 15-cell profile × company-type matrix as the CV generator. Produces 3-paragraph letters (~300 words EN / ~330 FR) anchored in real verifiable facts. No HR boilerplate — opens with a hook, closes with confidence. Applies the same cell-specific narrative rules (T3: delivery advisory, T4: P&L/governance, T5: velocity + solopreneur counter). Registered in `marketplace.json`.
- **`/cover-letter` command** (`commands/cover-letter.md`) — slash command routing to the cover letter skill.

### Changed

- **`cv-generator` SKILL.md v0.2.1 → v0.2.2** — Added "Narrative methodology" section documenting: experience order rules per cell (CORPORATE_FIRST for T4, default BG-first otherwise), the signal to emphasise per company type (T3/T4/T5/T1/T2), the signal per profile (P1–P5), complete factual anchors table (real metrics, verified client names), and banned phrases list ("urban planning automation", "DCNS", "Business Angels", "delivery" in FR, "en solo à vélocité maximale").

### Fixed (cv-master.json — P2/P3/P4/P5 defaults)

- Added cell-specific bullets (T3/T4/T5) for P2 (Lead/Manager) across all 3 companies
- Added cell-specific bullets (T1/T5) for P3 (CTO) across all 3 companies
- Artelia P3 default: removed factually wrong "Led investor presentations" bullet (that was Open Ocean, not Artelia)
- "DCNS" → "Naval Group (ex-DCNS)" everywhere (P2/P3/P4/P5, EN+FR)
- "Business Angels" → "institutional investors (Seventure Partners, Cap Décisif/FNA)"
- P4 Blue Green FR: "automatisation urbanisme" (banned) → "analyse PLU pour l'éolien terrestre"
- Blue Green P2 FR: "delivery" → "livraison"
- Blue Green P3 FR/EN: removed "en solo à vélocité maximale" / "solo at maximum velocity"
- P5 Blue Green: trim over-limit bullets (141→116 EN, 147→111 + 121→119 + 142→113 FR)

All 30 CVs validated — 1 page each.

## jobsearch 0.4.2

### Added (WP-D — hal mirror tagged `jobsearch`)
- `log-application` Step 4b: after the canonical Obsidian `tache` write, also create a hal task in the `renaud` workspace with `tags=["jobsearch"]` and `due_date = date_candidature + 7d`. Mirrors the relance into hal so it surfaces under `/briefing`'s tag-grouped `🎯 jobsearch` subsection of the Renaud section (WP-D — see `briefing` 0.3.0). Sprint-less by design. Idempotent on re-apply (skips if a non-closed hal task with the exact title already exists). Partial-failure mode: Obsidian-OK + hal-fail is degraded-but-safe — reported explicitly, Step 5 still fires.
- `interview-prep` Step 4b: after the canonical `entretien` prep note write, also create a hal task in the `renaud` workspace titled `Entretien <type> — <Entreprise> — <DD-MM-YYYY>` with `tags=["jobsearch"]` and `due_date = interview_date`. Same idempotency + degraded-but-safe failure semantics as `log-application`. The Obsidian prep note stays the canonical document; the hal task is a thin pointer.
- `allowed-tools` for both skills now includes `mcp__hal-mcp__create_task` alongside `Skill(jobsearch-vault)` (`interview-prep` also keeps `Read`).
- Both skills' Step 5 success report now mentions the hal mirror.

### Notes
- Frontmatter version of `log-application` and `interview-prep` jumps 0.4.0 → 0.4.2 to re-sync with the plugin `plugin.json` (which advanced to 0.4.1 in the cv-generator FR pass without touching these two skills).
- `cv-generator` SKILL.md unchanged at 0.2.1 — its frontmatter version is independent of the plugin-level bump (only the 3 skills that change behaviour need to track the plugin version per the 4-field sync rule).
- No CV/PDF, no schema, no `jobsearch-vault` change.

## jobsearch 0.4.1

### Fixed (cv-generator — FR quality pass on the P4 Customer Success / Solutions Engineer CV)
- **Open Ocean FR job titles** (p2/p4/p5): "Co-Fondateur & Directeur Général" → "Directeur Technique & Co-Fondateur" — leads with the technical/functional role, founder status second.
- **Blue Green FR title** (p2): "AI Lead" → "Responsable Solutions IA — Consultant" (was an untranslated English label).
- **Container titles** — removed residual English from the FR side across cells: P4×T5 (`Ingénierie IA terrain`, `Succès & adoption client`, `Secteurs d'expertise`), plus p2×t1, p2×t3, p2×t4, p2×t5, p3×t1, p3×t5 (`Leadership`/`Scale-up`/`hands-on` calques reworded).
- **P4×T5 competency items** rewritten as transferable skills, not tasks: `Conduite du changement & formation IA`, `Gestion multi-niveaux (C-level → ops)`, `Vente de solution complexe B2B`.
- **P4×T5 `about` + title** de-anglicised: title → "Solutions Engineer IA — Déploiement GenAI en environnement industriel"; the three FR sentences reworded from English calques into natural French.
- **P4 experience bullets** cleaned of franglais (`discovery`/`delivery`/`workflows`/`cross-fonctionnelle`/`data marines` → French), keeping the +15% YoY retention/expansion proof.
- **`generate_cv.py`**: FR periods now render "Aujourd'hui" instead of "Present".
- cv-generator skill bumped 0.2.0 → 0.2.1.

## jobsearch 0.4.0

### Added
- `jobsearch-vault` skill — self-contained, **filesystem-only** (no network, no API key) read/write access to the Job-Search slice of the Obsidian vault. Owns 5 note types (`opportunite-js`, `entreprise-js`, `contact-js`, `entretien`, jobsearch `tache`) via plain-stdlib CLI scripts (`create_note.py`, `read_note.py`, `update_frontmatter.py`, `search_vault.py`, `list_notes.py`). Ported from the global `obsidian-crm` skill with the REST/Local-REST-API backend stripped out. Doubles as an invocable skill (triggers: "pipeline candidatures", "liste mes entretiens", "cherche dans mes candidatures", "mes relances jobsearch") and as the shared library the other jobsearch skills compose.
- Bundled `note_schemas.py` ships the `entretien` `categorie`/`interlocuteurs` fix natively — creating a fully-specified interview note now raises **zero** validation warnings.
- `jobsearch-vault` registered in `marketplace.json` `plugins.jobsearch.skills`.

### Changed
- **`log-application` + `interview-prep` re-pointed to `jobsearch-vault`** (Option A — invoke via the `Skill` tool, no script paths, no PLUGIN_DIR resolver for vault I/O). `allowed-tools` swapped `Skill(obsidian-crm)` → `Skill(jobsearch-vault)`. Same structured create/update/search payloads, same idempotency, same exit-code contract — only the addressee changed. `interview-prep` keeps `Read` for `profiles/`.
- `interview-prep`: removed the "expected non-blocking `categorie`/`interlocuteurs` warnings" paragraph — the bundled schema accepts both fields, so a clean `entretien` create has zero warnings.
- The global `obsidian-crm` skill is left byte-for-byte unchanged (legacy/fallback for non-jobsearch domains).

## jobsearch 0.3.0

### Added
- `log-application` skill — classifies a pasted offer against the existing P1–P5 profile taxonomy, then composes the global `obsidian-crm` skill to create one `opportunite-js` candidature note (with `source`, `target_profile`, `lien_offre`, `date_relance: today+7d`, body = pasted offer) and one `tache` relance (`etiquettes: ["jobsearch"]`, `echeance: today+7d`) that the Loop 3 `morning-briefing` surfaces.
- `interview-prep` skill — given a candidature, composes `obsidian-crm` to read the candidature note + the matching `profiles/p{1-5}_*.md`, then creates one `entretien` note (`categorie: Préparation`) with the always-identical 5-section body: Société · Résumé JD · Pitch (positioned for the candidature's `target_profile`) · Cas du parcours · Questions probables.
- `/log-application` and `/interview-prep` slash commands.
- Both new skills registered in `marketplace.json` `plugins.jobsearch.skills`.

### Fixed (live smoke-test findings against the real Obsidian vault)
- `log-application`: the relance surfaces in `/briefing` **on its due date** (`date_relance`, today+7d), not "tomorrow" — corrected the misleading frontmatter description + Step 4 prose.
- `log-application`: `lien_offre` is now **omitted** when no URL is provided (passing `""` triggered a spurious `does not look like a URL` warning on every link-less application).
- `log-application`: Step 4 idempotency now matches the real `tache` enum — open states `Pas commencée`/`Today`/`En cours`, closed `Terminé`/`Archivé` (was the non-existent `Terminée`/`Annulée`).
- `interview-prep`: documented the expected non-blocking `unknown field "categorie"`/`"interlocuteurs"` warnings (the fields are documented in `obsidian-crm/references/schemas.md` but lag its runtime validator) — mirrors the `target_profile` escape hatch, so the skill no longer reads as failing.

### Changed
- Renamed CHANGELOG title `cv-generator — Changelog` → `jobsearch — Changelog` (the plugin now hosts three skills, not just cv-generator).

## jobsearch 0.2.0

- Plugin renamed `cv-generator` → `jobsearch`; declares the `gmail-mcp` connector

## jobsearch 0.1.2 — shipped as `cv-generator`

### Fixed
- Language mixing in FR CVs: all competency items in `fr` containers were left in English — now fully translated
- Section labels hardcoded in English (`About`, `Key Competencies`, `Work Experience`, `Earlier Career`, `Education`) — now lang-aware via template placeholders
- `Earlier Career` section had no FR support in data or generator — added `title_fr`/`description_fr` fields and lang-aware rendering

### Changed
- Blue Green P1 FR bullet: removed ultra-technical details (chunk counts, framework names) for broader audience
- P3×T5 and P4×T5 FR about sections: softened technical jargon

### Added (SKILL.md)
- Step 0: spontaneous application detection — when no job offer is present, the skill now asks Renaud for target profile and company type interactively instead of silently defaulting

## jobsearch 0.1.1 — shipped as `cv-generator`

### Fixed
- Cowork compatibility: output dir, cleanup, photo fallback
- Photo bundled in plugin assets

## jobsearch 0.1.0 — shipped as `cv-generator`

### Added
- Initial plugin structure (migrated from `~/Projects/MyClaudeSkills/cv-generator/`)
- 5-profile × 5-company-type matrix (15 cells, FR + EN) — see task brief
- New `--profile / --company-type / --lang` CLI API
- Rétro-compat: `--positioning ai_consulting/cto/business_dev` still works
- Plugin directory resolver in SKILL.md (env var → cache → Cowork → dev path)
- Cowork-compliant: WeasyPrint loaded via `uv run --with`, no pre-install

## improve 0.4.0

- Route observations to archon-workflows (doctrine/maps) and verify labels per target repo

## improve 0.3.2

- regenerated the skill→plugin→repo map: apply-to-offer

## improve 0.3.1

- regenerated the skill→plugin→repo map: read-job-offer

## improve 0.3.0

- `generate_improve_map.py`: add `EXTRA_TARGETS` for `/improve` destinations that carry no skill directory in either marketplace — `hal` now routes to `BluegReeno/hal` (its connector-only bluegreen-marketplace entry enumerates no skill rows by design) instead of falling back to the nearest marketplace wrapper (closes #83)
- Step 1's skill options list is now rendered from the same table rows as Step 2's routing table, between `<!-- improve-options:start/end -->` markers — it can no longer drift from the table, and three phantom entries (`blue-green-proposal-generator`, `document-generator`, plus the missing `mail-triage`/`log-cr`/`mycoach`/`crm`/`linkedin`/`pm`) are gone
- Step 3's issue body and Archon checklist omit the `Fichier`/`plugin.json`/`CHANGELOG.md` steps when the target has no marketplace `SKILL.md` (table's `Plugin` column is `—`)

## improve 0.2.0

- generated skill→repo map

## improve 0.1.3

- Update the "Pour fixer (Archon)" checklist to the 2-field version invariant
  (plugin.json / marketplace.json) + CHANGELOG entry + `check_version_sync.sh`,
  replacing the retired 3-field rule that referenced `SKILL.md` frontmatter.

## improve 0.1.2

- Skill improvement capture (`improve`) — turn an observation into a GitHub
  issue in ≤30s from Cowork.

## improve 0.1.1

- First release: one generic `improve` skill turns an observation into a GitHub issue, plus the `skill-improve` Archon workflow (#8)

## mycoach 0.4.4

- the `Tags.` rule no longer promises a `hal://vocabulary` MCP resource — hal#135 decided it will never ship. The doctrine now lives in hal-mcp's server `instructions`; the skill carries a one-line enforceable pointer instead of the full paragraph (renaud#111)

## mycoach 0.4.3

- fix: channel='mycoach-session' rejected by hal's controlled vocabulary (hal#124) — write 'note' instead

## mycoach 0.4.2

- added the `Tags.` rule — `tags` is functional domain, picked only from the calling workspace's `allowed_tags` (via `whoami`), never invented, never used for what `company_id`/`role`/`channel`/`project_id` already carry (renaud#107)

## mycoach 0.4.1

- `list_tasks` documented and handled as `{tasks, total, returned, truncated}`, not a bare array — matches hal#105/hal#107 (renaud#99)

## mycoach 0.4.0

- multi-user: add a `whoami` probe and resolve the session workspace by the `mycoach` tag in its `allowed_tags` (none → stop with the init message; several → ask which); never fall back to `default_workspace_slug`, so a personal session is never written to a business workspace. All hardcoded workspace slugs removed (#77)

## mycoach 0.3.0

- Rename the plugin and its skill `myspy` → `mycoach` (directories, frontmatter,
  triggers). The knowledge bundle moved to `mycoach-kwiki` and the skill now reads
  it from `/Users/renaud/Projects/mycoach-kwiki`. hal writes use the `mycoach` tag
  and the `mycoach-session` channel. No transition alias: the old trigger
  "séance MySpy" is gone. Entries below are the ones shipped as `myspy`
  (closes #73).

## mycoach 0.2.0 — shipped as `myspy`

- address hal-mcp tools as mcp__plugin_hal_hal-mcp__*

## mycoach 0.1.0 — shipped as `myspy`

- Personal weekly self-reflection check-in (`myspy`) — structured CBT/SFBT
  session backed by a private OKF knowledge base.
