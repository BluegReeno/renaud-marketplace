# BANT CR Template — canonical source

Single source of truth for the `log-cr` CR body template, the
`## 🏢 BANT (agrégé)` template written onto the `opportunite-js`, and the
two free-string enums (`feeling`, `type_entretien`). `SKILL.md` references
this file instead of duplicating the templates — edit here, not there.

The BANT (employer's read) is never written into the CR body. It is
aggregated onto the matching `opportunite-js` instead (`log-cr` Step 7, via
`jobsearch-vault`'s `upsert_section.py`), so a company's BANT lives in one
traceable, growing place instead of being re-typed and scattered across
every `entretien` CR (issue #138).

## CR body template

```markdown
## Notes clés

<notes libres>

## Questions posées

<questions et réponses>

## 🪞 Lecture Renaud — Fit

- **Feeling global** : 🔥 / 🟡 / ❌
- **Ce qui m'a convaincu** :
- **Ce qui me questionne** :
- **Questions encore ouvertes** :

## Next steps

- [ ] <action 1>
```

The Fit section is Renaud's own subjective read (fit, doubts, open
questions) — distinct from the BANT, which is the employer's read and lives
on the opportunité. Never drop it — a CR without it doesn't help decide on
a relance.

## `## 🏢 BANT (agrégé)` template — written on the `opportunite-js`

```markdown
## 🏢 BANT (agrégé)

### B — Comp/Budget

- <date> — <interlocuteurs> (<type_entretien>) : « <contenu> » → [[CR <Entreprise> — <Interlocuteurs> — <DD-MM-YYYY>]]

### A — Autorité

- <date> — <interlocuteurs> (<type_entretien>) : « <contenu> » → [[CR <Entreprise> — <Interlocuteurs> — <DD-MM-YYYY>]]

### N — Besoin précis

- <date> — <interlocuteurs> (<type_entretien>) : « <contenu> » → [[CR <Entreprise> — <Interlocuteurs> — <DD-MM-YYYY>]]

### T — Timeline

- <date> — <interlocuteurs> (<type_entretien>) : « <contenu> » → [[CR <Entreprise> — <Interlocuteurs> — <DD-MM-YYYY>]]
```

The four directive questions still drive what `log-cr` Step 1.8 asks for
(from the user, or extracted from a Granola transcript) — they just never
land in the CR body anymore. Ask these back to the user when their notes
are sparse:

- **B — Comp/Budget** — fourchette confirmée ? fixe + variable + equity ?
- **A — Autorité** — qui décide ? étapes restantes ? combien d'interlocuteurs ?
- **N — Besoin précis** — quel problème je viens résoudre ? succès à J+30/J+90 ?
- **T — Timeline** — quand veulent-ils décider ? urgence du recrutement ?

**Aggregation rules (load-bearing):**
- **One sub-section per meeting per non-empty item.** Skip an item Step 1.8
  left unset — do not write an `<à compléter>` bullet, there is nothing to
  aggregate.
- **Append, never overwrite.** A later meeting's read that contradicts an
  earlier one is a *new* dated, attributed bullet next to the earlier one —
  never a replacement. The contradiction itself is signal worth keeping
  visible.
- **Traceability.** Every bullet is `<date> — <who> : « <what> » →
  [[<CR note>]]` — attributed and linked back to its source CR.
- **Dedup is exact-string only** (`upsert_section.py`'s contract) — a
  re-run of `log-cr` on an already-logged CR (Step 4 idempotency) reproduces
  the identical line and it is silently skipped, not duplicated. No
  semantic/paraphrase matching.

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

The `## 🏢 BANT (agrégé)` section on `opportunite-js` is unstructured body
content, not a frontmatter field — it has no `note_schemas.py` entry and
needs none.
