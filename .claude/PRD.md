# renaud-marketplace — Product Requirements Document

**Version**: 1.0
**Last Updated**: 2026-06-03
**Target**: Plugin 1 (cv-generator) — functional build

---

## 1. Mission

Public Claude Code skill marketplace for personal plugins (CV content, job search tools). One command turns a job offer into a perfectly positioned 1-page PDF CV. Secrets and private data are kept out of the repo via gitignore.

```
User pastes job offer
        ↓
Skill detects profile + company type
        ↓
generate_cv(profile, company_type, lang)
        ↓
CV_Renaud_Laborbe_{Profile}_{CompanyType}.pdf  (30 seconds)
```

**Target Users**: Renaud Laborbe (public repo, installed via `/plugin marketplace add`)

**"Wow" Effect**: 15-cell positioning matrix — the skill picks the right narrative, title, about text, and competency containers for every profile × company type combination, in FR or EN.

---

## 2. Architecture

```
renaud-marketplace/
├── .claude-plugin/
│   └── marketplace.json          # Registry (required by Claude Code)
└── plugins/
    └── cv-generator/
        ├── .claude-plugin/
        │   └── plugin.json       # name, version, description, author
        ├── skills/
        │   └── cv-generator/
        │       └── SKILL.md      # Skill instructions
        ├── scripts/
        │   └── generate_cv.py    # PDF generator
        ├── data/
        │   └── cv-master.json    # CV content + 5×5 matrix
        ├── templates/
        │   └── cv_template.html  # HTML/CSS → PDF
        └── CHANGELOG.md
```

---

## 3. Tech Stack

| Component | Technology |
|-----------|------------|
| Skills | Markdown (SKILL.md with frontmatter) |
| PDF generation | WeasyPrint via `uv run --with weasyprint` |
| Data | JSON (cv-master.json) |
| Templating | Jinja2-style HTML + CSS |
| Install | Claude Code marketplace + GitHub PAT |

---

## 4. Data Model

### cv-master.json structure

| Section | Content |
|---------|---------|
| `personal` | Contact info, languages, international experience |
| `education` | Degrees |
| `matrix` | 15 cells — each: `{title, about[3], containers[3]}` × `{fr, en}` |
| `competencies` | Full pool of skills (existing + 5 new ⊕ items) |
| `experiences` | Blue Green, Artelia, Open Ocean, Earlier — bullets indexed by profile |

### Matrix dimensions

**Profiles**: P1 AI Architect · P2 AI Lead/Manager · P3 CTO · P4 CS/FDE · P5 Sales/BizDev

**Company types**: T1 Industrial Startup · T2 Engineering/BET · T3 ESN/Consulting · T4 Large Energy/Industry · T5 AI SaaS/Lab

**15 active cells**: P1×{T1,T2,T3,T4,T5} · P2×{T1,T3,T4,T5} · P3×{T1,T5} · P4×{T1,T5} · P5×{T3,T5}

---

## 5. Features

### Plugin 1: cv-generator

**In Scope**:
- [ ] Marketplace plugin structure (plugin.json, SKILL.md with resolver, CHANGELOG)
- [ ] `cv-master.json` upgraded: 15-cell matrix + 5 new competency items
- [ ] `generate_cv.py` upgraded: `--profile / --company-type / --lang` params
- [ ] SKILL.md: matrix-aware logic (profile + company type detection from job offer)
- [ ] Rétro-compat: `ai_consulting` → P1/T4, `cto` → P3/T1, `business_dev` → P5/T3
- [ ] Experience bullets per profile (5 variants of Blue Green/Artelia/Open Ocean)
- [ ] Profile files: `profiles/{p1,p2,p3,p4,p5}.md` — narrative rules per profile
- [ ] Batch validation: 30 CVs (15 FR + 15 EN), all 1 page
- [ ] Priority test cases: Relief P3×T1, Dust P4×T5, ILLUIN AE P5×T3, ILLUIN Arch P1×T3, Oplit P4×T1

**Out of Scope** (future plugins):
- [ ] notion-jobsearch plugin
- [ ] morning-briefing plugin

---

## 6. User Interface

Single entry point via Claude Code skill:

```
User: [pastes job offer or describes target]
Claude:
  1. Extracts role type + company type from job offer
  2. Selects profile (P1–P5) + company type (T1–T5)
  3. Calls generate_cv(profile, company_type, lang)
  4. Returns: CV_Renaud_Laborbe_P1_T5_EN.pdf (path + summary)
```

---

## 7. Roadmap

### Phase 1: Migration + Matrix Upgrade (current)
- [ ] Marketplace scaffold (plugin.json, marketplace.json)
- [ ] cv-master.json matrix + new competency items
- [ ] generate_cv.py new API + rétro-compat
- [ ] SKILL.md rewrite with plugin resolver
- [ ] Profile .md files
- [ ] Batch validation (30 CVs)
- [ ] Delete legacy skill at `~/Projects/MyClaudeSkills/cv-generator/`

### Phase 2: Future plugins
- [ ] notion-jobsearch
- [ ] morning-briefing (if migrated from personal setup)

---

## 8. Success Criteria

MVP done when:
1. `generate_cv(profile='p1', company_type='t5', lang='en')` produces correct 1-page PDF
2. All 15 cells validated FR + EN (30 PDFs)
3. Old `--positioning ai_consulting/cto/business_dev` still works (rétro-compat)
4. Works in Cowork — zero `pip install` at session start
5. Priority pipelines tested: Relief, Dust, ILLUIN AE, ILLUIN Architect, Oplit

---

## 9. Constraints

```
# No env vars needed for cv-generator
# Installed via /plugin marketplace add (public repo, no PAT needed)
# Photo: committed at assets/photo.jpeg (already public, OK in public repo)
# WeasyPrint: loaded via uv run --with, not pre-installed
```
