# STATUS — renaud-marketplace

Last updated: 2026-06-12

## Current Focus

**🏁 `jobsearch-vault` SHIPPED (all 5 phases done, committed to main `3a2b138`).** Job-search vault I/O is now owned by renaud-marketplace: self-contained, **filesystem-only** (no network, no API key), 5 JS note types, carved out of the global `obsidian-crm` (left byte-for-byte unchanged as legacy/fallback). `log-application` + `interview-prep` + `morning-briefing` re-pointed via Option A (`Skill(jobsearch-vault)`, no path resolver for vault I/O). Versions bumped (jobsearch 0.4.0, briefing 0.2.0, marketplace 0.4.0, 4-field sync). AC1/AC2/AC3 re-validated **live against the real vault**; `obsidian-crm` untouched. Brief: [`.claude/tasks/jobsearch-vault-skill.md`](tasks/jobsearch-vault-skill.md).

**🏁 LastDev chain COMPLETE.** All 4 loops shipped (backend frozen since Loop 1 at hal-mcp v38; skills done with Loop 4). New ideas weigh against the stopping rule: does it directly produce a job interview or Blue Green revenue? Confirmed split: **Blue Green CRM → `/hal`** (hal cloud) · **Job Search CRM → Obsidian vault** (soon via `jobsearch-vault`).

jobsearch v0.3.0 ships `log-application` + `interview-prep` (PR #3 merged). AC1/AC2/AC3 validated **live against the real Obsidian vault** (2 real applications logged: Anthropic P1, Yotta P4 — both kept). The live run found + fixed 4 real defects the static review missed (relance surfaces on its due date not "tomorrow"; lien_offre omitted when empty; idempotency enum corrected; entretien categorie/interlocuteurs warnings documented).

Reste de l'ancien focus (backlog, non bloquant) : implémenter les vrais appels Gmail API si encore en stub.

## In Progress

- (nothing active)

## Done (current sprint)

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
