---
name: cover-letter
description: >
  Generate a tailored cover letter for Renaud Laborbe. Use when the user pastes a job offer
  and asks for a cover letter / lettre de motivation. Detects profile × company type from
  the offer (same 15-cell matrix as the CV generator) and produces a 3-paragraph letter
  anchored in real, verifiable experience. No boilerplate.
version: 0.1.0
allowed-tools: "Read"
---

# Cover Letter — Skill Instructions

## What this skill does

Generate a 1-page, 3-paragraph cover letter for Renaud Laborbe. Uses the same profile × company-type matrix as the CV generator. The letter is written entirely from real facts — no invented experience, no HR boilerplate.

The output is text (not a PDF). Copy-paste ready.

---

## Step 0 — Check for job offer

Is there a concrete job offer?
- **YES** → proceed to Step 1
- **NO** → ask: "Quel profil et quel type d'entreprise ?" (use the same table as the CV generator)

---

## Step 1 — Detect profile × company type

Use exactly the same detection logic as the CV generator SKILL.md (Step 1).

Also note:
- **Company name** (Anthropic, TotalEnergies, etc.) — use it in the letter body
- **Hiring manager name** if present — use it in the salutation
- **Key 3 requirements** from the offer — weave them into the letter

---

## Step 2 — Detect language

- French offer → write in French
- English offer → write in English
- Never translate — each language has its own register

---

## Step 3 — Load narrative context

Before writing, read the relevant profile file to load narrative rules:

| Profile | File |
|---------|------|
| P1 | `profiles/p1_architecte.md` |
| P2 | `profiles/p2_lead_manager.md` |
| P3 | `profiles/p3_cto.md` |
| P4 | `profiles/p4_cs_fde.md` |
| P5 | `profiles/p5_sales_bizdev.md` |

The file is at `$PLUGIN_DIR/profiles/<profile>.md`. Use the Read tool.

---

## Step 4 — Write the cover letter

### Structure (strict — 3 paragraphs, ~300 words EN / ~330 words FR)

**Para 1 — Hook (50–60 words)**
Open with energy and a concrete signal of fit. Never start with "I am writing to apply for" or "Je me permets de vous adresser ma candidature." Start with the problem, the mission, or a bold statement of relevance.

Good: "Offshore wind AI architecture is the exact intersection where I've been building for the past three years."
Bad: "I am pleased to apply for the position of..."

**Para 2 — Proof (130–150 words)**
2–3 concrete achievements, cell-appropriate, verifiable. Use real metrics from the factual anchors below. Match the job's key requirements.

The proof paragraph follows the cell's narrative logic:
- T3 (ESN): full lifecycle delivery, client advisory, tech leadership
- T4 (Corporate): P&L, governance, enterprise scale, named institutional clients
- T5 (AI Lab): velocity, LLM-native architecture, team + exit story
- T1 (Scale-up): 0→1 build, current tech stack, team management
- For solopreneur risk (T5): mention Open Ocean (12-person team, €2M, Seventure Partners)

**Para 3 — Why them + call to action (70–90 words)**
1 sentence about what draws Renaud to this specific company/mission.
1 sentence about the fit from their perspective (what he brings that others don't).
Close: confident, direct. Not "dans l'attente de votre réponse, veuillez agréer..." — that is forbidden.

Good EN close: "I would be glad to discuss how this maps to your current roadmap."
Good FR close: "Je serais ravi d'en discuter avec vous lors d'un échange."

### Salutation

- If hiring manager name known: "Dear [First name]," (EN) / "Bonjour [Prénom]," (FR)
- If unknown: "Dear Hiring Team," (EN) / "Bonjour," (FR)

### Sign-off

Always: "Renaud Laborbe" — no "Cordialement" or "Sincerely," — just the name.

---

## Factual anchors (always use these — never invent)

| Company | Key verifiable facts to use in letters |
|---------|----------------------------------------|
| Blue Green — EnBW France | RAG 22,800 chunks, 5 Pydantic AI agents, offshore wind tender analysis |
| Blue Green — Valorem | PLU analysis for onshore wind farm siting (RAG-based) |
| Blue Green — IC Ingénieurs Conseils | AI-assisted building diagnostics, Aulnay (€25M) + La Ferme du Temple (€35M) |
| Blue Green — WattCast | D+1 MAE 12.42 EUR/MWh, LEAR + XGBoost ensemble, EPEX SPOT France |
| Blue Green — BlueWind Companion v2.2 | 91 regulatory docs, 22,800 chunks, 5 agents, Next.js + FastAPI + pgvector |
| Artelia | Full P&L (renewables & energy BU, London), +15% YOY, clients: SBM Offshore, Nexans, Alcatel Submarine Networks, Cadeler |
| Open Ocean | Team of 12, €2M from Seventure Partners + Cap Décisif/FNA (institutional VCs), acquired by Artelia (2019), clients: Naval Group (ex-DCNS), RTE, Doris Engineering |

---

## Banned phrases

**French:**
- "Je me permets de vous adresser ma candidature" → banned
- "Dans l'attente de votre réponse, veuillez agréer..." → banned
- "En réponse à votre annonce" → banned
- "delivery", "end-to-end" → use "livraison", "bout en bout"
- "Business Angels" → "investisseurs institutionnels (Seventure Partners, Cap Décisif/FNA)"
- "DCNS" → "Naval Group (ex-DCNS)"
- "automatisation de l'urbanisme" → "analyse PLU pour l'implantation de parcs éoliens"

**English:**
- "I am pleased to apply for" → banned
- "Please find attached my resume" → banned
- "I look forward to hearing from you" → weak; replace with a specific forward-looking statement
- "DCNS" → "Naval Group (ex-DCNS)"
- "urban planning automation" → "PLU analysis for wind farm siting"

---

## Step 5 — Output format

Output the letter directly in the conversation. No preamble. No "Here is your cover letter:".

Start directly with the salutation. End with "Renaud Laborbe".

After the letter, add one line (collapsed / meta):
> _Profile detected: **{profile_label}** × **{company_type_label}** · Language: **{lang}**_

---

## Full example

**Input**: Anthropic Partnership AE job offer (English)

**Detection**: P5 × T5, EN
**Profile rules**: Load `p5_sales_bizdev.md` → Artelia-first order, technical fluency emphasis

**Letter**:

---

Dear Recruiting Team,

Building with frontier models while selling them is a rare combination — I've been doing exactly that for the past two years. BlueWind Companion v2.2, the AI platform I built for offshore wind developers, runs on Claude multi-agent pipelines in production. I'm not applying to Anthropic because I know the API. I'm applying because I've been the user you're trying to reach.

At Artelia (6,000-person engineering group, London), I carried a quota and grew the offshore wind portfolio 15% YOY through C-level negotiations and long-term framework contracts with SBM Offshore, Nexans, and Cadeler. Before that, I ran 100% of commercial cycles at Open Ocean — the marine data SaaS I co-founded with a 12-person team, raised €2M from Seventure Partners and Cap Décisif, and sold to Artelia in 2019. At Blue Green, I've delivered GenAI systems to EnBW France (22,800-chunk RAG, 5 AI agents) and Valorem (PLU analysis for wind farm siting) — both clients I sourced, scoped, and closed myself. For energy and industrial buyers, I've been on both sides of the table.

Anthropic's enterprise push into the energy vertical is the exact space where my network and production credibility overlap. I would be glad to discuss how that maps to your current pipeline.

Renaud Laborbe

---

_Profile detected: **P5 — Sales/BizDev** × **T5 — AI SaaS/Lab** · Language: **EN**_
