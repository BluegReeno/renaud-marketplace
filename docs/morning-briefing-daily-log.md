# Brief — morning-briefing v0.5.0 : daily log dans HAL

> **Repo** : `renaud-marketplace`
> **Skill** : `plugins/briefing/skills/morning-briefing/SKILL.md`
> **Scope** : étendre le morning-briefing pour écrire un daily log par workspace dans HAL (`domain="memory"`, `kind="daily-log"`). La partie lecture en début de session et l'écriture structurée en fin de skill.
> **Dépend de** : migration hal `20260629000000_memory_domain_allowed_tags` appliquée en prod (domain `memory` disponible dans `allowed_tags` des workspaces `blue-green` et `renaud`).
> **Deferred** : handoffs, decisions, session-briefs — backlog. Ce brief couvre daily-log uniquement.
> **Pipeline** : `archon-idea-to-pr`

---

## Context

Le morning-briefing (v0.4.3) est read-only : il lit les tâches hal, le vault jobsearch Obsidian et les 3 Google Calendars. Le daily log est écrit manuellement en fin de session dans `SynologyDrive-MyAssistant/memory/YYYY-MM-DD.md` — inaccessible depuis Claude mobile (OpenClaw, Claude.ai iOS/Android) ou n8n.

Avec la migration hal `memory` domain, `save_document` / `get_document` permettent maintenant de stocker un daily log par workspace dans Supabase, accessible de tout client MCP authentifié.

Le pattern retenu (inspiré de ClawMem) : **un daily log par workspace par jour**, écrit par le morning-briefing à la génération, mis à jour manuellement tout au long de la journée depuis n'importe quel client.

## Ce que ce brief livre

1. **Step 0 étendu** : avant de générer le brief, lire le daily log de la veille pour chaque workspace (contexte cross-session).
2. **Step 4 nouveau** : après le rendu du brief, écrire un daily log structuré dans HAL pour chaque workspace concerné (`blue-green` et `renaud`).
3. **Contrainte READ-ONLY levée** : le skill écrit maintenant deux documents en fin d'exécution. C'est la seule mutation autorisée — aucune autre écriture hal/calendar.
4. **`allowed-tools` mis à jour** : ajout de `mcp__hal-mcp__get_document` et `mcp__hal-mcp__save_document`.

## Convention daily log

| Champ | Valeur |
|---|---|
| `domain` | `memory` |
| `kind` | `daily-log` |
| `slug` | `daily-log-YYYY-MM-DD` (ex. `daily-log-2026-06-25`) |
| `title` | `Daily log — <workspace-slug> — <date en français>` |
| `workspace_slug` | le workspace concerné (`blue-green` ou `renaud`) |
| `content_md` | markdown généré par le skill (voir structure ci-dessous) |

La clé d'upsert `(workspace_slug, slug)` garantit **un log par workspace par jour**. Pas de collision entre workspaces : le log `blue-green` et le log `renaud` ont le même slug mais des `workspace_slug` différents → deux lignes distinctes en DB.

## Structure du daily log

### Log `blue-green`

```markdown
# Daily log — blue-green — <jour, date en français>

## Sprint en cours [business]
- [ ] <titre tâche> · priorité: <priority|none>
...
(ou "(aucune tâche en cours)" si sprint vide)

## Agenda du jour [pro]
HH:MM — <événement> [pro]
...
(ou "(aucun événement pro aujourd'hui)")

## Notes
(vide — à compléter en cours de journée)
```

### Log `renaud`

```markdown
# Daily log — renaud — <jour, date en français>

## Sprint en cours [perso]

### 🎯 jobsearch
- [ ] <titre tâche>
...

### 🏡 rosaslaborbe / 🧍 personal / 💶 finance / …
- [ ] <titre tâche>
...
(groupes vides omis)

## Agenda du jour [perso + famille]
HH:MM — <événement> [perso|famille]
...
(ou "(aucun événement perso/famille aujourd'hui)")

## Notes
(vide — à compléter en cours de journée)
```

## Non-goals

- Pas de nouveau skill `update-daily-log` — la mise à jour se fait via `save_document` directement depuis n'importe quel client (read-modify-write manuel).
- Pas de daily log pour `ic-ingenieurs-conseils` — Renaud n'est pas encore membre de ce workspace. Si ça arrive, le skill lit les workspaces retournés par `whoami` et scale automatiquement.
- Pas de daily log pour les workspaces autres que ceux retournés par `whoami` — ne pas hardcoder `blue-green`/`renaud`.
- Pas de log SI `hal:DOWN` — si hal est inaccessible en Step 0, on skip Step 0 et Step 4 sans erreur (le brief reste utile).
- Pas de migration des anciens logs markdown vers HAL.
- Pas de changement au skill `bluegreen-marketplace/plugins/hal` — aucun impact.

---

## CONTEXT REFERENCES

### Fichiers à lire avant d'implémenter

- `plugins/briefing/skills/morning-briefing/SKILL.md` (version actuelle v0.4.3) — structure complète du skill, contraintes load-bearing, template de rendu
- `docs/loop-3-morning-briefing.md` — brief original du skill, contexte des décisions architecturales

### Fichier à modifier

- `plugins/briefing/skills/morning-briefing/SKILL.md` — le seul fichier à changer

---

## Implementation Tasks

### Task 1 — Mettre à jour `SKILL.md` du morning-briefing (v0.4.3 → v0.5.0)

**Fichier** : `plugins/briefing/skills/morning-briefing/SKILL.md`

#### 1a — Frontmatter : version + allowed-tools

```yaml
version: 0.5.0
allowed-tools: "mcp__hal-mcp__whoami mcp__hal-mcp__list_sprints mcp__hal-mcp__list_tasks mcp__hal-mcp__get_document mcp__hal-mcp__save_document mcp__claude_ai_Google_Calendar__list_calendars mcp__claude_ai_Google_Calendar__list_events Skill(jobsearch-vault)"
```

#### 1b — Ajouter Step 0.5 — Lecture des daily logs de la veille

Insérer entre Step 0 (pre-flight) et Step 1 (pull data) :

```
## Step 0.5 — Lecture du daily log de la veille (contexte cross-session)

Si `hal:UP` (probe Step 0 passé) : pour chaque workspace retourné par `whoami`, appeler :
  get_document(workspace_slug=<slug>, slug="daily-log-<hier>")

Si le document existe, extraire la section "Notes" et l'injecter comme contexte silencieux
(ne pas l'afficher dans le brief rendu — c'est un contexte interne pour l'agent).
Si le document n'existe pas (404 ou entrée absente), ignorer silencieusement — ce n'est pas une erreur.
Si hal est DOWN, skiper entièrement ce step.
```

#### 1c — Ajouter Step 4 — Écriture des daily logs dans HAL

Ajouter après Step 3 (Render the brief) :

```
## Step 4 — Écrire les daily logs dans HAL

Si `hal:UP` : pour chaque workspace retourné par `whoami`, appeler `save_document` avec :
- workspace_slug : le slug du workspace
- slug : "daily-log-<YYYY-MM-DD>" (date du jour)
- domain : "memory"
- kind : "daily-log"
- title : "Daily log — <workspace-slug> — <date en français>"
- content_md : le contenu structuré correspondant au workspace (voir structure ci-dessous)

Ce sont les SEULS appels write autorisés dans ce skill. Aucune autre mutation.

Si `save_document` échoue pour un workspace, afficher une ligne d'erreur dans le brief :
  ⚠️ Daily log <workspace-slug> — écriture échouée : <reason>

Si hal est DOWN (Step 0 échoué), skiper Step 4 entièrement sans erreur.
```

#### 1d — Mettre à jour la contrainte READ-ONLY dans Step 4 (ancien) → Step 5

Renommer l'actuel "Step 4 — Constraints" en "Step 5 — Constraints" et modifier :

```
- **Deux writes autorisés, pas plus.** `save_document` pour le daily log `blue-green` et
  `save_document` pour le daily log `renaud` (ou autant de workspaces que `whoami` retourne).
  C'est la seule exception au principe read-only. Aucun autre `create_*`, `update_*`, ou
  `delete_*` hal/calendar/vault.
- **Jamais d'écriture si hal:DOWN.** Step 4 est conditionnel à `hal:UP`.
```

**Commit** : `feat(briefing): daily log write to HAL — v0.5.0`

---

## Testing

### Smoke test

1. Lancer le skill morning-briefing après deploy.
2. Vérifier que le brief s'affiche normalement (régression AC1-3 du brief original).
3. Depuis Supabase dashboard ou via MCP : `get_document(workspace_slug="blue-green", slug="daily-log-<aujourd'hui>")` → document présent avec `domain="memory"`, `kind="daily-log"`, contenu structuré.
4. Idem pour `workspace_slug="renaud"`.
5. Depuis Claude mobile (OpenClaw ou claude.ai) : appeler `get_document` sur les deux slugs → lecture confirme l'accessibilité cross-client.

### Regression guard

- Les AC1-3 originaux du brief loop-3 restent satisfaits : brief complet, tâches perso/business labellisées, sources DOWN signalées.
- Si hal est DOWN lors du smoke test : le brief s'affiche quand même (Step 4 skippé), et la source-status footer indique `hal-mcp: ⚠️ DOWN`.

---

## Acceptance Criteria

- [ ] `version: 0.5.0` dans le frontmatter SKILL.md
- [ ] `mcp__hal-mcp__get_document` et `mcp__hal-mcp__save_document` dans `allowed-tools`
- [ ] Après exécution du skill : `get_document(workspace_slug="blue-green", slug="daily-log-<aujourd'hui>")` retourne un doc `domain="memory"`, `kind="daily-log"` avec les tâches BG du sprint
- [ ] Idem pour `workspace_slug="renaud"` avec tâches groupées par tag
- [ ] Si hal:DOWN → brief rendu normalement, Step 4 skippé, aucune erreur non-gérée
- [ ] Lecture du daily log accessible depuis un client mobile (test manuel)

---

## Rollback

`git revert <sha>` — la modification est limitée à un seul fichier SKILL.md. Les daily logs déjà écrits dans Supabase restent en DB mais ne sont plus mis à jour par le skill. Aucun impact sur les autres skills.
