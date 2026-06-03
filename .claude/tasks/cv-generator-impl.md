# Feature: cv-generator — Implementation (matrix upgrade)

## Goal
Migrate cv-generator from legacy MyClaudeSkills into the renaud-marketplace plugin structure, and upgrade from 3-mode to a 5×5 matrix (15 cells, FR+EN).

## Context
- **Plan Reference**: `.agents/plans/cv-generator-matrix-upgrade.md`
- **Source**: `~/Projects/MyClaudeSkills/cv-generator/`
- **Target**: `plugins/cv-generator/`

## Tasks

### Phase 0 — Template migration
- [x] TASK 1: Create `plugins/cv-generator/templates/cv_template.html` ✓ 2026-06-03
- [x] TASK 2: Create `plugins/cv-generator/data/cv-master.json` ✓ 2026-06-03

### Phase 1 — Data
- [ ] TASK 2: Create `plugins/cv-generator/data/cv-master.json` — personal+education migrated, competencies_pool, 15-cell matrix, 5-profile experiences

### Phase 2 — Script
- [x] TASK 3: Create `plugins/cv-generator/scripts/generate_cv.py` ✓ 2026-06-03

### Phase 3 — Batch validator
- [x] TASK 4: Create `plugins/cv-generator/scripts/batch_validate.py` ✓ 2026-06-03

### Phase 4 — SKILL.md
- [x] TASK 5: Rewrite `plugins/cv-generator/skills/cv-generator/SKILL.md` ✓ 2026-06-03

### Phase 5 — Profile files
- [x] TASK 6: Create 5 profile files in `plugins/cv-generator/profiles/` ✓ 2026-06-03

### Phase 6 — Validation
- [x] TASK 7: Run batch validation (30 CVs, 1-page constraint) — 30/30 OK ✓ 2026-06-03
- [x] TASK 8: Verify retro-compat + copy photo + check version consistency ✓ 2026-06-03

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `plugins/cv-generator/templates/cv_template.html` | Create | Migrated HTML template, emoji-free, 3 dynamic title placeholders |
| `plugins/cv-generator/data/cv-master.json` | Create | Full data: personal, education, competencies_pool, 15-cell matrix, 5-profile experiences |
| `plugins/cv-generator/scripts/generate_cv.py` | Create | New API + retro-compat + corporate-first logic |
| `plugins/cv-generator/scripts/batch_validate.py` | Create | Generate all 30 CVs, assert 1-page via pikepdf |
| `plugins/cv-generator/skills/cv-generator/SKILL.md` | Rewrite | Matrix detection logic + PLUGIN_DIR resolver |
| `plugins/cv-generator/profiles/p1_architecte.md` | Create | Profile narrative rules P1 |
| `plugins/cv-generator/profiles/p2_lead_manager.md` | Create | Profile narrative rules P2 |
| `plugins/cv-generator/profiles/p3_cto.md` | Create | Profile narrative rules P3 |
| `plugins/cv-generator/profiles/p4_cs_fde.md` | Create | Profile narrative rules P4 |
| `plugins/cv-generator/profiles/p5_sales_bizdev.md` | Create | Profile narrative rules P5 |

## Notes
- CRITICAL: `DYLD_LIBRARY_PATH=/opt/homebrew/lib` required for every WeasyPrint call on this Mac
- Corporate-first cells: P1×T4, P2×T4, P5×T5 → experience order Artelia → Blue Green → Open Ocean
- Retro-compat: ai_consulting→(p1,t4), cto→(p3,t1), business_dev→(p5,t3)

## Completion
- **Started**: 2026-06-03
- **Completed**: 2026-06-03
- **Commit**: (ready for /commit)
