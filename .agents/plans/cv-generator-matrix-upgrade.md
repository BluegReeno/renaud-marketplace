# Feature: cv-generator — Migration Marketplace + Matrice 5×5

> Validate documentation and codebase patterns before implementing.
> Pay attention to the exact placeholder names in the HTML template and JSON key naming conventions.

> **CRITICAL — ENVIRONMENT**: WeasyPrint requires `DYLD_LIBRARY_PATH=/opt/homebrew/lib` on this Mac (GLib/Pango are installed via Homebrew but not in default dyld path). Without this prefix, ALL `uv run --with weasyprint` calls crash with `OSError: cannot load library 'libgobject-2.0-0'`. This has been verified — add it to every command and to `batch_validate.py`'s `subprocess.run` env.

---

## Feature Description

Migrate the existing `cv-generator` skill from `~/Projects/MyClaudeSkills/cv-generator/` into the `renaud-marketplace` plugin structure at `plugins/cv-generator/`, AND upgrade it from a 3-mode system (`ai_consulting / cto / business_dev`) to a **5 profiles × 5 company types** matrix with **15 active cells**, bilingual (FR + EN), with full batch validation (30 PDFs, all 1-page A4).

## User Story

As Renaud Laborbe  
I want to type `/cv-generator` then paste a job offer  
So that Claude picks the right profile × company-type cell and generates a perfectly positioned 1-page PDF CV in 30 seconds, in the right language

## Problem Statement

The current 3-mode skill can't capture the nuance of Renaud's actual candidate positioning (e.g. CTO vs Architecte vs CS/FDE vs Sales are radically different narratives). The legacy code also lives outside the marketplace structure and uses a `pip install` approach that breaks in Cowork.

## Solution Statement

1. Copy and upgrade the source files into the marketplace plugin structure.
2. Replace the 3 generic modes with a 15-cell matrix (5 profiles × 5 company types) in `cv-master.json`.
3. Upgrade `generate_cv.py` with a new `--profile / --company-type / --lang` API while preserving retro-compat.
4. Rewrite `SKILL.md` with matrix-aware detection logic and the standard 4-step `PLUGIN_DIR` resolver.
5. Validate all 30 CVs stay on 1 page A4.

## Feature Metadata

**Feature Type**: Enhancement (migration + major content upgrade)  
**Estimated Complexity**: High  
**Primary Systems Affected**: `plugins/cv-generator/` (all files)  
**Dependencies**: `weasyprint` (via `uv run --with`), `pikepdf` (batch validation only)

---

## CONTEXT REFERENCES

### Mandatory reading — YOU MUST READ THESE FILES BEFORE IMPLEMENTING

| File | Lines | Why |
|------|-------|-----|
| `~/Projects/MyClaudeSkills/cv-generator/scripts/generate_cv.py` | All | Source to migrate — understand the `{{PLACEHOLDER}}` replacement pattern and HTML generation flow |
| `~/Projects/MyClaudeSkills/cv-generator/data/cv-master.json` | All | Source data structure — migrate `personal`, `education`, `competencies` sections intact |
| `~/Projects/MyClaudeSkills/cv-generator/templates/cv_template.html` | All | Source template — migrate and fix emoji → text, add 3 new `{{COMP_*_TITLE}}` placeholders |
| `.claude/tasks/cv-generator-matrix-upgrade.md` | All | Full matrix content — 15 cells with title/about/containers in EN+FR; experience bullet context per profile |
| `.claude/PRD.md` | All | Data model spec and success criteria |
| `docs/skill-marketplace-guide.md` | All | Marketplace conventions, resolver pattern (§7) |

### Existing marketplace scaffold (already done — do NOT recreate)

| File | Status |
|------|--------|
| `plugins/cv-generator/.claude-plugin/plugin.json` | ✅ exists, v0.1.0 |
| `.claude-plugin/marketplace.json` | ✅ exists, v0.1.0 |
| `plugins/cv-generator/skills/cv-generator/SKILL.md` | ✅ stub — needs full rewrite |
| `plugins/cv-generator/CHANGELOG.md` | ✅ exists |

### New files to create

| File | Description |
|------|-------------|
| `plugins/cv-generator/scripts/generate_cv.py` | Upgraded generator — new `--profile/--company-type/--lang` API |
| `plugins/cv-generator/data/cv-master.json` | Migrated data + 15-cell matrix + 5 new competency items |
| `plugins/cv-generator/templates/cv_template.html` | Migrated template (emoji fixed, 3 title placeholders added) |
| `plugins/cv-generator/scripts/batch_validate.py` | Generates all 30 CVs, validates 1-page constraint via pikepdf |
| `plugins/cv-generator/profiles/p1_architecte.md` | Profile narrative rules for P1 |
| `plugins/cv-generator/profiles/p2_lead_manager.md` | Profile narrative rules for P2 |
| `plugins/cv-generator/profiles/p3_cto.md` | Profile narrative rules for P3 |
| `plugins/cv-generator/profiles/p4_cs_fde.md` | Profile narrative rules for P4 |
| `plugins/cv-generator/profiles/p5_sales_bizdev.md` | Profile narrative rules for P5 |

### Patterns to follow

**CLI argument pattern** (from legacy `generate_cv.py:234-276`):
```python
parser.add_argument('--profile', '-p', choices=['p1','p2','p3','p4','p5'], default='p1')
parser.add_argument('--company-type', '-c', choices=['t1','t2','t3','t4','t5'], default='t4')
parser.add_argument('--lang', '-l', choices=['en', 'fr'], default='en')
# Retro-compat: keep --positioning for backward compat, but map internally
parser.add_argument('--positioning', help=argparse.SUPPRESS)  # hidden, retro-compat
```

**Retro-compat mapping** (tranche in main before resolve):
```python
RETRO_COMPAT_MAP = {
    'ai_consulting': ('p1', 't4'),
    'cto':           ('p3', 't1'),
    'business_dev':  ('p5', 't3'),
}
```

**Template placeholder pattern** (string `.replace()`, from legacy `generate_cv.py:54-133`):
```python
html = html.replace('{{TITLE}}', title)
html = html.replace('{{ABOUT_1}}', about_lines[0])
# ... etc
```

**New placeholders required by matrix**:
- `{{COMP_AI_TITLE}}` — container 1 title (gold, dynamic per cell)
- `{{COMP_BUSINESS_TITLE}}` — container 2 title (green, dynamic per cell)
- `{{COMP_SECTOR_TITLE}}` — container 3 title (blue, dynamic per cell)

**Emoji fix**: Replace emoji in template with CSS-only approach or simple Unicode:
```html
<!-- BEFORE (breaks WeasyPrint) -->
<span class="about-icon">👥</span>

<!-- AFTER (works with WeasyPrint) -->
<span class="about-icon">&#8250;</span>  <!-- › (single right angle quotation mark) -->
<!-- OR remove icon span entirely and use CSS ::before -->
```
Simplest working solution: remove the `<span class="about-icon">` and `<span class="contact-icon">` spans entirely. The layout still works because the flexbox gap handles spacing. Alternatively use `&#8250;` (›) or `&#10148;` (➤).

**Corporate-first rule** — for T4 (grand groupe) and P5×T5, experience order is Artelia → Blue Green → Open Ocean:
```python
CORPORATE_FIRST_CELLS = {('p1','t4'), ('p2','t4'), ('p5','t5')}
if (profile, company_type) in CORPORATE_FIRST_CELLS:
    job_order = ['artelia', 'blue_green', 'open_ocean']
else:
    job_order = ['blue_green', 'artelia', 'open_ocean']
```

**Output filename convention**:
```
CV_Renaud_Laborbe_P1_T5_EN.pdf   (new format)
CV_Renaud_Laborbe_ai_consulting.pdf  (retro-compat: keep old name when --positioning used)
```

---

## IMPLEMENTATION PLAN

### Phase 0: Template migration + fix

Migrate `cv_template.html` from legacy, fix emoji, add 3 dynamic title placeholders for competency containers. This file drives the visual output of every CV.

### Phase 1: cv-master.json — full content build

The most content-heavy task. Migrate the unchanged sections (`personal`, `education`) and rewrite the rest:
- `competencies_pool` — migrated from `competencies` + 5 new items
- `matrix` — 15 cells, each with `title/about/containers` in EN+FR
- `experiences` — bullets expanded from 3 variants to 5 profiles × EN+FR

### Phase 2: generate_cv.py upgrade

New API on top of the same HTML-replacement engine. Retro-compat layer before profile resolution. Corporate-first logic. Clean output naming.

### Phase 3: batch_validate.py

Iterate 15 valid cells × 2 langs = 30 outputs. Use pikepdf to assert exactly 1 page per PDF. Report failures clearly.

### Phase 4: SKILL.md full rewrite

Matrix-aware detection from job offer → profile × company type. Standard 4-step resolver. Language detection. Clean call syntax.

### Phase 5: Profile .md files

5 files with narrative rules, cases, anti-patterns, real examples. Reference material for the SKILL.md detection logic and for manual use.

---

## STEP-BY-STEP TASKS

### TASK 1 — CREATE `plugins/cv-generator/templates/cv_template.html`

- **MIGRATE**: Copy from `~/Projects/MyClaudeSkills/cv-generator/templates/cv_template.html`
- **FIX emoji**: Replace `<span class="about-icon">👥</span>`, `🌍`, `📈`, `📞`, `✉️`, `📍`, `🔗` with `<span class="about-icon">&#8250;</span>` or remove the icon spans entirely (remove the span + its content, keep only the text span). Removing the icon spans is the safest approach.
- **ADD** 3 new dynamic title placeholders — replace the 3 hardcoded `<div class="competency-title">` values:
  - `AI & Digital` → `{{COMP_AI_TITLE}}`
  - `Business & Leadership` → `{{COMP_BUSINESS_TITLE}}`
  - `Sector Expertise` → `{{COMP_SECTOR_TITLE}}`
- **KEEP** all CSS, colors (`#E7AF44` gold, `#4EA265` green, `#3C9ED9` blue), layout, and existing placeholders (`{{TITLE}}`, `{{ABOUT_1-3}}`, `{{COMP_AI}}`, `{{COMP_BUSINESS}}`, `{{COMP_SECTOR}}`, `{{JOB1_TITLE}}` etc.) exactly as-is
- **VALIDATE**: `grep -c '{{' plugins/cv-generator/templates/cv_template.html` should return ≥ 16

---

### TASK 2 — CREATE `plugins/cv-generator/data/cv-master.json`

This is the largest task. Build the JSON file with 4 top-level sections:

#### 2a — `personal` and `education` sections
- **COPY** verbatim from `~/Projects/MyClaudeSkills/cv-generator/data/cv-master.json` lines 2-26 (no changes)

#### 2b — `competencies_pool` section
- **MIGRATE** from legacy `competencies` block (rename key from `competencies` to `competencies_pool`)
- **ADD** 5 new items (marked ⊕ in the task brief):
  - To `ai_digital`: `"Document Intelligence & Reporting"`, `"AI Evals & Observability"`, `"Solution Scoping & Proposals"`
  - To `business_leadership`: `"AI Awareness Training"`, `"Customer Onboarding & Adoption"`
- Keep existing items, just append new ones

#### 2c — `matrix` section — THE CORE CONTENT

Structure: `matrix[profile][company_type]` — only the 15 valid cells (skip invalid ones).

Each cell schema:
```json
{
  "title": {"en": "...", "fr": "..."},
  "about": {
    "en": ["line 1", "line 2", "line 3"],
    "fr": ["ligne 1", "ligne 2", "ligne 3"]
  },
  "containers": {
    "en": [
      {"title": "Container 1 Title", "items": ["item1", "item2", "item3", "item4"]},
      {"title": "Container 2 Title", "items": ["item1", "item2", "item3"]},
      {"title": "Container 3 Title", "items": ["item1", "item2", "item3"]}
    ],
    "fr": [
      {"title": "Titre Conteneur 1", "items": [...]},
      {"title": "Titre Conteneur 2", "items": [...]},
      {"title": "Titre Conteneur 3", "items": [...]}
    ]
  },
  "credibility_note": {"en": "...", "fr": "..."}
}
```

**All 15 cells to create** — content sourced from `.claude/tasks/cv-generator-matrix-upgrade.md` sections P1–P5:

| Cell | Title EN | Title FR |
|------|----------|----------|
| p1×t1 | `AI Product Architect — Industrial Data & GenAI` | `Architecte Produit IA — Données industrielles & GenAI` |
| p1×t2 | `AI Architect — GenAI for Engineering Workflows` | `Architecte IA — GenAI pour les métiers de l'ingénierie` |
| p1×t3 | `GenAI Solution Architect — Pre-Sales to Production` | `Architecte Solutions GenAI — De l'avant-vente à la production` |
| p1×t4 | `AI Solutions Architect — Energy & Industry` | `Architecte Solutions IA — Énergie & Industrie` |
| p1×t5 | `Applied AI Architect — Enterprise GenAI Deployments` | `Architecte Applied AI — Déploiements GenAI enterprise` |
| p2×t1 | `AI Lead — Player-Coach for Industrial Scale-ups` | `AI Lead — Player-coach pour scale-ups industrielles` |
| p2×t3 | `GenAI Practice Lead — Build, Sell, Deliver` | `Responsable Practice GenAI — Construire, vendre, livrer` |
| p2×t4 | `AI Lead — Industrial AI Transformation` | `AI Lead — Transformation IA industrielle` |
| p2×t5 | `AI Product Lead — From Prototype to Production` | `Lead Produit IA — Du prototype à la production` |
| p3×t1 | `CTO — Scaling AI-Powered Solutions for Climate & Industry` | `CTO — Scale-up de solutions IA pour le climat & l'industrie` |
| p3×t5 | `CTO — AI SaaS, from First Commit to Scale` | `CTO — SaaS IA, du premier commit au scale` |
| p4×t1 | `Forward Deployed Engineer — Industrial AI` | `Forward Deployed Engineer — IA industrielle` |
| p4×t5 | `AI Solutions Engineer — Enterprise GenAI Adoption` | `Solutions Engineer IA — Adoption GenAI enterprise` |
| p5×t3 | `Senior Account Executive — AI Consulting & Services` | `Senior Account Executive — Conseil & services IA` |
| p5×t5 | `Account Executive — GenAI for Energy & Industry` | `Account Executive — GenAI pour l'énergie & l'industrie` |

**Container items**: Read the exact items from the task brief for each cell under each "Containers EN/FR" line. Item names must EXACTLY match items in `competencies_pool` (for traceability), including the ⊕ new items.

**- GOTCHA**: `p2` has no `t2` or `t5` key; `p3` has no `t2`, `t3`, `t4`; `p4` has no `t2`, `t3`, `t4`; `p5` has no `t1`, `t2`, `t4`. Do not create empty keys for missing cells.

#### 2d — `experiences` section

Expand from 3 positioning variants to 5 profile variants × EN+FR. Structure:

```json
{
  "blue_green": {
    "company": "Blue Green",
    "location": "Paris, France",
    "period": "2023 – Present",
    "titles": {
      "p1": {"en": "AI Solutions Architect", "fr": "Architecte Solutions IA"},
      "p2": {"en": "AI Lead", "fr": "AI Lead"},
      "p3": {"en": "AI & Technology Director", "fr": "Directeur IA & Technologie"},
      "p4": {"en": "AI Solutions Engineer", "fr": "Solutions Engineer IA"},
      "p5": {"en": "AI Business Developer", "fr": "Business Developer IA"}
    },
    "bullets": {
      "p1": {
        "en": [
          "Designed and deployed end-to-end AI solutions for EnBW France (offshore wind tender analysis) and Valorem (urban planning automation)",
          "Architected production GenAI systems: RAG (22,800-chunk pgvector index), 5 Pydantic AI agents, MCP servers — BlueWind Companion v2.2 live",
          "Technical stack: LLMs (Claude, Mistral), RAG, AI Agents, MCP servers, workflow automation"
        ],
        "fr": [
          "Conçu et déployé des solutions IA bout-en-bout pour EnBW France (analyse d'AO éolien offshore) et Valorem (automatisation urbanisme)",
          "Architecture de systèmes GenAI en production : RAG (22 800 chunks pgvector), 5 agents Pydantic AI, serveurs MCP — BlueWind Companion v2.2 live",
          "Stack : LLMs (Claude, Mistral), RAG, Agents IA, serveurs MCP, automatisation de workflows"
        ]
      },
      "p2": {
        "en": [
          "Led end-to-end AI delivery for enterprise clients (EnBW France, Valorem): scoping, architecture, production deployment",
          "Architected multi-agent GenAI platform (BlueWind Companion v2.2): RAG, 5 AI agents, MCP servers — live in production",
          "Conducted AI awareness workshops and facilitated cross-functional adoption"
        ],
        "fr": [
          "Piloté le delivery IA bout-en-bout pour des clients enterprise (EnBW France, Valorem) : cadrage, architecture, mise en production",
          "Architecture de plateforme GenAI multi-agents (BlueWind Companion v2.2) : RAG, 5 agents IA, serveurs MCP — live en production",
          "Animé des ateliers de sensibilisation à l'IA et facilité l'adoption cross-fonctionnelle"
        ]
      },
      "p3": {
        "en": [
          "Built and shipped full-stack AI SaaS platform (BlueWind Companion v2.2): Next.js, FastAPI, Pydantic AI, pgvector — live in France",
          "Architected and deployed production GenAI systems for enterprise clients (EnBW France, Valorem)",
          "Defined technical roadmap, selected stack, and led end-to-end delivery solo at maximum velocity"
        ],
        "fr": [
          "Construit et livré une plateforme SaaS IA full-stack (BlueWind Companion v2.2) : Next.js, FastAPI, Pydantic AI, pgvector — live en France",
          "Architecture et déploiement de systèmes GenAI en production pour des clients enterprise (EnBW France, Valorem)",
          "Défini la roadmap technique, choisi le stack, dirigé le delivery bout-en-bout en solo à vélocité maximale"
        ]
      },
      "p4": {
        "en": [
          "Deployed AI solutions for industrial clients (EnBW France, Valorem): discovery, integration, production handover",
          "Built RAG systems and AI agents adapted to client workflows (offshore wind analysis, urban planning automation)",
          "Conducted AI awareness workshops and onboarded client teams to autonomous use"
        ],
        "fr": [
          "Déployé des solutions IA chez des clients industriels (EnBW France, Valorem) : discovery, intégration, mise en production",
          "Construit des systèmes RAG et agents IA adaptés aux workflows clients (analyse d'AO éolien offshore, automatisation urbanisme)",
          "Animé des ateliers de sensibilisation à l'IA et accompagné l'autonomisation des équipes clients"
        ]
      },
      "p5": {
        "en": [
          "Developed and closed AI consulting engagements with enterprise clients (EnBW France, Valorem): full cycle from prospecting to signed contract",
          "Ran discovery sessions, scoped GenAI solutions, and produced commercial proposals for C-level decision-makers",
          "AI Awareness Training for renewable energy developers: positions Blue Green as the go-to GenAI partner"
        ],
        "fr": [
          "Développé et closé des missions de conseil IA avec des clients enterprise (EnBW France, Valorem) : cycle complet de la prospection au contrat signé",
          "Animé des sessions de discovery, cadré des solutions GenAI et rédigé des propales commerciales pour des décideurs C-level",
          "Ateliers de sensibilisation à l'IA pour des développeurs d'énergie renouvelable : positionne Blue Green comme le partenaire GenAI de référence"
        ]
      }
    }
  },
  "artelia": {
    "company": "Artelia",
    "location": "London, UK",
    "period": "2019 – 2022",
    "titles": {
      "p1": {"en": "Business Development & Project Director", "fr": "Directeur Développement & Projets"},
      "p2": {"en": "Business Development & Project Director", "fr": "Directeur Développement & Projets"},
      "p3": {"en": "Business Development & Project Director", "fr": "Directeur Développement & Projets"},
      "p4": {"en": "Business Development & Project Director", "fr": "Directeur Développement & Projets"},
      "p5": {"en": "Business Development & Project Director", "fr": "Directeur Développement & Projets"}
    },
    "bullets": {
      "p1": {
        "en": [
          "Drove product roadmap alignment with market requirements for offshore wind data services",
          "Managed client portfolio generating 15% YOY revenue growth through C-level negotiations",
          "Full P&L responsibility for the offshore wind business unit"
        ],
        "fr": [
          "Aligné la roadmap produit avec les besoins du marché pour les services de données éolien offshore",
          "Géré un portefeuille clients générant +15% de croissance annuelle via des négociations C-level",
          "Responsabilité P&L complète de la business unit éolien offshore"
        ]
      },
      "p2": {
        "en": [
          "Managed cross-functional teams delivering offshore wind data services to major European clients",
          "Drove 15% YOY revenue growth through strategic client engagement and C-level negotiations",
          "Full P&L responsibility for the offshore wind business unit in London"
        ],
        "fr": [
          "Managé des équipes transverses livrant des services de données éolien offshore à de grands clients européens",
          "+15% de croissance annuelle via engagement client stratégique et négociations C-level",
          "Responsabilité P&L complète de la business unit éolien offshore à Londres"
        ]
      },
      "p3": {
        "en": [
          "Led investor presentations and technical due diligence for offshore wind data services",
          "Managed client portfolio generating 15% YOY revenue growth; Full P&L responsibility",
          "Drove product development aligned with major European offshore wind developers"
        ],
        "fr": [
          "Dirigé les présentations investisseurs et la due diligence technique pour les services de données éolien offshore",
          "Géré un portefeuille clients avec +15% de croissance annuelle ; responsabilité P&L complète",
          "Piloté le développement produit en alignement avec les grands développeurs éoliens offshore européens"
        ]
      },
      "p4": {
        "en": [
          "Deployed offshore wind data services with major European developers (DCNS, SBM Offshore, RTE)",
          "Managed client portfolio generating 15% YOY growth — discovery, proposal, delivery, adoption",
          "Facilitated cross-functional collaboration between engineering teams and client operations"
        ],
        "fr": [
          "Déployé des services de données éolien offshore avec de grands développeurs européens (DCNS, SBM Offshore, RTE)",
          "Géré un portefeuille clients avec +15% de croissance — discovery, propale, delivery, adoption",
          "Facilité la collaboration cross-fonctionnelle entre équipes ingénierie et opérations clients"
        ]
      },
      "p5": {
        "en": [
          "Managed offshore wind enterprise portfolio generating 15% YOY revenue growth",
          "Negotiated complex enterprise contracts with C-level executives across Europe",
          "Created powerful presentations for Investor Days and C-Level meetings; Full P&L responsibility"
        ],
        "fr": [
          "Géré un portefeuille enterprise éolien offshore générant +15% de croissance annuelle",
          "Négocié des contrats enterprise complexes avec des dirigeants C-level à travers l'Europe",
          "Créé des présentations percutantes pour les Journées Investisseurs et réunions C-Level ; P&L complet"
        ]
      }
    }
  },
  "open_ocean": {
    "company": "Open Ocean",
    "location": "Paris, France",
    "period": "2011 – 2019",
    "titles": {
      "p1": {"en": "Co-Founder & CTO", "fr": "Co-Fondateur & CTO"},
      "p2": {"en": "Co-Founder & Managing Director", "fr": "Co-Fondateur & Directeur Général"},
      "p3": {"en": "Co-Founder & CTO", "fr": "Co-Fondateur & CTO"},
      "p4": {"en": "Co-Founder & Managing Director", "fr": "Co-Fondateur & Directeur Général"},
      "p5": {"en": "Co-Founder & Managing Director", "fr": "Co-Fondateur & Directeur Général"}
    },
    "bullets": {
      "p1": {
        "en": [
          "Architected and scaled marine data intelligence SaaS platform from prototype to industrial deployment (team of 12, €2M raised, exit)",
          "Led product development: client requirements, technical roadmap, agile delivery — major clients: DCNS, SBM Offshore, RTE",
          "Raised €2M from Business Angels and VCs — successful exit through acquisition by Artelia (2019)"
        ],
        "fr": [
          "Architecture et scale-up d'une plateforme SaaS de données marines du prototype au déploiement industriel (équipe 12, €2M levés, exit)",
          "Pilotage du développement produit : besoins clients, roadmap technique, delivery agile — clients majeurs : DCNS, SBM Offshore, RTE",
          "Levée de €2M (Business Angels et VCs) — exit réussi par acquisition par Artelia (2019)"
        ]
      },
      "p2": {
        "en": [
          "Built and led a 12-person multidisciplinary product team (engineers, data scientists, web specialists)",
          "Scaled marine data intelligence SaaS platform from prototype to industrial deployment",
          "Raised €2M — successful exit through acquisition by Artelia (2019)"
        ],
        "fr": [
          "Construit et dirigé une équipe produit pluridisciplinaire de 12 (ingénieurs, data scientists, web)",
          "Scale-up de la plateforme SaaS data marines du prototype au déploiement industriel",
          "Levée de €2M — exit réussi par acquisition par Artelia (2019)"
        ]
      },
      "p3": {
        "en": [
          "Architected and scaled marine data intelligence SaaS from prototype to industrial deployment",
          "Led product development with a 12-person team: roadmap, agile delivery, major clients (DCNS, SBM Offshore, RTE)",
          "Raised €2M from Business Angels and VCs — successful exit by acquisition (Artelia, 2019)"
        ],
        "fr": [
          "Architecture et scale-up d'un SaaS de données marines du prototype au déploiement industriel",
          "Dirigé le développement produit avec une équipe de 12 : roadmap, delivery agile, clients majeurs (DCNS, SBM Offshore, RTE)",
          "Levée de €2M (Business Angels et VCs) — exit réussi par acquisition (Artelia, 2019)"
        ]
      },
      "p4": {
        "en": [
          "Deployed marine data intelligence SaaS with major industrial clients (DCNS, SBM Offshore, RTE)",
          "Owned 100% of client-facing delivery: discovery, proposal, implementation, adoption",
          "Raised €2M — successful exit through acquisition by Artelia (2019)"
        ],
        "fr": [
          "Déployé le SaaS data marines chez des clients industriels majeurs (DCNS, SBM Offshore, RTE)",
          "Porté 100% du delivery client : discovery, propale, implémentation, adoption",
          "Levée de €2M — exit réussi par acquisition par Artelia (2019)"
        ]
      },
      "p5": {
        "en": [
          "Owned 100% of sales cycles from prospecting to C-level closing (8 years)",
          "Scaled marine data intelligence SaaS platform — major clients across Europe (DCNS, SBM Offshore, RTE)",
          "Raised €2M from Business Angels and VCs — successful exit through acquisition by Artelia (2019)"
        ],
        "fr": [
          "Porté 100% des cycles de vente de la prospection au closing C-level (8 ans)",
          "Scale-up de la plateforme SaaS data marines — clients majeurs en Europe (DCNS, SBM Offshore, RTE)",
          "Levée de €2M (Business Angels et VCs) — exit réussi par acquisition par Artelia (2019)"
        ]
      }
    }
  },
  "earlier": {
    "period": "2004 – 2010",
    "items": [
      {"title": "Product Developer", "company": "SAT OCEAN", "description": "marine metocean data services", "period": "2006-2010"},
      {"title": "Data Analyst", "company": "CPTEC", "description": "extreme events data analysis", "location": "Brazil", "period": "2004-2005"}
    ]
  }
}
```

- **VALIDATE**: `python3 -c "import json; d=json.load(open('plugins/cv-generator/data/cv-master.json')); assert len([c for p in d['matrix'].values() for c in p]) == 15, f'Expected 15 cells, got {len([c for p in d[\"matrix\"].values() for c in p])}'; print('OK — 15 cells')" `

---

### TASK 3 — CREATE `plugins/cv-generator/scripts/generate_cv.py`

New script built on the same `{{PLACEHOLDER}}` replacement engine as legacy. Key changes:

**New function signature**:
```python
def generate_cv(profile='p1', company_type='t4', lang='en',
                output_filename=None, output_dir=None):
```

**Matrix lookup** (replaces legacy `titles.get(positioning)`):
```python
def get_cell(cv_data, profile, company_type):
    try:
        return cv_data['matrix'][profile][company_type]
    except KeyError:
        valid = [(p, ct) for p, cts in cv_data['matrix'].items() for ct in cts]
        raise ValueError(f"Cell ({profile}, {company_type}) not in matrix. Valid cells: {valid}")

def resolve_cell_content(cv_data, profile, company_type, lang):
    cell = get_cell(cv_data, profile, company_type)
    return {
        'title': cell['title'][lang],
        'about': cell['about'][lang],
        'containers': cell['containers'][lang],
    }
```

**Experience ordering** (corporate_first rule):
```python
CORPORATE_FIRST_CELLS = {('p1', 't4'), ('p2', 't4'), ('p5', 't5')}

def get_job_order(profile, company_type):
    if (profile, company_type) in CORPORATE_FIRST_CELLS:
        return ['artelia', 'blue_green', 'open_ocean']
    return ['blue_green', 'artelia', 'open_ocean']
```

**HTML generation** — the `generate_cv_html()` function must handle:
- `{{COMP_AI_TITLE}}` / `{{COMP_BUSINESS_TITLE}}` / `{{COMP_SECTOR_TITLE}}` from `containers[0/1/2]['title']`
- `{{COMP_AI}}` / `{{COMP_BUSINESS}}` / `{{COMP_SECTOR}}` from `containers[0/1/2]['items']`
- Job 1/2/3 slots filled from `job_order` (not hardcoded blue_green/artelia/open_ocean)
- Bilingual experience titles and bullets from `experiences[job_key]['titles'][profile][lang]` and `experiences[job_key]['bullets'][profile][lang]`

**Retro-compat in `main()`**:
```python
RETRO_COMPAT_MAP = {
    'ai_consulting': ('p1', 't4'),
    'cto':           ('p3', 't1'),
    'business_dev':  ('p5', 't3'),
}

# In main():
if args.positioning:
    if args.positioning in RETRO_COMPAT_MAP:
        profile, company_type = RETRO_COMPAT_MAP[args.positioning]
        output_filename = output_filename or f"CV_Renaud_Laborbe_{args.positioning}.pdf"
    else:
        parser.error(f"Unknown --positioning value: {args.positioning}")
```

**Output filename**:
```python
# Default (new API): CV_Renaud_Laborbe_P1_T5_EN.pdf
output_filename = output_filename or f"CV_Renaud_Laborbe_{profile.upper()}_{company_type.upper()}_{lang.upper()}.pdf"
```

- **GOTCHA**: `get_skill_dir()` must resolve relative to `__file__` (same as legacy — `Path(__file__).parent.parent`). The script lives at `plugins/cv-generator/scripts/generate_cv.py` so `parent.parent` = `plugins/cv-generator/`.
- **GOTCHA**: Photo copy must use the resolved skill dir, not CWD.
- **VALIDATE**: `DYLD_LIBRARY_PATH=/opt/homebrew/lib CV_GENERATOR_DIR=~/Projects/renaud-marketplace/plugins/cv-generator uv run --with weasyprint python3 plugins/cv-generator/scripts/generate_cv.py --profile p1 --company-type t5 --lang en && echo "OK"`
- **VALIDATE retro-compat**: `DYLD_LIBRARY_PATH=/opt/homebrew/lib CV_GENERATOR_DIR=~/Projects/renaud-marketplace/plugins/cv-generator uv run --with weasyprint python3 plugins/cv-generator/scripts/generate_cv.py --positioning cto && echo "OK retro"`

---

### TASK 4 — CREATE `plugins/cv-generator/scripts/batch_validate.py`

Generate all 30 CVs and verify 1-page constraint:

```python
#!/usr/bin/env python3
"""Batch validation: generate all 30 CVs (15 cells × FR+EN), assert 1-page A4."""
import subprocess, sys, pathlib, tempfile, os

VALID_CELLS = [
    ('p1','t1'),('p1','t2'),('p1','t3'),('p1','t4'),('p1','t5'),
    ('p2','t1'),('p2','t3'),('p2','t4'),('p2','t5'),
    ('p3','t1'),('p3','t5'),
    ('p4','t1'),('p4','t5'),
    ('p5','t3'),('p5','t5'),
]
LANGS = ['en', 'fr']
GENERATOR = pathlib.Path(__file__).parent / 'generate_cv.py'

def check_page_count(pdf_path):
    """Return page count using pikepdf."""
    import pikepdf
    with pikepdf.open(pdf_path) as pdf:
        return len(pdf.pages)

def main():
    out_dir = pathlib.Path(tempfile.mkdtemp(prefix='cv_batch_'))
    errors = []
    total = 0

    for (profile, ctype) in VALID_CELLS:
        for lang in LANGS:
            total += 1
            fname = f"CV_Renaud_Laborbe_{profile.upper()}_{ctype.upper()}_{lang.upper()}.pdf"
            out_path = out_dir / fname
            env = os.environ.copy()
            env['DYLD_LIBRARY_PATH'] = '/opt/homebrew/lib'  # WeasyPrint/Pango on macOS
            result = subprocess.run([
                'python3', str(GENERATOR),
                '--profile', profile, '--company-type', ctype, '--lang', lang,
                '--output', fname, '--output-dir', str(out_dir)
            ], capture_output=True, text=True, env=env)

            if result.returncode != 0:
                errors.append(f"FAIL generation {profile}×{ctype}/{lang}: {result.stderr}")
                continue

            if not out_path.exists():
                errors.append(f"FAIL missing output {fname}")
                continue

            pages = check_page_count(out_path)
            if pages != 1:
                errors.append(f"FAIL {fname}: {pages} pages (expected 1)")
            else:
                print(f"  OK  {fname} ({pages}p)")

    print(f"\n{'='*50}")
    print(f"Total: {total} CVs — {total - len(errors)} OK, {len(errors)} errors")
    if errors:
        print("\nERRORS:")
        for e in errors: print(f"  {e}")
        sys.exit(1)
    else:
        print("All 30 CVs validated — 1 page each.")

if __name__ == '__main__':
    main()
```

- **VALIDATE**: `DYLD_LIBRARY_PATH=/opt/homebrew/lib CV_GENERATOR_DIR=~/Projects/renaud-marketplace/plugins/cv-generator uv run --with weasyprint --with pikepdf python3 plugins/cv-generator/scripts/batch_validate.py`

---

### TASK 5 — REWRITE `plugins/cv-generator/skills/cv-generator/SKILL.md`

Full rewrite of the stub. Structure:

```markdown
---
name: cv-generator
description: >
  Generate a personalized 1-page PDF CV for Renaud Laborbe. Use when the user pastes
  a job offer, describes a target role, or asks to generate/update a CV. Selects the
  right positioning from a 5-profile × 5-company-type matrix (15 cells, FR + EN).
version: 0.1.0
allowed-tools: "Bash(uv *) Bash(python3 *) Read Write"
---
```

**Body content** (include all of the following):

1. **Profile × company type matrix** — full lookup table (show which cells are valid) so Claude can detect the right cell from a job offer
2. **Detection logic** — how to map a job offer to (profile, company_type):
   - Profile trigger words / signals
   - Company type classification signals
   - Fallback: default to `p1 × t4` if ambiguous
3. **Language detection** — if job offer is in French → `--lang fr`, else `--lang en`
4. **PLUGIN_DIR resolver** — EXACT code from task brief §6.6 (copy verbatim):
   ```bash
   PLUGIN_DIR=$(python3 - <<'PYEOF'
   import json, os, pathlib, sys, glob as _glob
   home = pathlib.Path.home()
   env = os.environ.get('CV_GENERATOR_DIR', '')
   if env and pathlib.Path(env, 'scripts', 'generate_cv.py').exists():
       print(env); sys.exit(0)
   cache_root = home / '.claude' / 'plugins' / 'cache' / 'renaud-marketplace' / 'cv-generator'
   if cache_root.exists():
       candidates = sorted(cache_root.glob('*/scripts/generate_cv.py'), key=lambda p: p.stat().st_mtime, reverse=True)
       if candidates:
           print(str(candidates[0].parent.parent)); sys.exit(0)
   for pat in ['/sessions/*/mnt/.remote-plugins/*/scripts/generate_cv.py']:
       matches = sorted(_glob.glob(pat), key=os.path.getmtime, reverse=True)
       if matches:
           print(os.path.dirname(os.path.dirname(matches[0]))); sys.exit(0)
   dev = home / 'Projects' / 'renaud-marketplace' / 'plugins' / 'cv-generator'
   if dev.joinpath('scripts', 'generate_cv.py').exists():
       print(str(dev)); sys.exit(0)
   print('PLUGIN_DIR_NOT_FOUND')
   PYEOF
   )
   if [ "$PLUGIN_DIR" = "PLUGIN_DIR_NOT_FOUND" ]; then
     echo "ERROR: cv-generator plugin not found."
     exit 1
   fi
   ```
5. **Generation call**:
   ```bash
   DYLD_LIBRARY_PATH=/opt/homebrew/lib \
   uv run --with weasyprint python3 "$PLUGIN_DIR/scripts/generate_cv.py" \
     --profile {profile} --company-type {company_type} --lang {lang}
   ```
6. **Output handling** — tell Claude to report the PDF path and a 1-sentence positioning summary
7. **Profile detection table** — quick reference:

| Profile | Key signals |
|---------|-------------|
| P1 Architect | "architect", "solution architect", "technical lead" (client-facing), "GenAI deployment" |
| P2 Lead/Manager | "AI lead", "head of AI", "practice lead", "manager", "team lead" |
| P3 CTO | "CTO", "Chief Technology Officer", "technical co-founder" |
| P4 CS/FDE | "customer success", "forward deployed", "solutions engineer", "SE", "FDE" |
| P5 Sales | "account executive", "AE", "business development", "BDM", "sales" |

| Company type | Key signals |
|-------------|-------------|
| T1 Industrial Startup | startup, deeptech, series A/B, scale-up, industriel early-stage |
| T2 Engineering/BET | bureau d'études, ingénierie, BET, engineering consultancy, Egis, Artelia |
| T3 ESN/Consulting | ESN, conseil, consulting, SSII, Médiane, Skapa, ILLUIN |
| T4 Large Energy/Industry | TotalEnergies, grand groupe, EDF, Thales, Technip, groupe industriel |
| T5 AI SaaS/Lab | éditeur SaaS IA, labo IA, Anthropic, Mistral, iAdvize, Dust, OpenAI |

- **VALIDATE**: Manually read the SKILL.md and verify the resolver block is verbatim, the matrix table is complete (15 cells), and the generation call is correct.

---

### TASK 6 — CREATE profile files (`plugins/cv-generator/profiles/`)

Create 5 files. Each should contain: definition, valid cells, narrative rules (incl. solopreneur neutralization), example real companies. Source: task brief sections P1–P5.

**`p1_architecte.md`**: AI Solutions Architect / Solution Architect — 5 cells (T1–T5). Key rule: never hide technical depth; Blue Green leads with architectures delivered. ~30 lines.

**`p2_lead_manager.md`**: AI Lead/Manager — 4 cells (T1,T3,T4,T5). Key rule: Open Ocean team of 12 is the management proof; Blue Green shows technical currency.

**`p3_cto.md`**: CTO — 2 cells only (T1, T5). Key rule: Open Ocean is THE proof; do not use for BET/ESN/grand groupe.

**`p4_cs_fde.md`**: Customer Success / Forward Deployed Engineer — 2 cells (T1, T5). Key rule: deployment history (DCNS, SBM, EnBW) is the credibility anchor.

**`p5_sales_bizdev.md`**: Sales / BizDev — 2 cells (T3, T5). Key rule: P5×T5 → open on Artelia (+15% YOY) and Open Ocean (8 yrs B2B), Blue Green LAST; never lead on Blue Green or founder for T5.

- **VALIDATE**: `ls plugins/cv-generator/profiles/ | wc -l` should return `5`

---

### TASK 7 — RUN BATCH VALIDATION + FIX OVERFLOWS

This is the integration test. Run batch_validate.py and fix any PDF that exceeds 1 page.

**Most likely overflow causes**:
- Bullets too long → shorten to max ~120 chars each
- Competency items with long text → truncate / abbreviate
- About lines too verbose → trim

**Process**:
1. Run batch validator
2. For each failing cell: inspect the generated HTML in `.cv_temp/` (add `--keep-temp` flag or add a debug mode)
3. Identify which section overflows (usually competencies or experience bullets)
4. Shorten the relevant content in `cv-master.json`
5. Re-run until all 30 pass

**Priority test cases** (from PRD):
- `p3 × t1 / en` — Relief CV (highest score 92)
- `p4 × t5 / en` — Dust CV (🔥 active pipeline)
- `p5 × t3 / en` — ILLUIN AE CV (🔥 active pipeline, step 2/4)
- `p1 × t3 / en` — ILLUIN Lead Architect
- `p4 × t1 / en` — Oplit FDE

- **VALIDATE**: `DYLD_LIBRARY_PATH=/opt/homebrew/lib CV_GENERATOR_DIR=~/Projects/renaud-marketplace/plugins/cv-generator uv run --with weasyprint --with pikepdf python3 plugins/cv-generator/scripts/batch_validate.py` → exit code 0, all 30 CVs pass

---

### TASK 8 — VERIFY RETRO-COMPAT + COPY PHOTO

- **COPY** `~/Projects/MyClaudeSkills/cv-generator/assets/photo.jpeg` to `plugins/cv-generator/assets/photo.jpeg` (file is gitignored, must be present locally)
- **VERIFY** retro-compat: `uv run --with weasyprint python3 plugins/cv-generator/scripts/generate_cv.py --positioning ai_consulting` produces `CV_Renaud_Laborbe_ai_consulting.pdf`
- **VERIFY** `plugins/cv-generator/.claude-plugin/plugin.json` version = `0.1.0` = `.claude-plugin/marketplace.json` version for `cv-generator`
- **VALIDATE**: `python3 -c "import json; p=json.load(open('.claude-plugin/marketplace.json')); m=json.load(open('plugins/cv-generator/.claude-plugin/plugin.json')); assert p['plugins'][0]['version'] == m['version'], 'VERSION MISMATCH'; print('versions OK')"`

---

## TESTING STRATEGY

### Unit Tests (manual, no test framework required)

The validation commands for each task serve as unit tests. The critical integration test is the batch validator.

### Priority Manual Tests (run before batch)

Run these 5 first to catch structural issues early:
```bash
BASE="CV_GENERATOR_DIR=~/Projects/renaud-marketplace/plugins/cv-generator"
CMD="uv run --with weasyprint python3 plugins/cv-generator/scripts/generate_cv.py"

eval "$BASE $CMD --profile p3 --company-type t1 --lang en"  # Relief
eval "$BASE $CMD --profile p4 --company-type t5 --lang en"  # Dust
eval "$BASE $CMD --profile p5 --company-type t3 --lang en"  # ILLUIN AE
eval "$BASE $CMD --profile p1 --company-type t3 --lang en"  # ILLUIN Arch
eval "$BASE $CMD --profile p4 --company-type t1 --lang en"  # Oplit
```

### Edge Cases to test

- Invalid cell (e.g., `p3 × t2`) → must raise clear `ValueError` with valid cells list
- `--positioning ai_consulting` → generates `CV_Renaud_Laborbe_ai_consulting.pdf` (retro-compat filename)
- Missing photo → must print WARNING and continue (not crash)
- `--lang fr` → title and about text are in French

---

## VALIDATION COMMANDS

### Level 1: Data integrity

```bash
# 15 cells in matrix
python3 -c "
import json
d = json.load(open('plugins/cv-generator/data/cv-master.json'))
cells = [(p,c) for p,cs in d['matrix'].items() for c in cs]
print(f'{len(cells)} cells: {cells}')
assert len(cells) == 15
"

# 5 new competency items exist
python3 -c "
import json
d = json.load(open('plugins/cv-generator/data/cv-master.json'))
pool = d['competencies_pool']
new_items = ['Document Intelligence & Reporting','AI Evals & Observability','Solution Scoping & Proposals','AI Awareness Training','Customer Onboarding & Adoption']
ai_biz = pool['ai_digital'] + pool['business_leadership']
missing = [i for i in new_items if i not in ai_biz]
print('Missing new items:' if missing else 'All 5 new items found')
if missing: print(missing)
"

# Version consistency
python3 -c "
import json
p = json.load(open('.claude-plugin/marketplace.json'))
m = json.load(open('plugins/cv-generator/.claude-plugin/plugin.json'))
assert p['plugins'][0]['version'] == m['version']
print('Versions consistent:', m['version'])
"
```

### Level 2: Single CV generation (5 priority cases)

```bash
export CV_GENERATOR_DIR=~/Projects/renaud-marketplace/plugins/cv-generator
export DYLD_LIBRARY_PATH=/opt/homebrew/lib  # required — WeasyPrint/Pango on macOS

uv run --with weasyprint python3 plugins/cv-generator/scripts/generate_cv.py \
  --profile p3 --company-type t1 --lang en && echo "Relief OK"

uv run --with weasyprint python3 plugins/cv-generator/scripts/generate_cv.py \
  --profile p4 --company-type t5 --lang en && echo "Dust OK"

uv run --with weasyprint python3 plugins/cv-generator/scripts/generate_cv.py \
  --profile p5 --company-type t3 --lang en && echo "ILLUIN AE OK"

# Retro-compat
uv run --with weasyprint python3 plugins/cv-generator/scripts/generate_cv.py \
  --positioning ai_consulting && echo "Retro-compat OK"
```

### Level 3: Full batch validation

```bash
export CV_GENERATOR_DIR=~/Projects/renaud-marketplace/plugins/cv-generator
export DYLD_LIBRARY_PATH=/opt/homebrew/lib  # required — WeasyPrint/Pango on macOS

uv run --with weasyprint --with pikepdf \
  python3 plugins/cv-generator/scripts/batch_validate.py
# Expected: "All 30 CVs validated — 1 page each."
```

### Level 4: Manual visual review

Open 3–5 PDFs and verify:
- Photo renders (circular, top-left of header)
- Title is visible and in the right language
- Competency container titles are dynamic (cell-specific, not "AI & Digital")
- No emoji characters visible (should be text or nothing)
- Content fits 1 page A4 — no text cut off

---

## ACCEPTANCE CRITERIA

- [ ] All 30 CVs generate without error (15 cells × FR + EN)
- [ ] All 30 CVs are exactly 1 page A4 (pikepdf assertion passes)
- [ ] `--profile p1 --company-type t5 --lang en` produces correct Applied AI Architect CV
- [ ] `--positioning ai_consulting` still works (retro-compat)
- [ ] `plugin.json` version === `marketplace.json` cv-generator version
- [ ] No emoji in template (WeasyPrint-compatible)
- [ ] Competency container titles are dynamic per matrix cell (not hardcoded)
- [ ] Corporate-first experience order for P1×T4, P2×T4, P5×T5 cells
- [ ] `PLUGIN_DIR` resolver works: env var → cache → cowork → dev path
- [ ] Profile files exist: `profiles/p1_architecte.md` through `profiles/p5_sales_bizdev.md`
- [ ] Priority cases look correct visually: Relief, Dust, ILLUIN AE, ILLUIN Arch, Oplit
- [ ] No `pip install` anywhere in the codebase — only `uv run --with`

---

## COMPLETION CHECKLIST

- [ ] Task 1 complete: template migrated, emoji fixed, 3 title placeholders added
- [ ] Task 2 complete: cv-master.json with 15 cells + 5 new competency items
- [ ] Task 3 complete: generate_cv.py with new API + retro-compat + corporate-first
- [ ] Task 4 complete: batch_validate.py
- [ ] Task 5 complete: SKILL.md fully rewritten with resolver + detection logic
- [ ] Task 6 complete: 5 profile files
- [ ] Task 7 complete: batch validation passes (30/30 OK)
- [ ] Task 8 complete: photo copied, retro-compat verified, versions consistent
- [ ] All acceptance criteria checked

---

## NOTES

### Why corporate_first matters

Cells P1×T4, P2×T4, P5×T5 are the ones where Renaud lost applications explicitly due to the "solopreneur" perception (Anthropic, iAdvize, ASN Marine Bidder). For these cells, the experience order is Artelia → Blue Green → Open Ocean — the hiring manager reads Artelia (big international group, P&L, London) first, not Blue Green (which reads as independent consulting if seen first).

### Container title placeholders — new in this version

The legacy template has hardcoded container titles ("AI & Digital", "Business & Leadership", "Sector Expertise"). The matrix version needs dynamic titles per cell (e.g., P1×T1 uses "AI Product Architecture / 0→1 Execution / Industrial & Energy Data"). This requires adding `{{COMP_AI_TITLE}}`, `{{COMP_BUSINESS_TITLE}}`, `{{COMP_SECTOR_TITLE}}` to the template and populating them from the matrix data.

### Emoji vs WeasyPrint

WeasyPrint's emoji rendering depends on system fonts. To avoid fragile behavior in Cowork (where font stacks differ), the plan removes emoji icons from the template entirely. The about and contact sections still use flex layout — the visual gap is preserved, just without icon glyphs.

### One-page overflow debugging

If a cell produces 2-page output, the usual culprits (in order):
1. About lines > ~120 chars each
2. Competency items with long text (> 35 chars)
3. Experience bullets > ~150 chars each
4. 4 bullets per job instead of 3 (prefer 3 bullets per job for most cells)

### Confidence score

**9/10** — environment verified (WeasyPrint + pikepdf confirmed working, 1-page A4 baseline proven). Architecture is additive. All experience bullets are pre-written in this plan. Matrix content (about + containers) is fully documented in the task brief. The DYLD_LIBRARY_PATH gotcha has been identified and added to every command. Remaining 1 point: 1-page overflow is a runtime property only measurable after generation — some cells may need bullet trimming. Task 7 documents the fix process.
