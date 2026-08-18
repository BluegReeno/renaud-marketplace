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
│   │   ├── skills/                ← PAS de .mcp.json : gmail-mcp appartient au plugin `briefing`
│   │   │   ├── cv-generator/SKILL.md       ← skill (pas de version dans le frontmatter)
│   │   │   ├── cover-letter/SKILL.md       ← skill
│   │   │   ├── log-application/SKILL.md    ← skill
│   │   │   ├── interview-prep/SKILL.md     ← skill
│   │   │   ├── log-cr/SKILL.md             ← compte-rendu d'entretien (template BANT)
│   │   │   └── jobsearch-vault/SKILL.md    ← filesystem-only vault I/O (lib partagée)
│   │   ├── commands/             ← slash commands
│   │   │   ├── cover-letter.md
│   │   │   ├── interview-prep.md
│   │   │   └── log-application.md
│   │   ├── profiles/             ← p1–p5 narrative files (lus par cv-generator + interview-prep)
│   │   ├── scripts/              ← Python — generate_cv.py, batch_validate.py
│   │   ├── data/                 ← cv-master.json
│   │   └── templates/            ← cv_template.html
│   ├── briefing/                 ← plugin briefing quotidien
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json       ← (VERSION ICI)
│   │   ├── .mcp.json             ← déclaration serveur MCP gmail-mcp (url + version MCP) — hal-mcp reste au plugin `hal`
│   │   ├── skills/
│   │   │   ├── morning-briefing/SKILL.md   ← skill (pas de version dans le frontmatter)
│   │   │   ├── mail-triage/SKILL.md        ← skill
│   │   │   └── book-appointment/SKILL.md   ← écriture calendrier (create-only, interactif)
│   │   ├── agents/
│   │   │   └── cv-log-worker.md  ← sous-agent fan-out appelé par morning-briefing
│   │   └── commands/
│   │       └── briefing.md       ← slash command de déclenchement
│   ├── improve/                  ← capture d'observation → GitHub Issue
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/improve/SKILL.md
│   └── mycoach/                  ← check-in hebdo (écrit dans hal)
│       ├── .claude-plugin/plugin.json
│       └── skills/mycoach/SKILL.md
├── servers/
│   └── gmail-mcp/               ← Supabase Edge Function (Deno/TypeScript)
│       ├── scripts/setup_secrets.sh
│       └── supabase/
│           ├── config.toml
│           └── functions/gmail-mcp/
│               ├── deno.json
│               └── index.ts     ← McpServer version ici (indépendant du plugin)
├── scripts/                     ← outillage de release + gardes CI
│   ├── release.sh               ← bump 4 champs + CHANGELOG en un passage
│   ├── check_version_sync.sh    ← drift plugin.json ↔ marketplace.json ↔ CHANGELOG
│   ├── check_marketplace_schema.sh
│   ├── check_no_identity_literals.sh  ← aucun calendar_id / mail / workspace_slug en dur
│   └── generate_improve_map.py  ← table skill→plugin→repo du skill `improve`
├── probes/                      ← sondes de runtime rejouables (hal-runtime-probe.html)
└── docs/
    ├── skill-marketplace-guide.md
    ├── connectors-and-skills.md
    └── mcp-server-supabase-edge.md
```

### Anatomie d'un plugin

```
plugins/<plugin>/
├── .claude-plugin/plugin.json   ← name + version (= entrée plugins[] de marketplace.json)
├── .mcp.json                    ← optionnel — { "mcpServers": { "<name>": { "type":"http", "url":"...", "version":"..." } } }
├── skills/<skill>/SKILL.md      ← frontmatter: name, description (pas de version)
└── scripts/                     ← invoqués par SKILL.md via uv run --with
```

⚠️ **Un seul plugin déclare un serveur MCP donné.** Claude Code déduplique par URL : deux
`.mcp.json` pointant la même adresse montent arbitrairement l'un ou l'autre, et le nom d'outil
résolu devient non déterministe. `plugins/briefing/.mcp.json` a été supprimé pour cette raison le
2026-07-23 — `hal-mcp` appartient au plugin `hal` de `bluegreen-marketplace`, et les outils se
nomment `mcp__plugin_hal_hal-mcp__*`.

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

Versions à jour au 2026-08-18 — source de vérité : `plugins/<plugin>/.claude-plugin/plugin.json`.

| Plugin | Version | Skills | Serveur MCP | Description |
|--------|---------|--------|-------------|-------------|
| `jobsearch` | 0.11.1 | `cv-generator`, `cover-letter`, `log-application`, `interview-prep`, `log-cr`, `jobsearch-vault` | `gmail-mcp` **via le plugin `briefing`** | CV génération, lettre de motivation, log candidature, prep d'entretien, log CR, et I/O vault job-search (filesystem-only, lib partagée) |
| `briefing` | 0.15.0 | `morning-briefing`, `mail-triage`, `book-appointment` (+ agent `cv-log-worker`) | `gmail-mcp` (déclaré ici), `hal-mcp` **via le plugin `hal`** | Briefing quotidien, tri de mails et prise de rendez-vous (calendriers résolus depuis les workspaces hal, hal tasks, jobsearch-vault). Depuis 0.12.0, `sprint-planner` et `sprint-review` vivent dans `pm@bluegreen-marketplace` |
| `improve` | 0.3.0 | `improve` | — | Capture d'observation sur un skill → GitHub Issue en ≤30s depuis Cowork (`/improve`) |
| `mycoach` | 0.4.0 | `mycoach` | `hal-mcp` **via le plugin `hal`** | Check-in hebdomadaire de développement personnel — séance structurée CBT/SFBT avec base de connaissance OKF privée |

`briefing` et `mycoach` **exigent le plugin `hal`** (`bluegreen-marketplace`) installé pour leurs
appels `mcp__plugin_hal_hal-mcp__*` — ni l'un ni l'autre ne déclare ce serveur. `jobsearch`
exige quant à lui le plugin `briefing` installé pour son unique appel gmail-mcp
(`cover-letter` → `mcp__plugin_briefing_gmail-mcp__draft_email`).

---

## Install

Dépôt public — pas de token requis. Ajouter le marketplace puis installer les plugins voulus :

```bash
# 1. enregistrer le marketplace (une fois)
/plugin marketplace add BluegReeno/renaud-marketplace

# 2. installer les plugins voulus
/plugin install jobsearch@renaud-marketplace
/plugin install briefing@renaud-marketplace
/plugin install improve@renaud-marketplace
/plugin install mycoach@renaud-marketplace
```

### Connecting from Claude, Gemini, or OpenAI

The MCP servers (**connectors**) and the `SKILL.md` files (**skills**) install differently:
a connector works on all three providers, but skills only run on the agent/CLI surfaces
(Claude Code, Gemini CLI, Codex). Both servers run an OAuth 2.1 authorization server, so both
connect by URL alone; `gmail-mcp` additionally accepts a shared API key (`?key=`) for headerless
clients like claude.ai. The `briefing` plugin itself takes the **OAuth path** — its `.mcp.json`
carries the bare URL — and every caller, keyed or OAuth, is gated by the `GMAIL_ALLOWED_USER_IDS`
allowlist.

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

⚠️ **Le compte Supabase dépend du répertoire, via direnv.** `renaud-marketplace/.envrc` porte le
token du compte perso, propriétaire de `isdyvrwnxqcfalmlkzui` ; lancer une commande `supabase`
depuis `~/Projects/hal` viserait le bon projet avec le mauvais compte. Si le CLI refuse un PAT au
format `sbp_v0_…`, voir `servers/gmail-mcp/README.md` §*When the CLI refuses your token*.

Voir `docs/mcp-server-supabase-edge.md` pour l'architecture complète, et
`docs/connectors-and-skills.md` pour le modèle d'authentification par client.

---

## Conventions code

- **Pas de `pip install`** dans les skills — `uv run --with <pkg>` uniquement (contrainte Cowork)
- **Pas de secrets en clair** — `.gitignore` couvre `tmp`, `*.json` OAuth, `.env`, `.temp/`
- Code/commits/filenames : **anglais**. Conversations : français OK.
