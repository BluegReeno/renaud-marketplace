# renaud-marketplace — Current Status

**Last Updated**: 2026-06-03
**Current Phase**: Phase 1 — cv-generator migration + 5×5 matrix upgrade
**Target**: First working build (all 30 CVs validated)

---

## Current Focus

**Task File**: `.claude/tasks/cv-generator-matrix-upgrade.md`

### Priority Order

1. **[P0]** Marketplace scaffold — plugin.json, marketplace.json, SKILL.md stub
2. **[P1]** cv-master.json — add 15-cell matrix + 5 new competency items
3. **[P2]** generate_cv.py — new `--profile / --company-type / --lang` API + rétro-compat
4. **[P3]** SKILL.md rewrite — matrix detection logic + plugin resolver
5. **[P4]** Profile .md files (p1–p5) + batch validation (30 CVs)

---

## What's DONE

### Phase 0: Bootstrap
- [x] Repo scaffold — 2026-06-03
- [x] Content matrix brief: 5 profiles × 5 types, 15 cells, FR + EN — 2026-06-03
- [x] Marketplace field guide (docs/skill-marketplace-guide.md) — 2026-06-03
- [x] PRD, STATUS, CLAUDE.md filled — 2026-06-03
- [x] Marketplace skeleton (.claude-plugin/, plugins/cv-generator/) — 2026-06-03

### Recent Commits
| Feature | Commit | Date |
|---------|--------|------|
| Initial scaffold | 52084f2 | 2026-06-03 |

---

## Architecture

```
renaud-marketplace/ (private GitHub repo)
└── plugins/
    └── cv-generator/
        ├── .claude-plugin/plugin.json   ← v0.1.0
        ├── skills/cv-generator/SKILL.md ← skill instructions
        ├── scripts/generate_cv.py       ← PDF generator
        ├── data/cv-master.json          ← content + 5×5 matrix
        └── templates/cv_template.html   ← HTML → PDF
```

---

## Quick Commands

```bash
# Dev test — single CV
CV_GENERATOR_DIR=~/Projects/renaud-marketplace/plugins/cv-generator \
  uv run --with weasyprint \
  python3 plugins/cv-generator/scripts/generate_cv.py \
  --profile p1 --company-type t5 --lang en

# Batch validation
uv run --with weasyprint \
  python3 plugins/cv-generator/scripts/batch_validate.py
```

---

## Key Files

```
.claude/tasks/cv-generator-matrix-upgrade.md       # Task brief → use for plan-feature
.claude/PRD.md                                     # Project scope
plugins/cv-generator/data/cv-master.json           # Source of truth for CV content
plugins/cv-generator/skills/cv-generator/SKILL.md  # Skill instructions
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Skills | Markdown SKILL.md |
| Scripts | Python 3 + uv run --with |
| PDF | WeasyPrint |
| Data | JSON |

---

**Next Action**: `/core_piv_loop:plan-feature` — use `.claude/tasks/cv-generator-matrix-upgrade.md`
