# jobsearch — Changelog

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
