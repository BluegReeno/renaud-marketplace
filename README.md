# renaud-marketplace

Public Claude Code skill marketplace for Renaud Laborbe — CV generation, Gmail MCP, job-search vault I/O, and daily briefing tools.

---

## ⚠️ Versioning — règle critique Cowork

**Cowork détecte les mises à jour exclusivement par numéro de version.**
Sans bump de version, les utilisateurs installés ne reçoivent jamais le fix.

### Les 3 champs à garder en sync (par plugin)

Pour **chaque plugin**, ces 3 champs doivent être identiques :

| Fichier | Champ | Exemple (`briefing`) |
|---------|-------|----------------------|
| `.claude-plugin/marketplace.json` | `plugins[].version` (entrée du plugin) | `"0.1.0"` |
| `plugins/<plugin>/.claude-plugin/plugin.json` | `version` | `"0.1.0"` |
| `plugins/<plugin>/skills/<skill>/SKILL.md` | `version:` frontmatter | `0.1.0` |

Si un seul dérive → Cowork ne détecte plus les mises à jour ou refuse l'installation.

### Top-level `marketplace.json` `version` — marqueur "what's new"

Le `version` **top-level** de `.claude-plugin/marketplace.json` suit le plugin **le plus récemment publié** dans le repo. Ce n'est pas un champ synchronisé repo-wide : il sert de marqueur "what's new" pour signaler au marketplace qu'il y a eu une release.

Conséquence attendue : quand on publie un nouveau plugin avec une version plus basse (ex. `briefing 0.1.0` après `jobsearch 0.2.0`), le top-level redescend à `0.1.0`. Ce n'est pas une drift à corriger.

### Quand bumper

| Type de changement | Bump |
|-------------------|------|
| Fix bug script, template, data | PATCH `0.x.Y+1` |
| Nouveau comportement, nouvel outil, nouveau skill | MINOR `0.X+1.0` |
| Refonte majeure | MAJOR `X+1.0.0` |

Le serveur MCP (`.mcp.json` → `version`) suit sa propre version indépendante.
Il NE force PAS un bump du plugin — sauf si l'interface MCP change.

### Checklist avant chaque commit

```
□ Ai-je modifié scripts/, templates/, data/, ou SKILL.md d'un plugin ?
  → Oui : bump PATCH dans les 3 champs du plugin concerné
□ Ai-je ajouté un outil ou changé le comportement visible ?
  → Oui : bump MINOR dans les 3 champs du plugin concerné
□ Les 3 versions du plugin sont-elles identiques ?
  → grep -E '"version"' .claude-plugin/marketplace.json plugins/<plugin>/.claude-plugin/plugin.json
  → grep "^version:" plugins/<plugin>/skills/*/SKILL.md
□ Si c'est une release : ai-je aussi mis à jour le `version` top-level de marketplace.json
  pour refléter le plugin qu'on vient de publier ?
```

---

## Structure du dépôt

```
renaud-marketplace/
├── .claude-plugin/
│   └── marketplace.json          ← point d'entrée Cowork (top-level version = plugin le plus récemment publié)
├── plugins/
│   ├── jobsearch/                ← plugin umbrella job search
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json       ← (VERSION ICI)
│   │   ├── .mcp.json             ← déclaration serveur MCP (url + version MCP)
│   │   ├── skills/
│   │   │   ├── cv-generator/SKILL.md       ← (VERSION ICI dans le frontmatter)
│   │   │   ├── log-application/SKILL.md    ← (VERSION ICI dans le frontmatter)
│   │   │   ├── interview-prep/SKILL.md     ← (VERSION ICI dans le frontmatter)
│   │   │   └── jobsearch-vault/SKILL.md    ← filesystem-only vault I/O (lib partagée)
│   │   ├── commands/             ← slash commands (/log-application, /interview-prep)
│   │   │   ├── log-application.md
│   │   │   └── interview-prep.md
│   │   ├── profiles/             ← p1–p5 narrative files (lus par cv-generator + interview-prep)
│   │   ├── scripts/              ← Python — generate_cv.py, batch_validate.py
│   │   ├── data/                 ← cv-master.json
│   │   ├── templates/            ← cv_template.html
│   │   └── CHANGELOG.md
│   └── briefing/                 ← plugin briefing quotidien (read-only)
│       ├── .claude-plugin/
│       │   └── plugin.json       ← (VERSION ICI)
│       ├── .mcp.json             ← hal-mcp dédupliqué avec bluegreen-marketplace/plugins/hal
│       ├── skills/
│       │   └── morning-briefing/
│       │       └── SKILL.md      ← (VERSION ICI dans le frontmatter)
│       ├── commands/
│       │   └── briefing.md       ← slash command de déclenchement
│       └── CHANGELOG.md
├── servers/
│   └── gmail-mcp/               ← Supabase Edge Function (Deno/TypeScript)
│       ├── scripts/setup_secrets.sh
│       └── supabase/
│           ├── config.toml
│           └── functions/gmail-mcp/
│               ├── deno.json
│               └── index.ts     ← McpServer version ici (indépendant du plugin)
└── docs/
    ├── skill-marketplace-guide.md
    └── mcp-server-supabase-edge.md
```

### Anatomie d'un plugin

```
plugins/<plugin>/
├── .claude-plugin/plugin.json   ← name + version (= entrée plugins[] de marketplace.json)
├── .mcp.json                    ← { "mcpServers": { "<name>": { "type":"http", "url":"...", "version":"..." } } }
├── skills/<skill>/SKILL.md      ← frontmatter: name, version, description
└── scripts/                     ← invoqués par SKILL.md via uv run --with
```

### .mcp.json — format exact

```json
{
  "mcpServers": {
    "gmail-mcp": {
      "type": "http",
      "url": "https://<ref>.supabase.co/functions/v1/<function>",
      "version": "0.1.0"
    }
  }
}
```

Sans ce fichier, Cowork ne sait pas qu'un serveur MCP est associé au plugin.

---

## Plugins

| Plugin | Version | Skills | Serveur MCP | Description |
|--------|---------|--------|-------------|-------------|
| `jobsearch` | 0.4.0 | `cv-generator`, `log-application`, `interview-prep`, `jobsearch-vault` | `gmail-mcp` | CV génération, log candidature, prep d'entretien, accès Gmail, et I/O vault job-search (filesystem-only, lib partagée) |
| `briefing` | 0.2.0 | `morning-briefing` | `hal-mcp` (dédupliqué) | Briefing quotidien read-only (calendriers + hal tasks + jobsearch-vault) |

---

## Install

Dépôt public — pas de token requis. Ajouter le marketplace puis installer les plugins voulus :

```bash
/plugin marketplace add BluegReeno/renaud-marketplace jobsearch
/plugin marketplace add BluegReeno/renaud-marketplace briefing
```

### Connecting from Claude, Gemini, or OpenAI

The MCP servers (**connectors**) and the `SKILL.md` files (**skills**) install differently:
a connector works on all three providers, but skills only run on the agent/CLI surfaces
(Claude Code, Gemini CLI, Codex). Note also that `gmail-mcp` uses an API-key (`?key=`) auth —
which limits it to Claude Code / claude.ai — while `briefing`'s `hal-mcp` uses OAuth and works
everywhere.

Full step-by-step per provider, the auth model, and the cross-client skills setup are in
[`docs/connectors-and-skills.md`](docs/connectors-and-skills.md).

---

## Deploy gmail-mcp

```bash
# 1. Configurer les secrets (à faire une fois)
bash servers/gmail-mcp/scripts/setup_secrets.sh

# 2. Déployer la fonction
cd servers/gmail-mcp
supabase link --project-ref isdyvrwnxqcfalmlkzui
supabase functions deploy --no-verify-jwt gmail-mcp
```

Voir `docs/mcp-server-supabase-edge.md` pour l'architecture complète.

---

## Conventions code

- **Pas de `pip install`** dans les skills — `uv run --with <pkg>` uniquement (contrainte Cowork)
- **Pas de secrets en clair** — `.gitignore` couvre `tmp`, `*.json` OAuth, `.env`, `.temp/`
- Code/commits/filenames : **anglais**. Conversations : français OK.
