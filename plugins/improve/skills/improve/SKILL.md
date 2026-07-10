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
allowed-tools: "AskUserQuestion ToolSearch mcp__github__issue_write"
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
3. Création de l'issue via `mcp__github__issue_write`
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
plugin et le repo via ce tableau (verbatim — ne pas inventer d'entrées).

> **Tableau généré** — ne pas éditer à la main. Régénéré par
> `scripts/generate_improve_map.py` (CI le vérifie contre toute dérive).

<!-- improve-map:start -->

| Skill            | Plugin    | Repo                  |
|------------------|-----------|-----------------------|
| mail-triage      | briefing  | renaud-marketplace    |
| morning-briefing | briefing  | renaud-marketplace    |
| sprint-planner   | briefing  | renaud-marketplace    |
| sprint-review    | briefing  | renaud-marketplace    |
| improve          | improve   | renaud-marketplace    |
| cover-letter     | jobsearch | renaud-marketplace    |
| cv-generator     | jobsearch | renaud-marketplace    |
| interview-prep   | jobsearch | renaud-marketplace    |
| jobsearch-vault  | jobsearch | renaud-marketplace    |
| log-application  | jobsearch | renaud-marketplace    |
| log-cr           | jobsearch | renaud-marketplace    |
| myspy            | myspy     | renaud-marketplace    |
| crm              | hal       | bluegreen-marketplace |
| edifice          | hal       | bluegreen-marketplace |
| linkedin         | hal       | bluegreen-marketplace |
| pm               | hal       | bluegreen-marketplace |

<!-- improve-map:end -->

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

## Step 3 — Create the GitHub issue via MCP

Use `mcp__github__issue_write` — outil GitHub MCP natif Cowork.
Ne jamais utiliser `Bash` / `gh` — `gh` n'est pas installé dans le workspace Cowork.

Si le tool est listé comme différé dans ton contexte, charge son schéma d'abord :
`ToolSearch { query: "select:mcp__github__issue_write" }`

### Appel `mcp__github__issue_write`

Paramètres :
- `method`: `"create"`
- `owner`: `"BluegReeno"`
- `repo`: `<REPO>` (renaud-marketplace ou bluegreen-marketplace)
- `title`: `"fix(skill:<skill-name>): <comportement attendu en <8 mots>"`
- `labels`: `["ai-improvable"]` — seul label garanti existant dans les deux repos
- `body`: voir template ci-dessous

Template du body (remplacer tous les `<placeholders>`) :

```
## Skill concerné
- Plugin : `<plugin>` (<repo>)
- Fichier : `plugins/<plugin>/skills/<skill>/SKILL.md`
- Skill : `<skill-name>`
- Priorité : <high|medium|low>

## Comportement observé
<verbatim depuis la phrase de Renaud — ce qui s'est passé>

## Comportement attendu
<verbatim depuis la phrase de Renaud — ce qui aurait dû se passer>

## Suggestion de fix
<inféré depuis le delta observé/attendu — 1-2 lignes, à valider par Archon>

## Pour fixer (Archon)
```bash
archon workflow run skill-improve "#<ISSUE_NUMBER>"
```
> Lancer depuis le répertoire local de `<repo>`

- [ ] Lire `plugins/<plugin>/skills/<skill>/SKILL.md`
- [ ] Identifier la section à modifier
- [ ] Corriger selon le comportement attendu
- [ ] Bumper la version dans les 2 champs (plugin.json / marketplace.json plugins[].version)
- [ ] Ajouter l'entrée `## <plugin> <version>` dans CHANGELOG.md
- [ ] `bash scripts/check_version_sync.sh` passe (exit 0)
- [ ] Ouvrir une PR avec `closes #<ISSUE_NUMBER>`
```

**Récupérer l'URL et le numéro** depuis la réponse du tool :
- `html_url` ou `url` → URL complète de l'issue
- `number` → numéro de l'issue

## Step 4 — One-line confirmation

Affiche exactement (avec les valeurs réelles de `<N>`, `<REPO>`, `<URL>`) :

```
✅ Issue #<N> créée dans <REPO> — <URL>
Pour fixer : archon workflow run skill-improve "#<N>" (depuis <REPO>)
```

Rien d'autre — pas de récap, pas de "voilà ce que j'ai fait". L'objectif
≤30 s impose une sortie minimale.

## IMPORTANT — disponibilité des outils dans Cowork

- `mcp__github__issue_write` — **EXISTE dans Cowork**. Méthode principale pour créer des issues.
- `gh` (GitHub CLI) — **N'EST PAS disponible** dans le workspace Cowork. Ne jamais utiliser `Bash` pour des opérations GitHub.
- `mcp__session_info__read_transcript` — N'existe pas dans Cowork.

Toutes les opérations GitHub passent par `mcp__github__issue_write`. Pas d'exception.

## NOT in scope (ne pas faire)

- Ne PAS modifier le code du skill concerné — c'est le rôle d'Archon
  (workflow `skill-improve`).
- Ne PAS bumper la version du skill concerné — c'est aussi le rôle d'Archon.
- Ne PAS auto-déclencher `archon workflow run` — la confirmation Step 4
  affiche la commande, Renaud la lance manuellement (depuis le repo
  concerné) quand il veut.
- Ne PAS poser plus de 2 questions par défaut (Question 3 sur le skill
  seulement en dernier recours, voir Step 2).
