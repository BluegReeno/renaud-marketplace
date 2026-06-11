# renaud-marketplace

Public Claude Code skill marketplace for Renaud Laborbe — CV generation, Gmail MCP, and job search tools.

---

## ⚠️ Versioning — règle critique Cowork

**Cowork détecte les mises à jour exclusivement par numéro de version.**
Sans bump de version, les utilisateurs installés ne reçoivent jamais le fix.

### Les 4 fichiers à garder en sync

Pour chaque plugin, **ces 4 fichiers doivent avoir exactement le même numéro de version** :

| Fichier | Champ | Exemple |
|---------|-------|---------|
| `.claude-plugin/marketplace.json` | `version` (top-level) | `"0.2.0"` |
| `.claude-plugin/marketplace.json` | `plugins[].version` | `"0.2.0"` |
| `plugins/<plugin>/.claude-plugin/plugin.json` | `version` | `"0.2.0"` |
| `plugins/<plugin>/skills/<skill>/SKILL.md` | `version:` frontmatter | `0.2.0` |

Si un seul dérive → Cowork ne détecte plus les mises à jour ou refuse l'installation.

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
□ Ai-je modifié scripts/, templates/, data/, ou SKILL.md ?
  → Oui : bump PATCH dans les 4 fichiers ci-dessus
□ Ai-je ajouté un outil ou changé le comportement visible ?
  → Oui : bump MINOR dans les 4 fichiers ci-dessus
□ Les 4 versions sont-elles identiques ?
  → grep -E '"version"' .claude-plugin/marketplace.json plugins/*/.*plugin/plugin.json
  → grep "^version:" plugins/*/skills/*/SKILL.md
```

---

## Structure du dépôt

```
renaud-marketplace/
├── .claude-plugin/
│   └── marketplace.json          ← point d'entrée Cowork (VERSION ICI)
├── plugins/
│   └── jobsearch/                ← plugin umbrella job search
│       ├── .claude-plugin/
│       │   └── plugin.json       ← (VERSION ICI)
│       ├── .mcp.json             ← déclaration serveur MCP (url + version MCP)
│       ├── skills/
│       │   └── cv-generator/
│       │       └── SKILL.md      ← (VERSION ICI dans le frontmatter)
│       ├── scripts/              ← Python — generate_cv.py, batch_validate.py
│       ├── data/                 ← cv-master.json
│       ├── templates/            ← cv_template.html
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
├── .claude-plugin/plugin.json   ← name + version (= marketplace.json)
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
| `jobsearch` | 0.2.0 | `cv-generator` | `gmail-mcp` | CV génération + accès Gmail |

---

## Install

Dépôt public — pas de token requis. Ajouter le marketplace puis installer le plugin :

```bash
/plugin marketplace add BluegReeno/renaud-marketplace jobsearch
```

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
