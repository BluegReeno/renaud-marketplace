# STATUS — renaud-marketplace

Last updated: 2026-06-11

## Current Focus

**➡️ LastDev Loop 3 — `morning-briefing`** (le dashboard quotidien pro + perso). La chaîne LastDev arrive ici depuis `bluegreen-marketplace` (Loop 2 / `/hal tasks` v0.7.0 mergé). hal-mcp **gelé v38** — on consomme, on ne touche pas. Amorçage : [`RESUME-LOOP3.md`](../RESUME-LOOP3.md) · brief [`docs/loop-3-morning-briefing.md`](../docs/loop-3-morning-briefing.md) · master plan `../hal/docs/lastdev-plan.md`.

Loop 3 = **nouveau plugin `briefing`** : un skill qui agrège read-only les tâches hal (`blue-green` + `renaud`, sprint courant) + jobsearch Obsidian + 3 calendriers Google, en une vue. Décisions verrouillées au terrain-prep (repo, host plugin, hal-mcp déclaré + dédup) → voir RESUME. Loop 3 crée le squelette du plugin lui-même. Deadline Loops 3-4 : dim. 2026-06-14 → STOP.

Reste de l'ancien focus (backlog, non bloquant) : implémenter les vrais appels Gmail API si encore en stub.

## In Progress

(nothing — Loop 3 not started, terrain prepared)

## Done (current sprint)

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
