---
name: bg-improve
description: >
  Capture un problème ou une suggestion d'amélioration sur un skill Blue Green et
  crée une GitHub Issue dans BluegReeno/bluegreen-marketplace avec le label
  ai-improvable. Utiliser quand tu dis "/bg-improve", "améliore ce skill",
  "problème avec le skill BG", "ce skill ne fait pas X", "ajoute ça au skill",
  ou que tu repères un bug dans un skill Blue Green (hal, edifice, proposal,
  document) pendant une session Cowork.
version: 0.1.0
allowed-tools: "mcp__github__issue_write mcp__session_info__read_transcript AskUserQuestion"
---

# bg-improve — Skill Instructions

## Objectif

Bloc ① Capture de la boucle d'amélioration automatisée des skills Blue Green.
En moins de 30 secondes, transformer l'observation de Renaud en une GitHub Issue
bien structurée dans `bluegreen-marketplace` que Claude Code pourra traiter la nuit.

```
① Capture (ce skill, ≤30s) → ② Fix (Claude Code, nuit) → ③ Review (morning briefing) → ④ Deploy (auto)
```

## Skills couverts (bluegreen-marketplace)

| Skill | Plugin | Chemin SKILL.md |
|---|---|---|
| `hal` | `hal` | `plugins/hal/skills/hal/SKILL.md` |
| `edifice` | `hal` | `plugins/hal/skills/edifice/SKILL.md` |
| `blue-green-proposal-generator` | `hal` | `plugins/hal/skills/blue-green-proposal-generator/SKILL.md` |
| `document-generator` | `hal` | `plugins/hal/skills/document-generator/SKILL.md` |

## Step 1 — 2 questions rapides

Poser ces deux questions via `AskUserQuestion` :

1. **Quel skill BG est concerné ?** (hal, edifice, blue-green-proposal-generator, document-generator)
2. **Comportement observé vs comportement attendu ?** (une phrase chacun)

Si le skill est identifiable depuis le contexte de la session (Renaud vient de l'utiliser),
pré-remplir avec le skill probable et demander confirmation plutôt qu'une question ouverte.

## Step 2 — Capture automatique du contexte

Sans demander à Renaud :

- **Timestamp ISO** : heure Paris au moment de l'invocation
- **Plugin présumé** : inférer depuis le skill name (hal/edifice/proposal/document → `hal`)
- **Chemin SKILL.md présumé** : voir table ci-dessus
- **Extrait transcript** : appeler `mcp__session_info__read_transcript` — extraire les 10
  derniers échanges pertinents autour du problème (max 500 tokens). Si non disponible,
  laisser `<transcript non disponible>`.
- **Priorité** :
  - `priority:high` — skill bloquant un livrable client ou une propale urgente
  - `priority:medium` — skill fonctionnel mais incomplet (cas par défaut)
  - `priority:low` — amélioration cosmétique ou nice-to-have

## Step 3 — Création de l'issue GitHub

Appeler `mcp__github__issue_write` avec :

```
method: create
owner: BluegReeno
repo: bluegreen-marketplace
title: fix(skill:<skill-name>): <comportement attendu résumé en <8 mots>
labels: ["ai-improvable", "skill:<skill-name>", "priority:<level>"]
body: <template ci-dessous>
```

### Template body

```markdown
## Skill concerné
- Plugin : `<plugin-name>` (bluegreen-marketplace)
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
- [ ] Lire `plugins/<plugin-name>/skills/<skill-name>/SKILL.md` dans bluegreen-marketplace
- [ ] Identifier la section à modifier (description, flow, tools, template, triggers...)
- [ ] Corriger selon le comportement attendu décrit ci-dessus
- [ ] Vérifier que le skill se déclenche correctement sur les triggers listés
- [ ] Ouvrir une PR avec `closes #<issue-number>` vers `main`
```

## Step 4 — Confirmation

Afficher une ligne de confirmation :

```
✅ Issue #<n> créée dans bluegreen-marketplace — labels : ai-improvable, skill:<name>, priority:<level>
🔗 <url de l'issue>
```

## Règles

- **≤30 secondes** de bout en bout. Pas de prose superflue.
- **Ne jamais modifier le skill soi-même** — créer l'issue pour Claude Code, pas de fix immédiat.
- Si `skill:<skill-name>` n'existe pas comme label, l'inclure quand même —
  `mcp__github__issue_write` le créera à la volée.
- Les issues créées ici sont consommées par le pipeline Archon `improve-skill.yaml`
  (bloc ② — hors scope de ce skill).
