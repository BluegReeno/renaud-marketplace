---
name: interview-prep
description: >
  Given a candidature (Obsidian `opportunite-js` note), produce one
  `entretien` note with `categorie: "Préparation"` whose body always has the
  same 5 H2 sections in the same order: Société · Résumé de la job description ·
  Pitch · Cas du parcours pertinents · Questions probables de l'interlocuteur.
  The Pitch is positioned for the candidature's declared `target_profile` (P1–P5)
  using the matching `plugins/jobsearch/profiles/p<n>_*.md` narrative rules, so
  every interview presents one coherent profile. Use when the user says
  "prépare l'entretien", "interview prep", "préparation entretien", "je passe un
  entretien avec", "prep <company>", "interview avec".
version: 0.4.2
allowed-tools: "Skill(jobsearch-vault) Read mcp__hal-mcp__list_tasks mcp__hal-mcp__create_task"
---

# Interview Prep — Skill Instructions

## What this skill does

Given a candidature (resolved by company name + role title, or a free-text reference), produce one Obsidian `entretien` note with `categorie: "Préparation"` in `CRM-JobSearch/Entretiens/`. The body is ALWAYS the same five H2 sections, in this exact order:

1. **Société**
2. **Résumé de la job description**
3. **Pitch** (profile-positioned for the candidature's `target_profile`)
4. **Cas du parcours pertinents**
5. **Questions probables de l'interlocuteur**

The Pitch section is grounded in the matching `profiles/p<n>_*.md` narrative file — concrete proofs, not generic claims. All vault I/O goes through the `jobsearch-vault` skill; the profile narrative files (which live in this plugin's source tree, NOT in the Obsidian vault) are read with the standard `Read` tool.

## Step 0 — Inputs you need from the user

Collect (and confirm) the following before doing anything else:

1. **Candidature reference** (required) — free text like "the Relief CTO one" or "Anthropic Applied AI". The skill searches by `entreprise` + `poste` in `CRM-JobSearch/Opportunites/`.
2. **Interview date** — default: tomorrow. Format `YYYY-MM-DD` for frontmatter; `DD-MM-YYYY` for the filename suffix.
3. **`type_entretien`** — default `"RH"`. One of `RH` / `Technique` / `Manager` / `Final` (drives the question set in Step 3, section 5).
4. **`interlocuteurs`** — default `["TBD"]`. Free-text list of names.

Do not proceed until the candidature is unambiguously identified.

## Step 1 — Locate the candidature (via `jobsearch-vault`)

Invoke `jobsearch-vault` to search `CRM-JobSearch/Opportunites/` by `entreprise` + `poste` text match, then read the matching note. Capture:

- `frontmatter.target_profile` — one of `"P1"` / `"P2"` / `"P3"` / `"P4"` / `"P5"`.
- `frontmatter.entreprise` — the company wikilink.
- `frontmatter.lien_offre` — optional URL.
- `frontmatter.source` — for context.
- `body` — the pasted offer (used for the JD summary in section 2).

**If `target_profile` is missing** (legacy candidature filed before `log-application` existed): ASK the user which P1–P5 to use. Show the P1–P5 short labels (Architect / Lead / CTO / CS-FDE / Sales). DO NOT silently default. Once chosen, optionally ask `jobsearch-vault` to update the candidature (`update_frontmatter`) to persist the answer back onto the candidature so the next prep finds it.

**If the candidature does not exist** (search returns nothing): return a clear error pointing the user at `/log-application` first. Do NOT create the `entretien` note with a broken wikilink — that pollutes the vault.

## Step 2 — Read the matching profile narrative

Read the file `profiles/p<n>_*.md` from this plugin's source tree, where `<n>` is the digit from `target_profile` (e.g. `P3` → `profiles/p3_cto.md`).

These files live in the **plugin source tree**, NOT in the Obsidian vault — that is why `Read` is allow-listed alongside `Skill(jobsearch-vault)`. Use the PLUGIN_DIR resolver to locate `profiles/` in any environment (dev workstation, marketplace cache, Cowork sandbox):

```bash
PLUGIN_DIR=$(python3 - <<'PYEOF'
import os, pathlib, sys, glob as _glob
def log(msg): print(msg, file=sys.stderr)
home = pathlib.Path.home()
env = os.environ.get('JOBSEARCH_PLUGIN_DIR', '')
if env:
    if pathlib.Path(env, 'profiles', 'p1_architecte.md').exists():
        log(f"[plugin-dir] env JOBSEARCH_PLUGIN_DIR={env} ACCEPTED")
        print(env); sys.exit(0)
    log(f"[plugin-dir] env JOBSEARCH_PLUGIN_DIR={env} REJECTED (no profiles/p1_architecte.md) — falling through")
cache_root = home / '.claude' / 'plugins' / 'cache' / 'renaud-marketplace' / 'jobsearch'
if cache_root.exists():
    candidates = sorted(cache_root.glob('*/profiles/p1_architecte.md'), key=lambda p: p.stat().st_mtime, reverse=True)
    if candidates:
        plug = str(candidates[0].parent.parent)
        log(f"[plugin-dir] marketplace cache ACCEPTED {plug}")
        print(plug); sys.exit(0)
    log(f"[plugin-dir] marketplace cache {cache_root} exists but no profiles match — falling through")
else:
    log(f"[plugin-dir] marketplace cache {cache_root} missing — falling through")
for pat in ['/sessions/*/mnt/.remote-plugins/*/profiles/p1_architecte.md']:
    matches = sorted(_glob.glob(pat), key=os.path.getmtime, reverse=True)
    if matches:
        plug = os.path.dirname(os.path.dirname(matches[0]))
        log(f"[plugin-dir] Cowork sandbox ACCEPTED {plug}")
        print(plug); sys.exit(0)
log("[plugin-dir] Cowork sandbox no match — falling through")
dev = home / 'Projects' / 'renaud-marketplace' / 'plugins' / 'jobsearch'
if dev.joinpath('profiles', 'p1_architecte.md').exists():
    log(f"[plugin-dir] dev path ACCEPTED {dev}")
    print(str(dev)); sys.exit(0)
log(f"[plugin-dir] dev path {dev} no match — no resolver tier matched")
print('PLUGIN_DIR_NOT_FOUND')
PYEOF
)
if [ -z "$PLUGIN_DIR" ]; then
  echo "ERROR: PLUGIN_DIR resolver returned empty output. Check 'which python3' — the heredoc may have failed to execute (missing interpreter or shell syntax error)." >&2
  exit 1
fi
if [ "$PLUGIN_DIR" = "PLUGIN_DIR_NOT_FOUND" ]; then
  echo "ERROR: jobsearch plugin not found. Set JOBSEARCH_PLUGIN_DIR=<path> or install from marketplace." >&2
  exit 1
fi
```

Then `Read "$PLUGIN_DIR/profiles/p<n>_<label>.md"` (e.g. `p3_cto.md`). Quote — don't paraphrase — the load-bearing claims under the file's "Narrative rules" and "Key differentiators" H2s.

## Step 3 — Compose the 5 sections (always identical structure)

The body of the `entretien` note MUST contain these five H2 headings, in this exact order, with these exact strings (the agent writes the actual content underneath in French):

### 1. Société

Pull from an `entreprise-js` note if `jobsearch-vault` finds one linked to `frontmatter.entreprise`; otherwise summarize from the offer body. 3–5 bullets max: what they do, size/stage, why this role exists now, anything from the offer that signals culture.

### 2. Résumé de la job description

5 bullets distilled from the offer body, in this rough order: scope, stack, seniority, mission, success criteria.

### 3. Pitch (P<n>)

(Positioned for the candidature's `target_profile` — the H2 heading written into the entretien note is the literal string `## 3. Pitch (P<n>)`, matching the Step 4 JSON payload and the Step 6 constraint. Do NOT write `## 3. Pitch (positionné P<n>)` — that drifts from the contract.)

A 3-paragraph pitch grounded in the `profiles/p<n>_*.md` file just read in Step 2. The pitch MUST cite concrete proofs from the profile file, quoted (not paraphrased), not generic claims. Examples of load-bearing claims by profile:

- **P1** — Lead on "Blue Green first (EnBW/Valorem + BWC in prod) → Open Ocean (SaaS scaled) → Artelia (enterprise client understanding)" per `p1_architecte.md`'s Narrative rules.
- **P3** — Lead on "Open Ocean IS the proof" per `p3_cto.md`'s Narrative rules — built marine data platform from lab to industrial deployment (team of 12, €2M raised, exit by Artelia).
- For P2 / P4 / P5 — apply the analogous "lead order" / "what to emphasise" rules from their own profile files.

If the profile file lists a Solopreneur neutralisation section, apply it: name enterprise clients, team sizes, raised amounts. Avoid generic "I'm passionate about AI" filler.

### 4. Cas du parcours pertinents

3 cases from {Blue Green, Open Ocean, Artelia}, picked using the profile file's narrative rules (which experience leads for this profile). One paragraph each. Each case should answer: what was the role, what was the outcome, why this is relevant for this specific offer.

### 5. Questions probables de l'interlocuteur

8 questions tagged by `type_entretien`:
- **RH** — culture fit, mobility, salary expectations, why this company / why now.
- **Technique** — stack details, system design, hands-on coding, architecture trade-offs.
- **Manager** — team building, conflict, prioritisation, scaling people, hiring.
- **Final** — vision, 12-month plan, decision criteria, mutual deal-breakers.

For each question, a 1-line answer hook (the bullet point to anchor the answer in — usually a concrete proof from a case).

## Step 4 — Create the `entretien` note (via `jobsearch-vault`)

Invoke `jobsearch-vault` and ask it to **create a note** with exactly this structured request (it runs `create_note.py` internally). Naming: `Prep {Entreprise} — {Interlocuteurs join " "} — {DD-MM-YYYY}.md`, with em-dash separators (` — `, spaces around the em-dash):

```json
{
  "name":"Prep <Entreprise> — <Interlocuteurs or TBD> — <DD-MM-YYYY>",
  "type":"entretien",
  "folder":"CRM-JobSearch/Entretiens",
  "fields":{
    "categorie":"Préparation",
    "date":"<YYYY-MM-DD>",
    "opportunite":"[[<Poste> — <Entreprise>]]",
    "interlocuteurs":["<name-or-TBD>"],
    "type_entretien":"<RH|Technique|Manager|Final>"
  },
  "body":"## 1. Société\n\n<...>\n\n## 2. Résumé de la job description\n\n<...>\n\n## 3. Pitch (P<n>)\n\n<...>\n\n## 4. Cas du parcours pertinents\n\n<...>\n\n## 5. Questions probables de l'interlocuteur\n\n<...>\n"
}
```

The `entretien` note does NOT carry its own `target_profile` field — the profile is read transitively via `opportunite` → candidature → `target_profile`. Avoids duplicating state.

**Result contract.** `jobsearch-vault`'s bundled `note_schemas` natively accepts `categorie` and `interlocuteurs`, so a fully-specified `entretien` create produces **zero** validation warnings. The rule is simply: **exit 0 → ACCEPT** (the note was written); **non-zero exit → the note was NOT written**: report `❌ Échec création prep — <stderr>` and do not fire the Step 5 success report. If any unexpected stderr warning does appear, surface it verbatim, then proceed.

## Step 4b — Mirror the interview into hal (tagged `jobsearch`)

Create a hal task in the `renaud` workspace so the upcoming interview surfaces in the `jobsearch` section of `/briefing`. The hal task is the unified-PM mirror; the `entretien` note in Obsidian stays the canonical prep document.

Invoke `mcp__hal-mcp__create_task` exactly once with:

```
mcp__hal-mcp__create_task(
  workspace_slug = "renaud",
  title          = "Entretien <type_entretien> — <Entreprise> — <DD-MM-YYYY>",
  description    = "Entretien <type_entretien> avec <Interlocuteurs or TBD>. Prep: CRM-JobSearch/Entretiens/Prep <Entreprise> — <Interlocuteurs or TBD> — <DD-MM-YYYY>.md (profil P<n>).",
  tags           = ["jobsearch"],
  due_date       = "<YYYY-MM-DD>"   # the interview date itself
)
```

No `sprint_id` — interviews are sprint-less by design (tracked by tag, surfaced in `/briefing` until passed).

**Idempotency on re-prep.** Before creating, call `mcp__hal-mcp__list_tasks(workspace_slug="renaud")` and skip if a non-closed task with the exact same title already exists (re-prepping the same interview slot — the user re-ran `/interview-prep`). Match on title equality, not substring. Do NOT update the existing task — the prep note in Obsidian carries the refreshed content; the hal task is a thin pointer.

**If `list_tasks` fails**, proceed with `create_task` anyway and prepend a warning to the Step 5 output:
`⚠️ idempotency pre-check failed (<error>) — attempting create; re-run may create a duplicate if the task was already present.`
Then apply the standard failure handling below if `create_task` also fails.

**Failure handling.** If `mcp__hal-mcp__create_task` fails (non-zero / exception) but Step 4 succeeded, this is a **partial half-state**: the prep note is in Obsidian, the hal mirror is missing, `/briefing` will under-count the day's prep load. Report explicitly:

```
⚠️  hal mirror NON créé (prep Obsidian OK).
    Stderr        : <error>
    Impact        : la prep est dans Obsidian (canonical), mais pas dans la sous-section 🎯 jobsearch
                    de la section Renaud de /briefing.
    Recovery      : re-run /interview-prep (Step 4's idempotency overwrites the prep note; Step 4b retries)
```

Continue to Step 5 — the prep itself is intact. This is degraded but not broken.

## Step 5 — Report to the user (in French)

Render a concise summary, in French:

```
✅ Prep d'entretien créée — <Entreprise>
   📁 Note      : CRM-JobSearch/Entretiens/Prep <Entreprise> — … — <DD-MM-YYYY>.md
   🎯 Profil    : P<n> (<short label>)
   📌 Pitch     : <one-line load-bearing claim from the profile file>
   🗓️ Date     : <YYYY-MM-DD> · type: <RH|Technique|Manager|Final>
   📋 hal       : tâche "Entretien <type> — <Entreprise> — <DD-MM-YYYY>" créée (renaud/jobsearch)
                  (omettre cette ligne si Step 4b a échoué — voir ⚠️ ci-dessus)
```

## Step 6 — Constraints (load-bearing)

- **5-section structure is FIXED.** Always 5 H2s, always in the order `## 1. Société` → `## 2. Résumé de la job description` → `## 3. Pitch (P<n>)` → `## 4. Cas du parcours pertinents` → `## 5. Questions probables de l'interlocuteur`. Never collapse, rename, reorder, or skip a section — even if the user says "skip the questions, I'm running late". The structural invariant is the value the skill ships.
- **Pitch MUST be profile-positioned.** Cite concrete proofs from `profiles/p<n>_*.md`. A pitch that doesn't quote the profile file is a failure — it means the skill regressed to free-form prep, which is exactly the bug Loop 4 closes.
- **`target_profile` missing → ASK.** Never silently pick a profile. (Step 1.)
- **Candidature missing → ERROR, do NOT create a broken-wikilink prep.** Point at `/log-application` first. (Step 1.)
- **All vault writes via `jobsearch-vault`.** NEVER `Write` to the vault filesystem directly. `Read` is allow-listed ONLY for `profiles/p*.md` inside this plugin's source tree (via the PLUGIN_DIR resolver) — not for vault content. `mcp__hal-mcp__create_task` is allow-listed exclusively for the Step 4b hal mirror.
- **hal mirror (Step 4b) is intentional and additive.** The Obsidian `entretien` note is the canonical prep document; the hal task is a thin pointer that surfaces in `/briefing`'s `jobsearch` section. Both carry `jobsearch`. If Step 4b fails after Step 4 succeeds, the prep is still safe — degrade gracefully and continue (see Step 4b's failure block).
- **Entretien naming uses em-dash separators (` — `)** with spaces around the em-dash. Hyphens or `--` will not match the vault's expected filename pattern.
- **`categorie` is `"Préparation"`** (verbatim, with accent). The other valid value is `"Compte-rendu"` for debriefs — out of scope for this skill.
- **Compose, do not reimplement.** This skill is orchestration: locate, read, classify, compose, call. It does not re-implement vault writes or profile-narrative logic.
