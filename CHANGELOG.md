# Changelog

Each plugin tracks its own version. Entries are grouped per plugin, newest
version first. The current version of every plugin must appear here — CI
(`scripts/check_version_sync.sh`) fails if a plugin's `plugin.json` version has
no matching entry below.

Heading format (parsed by the sync check): `## <plugin> <version>`.

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

## improve 0.3.2

- regenerated the skill→plugin→repo map: apply-to-offer

## improve 0.3.1

- regenerated the skill→plugin→repo map: read-job-offer

## improve 0.3.0

- `generate_improve_map.py`: add `EXTRA_TARGETS` for `/improve` destinations that carry no skill directory in either marketplace — `hal` now routes to `BluegReeno/hal` (its connector-only bluegreen-marketplace entry enumerates no skill rows by design) instead of falling back to the nearest marketplace wrapper (closes #83)
- Step 1's skill options list is now rendered from the same table rows as Step 2's routing table, between `<!-- improve-options:start/end -->` markers — it can no longer drift from the table, and three phantom entries (`blue-green-proposal-generator`, `document-generator`, plus the missing `mail-triage`/`log-cr`/`mycoach`/`crm`/`linkedin`/`pm`) are gone
- Step 3's issue body and Archon checklist omit the `Fichier`/`plugin.json`/`CHANGELOG.md` steps when the target has no marketplace `SKILL.md` (table's `Plugin` column is `—`)

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

## improve 0.2.0

- generated skill→repo map

## improve 0.1.3

- Update the "Pour fixer (Archon)" checklist to the 2-field version invariant
  (plugin.json / marketplace.json) + CHANGELOG entry + `check_version_sync.sh`,
  replacing the retired 3-field rule that referenced `SKILL.md` frontmatter.

## improve 0.1.2

- Skill improvement capture (`improve`) — turn an observation into a GitHub
  issue in ≤30s from Cowork.

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
  "séance MySpy" is gone. Entries below keep their historical `myspy` heading
  (closes #73).

## myspy 0.2.0

- address hal-mcp tools as mcp__plugin_hal_hal-mcp__*

## myspy 0.1.0

- Personal weekly self-reflection check-in (`myspy`) — structured CBT/SFBT
  session backed by a private OKF knowledge base.
