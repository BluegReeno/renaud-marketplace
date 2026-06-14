# briefing — Changelog

## [0.4.1] — 2026-06-14

### Changed (sprint-planner capacity calibration)
- Job search blocs Mar–Ven : 08h30–10h30 → **09h30–11h30** (dépose Lalie à l'école 8h50)
- Post LinkedIn : 30min → **2h** (rédaction + illustration + publication — toujours plus long que prévu)
- Buffer : 30% → **40%** (marge pour les imprévus de la semaine)
- Capacity formula updated : `(22 - X) × 0.6` dispo sprint (was `(23.5 - X) × 0.7`)

## [0.4.0] — 2026-06-14

### Added (sprint-review + sprint-planner skills)
- `sprint-review` skill: full weekly sprint bilan — hal task completion rate across `blue-green` and `renaud` workspaces, jobsearch metrics (candidatures/week, conversion by profile, refus patterns, relances due next week), Blue Green active projects, prioritised shortlist for next sprint. Clôtures sprint in hal only after explicit user validation. Includes scheduled-mode support (fully autonomous steps 0–4, gate on step 5).
- `sprint-planner` skill: next-sprint builder — report/abandon decisions for unfinished tasks, jobsearch vault metrics + vault relances, LinkedIn job alert scan via gmail-mcp (rlaborbe@gmail.com), 3-calendar conflict detection with automatic bloc adjustment in schedule mode, capacity calculation (35h brute, 10h job-search blocs, IC meeting, 30% buffer), 4-tier MUST/SHOULD/COULD/BACKLOG plan, hal sprint creation with sprint_number auto-increment and idempotency check. Creates sprint + assigns tasks only after explicit user validation.
- `/sprint-review` and `/sprint-planner` slash commands.

### Notes
- Both skills are scheduled-mode-friendly (run autonomously on Friday afternoon, present output, gate writes on explicit validation).
- `sprint-planner` Step 3 (LinkedIn scan) requires the `jobsearch` plugin to be co-installed (uses `mcp__claude_ai_gmail-mcp__search_emails`). Degrades gracefully with `gmail:DOWN` if unavailable.
- `sprint_number` for `create_sprint` is auto-computed: `list_sprints(status="actuel").sprint_number + 1`, with idempotency check via `list_sprints(status="suivant")`.

## [0.3.0] — 2026-06-13

### Added (WP-D — tag-aware renaud section)
- `morning-briefing` Step 1b now groups `renaud` workspace hal tasks by their first tag (drawn from hal-mcp v39's `tags` field, vocabulary `jobsearch` / `rosaslaborbe` / `personal` / `finance` / `hr` / `laborbe` / `other`). Tasks with empty/missing `tags` land under `other`. Fixed group order: `jobsearch` first (job + revenue priority), then `rosaslaborbe` → `personal` → `finance` → `hr` → `laborbe` → `other`.
- Step 3 render template: `## 🏠 Sprint en cours — Renaud [perso]` is now split into per-tag `### 🎯 jobsearch` / `### 🏡 rosaslaborbe` / … subsections (empty groups skipped). The `[perso]` workspace label still applies to every task regardless of tag.

### Notes
- `blue-green` workspace rendering is unchanged — tags only affect `renaud`.
- Hermetic: no MCP schema change, no new tools in `allowed-tools` (existing `mcp__hal-mcp__list_tasks` already returns the `tags` field).

## [0.2.0] — 2026-06-12

### Changed
- `morning-briefing` re-pointed from the global `obsidian-crm` skill to the new `jobsearch-vault` skill (Option A — invoke via the `Skill` tool). Step 0 probe + Step 1c now address `jobsearch-vault`; `allowed-tools` swapped `Skill(obsidian-crm)` → `Skill(jobsearch-vault)` (hal-mcp + Google Calendar tools unchanged). READ-ONLY.
- AC3 loud-failure contract preserved: a `jobsearch-vault` failure renders `⚠️ Jobsearch DOWN — <reason>` in the jobsearch section and flips the `jobsearch-vault:` source-status footer line — never a silent empty.

## [0.1.0] — 2026-06-11

### Added
- Initial plugin structure: `.claude-plugin/plugin.json`, `.mcp.json`, `skills/morning-briefing/SKILL.md`, `commands/briefing.md`, `CHANGELOG.md`
- `hal-mcp` http MCP server declaration (deduped at name+endpoint level with `bluegreen-marketplace/plugins/hal`)
- `morning-briefing` skill: composes hal tasks (both workspaces, current sprint + fallback to open tasks), Obsidian jobsearch via the global `obsidian-crm` skill, and 3 Google Calendars via the claude.ai Google Calendar MCP connector — read-only, with loud per-source failure notices
- `/briefing` slash command (self-contained trigger)
