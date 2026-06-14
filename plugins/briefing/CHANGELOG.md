# briefing — Changelog

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
