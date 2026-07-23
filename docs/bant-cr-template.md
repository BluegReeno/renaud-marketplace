# BANT CR Template — Shared Reference

This template is used by two entry points that write to different backends:

1. **`renaud-marketplace/plugins/jobsearch/skills/log-cr`** — writes `entretien` (Compte-rendu) notes to the Obsidian jobsearch vault (`CRM-JobSearch/Entretiens/`).
2. **`bluegreen-marketplace/plugins/hal/skills/crm` (`/crm log`)** — logs interactions via `mcp__plugin_hal_hal-mcp__log_interaction` to the `blue-green` workspace CRM.

Both use the same Markdown structure below. If you update this template, check that `/crm log` in bluegreen-marketplace is aligned — the two must not diverge.

---

## Obsidian `entretien` frontmatter (Compte-rendu)

```yaml
---
categorie: "Compte-rendu"
date: YYYY-MM-DD
opportunite: "[[<Poste> — <Entreprise>]]"
interlocuteurs:
  - <Prénom Nom>
type_entretien: <RH|Technique|Manager|Final>
feeling: <😊|😐|😟>
suivi_envoye: false
prep: "[[Prep <Entreprise> — <Interlocuteurs> — <DD-MM-YYYY>]]"   # omit if no prep note
---
```

Filename: `CR <Entreprise> — <Interlocuteurs> — <DD-MM-YYYY>.md`
Folder: `CRM-JobSearch/Entretiens/`

---

## Body — BANT structure

```markdown
## Notes clés

<notes libres — ce qui a été dit, dynamique de l'échange, impressions générales>

## Questions posées

- Q : <question posée par Renaud>
  R : <réponse de l'interlocuteur>

## BANT extrait

- **Budget :** <enveloppe budgétaire discutée, fourchette de rémunération, ou absence de contrainte>
- **Authority :** <décideur réel, niveau d'autonomie de l'interlocuteur dans le processus>
- **Need :** <besoin exprimé, douleur identifiée, urgence, why-now>
- **Timeline :** <horizon de décision, deadline interne, priorité vs autres projets>

## Next steps

- [ ] <action 1 — ex. envoyer un message de remerciement>
- [ ] <action 2 — ex. préparer un cas technique pour le prochain entretien>
```

---

## BANT extraction — targeted questions to ask the user

When the user's notes are sparse, ask these questions to fill the BANT:

| Field | Question |
|-------|----------|
| **Budget** | "Ont-ils mentionné une fourchette de salaire ou un package ? Y a-t-il un budget figé ?" |
| **Authority** | "Qui prend la décision finale ? L'interlocuteur recrute-t-il seul ou valide-t-il avec quelqu'un d'autre ?" |
| **Need** | "Quel problème essaient-ils de résoudre avec ce recrutement ? Qu'est-ce qui manque actuellement dans l'équipe ?" |
| **Timeline** | "Ont-ils évoqué une date de prise de poste ou une deadline pour décider ?" |

Leave `<à compléter>` for any field the user cannot answer — do not invent data.

---

## Feeling guide

| Emoji | Signification |
|-------|--------------|
| 😊 | Très bon ressenti — bon feeling mutuel, suite probable |
| 😐 | Neutre / incertain — manque d'éléments pour évaluer |
| 😟 | Mauvais ressenti — misalignment ou feedback négatif perçu |
