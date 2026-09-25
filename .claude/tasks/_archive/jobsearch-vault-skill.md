# Brief — `jobsearch-vault` skill (own the Job-Search vault I/O in renaud-marketplace)

> **Repo**: `renaud-marketplace` · **Plugin**: `jobsearch` · **New skill**: `jobsearch-vault`
> **Status**: planned — next sprint (starts Mon 2026-06-15)
> **Type**: skill evolution (allowed under the LastDev stopping rule — it directly serves job search). Backend stays frozen: no `hal-mcp`, no Supabase, no MCP server, **no network at all**.

## Why

The job-search domain currently reads/writes the Obsidian vault through the **global** `obsidian-crm` skill (`~/.claude/skills/obsidian-crm/`). That skill is a shared, do-everything CRM (Blue Green + Job Search + Project Management) living outside any marketplace. Three renaud-marketplace skills depend on it — `log-application`, `interview-prep` (plugin `jobsearch`) and `morning-briefing` (plugin `briefing`).

We want the job-search vault I/O **owned by renaud-marketplace**: self-contained, shipped via the marketplace, Cowork-compatible, decoupled from the global skill. `obsidian-crm` is **not touched** — it stays as-is for everything else (and as a fallback). Going forward, jobsearch flows compose the new skill.

## Confirmed architecture (the coherence target)

| Domain | Source of truth | Accessed via |
|--------|-----------------|--------------|
| **Blue Green CRM** (companies, contacts, opportunities, interactions) | **hal cloud** (Supabase `halcrm_*`, migrated 2026-05-30) | **`/hal`** skill + `hal-mcp` tools |
| **Job Search CRM** (candidatures, companies, contacts, interviews) | **Obsidian vault** (`CRM-JobSearch/`) | **`jobsearch-vault`** (this skill) ← was `obsidian-crm` |
| Project/sprint management | Obsidian vault | stays in `obsidian-crm` (out of scope here) |

> `obsidian-crm` still declares legacy `CRM-BlueGreen/*` schemas — **dead path**, the BG data lives in hal now. This brief does not change that; it only carves out the *jobsearch* slice.

## What `jobsearch-vault` IS — a skill AND a shared script library (no skill-nesting)

`jobsearch-vault` is **two things at once**, on purpose:

1. **An invocable skill** — its `SKILL.md` carries a description + triggers so Renaud can use it directly to explore the job-search vault: *"pipeline candidatures", "liste mes entretiens", "cherche dans mes candidatures", "mes relances jobsearch", "search my applications"*. Read/list/search/create/update on the jobsearch notes.
2. **A shared script library** — its `scripts/` are plain CLIs (`create_note.py`, `read_note.py`, `update_frontmatter.py`, `search_vault.py`, `list_notes.py`). They remain directly callable by file path for ad-hoc use or future routines (a cron job, a one-off script, the user manually).

**How the 3 sibling skills compose it — LOCKED: Option A, invoke via the `Skill` tool.** `log-application`, `interview-prep` and `morning-briefing` reach `jobsearch-vault` exactly the way `morning-briefing` reaches `obsidian-crm` **today**: they declare `Skill(jobsearch-vault)` in `allowed-tools` and *invoke the skill* ("ask jobsearch-vault to create / read / list …"). They do **not** call its scripts by a resolved path, and they do **not** hardcode `~/.claude/skills/...`. The determinism for writes lives **inside** `jobsearch-vault` (its SKILL.md takes a structured request and runs `create_note.py` with the exact payload).

Why Option A (decided 2026-06-12): in Renaud's Cowork session both marketplaces' skills are loaded and invocable, and `obsidian-crm` already works this way — so the `Skill` tool locates `jobsearch-vault` itself. **No PLUGIN_DIR resolution, no cross-plugin path-hunting anywhere.** This also keeps the "a skill using a skill" question clean: it's the same lightweight skill-invocation morning-briefing already does, not heavyweight nesting — and Option A is the only path that needs no on-disk lookup.

## Objective

One self-contained skill providing the **primitive vault operations** (create / read / update / search / list) for the **job-search note types only**, **filesystem-only** (no network, no API key), with zero dependency on the global `obsidian-crm`.

## Scope — note types owned by this skill

Bundle a **jobsearch-only** `note_schemas.py` (5 types):

| Type | Folder | Role |
|------|--------|------|
| `opportunite-js` | `CRM-JobSearch/Opportunites/` | candidature |
| `entreprise-js` | `CRM-JobSearch/Entreprises/` | company |
| `contact-js` | `CRM-JobSearch/Contacts/` | contact |
| `entretien` | `CRM-JobSearch/Entretiens/` | interview (prep + CR) |
| `tache` | `Taches/` | **jobsearch-tagged relances only** (`etiquettes` contains `"jobsearch"`) |

Carry over the **schema fix already applied** to `obsidian-crm/note_schemas.py` on 2026-06-12: `entretien` includes `categorie` (enum `Préparation`/`Compte-rendu`) and `interlocuteurs` (list). The bundled copy starts correct — no "unknown field" warnings.

**Out of scope** (stay in `obsidian-crm`): all `*-bg` types, `projet`, `sprint`, `sprint_transition.py`, Blue Green / project-management workflows, the Templater templates (optionally copy the 5 jobsearch ones for reference).

## Build — what to port, filesystem-only

Bundle under `plugins/jobsearch/skills/jobsearch-vault/scripts/` jobsearch-scoped copies of:

- `obsidian_api.py` — **strip it to the filesystem backend only.** Drop the REST/`requests`/`urllib3` path, the auto-detect, and the `OBSIDIAN_BACKEND` override. Result: pure-stdlib direct `.md` read/write. (Editing local files needs no server and no key; if Obsidian is open it auto-reloads externally-changed files.)
- `note_schemas.py` — trimmed to the 5 jobsearch types (+ the `categorie`/`interlocuteurs` fix). Keep the `__main__` self-test.
- `create_note.py`, `update_frontmatter.py`, `read_note.py`, `search_vault.py`, `list_notes.py` — same CLI interfaces as `obsidian-crm`, repointed at the bundled `obsidian_api` + `note_schemas`. These are the engine `jobsearch-vault`'s SKILL.md runs internally when invoked, and they stay directly callable for ad-hoc/other-routine use. `search_vault.py` keeps the filesystem-mode basic-DQL + text search (sufficient for the jobsearch pipeline queries — no Dataview-API features are used by any consumer).

Keep the load-bearing gotchas: manual double-quoted YAML (never PyYAML), exact emoji enum strings, **APFS case-insensitive collision check before create**, the `tache` enum is `Pas commencée`/`Today`/`En cours`/`Terminé`/`Archivé` (closed = `Terminé`/`Archivé`).

## Config — no secret, nothing to gitignore

Filesystem-only means **no API key anywhere**. The skill only needs the **vault folder path** (not a secret). Resolution order:

1. **`OBSIDIAN_VAULT_PATH`** env var (required in Cowork, where the vault is mounted at a session path).
2. Fallback to the known macOS path: `/Users/renaud/Library/CloudStorage/SynologyDrive-MyAssistant/SecondLife-vault/SecondLife`.
3. Optional last-resort: read `vault_path` from `~/.claude/skills/obsidian-crm/scripts/config.json` if present.

No `config.local.json`, no secret, no `.gitignore` change needed. (This is the main simplification vs the first draft of this brief.)

## Modifications to the 3 consumer skills (this sprint, after the primitive is built + verified)

**Option A everywhere — the change is the same shape for all three**: in `allowed-tools`, swap `Skill(obsidian-crm)` → `Skill(jobsearch-vault)`; in the instructions, change "invoke `obsidian-crm`" → "invoke `jobsearch-vault`". **No script paths, no PLUGIN_DIR resolver, no cross-plugin path-hunting** — the `Skill` tool locates the skill (it is loaded in-session in Cowork, and installed in CLI). The structured request (exact fields for writes) is what each caller passes; `jobsearch-vault` runs the scripts internally.

### A. `log-application` (`plugins/jobsearch/skills/log-application/SKILL.md`)
- **`allowed-tools`**: `Skill(obsidian-crm)` → `Skill(jobsearch-vault)`.
- **Instructions**: every "compose the global `obsidian-crm` skill" / hardcoded `~/.claude/skills/obsidian-crm/scripts/…` becomes "invoke `jobsearch-vault`" with the same structured create/update/search request (Step 3 idempotency search, Step 3 create, Step 4 relance create). Same payloads, same idempotency, same exit-code contract — only the addressee changes.

### B. `interview-prep` (`plugins/jobsearch/skills/interview-prep/SKILL.md`)
- **`allowed-tools`**: `Skill(obsidian-crm)` → `Skill(jobsearch-vault)`; keep `Read` (for `profiles/`, still read from the plugin source tree).
- **Instructions**: candidature lookup (Step 1) + `entretien` create (Step 4) go through `jobsearch-vault` instead of `obsidian-crm`.
- **Simplify the Step 4 note**: the bundled `note_schemas` already accepts `categorie`/`interlocuteurs`, so the "expected unknown-field warning" paragraph (added 2026-06-12) can be removed — those warnings no longer fire. Keep only the generic "non-zero result → fail, don't fire the success report" rule.

### C. `morning-briefing` (`plugins/briefing/skills/morning-briefing/SKILL.md`)
- **The smallest change of the three — it already uses Option A.** Step 0 probe + Step 1c just swap the word `obsidian-crm` → `jobsearch-vault` ("invoke `jobsearch-vault` and ask it for upcoming interviews / relances due / active candidatures"). READ-ONLY.
- **`allowed-tools`**: `Skill(obsidian-crm)` → `Skill(jobsearch-vault)`; keep the hal-mcp + Google Calendar tools.
- **Loud failure preserved**: if `jobsearch-vault` is unavailable/errors, the existing AC3 contract still fires — `⚠️ jobsearch DOWN — <reason>` in the section + footer, never a silent empty. (No resolver needed — the `Skill` invocation simply fails and is caught by the existing probe/degradation logic.)

## Data — no migration, zero-risk cutover

The jobsearch data **stays in the same vault, same folders, same schemas**. The new skill reads/writes the exact same `.md` files `obsidian-crm` does — both can coexist on the same data. No migration, no backfill — only the *code path* changes. The 2 real candidatures + preps logged during the Loop 4 smoke test (Anthropic P1, Yotta P4) remain valid and readable by the new skill.

## Versioning (4-field sync rule — strict)

Two plugins change:
- **`jobsearch`: 0.3.0 → 0.4.0** (MINOR — new skill + re-pointed consumers). Sync all 4: `marketplace.json` top-level, `plugins[].jobsearch.version`, `plugins/jobsearch/.claude-plugin/plugin.json`, and `version:` in each touched SKILL.md (`jobsearch-vault`, `log-application`, `interview-prep`). Register `jobsearch-vault` in `marketplace.json` `plugins.jobsearch.skills`. CHANGELOG `[0.4.0]`.
- **`briefing`: 0.1.0 → 0.2.0** (MINOR — re-pointed `morning-briefing`). Sync its 4 fields + CHANGELOG `[0.2.0]`. Per repo rule, bump `marketplace.json` top-level to the latest-changed plugin.

## Acceptance criteria

1. `jobsearch-vault` does create / read / update / search / list on all 5 jobsearch note types, **filesystem-only**, **pure stdlib** (no pip install), **no network**, **no API key**.
2. Creating an `entretien` with `categorie` + `interlocuteurs` produces **zero** validation warnings (the fix is bundled).
3. Renaud can **invoke `jobsearch-vault` directly** (its triggers fire: e.g. "pipeline candidatures", "liste mes entretiens") AND the other skills call its scripts as a library.
4. `log-application`, `interview-prep`, `morning-briefing` run end-to-end composing **only** `jobsearch-vault` (no `obsidian-crm` in their `allowed-tools`); re-running the Loop 4 AC1/AC2/AC3 live smoke tests against the real vault — all pass.
5. `obsidian-crm` is byte-for-byte unchanged; the global skill still works independently.
6. No secret/credential of any kind in the skill or repo (filesystem-only — there is none to leak).

## Open decisions

- **None.** Name = `jobsearch-vault` (locked). Filesystem-only (no secret-key question). Composition = Option A, invoke via the `Skill` tool (no path resolver). All majors settled — the brief is implementation-ready.

## Suggested phasing

1. Build `jobsearch-vault` (filesystem-only scripts + trimmed schemas + SKILL.md with user triggers + vault-path resolution). Run `note_schemas.py` self-test + a manual CRUD smoke on each of the 5 types.
2. Re-point the 3 consumers (section above), bump versions (4-field sync), update CHANGELOGs.
3. Re-run the Loop 4 live smoke tests (AC1/AC2/AC3) to confirm parity, then merge.
