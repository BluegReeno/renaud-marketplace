---
name: log-application
description: >
  Log a job application end-to-end: classify the pasted offer against the P1–P5
  profile taxonomy from `cv-generator`, then compose the global `obsidian-crm`
  skill to create (or update) one `opportunite-js` candidature note with all
  fixed fields (`entreprise`, `statut`, `source`, `target_profile`,
  `date_candidature`, `date_relance`, `lien_offre`, body = pasted offer) and one
  `tache` relance with `etiquettes: ["jobsearch"]` and `echeance: today + 7d`
  so it surfaces in tomorrow's `/briefing`. Use when the user says "log
  application", "j'ai postulé", "candidature envoyée", "je viens de candidater",
  "track application", "log apply", or pastes a job offer with intent to file it.
version: 0.3.0
allowed-tools: "Skill(obsidian-crm)"
---

# Log Application — Skill Instructions

## What this skill does

Take a pasted job offer plus a declared source (LinkedIn / WTTJ / direct / referral / other), classify it against the existing P1–P5 profile taxonomy from `cv-generator`, then compose the global `obsidian-crm` skill to write the candidature trail into Obsidian: one `opportunite-js` note in `CRM-JobSearch/Opportunites/` with every fixed field populated, and one `tache` relance in `Taches/` with `etiquettes: ["jobsearch"]` and an `echeance` 7 days out. The morning-briefing (Loop 3) already surfaces tasks shaped this way. This skill NEVER touches the vault directly — all reads and writes flow through `obsidian-crm`.

## Step 0 — Inputs you need from the user

Collect (and confirm) the following before doing anything else:

1. **Pasted offer text** (required) — the job description body. The skill will not fetch URLs; the user pastes the text.
2. **Company name** and **role title** — extract from the offer body if obvious, otherwise ASK. They drive the candidature title `<Poste> — <Entreprise>` and the `entreprise` frontmatter.
3. **`source`** (required, one of `LinkedIn` / `WTTJ` / `direct` / `referral` / other) — ASK if not stated. This field is mandatory.
4. **`lien_offre`** (optional URL) — empty string if the user has no link (e.g. referral-only).

Do not proceed until `source` and `entreprise` + `poste` are settled.

## Step 1 — Classify the offer against P1–P5

Use the profile detection table from `cv-generator` (REUSED VERBATIM — do not invent a new classifier):

| Profile | Key signals in the job offer |
|---------|------------------------------|
| **P1** `p1` — AI Architect / Solution Architect | "architect", "solution architect", "applied AI", "technical lead" (client-facing), "GenAI deployment", "pre-sales architect" |
| **P2** `p2` — AI Lead / Manager | "AI lead", "head of AI", "practice lead", "manager", "team lead", "responsable IA" |
| **P3** `p3` — CTO | "CTO", "Chief Technology Officer", "technical co-founder", "VP Engineering" |
| **P4** `p4` — Customer Success / FDE | "customer success", "forward deployed engineer", "solutions engineer", "SE", "FDE", "customer onboarding" |
| **P5** `p5` — Sales / BizDev | "account executive", "AE", "business development", "BDM", "sales", "commercial" |

Default if ambiguous: **P1** (`target_profile: "P1"`). When two profiles plausibly match, report it to the user as "ambiguous between P<x>/P<y>, defaulting to P1 — say P<y> to override" and proceed. The candidature note only needs the profile half; T1–T5 company-type is a `cv-generator` concern and is NOT written here.

Set `target_profile` to one of the literal strings `"P1"`, `"P2"`, `"P3"`, `"P4"`, `"P5"`.

## Step 2 — Resolve dates

- `date_candidature` = today, formatted `YYYY-MM-DD`, Europe/Paris.
- `date_relance` = `date_candidature + 7 days`, formatted `YYYY-MM-DD`.

## Step 3 — Check for existing candidature (idempotency)

macOS APFS is case-insensitive; two candidatures with the same name will collide. Re-applying to the same role must not silently fail. Invoke `obsidian-crm` to search `CRM-JobSearch/Opportunites/` for a note matching `entreprise` + `poste`:

**Match semantics** (binding): exact filename `"<Poste> — <Entreprise>.md"` (em-dash with spaces, case-insensitive — APFS-equivalent). Substring or fuzzy matches MUST NOT be treated as hits. If `obsidian-crm` returns >1 result for the exact filename (theoretically impossible but allow for upstream bugs), ASK the user which one — do NOT auto-pick.

- **If found** → use `obsidian-crm`'s `update_frontmatter.py` to refresh `statut`, `source`, `target_profile`, `date_relance` (keep the original `date_candidature` from the existing note). Report to the user that an existing candidature was updated, not created.
- **If not found** → use `obsidian-crm`'s `create_note.py` with the full payload below.

### `opportunite-js` creation payload

```bash
echo '{
  "name":"<Poste> — <Entreprise>",
  "type":"opportunite-js",
  "folder":"CRM-JobSearch/Opportunites",
  "fields":{
    "entreprise":"[[<Entreprise>]]",
    "statut":"✉️ Candidature envoyée",
    "source":"<LinkedIn|WTTJ|direct|referral|other>",
    "date_candidature":"<YYYY-MM-DD>",
    "date_relance":"<YYYY-MM-DD +7d>",
    "lien_offre":"<url-or-empty>",
    "target_profile":"P<1-5>"
  },
  "body":"## Annonce\n\n<pasted offer text, verbatim>\n"
}' | python ~/.claude/skills/obsidian-crm/scripts/create_note.py
```

`target_profile` is NOT in the global `opportunite-js` schema → `create_note.py` will print a non-blocking warning to stderr (per `obsidian-crm/SKILL.md:286`). The agreed contract is:

- **Exit 0 + stderr contains `unknown field 'target_profile'`** → ACCEPT. The candidature was written. Do not retry.
- **Exit 0 + any OTHER stderr warning** → SURFACE the warning to the user verbatim, then proceed. Do not silently swallow it (a future `obsidian-crm` schema change might surface here first).
- **Non-zero exit** → FAIL HARD per the rule below. The candidature was NOT written.

Adding `target_profile` to the global schema is out of scope for this skill — the warning is the agreed-upon escape hatch.

**Check Step 3's exit code before proceeding.** `create_note.py` / `update_frontmatter.py` exit 0 on success (including the non-blocking `target_profile` warning above). Any non-zero exit means the candidature was NOT written: report `❌ Échec création candidature — <stderr>` to the user and **DO NOT proceed to Step 4 or fire the Step 5 success report.** This is the AC1 invariant — no half-states, no silent success.

## Step 4 — Create the relance task

**Idempotency on re-apply**: mirror Step 3's search-before-create. Invoke `obsidian-crm` to search `Taches/` for a `tache` whose `opportunite` wikilink equals `"[[<Poste> — <Entreprise>]]"` AND whose `etiquettes` contains `"jobsearch"` AND whose `etat` is open (`Pas commencée` or `En cours`, NOT `Terminée` / `Annulée`).

- **If found** → use `update_frontmatter.py` to refresh `echeance` to `date_candidature + 7d`. Do NOT create a duplicate. Reuse the existing task — `/briefing` will surface it tomorrow.
- **If not found** → create the relance `tache` with the payload below.

Invoke `obsidian-crm` to create the 7-day relance `tache`:

```bash
echo '{
  "name":"Relance — <Entreprise> — <YYYY-MM-DD candidature>",
  "type":"tache",
  "folder":"Taches",
  "fields":{
    "etat":"Pas commencée",
    "priorite":"Moyenne",
    "echeance":"<YYYY-MM-DD +7d>",
    "etiquettes":["jobsearch"],
    "opportunite":"[[<Poste> — <Entreprise>]]"
  },
  "body":"## Résumé\n\nRelance candidature envoyée le <YYYY-MM-DD> (<source>). Vérifier réponse, sinon LinkedIn message au recruteur.\n"
}' | python ~/.claude/skills/obsidian-crm/scripts/create_note.py
```

**Check Step 4's exit code.** If Step 3 succeeded but Step 4 failed (non-zero exit), the vault is in a **half-state**: the candidature exists, the relance task does not, `/briefing` will silently miss the relance. Report explicitly to the user with both recovery paths:

```
⚠️  Half-state — candidature loguée, relance NON créée.
    Stderr Step 4 : <stderr>
    Recovery A    : re-run /log-application (Step 3 idempotency short-circuits to Step 4)
    Recovery B    : manually create a Taches/ note with
                    type: tache · etiquettes: ["jobsearch"] · echeance: <YYYY-MM-DD +7d>
                    · opportunite: "[[<Poste> — <Entreprise>]]"
```

Do NOT fire Step 5's success report on a half-state — its `/briefing` claim would be a lie, which is the exact AC1 regression Loop 4 closes.

The morning-briefing's Step 1c resolves "relances due today or overdue" against (a) `tache` with `etiquettes` containing `"jobsearch"` and `echeance <= today`, OR (b) `opportunite-js` with `statut: "🔄 Relance à faire"`. Path (a) is the one this skill takes. Path (b) is reserved for the day the user actually starts the relance — out of scope here.

## Step 5 — Report to the user (in French)

Render a concise summary, in French:

```
✅ Candidature loguée — <Poste> chez <Entreprise>
   📁 Note     : CRM-JobSearch/Opportunites/<Poste> — <Entreprise>.md
   🎯 Profil   : P<n> (<short label, e.g. "CTO" or "Architect">)
   🔄 Relance  : <YYYY-MM-DD +7d> — apparaîtra dans /briefing
   🔗 Source   : <source>
```

If the candidature already existed and was updated rather than created, change the first line to `🔁 Candidature mise à jour — …` and include the original `date_candidature`.

If the user has not yet generated a CV for this offer, suggest running `/cv-generator` next (with the same offer text and target profile).

## Step 6 — Constraints (load-bearing)

- **All vault I/O via `obsidian-crm`.** NEVER `Read` or `Write` the vault filesystem directly. `allowed-tools` lists only `Skill(obsidian-crm)` — do not work around it.
- **First-apply `statut` is `✉️ Candidature envoyée`** (with emoji, verbatim — re-typing the emoji loses the variation selector). Do NOT set `🔄 Relance à faire` here; the relance is carried by the `tache`, not the candidature `statut`. The user transitions the candidature's `statut` manually (or via a later skill) when they actually chase the relance.
- **Relance `etat` is `Pas commencée`** (verbatim, including accent).
- **Wikilinks**: `entreprise` is `"[[<Entreprise>]]"`, the task's `opportunite` is `"[[<Poste> — <Entreprise>]]"` (em-dash with spaces, matching the candidature title exactly).
- **`target_profile` warning is expected.** It is non-blocking. Do not retry without the field; do not patch the global schema from here.
- **`source` is mandatory.** If the user did not state one, the skill ASKS in Step 0 before proceeding. No silent default.
- **Idempotency on re-apply.** Step 3 must search before creating, and switch to `update_frontmatter.py` when the note exists. Do not let `create_note.py` fail-then-retry-by-rename.
- **No auto-apply, no email, no CV attach.** The skill files the trail; the user submits the application themselves. `cv-generator` handles the PDF — invoke it separately via `/cv-generator`.
- **Compose, do not reimplement.** This skill is orchestration: classify, compose JSON payloads, and call `obsidian-crm`. It does not re-implement vault writes.
