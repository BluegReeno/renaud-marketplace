---
name: jobsearch-vault
description: >
  Primitive read/write access to the Job-Search slice of Renaud's Obsidian vault
  (`CRM-JobSearch/` + jobsearch-tagged `Taches/`), FILESYSTEM-ONLY (no network,
  no API key). Owns five note types: `opportunite-js` (candidature),
  `entreprise-js` (company), `contact-js` (contact), `entretien` (interview prep
  + compte-rendu), and jobsearch `tache` (relances). Exposes create / read /
  update / search / list as plain-stdlib CLI scripts. Use directly when Renaud
  asks to explore the job-search pipeline — "pipeline candidatures", "liste mes
  entretiens", "cherche dans mes candidatures", "mes relances jobsearch",
  "search my applications", "show my interviews", "mes candidatures actives" — and
  use as a shared library invoked by `log-application`, `interview-prep`, and
  `morning-briefing`.
allowed-tools: "Bash Read"
---

# Job-Search Vault — Skill Instructions

## What this skill does

This skill owns the **job-search vault I/O** for renaud-marketplace. It reads and
writes Obsidian Markdown notes **directly on the filesystem** — there is no REST
API, no server, no API key, and no network access of any kind. Editing local
`.md` files needs none of that; if Obsidian is open it auto-reloads externally
changed files.

It is **two things at once**:

1. An **invocable skill** — Renaud can ask it to explore or mutate the job-search
   pipeline (triggers in the frontmatter `description`).
2. A **shared script library** — `log-application`, `interview-prep` and
   `morning-briefing` invoke this skill (via the `Skill` tool) and it runs the
   scripts below internally with the exact payload they pass.

It does **not** touch Blue Green CRM, project/sprint notes, or any `*-bg` type —
those stay in the global `obsidian-crm` skill.

## Note types owned (the only 5)

| Type | Folder | Role |
|------|--------|------|
| `opportunite-js` | `CRM-JobSearch/Opportunites/` | candidature |
| `entreprise-js` | `CRM-JobSearch/Entreprises/` | company |
| `contact-js` | `CRM-JobSearch/Contacts/` | contact |
| `entretien` | `CRM-JobSearch/Entretiens/` | interview (prep + compte-rendu) |
| `tache` | `Taches/` | **jobsearch relances only** (`etiquettes` contains `"jobsearch"`) |

`note_schemas.py` validates fields per type. `entretien` natively accepts
`categorie` (enum `Préparation` / `Compte-rendu`) and `interlocuteurs` (list) —
creating a fully-specified interview note raises **zero** validation warnings.

## Step 1 — Locate this skill's scripts (self-resolver)

The scripts ship inside this skill. Resolve their directory once per session,
covering dev, marketplace cache, and Cowork sandbox. (This is *self-location* of
the skill's own bundled scripts — it is NOT cross-plugin path-hunting. Callers
reach this skill via the `Skill` tool and never resolve a path.)

```bash
SCRIPTS=$(python3 - <<'PYEOF'
import os, pathlib, sys, glob as _glob
def log(msg): print(msg, file=sys.stderr)
home = pathlib.Path.home()
sentinel = ('scripts', 'create_note.py')

# 1. Env override (dev)
env = os.environ.get('JOBSEARCH_VAULT_DIR', '')
if env and pathlib.Path(env, *sentinel).exists():
    print(str(pathlib.Path(env, 'scripts'))); sys.exit(0)

# 2. Claude Code marketplace cache
for mkt in ['renaud-marketplace', 'bluegreen-marketplace']:
    cache_root = home / '.claude' / 'plugins' / 'cache' / mkt / 'jobsearch'
    if cache_root.exists():
        cand = sorted(
            cache_root.glob('*/skills/jobsearch-vault/scripts/create_note.py'),
            key=lambda p: p.stat().st_mtime, reverse=True)
        if cand:
            print(str(cand[0].parent)); sys.exit(0)

# 3. Cowork sandbox
for pat in ['/sessions/*/mnt/.remote-plugins/*/skills/jobsearch-vault/scripts/create_note.py']:
    matches = sorted(_glob.glob(pat), key=os.path.getmtime, reverse=True)
    if matches:
        print(os.path.dirname(matches[0])); sys.exit(0)

# 4. Known dev paths
for dev in [
    home / 'Projects' / 'renaud-marketplace' / 'plugins' / 'jobsearch' / 'skills' / 'jobsearch-vault',
    home / 'Projects' / 'bluegreen-marketplace' / 'plugins' / 'jobsearch' / 'skills' / 'jobsearch-vault',
]:
    if dev.joinpath(*sentinel).exists():
        print(str(dev / 'scripts')); sys.exit(0)

print('SCRIPTS_NOT_FOUND')
PYEOF
)
if [ "$SCRIPTS" = "SCRIPTS_NOT_FOUND" ] || [ -z "$SCRIPTS" ]; then
  echo "ERROR: jobsearch-vault scripts not found. Set JOBSEARCH_VAULT_DIR=<skill dir> or install from marketplace." >&2
  exit 1
fi
```

Run every script as `python3 "$SCRIPTS/<script>.py"`. The scripts import each
other by relative module name, so always invoke them from their own directory or
with `$SCRIPTS` on the path (running `python3 "$SCRIPTS/foo.py"` already puts
`$SCRIPTS` first on `sys.path`, so the imports resolve).

## Step 2 — Vault path resolution (no secret)

The scripts resolve the vault folder themselves, in this order:

1. **`OBSIDIAN_VAULT_PATH`** env var (set this in Cowork, where the vault is
   mounted at a session path).
2. Known macOS path `…/SecondLife-vault/SecondLife`.
3. Last resort: `vault_path` from `~/.claude/skills/obsidian-crm/scripts/config.json`
   (only the path is read — never any key).

There is no API key and nothing to gitignore. If none resolves, the scripts fail
loudly naming the path they tried.

## Step 3 — The five operations

### create_note.py — create a note (stdin JSON)

```bash
echo '{
  "name":"<Title>",
  "type":"opportunite-js",
  "folder":"CRM-JobSearch/Opportunites",
  "fields":{ "statut":"✉️ Candidature envoyée", "entreprise":"[[Anthropic]]" },
  "body":"## Annonce\n\n<text>\n"
}' | python3 "$SCRIPTS/create_note.py"
```
- Prints `{"created": "<path>"}` on success (exit 0).
- Schema warnings go to **stderr** but do not fail (exit 0). Errors fail (exit 1).
- **Refuses to overwrite** an existing note (APFS case-insensitive collision
  check) → exit 1 `note already exists`. This is the idempotency guard.

### read_note.py — read one note

```bash
python3 "$SCRIPTS/read_note.py" "CRM-JobSearch/Opportunites/<Title>.md"        # parsed JSON
python3 "$SCRIPTS/read_note.py" "CRM-JobSearch/Entretiens/<Title>.md" --raw    # raw markdown
```

### update_frontmatter.py — set one field

```bash
python3 "$SCRIPTS/update_frontmatter.py" "<path>.md" statut "❌ Refus"
python3 "$SCRIPTS/update_frontmatter.py" "<path>.md" echeance "2026-06-26"
python3 "$SCRIPTS/update_frontmatter.py" "<path>.md" etiquettes --json-value '["jobsearch"]'
```
Validates the new value against the note's `type`. Reads back the written value.

### search_vault.py — full-text or basic DQL

```bash
python3 "$SCRIPTS/search_vault.py" "Anthropic" --limit 10
python3 "$SCRIPTS/search_vault.py" --dql 'TABLE statut, entreprise FROM "CRM-JobSearch/Opportunites" WHERE statut != "❌ Refus" SORT date_candidature DESC'
```
DQL supports `TABLE … FROM "folder" [WHERE field =/!=/contains(...) [AND …]] [SORT field ASC|DESC]`.

### list_notes.py — list a folder, optionally filtered

```bash
python3 "$SCRIPTS/list_notes.py" "CRM-JobSearch/Opportunites"
python3 "$SCRIPTS/list_notes.py" "CRM-JobSearch/Opportunites" --field statut --value "✉️ Candidature envoyée"
python3 "$SCRIPTS/list_notes.py" "Taches" --field etiquettes --value "jobsearch" --limit 20
```
For list-valued fields (e.g. `etiquettes`), `--value` matches membership.

## Step 4 — Common read recipes for callers

- **Active candidatures** → `list_notes.py "CRM-JobSearch/Opportunites"`, exclude
  `statut` in `❌ Refus` / `✅ Offre reçue` client-side, or DQL with
  `WHERE statut != "❌ Refus"`.
- **Upcoming interviews** → `list_notes.py "CRM-JobSearch/Entretiens"` and filter
  `date` within the window client-side (filesystem DQL has no date math).
- **Relances due** → `list_notes.py "Taches" --field etiquettes --value "jobsearch"`,
  then keep open `etat` (`Pas commencée` / `Today` / `En cours`) with
  `echeance <= today`.

## Step 5 — Constraints (load-bearing)

- **Filesystem-only.** No network, no API key, pure stdlib. Never add a REST path.
- **Manual YAML, never PyYAML.** Frontmatter is serialized by hand to preserve
  Obsidian's exact formatting and emoji enums.
- **Emoji enums are verbatim.** `statut` values (`✉️ Candidature envoyée`,
  `📞 Entretien prévu`, `❌ Refus`, …) and accents must be passed exactly —
  re-typing an emoji loses the variation selector and fails validation.
- **Wikilinks** are `"[[Note Title]]"`; the task's `opportunite` mirrors the
  candidature title exactly (em-dash ` — ` with spaces).
- **`tache` enum** is `Pas commencée` / `Today` / `En cours` / `Terminé` /
  `Archivé` (closed = `Terminé` / `Archivé`). Not `Terminée` / `Annulée`.
- **`entretien` `categorie`** is `Préparation` or `Compte-rendu` (verbatim).
- **Idempotent create.** Re-creating an existing note fails (exit 1). Callers that
  need re-apply semantics must search first and switch to `update_frontmatter.py`.
- **`target_profile` on `opportunite-js` warns** (non-blocking, exit 0) — it is an
  accepted extra field log-application writes, kept as the documented escape hatch.
