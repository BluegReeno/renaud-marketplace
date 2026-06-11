# briefing — Changelog

## [0.1.0] — 2026-06-11

### Added
- Initial plugin structure: `.claude-plugin/plugin.json`, `.mcp.json`, `skills/morning-briefing/SKILL.md`, `commands/briefing.md`, `CHANGELOG.md`
- `hal-mcp` http MCP server declaration (deduped at name+endpoint level with `bluegreen-marketplace/plugins/hal`)
- `morning-briefing` skill: composes hal tasks (both workspaces, current sprint + fallback to open tasks), Obsidian jobsearch via the global `obsidian-crm` skill, and 3 Google Calendars via the claude.ai Google Calendar MCP connector — read-only, with loud per-source failure notices
- `/briefing` slash command (self-contained trigger)
