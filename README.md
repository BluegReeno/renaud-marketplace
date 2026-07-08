# renaud-marketplace

Personal Claude Code plugin marketplace — MCP servers and AI skills for daily productivity and job-search workflows.

Powered by [hal](https://github.com/BluegReeno/hal) (CRM + morning briefing) and gmail-mcp (email workflows).

---

## Structure du dépôt

```
renaud-marketplace/
├── .claude-plugin/
│   └── marketplace.json          ← point d'entrée Cowork (top-level version = compteur monotone, +0.0.1 par release)
├── plugins/
│   ├── jobsearch/                ← plugin umbrella job search
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json       ← (VERSION ICI)
│   │   ├── .mcp.json             ← déclaration serveur MCP (url + version MCP)
│   │   ├── skills/
│   │   │   ├── cv-generator/SKILL.md       ← skill (pas de version dans le frontmatter)
│   │   │   ├── log-application/SKILL.md    ← skill
│   │   │   ├── interview-prep/SKILL.md     ← skill
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
│       │       └── SKILL.md      ← skill (pas de version dans le frontmatter)
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
├── skills/<skill>/SKILL.md      ← frontmatter: name, description (pas de version)
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
| `jobsearch` | 0.8.3 | `cv-generator`, `cover-letter`, `log-application`, `interview-prep`, `log-cr`, `jobsearch-vault` | `gmail-mcp` | CV génération, lettre de motivation, log candidature, prep d'entretien, log CR, et I/O vault job-search (filesystem-only, lib partagée) |
| `briefing` | 0.8.0 | `morning-briefing`, `mail-triage`, `sprint-review`, `sprint-planner` | `hal-mcp` (dédupliqué) | Briefing quotidien + tri de mails + sprint review + sprint planner (calendriers, hal tasks, jobsearch-vault) |
| `improve` | 0.1.2 | `improve` | — | Capture d'observation sur un skill → GitHub Issue en ≤30s depuis Cowork (`/improve`) |
| `myspy` | 0.1.0 | `myspy` | `hal-mcp` | Check-in hebdomadaire de développement personnel — séance structurée CBT/SFBT avec base de connaissance OKF privée |

---

## Install

Dépôt public — pas de token requis. Ajouter le marketplace puis installer les plugins voulus :

```bash
/plugin marketplace add BluegReeno/renaud-marketplace jobsearch
/plugin marketplace add BluegReeno/renaud-marketplace briefing
/plugin marketplace add BluegReeno/renaud-marketplace improve
/plugin marketplace add BluegReeno/renaud-marketplace myspy
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
