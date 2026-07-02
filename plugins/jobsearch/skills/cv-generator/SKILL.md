---
name: cv-generator
description: >
  Generate a personalized 1-page PDF CV for Renaud Laborbe. Use when the user pastes
  a job offer, describes a target role, or asks to generate/update a CV. Selects the
  right positioning from a 5-profile × 5-company-type matrix (15 cells, FR + EN).
version: 0.5.3
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

## Step 3b — Personalize bullets to the job offer (LLM step, no script)

> Only applies when a concrete job offer is available. Skip for spontaneous CVs.

After selecting the cell, read the job offer and adapt the pre-written bullets **before** calling `generate_cv.py`:

1. **Identify 2–3 key signals** from the offer — specific tech, sector challenge, company framing (e.g. "prototyper rapidement en environnement réel", "logique ARR", "briques réutilisables")
2. **Rewrite 1–2 bullets per company** to mirror those signals — rephrase emphasis, reorder, surface a relevant factual anchor
3. **Optionally adjust the `about` section** to echo the job's specific framing (keep same infinitive structure)
4. **Optionally adjust container titles** if the cell defaults don't match the role framing (see `--container-titles` in Step 4)
5. **Validate before generating** — every rewritten bullet must: start with an infinitive verb, keep all factual anchors intact, pass the pre-generation checklist

Build the `--bullet-overrides` JSON dict from personalised bullets. Key format: `"{company}.{profile}.{lang}.{index}"`. Companies: `blue_green`, `artelia`, `open_ocean`. Index is 0-based.

Example:
```json
{"blue_green.p4.fr.0": "Analyser les workflows clients et identifier les opportunités d'automatisation IA — 5 agents déployés chez EnBW France, temps de traitement ÷10"}
```

**Rules — never violate:**
- Only rewrite bullets — never invent new facts, metrics, client names, or dates
- Keep all verifiable anchors: client names (EnBW, Valorem, Naval Group, SBM Offshore, RTE), metrics (22 800 chunks, ÷10, +15%), dates, team sizes
- If the offer mentions a specific tech (n8n, LangChain, Pydantic AI), surface it **only if it exists** in the factual anchors — do not add if it doesn't
- Limit: **max 2 bullets changed per company** — don't rewrite everything
- Banned phrases (DCNS, Business Angels, "urban planning automation", etc.) still apply

---

## Step 4 — Generate the CV

```bash
DYLD_LIBRARY_PATH=/opt/homebrew/lib \
uv run --with weasyprint python3 "$PLUGIN_DIR/scripts/generate_cv.py" \
  --profile {profile} --company-type {company_type} --lang {lang} \
  --company "{company_name}" \
  --job-title "{job_title}" \
  --output-dir ~/Library/CloudStorage/SynologyDrive-MyAssistant/jobsearch/
```

Replace `{profile}`, `{company_type}`, `{lang}`, `{company_name}`, `{job_title}` with the detected values. Output filename is auto-built: `CV_Renaud_Laborbe_{job_slug}_{company_slug}_{LANG}.pdf`.

**Optional flags:**

`--container-titles '["Title 1", "Title 2", "Title 3"]'`
Override the 3 competency block titles. Use when cell defaults don't fit the offer framing. The agent can propose better titles if it sees a stronger angle — defaults from cv-master.json are a starting point, not a constraint. P4×T5 defaults: `["Architecture & agents IA", "Cycle client & déploiement", "Secteurs d'expertise"]`.

`--bullet-overrides '{"blue_green.p4.fr.0": "Nouveau bullet..."}'`
Inject personalised bullets without modifying cv-master.json. Built from Step 3b personalization. Key: `"{company}.{profile}.{lang}.{index}"`.

`--about-override '["Line 1", "Line 2", "Line 3"]'`
Override all 3 about lines. Use for killer CVs tailored to a specific company. JSON array of exactly 3 strings. See EN readability rules below before writing.

`--title-override "Applied AI Engineer — Enterprise GenAI Deployment"`
Override the headline title under the candidate name. Use when the job title wording differs significantly from the cell default.

`--data-dir ~/path/to/dir/`
Load cv-master.json from a custom directory (useful if the plugin dir is read-only in Cowork).

> **1-page auto-check**: add `--with pikepdf` to the uv command. The script detects overflow and retries with up to 3 progressively tighter compact CSS levels (gentle → moderate → ultra-compact). If still >1 page after all levels, it warns explicitly — content needs trimming.

> **Cold start**: the first run in a fresh environment downloads WeasyPrint + pikepdf (~20 MB, 10–30 s). Subsequent runs use the UV package cache — steady-state is under 1 s. To pre-warm once per machine:
> ```bash
> uv run --with weasyprint --with pikepdf python3 -c "import weasyprint, pikepdf; print('warm')"
> ```

> **Photo**: bundled at `assets/photo.jpeg` (already public, committed) and used automatically. If it's ever missing, the script falls back to `~/.claude/assets/photo.jpeg`, and renders without a photo if neither exists.

---

## Step 5 — Report to the user

After generation, report:
1. The path to the generated PDF
2. One sentence with a **human-readable cell label** — no P/T codes in the output. Use the `label` field from `cv-master.json matrix` for the selected cell:

**Cell labels (FR → EN):**

| Cell | Label FR | Label EN |
|------|----------|---------|
| P1×T1 | Architecte IA — startup industrielle deeptech | AI Architect — Industrial Deeptech Startup |
| P1×T2 | Architecte IA — bureau d'études / ingénierie | AI Architect — Engineering Consultancy / BET |
| P1×T3 | Architecte IA — ESN / cabinet de conseil | AI Architect — Consulting Firm |
| P1×T4 | Architecte IA — grand groupe industriel | AI Architect — Large Industrial Group |
| P1×T5 | Architecte IA — éditeur SaaS IA | AI Architect — AI SaaS / Lab |
| P2×T1 | Lead IA — startup industrielle | AI Lead — Industrial Startup |
| P2×T3 | Lead IA — ESN / conseil | AI Lead — Consulting Firm |
| P2×T4 | Lead IA — grand groupe | AI Lead — Large Industrial Group |
| P2×T5 | Lead IA — éditeur SaaS IA | AI Lead — AI SaaS / Lab |
| P3×T1 | CTO — startup industrielle | CTO — Industrial Startup |
| P3×T5 | CTO — éditeur SaaS IA | CTO — AI SaaS / Lab |
| P4×T1 | Solutions Engineer — startup industrielle | Forward Deployed Engineer — Industrial Startup |
| P4×T5 | Solutions Engineer — éditeur SaaS IA | Forward Deployed Engineer — AI SaaS / Lab |
| P5×T3 | Business Developer — ESN / conseil | Sales / BizDev — Consulting Firm |
| P5×T5 | Business Developer — éditeur SaaS IA | Sales / BizDev — AI SaaS / Lab |

Example output sentences:
- ✅ "CV généré — **Solutions Engineer — éditeur SaaS IA** (P4×T5 FR) — _Solutions Engineer IA — Déploiement GenAI en environnement industriel_"
- ✅ "CV généré — **CTO — startup industrielle** (P3×T1 EN) — _CTO — Scaling AI-Powered Solutions for Climate & Industry_"

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
  --output-dir ~/Library/CloudStorage/SynologyDrive-MyAssistant/jobsearch/
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

## Editorial rules — CV content checklist

Apply these rules when reviewing or editing any content in `cv-master.json`.

### Person and tense
- **No explicit subject** — never "je", "il", "elle", "vous", "Renaud"
- All roles (current and past) → **infinitive, no subject**: "Déployer", "Construire", "Lever", "Piloter", "Maîtriser"
- ❌ Never past participle: "Déployé", "Construit", "Piloté" — ❌ Never conjugated present: "Conçoit", "Livre", "Pilote"
- No English calques: "parle ingénierie" ❌ → "Maîtriser les contraintes terrain" ✅; "speaks X" → restructure in French

### Bullets — STAR compressed
- Format: `[Strong verb] + [what + precise context] → [measurable or strong qualitative result]`
- Max 4 bullets per role — pick the most impactful
- **Banned verbs**: "participé", "contribué", "impliqué dans", "aidé à", "en charge de", "facilité", "animé", "géré" (without a result)
- Every role must have ≥1 measurable result (% growth, client name, timeline, scale)

### About section (3 bullets max)
1. What you **do** concretely (tech or domain, with tool or sector named)
2. What you **bring** to the client (measurable business value)
3. What **differentiates** you (true for Renaud, false for most candidates)
- No third person, no "passionné", "dynamique", "orienté résultats"

### English about & bullets — readability rules (critical)

**The first reader is HR, not an engineer.** Every sentence must pass the non-specialist test: a smart person with no AI background must understand it immediately.

#### About (EN) — narrative, not a list

| | Rule |
|---|---|
| **Line 1** | What you do — plain English, domain + end-to-end ownership. No acronyms. |
| **Line 2** | What you've built — describe the *problem solved*, not the stack. Avoid unknown company names; describe the sector instead ("offshore wind developers", not "EnBW France"). |
| **Line 3** | Why you're different — the angle no other candidate has. Factual, human, specific. |

❌ **Never in the about:**
- Technical acronyms without explanation (RAG, RRF, LEAR, MAE, pgvector, chunking…)
- Metrics that require domain knowledge ("MAE J+1 = 12.4 €/MWh", "22,812 chunks", "8.65/10 LLM-judged vs expert ground truth")
- Lists disguised as sentences ("Three live deployments: X, Y, Z" → no)
- Unknown company names (EnBW France, IC Ingénieurs Conseils, Weathernews → describe the sector instead)

✅ **Always in the about:**
- Plain-English problems ("turns weeks of document analysis into minutes")
- Self-explanatory results ("scored 8.6/10 against expert-validated ground truth", "€2M raised")
- Well-known client names only if they add credibility (Naval Group, RTE, SBM Offshore → OK)

#### Bullets (EN) — problem → action → readable result

Format: `[Action verb] + [what you built / for whom] — [result in plain English]`

❌ **Never:**
- Unexplained acronyms as the main message ("Hybrid RAG pipeline (pgvector, RRF, chunking…)")
- Metrics without context that a non-specialist can't interpret ("LEAR + XGBoost daily-recalibrated ensemble, MAE J+1 = 12.4 €/MWh")
- Jargon pileups ("5 specialized agents, 22,812 chunks, hybrid semantic+keyword retrieval (RRF)…")

✅ **Always:**
- The business problem in plain English ("reads hundreds of regulatory documents and generates reports in minutes")
- The result stated simply ("live in production, used daily" / "accurate within target threshold" / "+15% ACV")
- Named clients when recognizable (Naval Group, RTE, EnBW France are OK; obscure names → describe sector)

---

### About section — FR style rule (mandatory)
- **Forme nominale uniquement** : phrase complète, sujet implicite, verbe conjugué ou participé passé
- ✅ `"Architecte IA issu du terrain…"` / `"Systèmes GenAI déployés en production…"` / `"15 ans de vente…"`
- ❌ Infinitif nu : `"Livrer de la GenAI…"`, `"Maîtriser le cycle…"`, `"Apporter une verticale…"`
- ❌ Fragment sans verbe : `"Fort de 15 ans…"` sans suite
- ❌ Calque anglais : `"Travailler en trilingue"` → `"Trilingue opérationnel"`
- Chaque bullet = claim complet avec preuve embarquée (chiffre, client nommé, ou différenciateur vérifiable)

### Competency containers
- Items anchored with context or proof — not bare keyword lists
- ✅ "Multi-agents LLM en production (Claude, pgvector, n8n)" not ❌ "LLMs, RAG, Agents IA"

### Pre-generation checklist
- [ ] No "je / il / elle / vous / Renaud" in any text block
- [ ] All FR bullets start with an **infinitive** verb (Déployer / Concevoir / Piloter / Lever / etc.)
- [ ] No past participle starts: "Déployé", "Construit", "Piloté" ❌
- [ ] No conjugated present starts: "Conçoit", "Livre", "Pilote" ❌
- [ ] No bullet starts with a banned/weak verb
- [ ] Every role has ≥1 chiffre ou résultat qualitatif fort
- [ ] Container items have proof/context, not bare keywords
- [ ] "urban planning automation" → "PLU analysis for wind farm siting"
- [ ] "Business Angels" → "institutional investors (Seventure Partners, Cap Décisif/FNA)"
- [ ] "DCNS" → "Naval Group (ex-DCNS)"
- [ ] "delivery" (FR bullets) → "livraison"

---

## Narrative methodology — what each cell emphasizes

The `cv-master.json` experience bullets are cell-specific. Each cell tells a different story with the same three companies.

### Experience order
Always chronological reverse: Blue Green (2023–present) → Artelia (2019–2023) → Open Ocean (2011–2019).
No exceptions.

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
