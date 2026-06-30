# STATUS — renaud-marketplace

Last updated: 2026-06-29

## Current Focus

Refonte qualité CV — nouvelle démarche structurée par profil (recherches marché → parcours HAL → CV par profil)
Morning-briefing v2 — scan 2 boîtes mail + scoring offres + plan du jour (#18 — #22 résolu, prêt pour brief-to-plan)

## In Progress
- [ ] **P6 Digital Innovation — Bureau d'ingénierie ENR** — session dédiée
- [ ] **P1 Architecte IA** — session dédiée
- [ ] **P3 Late CTO** — session dédiée
- [ ] **P2 Lead IA** — session dédiée (profil le plus faible, à reconsidérer)

**Ressources prêtes :**
- Parcours source de vérité → HAL workspace `renaud`, slug `parcours` (màj 2026-06-19)
- Fichier local → `~/Library/CloudStorage/SynologyDrive-MyAssistant/jobsearch/parcours-renaud.md`
- Briefs marché par profil → `~/Library/CloudStorage/SynologyDrive-MyAssistant/jobsearch/research/P{1,2,3,4,6}-*.md`

**Template session par profil :**
1. LOAD → parcours HAL + brief recherche profil
2. SCRAPE → 2-3 offres LinkedIn (Bright Data MCP)
3. DRAFT → about + containers + bullets par expérience (markdown)
4. REVIEW → validation Renaud
5. GEN → cv-generator → PDF
6. COMMIT → bump version cv-master.json + STATUS.md

## Done (current sprint)

- [x] **fix(jobsearch): log-application relance task in hal renaud only, drop Obsidian tache (jobsearch v0.6.1 / PR #28)** — Step 4 crée directement la tâche relance dans hal (`renaud`, tag `jobsearch`). Step 4b (miroir hal) supprimé — hal est la source unique. Closes #27. — 2026-06-29

- [x] **feat(briefing): morning-briefing v2 (#18) — Gmail perso+pro, scoring offres BrightData, plan du jour 6 blocs (briefing v0.6.0 / PR #24)** — 2026-06-24

- [x] **research(brightdata): pipeline extraction JD LinkedIn validé (#22)** — `web_data_linkedin_job_listings` retenu (JSON structuré, zéro bruit). gmail-mcp retourne plain text, job IDs extractibles par regex `jobs/view/(\d+)`. Pipeline : email → job IDs → URL slug → web_data_linkedin_job_listings → job_summary → LLM. `scrape_as_markdown` éliminé (85% bruit, LinkedIn bloque). Bonus : `web_data_linkedin_posts` disponible pour analyse tendances (likes/comments, pas d'impressions). Issue #22 commentée + fermée. Débloque #18. — 2026-06-24

- [x] **fix(briefing): sprint-planner clôture sprints actuel avant création (briefing v0.4.4 / PR #19)** — Nouvelle étape 6b : `list_sprints(status="actuel")` sur blue-green + renaud → `update_sprint(status="passes")` avant `create_sprint`. Closes #17. — 2026-06-24

- [x] **fix(jobsearch): P4×T5 About rewrite — technical-first, drop false buyer claim (jobsearch v0.5.1 / PR #20)** — About EN réécrit (technique → delivery → empathie), HAL + BlueWind comme ancres, suppression "15 years client side" → "4 years DSI Artelia", suppression "user-buyer GenAI vendors target". credibility_note + profiles/p4_cs_fde.md corrigés. Closes #14. — 2026-06-24

- [x] **fix(cv-generator): auto-fit itératif 3 niveaux + doc cold start (jobsearch v0.5.2 / PR #21)** — `COMPACT_CSS` → `COMPACT_CSS_LEVELS[3]` (gentle → moderate → ultra-compact). Retry binaire → boucle itérative niveau 1-2-3 jusqu'à 1 page. SKILL.md : doc cold start + commande pre-warm. Closes #15. — 2026-06-24

- [x] **Mistral AI — CVs killer P4×T5 EN (jobsearch v0.5.1)** — 2 CVs générés et validés (FDE + Prototyping). Nouveaux params `--about-override` / `--title-override` ajoutés au générateur. Règles éditoriales EN gravées dans SKILL.md (premier lecteur = RH, pas ingénieur). P4×T5 EN containers mis à jour (AI Solutions 3 items, Open Ocean 1 bullet). — 2026-06-20

- [x] **cv-generator P4 fix (jobsearch v0.4.9 / PR #13)** — Refonte complète profil P4 (FDE/Solutions Engineer) : about P4×T5 triangle différenciateur (vendeur B2B Artelia / DSI insider / constructeur IA), containers restructurés, bullets BG (BlueWind 91 docs 5 agents 8.6/10), bullets Artelia créés (pipeline grands comptes + comités DSI), bullets OO créés (co-fondateur/CTO, pas Sales). Fix généré par `archon workflow run skill-improve "#12"` — premier run end-to-end réussi. — 2026-06-18

- [x] **fix(improve): mcp__github__issue_write + workflow self-contained (v0.1.2)** — 2 bugs : (1) SKILL.md utilisait `gh` (non dispo Cowork) → remplacé par `mcp__github__issue_write`, `allowed-tools` et section IMPORTANT corrigés ; (2) `skill-improve.yaml` node 2 référençait `archon-fix-github-issue-experimental` (commande inexistante) → remplacé par prompt self-contained en 6 étapes. Closes #11. — 2026-06-18

- [x] **plugin `improve` v0.1.1 + workflow `skill-improve.yaml` (marketplace v0.5.0 / PR #9)** — Un skill Cowork générique `/improve <skill-name>` : auto-détecte le repo depuis le nom du skill, 1 seule question (delta observé/attendu), crée l'issue GitHub avec la commande Archon dedans. Archon workflow `skill-improve.yaml` wrape `archon-fix-github-issue-experimental` + verify-version-bump. Remplace PR #7 (bg-improve + renaud-improve dupliqués). Follow-up P2 : copier `skill-improve.yaml` dans `bluegreen-marketplace`. — 2026-06-17

- [x] **cv-generator about FR + experience order (jobsearch v0.4.8 / cv-generator v0.2.7)** — 15 about.fr réécrits en forme nominale, ordre fixe BG→Artelia→OO (suppression CORPORATE_FIRST_CELLS), 3 bullets corrigés (OO Business Angels→institutionnels, BG stack→Edifice/IC, Artelia default→P&L spécifique). Règle style FR ajoutée SKILL.md. — 2026-06-16

- [x] **cv-generator FR quality pass (jobsearch v0.4.7 / cv-generator v0.2.6)** — 14 corrections sur P1–P5 : openers "Cumuler" → "Fort de", infinitif passé P2×T1, "Manager" verbe → "Diriger", "ventures" → "startups", bullet vague BG P1 → Edifice/IC Ingénieurs, "delivery agile" → "livraison agile", P5 20 ans → 15 ans (factuel), Artelia period 2019–2022 → 2019–2023 (factuel), CPTEC "Analyste Données" → "Analyste Climatique — Événements Extrêmes". — 2026-06-16

- [x] **update_sprint wiring — briefing v0.4.3** — `mcp__hal-mcp__update_sprint` ajouté aux `allowed-tools` de sprint-planner + sprint-review. Section "6a bis" dans sprint-planner ÉTAPE 6 : correction statut post-création via `update_sprint` avant de recréer. 4-field version sync : briefing 0.4.2 → 0.4.3. — 2026-06-15

- [x] **fix(sprint-planner): SPRINT_STATUS dynamique — briefing v0.4.2** — `SPRINT_STATUS = "actuel"` si `NEXT_MON <= TODAY` (planning lundi matin / rattrapage), `"suivant"` sinon. Corrige `list_sprints` idempotence (ÉTAPE 6a) et `create_sprint status=` (ÉTAPE 6b). Sprint-review drift 0.4.0 → 0.4.2 corrigé au passage. — 2026-06-15

- [x] **sprint-review + sprint-planner skills (briefing v0.4.0)** — `sprint-review` : bilan sprint hal (blue-green + renaud), métriques jobsearch, projets BG, shortlist semaine suivante, clôture hal après validation explicite. `sprint-planner` : report/abandon décisions, métriques vault, scan LinkedIn gmail-mcp, conflit calendriers, calcul capacité 35h, plan MUST/SHOULD/COULD/BACKLOG, création sprint hal avec sprint_number auto-incrémenté + idempotence. Mode schedule : autonome pour étapes 0-4/0-5, gate sur création. — 2026-06-14

- [x] **cv-generator tooling upgrade (jobsearch v0.4.5 / cv-generator v0.2.4)** — `--company`+`--job-title` → filename lisible (ex: `CV_Renaud_Laborbe_forward_deployed_engineer_yotta_FR.pdf`). `--data-dir` pour Cowork read-only. `--container-titles` JSON array pour override sans toucher le JSON. `--bullet-overrides` pour injecter les bullets Step 3b. Auto 1-page check (pikepdf) + compact layout fallback. P4×T5 FR defaults: "Architecture & agents IA" + "Cycle client & déploiement". 30/30 validés. — 2026-06-14
- [x] **cv-generator editorial upgrade — FR infinitif + labels + Step 3b personnalisation (jobsearch v0.4.4 / cv-generator v0.2.3)** — Tous les bullets FR réécrits à l'infinitif (P1–P5 × BG/Artelia/OO, ~80 bullets + 15 about.fr). Labels human-readable ajoutés aux 15 cellules. Step 3b : personnalisation LLM (1–2 bullets/entreprise adaptés aux signaux de l'offre, ancres factuelles toujours intactes). 30/30 CVs 1-page validés. — 2026-06-14

- [x] **cover-letter skill + cv-generator methodology (jobsearch v0.4.3)** — New `/cover-letter` command: LLM-native 3-paragraph letter, 15-cell matrix, factual anchors, banned phrases, solopreneur counter. cv-generator SKILL.md v0.2.2: added narrative methodology section (experience order rules, T/P signals, factual anchors, banned phrases). — 2026-06-14

- [x] **cv-generator quality sprint — cell-specific bullets P1/P2/P3 + factual fixes (30/30 CVs validated)** — Added T3/T4/T5 bullets for P2 (Lead/Manager) × all 3 companies; T1+T5 bullets for P3 (CTO) × all 3 companies; fixed Artelia P3 "investor presentations" lie (was Open Ocean), fixed "Business Angels" → institutional investors, fixed "DCNS" → Naval Group, fixed franglais "delivery" → "livraison" in FR bullets. All 30 CVs 1-page validated. — 2026-06-14

- [x] **cv-generator multi-company-type differentiation — P1×T3/T4/T5 (30/30 CVs, commit 6162a0c)** — Restructured cv-master.json: bullets[profile] now has `default` + per-cell overrides. P1×T5 counters solopreneur (Open Ocean first, institutional VCs), P1×T4 frontloads Artelia (corporate credibility), P1×T3 technical delivery emphasis. "urban planning automation" banned → replaced with accurate PLU analysis. Real client names + verifiable metrics throughout. generate_cv.py updated for cell-specific title overrides + bullet fallback. — 2026-06-14

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

- [ ] **#10 — skill mail** : scanner/classifier boîte jobsearch Gmail. Dépend de #18 (✅ mergé).
- [ ] **#10 — skill mail** : scanner/classifier boîte jobsearch Gmail. Dépend de #18.
- [ ] Visual review of priority CVs (p1×t4, p3×t1, p2×t5)
- [ ] gmail-mcp: test OAuth flow end-to-end from claude.ai (connector validated 2026-06-10)
- [ ] Notion job search skill
