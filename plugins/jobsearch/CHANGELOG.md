# jobsearch — Changelog

## [0.4.8] — 2026-06-16

### Changed (cv-generator SKILL.md v0.2.6 → v0.2.7 / generate_cv.py / cv-master.json)

- **Experience order — fixed, no exceptions** : removed `CORPORATE_FIRST_CELLS` logic (Artelia-first for T4/T5). All cells now output Blue Green → Artelia → Open Ocean (chronological reverse). Updated SKILL.md accordingly.
- **About FR — forme nominale** : all 15 `about.fr` sections rewritten to nominal form. No more bare infinitives (`"Livrer…"`, `"Maîtriser…"`, `"Apporter…"`). Added mandatory FR style rule in SKILL.md.
- **SKILL.md** : added "About section — FR style rule" block; replaced "Experience order rules" table with single fixed-order rule.
- **cv-master.json bullets** :
  - `open_ocean.p1.default.en[2]` : "Business Angels and VCs" → "institutional investors (Seventure Partners, Cap Décisif/FNA)"
  - `blue_green.p1.default.en[2]` : generic stack line → Edifice/IC Ingénieurs Conseils (€25M + €35M projects)
  - `artelia.p1.default` (en + fr) : replaced 3 vague bullets with specific P&L/portfolio/roadmap bullets (SBM Offshore, Nexans, ASN, Cadeler)

## [0.4.7] — 2026-06-16

### Fixed (cv-master.json / cv-generator v0.2.6)

- CPTEC title FR : "Analyste Données Climatiques" → "Analyste Climatique — Événements Extrêmes"
- CPTEC title EN : "Climate Data Analyst" → "Climate Data Analyst — Extreme Events"
- Open Ocean P1 title : added "Marine Data Intelligence" branding
- Artelia bullets : stripped P&L BU scope across all FR + EN bullets
- P1×T2 : trimmed about[0] + BG t2 bullet[0] for 1-page fit

## [0.4.6] — 2026-06-16

### Fixed (cv-master.json / cv-generator SKILL.md v0.2.5)

- FR quality pass — 14 corrections across P1–P5 : openers "Cumuler"/"Fort de" → nominal forms, infinitif passé P2×T1, "Manager" → "Diriger", "ventures" → "startups", bullet vague BG P1 → Edifice/IC Ingénieurs, "delivery agile" → "livraison agile", P5 20 ans → 15 ans (factuel), Artelia period 2019–2022 → 2019–2023 (factuel), CPTEC "Analyste Données" → "Analyste Climatique — Événements Extrêmes"
- P1×T2 about rewrite + BG t2 bullets override

## [0.4.5] — 2026-06-14

### Changed (cv-generator SKILL.md v0.2.3 → v0.2.4 / generate_cv.py)

- **`--company` + `--job-title`** — output filename auto-built: `CV_Renaud_Laborbe_{job_slug}_{company_slug}_{LANG}.pdf`. Falls back to `P{n}_T{n}_{LANG}` if omitted.
- **`--data-dir`** — load `cv-master.json` from a custom path (workaround for read-only plugin dir in Cowork).
- **`--container-titles`** — JSON array of 3 strings, overrides competency block titles for this generation only. Cell defaults apply when omitted. Agent can propose better titles if the offer signals a stronger angle.
- **`--bullet-overrides`** — JSON dict `{"company.profile.lang.index": "new bullet"}`, injects personalised bullets without touching cv-master.json. Wired into Step 3b of SKILL.md.
- **Auto 1-page check** — if `pikepdf` is available (`--with pikepdf`), script checks page count post-render and retries with compact CSS layout if overflow. Warns explicitly if still >1 page after compact.
- **P4×T5 FR container title defaults** updated: "Ingénierie IA terrain" → "Architecture & agents IA", "Succès & adoption client" → "Cycle client & déploiement".
- **SKILL.md Step 3b** updated to document `--bullet-overrides` key format + example.
- **SKILL.md Step 4** updated with all new flags, output filename format, and compact-layout note.

### Validated

All 30 CVs — 1 page each.

## [0.4.4] — 2026-06-14

### Changed (cv-generator SKILL.md v0.2.2 → v0.2.3)

- **FR verb convention — infinitif exclusivement** — All FR bullets and `about.fr` across P1–P5 × BG/Artelia/OO rewritten to start with an infinitive verb ("Déployer", "Piloter", "Construire"). Removes all past participles ("Déployé", "Construit") and conjugated present forms ("Conçoit", "Pilote"). Research-backed: CV Creator, JobImpact, TopCV, Zety all confirm infinitive as the only correct form for French CVs.
- **Cell labels** — Added `label.fr` + `label.en` to all 15 matrix cells in `cv-master.json`. SKILL.md Step 5 now outputs the cell label (e.g. "Solutions Engineer — éditeur SaaS IA") instead of the P/T code.
- **Step 3b — LLM personalization** — New step in SKILL.md between cell selection and PDF generation: the LLM reads the job offer, identifies 2–3 key signals, rewrites 1–2 bullets per company to mirror those signals — factual anchors always intact. Max 2 bullets changed per company.
- **Editorial rules updated** — Removed "past participle for past roles" and "present tense for current role" rules. Replaced with "infinitive for all roles, current and past".
- **Open Ocean P1 default FR** — Also fixed residual "Business Angels" → "Seventure Partners, Cap Décisif/FNA" and "DCNS" → "Naval Group (ex-DCNS)" in the default (P1×T1/T2) cell.

### Validated

All 30 CVs — 1 page each.

## [0.4.3] — 2026-06-14

### Added

- **`cover-letter` skill** (`skills/cover-letter/SKILL.md` v0.1.0) — LLM-native cover letter generator using the same 15-cell profile × company-type matrix as the CV generator. Produces 3-paragraph letters (~300 words EN / ~330 FR) anchored in real verifiable facts. No HR boilerplate — opens with a hook, closes with confidence. Applies the same cell-specific narrative rules (T3: delivery advisory, T4: P&L/governance, T5: velocity + solopreneur counter). Registered in `marketplace.json`.
- **`/cover-letter` command** (`commands/cover-letter.md`) — slash command routing to the cover letter skill.

### Changed

- **`cv-generator` SKILL.md v0.2.1 → v0.2.2** — Added "Narrative methodology" section documenting: experience order rules per cell (CORPORATE_FIRST for T4, default BG-first otherwise), the signal to emphasise per company type (T3/T4/T5/T1/T2), the signal per profile (P1–P5), complete factual anchors table (real metrics, verified client names), and banned phrases list ("urban planning automation", "DCNS", "Business Angels", "delivery" in FR, "en solo à vélocité maximale").

### Fixed (cv-master.json — P2/P3/P4/P5 defaults)

- Added cell-specific bullets (T3/T4/T5) for P2 (Lead/Manager) across all 3 companies
- Added cell-specific bullets (T1/T5) for P3 (CTO) across all 3 companies
- Artelia P3 default: removed factually wrong "Led investor presentations" bullet (that was Open Ocean, not Artelia)
- "DCNS" → "Naval Group (ex-DCNS)" everywhere (P2/P3/P4/P5, EN+FR)
- "Business Angels" → "institutional investors (Seventure Partners, Cap Décisif/FNA)"
- P4 Blue Green FR: "automatisation urbanisme" (banned) → "analyse PLU pour l'éolien terrestre"
- Blue Green P2 FR: "delivery" → "livraison"
- Blue Green P3 FR/EN: removed "en solo à vélocité maximale" / "solo at maximum velocity"
- P5 Blue Green: trim over-limit bullets (141→116 EN, 147→111 + 121→119 + 142→113 FR)

All 30 CVs validated — 1 page each.

## [0.4.2] — 2026-06-13

### Added (WP-D — hal mirror tagged `jobsearch`)
- `log-application` Step 4b: after the canonical Obsidian `tache` write, also create a hal task in the `renaud` workspace with `tags=["jobsearch"]` and `due_date = date_candidature + 7d`. Mirrors the relance into hal so it surfaces under `/briefing`'s tag-grouped `🎯 jobsearch` subsection of the Renaud section (WP-D — see `briefing` 0.3.0). Sprint-less by design. Idempotent on re-apply (skips if a non-closed hal task with the exact title already exists). Partial-failure mode: Obsidian-OK + hal-fail is degraded-but-safe — reported explicitly, Step 5 still fires.
- `interview-prep` Step 4b: after the canonical `entretien` prep note write, also create a hal task in the `renaud` workspace titled `Entretien <type> — <Entreprise> — <DD-MM-YYYY>` with `tags=["jobsearch"]` and `due_date = interview_date`. Same idempotency + degraded-but-safe failure semantics as `log-application`. The Obsidian prep note stays the canonical document; the hal task is a thin pointer.
- `allowed-tools` for both skills now includes `mcp__hal-mcp__create_task` alongside `Skill(jobsearch-vault)` (`interview-prep` also keeps `Read`).
- Both skills' Step 5 success report now mentions the hal mirror.

### Notes
- Frontmatter version of `log-application` and `interview-prep` jumps 0.4.0 → 0.4.2 to re-sync with the plugin `plugin.json` (which advanced to 0.4.1 in the cv-generator FR pass without touching these two skills).
- `cv-generator` SKILL.md unchanged at 0.2.1 — its frontmatter version is independent of the plugin-level bump (only the 3 skills that change behaviour need to track the plugin version per the 4-field sync rule).
- No CV/PDF, no schema, no `jobsearch-vault` change.

## [0.4.1] — 2026-06-12

### Fixed (cv-generator — FR quality pass on the P4 Customer Success / Solutions Engineer CV)
- **Open Ocean FR job titles** (p2/p4/p5): "Co-Fondateur & Directeur Général" → "Directeur Technique & Co-Fondateur" — leads with the technical/functional role, founder status second.
- **Blue Green FR title** (p2): "AI Lead" → "Responsable Solutions IA — Consultant" (was an untranslated English label).
- **Container titles** — removed residual English from the FR side across cells: P4×T5 (`Ingénierie IA terrain`, `Succès & adoption client`, `Secteurs d'expertise`), plus p2×t1, p2×t3, p2×t4, p2×t5, p3×t1, p3×t5 (`Leadership`/`Scale-up`/`hands-on` calques reworded).
- **P4×T5 competency items** rewritten as transferable skills, not tasks: `Conduite du changement & formation IA`, `Gestion multi-niveaux (C-level → ops)`, `Vente de solution complexe B2B`.
- **P4×T5 `about` + title** de-anglicised: title → "Solutions Engineer IA — Déploiement GenAI en environnement industriel"; the three FR sentences reworded from English calques into natural French.
- **P4 experience bullets** cleaned of franglais (`discovery`/`delivery`/`workflows`/`cross-fonctionnelle`/`data marines` → French), keeping the +15% YoY retention/expansion proof.
- **`generate_cv.py`**: FR periods now render "Aujourd'hui" instead of "Present".
- cv-generator skill bumped 0.2.0 → 0.2.1.

## [0.4.0] — 2026-06-12

### Added
- `jobsearch-vault` skill — self-contained, **filesystem-only** (no network, no API key) read/write access to the Job-Search slice of the Obsidian vault. Owns 5 note types (`opportunite-js`, `entreprise-js`, `contact-js`, `entretien`, jobsearch `tache`) via plain-stdlib CLI scripts (`create_note.py`, `read_note.py`, `update_frontmatter.py`, `search_vault.py`, `list_notes.py`). Ported from the global `obsidian-crm` skill with the REST/Local-REST-API backend stripped out. Doubles as an invocable skill (triggers: "pipeline candidatures", "liste mes entretiens", "cherche dans mes candidatures", "mes relances jobsearch") and as the shared library the other jobsearch skills compose.
- Bundled `note_schemas.py` ships the `entretien` `categorie`/`interlocuteurs` fix natively — creating a fully-specified interview note now raises **zero** validation warnings.
- `jobsearch-vault` registered in `marketplace.json` `plugins.jobsearch.skills`.

### Changed
- **`log-application` + `interview-prep` re-pointed to `jobsearch-vault`** (Option A — invoke via the `Skill` tool, no script paths, no PLUGIN_DIR resolver for vault I/O). `allowed-tools` swapped `Skill(obsidian-crm)` → `Skill(jobsearch-vault)`. Same structured create/update/search payloads, same idempotency, same exit-code contract — only the addressee changed. `interview-prep` keeps `Read` for `profiles/`.
- `interview-prep`: removed the "expected non-blocking `categorie`/`interlocuteurs` warnings" paragraph — the bundled schema accepts both fields, so a clean `entretien` create has zero warnings.
- The global `obsidian-crm` skill is left byte-for-byte unchanged (legacy/fallback for non-jobsearch domains).

## [0.3.0] — 2026-06-12

### Added
- `log-application` skill — classifies a pasted offer against the existing P1–P5 profile taxonomy, then composes the global `obsidian-crm` skill to create one `opportunite-js` candidature note (with `source`, `target_profile`, `lien_offre`, `date_relance: today+7d`, body = pasted offer) and one `tache` relance (`etiquettes: ["jobsearch"]`, `echeance: today+7d`) that the Loop 3 `morning-briefing` surfaces.
- `interview-prep` skill — given a candidature, composes `obsidian-crm` to read the candidature note + the matching `profiles/p{1-5}_*.md`, then creates one `entretien` note (`categorie: Préparation`) with the always-identical 5-section body: Société · Résumé JD · Pitch (positioned for the candidature's `target_profile`) · Cas du parcours · Questions probables.
- `/log-application` and `/interview-prep` slash commands.
- Both new skills registered in `marketplace.json` `plugins.jobsearch.skills`.

### Fixed (live smoke-test findings against the real Obsidian vault)
- `log-application`: the relance surfaces in `/briefing` **on its due date** (`date_relance`, today+7d), not "tomorrow" — corrected the misleading frontmatter description + Step 4 prose.
- `log-application`: `lien_offre` is now **omitted** when no URL is provided (passing `""` triggered a spurious `does not look like a URL` warning on every link-less application).
- `log-application`: Step 4 idempotency now matches the real `tache` enum — open states `Pas commencée`/`Today`/`En cours`, closed `Terminé`/`Archivé` (was the non-existent `Terminée`/`Annulée`).
- `interview-prep`: documented the expected non-blocking `unknown field "categorie"`/`"interlocuteurs"` warnings (the fields are documented in `obsidian-crm/references/schemas.md` but lag its runtime validator) — mirrors the `target_profile` escape hatch, so the skill no longer reads as failing.

### Changed
- Renamed CHANGELOG title `cv-generator — Changelog` → `jobsearch — Changelog` (the plugin now hosts three skills, not just cv-generator).

## [0.1.2] — 2026-06-09

### Fixed
- Language mixing in FR CVs: all competency items in `fr` containers were left in English — now fully translated
- Section labels hardcoded in English (`About`, `Key Competencies`, `Work Experience`, `Earlier Career`, `Education`) — now lang-aware via template placeholders
- `Earlier Career` section had no FR support in data or generator — added `title_fr`/`description_fr` fields and lang-aware rendering

### Changed
- Blue Green P1 FR bullet: removed ultra-technical details (chunk counts, framework names) for broader audience
- P3×T5 and P4×T5 FR about sections: softened technical jargon

### Added (SKILL.md)
- Step 0: spontaneous application detection — when no job offer is present, the skill now asks Renaud for target profile and company type interactively instead of silently defaulting

## [0.1.1] — 2026-06-03

### Fixed
- Cowork compatibility: output dir, cleanup, photo fallback
- Photo bundled in plugin assets

## [0.1.0] — 2026-06-03

### Added
- Initial plugin structure (migrated from `~/Projects/MyClaudeSkills/cv-generator/`)
- 5-profile × 5-company-type matrix (15 cells, FR + EN) — see task brief
- New `--profile / --company-type / --lang` CLI API
- Rétro-compat: `--positioning ai_consulting/cto/business_dev` still works
- Plugin directory resolver in SKILL.md (env var → cache → Cowork → dev path)
- Cowork-compliant: WeasyPrint loaded via `uv run --with`, no pre-install
