---
name: renaud-improve
description: >
  Capture un problème ou une suggestion d'amélioration sur un skill
  renaud-marketplace et crée une GitHub Issue dans BluegReeno/renaud-marketplace
  avec le label ai-improvable. Utiliser quand tu dis "/renaud-improve",
  "améliore ce skill", "problème avec le skill X", "ce skill ne fait pas Y",
  "ajoute ça au skill", ou que tu repères un bug dans un skill renaud
  (morning-briefing, sprint-planner, log-application, cv-generator, etc.)
  pendant une session Cowork.
version: 0.1.0
allowed-tools: "mcp__github__issue_write mcp__session_info__read_transcript AskUserQuestion"
---

# renaud-improve — Skill Instructions

## Objectif

Bloc ① Capture de la boucle d'amélioration automatisée des skills perso de Renaud.
En moins de 30 secondes, transformer l'observation de Renaud en une GitHub Issue
bien structurée dans `renaud-marketplace` que Claude Code pourra traiter la nuit.

```
① Capture (ce skill, ≤30s) → ② Fix (Claude Code, nuit) → ③ Review (morning briefing) → ④ Deploy (auto)
```

## Skills couverts (renaud-marketplace)

| Skill | Plugin | Chemin SKILL.md |
|---|---|---|
| `morning-briefing` | `briefing` | `plugins/briefing/skills/morning-briefing/SKILL.md` |
| `sprint-planner` | `briefing` | `plugins/briefing/skills/sprint-planner/SKILL.md` |
| `sprint-review` | `briefing` | `plugins/briefing/skills/sprint-review/SKILL.md` |
| `log-application` | `jobsearch` | `plugins/jobsearch/skills/log-application/SKILL.md` |
| `cv-generator` | `jobsearch` | `plugins/jobsearch/skills/cv-generator/SKILL.md` |
| `cover-letter` | `jobsearch` | `plugins/jobsearch/skills/cover-letter/SKILL.md` |
| `interview-prep` | `jobsearch` | `plugins/jobsearch/skills/interview-prep/SKILL.md` |
| `jobsearch-vault` | `jobsearch` | `plugins/jobsearch/skills/jobsearch-vault/SKILL.md` |
| `bg-improve` | `workflow` | `plugins/workflow/skills/bg-improve/SKILL.md` |
| `renaud-improve` | `workflow` | `plugins/workflow/skills/renaud-improve/SKILL.md` |

## Step 1 — 2 questions rapides

Poser ces deux questions via `AskUserQuestion` :

1. **Quel skill est concerné ?** (ex: morning-briefing, cv-generator, sprint-planner…)
2. **Comportement observé vs comportement attendu ?** (une phrase chacun)

Si le skill est identifiable depuis le contexte de la session (Renaud vient de
l'utiliser), pré-remplir avec le skill probable et demander confirmation.

## Step 2 — Capture automatique du contexte

Sans demander à Renaud :

- **Timestamp ISO** : heure Paris au moment de l'invocation
- **Plugin présumé** : inférer depuis le skill name
  - `briefing` → morning-briefing, sprint-planner, sprint-review
  - `jobsearch` → log-application, cv-generator, cover-letter, interview-prep, jobsearch-vault
  - `workflow` → bg-improve, renaud-improve
- **Chemin SKILL.md présumé** : voir table ci-dessus
- **Extrait transcript** : appeler `mcp__session_info__read_transcript` — extraire les 10
  derniers échanges pertinents autour du problème (max 500 tokens). Si non disponible,
  laisser `<transcript non disponible>`.
- **Priorité** :
  - `priority:high` — skill bloquant une action jobsearch critique (entretien, candidature)
  - `priority:medium` — skill fonctionnel mais incomplet (cas par défaut)
  - `priority:low` — amélioration cosmétique ou nice-to-have

## Step 3 — Création de l'issue GitHub

Appeler `mcp__github__issue_write` avec :

```
method: create
owner: BluegReeno
repo: renaud-marketplace
title: fix(skill:<skill-name>): <comportement attendu résumé en <8 mots>
labels: ["ai-improvable", "skill:<skill-name>", "priority:<level>"]
body: <template ci-dessous>
```

### Template body

```markdown
## Skill concerné
- Plugin : `<plugin-name>` (renaud-marketplace)
- Fichier : `plugins/<plugin-name>/skills/<skill-name>/SKILL.md`
- Déclenché par : Renaud en session Cowork — <timestamp ISO>

## Comportement observé
<verbatim ce que Renaud a décrit>

## Comportement attendu
<verbatim ce que Renaud attendait>

## Contexte session
<extrait transcript — max 500 tokens, échanges autour du problème>

## Suggestion de fix
<inférer une suggestion concrète à partir du delta observé/attendu>

## Pour Claude Code
- [ ] Lire `plugins/<plugin-name>/skills/<skill-name>/SKILL.md` dans renaud-marketplace
- [ ] Identifier la section à modifier (description, flow, tools, template, triggers...)
- [ ] Corriger selon le comportement attendu décrit ci-dessus
- [ ] Vérifier que le skill se déclenche correctement sur les triggers listés
- [ ] Ouvrir une PR avec `closes #<issue-number>` vers `main`
```

## Step 4 — Confirmation

Afficher une ligne de confirmation :

```
✅ Issue #<n> créée dans renaud-marketplace — labels : ai-improvable, skill:<name>, priority:<level>
🔗 <url de l'issue>
```

## Exemple concret (cas de test de l'issue #6)

> Renaud : "améliore ce skill, le morning briefing ne lit pas mes mails non lus des 3 derniers jours"

Résultat attendu :
- **Title** : `fix(skill:morning-briefing): ajouter lecture mails non lus 3 derniers jours`
- **Labels** : `ai-improvable`, `skill:morning-briefing`, `priority:medium`
- **Body** : comportement observé = "le morning briefing ne lit pas mes mails non lus",
  comportement attendu = "lire les mails non lus des 3 derniers jours"

## Règles

- **≤30 secondes** de bout en bout. Pas de prose superflue.
- **Ne jamais modifier le skill soi-même** — créer l'issue pour Claude Code, pas de fix immédiat.
- Si `skill:<skill-name>` n'existe pas comme label, l'inclure quand même —
  `mcp__github__issue_write` le créera à la volée.
- Les issues créées ici sont consommées par le pipeline Archon `improve-skill.yaml`
  (bloc ② — hors scope de ce skill).
