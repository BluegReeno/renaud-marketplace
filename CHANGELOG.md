# Changelog

Each plugin tracks its own version. Entries are grouped per plugin, newest
version first. The current version of every plugin must appear here — CI
(`scripts/check_version_sync.sh`) fails if a plugin's `plugin.json` version has
no matching entry below.

Heading format (parsed by the sync check): `## <plugin> <version>`.

## jobsearch 0.9.0

- address hal-mcp and gmail-mcp tools by their plugin-bundled names

## jobsearch 0.8.4

- Fix P4 narrative in `cv-generator`: replace false "was the customer" framing with accurate founder/builder-on-vendor-side framing (15 years energy/offshore/engineering delivering to industrial clients).

## jobsearch 0.8.3

- CV generation (`cv-generator`), cover letters (`cover-letter`), application
  logging (`log-application`), interview prep (`interview-prep`), CR logging
  (`log-cr`), and job-search vault I/O (`jobsearch-vault`).

## briefing 0.11.0

- multi-user: morning-briefing, mail-triage, sprint-planner and sprint-review now iterate over every workspace `whoami` returns instead of hardcoding workspace slugs; calendars are the union of the `calendar_id` / `member_calendar_id` each workspace declares; task labels use the workspace name; mailbox references are server-decided (Gmail perso/pro labels, no addresses). sprint-planner and sprint-review probe hal before loading any context document (fixes the hardcoded-slug `get_document` that ran before the probe). No workspace slug, calendar ID or mailbox address remains as a literal (#77, #76 partial)

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
