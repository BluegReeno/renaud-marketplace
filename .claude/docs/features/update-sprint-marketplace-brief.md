# Brief — `update_sprint` wiring · repos `renaud-marketplace` + `bluegreen-marketplace`

**Prérequis** : `update_sprint` déployé dans hal-mcp (voir `update-sprint-hal-brief.md`).

---

## 1. `renaud-marketplace` — plugin `briefing`

### 1a. sprint-planner/SKILL.md — ajouter le tool aux allowed-tools

**Fichier** : `plugins/briefing/skills/sprint-planner/SKILL.md`

**Chercher dans le frontmatter** :

```
allowed-tools: "mcp__hal-mcp__whoami mcp__hal-mcp__list_sprints mcp__hal-mcp__list_tasks mcp__hal-mcp__create_sprint mcp__hal-mcp__create_task mcp__hal-mcp__assign_task_to_sprint mcp__hal-mcp__update_task mcp__hal-mcp__get_document mcp__claude_ai_Google_Calendar__list_events mcp__claude_ai_gmail-mcp__search_emails Skill(jobsearch-vault) Bash"
```

**Remplacer par** (ajouter `mcp__hal-mcp__update_sprint` après `create_sprint`) :

```
allowed-tools: "mcp__hal-mcp__whoami mcp__hal-mcp__list_sprints mcp__hal-mcp__list_tasks mcp__hal-mcp__create_sprint mcp__hal-mcp__update_sprint mcp__hal-mcp__create_task mcp__hal-mcp__assign_task_to_sprint mcp__hal-mcp__update_task mcp__hal-mcp__get_document mcp__claude_ai_Google_Calendar__list_events mcp__claude_ai_gmail-mcp__search_emails Skill(jobsearch-vault) Bash"
```

### 1b. sprint-planner/SKILL.md — ajouter section "Correction statut sprint" à l'ÉTAPE 6

**Insérer à la fin de l'ÉTAPE 6a** (après la phrase "Si un sprint avec le statut cible existe déjà…"),
avant la section `### 6b. Créer les sprints` :

```markdown
### 6a bis. Corriger le statut d'un sprint existant (si statut incorrect)

Si un sprint existe déjà avec le mauvais statut (ex: `status="suivant"` alors que
`SPRINT_STATUS="actuel"`), corriger via :

​```
mcp__hal-mcp__update_sprint(
  workspace_slug=<workspace>,
  sprint_id=<sprint_id_existant>,
  status=<SPRINT_STATUS>
)
​```

Ne recréer le sprint que si aucun sprint existant n'est trouvé avec le statut cible.
```

### 1c. sprint-review/SKILL.md — ajouter le tool aux allowed-tools

**Fichier** : `plugins/briefing/skills/sprint-review/SKILL.md`

**Chercher dans le frontmatter** :

```
allowed-tools:
```

Ou le bloc équivalent. Ajouter `mcp__hal-mcp__update_sprint` à la liste existante.

Si la skill utilise une liste multi-ligne :

```yaml
allowed-tools:
  - mcp__hal-mcp__whoami
  - mcp__hal-mcp__list_sprints
  - mcp__hal-mcp__list_tasks
  - mcp__hal-mcp__update_sprint      ← ajouter ici
  - mcp__hal-mcp__update_task_status
  - mcp__hal-mcp__save_document
  - mcp__claude_ai_Google_Calendar__list_events
  - mcp__claude_ai_gmail-mcp__search_emails
  - Skill(jobsearch-vault)
  - Bash
```

### 1d. Bump versions

Après ces modifications : bump `briefing` de `0.4.2` → `0.4.3` dans les 4 fichiers en sync :
- `.claude-plugin/marketplace.json` (top-level `version` + plugin entry `briefing.version`)
- `plugins/briefing/.claude-plugin/plugin.json`
- `plugins/briefing/skills/sprint-planner/SKILL.md` frontmatter
- `plugins/briefing/skills/sprint-review/SKILL.md` frontmatter
- `plugins/briefing/skills/morning-briefing/SKILL.md` frontmatter

---

## 2. `bluegreen-marketplace` — plugin `hal`

### 2a. hal skill — ajouter update_sprint aux allowed-tools

**Fichier** : `bluegreen-marketplace/plugins/hal/skills/hal/SKILL.md`  
(adapter le chemin exact selon la structure du repo)

Ajouter `mcp__hal-mcp__update_sprint` à la liste `allowed-tools` du frontmatter.

### 2b. Bump version

Bump `hal` plugin → PATCH dans les 3 fichiers en sync de `bluegreen-marketplace`.

---

## Ordre d'exécution recommandé

1. Appliquer le brief `hal` en premier (migration + deploy Edge Function)
2. Vérifier le tool disponible : `mcp__hal-mcp__whoami` puis tester `update_sprint` manuellement
3. Appliquer les modifications `renaud-marketplace` + bump 0.4.3
4. Appliquer les modifications `bluegreen-marketplace`
5. Commit + push les deux repos marketplace
