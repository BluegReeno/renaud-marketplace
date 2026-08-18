---
name: log-cr
description: >
  Log a post-interview debrief as an Obsidian `entretien` note with
  `categorie: "Compte-rendu"`, structured with the BANT template
  (Notes clés / Questions posées / Lecture employeur — BANT / Lecture Renaud
  — Fit / Next steps). Advances the matching `opportunite-js` to
  `statut: "🔄 Relance à faire"` (and `prochain_rdv` when a follow-up date is
  confirmed), closes the prep hal task created by `interview-prep`, and
  creates a follow-up relance hal task. Use when the user says "log CR",
  "compte-rendu entretien", "j'ai passé l'entretien", "retour d'entretien",
  "debrief entretien", "debrief <company>", "j'ai eu l'entretien avec",
  "log debrief".
allowed-tools: "Skill(jobsearch-vault) mcp__plugin_hal_hal-mcp__list_tasks mcp__plugin_hal_hal-mcp__update_task_status mcp__plugin_hal_hal-mcp__create_task"
---

# Log CR — Skill Instructions

## What this skill does

Given a completed interview, produce one Obsidian `entretien` note with `categorie: "Compte-rendu"` in `CRM-JobSearch/Entretiens/`, filled with the BANT (employer's read) + Fit (Renaud's own read) debrief (see `docs/bant-cr-template.md` for the canonical template). Then:

1. Advance the matching `opportunite-js` to `statut: "🔄 Relance à faire"`, and `prochain_rdv` when a follow-up date is confirmed.
2. Close the prep hal task created by `interview-prep` (if found).
3. Create a post-interview relance hal task in the `renaud` workspace.

All vault I/O flows through `jobsearch-vault`. This skill NEVER writes to the vault filesystem directly.

## Step 0 — Domain check

If the user mentions a Blue Green client, partner, or sales context, redirect immediately:

> "Ce CR semble être un meeting Blue Green. Utilise `/crm log` dans Cowork bluegreen-marketplace plutôt que ce skill."

Do NOT write Blue Green data into the Obsidian vault (vault = jobsearch only — hard rule).

## Step 1 — Collect inputs

Gather (and confirm) the following before doing anything else:

1. **Entreprise + Poste** — to locate the `opportunite-js` candidature. Free-text reference ("the Anthropic one") is fine; resolve it in Step 2.
2. **Date de l'entretien** — default: today (`YYYY-MM-DD`). Filename suffix format: `DD-MM-YYYY`.
3. **`format`** — `Teams` / `Meet` / `Présentiel` (free text, not an enum). Ask if not provided.
4. **`heure`** — `HH:MM–HH:MM`. Ask if not provided.
5. **`type_entretien`** — one of `RH` / `Technique` / `Manager` / `Final`. Default: `RH`.
6. **`interlocuteurs`** — list of names. No default — ask if not provided.
7. **`feeling`** — one of `🔥` / `🟡` / `❌`. Ask if not provided.
8. **BANT notes** — ask the user to share their notes from the interview, prompting with the directive questions from `docs/bant-cr-template.md` when notes are sparse:
   - **B — Comp/Budget** — fourchette confirmée ? fixe + variable + equity ?
   - **A — Autorité** — qui décide ? étapes restantes ? combien d'interlocuteurs ?
   - **N — Besoin précis** — quel problème je viens résoudre ? succès à J+30/J+90 ?
   - **T — Timeline** — quand veulent-ils décider ? urgence du recrutement ?

   Fill what you can; leave `<à compléter>` placeholders for unknowns.
9. **Lecture Renaud — Fit** — ask the user directly: feeling global (🔥/🟡/❌), ce qui l'a convaincu, ce qui le questionne, questions encore ouvertes. This is Renaud's own subjective read, distinct from the BANT (the employer's read) — never skip it.
10. **Prochain rendez-vous** (optional) — if the interview already produced a confirmed next-step date (a next round, a decision date), capture it (`YYYY-MM-DD`) for `prochain_rdv` in Step 6. Omit if no date was confirmed — do not guess one.

Do not proceed until `entreprise`, `interlocuteurs`, and `feeling` are confirmed.

## Step 2 — Locate the candidature (via `jobsearch-vault`)

Invoke `jobsearch-vault` to search `CRM-JobSearch/Opportunites/` by `entreprise` + `poste` text match. Capture:

- `frontmatter.entreprise` — wikilink `[[<Entreprise>]]`
- `frontmatter.poste` — role title
- `frontmatter.target_profile` — `P1`–`P5` (for context only, not written to CR)
- `frontmatter.date_candidature` — used in Step 7 hal task title

**If the candidature is not found**: return a clear error pointing at `/log-application` first. Do NOT create a CR with a broken wikilink — that pollutes the vault.

## Step 3 — Find the prep note (for the wikilink, via `jobsearch-vault`)

Invoke `jobsearch-vault` to search `CRM-JobSearch/Entretiens/` for a note matching `Prep <Entreprise> — * — <DD-MM-YYYY>.md`.

- **Found** → capture the note name (without `.md`) for the `prep` frontmatter field.
- **Not found** → omit the `prep` field entirely. Do not warn the user (the prep note may have been skipped or created manually).

## Step 4 — Idempotency check for the CR note

Before creating, invoke `jobsearch-vault` to search `CRM-JobSearch/Entretiens/` for a note matching `CR <Entreprise> — * — <DD-MM-YYYY>.md` (exact date, case-insensitive).

- **Found** → ask `jobsearch-vault` to update the note (`update_frontmatter`) refreshing `feeling`, `suivi_envoye`, `interlocuteurs`, `format`, `heure`, and the body sections. Report to the user that an existing CR was updated, not created. Skip to Step 5.
- **Not found** → proceed to create.

## Step 5 — Create the CR note (via `jobsearch-vault`)

Invoke `jobsearch-vault` and ask it to **create a note** with this structured request. Naming convention: `CR <Entreprise> — <Interlocuteurs joined " "> — <DD-MM-YYYY>.md`, em-dash separators (` — ` with spaces around the em-dash):

```json
{
  "name": "CR <Entreprise> — <Interlocuteurs> — <DD-MM-YYYY>",
  "type": "entretien",
  "folder": "CRM-JobSearch/Entretiens",
  "fields": {
    "categorie": "Compte-rendu",
    "date": "<YYYY-MM-DD>",
    "format": "<Teams|Meet|Présentiel>",
    "heure": "<HH:MM–HH:MM>",
    "opportunite": "[[<Poste> — <Entreprise>]]",
    "interlocuteurs": ["<name1>", "<name2>"],
    "type_entretien": "<RH|Technique|Manager|Final>",
    "feeling": "<🔥|🟡|❌>",
    "suivi_envoye": false,
    "prep": "[[<Prep note name>]]"
  },
  "body": "## Notes clés\n\n<notes libres>\n\n## Questions posées\n\n<questions et réponses>\n\n## 🏢 Lecture employeur — BANT\n\n- **B — Comp/Budget** (fourchette confirmée ? fixe + variable + equity ?) : <réponse>\n- **A — Autorité** (qui décide ? étapes restantes ? combien d'interlocuteurs ?) : <réponse>\n- **N — Besoin précis** (quel problème je viens résoudre ? succès à J+30/J+90 ?) : <réponse>\n- **T — Timeline** (quand veulent-ils décider ? urgence du recrutement ?) : <réponse>\n\n## 🪞 Lecture Renaud — Fit\n\n- **Feeling global** : <🔥|🟡|❌>\n- **Ce qui m'a convaincu** : <...>\n- **Ce qui me questionne** : <...>\n- **Questions encore ouvertes** : <...>\n\n## Next steps\n\n- [ ] <action 1>\n"
}
```

See `docs/bant-cr-template.md` for the canonical version of this body template and the reasoning behind the `feeling` / `type_entretien` enum choices — this JSON payload must stay in sync with it.

**Field rules:**
- Omit `prep` entirely if Step 3 found nothing (do not pass an empty string or null).
- `suivi_envoye: false` is mandatory — drives follow-up tracking.
- `categorie: "Compte-rendu"` verbatim (accent required — it is an enum value).

**Warning contract:**
- `prep`, `format`, `heure` are not in the `entretien` native schema → each expects a warning `unknown field '<name>'` at exit 0. Apply AC1: exit 0 + these warnings → ACCEPT (non-blocking). Do not retry without the fields.
- **Exit 0 + any OTHER stderr warning** → surface verbatim to the user, then proceed.
- **Non-zero exit** → FAIL HARD: report `❌ Échec création CR — <stderr>` and do NOT proceed to Steps 6–8.

## Step 6 — Advance the opportunité (via `jobsearch-vault`)

Ask `jobsearch-vault` to update the candidature note (`update_frontmatter`) setting:

```json
{ "statut": "🔄 Relance à faire" }
```

**If Step 1.10 captured a confirmed next-step date**, include it in the same `update_frontmatter` call:

```json
{ "statut": "🔄 Relance à faire", "prochain_rdv": "<YYYY-MM-DD>" }
```

`prochain_rdv` is a native `opportunite-js` field — no warning expected. Omit it entirely when no next date was confirmed; do not write a placeholder.

**If `update_frontmatter` fails** after Step 5 succeeded, report and continue:

```
⚠️  Statut opportunité NON mis à jour (CR créé OK).
    Erreur   : <stderr>
    Recovery : mettre à jour manuellement le statut dans
               CRM-JobSearch/Opportunites/<Poste> — <Entreprise>.md
               statut → "🔄 Relance à faire"
```

## Step 7 — Close the prep hal task

The prep task was created by `interview-prep` with title `"Entretien <type_entretien> — <Entreprise> — <DD-MM-YYYY>"`.

**Find it:** `mcp__plugin_hal_hal-mcp__list_tasks(workspace_slug="renaud", tags=["jobsearch"])`. The response has the shape `{tasks: [...], total: <n>, returned: <n>, truncated: <bool>}` — search `.tasks`, not the raw response, for a non-closed task whose title starts with `"Entretien"` and contains the `entreprise` name (case-insensitive substring match). Take the closest match by interview date.

- **Found** → `mcp__plugin_hal_hal-mcp__update_task_status(workspace_slug="renaud", task_id=<id>, status="done")`.
- **Not found and `truncated` is `false`** → silently skip (already closed, or never created — both are normal).
- **Not found and `truncated` is `true`** → the search only covered the newest `returned` of `total` tasks; do not assume the prep task never existed. Skip closing it, but prepend to the Step 9 report:

```
⚠️  Tâche hal prep introuvable dans une lecture tronquée (<returned>/<total>) — non clôturée, à vérifier manuellement.
```
- **`update_task_status` fails** → prepend to the Step 9 report and continue:

```
⚠️  Tâche hal prep NON clôturée (<error>) — relance créée quand même.
```

## Step 8 — Create the post-interview relance hal task

**Idempotency:** call `mcp__plugin_hal_hal-mcp__list_tasks(workspace_slug="renaud", tags=["jobsearch"])`. As in Step 7, read tasks from `.tasks`. Skip creation if a non-closed task titled exactly `"Relance — <Entreprise> — <date_entretien>"` already exists. If `list_tasks` fails, proceed anyway and prepend:

```
⚠️ idempotency pre-check failed (<error>) — attempting create; may duplicate if already present.
```

If `truncated` is `true`, the pre-check may have missed an older duplicate beyond the cut — proceed with `create_task` anyway and prepend:

```
⚠️ idempotency pre-check was partial (<returned>/<total> tasks read) — a duplicate beyond the cut would not have been caught.
```

Invoke `mcp__plugin_hal_hal-mcp__create_task` exactly once:

```
mcp__plugin_hal_hal-mcp__create_task(
  workspace_slug = "renaud",
  title          = "Relance — <Entreprise> — <YYYY-MM-DD entretien>",
  description    = "Relance post-entretien <type_entretien> avec <Interlocuteurs>. CR : CRM-JobSearch/Entretiens/CR <Entreprise> — <Interlocuteurs> — <DD-MM-YYYY>.md",
  tags           = ["jobsearch"],
  due_date       = "<YYYY-MM-DD entretien + 7d>"
)
```

Note: the title uses the **interview date** (not the candidature date) — this distinguishes it from the `log-application` relance and makes the follow-up timeline explicit.

**Failure handling.** If `create_task` fails but Step 5 succeeded:

```
⚠️  Half-state — CR logué, relance NON créée dans hal.
    Erreur     : <error>
    Impact     : la relance n'apparaîtra pas dans /briefing.
    Recovery A : re-run /log-cr (Steps 4–6 idempotency court-circuite le vault)
    Recovery B : créer manuellement une tâche hal renaud
                 · tags: ["jobsearch"]
                 · title: "Relance — <Entreprise> — <YYYY-MM-DD entretien>"
                 · due_date: <YYYY-MM-DD +7d>
```

Do NOT fire Step 9's success report on a full half-state (Step 5 OK + Step 8 fail).

## Step 9 — Report to the user (in French)

```
✅ CR logué — <type_entretien> chez <Entreprise> (<format>, <heure>)
   📁 Note       : CRM-JobSearch/Entretiens/CR <Entreprise> — <Interlocuteurs> — <DD-MM-YYYY>.md
   <feeling> Feeling   : <feeling>
   🔄 Statut opp : 🔄 Relance à faire (mis à jour)
   🗓️ Prochain rdv : <YYYY-MM-DD> (omettre cette ligne si Step 1.10 n'a rien capturé)
   ✓  Tâche prep : "Entretien <type> — <Entreprise> — …" clôturée dans hal
                   (omettre cette ligne si tâche non trouvée)
   📋 Relance    : due <YYYY-MM-DD +7d> — tâche hal renaud/jobsearch créée, apparaîtra dans /briefing
```

If `suivi_envoye: false` (always the case after creation), suggest:

> 💡 Pense à envoyer un message de remerciement sous 24h. Met à jour `suivi_envoye → true` dans la note quand c'est fait.

## Step 10 — Constraints (load-bearing)

- **All vault I/O via `jobsearch-vault`.** NEVER `Read` or `Write` the vault filesystem directly.
- **`categorie: "Compte-rendu"` verbatim** (accent required). Wrong spelling breaks the note type enum and the vault dashboard filters.
- **`prep`, `format`, `heure` are non-schematized.** Each expects a warning `unknown field '<name>'` at exit 0 → ACCEPT (AC1 contract). Do not retry without them; do not patch the schema from here.
- **`suivi_envoye: false` is mandatory.** Do not omit — it drives follow-up tracking in the vault.
- **`feeling` is `🔥`/`🟡`/`❌`** — an intensity read on the interview outcome, not a mood face. **`type_entretien`** stays `RH`/`Technique`/`Manager`/`Final`, matching `interview-prep`'s enum on the same field — do not add a value here without also adding it there.
- **The `🪞 Lecture Renaud — Fit` body section is mandatory, never drop it.** It's Renaud's own subjective read (fit, doubts, open questions) — distinct from the `🏢 Lecture employeur — BANT` section, which is the employer's read. A CR without the Fit section doesn't help decide on the relance.
- **`prochain_rdv` is written on the opportunité only when Step 1.10 captured a confirmed date.** Never guess or default it.
- **Closing the hal prep task uses `status="done"`** (hal vocabulary), not vault vocabulary like `Terminé`.
- **Relance title uses the interview date** (`"Relance — <Entreprise> — <YYYY-MM-DD entretien>"`), NOT the candidature date. This avoids collision with the existing `log-application` relance.
- **Blue Green hard stop at Step 0.** The vault is jobsearch-only. No CRM/opportunity data from Blue Green goes here — use `/crm log` in bluegreen-marketplace.
- **BANT + Fit template** is documented in `docs/bant-cr-template.md` — the canonical body template and the single source of truth for the `feeling`/`type_entretien` enums. Reference it when the user's notes are sparse, and keep Step 5's JSON payload in sync with it. The equivalent Blue Green template lives in `bluegreen-marketplace/plugins/hal/skills/crm/SKILL.md` (`/crm log`).
- **Em-dash separators** (` — ` with spaces) in every filename. Hyphens or `--` break vault filename matching.
- **Compose, do not reimplement.** This skill is orchestration — vault writes and hal MCP calls are the primitives.
