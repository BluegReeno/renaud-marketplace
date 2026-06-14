---
name: cv-generator
description: >
  Generate a personalized 1-page PDF CV for Renaud Laborbe. Use when the user pastes
  a job offer, describes a target role, or asks to generate/update a CV. Selects the
  right positioning from a 5-profile × 5-company-type matrix (15 cells, FR + EN).
version: 0.2.2
allowed-tools: "Bash(uv *) Bash(python3 *) Read Write"
---

# CV Generator — Skill Instructions

## What this skill does

Generate a 1-page A4 PDF CV for Renaud Laborbe. It selects the right profile × company-type cell from a 15-cell matrix, in the right language, and produces a PDF using WeasyPrint.

---

## Step 0 — Check if a job offer is present

**Is there a concrete job offer or a described target role?**

- **YES** → proceed to Step 1 (automatic detection from the offer)
- **NO** (spontaneous application, "generic CV", no offer pasted) → **ask two questions before generating**:

> "Quel type de poste vises-tu pour cette candidature spontanée ?"
>
> | # | Profil | Quand le choisir |
> |---|--------|------------------|
> | 1 | **Architecte / Expert technique** (P1) | Avant-vente, déploiement, cadrage technique |
> | 2 | **Lead / Manager IA** (P2) | Encadrement d'équipe, pilotage practice |
> | 3 | **CTO** (P3) | Direction technique, co-fondateur |
> | 4 | **Customer Success / FDE** (P4) | Déploiement chez le client, onboarding |
> | 5 | **Sales / BizDev** (P5) | Vente de solutions, AE |
>
> "Et quel type d'entreprise cibles-tu ?"
>
> | # | Type | Exemples |
> |---|------|---------|
> | 1 | **Startup industrielle** (T1) | deeptech, scale-up, énergie |
> | 2 | **Bureau d'études / BET** (T2) | Artelia, Egis, Natural Power |
> | 3 | **ESN / Cabinet de conseil** (T3) | SSII, consulting, ILLUIN |
> | 4 | **Grand groupe énergie/industrie** (T4) | TotalEnergies, EDF, Thales |
> | 5 | **Éditeur SaaS IA / Labo IA** (T5) | Anthropic, Mistral, Dust |

Once Renaud answers, proceed with the chosen profile × company type. Do NOT default silently — always ask when there is no job offer.

---

## Step 1 — Detect profile and company type from the job offer

### Profile detection table

| Profile | Key signals in the job offer |
|---------|------------------------------|
| **P1** `p1` — AI Architect / Solution Architect | "architect", "solution architect", "applied AI", "technical lead" (client-facing), "GenAI deployment", "pre-sales architect" |
| **P2** `p2` — AI Lead / Manager | "AI lead", "head of AI", "practice lead", "manager", "team lead", "responsable IA" |
| **P3** `p3` — CTO | "CTO", "Chief Technology Officer", "technical co-founder", "VP Engineering" |
| **P4** `p4` — Customer Success / FDE | "customer success", "forward deployed engineer", "solutions engineer", "SE", "FDE", "customer onboarding" |
| **P5** `p5` — Sales / BizDev | "account executive", "AE", "business development", "BDM", "sales", "commercial" |

Default if ambiguous: **P1 × T4** (`--profile p1 --company-type t4`)

### Company type detection table

| Company type | Key signals |
|-------------|-------------|
| **T1** `t1` — Industrial Startup / Deeptech | startup, deeptech, series A/B, scale-up industrielle, early-stage, "built from scratch" |
| **T2** `t2` — Engineering / BET | bureau d'études, BET, ingénierie, engineering consultancy, Egis, EP2C, Natural Power, Artelia-like |
| **T3** `t3` — ESN / Consulting | ESN, conseil, consulting, SSII, Médiane, Skapa, ILLUIN, cabinet de conseil |
| **T4** `t4` — Large Energy / Industry Group | TotalEnergies, grand groupe, EDF, Thales, Technip, groupe industriel, corporate |
| **T5** `t5` — AI SaaS / AI Lab | éditeur SaaS IA, labo IA, Anthropic, Mistral, iAdvize, Dust, OpenAI, AI startup with a product |

### Valid cells matrix (15 cells)

| | T1 Startup | T2 BET | T3 ESN/Conseil | T4 Grand groupe | T5 SaaS/Labo |
|--|--|--|--|--|--|
| **P1 Architect** | ✅ p1×t1 | ✅ p1×t2 | ✅ p1×t3 | ✅ p1×t4 | ✅ p1×t5 |
| **P2 Lead/Manager** | ✅ p2×t1 | — | ✅ p2×t3 | ✅ p2×t4 | ✅ p2×t5 |
| **P3 CTO** | ✅ p3×t1 | — | — | — | ✅ p3×t5 |
| **P4 CS/FDE** | ✅ p4×t1 | — | — | — | ✅ p4×t5 |
| **P5 Sales** | — | — | ✅ p5×t3 | — | ✅ p5×t5 |

If the detected combination is not a valid cell (marked —), fall back to the nearest valid cell or ask the user for clarification.

---

## Step 2 — Detect language

- If the job offer is written in French → `--lang fr`
- Otherwise → `--lang en`

---

## Step 3 — Resolve PLUGIN_DIR

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
  echo "ERROR: cv-generator plugin not found. Set CV_GENERATOR_DIR=<path> or install from marketplace."
  exit 1
fi
```

---

## Step 4 — Generate the CV

```bash
DYLD_LIBRARY_PATH=/opt/homebrew/lib \
uv run --with weasyprint python3 "$PLUGIN_DIR/scripts/generate_cv.py" \
  --profile {profile} --company-type {company_type} --lang {lang} \
  --output-dir ~/SynologyDrive-MyAssistant/jobsearch/
```

Replace `{profile}`, `{company_type}`, `{lang}` with the detected values.

> **Photo**: bundled at `assets/photo.jpeg` (already public, committed) and used automatically. If it's ever missing, the script falls back to `~/.claude/assets/photo.jpeg`, and renders without a photo if neither exists.

---

## Step 5 — Report to the user

After generation, report:
1. The path to the generated PDF
2. One sentence summarising the positioning: e.g. "CV généré pour le profil **CTO** (P3) chez une **startup industrielle** (T1) — _CTO — Scaling AI-Powered Solutions for Climate & Industry_"

---

## Full example (single CV generation)

```bash
# Detect: P3 × T1, EN (Relief job offer)
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

DYLD_LIBRARY_PATH=/opt/homebrew/lib \
uv run --with weasyprint python3 "$PLUGIN_DIR/scripts/generate_cv.py" \
  --profile p3 --company-type t1 --lang en \
  --output-dir ~/SynologyDrive-MyAssistant/jobsearch/
```

---

## Retro-compat (legacy --positioning flag)

If the user specifies an old-style positioning:
- `--positioning ai_consulting` → maps to `p1 × t4`, output: `CV_Renaud_Laborbe_ai_consulting.pdf`
- `--positioning cto` → maps to `p3 × t1`
- `--positioning business_dev` → maps to `p5 × t3`

```bash
DYLD_LIBRARY_PATH=/opt/homebrew/lib \
uv run --with weasyprint python3 "$PLUGIN_DIR/scripts/generate_cv.py" \
  --positioning ai_consulting
```

---

## Batch validation (all 30 CVs)

```bash
DYLD_LIBRARY_PATH=/opt/homebrew/lib \
uv run --with weasyprint --with pikepdf \
  python3 "$PLUGIN_DIR/scripts/batch_validate.py"
```

Expected output: `All 30 CVs validated — 1 page each.`

---

## Narrative methodology — what each cell emphasizes

The `cv-master.json` experience bullets are cell-specific. Each cell tells a different story with the same three companies (Blue Green → Artelia → Open Ocean, or Artelia-first for corporate cells).

### Experience order rules

| Cell | Job order | Reason |
|------|-----------|--------|
| P1×T4, P2×T4, P5×T5 | Artelia → BG → OO | Corporate credibility first; "founder" framing is a red flag for large groups |
| All other cells | BG → Artelia → OO | Blue Green as current work, most relevant GenAI signal |

### Signal per company type (T)

**T3 — ESN / Consulting (ILLUIN, Capgemini)**
- Emphasise: delivery management, full project lifecycle (scoping → production handover), client advisory, technical depth proven in client context
- Blue Green: "managed client projects end to end, can lead delivery squads"
- Artelia: "cross-functional delivery teams for enterprise clients"
- Open Ocean: "built 12-person product team, shipped SaaS to industrial clients"

**T4 — Grand groupe / Corporate (TotalEnergies, ASN, EDF)**
- Emphasise: P&L, governance, compliance-ready outputs, C-level stakeholder management, enterprise procurement
- Blue Green: "production-grade, compliance-ready, auditability built-in"
- Artelia: **appears FIRST** — P&L, team, 6000-person group, London base
- Open Ocean: "Naval Group, RTE framework contract" — enterprise client names, not startup story

**T5 — AI Lab / SaaS startup (Anthropic, Mistral, Dust)**
- Emphasise: velocity, LLM-native architecture, team building, fundraising, exit
- Blue Green: "zero to production in under 3 months", "LLM-native (MCP, pgvector, Pydantic AI)"
- Artelia: secondary role — shows corporate-scale credibility
- Open Ocean: strongest card — "12-person team, €2M institutional VCs, acquired by Artelia (2019)"
- **Solopreneur counter**: never hide Open Ocean; it proves team leadership, not solo work

**T1 — Industrial startup / scale-up**
- Emphasise: 0→1 architecture, technical ownership, product roadmap at scale, industrial deployment
- Blue Green: production AI stack details (FastAPI, pgvector, Pydantic AI), product suite (Edifice, WattCast, EnerCast)
- Open Ocean: CTO-who-scaled narrative — prototype → industrial deployment → exit

**T2 — BET / Engineering consultancy**
- Emphasise: industry credibility (15+ years in energy/offshore), technical integration, speaking the engineer's language
- Use default bullets (T2-specific overrides not required; energy domain knowledge is the differentiator)

### Signal per profile (P)

**P1 — AI Architect**: Technical depth + delivery. Never just slides — always a system in production (BWC v2.2).

**P2 — Lead/Manager**: Management proof = Open Ocean (12-person team, 8 years). Blue Green shows technical currency (still ships). For T5: counter solopreneur via OO team story.

**P3 — CTO**: Open Ocean IS the proof (start to exit). Must show current stack is live (BWC v2.2). For T5: velocity + team-building combo. For T1: scaling experience, fundraising, technical maturity.

**P4 — CS/FDE**: "Was the customer before being the FDE" — 15 years on the industrial-client side. Full cycle: discovery → demo → POC → production handover → autonomous use.

**P5 — Sales/BizDev**: Technical enough to run live demos and scope with engineering teams. For T5: builds with the product he sells (uses Claude/Mistral daily in production).

### Factual anchors (never invent — always use these)

| Company | Key verifiable facts |
|---------|---------------------|
| Blue Green — EnBW France | RAG 22,800 chunks, 5 Pydantic AI agents, offshore wind tender analysis |
| Blue Green — Valorem | RAG-based PLU analysis for onshore wind farm siting |
| Blue Green — IC Ingénieurs Conseils | AI-assisted building diagnostics, Aulnay (€25M) + La Ferme du Temple (€35M) |
| Blue Green — WattCast | D+1 MAE 12.42 EUR/MWh, LEAR + XGBoost, EPEX SPOT France |
| Blue Green — BlueWind Companion v2.2 | 91 regulatory docs, 22,800 RAG chunks, 5 agents, Next.js + FastAPI + Supabase pgvector |
| Artelia | P&L confirmed, clients: SBM Offshore, Nexans, Alcatel Submarine Networks (ASN), Cadeler |
| Open Ocean | Team of 12, €2M from Seventure Partners + Cap Décisif/FNA (institutional VCs), acquired by Artelia (2019) |
| Open Ocean clients | Naval Group (ex-DCNS), RTE (framework contract), Doris Engineering |

### Banned phrases (never use these)

- "urban planning automation" → use "PLU analysis for wind farm siting"
- "end-to-end" (FR bullets) → use "bout en bout" or "de A à Z"
- "delivery" (FR bullets) → use "livraison"
- "Business Angels" → use "institutional investors (Seventure Partners, Cap Décisif/FNA)"
- "DCNS" → use "Naval Group (ex-DCNS)"
- "en solo à vélocité maximale" → always counter solopreneur framing
