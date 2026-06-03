# renaud-marketplace — Current Status

**Last Updated**: 2026-06-03
**Current Phase**: Phase 1 COMPLETE — cv-generator v0.1.0 shipped
**Target**: ✅ First working build — 30/30 CVs validated (1 page each)

---

## Current Focus

**DONE** — Ready to commit. Next: visual review of priority CVs + delete legacy source.

---

## What's DONE

### Phase 0: Bootstrap
- [x] Repo scaffold — 2026-06-03
- [x] Content matrix brief: 5 profiles × 5 types, 15 cells, FR + EN — 2026-06-03
- [x] Marketplace field guide (docs/skill-marketplace-guide.md) — 2026-06-03
- [x] PRD, STATUS, CLAUDE.md filled — 2026-06-03
- [x] Marketplace skeleton (.claude-plugin/, plugins/cv-generator/) — 2026-06-03

### Phase 1: cv-generator v0.1.0
- [x] cv_template.html — migrated, emoji-free, 3 dynamic title placeholders — 2026-06-03
- [x] cv-master.json — 15-cell matrix + 5 new competency items + 5-profile experiences — 2026-06-03
- [x] generate_cv.py — new --profile/--company-type/--lang API + retro-compat + corporate-first — 2026-06-03
- [x] batch_validate.py — generates all 30 CVs, asserts 1-page via pikepdf — 2026-06-03
- [x] SKILL.md rewrite — matrix detection + PLUGIN_DIR resolver — 2026-06-03
- [x] Profile files (p1–p5) — narrative rules + anti-patterns — 2026-06-03
- [x] Batch validation: 30/30 CVs pass, 1 page each — 2026-06-03
- [x] Retro-compat verified (--positioning ai_consulting/cto/business_dev) — 2026-06-03
- [x] Versions consistent: plugin.json = marketplace.json = 0.1.0 — 2026-06-03

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
DYLD_LIBRARY_PATH=/opt/homebrew/lib \
CV_GENERATOR_DIR=~/Projects/renaud-marketplace/plugins/cv-generator \
  uv run --with weasyprint \
  python3 plugins/cv-generator/scripts/generate_cv.py \
  --profile p1 --company-type t5 --lang en

# Batch validation
DYLD_LIBRARY_PATH=/opt/homebrew/lib \
CV_GENERATOR_DIR=~/Projects/renaud-marketplace/plugins/cv-generator \
  uv run --with weasyprint --with pikepdf \
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
