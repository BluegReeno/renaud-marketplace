---
name: sprint-review
description: >
  Bilan du sprint de la semaine pour Renaud Laborbe. Métriques jobsearch
  (candidatures, taux de conversion, profil performance, patterns de refus).
  Bilan Blue Green (projets en cours). Shortlist pour le sprint suivant.
  Ne crée pas le sprint suivant — c'est le sprint-planner qui s'en charge.
  Clôture le sprint dans hal uniquement après validation explicite.
  Utiliser quand Renaud dit "sprint review", "bilan du sprint", "bilan de la
  semaine", "weekly review", "rétrospective", "fin de sprint" — ou en mode
  schedule (vendredi après-midi automatique).
version: 0.4.2
allowed-tools: "mcp__hal-mcp__whoami mcp__hal-mcp__list_sprints mcp__hal-mcp__list_tasks mcp__hal-mcp__list_projects mcp__hal-mcp__update_task_status mcp__hal-mcp__get_document mcp__hal-mcp__save_document mcp__claude_ai_Google_Calendar__list_events Skill(jobsearch-vault) Bash"
---

# Sprint Review — Renaud Laborbe

Tu es le copilote de Renaud Laborbe. Ta mission : faire le bilan honnête du sprint, mesurer les métriques jobsearch, identifier les patterns à corriger, préparer la shortlist pour la semaine suivante. Ton direct, sans complaisance, sans flatterie.

## Contexte permanent

- **hal-mcp** = source de vérité pour les tâches et sprints.
- **Vault Obsidian** (`CRM-JobSearch/`) = source de vérité pour les candidatures.
- **Timezone** : Europe/Paris.
- **Règle d'or :** 60–70% completion = normal. Sous 50% = chercher les causes. Si même tâche reportée 3 sprints de suite → le dire sans détour.

## Mode scheduled vs conversationnel

En **mode schedule** (vendredi après-midi automatique) : le skill s'exécute de façon entièrement autonome. Il produit le bilan complet (étapes 0–4), puis présente la liste des tâches à clore avec une demande de confirmation. Il **ne clôture jamais le sprint ni n'écrit dans hal sans validation explicite de Renaud**.

En **mode conversationnel** : comportement identique pour les étapes 0–4. Étape 5 déclenchée uniquement par "clôture", "ferme le sprint", "ok pour clôturer" ou équivalent.

---

## ÉTAPE 0 — Charger le contexte (silencieux, pas affiché)

En parallèle :

```
mcp__hal-mcp__get_document(workspace_slug="renaud", slug="memory")
mcp__hal-mcp__get_document(workspace_slug="blue-green", slug="soul")
```

Ne pas afficher le contenu brut. Utiliser pour calibrer le ton et les priorités.
Si un document est absent (404), continuer sans bloquer.

---

## ÉTAPE 1 — Bilan des tâches sprint (hal)

Probe hal : `mcp__hal-mcp__whoami`. Si échec → marquer `hal:DOWN <raison>` et sauter cette étape en rendant `⚠️ hal DOWN — <raison>`.

Lire en parallèle :

```
mcp__hal-mcp__list_sprints(workspace_slug="blue-green", status="actuel")
mcp__hal-mcp__list_sprints(workspace_slug="renaud", status="actuel")
```

Pour chaque workspace : prendre le premier élément de la liste (un seul sprint actif possible). Si la liste est vide → utiliser `list_tasks` sans `sprint_id` et noter `(aucun sprint actif — tâches ouvertes)`.

```
mcp__hal-mcp__list_tasks(workspace_slug="blue-green", sprint_id=<sprint_id_bg>)
mcp__hal-mcp__list_tasks(workspace_slug="renaud", sprint_id=<sprint_id_rn>)
```

Calculer par workspace :
- `done` = tasks avec `status == "done"`
- `non_terminées` = tasks avec `status != "done"` (todo | in_progress | blocked)
- `taux` = `len(done) / len(all) * 100` (0% si aucune tâche)

Afficher :

```
## Bilan Sprint [N] — Semaine du [date_lundi]–[date_vendredi]

### Blue Green [business] — X/Y terminées (Z%)
✅ [titre]
✅ [titre]
⏳ [titre] — [status] — bloqueur probable : [inférer si possible depuis description/tags]

### Renaud [perso] — X/Y terminées (Z%)
✅ [titre]
⏳ [titre] — [status]

### Score global : X/Y (Z%)
```

**Commentaire automatique selon le score :**
- ≥ 80% : "Bonne semaine sur les tâches."
- 60–79% : "Normal avec le buffer. Regardons les non-terminées."
- 50–59% : "En dessous de la normale. Analyse nécessaire."
- < 50% : "⚠️ Moins de 50%. Causes à identifier avant de planifier la suivante."

---

## ÉTAPE 2 — Métriques jobsearch (section la plus importante)

Invoquer `jobsearch-vault` pour compter les candidatures actives. En parallèle, exécuter les scripts bash ci-dessous.

### 2a. Candidatures de la semaine

```bash
VAULT="$(find /sessions /Users -path "*/SynologyDrive-MyAssistant/SecondLife-vault/SecondLife" -maxdepth 8 2>/dev/null | head -1)"
TODAY=$(date +%Y-%m-%d)
WEEK_START=$(date -d "last monday" +%Y-%m-%d 2>/dev/null || date -v-1w -v+monday +%Y-%m-%d 2>/dev/null || date -v-7d +%Y-%m-%d 2>/dev/null)
PREV_WEEK_START=$(date -d "2 weeks ago monday" +%Y-%m-%d 2>/dev/null || date -v-14d +%Y-%m-%d 2>/dev/null || echo "")

count_week=0; count_prev=0; refus_week=0

while IFS= read -r f; do
  dc=$(grep "^date_candidature:" "$f" | head -1 | sed 's/.*: *//;s/"//g;s/null//' | tr -d ' ')
  statut=$(grep "^statut:" "$f" | head -1 | sed 's/.*: *//;s/"//g' | tr -d ' ')
  [ -z "$dc" ] && continue
  if [ "$dc" \>= "$WEEK_START" ] && [ "$dc" \<= "$TODAY" ]; then
    count_week=$((count_week+1))
    echo "$statut" | grep -qi "refus" && refus_week=$((refus_week+1))
  fi
  [ -n "$PREV_WEEK_START" ] && [ "$dc" \>= "$PREV_WEEK_START" ] && [ "$dc" \< "$WEEK_START" ] && \
    count_prev=$((count_prev+1))
done < <(find "$VAULT/CRM-JobSearch/Opportunites" -name "*.md" 2>/dev/null)

echo "WEEK_START=$WEEK_START"
echo "candid_week=$count_week"
echo "candid_prev=$count_prev"
echo "refus_week=$refus_week"
```

### 2b. Performance par profil (all time)

```bash
echo "=== Performance par profil ==="
for profile in P1 P2 P3 P4 P5; do
  total=$(grep -rl "^target_profile:.*$profile" "$VAULT/CRM-JobSearch/Opportunites/" 2>/dev/null | wc -l | tr -d ' ')
  entretiens=$(grep -rl "^target_profile:.*$profile" "$VAULT/CRM-JobSearch/Opportunites/" 2>/dev/null | \
    xargs grep -l "Entretien\|entretien\|📞" 2>/dev/null | wc -l | tr -d ' ')
  echo "$profile : $total candidatures → $entretiens entretiens"
done
```

### 2c. Patterns de refus cette semaine

```bash
WEEK_START_VAR="$WEEK_START"
echo "=== Refus cette semaine ==="
find "$VAULT/CRM-JobSearch/Opportunites" -name "*.md" 2>/dev/null | while IFS= read -r f; do
  statut=$(grep "^statut:" "$f" | head -1)
  dc=$(grep "^date_candidature:" "$f" | head -1 | sed 's/.*: *//;s/"//g' | tr -d ' ')
  echo "$statut" | grep -qi "refus" || continue
  [ -z "$dc" ] && continue
  [ "$dc" \< "$WEEK_START_VAR" ] && continue
  entreprise=$(grep "^entreprise:" "$f" | head -1 | sed 's/.*: *//;s/\[\[//g;s/\]\]//g')
  echo "  ❌ $entreprise"
done
```

### 2d. Relances dues semaine prochaine

```bash
NEXT_MON=$(date -d "next monday" +%Y-%m-%d 2>/dev/null || date -v+1w -v+monday +%Y-%m-%d 2>/dev/null)
NEXT_FRI=$(date -d "next friday" +%Y-%m-%d 2>/dev/null || date -v+1w -v+friday +%Y-%m-%d 2>/dev/null)
echo "=== Relances semaine prochaine ($NEXT_MON → $NEXT_FRI) ==="
find "$VAULT/CRM-JobSearch/Opportunites" -name "*.md" 2>/dev/null | while IFS= read -r f; do
  dr=$(grep "^date_relance:" "$f" | head -1 | sed 's/.*: *//;s/"//g;s/null//' | tr -d ' ')
  statut=$(grep "^statut:" "$f" | head -1)
  echo "$statut" | grep -qi "Refus\|Abandonné\|Archivé" && continue
  [ -n "$dr" ] && [ "$dr" \>= "$NEXT_MON" ] && [ "$dr" \<= "$NEXT_FRI" ] && \
    printf "  %s — %s\n" "$dr" "$(grep "^entreprise:" "$f" | head -1 | sed 's/.*: *//;s/\[\[//g;s/\]\]//g')"
done | sort
```

### 2e. Tableau métriques

Afficher :

```
## Métriques jobsearch — semaine du [WEEK_START]

| Métrique | Cette semaine | Sem. précédente | Tendance |
|---|---|---|---|
| Candidatures envoyées | X | Y | ↑/↓/= |
| Entretiens obtenus | X | Y | ↑/↓/= |
| Taux conversion | X% | Y% | ↑/↓/= |
| Rejets reçus | X | Y | ↑/↓/= |
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

### 2f. Alertes automatiques

Déclencher si :
- `taux_conversion < 10%` ET `count_week >= 3` → "⚠️ Taux conversion < 10% cette semaine. Revoir le ciblage ou les messages ?"
- Profil dominant en candidatures ≠ profil le plus performant en entretiens → "⚠️ Tu envoies surtout des candidatures [P?] mais tu décroches plus d'entretiens en [P?]."
- Post LinkedIn non détecté → "❌ Pas de post LinkedIn cette semaine. Propositions pour la suivante : [3 sujets concrets issus de l'actualité de la semaine]."
- Même tâche visible 3 sprints de suite → "⚠️ [titre] est reportée depuis 3 sprints. À trancher."

---

## ÉTAPE 3 — Bilan Blue Green

```
mcp__hal-mcp__list_projects(workspace_slug="blue-green")
```

Afficher les projets dont le stage n'est pas fermé/annulé :

```
## Blue Green — Projets en cours
- [Projet] — stage : [stage] — prochaine action : [inférer depuis description ou tags]
```

Si aucun projet actif : "Pipeline BG vide — action à planifier semaine prochaine ?"

---

## ÉTAPE 4 — Shortlist sprint suivant

Scanner en parallèle :

```
mcp__hal-mcp__list_tasks(workspace_slug="blue-green")  → filtrer non terminées + sans sprint_id
mcp__hal-mcp__list_tasks(workspace_slug="renaud")      → filtrer non terminées + sans sprint_id

mcp__claude_ai_Google_Calendar__list_events(
  calendarId="renaud@bluegreen.ai",
  timeMin="[lundi_prochain]T00:00:00+02:00",
  timeMax="[vendredi_prochain]T23:59:59+02:00"
)
mcp__claude_ai_Google_Calendar__list_events(
  calendarId="rlaborbe@gmail.com",
  timeMin="[lundi_prochain]T00:00:00+02:00",
  timeMax="[vendredi_prochain]T23:59:59+02:00"
)
mcp__claude_ai_Google_Calendar__list_events(
  calendarId="hah0feg81cofndkov7derd6g00@group.calendar.google.com",
  timeMin="[lundi_prochain]T00:00:00+02:00",
  timeMax="[vendredi_prochain]T23:59:59+02:00"
)
```

Afficher la shortlist avec les relances dues et les entretiens détectés via jobsearch-vault :

```
## Shortlist sprint suivant — semaine du [lundi_prochain]

🔴 MUST (revenus + engagement pris)
- [ ] [Entretien prévu semaine prochaine — depuis jobsearch-vault]
- [ ] [Relance due semaine prochaine — depuis vault]
- [ ] Post LinkedIn — sujet proposé : "[proposition basée sur la semaine]"
- [ ] [Offres 🔥 non encore traitées]

🟠 SHOULD (pipeline)
- [ ] [Relance secondaire]
- [ ] [Action BG prioritaire depuis hal backlog]

🟡 COULD
- [ ] [Si capacité disponible]

Contraintes calendrier semaine prochaine :
- [Événement impactant + jour + impact sur blocs job search]
```

Terminer par :

> "Voilà le bilan. Pour clôturer le sprint dans hal (marquer les tâches terminées + sauvegarder le bilan), réponds **'clôture'** ou **'ferme le sprint'**. Le sprint-planner prend le relais pour construire le planning détaillé."

---

## ÉTAPE 5 — Clôturer le sprint (validation explicite requise)

**UNIQUEMENT après validation explicite** ("clôture", "ferme le sprint", "ok pour clôturer", "valide").
**Ne jamais exécuter automatiquement, même en mode schedule.**

### 5a. Marquer les tâches terminées

Pour chaque tâche déjà `done` dans hal — aucune action. Pour les tâches que Renaud confirme comme terminées :

```
mcp__hal-mcp__update_task_status(workspace_slug="blue-green", task_id=..., status="done")
mcp__hal-mcp__update_task_status(workspace_slug="renaud", task_id=..., status="done")
```

### 5b. Sauvegarder le bilan dans hal

```
mcp__hal-mcp__save_document(
  workspace_slug="renaud",
  slug="sprint-review-[sprint_number_rn]",
  domain="jobsearch",
  kind="sprint_review",
  title="Sprint Review [N] — Semaine du [date_lundi]",
  content_md="[bilan résumé : score sprint, métriques jobsearch, shortlist, décisions prises]"
)
```

Confirmer :

```
✅ Sprint [N] clôturé.
- Blue Green [sprint_name_bg] : [X] tâches marquées done
- Renaud [sprint_name_rn] : [X] tâches marquées done
- Bilan sauvegardé : hal/renaud/sprint-review-[N]

Bonne semaine. Le sprint-planner prend le relais.
```
