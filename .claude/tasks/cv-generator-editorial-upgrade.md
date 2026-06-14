# Task — cv-generator Editorial Upgrade (v0.3.0)

**Status**: ✅ complete — 2026-06-14  
**Plugin**: `plugins/jobsearch` (cv-generator skill)  
**Approach**: validate on P4 first → roll out to all cells

## Tasks

### Phase 1 — P4 validation
- [x] Fix SKILL.md editorial rules (infinitive, remove participe passé / présent conjugué) ✓ 2026-06-14
- [x] Add Step 3b (LLM personalization) to SKILL.md ✓ 2026-06-14
- [x] Update Step 5 with cell labels ✓ 2026-06-14
- [x] Rewrite P4×T1 about.fr to infinitive (3 lines) ✓ 2026-06-14
- [x] Rewrite P4×T5 about.fr to infinitive (3 lines) ✓ 2026-06-14
- [x] Rewrite BG P4 default.fr bullets to infinitive (3 lines) ✓ 2026-06-14
- [x] Rewrite Artelia P4 default.fr bullets to infinitive (3 lines) ✓ 2026-06-14
- [x] Rewrite Open Ocean P4 default.fr bullets to infinitive (3 lines) ✓ 2026-06-14
- [x] Add `label.fr` + `label.en` to all 15 matrix cells ✓ 2026-06-14

### Phase 2 — Roll out to all cells
- [x] Rewrite all BG FR bullets (P1/P2/P3/P5) to infinitive ✓ 2026-06-14
- [x] Rewrite all Artelia FR bullets (P1/P2/P3/P5) to infinitive ✓ 2026-06-14
- [x] Rewrite all Open Ocean FR bullets (P1/P2/P3/P5) to infinitive ✓ 2026-06-14
- [x] Rewrite all about.fr for 13 remaining cells (P1×T1-T5, P2×T1/T3/T4/T5, P3×T1/T5, P5×T3/T5) to infinitive ✓ 2026-06-14

### Finalization
- [x] Bump version to 0.3.0 / 0.5.0 (4-file sync) ✓ 2026-06-14
- [x] Generate P4×T5 FR PDF and validate 1 page ✓ 2026-06-14
- [x] Batch validate 30/30 CVs — ALL OK ✓ 2026-06-14

## Completion
- **Started**: 2026-06-14
- **Completed**: 2026-06-14

---

## Context & problem

The current `cv-master.json` FR bullets use **past participle** ("Déployé", "Construit") and **present tense** ("Conçoit", "Pilote") — both are wrong for French CVs.

Research from authoritative French sources (CV Creator, JobImpact, TopCV, Zety) confirms:

> **French CVs use the infinitive exclusively** — no "je", no past tense, no present conjugation.

### Research evidence

Sources: [cv-creator.fr](https://www.cv-creator.fr/blog/verbes-action-cv), [jobimpact.fr](https://jobimpact.fr/verbes-action-cv), [topcv.fr](https://topcv.fr/conseils-emploi/mots-d-action-cv), [zety.com/fr-ca](https://zety.com/fr-ca/blog/verbes-action-cv)

**What they say:**
- "Utilisez un verbe d'action **à l'infinitif** — c'est la forme qui crée un ton direct et professionnel et évite la répétition de 'je'."
- "L'infinitif est la forme du verbe sans indication de personne ni de temps — c'est précisément ce qui le rend approprié pour un CV."

**Correct examples (from sources):**
```
✅ Coordonner les tâches d'une équipe multidisciplinaire
✅ Accroître les ventes de 15 % grâce à de nouvelles stratégies marketing
✅ Rédiger les rapports financiers mensuels
✅ Optimiser les processus de gestion des stocks
```

**Wrong (what we currently have):**
```
❌ Déployé des solutions IA chez EnBW... (participe passé)
❌ Conçoit et déploie des systèmes IA... (présent conjugué)
❌ Piloté un portefeuille clients... (participe passé)
```

**Correct format for cv-master.json FR bullets:**
```
✅ Déployer 5 agents IA chez EnBW France (22 800 documents) — temps d'analyse divisé par 10
✅ Concevoir et intégrer un système RAG pour l'analyse de PLU chez Valorem
✅ Former les équipes clients jusqu'à l'usage autonome en production
```

Same rule applies to the **about** section:
```
✅ Concevoir et déployer des agents IA documentaires en production pour des clients industriels
✅ Piloter le cycle client complet : qualification des besoins, POC, intégration, formation
✅ Maîtriser les contraintes terrain : 15 ans côté industriel en énergie offshore et ingénierie
```

---

## Two development tracks

### Track A — Fix FR verb convention (infinitive throughout)

Rewrite all FR bullets in `cv-master.json` to use infinitive.  
Scope: `blue_green`, `artelia`, `open_ocean`, `earlier` × all profiles (P1–P5) × all cells.  
Also rewrite `about.fr` for all matrix cells.

### Track B — LLM-powered personalization step

Currently the skill only picks a pre-written cell. It does not adapt content to the specific job offer.

Add a **Step 3b** in SKILL.md between cell selection and PDF generation:

> After selecting the cell, the LLM reads the job offer and:
> 1. Identifies 2–3 key signals from the offer (specific tech, sector, company challenge)
> 2. Rewrites 1–2 bullets per company experience to mirror those signals — keeping factual anchors intact
> 3. Optionally adjusts the `about` section to echo the job's specific framing
> 4. Validates against editorial rules (infinitive, no calques, result present) before generating

**Rules for personalization:**
- Only rewrite bullets — never invent new facts
- Keep all verifiable anchors: client names, metrics, dates, team sizes
- Banned phrases and factual anchors from SKILL.md `## Factual anchors` section still apply
- If the offer mentions a specific tech (e.g., "n8n", "LangChain"), surface it from factual anchors if it exists; do not add if it doesn't
- Limit: max 2 bullets changed per company (don't rewrite everything)

---

## Phase 1 — Validate on P4 × "Solutions Engineer SaaS IA"

### Step 1 — New profile naming convention

Replace P/T codes with human-readable cell labels in SKILL.md and in the output.

Define one label per active cell (15 cells). Label format:
`[Role title] — [Company type description]`

Examples:
| Code | Label FR | Label EN |
|------|----------|---------|
| P1×T1 | Architecte IA — startup industrielle deeptech | AI Architect — Industrial Deeptech Startup |
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

These labels go:
1. In SKILL.md Step 1 detection table (replace "P4" etc. with the label)
2. In SKILL.md Step 5 output (the sentence shown to the user)
3. In the `matrix` section of `cv-master.json` as a new `label` field per cell

### Step 2 — Rewrite P4 bullets (FR) to infinitive

Rewrite all P4 FR bullets to use infinitive. Target content:

**Blue Green — P4 FR:**
```
Déployer 5 agents IA chez EnBW France (22 800 documents, analyse AO offshore) — temps d'analyse divisé par 10
Concevoir et intégrer un système RAG pour l'analyse de PLU chez Valorem — de la qualification du besoin à la mise en production
Former les équipes clients jusqu'à l'usage autonome en production (EnBW France, Valorem)
```

**Artelia — P4 FR:**
```
Déployer des services de données éolien offshore auprès de grands développeurs européens (SBM Offshore, Naval Group, RTE)
Développer un portefeuille clients en croissance de +15 % par an — de la qualification à l'adoption
Coordonner les équipes pluridisciplinaires (ingénierie + ops) pour tenir les engagements clients sur projets offshore
```

**Open Ocean — P4 FR:**
```
Déployer le SaaS de données marines chez des clients industriels majeurs (Naval Group, SBM Offshore, RTE)
Porter 100 % du cycle client : qualification, proposition, intégration, adoption
Lever €2M — exit réussi par acquisition par Artelia (2019)
```

**P4×T5 about FR:**
```
Concevoir et déployer des agents IA documentaires en production pour des clients industriels (RAG, orchestration multi-agents).
Piloter le cycle client complet : qualification des besoins, POC, intégration SI, formation et mise en production.
Maîtriser les contraintes terrain : 15 ans côté industriel en énergie offshore et ingénierie.
```

**P4×T1 about FR:**
```
Déployer des solutions techniques chez des industriels depuis 15 ans (énergie, offshore, ingénierie).
Intégrer des solutions IA en environnement contraint : RAG, agents, automatisation de workflows.
Maîtriser les contraintes terrain et les systèmes industriels — pas seulement le logiciel.
```

### Step 3 — Test personalization on the Yotta offer

Job offer: Forward Deployed Engineer at a groupe international building AI SaaS (Paris)  
Cell selected: P4×T5 FR

After selecting the cell, the LLM should:
- Notice the offer emphasizes "prototyper rapidement en environnement réel", "workflows", "logique ARR", "briques réutilisables"
- Adapt 1–2 BG bullets to surface: rapid prototyping + scalability angle
- Keep EnBW/Valorem client names and the ÷10 metric intact

### Step 4 — Generate and validate

Regenerate `CV_Renaud_Laborbe_P4_T5_FR.pdf`  
Check: 1 page, infinitive verbs, no calques, result present in each bullet, profile label shows "Solutions Engineer — éditeur SaaS IA"

---

## Phase 2 — Roll out to all cells (after P4 validated)

1. Rewrite all FR bullets for P1–P5 × all companies to infinitive
2. Rewrite all `about.fr` for all 15 cells to infinitive
3. Add `label.fr` and `label.en` fields to all 15 matrix cells
4. Update SKILL.md Step 1 detection table with labels
5. Bump version: `0.2.x` → `0.3.0` (minor — new behavior)
6. Batch validate: 30/30 CVs, 1 page each

---

## Files to modify

| File | Change |
|------|--------|
| `plugins/jobsearch/data/cv-master.json` | All FR bullets → infinitive; add `label` per cell |
| `plugins/jobsearch/skills/cv-generator/SKILL.md` | Step 1 labels; Step 3b personalization; Step 5 label output; editorial rules update |
| `plugins/jobsearch/.claude-plugin/plugin.json` | Bump to 0.3.0 |
| `.claude-plugin/marketplace.json` | Sync top-level + jobsearch entry |

---

## Success criteria

- [ ] P4×T5 FR: all bullets at infinitive, no past participle, no conjugated verb
- [ ] P4×T5 FR: personalization adapts 1–2 bullets to Yotta offer signals — facts intact
- [ ] Output shows "Solutions Engineer — éditeur SaaS IA" not "P4 × T5"
- [ ] 1-page PDF confirmed
- [ ] All 30 CVs re-validated after Phase 2
