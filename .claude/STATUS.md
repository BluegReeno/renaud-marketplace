# STATUS — renaud-marketplace

Last updated: 2026-06-12

## Current Focus

**➡️ LastDev Loop 4 — jobsearch systematization** (même repo, dernière boucle). `log-application` (annonce + source → note Obsidian + tâche de suivi) et `interview-prep` (structure fixe, câblée aux 5 profils CV). Le briefing *lit* ce que Loop 4 *écrit*. Brief : `../hal/docs/features/loop-4-jobsearch-systematization.md`. hal-mcp **gelé v38**. **Deadline dim. 2026-06-14 → la chaîne LastDev STOPPE.**

Loop 3 livré : nouveau plugin `briefing` v0.1.0 (skill `morning-briefing`) mergé via PR #2. Agrège read-only tâches hal (`blue-green` + `renaud`) + jobsearch Obsidian + 3 calendriers Google, échecs bruyants (AC3). Décisions terrain-prep respectées (repo, host plugin, hal-mcp dédup).

Reste de l'ancien focus (backlog, non bloquant) : implémenter les vrais appels Gmail API si encore en stub.

## In Progress

- [ ] LastDev Loop 4 — `log-application` + `interview-prep` skills

## Done (current sprint)

- [x] Loop 3 — plugin `briefing` v0.1.0 (skill `morning-briefing`) — read-only daily dashboard (3 calendriers + hal tasks business/perso + Obsidian jobsearch), AC3 loud-failure, hal-mcp dedup — PR #2 merged — 2026-06-12

- [x] cv-generator v0.1.0 — 30/30 CVs validated (1 page each) — 2026-06-03
- [x] cv-generator v0.1.1 — fix FR language mixing — 2026-06-05
- [x] cv-generator v0.1.2 — add spontaneous mode — 2026-06-05
- [x] photo.jpeg bundled in plugin — 2026-06-05
- [x] gmail-mcp Supabase Edge Function deployed — fixes: McpServer import, webStandardStreamableHttp, registerTool API, export default — 2026-06-09
- [x] gmail-mcp auth fixed — SUPABASE_SECRET_KEYS env override workaround — 2026-06-09
- [x] All 4 MCP tools tested live: list_labels, search_emails, read_email, draft_email — 2026-06-09
- [x] Plugin renamed cv-generator → jobsearch, .mcp.json added for gmail-mcp server — 2026-06-09
- [x] Bumped to v0.2.0 (all 4 files in sync) — 2026-06-09
- [x] docs/mcp-server-supabase-edge.md — SUPABASE_SECRET_KEYS gotcha documented — 2026-06-09
- [x] README — versioning rules + .mcp.json format + repo structure — 2026-06-09
- [x] .gitignore — added tmp, breif-gmail.md, pycache, supabase temp dirs — 2026-06-09
- [x] gmail-mcp v0.2.0 — ?key= query-param auth for headerless connectors (Cowork/claude.ai), deployed + 401 behaviors verified — 2026-06-10
- [x] docs/mcp-server-supabase-edge.md §10 — OAuth prerequisites (feature_disabled gotcha) + query-param fallback — 2026-06-10
- [x] gmail-mcp OAuth consent page `oauth/consent/index.html` créée + Edge Function oauth supprimée — 2026-06-10
- [x] docs/mcp-server-supabase-edge.md §10a — HTML limitation Edge Functions + solution GitHub Pages documentée — 2026-06-10
- [x] gmail-mcp OAuth flow complet — consent page GitHub Pages + Google Auth + claude.ai connecteur validé — 2026-06-10
- [x] gmail-mcp OAuth flow testé — vrais appels Gmail API confirmés (pas de stubs) — 2026-06-10

## Backlog

- [ ] Visual review of priority CVs (p1×t4, p3×t1, p2×t5)
- [ ] gmail-mcp: test OAuth flow end-to-end from claude.ai (connector validated 2026-06-10)
- [ ] Notion job search skill
