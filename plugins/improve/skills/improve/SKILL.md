---
name: improve
description: >
  Capture une observation sur n'importe quel skill et la transforme en GitHub
  Issue (label `ai-improvable`) en ≤30 secondes, prête pour Archon. Accepte
  `/improve <skill-name>` (skill connu directement) ou `/improve` seul (pose
  la question). Auto-détecte le repo cible depuis le nom du skill — jamais
  besoin de le préciser. Une seule question : le delta observé/attendu. Use
  when Renaud says `/improve`, `/improve <skill-name>`, "améliore ce skill",
  "problème avec le skill X", "ce skill ne fait pas Y", "ajoute ça au skill",
  or spots a bug in any skill (morning-briefing, cv-generator, sprint-planner,
  hal, edifice, blue-green-proposal-generator, etc.) during a Cowork session.
version: 0.1.1
allowed-tools: "AskUserQuestion Bash"
---

# Improve — Skill Instructions

## What this skill does

Capture, en ≤30 secondes, une observation de Renaud sur le comportement d'un
skill (n'importe lequel des skills installés via la marketplace), puis la
transformer en une GitHub Issue propre — bien labellée, avec un body
structuré pour qu'Archon puisse la traiter de manière autonome. Le skill ne
modifie aucun code : il ne fait que créer le ticket.

Le flux est :

1. Deux questions à Renaud via `AskUserQuestion`
2. Inférence automatique du contexte (skill → plugin → repo + priorité)
3. Création de l'issue via `gh issue create`
4. Confirmation sur une ligne avec l'URL et la commande Archon pour fixer

## Step 1 — Identifier le skill + le delta

### Détection du skill (depuis les arguments)

Inspecte d'abord `$ARGUMENTS` (ce que Renaud a tapé après `/improve`) :

- **`/improve morning-briefing`** → skill = `morning-briefing`, passe
  directement à la question delta.
- **`/improve`** (sans args) → pose UNE question via `AskUserQuestion` :
  - `question`: "Quel skill améliorer ?"
  - `header`: "Skill"
  - `options`: liste des skills connus (morning-briefing, sprint-planner,
    sprint-review, cv-generator, cover-letter, log-application,
    interview-prep, jobsearch-vault, improve, hal, edifice,
    blue-green-proposal-generator, document-generator)

Ne demande **jamais** le repo — il est déduit automatiquement du skill (Step 2).

### Question delta — toujours posée

Via `AskUserQuestion` (ou en texte si non disponible) :

- `question`: "Décris le problème en une phrase (observé → attendu)"
- `header`: "Problème"
- Renaud écrit une phrase couvrant :
  - ce qui s'est passé (observed behavior)
  - ce qui aurait dû se passer (expected behavior)

**Fallback si `AskUserQuestion` indisponible** : pose les questions en texte
normal et continue avec les réponses.

## Step 2 — Infer context (no questions to Renaud)

### Skill → plugin → repo lookup

À partir de la phrase de Renaud, identifie le skill mentionné et déduis le
plugin et le repo via ce tableau (verbatim — ne pas inventer d'entrées) :

| Skill                         | Plugin   | Repo                  |
|-------------------------------|----------|-----------------------|
| morning-briefing              | briefing | renaud-marketplace    |
| sprint-planner                | briefing | renaud-marketplace    |
| sprint-review                 | briefing | renaud-marketplace    |
| cv-generator                  | jobsearch | renaud-marketplace   |
| cover-letter                  | jobsearch | renaud-marketplace   |
| log-application               | jobsearch | renaud-marketplace   |
| interview-prep                | jobsearch | renaud-marketplace   |
| jobsearch-vault               | jobsearch | renaud-marketplace   |
| improve                       | improve  | renaud-marketplace    |
| hal                           | hal      | bluegreen-marketplace |
| edifice                       | hal      | bluegreen-marketplace |
| blue-green-proposal-generator | hal      | bluegreen-marketplace |
| document-generator            | hal      | bluegreen-marketplace |

Le chemin du SKILL.md est toujours :
`plugins/<plugin>/skills/<skill>/SKILL.md`

Si tu n'arrives pas à identifier le skill depuis la phrase de Renaud, choisis
le skill le plus probable basé sur le contexte de session ; en dernier
recours, demande une 3e question (`AskUserQuestion`) avec les skills du repo
choisi en options.

### Priority inference (automatic, no question)

Déduis la priorité **sans poser de question** :

- `priority:high` — la phrase de Renaud mentionne explicitement qu'un
  livrable client, un entretien ou une candidature est bloqué·e.
- `priority:low` — cosmétique, wording, nice-to-have.
- `priority:medium` — défaut (le skill marche mais est incomplet).

## Step 3 — Create the GitHub issue via Bash

Une seule passe `Bash` :

1. Pré-créer les labels dynamiques (idempotent — le `|| true` couvre le cas
  "label déjà existant"). `ai-improvable` existe déjà dans
  `renaud-marketplace`, mais on protège pareil pour
  `bluegreen-marketplace` :

   ```bash
   REPO="<repo>"            # renaud-marketplace ou bluegreen-marketplace
   SKILL_NAME="<skill>"     # ex: morning-briefing
   PRIORITY="<level>"       # high | medium | low

   gh label create "ai-improvable"           --color "5319e7" --repo "BluegReeno/${REPO}" 2>/dev/null || true
   gh label create "skill:${SKILL_NAME}"     --color "0075ca" --repo "BluegReeno/${REPO}" 2>/dev/null || true
   gh label create "priority:${PRIORITY}"    --color "e4e669" --repo "BluegReeno/${REPO}" 2>/dev/null || true
   ```

2. Créer l'issue. Le titre doit être court (`<8 mots` après le préfixe),
  factuel, en français ou anglais selon la langue de Renaud :

   ```bash
   ISSUE_URL=$(gh issue create \
     --repo "BluegReeno/${REPO}" \
     --title "fix(skill:${SKILL_NAME}): <comportement attendu en <8 mots>" \
     --label "ai-improvable" \
     --label "skill:${SKILL_NAME}" \
     --label "priority:${PRIORITY}" \
     --body "$(cat <<EOF
   ## Skill concerné
   - Plugin : \`<plugin>\` (<repo>)
   - Fichier : \`plugins/<plugin>/skills/<skill>/SKILL.md\`

   ## Comportement observé
   <verbatim depuis la phrase de Renaud — ce qui s'est passé>

   ## Comportement attendu
   <verbatim depuis la phrase de Renaud — ce qui aurait dû se passer>

   ## Suggestion de fix
   <inféré depuis le delta observé/attendu — 1-2 lignes, à valider par Archon>

   ## Pour fixer (Archon)
   \`\`\`bash
   archon workflow run skill-improve "#<ISSUE_NUMBER>"
   \`\`\`
   > Lancer depuis le répertoire local de \`<repo>\`

   - [ ] Lire \`plugins/<plugin>/skills/<skill>/SKILL.md\`
   - [ ] Identifier la section à modifier
   - [ ] Corriger selon le comportement attendu
   - [ ] Bumper la version dans les 3 endroits (plugin.json / SKILL.md frontmatter / marketplace.json)
   - [ ] Ouvrir une PR avec \`closes #<ISSUE_NUMBER>\`
   EOF
   )") || { echo "❌ gh issue create failed — check: gh auth status && echo \$REPO"; exit 1; }

   ISSUE_NUMBER=$(echo "$ISSUE_URL" | grep -oE '[0-9]+$')
   ```

**Gotchas Bash** :
- Les labels passés à `--label` doivent exister AVANT le `gh issue create`
  (sinon `could not add label: ... not found` — d'où l'étape de pré-création).
- Pas d'espace après la virgule si tu passes plusieurs labels dans un seul
  `--label "a,b"` ; ici on utilise plusieurs flags `--label` séparés (plus
  sûr).
- Le HEREDOC utilise `EOF` non-quoté pour que les variables shell hors
  HEREDOC (`${SKILL_NAME}`, `${REPO}`, `${PRIORITY}`) s'expandent. À
  l'intérieur du HEREDOC, les `<placeholders>` sont remplacés textuellement
  par le modèle — pas par le shell. Les backticks dans le body sont échappés
  (`\``).

## Step 4 — One-line confirmation

Imprime exactement (en utilisant les variables capturées `$ISSUE_NUMBER`, `$REPO`, `$ISSUE_URL`) :

```
✅ Issue #${ISSUE_NUMBER} créée dans ${REPO} — ${ISSUE_URL}
Pour fixer : archon workflow run skill-improve "#${ISSUE_NUMBER}" (depuis renaud-marketplace)
```

Rien d'autre — pas de récap, pas de "voilà ce que j'ai fait". L'objectif
≤30 s impose une sortie minimale.

## IMPORTANT — tools that do NOT exist (never use them)

- `mcp__github__issue_write` — N'EXISTE PAS dans Cowork.
- `mcp__session_info__read_transcript` — N'EXISTE PAS dans Cowork.

Toutes les opérations GitHub passent par `gh` via `Bash`. Pas d'exception.

## NOT in scope (ne pas faire)

- Ne PAS modifier le code du skill concerné — c'est le rôle d'Archon
  (workflow `skill-improve`).
- Ne PAS bumper la version du skill concerné — c'est aussi le rôle d'Archon.
- Ne PAS auto-déclencher `archon workflow run` — la confirmation Step 4
  affiche la commande, Renaud la lance manuellement (depuis le repo
  concerné) quand il veut.
- Ne PAS poser plus de 2 questions par défaut (Question 3 sur le skill
  seulement en dernier recours, voir Step 2).
