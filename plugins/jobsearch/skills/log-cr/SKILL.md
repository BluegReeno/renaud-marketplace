---
name: log-cr
description: >
  Log a post-interview debrief (compte-rendu) end-to-end: create an `entretien`
  note with `categorie: "Compte-rendu"` and the full BANT structure
  (Lecture employeur, Fit Renaud, Notes clés, Questions posées, Next steps),
  link it to the `prep` and `opportunite`, advance the `opportunite-js` statut
  and next-date fields, close the hal task "Entretien …" from `interview-prep`,
  and create a hal relance task with key takeaways ("pour la prochaine fois").
  Use when the user says "fais le CR", "j'ai passé l'entretien",
  "CR d'entretien", "compte-rendu entretien", "debrief entretien",
  "j'ai eu l'entretien".
version: 0.7.0
allowed-tools: "Skill(jobsearch-vault) mcp__hal-mcp__list_tasks mcp__hal-mcp__create_task mcp__hal-mcp__update_task_status"
---

# Log CR — Skill Instructions

## What this skill does

After an interview, create the canonical compte-rendu trail: one `entretien` note in
`CRM-JobSearch/Entretiens/` with `categorie: "Compte-rendu"` and the BANT structure,
linked to the prep note and candidature; then advance the `opportunite-js` statut and
next-date fields; close the hal "Entretien …" task created by `interview-prep`; and
create a hal relance task with the post-interview insights ("pour la prochaine fois").
This skill NEVER touches the vault directly — all vault reads and writes flow through
`jobsearch-vault`.

## Step 0 — Inputs you need from the user

Collect (and confirm) all of the following before doing anything else:

1. **Candidature reference** (required) — free text like "l'entretien RH Anthropic" or
   "Mistral Manager". Used to locate the `opportunite-js` note and the matching prep note.
2. **Date de l'entretien** (default: today) — `YYYY-MM-DD` for frontmatter,
   `DD-MM-YYYY` for filename suffix.
3. **`type_entretien`** (required) — one of `RH` / `Technique` / `Manager` / `Final`.
   Drives the hal task title match in Step 5.
4. **`interlocuteurs`** (required) — list of names, e.g. `["Alice Dupont (RH)", "Bob Martin (CTO)"]`.
5. **`feeling`** (required) — one of `🔥` (très positif) / `🟡` (mitigé) / `❌` (négatif).
   Recorded in frontmatter.
6. **`format`** (optional) — one of `Teams` / `Meet` / `Présentiel`. Non-blocking warning
   expected from `jobsearch-vault` (field not in schema — AC1 contract applies, see Step 3).
7. **`heure`** (optional) — time slot, e.g. `"14:00–15:30"`. Same non-blocking warning expected.
8. **Interview notes** (required for BANT body) — ask the user to share their raw notes /
   impressions from the interview. The skill structures these into the 5 BANT sections. Without
   notes the CR body will be empty — insist if omitted.
9. **Next step** (required) — what happens after the CR? One of:
   - **Another round scheduled** → ask for date (`prochain_rdv`) → statut `"📞 Entretien prévu"`
   - **Waiting for an answer** → statut unchanged, `date_relance` = today + 7d
   - **Offer received** → statut `"🎉 Offre reçue"`
   - **Rejected / no-go** → statut `"❌ Refus"` or `"🚫 Pas de suite"` (ask which)
   - **Unknown / TBC** → statut unchanged, `date_relance` = today + 7d

Do not proceed until inputs 1–5 and 8–9 are settled.

## Step 1 — Locate the candidature and prep note (via `jobsearch-vault`)

Invoke `jobsearch-vault` to search `CRM-JobSearch/Opportunites/` by `entreprise` + `poste`
text match. Capture:

- `frontmatter.entreprise` — company wikilink (e.g. `[[Anthropic]]`).
- `frontmatter.statut` — current statut (for Step 4 update).
- `frontmatter.target_profile` — for context.
- The candidature title `<Poste> — <Entreprise>` (used as wikilink in the CR frontmatter).

Also search `CRM-JobSearch/Entretiens/` for the matching prep note (`Prep <Entreprise> — …`).
Capture the exact prep note name as `prep_name` (without `.md`) for the `prep` wikilink.

**If the candidature does not exist** → return a clear error: "Aucune candidature trouvée pour
<Entreprise>. Loguez d'abord la candidature avec `/log-application`." Do NOT create a CR with
a broken wikilink.

**If no prep note is found** → proceed without the `prep` wikilink (omit the field entirely).
Surface a warning: "⚠️ Aucune note de préparation trouvée pour <Entreprise> — le champ `prep`
sera omis du CR."

## Step 2 — Compose the BANT body

Using the user's raw interview notes (Step 0, input 8), structure the body into these 5 H2
sections in this exact order. Write the content in French:

### BANT template (fixed structure — do not rename, reorder, or skip sections)

```
## 🏢 Lecture employeur — BANT

**Budget** : <budget / fourchette salariale mentionnée, ou "Non abordé">
**Authority** : <qui prend la décision finale — hiring manager, DG, board ?>
**Need** : <besoin exprimé — urgences, chantiers, pain points>
**Timeline** : <processus : prochaines étapes, nombre de rounds, deadline de décision>

## 🪞 Lecture Renaud — Fit

<3–5 bullets : ce qui a résonné positivement, ce qui a suscité des réserves, alignement mission/valeurs>

## 📝 Notes clés

<observations verbatim ou paraphrasées de l'entretien — citations notables de l'interlocuteur si disponibles>

## ❓ Questions posées

**Par l'interlocuteur :**
- <question 1>
- <question 2>

**Par Renaud :**
- <question 1>
- <question 2>

## ➡️ Next steps

<résumé de ce qui a été convenu : qui recontacte, dans quel délai, prochaine étape du process>
```

Do not invent information absent from the user's notes — leave `<non mentionné>` for elements
not covered in the interview.

## Step 3 — Check for existing CR note (idempotency) then create or update

Note naming convention: `CR <Entreprise> — <Interlocuteur principal> — <DD-MM-YYYY>.md`
(em-dash ` — ` with spaces; use first interlocuteur name if multiple; same separator pattern
as `Prep …` and `opportunite-js` filenames).

**Match semantics** (binding): exact filename, case-insensitive (APFS). Invoke `jobsearch-vault`
to search `CRM-JobSearch/Entretiens/` for the exact filename.

- **If found** → ask `jobsearch-vault` to update (`update_frontmatter`), refreshing `feeling`,
  `date_suivi`, `interlocuteurs`. Report "🔁 CR existant mis à jour" — not created.
- **If not found** → ask `jobsearch-vault` to create the note with the payload below.

### `entretien` creation payload (categorie: Compte-rendu)

```json
{
  "name": "CR <Entreprise> — <Interlocuteur principal> — <DD-MM-YYYY>",
  "type": "entretien",
  "folder": "CRM-JobSearch/Entretiens",
  "fields": {
    "categorie": "Compte-rendu",
    "date": "<YYYY-MM-DD>",
    "opportunite": "[[<Poste> — <Entreprise>]]",
    "prep": "[[<prep_name>]]",
    "interlocuteurs": ["<Prénom Nom (Rôle)>"],
    "type_entretien": "<RH|Technique|Manager|Final>",
    "feeling": "<🔥|🟡|❌>",
    "format": "<Teams|Meet|Présentiel — OMIT KEY if not provided>",
    "heure": "<HH:MM–HH:MM — OMIT KEY if not provided>"
  },
  "body": "<BANT body from Step 2>"
}
```

**Field contracts:**

- `prep` is NOT in the `entretien` schema → non-blocking warning expected. AC1 contract:
  exit 0 + `unknown field 'prep'` → ACCEPT. Do not retry without the field.
- `format` is NOT in the `entretien` schema → same AC1 contract.
- `heure` is NOT in the `entretien` schema → same AC1 contract.
- Omit `format` and `heure` entirely if the user did not provide them (never pass empty strings).
- Omit `prep` entirely if no matching prep note was found (Step 1 warned the user).

**General result contract:**

- **Exit 0 → ACCEPT** (note written; any AC1 field warnings are non-blocking).
- **Exit 0 + unexpected stderr (not the known AC1 fields listed above)** → surface the warning
  verbatim to the user, then proceed.
- **Non-zero exit → FAIL HARD.** Report `❌ Échec création CR — <stderr>` and do NOT proceed
  to Steps 4–6. This is the AC1 invariant — no half-states.

## Step 4 — Advance the `opportunite-js` (via `jobsearch-vault`)

Update the candidature frontmatter via `update_frontmatter` based on the next step (Step 0, input 9):

| Next step | Fields to update |
|-----------|-----------------|
| Another round scheduled | `statut: "📞 Entretien prévu"`, `prochain_rdv: "<YYYY-MM-DD>"` |
| Waiting for answer | `date_relance: "<today + 7d>"` (keep statut unchanged) |
| Offer received | `statut: "🎉 Offre reçue"` |
| Rejected / no-go | `statut: "❌ Refus"` OR `statut: "🚫 Pas de suite"` (ask user which) |
| Unknown / TBC | `date_relance: "<today + 7d>"` (keep statut unchanged) |

Only write statut values from this table — never write an arbitrary string.

**Failure handling.** If `update_frontmatter` fails (non-zero) after Step 3 succeeded:

```
⚠️  Half-state — CR créé, opportunité NON mise à jour.
    Erreur  : <stderr>
    Recovery: re-run /log-cr (Step 3 idempotency court-circuite vers Step 4)
```

Continue to Steps 5–6 regardless — hal actions are independent of the vault statut update.

## Step 5 — Close the hal "Entretien" task

The `interview-prep` skill created a hal task titled
`"Entretien <type_entretien> — <Entreprise> — <DD-MM-YYYY>"`. After the CR, close it.

**Pre-check.** Call `mcp__hal-mcp__list_tasks(workspace_slug="renaud")`. Search for a task
whose title exactly matches `"Entretien <type_entretien> — <Entreprise> — <DD-MM-YYYY>"`
(interview date from Step 0, formatted `DD-MM-YYYY` with 4-digit year).

- **If found and not already closed** → call `mcp__hal-mcp__update_task_status` to mark it
  `"Terminé"`.
  <!-- TODO: verify in Cowork — exact parameter signature for update_task_status (task_id, workspace_slug, status string) -->
- **If not found or already closed** → skip silently (idempotent).
- **If `list_tasks` fails** → skip the close; prepend to Step 7 output:
  `⚠️ Impossible de vérifier la tâche hal "Entretien …" — <error>. À clôturer manuellement.`

**If `update_task_status` fails after finding the task:**

```
⚠️  Tâche hal "Entretien <type> — <Entreprise> — <DD-MM-YYYY>" NON clôturée.
    Erreur  : <error>
    Recovery: clôturer manuellement dans hal renaud/jobsearch
```

Continue to Step 6.

## Step 6 — Create the hal relance task (with post-interview insights)

Create a hal task in the `renaud` workspace. The `description` MUST include the key takeaways
("pour la prochaine fois") extracted from the `## 🪞 Lecture Renaud — Fit` section of the BANT.

**Idempotency.** If `list_tasks` already ran in Step 5 and succeeded, reuse the result —
do NOT call it a second time. Otherwise call `mcp__hal-mcp__list_tasks(workspace_slug="renaud")`
and skip if a non-closed task with title `"Relance CR — <Entreprise> — <YYYY-MM-DD>"` exists
(exact title match, not substring).

Invoke `mcp__hal-mcp__create_task` exactly once with:

```
mcp__hal-mcp__create_task(
  workspace_slug = "renaud",
  title          = "Relance CR — <Entreprise> — <YYYY-MM-DD interview date>",
  description    = "CR <type_entretien> — feeling: <feeling emoji>. Pour la prochaine fois : <2–3 key takeaways from Lecture Renaud — Fit, plain text>. Prochain contact : <next step summary from Step 0>.",
  tags           = ["jobsearch"],
  due_date       = "<prochain_rdv if set, else today + 7d>"
)
```

**Failure handling.** If `create_task` fails but Steps 3–5 succeeded:

```
⚠️  Half-state — CR et clôture OK, relance hal NON créée.
    Erreur        : <error>
    Recovery A    : re-run /log-cr (Steps 3–5 idempotent ; Step 6 retente)
    Recovery B    : créer manuellement une tâche hal renaud/jobsearch
                    title: "Relance CR — <Entreprise> — <YYYY-MM-DD>"
                    tags: ["jobsearch"] · due_date: <YYYY-MM-DD>
```

## Step 7 — Report to the user (in French)

Render a concise summary:

```
✅ CR loggé — <type_entretien> chez <Entreprise>
   📁 Note       : CRM-JobSearch/Entretiens/CR <Entreprise> — … — <DD-MM-YYYY>.md
   🔗 Liens      : [[<Poste> — <Entreprise>]] · [[Prep <Entreprise> — … — <DD-MM-YYYY>]]
   🎭 Feeling    : <feeling emoji>
   📊 Opportunité : <new statut or "statut inchangé"> · <prochain_rdv or date_relance>
   ✔️  hal task   : "Entretien …" clôturée (ou ⚠️ si échec — voir ci-dessus)
   🔄 Relance    : <due_date> — "Relance CR — <Entreprise> — <YYYY-MM-DD>" créée dans hal renaud/jobsearch
```

If the CR already existed and was updated (not created), change the first line to
`🔁 CR mis à jour — <type_entretien> chez <Entreprise>`.

## Step 8 — Constraints (load-bearing)

- **All vault I/O via `jobsearch-vault`.** NEVER `Read` or `Write` the vault filesystem directly.
- **Trigger isolation.** This skill handles post-interview CRs ONLY. Pasted job offer / "j'ai
  postulé" → `/log-application`. "Prépare l'entretien" / upcoming interview → `/interview-prep`.
  If invoked in error before an interview: "❌ Ce skill est pour les CR post-entretien. Utilisez
  `/interview-prep` pour préparer un entretien à venir."
- **BANT sections are FIXED.** Always 5 H2s in this exact order: `## 🏢 Lecture employeur — BANT`
  → `## 🪞 Lecture Renaud — Fit` → `## 📝 Notes clés` → `## ❓ Questions posées` →
  `## ➡️ Next steps`. Never reorder, rename, or skip.
- **`categorie: "Compte-rendu"`** — verbatim with accent. The `"Préparation"` variant is for
  `interview-prep` only.
- **Non-blocking field warnings** — `prep`, `format`, `heure` are not in the `entretien` schema.
  All three apply the AC1 contract (exit 0 + known warning → ACCEPT). Do not retry without these
  fields; do not patch the global schema from here.
- **Statut values** — only from the Step 4 table. Never write an arbitrary statut string.
- **hal task title match is exact.** `"Entretien RH — Anthropic — 01-07-2026"` does NOT match
  `"Entretien RH — Anthropic — 01-07-26"`. Always use `DD-MM-YYYY` with 4-digit year.
- **`update_task_status` signature is runtime-verified** (see Step 5 TODO). If the call fails
  with a parameter error, surface the raw error and ask the user to close the task manually.
- **Idempotency at every step.** Steps 3, 5, and 6 all search-before-write. Re-running `/log-cr`
  for the same interview is safe.
- **Compose, do not reimplement.** Orchestration only: collect, compose, call `jobsearch-vault`,
  call hal-mcp. No direct vault writes.
