---
name: jobsearch-vault
description: >
  Primitive read/write access to the Job-Search slice of Renaud's Obsidian vault
  (`CRM-JobSearch/` + jobsearch-tagged `Taches/`), FILESYSTEM-ONLY (no network,
  no API key). Owns five note types: `opportunite-js` (candidature),
  `entreprise-js` (company), `contact-js` (contact), `entretien` (interview prep
  + compte-rendu), and jobsearch `tache` (relances). Exposes create / read /
  update / upsert-section / search / list as plain-stdlib CLI scripts. Use directly when Renaud
  asks to explore the job-search pipeline — "pipeline candidatures", "liste mes
  entretiens", "cherche dans mes candidatures", "mes relances jobsearch",
  "search my applications", "show my interviews", "mes candidatures actives" — and
  use as a shared library invoked by `log-application`, `interview-prep`, and
  `morning-briefing`.
allowed-tools: "Bash Read mcp__remote-devices__device_bash"
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

Judge which of three cases applies to this session — this is an agent-level
judgment call, never a shell `if`: no bash command can test whether an MCP tool
is available to the current session.

- **`mcp__remote-devices__device_bash` is available** (a cloud session linked to
  Renaud's Mac via the desktop app — it sits next to `device_list_dir`,
  `device_stage_files`, `device_commit_files`) → **Case A** below: a self-contained
  reader sent in the command. Read-only (list / read / search).
- **Otherwise** → **Case B**, the local self-resolver (unchanged): plain `Bash`,
  because this is Cowork running directly on the Mac and the vault is mounted
  locally. Full read/write.
- **Neither reaches the vault** (Case A exits `VAULT_NOT_FOUND`, or Case B's
  resolver prints `SCRIPTS_NOT_FOUND`) → Case C. Never skip the vault silently.

### Case A — `device_bash` (cloud session, Mac linked remotely)

`device_bash` executes on the physical Mac, not in the cloud sandbox — the plugin's own scripts
(cloud-side, under `~/.claude/plugins/...`) are **not reachable from there**, and nothing is
installed on the Mac for this case. The reader below is therefore **sent whole, in the command
itself**: a stdlib-only Python script passed as a heredoc. There is no copy to keep in sync and no
version to compare.

Every `device_bash` call is a fresh shell — nothing, including env vars, persists between calls.
Each call carries the full script. Read-only: `list`, `read`, `search`. A caller that needs a write
(`create_note.py`, `update_frontmatter.py`, `upsert_section.py`) in a `device_bash`-only session
cannot be served from here — writes to the Synology File Provider are not atomic and can collide
with Obsidian or the sync. Say so; for a jobsearch task, write it in hal instead.

The vault is found by the script itself: `OBSIDIAN_VAULT_PATH` if set, otherwise the first
`~/mnt/*/SecondLife-vault/SecondLife` (or `~/mnt/*/*/SecondLife`). None → it exits with
`VAULT_NOT_FOUND`, which is Case C below.

Replace the first line's arguments with the operation:

| Operation | First line |
|---|---|
| list a folder (optionally filtered on one field) | `python3 - list "CRM-JobSearch/Opportunites" 500 [<field> <value>] <<'PY'` |
| read one note (parsed, or `--raw` markdown) | `python3 - read "CRM-JobSearch/Opportunites/<Title>.md" [--raw] <<'PY'` |
| full-text search (default root `CRM-JobSearch`) | `python3 - search "<text>" [<limit>] [<root>...] <<'PY'` |

```bash
python3 - list "CRM-JobSearch/Opportunites" 500 <<'PY'
import sys, os, re, json, glob, unicodedata, time
from pathlib import Path
# list <folder> [limit] [field value] | read <path> [--raw] | search <query> [limit] [root...]
V = os.environ.get("OBSIDIAN_VAULT_PATH") or next(iter(sorted(glob.glob(os.path.expanduser("~/mnt/*/SecondLife-vault/SecondLife")) + glob.glob(os.path.expanduser("~/mnt/*/*/SecondLife")))), "")
if not os.path.isdir(V): sys.exit("VAULT_NOT_FOUND (no ~/mnt/*/SecondLife-vault/SecondLife)")
V = Path(V); N = lambda s: unicodedata.normalize("NFC", s)
def scalar(s):
    if not s: return None
    if len(s) > 1 and s[0] == s[-1] and s[0] in "\"'": return s[1:-1].replace('\\"', '"').replace("\\'", "'")
    if s.lower() in ("true", "false"): return s.lower() == "true"
    if s.lower() == "null": return None
    try: return float(s) if "." in s else int(s)
    except ValueError: return s
def split_inline(s):
    out, cur, q = [], "", None
    for c in s:
        if q is None and c in "\"'": q = c
        elif c == q: q = None
        if c == "," and q is None: out.append(cur.strip()); cur = ""
        else: cur += c
    if cur.strip(): out.append(cur.strip())
    return out
def parse(fm):
    r, L, i = {}, fm.split("\n"), 0
    while i < len(L):
        m = re.match(r'^([A-Za-z_][\w_-]*)\s*:\s*(.*)', L[i]); i += 1
        if not m: continue
        k, v = m.group(1), m.group(2).strip()
        if v in ("", "|"):
            items, blk = [], []
            while i < len(L) and L[i].startswith("  "):
                t = L[i].strip(); i += 1; blk.append(t)
                if t.startswith("- "): items.append(scalar(t[2:].strip()))
            r[k] = items or ("\n".join(blk) if v == "|" and blk else None)
        elif v.startswith("[") and v.endswith("]"):
            r[k] = [scalar(x.strip()) for x in split_inline(v[1:-1])]
        else: r[k] = scalar(v)
    return r
def rt(fp, n=4):  # Synology/File Provider can throw EDEADLK (35): retry a few times
    for i in range(n):
        try: return fp.read_text(encoding="utf-8")
        except OSError as ex:
            if ex.errno not in (11, 35) or i == n - 1: raise
            time.sleep(0.3 * (i + 1))
def read(rel):
    t = rt(V / N(rel))
    fm, body = "", t
    if t.startswith("---") and t.find("\n---", 3) != -1:
        e = t.find("\n---", 3); fm, body = t[4:e], t[e+4:]
        if body.startswith("\n"): body = body[1:]
    return parse(fm), body
cmd, a = sys.argv[1], sys.argv[2:]
if cmd == "list":
    folder, lim = a[0], int(a[1]) if len(a) > 1 else 50
    fld, val = (a[2], a[3]) if len(a) > 3 else (None, None)
    files = sorted(f.name for f in (V / N(folder)).iterdir() if f.suffix == ".md")
    res, bad = [], []
    for f in files:
        if len(res) >= lim: break
        p = f"{folder}/{f}"
        try: fm, _ = read(p)
        except Exception as ex: bad.append(f"{p}: {type(ex).__name__}: {ex}"); continue
        if fld:
            x = fm.get(fld)
            if x is None or (val not in x if isinstance(x, list) else str(x) != val): continue
        res.append({"path": p, "frontmatter": fm})
    print(json.dumps(res, ensure_ascii=False, indent=2))
    print(f"# {len(res)} notes returned (of {len(files)} in folder), {len(bad)} unreadable", file=sys.stderr)
    for b in bad[:5]: print("# UNREADABLE " + b, file=sys.stderr)
elif cmd == "read":
    if "--raw" in a: print((V / N(a[0])).read_text(encoding="utf-8"))
    else:
        fm, body = read(a[0]); print(json.dumps({"frontmatter": fm, "content": body, "path": a[0]}, ensure_ascii=False, indent=2))
elif cmd == "search":
    q, lim, out, bad = a[0].lower(), int(a[1]) if len(a) > 1 else 20, [], []
    roots = [V / r for r in (a[2:] or ["CRM-JobSearch"])]
    for fp in (f for r in roots if r.is_dir() for f in r.rglob("*.md")):
        rel = fp.relative_to(V)
        if any(p.startswith(".") for p in rel.parts): continue
        try: t = rt(fp, 1)
        except Exception as ex: bad.append(f"{rel}: {type(ex).__name__}: {ex}"); continue
        tl = t.lower(); pos = tl.find(q)
        if pos < 0: continue
        out.append({"filename": str(rel), "score": min(tl.count(q), 5), "first_match": t[max(0, pos-100):pos+len(q)+100][:300]})
    out.sort(key=lambda r: -r["score"]); print(json.dumps(out[:lim], ensure_ascii=False, indent=2))
    print(f"# {len(bad)} unreadable", file=sys.stderr)
    for b in bad[:5]: print("# UNREADABLE " + b, file=sys.stderr)
PY
```

Output is the same JSON shape as `list_notes.py` / `read_note.py` / `search_vault.py` (Case B). The
one difference: a `|` block scalar comes back as its text, where the plugin parser returns `"|"`.

**Unreadable files are counted, never hidden.** On the Mac, Synology's File Provider refuses some
files that are not materialised locally (`Resource deadlock avoided`, errno 35). Measured
2026-10-21 over the real vault: `CRM-JobSearch` 0 unreadable of 407; `Taches`, `Projets`,
`Sprints`, `_config` 100 % unreadable; `CRM-BlueGreen` 665 of 666. Hence:

- every call prints on stderr `# N unreadable` and the first five paths with their error — a
  non-zero count is a degraded read, and the caller says so;
- `list` and `read` retry a locked file three times (0.3 s, 0.6 s, 0.9 s); `search` does not — with
  retries a search crossed the 120 s `device_bash` timeout, without it ran in 0.3 s;
- `search` covers `CRM-JobSearch` by default; jobsearch tasks (`Taches/`) are read with hal's
  `list_tasks`, never through this reader.

### Case B — local `Bash` self-resolver (unchanged)

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

# 3. Cowork sandbox — both layouts: the mounted .remote-plugins tree and the synced/ tree
for pat in ['/sessions/*/mnt/.remote-plugins/*/skills/jobsearch-vault/scripts/create_note.py',
            str(home / '.claude/plugins/synced/*/jobsearch/skills/jobsearch-vault/scripts/create_note.py')]:
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

### Case C — the vault is not read

Two different situations, and the caller must render them differently — never one vague line:

- **Not mounted** — Case A exited `VAULT_NOT_FOUND` (no linked device, or the Synology folder is
  not mounted on it), or Case B printed `SCRIPTS_NOT_FOUND`: `⚠️ vault non monté — <which case,
  what it printed>`.
- **Mounted but not read** — the vault was found but the call failed (non-zero exit, a Python
  error, a `device_bash` timeout), or `list` returned unreadable files in `CRM-JobSearch`:
  `⚠️ vault monté mais illisible — <the error or the stderr count, verbatim>`.

Continue the rest of the run either way — this mirrors the DOWN-source contract (never omit a
source silently, see `morning-briefing` Step 0/Step 5).

## Step 2 — Vault path resolution (no secret)

The scripts resolve the vault folder themselves, in this order:

1. **`OBSIDIAN_VAULT_PATH`** env var (set this in Cowork, where the vault is
   mounted at a session path). Case A's reader finds the vault by itself.
2. Known macOS path `…/SecondLife-vault/SecondLife`.
3. Last resort: `vault_path` from `~/.claude/skills/obsidian-crm/scripts/config.json`
   (only the path is read — never any key).

There is no API key and nothing to gitignore. If none resolves, the scripts fail
loudly naming the path they tried.

## Step 3 — The six operations

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

### upsert_section.py — idempotently add a bullet line to a body section

```bash
python3 "$SCRIPTS/upsert_section.py" "CRM-JobSearch/Opportunites/<Poste> — <Entreprise>.md" \
  --heading "🏢 BANT (agrégé)" \
  --subheading "B — Comp/Budget" \
  --line "- 2026-09-15 — Deon van der Vyver (CTO) : « fourchette 70-85k » → [[CR Cognyx — Deon van der Vyver — 15-09-2026]]"
```
- Creates the `## heading` (and `### subheading`, if given) when missing; otherwise appends under the existing one.
- **Dedup is exact-string only** — a line identical (stripped) to one already in the same block is skipped, never duplicated. A contradicting entry (different date, different quote) is a *different* line and is appended alongside the existing one, never overwriting it.
- Body-only. It never touches frontmatter, and it never reorders or rewrites existing lines — pure append.
- A line appended after prose, a table or a `---` rule is preceded by a blank line, so it cannot be read as part of that block; after a bullet it continues the list.
- Prints `{"path": ..., "heading": ..., "subheading": ...}` on success (exit 0). Errors fail (exit 1).
- Used by `log-cr` to aggregate a company's BANT onto its `opportunite-js` note instead of duplicating it in every `entretien` CR (issue #138).
- Used by `interview-prep` and `log-cr` to list each prep and CR in the `opportunite-js`'s `## Entretiens` section, so the candidature links back to its interviews (issue #119). The line format is fixed — `- <YYYY-MM-DD> — <Prep|CR> — [[<entretien note name>]]` — because dedup is exact-string.

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

### migrate_legacy_statuts.py — one-shot maintenance (not a caller-facing operation)

```bash
python3 "$SCRIPTS/migrate_legacy_statuts.py"            # dry run
python3 "$SCRIPTS/migrate_legacy_statuts.py" --apply    # rewrite the notes
```
Rewrites `opportunite-js` notes still carrying a pre-#127 statut value
(`❌ Sans suite (mort)`, `❌ Abandonné`, `⏳ Relance envoyée — en attente`) to
their canonical replacement (`JS_STATUTS_LEGACY_ALIASES` in `note_schemas.py`).
Run manually, once, against the vault — not invoked by any other skill.

### backfill_entretien_links.py — one-shot maintenance (not a caller-facing operation)

```bash
python3 "$SCRIPTS/backfill_entretien_links.py"            # dry run
python3 "$SCRIPTS/backfill_entretien_links.py" --apply    # write the sections
```
Rebuilds the `## Entretiens` section of every `opportunite-js` from the
`opportunite` / `opportunite_secondaire` frontmatter of the `entretien` notes
written before `interview-prep` and `log-cr` linked back themselves (#119).
Chronological; on the same day, prep before CR; undated notes last. Writes
through `upsert_section`, in the same line format, so a re-run is a no-op and a
later skill run is deduplicated. A note the section already links in another
wording (hand-written line, table row) is skipped. Links that resolve to no
opportunité are reported on stderr, never created.

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
  `📞 Entretien prévu`, `❌ Refus`, `🗄️ Sans suite`, `⛔ Abandonné`, …) and
  accents must be passed exactly — re-typing an emoji loses the variation
  selector and fails validation. `🗄️ Sans suite` is for a dead application
  (no reply, closed at the daily relance clean-up); `⛔ Abandonné` is for an
  offer Renaud drops before ever sending — see `JS_STATUTS` in
  `note_schemas.py` for the full enum.
- **Wikilinks** are `"[[Note Title]]"`; the task's `opportunite` mirrors the
  candidature title exactly (em-dash ` — ` with spaces).
- **`tache` enum** is `Pas commencée` / `Today` / `En cours` / `Terminé` /
  `Archivé` (closed = `Terminé` / `Archivé`). Not `Terminée` / `Annulée`.
- **`entretien` `categorie`** is `Préparation` or `Compte-rendu` (verbatim).
- **Idempotent create.** Re-creating an existing note fails (exit 1). Callers that
  need re-apply semantics must search first and switch to `update_frontmatter.py`.
- **`target_profile` on `opportunite-js` warns** (non-blocking, exit 0) — it is an
  accepted extra field log-application writes, kept as the documented escape hatch.
