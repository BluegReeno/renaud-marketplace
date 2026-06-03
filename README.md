# renaud-marketplace

Private Claude Code skill marketplace for Renaud Laborbe's personal skills — CV generation, job search tools, and productivity plugins too sensitive for public distribution.

## Install (private repo via GitHub PAT)

Add to `~/.claude/settings.json`:

```json
{
  "plugins": {
    "sources": [
      {
        "repo": "BluegReeno/renaud-marketplace",
        "token": "ghp_xxxxxxxxxxxx"
      }
    ]
  }
}
```

Then install a plugin:

```bash
/plugin marketplace add BluegReeno/renaud-marketplace cv-generator
```

## Plugins

| Plugin | Status | Description |
|--------|--------|-------------|
| `cv-generator` | In development | 1-page PDF CV — 5 profiles × 5 company types, FR + EN |

## Project Structure

```
renaud-marketplace/
├── .claude-plugin/
│   └── marketplace.json          # Registry entry point
├── plugins/
│   └── cv-generator/             # First plugin
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── skills/cv-generator/
│       │   └── SKILL.md
│       ├── scripts/
│       │   └── generate_cv.py
│       ├── data/
│       │   └── cv-master.json
│       ├── templates/
│       │   └── cv_template.html
│       └── CHANGELOG.md
└── docs/
    └── skill-marketplace-guide.md  # Architecture & conventions
```

## Development

This project uses Claude Code with a PRD-first methodology.

### Key Commands

```bash
/core_piv_loop:prime          # Load project context
/core_piv_loop:plan-feature   # Plan a new feature
/core_piv_loop:execute        # Execute with task tracking
/handoff                      # Capture session state
/commit                       # Create clean commit
```

## Conventions

- No `pip install` in skills — use `uv run --with <pkg>` (Cowork constraint)
- `marketplace.json` version === `plugin.json` version — always in sync
- Personal data (photo, contact info) stays gitignored
- See [Marketplace Guide](docs/skill-marketplace-guide.md) for full conventions
