# jobsearch — Changelog

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
