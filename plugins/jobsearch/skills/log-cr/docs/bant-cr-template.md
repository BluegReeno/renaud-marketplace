# BANT CR Template — canonical source

Single source of truth for the `log-cr` body template and its two
free-string enums (`feeling`, `type_entretien`). `SKILL.md` references this
file instead of duplicating the template — edit here, not there.

## Body template

```markdown
## Notes clés

<notes libres>

## Questions posées

<questions et réponses>

## 🏢 Lecture employeur — BANT

- **B — Comp/Budget** (fourchette confirmée ? fixe + variable + equity ?) : <réponse>
- **A — Autorité** (qui décide ? étapes restantes ? combien d'interlocuteurs ?) : <réponse>
- **N — Besoin précis** (quel problème je viens résoudre ? succès à J+30/J+90 ?) : <réponse>
- **T — Timeline** (quand veulent-ils décider ? urgence du recrutement ?) : <réponse>

## 🪞 Lecture Renaud — Fit

- **Feeling global** : 🔥 / 🟡 / ❌
- **Ce qui m'a convaincu** :
- **Ce qui me questionne** :
- **Questions encore ouvertes** :

## Next steps

- [ ] <action 1>
```

The BANT section is phrased as directive questions on purpose — it prompts
better extraction from sparse notes than a blank `**Budget :** <budget>`
field would. Ask these questions back to the user when their notes don't
already answer them.

The Fit section is the subjective counterpart to the BANT's employer
reading: BANT is how the employer sees the fit, Fit is how Renaud sees it.
Never drop it — a CR without it doesn't help decide on a relance.

## Enums (frontmatter)

- **`feeling`** — `🔥` / `🟡` / `❌`. Chosen over face emoji because it
  carries interview-outcome intensity (hot lead / lukewarm / dead) rather
  than a mood reading — matches what the Fit section's "Feeling global"
  bullet expects.
- **`type_entretien`** — `RH` / `Technique` / `Manager` / `Final`. Kept in
  sync with `interview-prep`'s enum (same field, same note type) — do not
  add `Fit` back here without also adding it to `interview-prep`, or the
  two skills drift on the same schema field.
- **`suivi_envoye`** — `bool`, always written, defaults to `false` at
  creation. Drives follow-up-message tracking; never omit.

## Frontmatter fields not in the native `entretien` schema

`prep`, `format`, `heure` are not declared in
`jobsearch-vault/scripts/note_schemas.py`'s `entretien` schema. Writing
them produces a non-blocking `unknown field '<name>'` warning at exit 0 —
expected and accepted (see `SKILL.md`'s warning contract). Do not retry
without them and do not patch the schema from this skill.
