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
version: 0.3.0
allowed-tools: "Skill(obsidian-crm) Read"
---

# Interview Prep — Skill Instructions

## What this skill does

Given a candidature (resolved by company name + role title, or a free-text reference), produce one Obsidian `entretien` note with `categorie: "Préparation"` in `CRM-JobSearch/Entretiens/`. The body is ALWAYS the same five H2 sections, in this exact order:

1. **Société**
2. **Résumé de la job description**
3. **Pitch** (profile-positioned for the candidature's `target_profile`)
4. **Cas du parcours pertinents**
5. **Questions probables de l'interlocuteur**

The Pitch section is grounded in the matching `profiles/p<n>_*.md` narrative file — concrete proofs, not generic claims. All vault I/O goes through the global `obsidian-crm` skill; the profile narrative files (which live in this plugin's source tree, NOT in the Obsidian vault) are read with the standard `Read` tool.

## Step 0 — Inputs you need from the user

Collect (and confirm) the following before doing anything else:

1. **Candidature reference** (required) — free text like "the Relief CTO one" or "Anthropic Applied AI". The skill searches by `entreprise` + `poste` in `CRM-JobSearch/Opportunites/`.
2. **Interview date** — default: tomorrow. Format `YYYY-MM-DD` for frontmatter; `DD-MM-YYYY` for the filename suffix.
3. **`type_entretien`** — default `"RH"`. One of `RH` / `Technique` / `Manager` / `Final` (drives the question set in Step 3.5).
4. **`interlocuteurs`** — default `["TBD"]`. Free-text list of names.

Do not proceed until the candidature is unambiguously identified.

## Step 1 — Locate the candidature (via `obsidian-crm`)

Invoke `obsidian-crm` to search `CRM-JobSearch/Opportunites/` by `entreprise` + `poste` text match, then read the matching note. Capture:

- `frontmatter.target_profile` — one of `"P1"` / `"P2"` / `"P3"` / `"P4"` / `"P5"`.
- `frontmatter.entreprise` — the company wikilink.
- `frontmatter.lien_offre` — optional URL.
- `frontmatter.source` — for context.
- `body` — the pasted offer (used for the JD summary in section 2).

**If `target_profile` is missing** (legacy candidature filed before `log-application` existed): ASK the user which P1–P5 to use. Show the P1–P5 short labels (Architect / Lead / CTO / CS-FDE / Sales). DO NOT silently default. Once chosen, optionally invoke `obsidian-crm`'s `update_frontmatter.py` to persist the answer back onto the candidature so the next prep finds it.

**If the candidature does not exist** (search returns nothing): return a clear error pointing the user at `/log-application` first. Do NOT create the `entretien` note with a broken wikilink — that pollutes the vault.

## Step 2 — Read the matching profile narrative

Read the file `profiles/p<n>_*.md` from this plugin's source tree, where `<n>` is the digit from `target_profile` (e.g. `P3` → `profiles/p3_cto.md`).

These files live in the **plugin source tree**, NOT in the Obsidian vault — that is why `Read` is allow-listed alongside `Skill(obsidian-crm)`. Use the PLUGIN_DIR resolver to locate `profiles/` in any environment (dev workstation, marketplace cache, Cowork sandbox):

```bash
PLUGIN_DIR=$(python3 - <<'PYEOF'
import json, os, pathlib, sys, glob as _glob
home = pathlib.Path.home()
env = os.environ.get('JOBSEARCH_PLUGIN_DIR', '')
if env and pathlib.Path(env, 'profiles', 'p1_architecte.md').exists():
    print(env); sys.exit(0)
cache_root = home / '.claude' / 'plugins' / 'cache' / 'renaud-marketplace' / 'jobsearch'
if cache_root.exists():
    candidates = sorted(cache_root.glob('*/profiles/p1_architecte.md'), key=lambda p: p.stat().st_mtime, reverse=True)
    if candidates:
        print(str(candidates[0].parent.parent)); sys.exit(0)
for pat in ['/sessions/*/mnt/.remote-plugins/*/profiles/p1_architecte.md']:
    matches = sorted(_glob.glob(pat), key=os.path.getmtime, reverse=True)
    if matches:
        print(os.path.dirname(os.path.dirname(matches[0]))); sys.exit(0)
dev = home / 'Projects' / 'renaud-marketplace' / 'plugins' / 'jobsearch'
if dev.joinpath('profiles', 'p1_architecte.md').exists():
    print(str(dev)); sys.exit(0)
print('PLUGIN_DIR_NOT_FOUND')
PYEOF
)
if [ "$PLUGIN_DIR" = "PLUGIN_DIR_NOT_FOUND" ]; then
  echo "ERROR: jobsearch plugin not found. Set JOBSEARCH_PLUGIN_DIR=<path> or install from marketplace."
  exit 1
fi
```

Then `Read "$PLUGIN_DIR/profiles/p<n>_<label>.md"` (e.g. `p3_cto.md`). Quote — don't paraphrase — the load-bearing claims under the file's "Narrative rules" and "Key differentiators" H2s.

## Step 3 — Compose the 5 sections (always identical structure)

The body of the `entretien` note MUST contain these five H2 headings, in this exact order, with these exact strings (the agent writes the actual content underneath in French):

### 1. Société

Pull from an `entreprise-js` note if `obsidian-crm` finds one linked to `frontmatter.entreprise`; otherwise summarize from the offer body. 3–5 bullets max: what they do, size/stage, why this role exists now, anything from the offer that signals culture.

### 2. Résumé de la job description

5 bullets distilled from the offer body, in this rough order: scope, stack, seniority, mission, success criteria.

### 3. Pitch (positionné P<n>)

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

## Step 4 — Create the `entretien` note (via `obsidian-crm`)

Invoke `obsidian-crm`'s `create_note.py` with the JSON payload below. Naming: `Prep {Entreprise} — {Interlocuteurs join " "} — {DD-MM-YYYY}.md` (per `~/.claude/skills/obsidian-crm/references/schemas.md:76`, with em-dash separators):

```bash
echo '{
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
  "body":"## 1. Société\n\n<...>\n\n## 2. Résumé de la job description\n\n<...>\n\n## 3. Pitch (P<n>)\n\n<...>\n\n## 4. Cas du parcours pertinents\n\n<...>\n\n## 5. Questions probables de l'\''interlocuteur\n\n<...>\n"
}' | python ~/.claude/skills/obsidian-crm/scripts/create_note.py
```

The `entretien` note does NOT carry its own `target_profile` field — the profile is read transitively via `opportunite` → candidature → `target_profile`. Avoids duplicating state.

## Step 5 — Report to the user (in French)

Render a concise summary, in French:

```
✅ Prep d'entretien créée — <Entreprise>
   📁 Note      : CRM-JobSearch/Entretiens/Prep <Entreprise> — … — <DD-MM-YYYY>.md
   🎯 Profil    : P<n> (<short label>)
   📌 Pitch     : <one-line load-bearing claim from the profile file>
   🗓️ Date     : <YYYY-MM-DD> · type: <RH|Technique|Manager|Final>
```

## Step 6 — Constraints (load-bearing)

- **5-section structure is FIXED.** Always 5 H2s, always in the order `## 1. Société` → `## 2. Résumé de la job description` → `## 3. Pitch (P<n>)` → `## 4. Cas du parcours pertinents` → `## 5. Questions probables de l'interlocuteur`. Never collapse, rename, reorder, or skip a section — even if the user says "skip the questions, I'm running late". The structural invariant is the value the skill ships.
- **Pitch MUST be profile-positioned.** Cite concrete proofs from `profiles/p<n>_*.md`. A pitch that doesn't quote the profile file is a failure — it means the skill regressed to free-form prep, which is exactly the bug Loop 4 closes.
- **`target_profile` missing → ASK.** Never silently pick a profile. (Step 1.)
- **Candidature missing → ERROR, do NOT create a broken-wikilink prep.** Point at `/log-application` first. (Step 1.)
- **All vault writes via `obsidian-crm`.** NEVER `Write` to the vault filesystem directly. `Read` is allow-listed ONLY for `profiles/p*.md` inside this plugin's source tree (via the PLUGIN_DIR resolver) — not for vault content.
- **Entretien naming uses em-dash separators (` — `)** with spaces around the em-dash, matching `~/.claude/skills/obsidian-crm/references/schemas.md:76` exactly. Hyphens or `--` will not match the schema's expected filename pattern.
- **`categorie` is `"Préparation"`** (verbatim, with accent). The other valid value is `"Compte-rendu"` for debriefs — out of scope for this skill.
- **Compose, do not reimplement.** This skill is orchestration: locate, read, classify, compose, call. It does not re-implement vault writes or profile-narrative logic.
