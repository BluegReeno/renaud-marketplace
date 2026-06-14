# STATUS — renaud-marketplace

Last updated: 2026-06-14

## Current Focus

**WP-D MERGED (PR #5) — hal tags wired into renaud skills.** `morning-briefing` groups `renaud` tasks by tag (jobsearch first), `log-application` + `interview-prep` auto-tag hal tasks with `jobsearch`. Requires hal-mcp v39 deployed (done 2026-06-13). briefing v0.3.0 · jobsearch v0.4.2.

**🏁 LastDev chain COMPLETE.** All 4 loops shipped (backend hal-mcp v39 since PR #46; skills done with WP-D). New ideas weigh against the stopping rule: does it directly produce a job interview or Blue Green revenue?

## In Progress

- (nothing active)

## Done (current sprint)

- [x] **WP-D — hal tags wired into renaud skills (briefing v0.3.0 · jobsearch v0.4.2 · PR #5 merged)** — `morning-briefing` groups `renaud` tasks by unified tag (jobsearch → rosaslaborbe → personal → finance → hr → laborbe → other); `log-application` + `interview-prep` create hal mirror task tagged `jobsearch` (best-effort, Obsidian stays canonical). `mcp__hal-mcp__create_task` + `list_tasks` added to `allowed-tools`. Requires hal-mcp v39. AC validated by static inspection + review fixes (H1 list_tasks allowed-tool, H2 README versions, M1/M2 Step 4b/5 failure semantics). 4-field version sync clean — 2026-06-14

- [x] **cv-generator FR quality pass (jobsearch 0.4.1 / cv-generator 0.2.1)** — applied Renaud's P4 (Customer Success / Solutions Engineer) feedback: de-anglicised FR titles (Open Ocean p2/p4/p5 → "Directeur Technique & Co-Fondateur", Blue Green p2 → "Responsable Solutions IA — Consultant"), container titles across P4×T5 + 6 p2/p3 cells, P4×T5 `about`/items reworded as skills-not-tasks, P4 bullets cleaned of franglais (discovery/delivery/workflows/data marines), `generate_cv.py` renders "Aujourd'hui" not "Present" in FR. CSM competencies researched + woven in (adoption, multi-level relationship, +15% retention proof). P4×T5 FR CV re-rendered live, 1 page, zero franglais. Umbrella version 0.4.0→0.4.1 (4-field sync). — 2026-06-12

- [x] **`jobsearch-vault` skill** (all 5 phases) — filesystem-only skill (5 JS note types, REST backend stripped) + 3 consumers re-pointed (Option A) + versions bumped (jobsearch 0.4.0, briefing 0.2.0, marketplace top-level 0.4.0, 4-field sync) + CHANGELOGs. Schema self-test 30/30; AC1/AC2/AC3 re-validated live vs the real vault (Anthropic P1 + Yotta P4 intact); `obsidian-crm` untouched. Committed direct to main `3a2b138` — 2026-06-12

- [x] Loop 4 — jobsearch v0.3.0 (`log-application` + `interview-prep`) — composition via `obsidian-crm`, P1–P5 reused, 5-section interview contract, idempotent relance; **AC1/AC2/AC3 smoke-tested live** + 4 findings fixed — PR #3 merged — 2026-06-12
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
