# BANT CR Template — Shared Reference

This template is used by two entry points that write to different backends:

1. **`renaud-marketplace/plugins/jobsearch/skills/log-cr`** — writes `entretien` (Compte-rendu) notes to the Obsidian jobsearch vault (`CRM-JobSearch/Entretiens/`).
2. **`bluegreen-marketplace/plugins/hal/skills/crm` (`/crm log`)** — logs interactions via `mcp__plugin_hal_hal-mcp__log_interaction` to the `blue-green` workspace CRM.

Both use the same Markdown structure below. If you update this template, check that `/crm log` in bluegreen-marketplace is aligned — the two must not diverge.

> **This file is the source of truth for the body structure and for the `feeling` /
> `type_entretien` enums.** `log-cr`'s Step 5 JSON payload must stay byte-compatible with the
> body below. It drifted once (an older revision of this file listed `😊/😐/😟` and a single
> "BANT extrait" section, neither of which the skill has ever written) — check both sides
> when you touch either.

---

## Obsidian `entretien` frontmatter (Compte-rendu)

```yaml
---
categorie: "Compte-rendu"
date: YYYY-MM-DD
format: <Teams|Meet|Zoom|Présentiel>          # free text, not an enum
heure: "HH:MM–HH:MM"
opportunite: "[[<Poste> — <Entreprise>]]"
interlocuteurs:
  - <Prénom Nom>
type_entretien: <RH|Technique|Manager|Final>
feeling: <🔥|🟡|❌>
suivi_envoye: false
prep: "[[Prep <Entreprise> — <Interlocuteurs> — <DD-MM-YYYY>]]"   # omit if no prep note
granola_id: <meeting UUID>                     # omit if no transcript was found
---
```

Filename: `CR <Entreprise> — <Interlocuteurs> — <DD-MM-YYYY>.md`
Folder: `CRM-JobSearch/Entretiens/`

`format`, `heure`, `prep` and `granola_id` are not in the `entretien` native schema. Each
produces an `unknown field '<name>'` warning at exit 0 — non-blocking, expected, do not
retry without them.

---

## Body — the five sections, in this order

```markdown
## Notes clés

<notes libres — ce qui a été dit, dynamique de l'échange, impressions générales>

## Questions posées

- Q : <question posée par Renaud>
  R : <réponse de l'interlocuteur>

## 🏢 Lecture employeur — BANT

- **B — Comp/Budget** (fourchette confirmée ? fixe + variable + equity ?) : <réponse>
- **A — Autorité** (qui décide ? étapes restantes ? combien d'interlocuteurs ?) : <réponse>
- **N — Besoin précis** (quel problème je viens résoudre ? succès à J+30/J+90 ?) : <réponse>
- **T — Timeline** (quand veulent-ils décider ? urgence du recrutement ?) : <réponse>

## 🪞 Lecture Renaud — Fit

- **Feeling global** : <🔥|🟡|❌>
- **Ce qui m'a convaincu** : <...>
- **Ce qui me questionne** : <...>
- **Questions encore ouvertes** : <...>

## Next steps

- [ ] <action 1 — ex. envoyer un message de remerciement>
- [ ] <action 2 — ex. préparer un cas technique pour le prochain entretien>
```

The two reads are not interchangeable. **🏢 BANT is the employer's read** — what they said
about budget, decision path, need and timing. **🪞 Fit is Renaud's own read** — never drop it:
a CR without it does not help decide whether to relancer.

---

## Where the content comes from

`log-cr` Step 1bis pulls the Granola transcript of the meeting (`mcp__Granola__list_meetings`
→ `mcp__Granola__get_meeting_transcript`) when one exists, and fills from it:

| Filled from the transcript | Asked from Renaud, always |
|---|---|
| `heure` (start), `interlocuteurs`, `format` when a platform is named out loud | `feeling` |
| `## Notes clés`, `## Questions posées`, `## Next steps` | the whole `🪞 Lecture Renaud — Fit` section |
| the four `🏢 BANT` lines | `type_entretien`, confirmation of `prochain_rdv` |

Two rules govern the extraction:

- **No transcript, no claim.** Anything the transcript does not state stays `<à compléter>`.
  Never bridge a gap with a plausible guess — an invented BANT line reads as fact months later.
- **Transcribed numbers are approximate.** Speech-to-text mangles figures and currencies.
  Write `≈ 80 k€, à reconfirmer`, never a clean rounded number the transcript did not give.

No transcript (not recorded, connector down, no match) → the questions below are the
fallback path, and the skill announces the miss rather than failing.

### BANT extraction — targeted questions to ask the user

| Field | Question |
|-------|----------|
| **Budget** | "Ont-ils mentionné une fourchette de salaire ou un package ? Y a-t-il un budget figé ?" |
| **Authority** | "Qui prend la décision finale ? L'interlocuteur recrute-t-il seul ou valide-t-il avec quelqu'un d'autre ?" |
| **Need** | "Quel problème essaient-ils de résoudre avec ce recrutement ? Qu'est-ce qui manque actuellement dans l'équipe ?" |
| **Timeline** | "Ont-ils évoqué une date de prise de poste ou une deadline pour décider ?" |

Leave `<à compléter>` for any field the user cannot answer — do not invent data.

---

## Feeling guide

`feeling` is an intensity read on the interview outcome, not a mood face.

| Emoji | Signification |
|-------|--------------|
| 🔥 | Très bon ressenti — bon feeling mutuel, suite probable |
| 🟡 | Neutre / incertain — manque d'éléments pour évaluer |
| ❌ | Mauvais ressenti — misalignment ou feedback négatif perçu |

`type_entretien` stays `RH` / `Technique` / `Manager` / `Final`, the same enum
`interview-prep` writes on the same field. Adding a value here means adding it there too.
