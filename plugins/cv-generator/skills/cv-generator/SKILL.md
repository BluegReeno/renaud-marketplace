---
name: cv-generator
description: >
  Generate a personalized 1-page PDF CV for Renaud Laborbe. Use when the user pastes
  a job offer, describes a target role, or asks to generate/update a CV. Selects the
  right positioning from a 5-profile × 5-company-type matrix (15 cells, FR + EN).
version: 0.1.1
allowed-tools: "Bash(uv *) Bash(python3 *) Read Write"
---

# CV Generator — Skill Instructions

## What this skill does

Generate a 1-page A4 PDF CV for Renaud Laborbe. It selects the right profile × company-type cell from a 15-cell matrix, in the right language, and produces a PDF using WeasyPrint.

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

> **Photo**: not bundled in the public plugin. The script auto-fallbacks to `~/.claude/assets/photo.jpeg` — place `photo.jpeg` there after install and the photo appears automatically.

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
