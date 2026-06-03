# Project Guidelines for Claude Code

## Language Policy

- **Conversations**: French OK
- **Code, docs, commits, filenames**: English only

---

## Project Overview

**renaud-marketplace** — Private Claude Code skill marketplace for Renaud Laborbe's personal skills (CV generation, job search tools). Too sensitive for public distribution.

**Full specifications**: See `.claude/PRD.md`

---

## Tech Stack

- **Language**: Python 3 (scripts), Markdown (skills)
- **PDF**: WeasyPrint via `uv run --with weasyprint`
- **Data**: JSON (`cv-master.json`)
- **Deploy**: Claude Code marketplace, installed via GitHub PAT

---

## Critical Rules — Marketplace-Specific

### No pre-install step (Cowork constraint)
Skills must never require `pip install`. Every dependency must be loaded at invocation time:

```bash
# NEVER:
pip install weasyprint

# CORRECT:
uv run --with weasyprint python3 $PLUGIN_DIR/scripts/generate_cv.py
```

Prefer stdlib (`json`, `pathlib`, `urllib`, `re`). Only use `--with` for unavoidable packages.

### Versioning — bump on every functional change
Cowork detects updates via version number. Without a bump, installed users never get the fix.

**On every commit that changes plugin behaviour (scripts, templates, SKILL.md, data):**
1. Bump `plugins/<plugin>/.claude-plugin/plugin.json` → PATCH (`0.x.Y+1`) for fixes, MINOR (`0.X+1.0`) for new behaviour
2. Sync `plugins/<plugin>/skills/<skill>/SKILL.md` frontmatter `version:` to the same value
3. Sync `.claude-plugin/marketplace.json` top-level `version` **and** the plugin entry `version` to the same value

All three must be identical after the bump. Drift breaks Cowork updates.

### Plugin directory resolver in every SKILL.md
Every SKILL.md that invokes a script must resolve `PLUGIN_DIR` via the standard priority-ordered resolver (env var → marketplace cache → Cowork sandbox → dev path). See `docs/skill-marketplace-guide.md` §7.

### Photo and personal data
`assets/photo.jpeg` is committed (public repo, photo already on LinkedIn). Other personal data files (keys, tokens, private docs) must be gitignored.

---

## Context System

| Tier | Location | Loaded | Use |
|------|----------|--------|-----|
| 1 | `CLAUDE.md` | Always | Global rules (this file) |
| 2 | `.claude/rules/` | Auto (by path) | Domain conventions |
| 3 | `.claude/docs/` | On-demand | Deep guides |

Always-read: `.claude/PRD.md`, `.claude/STATUS.md`

---

## Task Management

1. Check `STATUS.md` for current focus
2. Read active task file in `.claude/tasks/`
3. Mark `@claude` when starting, `[x] ✓ YYYY-MM-DD` when done
4. Move completed features to `_archive/`

---

## Code Style

- Files: `snake_case.py`
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Max line length: 100 chars

---

## Core Principles

- **Fix forward** — no backward compatibility, remove deprecated code immediately
- **Fail fast** — detailed errors over graceful failures
- **KISS / YAGNI** — simple, no overbuilding
- **Rétro-compat explicit** — old `positioning` param must still work until explicitly removed

---

## External Resources

- [PRD](.claude/PRD.md) | [Status](.claude/STATUS.md) | [Marketplace Guide](docs/skill-marketplace-guide.md)
