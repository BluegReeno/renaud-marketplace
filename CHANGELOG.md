# Changelog

Each plugin tracks its own version. Entries are grouped per plugin, newest
version first. The current version of every plugin must appear here — CI
(`scripts/check_version_sync.sh`) fails if a plugin's `plugin.json` version has
no matching entry below.

Heading format (parsed by the sync check): `## <plugin> <version>`.

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
