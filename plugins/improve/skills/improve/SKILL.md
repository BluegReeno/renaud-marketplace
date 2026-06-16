---
name: improve
description: >
  Capture une observation sur n'importe quel skill et la transformer en GitHub
  Issue (label `ai-improvable`) en ≤30 secondes, prête pour Archon. Pose 2
  questions (repo concerné + une phrase décrivant le problème), infère le
  contexte (skill → plugin → repo, priorité), pré-crée les labels manquants,
  puis appelle `gh issue create`. Use when Renaud says `/improve`, "améliore
  ce skill", "problème avec le skill X", "ce skill ne fait pas Y", "ajoute ça
  au skill", or spots a bug in any skill (morning-briefing, cv-generator,
  sprint-planner, hal, edifice, blue-green-proposal-generator, etc.) during a
  Cowork session.
version: 0.1.0
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

## Step 1 — Two questions via AskUserQuestion

Pose les deux questions en un seul appel `AskUserQuestion` (un seul
formulaire pour Renaud).

**Question 1 — Repo concerné**
- `question`: "Quel repo est concerné ?"
- `header`: "Repo"
- `options`:
  - `{label: "renaud-marketplace", description: "Skills perso (briefing, jobsearch, improve)"}`
  - `{label: "bluegreen-marketplace", description: "Skills BG (hal, edifice, proposals, document-generator)"}`
- Si tu peux pré-déduire le repo du contexte de la session (Renaud venait
  juste d'utiliser un skill spécifique), mentionne-le dans le label de la
  question — mais laisse les options ouvertes.

**Question 2 — Description du problème**
- `question`: "Décris le problème en une phrase (observé → attendu)"
- `header`: "Problème"
- Pas d'options (free text) — Renaud écrit une phrase qui couvre :
  - ce qui s'est passé (observed behavior)
  - ce qui aurait dû se passer (expected behavior)

**Fallback si `AskUserQuestion` indisponible** (subagent, environnement non
Cowork) : pose les deux questions en texte normal et continue avec les
réponses.

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

Si le repo déduit ne correspond pas à la réponse de Renaud à la Question 1,
fais confiance à la réponse de Renaud (il sait mieux que toi).

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
   gh issue create \
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

   ## Pour Archon
   - [ ] Lire \`plugins/<plugin>/skills/<skill>/SKILL.md\`
   - [ ] Identifier la section à modifier
   - [ ] Corriger selon le comportement attendu
   - [ ] Bumper la version dans les 3 endroits (plugin.json / SKILL.md frontmatter / marketplace.json)
   - [ ] Ouvrir une PR avec \`closes #<this-issue-number>\`
   EOF
   )"
   ```

**Gotchas Bash** :
- Les labels passés à `--label` doivent exister AVANT le `gh issue create`
  (sinon `could not add label: ... not found` — d'où l'étape de pré-création).
- Pas d'espace après la virgule si tu passes plusieurs labels dans un seul
  `--label "a,b"` ; ici on utilise plusieurs flags `--label` séparés (plus
  sûr).
- Le HEREDOC doit utiliser `EOF` non-quoté pour laisser
  `${SKILL_NAME}` etc. s'interpoler — les backticks dans le body sont
  échappés (`\``).

## Step 4 — One-line confirmation

Imprime exactement (remplace `<n>`, `<repo>`, `<url>`) :

```
✅ Issue #<n> créée dans <repo> — <url>
Pour fixer : archon workflow run skill-improve "#<n>" (depuis le repo concerné)
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
