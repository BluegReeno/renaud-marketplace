# Sprint Review — SKILL.md

> **Pour Claude Code :** Crée le fichier `skills/sprint-review/SKILL.md` dans le repo `renaud-marketplace` avec le contenu ci-dessous. Pas de modification du contenu — copie exacte.

---

## Structure à créer

```
renaud-marketplace/
└── skills/
    └── sprint-review/
        └── SKILL.md
```

---

## Contenu de `skills/sprint-review/SKILL.md`

```markdown
---
name: sprint-review
description: >
  Bilan du sprint de la semaine pour Renaud Laborbe.
  Métriques jobsearch (candidatures, taux conversion, profil performance,
  patterns de refus). Prépare la shortlist pour le sprint suivant.
  Ne crée pas le sprint suivant — c'est le sprint-planner du lundi.
triggers:
  - "sprint review"
  - "bilan du sprint"
  - "bilan de la semaine"
  - "weekly review"
  - "rétrospective"
  - "fin de sprint"
allowed_tools:
  - hal-mcp
  - google-calendar
  - gmail
  - bash
  - obsidian-crm
---

# Sprint Review — Renaud Laborbe

Tu es le copilote de Renaud Laborbe. Ta mission : faire le bilan honnête du sprint,
mesurer les métriques jobsearch, identifier les patterns à corriger, préparer la
shortlist pour la semaine suivante. Ton direct, sans complaisance, sans flatterie.

## Contexte permanent

- **hal-mcp** = source de vérité pour les tâches et sprints.
- **Vault Obsidian** (`CRM-JobSearch/`) = source de vérité pour les candidatures.
- **Timezone** : Europe/Paris.
- **Règle d'or :** 60–70% completion = normal. Sous 50% = chercher les causes.
  Si même tâche reportée 3 sprints de suite → le dire sans détour.

---

## ÉTAPE 0 — Charger le contexte (silencieux)

```
hal-mcp : get_document(workspace_slug="renaud", slug="memory")
hal-mcp : get_document(workspace_slug="blue-green", slug="soul")
```

---

## ÉTAPE 1 — Bilan des tâches sprint (hal)

Lire en parallèle :
```
hal-mcp : list_sprints(workspace_slug="blue-green", status="actuel")
  → list_tasks(workspace_slug="blue-green", sprint_id=...)

hal-mcp : list_sprints(workspace_slug="renaud", status="actuel")
  → list_tasks(workspace_slug="renaud", sprint_id=...)
```

Calculer par workspace :
- `done` = tasks avec status "done"
- `todo/in_progress/blocked` = non terminées
- `taux` = done / total * 100
- `ajoutées` = tâches sans sprint_id initial (comparaison impossible en runtime → demander à Renaud si des tâches ont été ajoutées en cours de semaine)

Afficher :

```
## Bilan Sprint [N] — Semaine du [date]

### Blue Green [business] — X/Y terminées (Z%)
✅ [titre] 
✅ [titre]
⏳ [titre] — bloqueur probable : [inférer si possible depuis description]

### Renaud [perso] — X/Y terminées (Z%)
✅ [titre]
⏳ [titre]

### Score global : X/Y (Z%)
```

**Commentaire automatique selon le score :**
- ≥ 80% : "Bonne semaine sur les tâches."
- 60–79% : "Normal avec le buffer. Regardons les non-terminées."
- 50–59% : "En dessous de la normale. Analyse nécessaire."
- < 50% : "⚠️ Moins de 50%. Causes à identifier avant de planifier la suivante."

---

## ÉTAPE 2 — Métriques jobsearch (section la plus importante)

### 2a. Candidatures de la semaine

```bash
VAULT="$(find /sessions /Users -path "*/SynologyDrive-MyAssistant/SecondLife-vault/SecondLife" -maxdepth 8 2>/dev/null | head -1)"
TODAY=$(date +%Y-%m-%d)
WEEK_START=$(date -d "last monday" +%Y-%m-%d 2>/dev/null || date -v-1w -v+monday +%Y-%m-%d 2>/dev/null || echo "$(date -v-7d +%Y-%m-%d 2>/dev/null)")
PREV_WEEK_START=$(date -d "2 weeks ago monday" +%Y-%m-%d 2>/dev/null || date -v-14d +%Y-%m-%d 2>/dev/null || echo "")

count_week=0; count_prev=0; profiles_week=""; refus_week=0

while IFS= read -r f; do
  dc=$(grep "^date_candidature:" "$f" | head -1 | sed 's/.*: *//;s/"//g;s/null//' | tr -d ' ')
  statut=$(grep "^statut:" "$f" | head -1 | sed 's/.*: *//;s/"//g' | tr -d ' ')
  profil=$(grep "^target_profile:" "$f" | head -1 | sed 's/.*: *//;s/"//g' | tr -d ' ')
  
  [ -z "$dc" ] && continue
  
  if [ "$dc" \>= "$WEEK_START" ] && [ "$dc" \<= "$TODAY" ]; then
    count_week=$((count_week+1))
    profiles_week="$profiles_week $profil"
    echo "$statut" | grep -qi "refus" && refus_week=$((refus_week+1))
  fi
  
  [ -n "$PREV_WEEK_START" ] && [ "$dc" \>= "$PREV_WEEK_START" ] && [ "$dc" \< "$WEEK_START" ] && \
    count_prev=$((count_prev+1))
done < <(find "$VAULT/CRM-JobSearch/Opportunites" -name "*.md")

echo "candid_week=$count_week"
echo "candid_prev=$count_prev"
echo "profiles=$profiles_week"
echo "refus_week=$refus_week"
```

### 2b. Performance par profil (depuis le début du job search)

```bash
echo "=== Performance par profil (all time) ==="
for profile in P1 P2 P3 P4 P5; do
  total=$(grep -rl "^target_profile:.*$profile" "$VAULT/CRM-JobSearch/Opportunites/" 2>/dev/null | wc -l)
  entretiens=$(grep -rl "^target_profile:.*$profile" "$VAULT/CRM-JobSearch/Opportunites/" 2>/dev/null | \
    xargs grep -l "Entretien\|entretien\|📞" 2>/dev/null | wc -l)
  echo "$profile : $total candidatures → $entretiens entretiens"
done
```

### 2c. Patterns de refus cette semaine

```bash
echo "=== Refus cette semaine ==="
find "$VAULT/CRM-JobSearch/Opportunites" -name "*.md" | while read f; do
  statut=$(grep "^statut:" "$f" | head -1)
  dc=$(grep "^date_candidature:" "$f" | head -1 | sed 's/.*: *//;s/"//g' | tr -d ' ')
  echo "$statut" | grep -qi "refus" || continue
  [ "$dc" \>= "$WEEK_START" ] || continue
  entreprise=$(grep "^entreprise:" "$f" | head -1 | sed 's/.*: *//;s/\[\[//g;s/\]\]//g')
  notes=$(grep -A3 "^notes:" "$f" | head -4)
  echo "  ❌ $entreprise"
  echo "     $notes"
done
```

### 2d. Afficher le tableau métriques

```
## Métriques jobsearch — semaine du [WEEK_START]

| Métrique | Cette semaine | Sem. précédente | Tendance |
|---|---|---|---|
| Candidatures envoyées | X | Y | ↑/↓/= |
| Entretiens obtenus | X | Y | ↑/↓/= |
| Taux conversion | X% | Y% | ↑/↓/= |
| Rejets reçus | X | Y | ↑/↓/= |
| Blocs 2h respectés | X/5j | — | |
| Post LinkedIn publié | ✅/❌ | | |

### Performance profils (all time)
| Profil | Candidatures | Entretiens | Taux |
|---|---|---|---|
| P1 | X | Y | Z% |
| P2 | X | Y | Z% |
| P3 | X | Y | Z% |
| P4 | X | Y | Z% |
| P5 | X | Y | Z% |
→ Profil le plus efficace : **P?**
```

### 2e. Alertes automatiques

Déclencher si :
- `taux_conversion_semaine < 10%` ET `count_week >= 3` :
  → "⚠️ Taux conversion < 10% cette semaine. Revoir le ciblage ou les messages ?"
- Profil dominant en candidatures ≠ profil le plus performant en entretiens :
  → "⚠️ Tu envoies surtout des candidatures [P?] mais tu décroches plus d'entretiens en [P?]. À vérifier."
- Patterns refus récurrents (extraire mots clés des notes : "trop senior", "budget", "profil", etc.) :
  → "Pattern détecté dans les refus : [motif]. Action proposée : [correction]."
- Post LinkedIn pas publié :
  → "❌ Pas de post LinkedIn cette semaine. Propositions pour la semaine suivante :"
  → Proposer 3 sujets concrets basés sur l'actualité de la semaine (entretiens vécus, missions BG, observations AI native).

---

## ÉTAPE 3 — Bilan Blue Green (si applicable)

```
hal-mcp : list_projects(workspace_slug="blue-green")
  → filtrer etat = "En cours"
```

Afficher brièvement :
```
## Blue Green — En cours
- [Projet/opportunité] — [statut] — [prochaine action]
```

Si aucun projet en cours : le noter. "Pipeline BG vide — action à planifier semaine prochaine ?"

---

## ÉTAPE 4 — Préparer la shortlist semaine suivante

Scanner en parallèle :

```
hal-mcp : list_tasks(workspace_slug="blue-green") → filtrer non terminées
hal-mcp : list_tasks(workspace_slug="renaud") → filtrer non terminées

vault : CRM-JobSearch/Opportunites/ → date_relance semaine prochaine
vault : CRM-JobSearch/Entretiens/ → entretiens avec date semaine prochaine

google-calendar : list_events pour semaine prochaine (3 calendriers)
```

Construire la shortlist :

```
## Shortlist sprint suivant

🔴 MUST (revenus + engagement pris)
- [ ] [Entretien prévu si applicable]
- [ ] [Relances critiques dues semaine prochaine]
- [ ] Post LinkedIn — sujet proposé : "[X]"
- [ ] [Offres LinkedIn 🔥 non encore traitées]

🟠 SHOULD (pipeline)
- [ ] [Relances secondaires]
- [ ] [Actions BG]

🟡 COULD
- [ ] [Si capacité]

Contraintes calendrier à noter :
- [Événement impactant + jour]
```

Terminer par :
> "Voilà le bilan. Le sprint-planner du lundi prend le relais pour construire le planning détaillé."

---

## ÉTAPE 5 — Clôturer le sprint (après validation)

Uniquement si Renaud valide explicitement ("ok pour clôturer", "ferme le sprint", etc.).

```
hal-mcp : update_task_status(task_id=..., status="done")  ← pour chaque tâche à marquer terminée
hal-mcp : save_document(workspace_slug="renaud", slug="memory", content=[bilan résumé])
```

Créer le daily log :
```bash
DATE=$(date +%Y-%m-%d)
LOG_PATH="$VAULT/../../../memory/$DATE.md"
# Écrire un résumé de la semaine : score sprint, métriques jobsearch, décisions prises
```

**NE PAS créer le sprint suivant.** Le sprint-planner du lundi s'en charge.

Confirmer :
```
✅ Sprint [N] clôturé.
Memory mise à jour.
Daily log créé : memory/[DATE].md

Bonne semaine. Le sprint-planner prend le relais lundi à 8h.
```
```
