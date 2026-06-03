# TASK — cv-generator : migration marketplace + matrice 5×5

> **Destinataire** : Claude Code, pour implémenter le skill `cv-generator` dans le plugin `renaud-marketplace`.
> **Objectif** : migrer le skill existant (`~/Projects/MyClaudeSkills/cv-generator/`) vers la structure marketplace ET passer de 3 modes génériques à une matrice **5 profils × 5 types d'entreprise**, avec 15 cases crédibles remplies. Pour chaque case : texte de crédibilité, titre CV, 3 lignes about, 3 containers sur-mesure + contenu — en **FR et EN**.
> **Statut** : brief validé — prêt pour plan-feature + exécution.

---

## 1. Décisions de cadrage (tranchées le 03/06/2026)

- **Q1 — Scope** : cases pertinentes uniquement (~15), pas de grille complète.
- **Q2 — Profils** : 5 profils — ajout d'un profil **Sales/BizDev** distinct du Customer Success.
- **Q3 — Types d'entreprise** : 5 types — ajout de **Grand groupe Énergie/Industrie** (~16 candidatures réelles) et **Éditeur SaaS IA / Labo IA** (~22 candidatures).

## 2. La matrice

**Profils** : P1 AI Architecte · P2 AI Lead/Manager · P3 CTO · P4 Customer Success/FDE · P5 Sales/BizDev
**Types** : T1 Startup industrielle/deeptech · T2 Ingénierie/BET · T3 ESN/Conseil · T4 Grand groupe Énergie/Industrie · T5 Éditeur SaaS IA/Labo IA

| | T1 Startup | T2 BET | T3 ESN/Conseil | T4 Grand groupe | T5 SaaS/Labo IA |
|---|---|---|---|---|---|
| **P1 Architecte** | ✅ Terabase | ✅ Egis, EP2C | ✅ ILLUIN, WEnvision, Le Hibou | ✅ TotalEnergies, Technip, Hilti, ASN | ✅ Cohere, Anthropic, Microsoft, Tomorro, Mapbox |
| **P2 Lead/Manager** | ✅ Fuse, Terabase | — | ✅ Médiane, Skapa, Quotacom | ✅ Tarkett, Thales | ✅ iAdvize, JobTeaser, Mistral |
| **P3 CTO** | ✅ Relief, Overstory | — | — | — | ✅ MuseIA, Virtuoz, Ublo |
| **P4 CS/FDE** | ✅ Oplit | — | — | — | ✅ Dust, Nabla, Zaion, OpenAI |
| **P5 Sales/BizDev** | — | — | ✅ ILLUIN Senior AE | — | ✅ Anthropic AE, Mistral BDM, Fennex |

**15 cases retenues.** Cases écartées : CTO/CS/Sales en BET ou grand groupe (pas crédible ou pas de marché), Lead en BET (en pratique, les BET qui se structurent recrutent un profil architecte-référent → couvert par P1×T2).

## 3. Règle transverse — neutraliser le gap « founder/solopreneur »

Gap récurrent identifié dans ~30 refus (explicite chez Anthropic, iAdvize, ASN Marine Bidder) : profil perçu comme « trop petit » ou « trop autonome ». Règles applicables à TOUTES les cases :

1. **Blue Green = « AI studio » avec clients enterprise nommés** (EnBW, Valorem, IC Ingénieurs) — jamais « indépendant » ou « freelance ».
2. **Open Ocean en avant** dès que la cible est structurée : équipe de 12, levée €2M, exit industriel (Artelia), clients DCNS/SBM Offshore/RTE.
3. **Artelia = preuve corporate** : 3 ans à Londres dans un groupe d'ingénierie international, P&L, C-level.
4. **Jamais le mot « founder » dans le titre CV** pour T4 (grand groupe) — il reste dans l'expérience Open Ocean.
5. **Toujours un produit en prod comme preuve** : BlueWind Companion v2.2 live (RAG 22 800 chunks, 5 agents Pydantic AI, Claude) — montre la capacité à shipper, pas à « conseiller ».

## 4. Convention containers (rappel technique)

3 colonnes de compétences, couleurs fixes : **container 1 = gold `#E7AF44`** (technique/IA), **container 2 = vert `#4EA265`** (business/leadership), **container 3 = bleu `#3C9ED9`** (secteur). La matrice fournit pour chaque case les 3 **titres** + 3-4 items chacun. Items marqués ⊕ = à ajouter au pool `cv-master.json` (n'existent pas encore).

---

# P1 — AI ARCHITECTE / SOLUTION ARCHITECT

**Définition** : cadrer quelle solution technique répond au besoin du client — design de solution, choix techno, architecture GenAI. Client-facing, pas commercial. **Le profil cœur** (~16 candidatures).

**Base profil (commune aux 5 cases)**
- Titre EN : `AI Solutions Architect — GenAI Systems in Production`
- Titre FR : `Architecte Solutions IA — Systèmes GenAI en production`
- Expérience mise en avant : Blue Green (architectures livrées EnBW/Valorem + BWC en prod) > Open Ocean (plateforme SaaS scalée) > Artelia (compréhension client enterprise).

## P1×T1 — Startup industrielle / deeptech (ex. Terabase)

**Crédibilité FR** : Renaud a fait exactement ce que ces boîtes cherchent : transformer de la donnée industrielle complexe en produit logiciel. Open Ocean = plateforme de données marines montée de zéro au déploiement industriel (équipe de 12, €2M levés, exit). Aujourd'hui il architecture des systèmes GenAI en production (BlueWind Companion : RAG 22 800 chunks, 5 agents). Il parle nativement les deux langues : l'ingénierie physique ET le produit IA.

**Credibility EN**: Renaud has done exactly what these companies need: turning complex industrial data into software products. Open Ocean = marine data platform built from scratch to industrial deployment (team of 12, €2M raised, exit). Today he architects production GenAI systems (BlueWind Companion: 22,800-chunk RAG, 5 agents). He natively speaks both languages: physical engineering AND AI product.

- Titre EN : `AI Product Architect — Industrial Data & GenAI`
- Titre FR : `Architecte Produit IA — Données industrielles & GenAI`
- About EN : (1) Engineer-entrepreneur, 15+ years turning industrial & environmental data into products. (2) Built a data platform from prototype to industrial scale (€2M raised, exit). (3) Now shipping production GenAI systems for the energy industry.
- About FR : (1) Ingénieur-entrepreneur, 15+ ans à transformer la donnée industrielle en produits. (2) A scalé une plateforme data du prototype au déploiement industriel (€2M levés, exit). (3) Livre aujourd'hui des systèmes GenAI en production pour l'énergie.
- Containers EN : **AI Product Architecture** [LLMs, RAG, AI Agents · Product Architecture · MCP servers · Backend & Cloud Systems] / **0→1 Execution** [Lab-to-Industrial Scale-up · Product Development & Architecture · Agile Product Delivery] / **Industrial & Energy Data** [Renewable Energy (15+ yrs) · Marine & Environmental Data · Engineering & Infrastructure]
- Containers FR : **Architecture Produit IA** / **Exécution 0→1** / **Données industrielles & Énergie** (mêmes items)

## P1×T2 — Ingénierie / BET qui se structure pour l'IA (ex. Egis, EP2C, Ekwil, Natural Power)

**Crédibilité FR** : Renaud EST un ingénieur de BET passé de l'autre côté. 15 ans dans l'ingénierie (océano, offshore wind, Artelia), il connaît les livrables, les AO, les marges et la culture métier. Depuis 2023 il fait précisément ce que ces boîtes veulent internaliser : automatiser la production de rapports, croiser la doc technique, mettre la GenAI dans les workflows d'ingénierie (IC Ingénieurs : diagnostics automatisés en prod). Profil rare : crédible devant les ingénieurs ET capable de shipper.

**Credibility EN**: Renaud IS an engineering-consultancy engineer who crossed over. 15 years in engineering (oceanography, offshore wind, Artelia), he knows the deliverables, tenders, margins and culture. Since 2023 he has done precisely what these firms want to internalise: automating report production, cross-referencing technical documentation, embedding GenAI in engineering workflows (IC Ingénieurs: automated diagnostics in production). Rare profile: credible with engineers AND able to ship.

- Titre EN : `AI Architect — GenAI for Engineering Workflows`
- Titre FR : `Architecte IA — GenAI pour les métiers de l'ingénierie`
- About EN : (1) 15+ years in engineering consultancies and offshore wind before going AI-first. (2) Ships GenAI tools used daily by engineering firms (automated diagnostics, tender analysis). (3) Fluent in both worlds: engineering deliverables and production AI systems.
- About FR : (1) 15+ ans en ingénierie et éolien offshore avant de passer à l'IA. (2) Livre des outils GenAI utilisés au quotidien par des BET (diagnostics automatisés, analyse d'AO). (3) Bilingue livrables d'ingénierie / systèmes IA en production.
- Containers EN : **GenAI for Engineering** [LLMs, RAG, AI Agents · Document Intelligence & Reporting ⊕ · Workflow Automation · Process Automation] / **Change & Adoption** [Stakeholder & Client Engagement · AI Awareness Training ⊕ · Cross-functional Team Management] / **Engineering & Infrastructure** [Engineering & Infrastructure · Offshore Wind Development · Renewable Energy (15+ yrs)]
- Containers FR : **GenAI pour l'ingénierie** / **Conduite du changement** / **Ingénierie & Infrastructure**

## P1×T3 — ESN / Conseil (ex. ILLUIN Lead Architect, WEnvision, Le Hibou)

**Crédibilité FR** : le combo qu'une ESN vend cher : un architecte senior qui produit (BWC, Edifice, WattCast en prod) ET qui sait tenir un cycle avant-vente — cadrage, propale, démo, négociation C-level (Artelia, Open Ocean : 100% des cycles de vente). Il apporte aussi un secteur différenciant (énergie/infrastructure) où les ESN généralistes manquent de légitimité.

**Credibility EN**: the combo consultancies charge a premium for: a senior architect who ships (BWC, Edifice, WattCast in production) AND can run pre-sales — scoping, proposals, demos, C-level negotiation (Artelia, Open Ocean: owned 100% of sales cycles). He also brings a differentiating vertical (energy/infrastructure) where generalist consultancies lack legitimacy.

- Titre EN : `GenAI Solution Architect — Pre-Sales to Production`
- Titre FR : `Architecte Solutions GenAI — De l'avant-vente à la production`
- About EN : (1) Senior architect shipping production GenAI systems (RAG, multi-agent, MCP). (2) Comfortable across the full cycle: scoping, proposal, demo, delivery. (3) Differentiating vertical: 15+ years energy & infrastructure.
- About FR : (1) Architecte senior, systèmes GenAI en production (RAG, multi-agents, MCP). (2) À l'aise sur tout le cycle : cadrage, propale, démo, delivery. (3) Verticale différenciante : 15+ ans énergie & infrastructure.
- Containers EN : **GenAI Architecture** [LLMs, RAG, AI Agents · MCP servers · Product Architecture · Backend & Cloud Systems] / **Consulting & Pre-Sales** [Stakeholder & Client Engagement · C-level negotiations · Solution Scoping & Proposals ⊕] / **Energy & Infrastructure** [Renewable Energy (15+ yrs) · Engineering & Infrastructure · Offshore Wind Development]
- Containers FR : **Architecture GenAI** / **Conseil & Avant-vente** / **Énergie & Infrastructure**

## P1×T4 — Grand groupe Énergie/Industrie (ex. TotalEnergies, Technip, Hilti, ASN, EDF)

**Crédibilité FR** : il connaît les deux faces : l'intérieur d'un groupe d'ingénierie international (Artelia Londres, P&L, gouvernance) et la livraison d'IA en environnement exigeant (EnBW France — analyse d'AO éolien offshore, données sensibles, hébergement France). 15 ans dans l'énergie = il parle métier avec les opérationnels, pas seulement techno avec la DSI. ⚠️ Ne JAMAIS ouvrir sur « founder » : ouvrir sur Artelia + clients majors.

**Credibility EN**: he knows both sides: inside an international engineering group (Artelia London, P&L, governance) and delivering AI in demanding environments (EnBW France — offshore wind tender analysis, sensitive data, French hosting). 15 years in energy = he talks business with operations, not just tech with IT. ⚠️ NEVER open on "founder": open on Artelia + major-account clients.

- Titre EN : `AI Solutions Architect — Energy & Industry`
- Titre FR : `Architecte Solutions IA — Énergie & Industrie`
- About EN : (1) 15+ years in energy & engineering, including 3 years in an international engineering group (London). (2) Delivers production GenAI for energy majors (EnBW, Valorem). (3) Trilingual, has worked in France, UK, Brazil and the US.
- About FR : (1) 15+ ans énergie & ingénierie, dont 3 ans dans un groupe international (Londres). (2) Livre de la GenAI en production pour des acteurs majeurs de l'énergie (EnBW, Valorem). (3) Trilingue, a travaillé en France, UK, Brésil, USA.
- Containers EN : **GenAI Production Systems** [LLMs, RAG, AI Agents · MCP servers · Process Automation · Backend & Cloud Systems] / **Enterprise Delivery** [Stakeholder & Client Engagement · Cross-functional Team Management · Full P&L responsibility] / **Energy & Industry** [Renewable Energy (15+ yrs) · Offshore Wind Development · Engineering & Infrastructure]
- Containers FR : **Systèmes GenAI en production** / **Delivery grands comptes** / **Énergie & Industrie**

## P1×T5 — Éditeur SaaS IA / Labo IA (ex. Cohere, Anthropic Applied AI, Microsoft CSA, Tomorro, Mapbox)

**Crédibilité FR** : le profil « applied AI » que cherchent les labos : il déploie LEURS modèles chez de vrais clients enterprise. Stack moderne maîtrisée en prod (Claude, RAG pgvector, Pydantic AI, MCP, CopilotKit), et surtout la capacité à traduire un besoin métier flou en architecture qui tient. Son passé d'opérateur (exit, P&L) le rend crédible face à des CTO clients. ⚠️ C'est ici que le gap solopreneur a coûté (Anthropic) : insister sur les équipes menées (12 chez Open Ocean) et les clients enterprise.

**Credibility EN**: the "applied AI" profile labs look for: he deploys THEIR models with real enterprise customers. Modern stack in production (Claude, pgvector RAG, Pydantic AI, MCP, CopilotKit), and above all the ability to turn a fuzzy business need into an architecture that holds. His operator background (exit, P&L) makes him credible with customer CTOs. ⚠️ This is where the solopreneur gap cost him (Anthropic): emphasise teams led (12 at Open Ocean) and enterprise clients.

- Titre EN : `Applied AI Architect — Enterprise GenAI Deployments`
- Titre FR : `Architecte Applied AI — Déploiements GenAI enterprise`
- About EN : (1) Deploys frontier-model systems in production for enterprise clients (energy, engineering). (2) Hands-on: RAG, multi-agent, MCP servers, evals — shipped, not slideware. (3) Former founder-CTO: built a 12-person product team, raised €2M, exited.
- About FR : (1) Déploie des systèmes à base de modèles frontière en production chez des clients enterprise. (2) Hands-on : RAG, multi-agents, MCP, evals — livré, pas du slideware. (3) Ex founder-CTO : équipe produit de 12, €2M levés, exit.
- Containers EN : **Applied AI Engineering** [LLMs, RAG, AI Agents · MCP servers · AI Evals & Observability ⊕ · Backend & Cloud Systems] / **Customer-Facing Delivery** [Stakeholder & Client Engagement · Solution Scoping & Proposals ⊕ · C-level negotiations] / **Industry Verticals** [Renewable Energy (15+ yrs) · Engineering & Infrastructure · Marine data intelligence]
- Containers FR : **Ingénierie Applied AI** / **Delivery client** / **Verticales industrie**

---

# P2 — AI LEAD / MANAGER

**Définition** : management d'équipe IA, delivery de produit IA, structuration de la fonction IA (~11 candidatures).

**Base profil** : la preuve de management vient d'Open Ocean (équipe de 12 pluridisciplinaire, 8 ans) + Artelia (cross-functional, P&L). Blue Green prouve que le leadership est resté hands-on et à jour techniquement.

## P2×T1 — Startup industrielle / deeptech (ex. Fuse Energy, Terabase)

**Crédibilité FR** : un lead qui a déjà vécu le scale-up de l'intérieur, côté fondateur : recrutement, roadmap, dette technique, investisseurs. Il sait arbitrer vitesse/qualité dans un contexte où le runway compte, et reste capable de coder/architecturer lui-même — exactement le « player-coach » que cherche une startup industrielle.

**Credibility EN**: a lead who has lived scale-up from the inside, as a founder: hiring, roadmap, tech debt, investors. He knows how to trade speed vs quality when runway matters, and can still code/architect himself — exactly the player-coach an industrial startup needs.

- Titre EN : `AI Lead — Player-Coach for Industrial Scale-ups`
- Titre FR : `AI Lead — Player-coach pour scale-ups industrielles`
- About EN : (1) Founder-CTO experience: grew a product team to 12, raised €2M, exited. (2) Still hands-on: ships production GenAI (RAG, agents) today. (3) Deep industrial & energy domain knowledge.
- About FR : (1) Expérience founder-CTO : équipe de 12, €2M levés, exit. (2) Toujours hands-on : livre de la GenAI en prod aujourd'hui. (3) Connaissance profonde des secteurs industriels & énergie.
- Containers EN : **Hands-on AI Leadership** [LLMs, RAG, AI Agents · Product Architecture · Workflow Automation] / **Product & Delivery** [R&D Team Leadership (12 people) · Agile Product Delivery · Lab-to-Industrial Scale-up · Investor Relations & Fundraising] / **Industrial Scale-up** [Renewable Energy (15+ yrs) · Scale-up Operations · Engineering & Infrastructure]
- Containers FR : **Leadership IA hands-on** / **Produit & Delivery** / **Scale-up industriel**

## P2×T3 — ESN / Conseil (ex. Médiane, Skapa, Quotacom)

**Crédibilité FR** : monter une practice GenAI demande trois choses qu'il a déjà faites : vendre (cycles complets C-level), livrer (systèmes en prod chez EnBW/Valorem/IC) et faire grandir une équipe (12 chez Open Ocean). Il peut être mis devant un client dès le premier jour avec une crédibilité technique réelle.

**Credibility EN**: building a GenAI practice requires three things he has already done: sell (full C-level cycles), deliver (production systems for EnBW/Valorem/IC) and grow a team (12 at Open Ocean). He can be put in front of a client on day one with real technical credibility.

- Titre EN : `GenAI Practice Lead — Build, Sell, Deliver`
- Titre FR : `Responsable Practice GenAI — Construire, vendre, livrer`
- About EN : (1) Has built and led a 12-person multi-disciplinary tech team. (2) Sells and delivers GenAI end-to-end: scoping, proposal, production. (3) Differentiating vertical: energy & infrastructure.
- About FR : (1) A construit et dirigé une équipe tech pluridisciplinaire de 12. (2) Vend et livre la GenAI de bout en bout : cadrage, propale, production. (3) Verticale différenciante : énergie & infrastructure.
- Containers EN : **GenAI Practice Building** [LLMs, RAG, AI Agents · Product Architecture · AI Awareness Training ⊕] / **Team & P&L Leadership** [Team Leadership (12 people) · Full P&L responsibility · Enterprise Sales · C-level negotiations] / **Energy & Infrastructure** [Renewable Energy (15+ yrs) · Engineering & Infrastructure · Offshore Wind Development]
- Containers FR : **Construction de practice GenAI** / **Leadership équipe & P&L** / **Énergie & Infrastructure**

## P2×T4 — Grand groupe Énergie/Industrie (ex. Tarkett AI Leader, Thales)

**Crédibilité FR** : pour piloter la transformation IA d'un groupe industriel, il faut quelqu'un qui comprenne les opérations (15 ans terrain énergie/ingénierie), sache parler aux directions métier (Artelia, C-level) et ait déjà mis de l'IA en production — pas en POC. Sa trajectoire entrepreneur est un atout reformulé : il sait faire beaucoup avec peu, et structurer de zéro. ⚠️ Même règle que P1×T4 : ouvrir corporate, pas founder.

**Credibility EN**: leading AI transformation in an industrial group takes someone who understands operations (15 years in energy/engineering), can talk to business leadership (Artelia, C-level) and has put AI into production — not POCs. His entrepreneurial track is reframed as an asset: he does a lot with little and structures from scratch. ⚠️ Same rule as P1×T4: open corporate, not founder.

- Titre EN : `AI Lead — Industrial AI Transformation`
- Titre FR : `AI Lead — Transformation IA industrielle`
- About EN : (1) 15+ years in energy & engineering, incl. international group experience (London). (2) Took AI from strategy to production for energy players. (3) Led cross-functional teams and full P&L.
- About FR : (1) 15+ ans énergie & ingénierie, dont groupe international (Londres). (2) A mené l'IA de la stratégie à la production chez des acteurs de l'énergie. (3) A dirigé des équipes transverses avec P&L complet.
- Containers EN : **AI Strategy & Delivery** [LLMs, RAG, AI Agents · Process Automation · Workflow Automation] / **Transformation Leadership** [Cross-functional Team Management · Stakeholder & Client Engagement · Full P&L responsibility · AI Awareness Training ⊕] / **Energy & Industry** [Renewable Energy (15+ yrs) · Engineering & Infrastructure · Offshore Wind Development]
- Containers FR : **Stratégie & Delivery IA** / **Leadership de transformation** / **Énergie & Industrie**

## P2×T5 — Éditeur SaaS IA (ex. iAdvize, JobTeaser, Mistral PM Science)

**Crédibilité FR** : il a déjà fait le métier : produit SaaS data/IA porté du prototype au déploiement industriel, avec roadmap, delivery agile et arbitrages produit (Open Ocean, puis BWC aujourd'hui). Il apporte en plus la vision client enterprise : il sait ce qu'un grand compte attend d'un produit IA. ⚠️ Gap iAdvize (« trop autonome ») : montrer l'appétence à s'intégrer dans une organisation produit existante.

**Credibility EN**: he has done the job before: a data/AI SaaS product taken from prototype to industrial deployment, with roadmap, agile delivery and product trade-offs (Open Ocean, now BWC). He adds the enterprise-customer lens: he knows what large accounts expect from an AI product. ⚠️ iAdvize gap ("too autonomous"): show willingness to integrate into an existing product org.

- Titre EN : `AI Product Lead — From Prototype to Production`
- Titre FR : `Lead Produit IA — Du prototype à la production`
- About EN : (1) Scaled an AI/data SaaS product from prototype to industrial deployment. (2) Led a 12-person product team through agile delivery. (3) Ships modern GenAI today: RAG, agents, evals.
- About FR : (1) A scalé un produit SaaS data/IA du prototype au déploiement industriel. (2) A mené une équipe produit de 12 en delivery agile. (3) Livre de la GenAI moderne aujourd'hui : RAG, agents, evals.
- Containers EN : **AI Product Delivery** [LLMs, RAG, AI Agents · Product Architecture · AI Evals & Observability ⊕] / **Cross-functional Leadership** [R&D Team Leadership (12 people) · Agile Product Delivery · Cross-functional Team Management] / **B2B SaaS & Verticals** [Scale-up Operations · Marine data intelligence · Renewable Energy (15+ yrs)]
- Containers FR : **Delivery produit IA** / **Leadership transverse** / **SaaS B2B & verticales**

---

# P3 — CTO

**Définition** : son ancien poste (Open Ocean). Leadership technique, scale-up, fundraising. 2 cases seulement — le CTO n'a de sens qu'en startup/scale-up.

## P3×T1 — Startup industrielle / deeptech (ex. Relief — score 92, Overstory)

**Crédibilité FR** : il a déjà été exactement ce CTO : Open Ocean, plateforme de données environnementales pour l'industrie offshore, du lab au déploiement industriel, équipe de 12, €2M levés, exit réussi. Il connaît les investisseurs, la dette technique, le recrutement et le terrain industriel. Et contrairement à beaucoup d'ex-CTO, sa stack est à jour : il livre du GenAI en prod aujourd'hui.

**Credibility EN**: he has already been exactly this CTO: Open Ocean, environmental-data platform for offshore industry, lab to industrial deployment, team of 12, €2M raised, successful exit. He knows investors, tech debt, hiring and the industrial field. Unlike many former CTOs, his stack is current: he ships production GenAI today.

- Titre EN : `CTO — Scaling AI-Powered Solutions for Climate & Industry`
- Titre FR : `CTO — Scale-up de solutions IA pour le climat & l'industrie`
- About EN : (1) 15+ years scaling technology ventures from prototype to industrial deployment. (2) Proven: built a 12-person team, raised €2M, successful exit. (3) Hands-on today: production GenAI systems (RAG, agents, MCP).
- About FR : (1) 15+ ans à scaler des ventures tech du prototype au déploiement industriel. (2) Preuves : équipe de 12, €2M levés, exit réussi. (3) Hands-on aujourd'hui : systèmes GenAI en production.
- Containers EN : **Technology & Architecture** [Product Architecture · AI/ML Stack (LLMs, RAG) · Backend & Cloud Systems · Process Automation] / **Scale-up Leadership** [R&D Team Leadership (12 people) · Investor Relations & Fundraising · Lab-to-Industrial Scale-up · Full P&L Responsibility] / **Climate & Industry** [Climate Tech & Sustainability · Renewable Energy (15+ yrs) · Marine & Environmental Data]
- Containers FR : **Technologie & Architecture** / **Leadership scale-up** / **Climat & Industrie**

## P3×T5 — Éditeur SaaS IA early-stage (ex. MuseIA, Virtuoz, Ublo)

**Crédibilité FR** : pour un éditeur early-stage, le risque CTO c'est l'architecte de papier. Lui apporte la preuve inverse : BWC v2.2 live (Next.js + FastAPI + Pydantic AI + Supabase pgvector, hébergé France), construit seul en mode produit — vélocité maximale — après avoir prouvé qu'il sait faire grandir une équipe quand le produit décolle (Open Ocean). Le couple vélocité solo + expérience scale est précisément ce qu'un fondateur non-technique cherche.

**Credibility EN**: for an early-stage vendor, the CTO risk is the paper architect. He brings the opposite proof: BWC v2.2 live (Next.js + FastAPI + Pydantic AI + Supabase pgvector, hosted in France), built solo at maximum velocity — after proving he can grow a team when the product takes off (Open Ocean). The solo-velocity + scaling-experience combo is precisely what a non-technical founder needs.

- Titre EN : `CTO — AI SaaS, from First Commit to Scale`
- Titre FR : `CTO — SaaS IA, du premier commit au scale`
- About EN : (1) Ships full-stack AI SaaS solo: Next.js, FastAPI, Pydantic AI, pgvector — live in production. (2) Has scaled before: 12-person team, €2M raised, exit. (3) Product-minded: talks to customers, owns the roadmap.
- About FR : (1) Livre un SaaS IA full-stack en solo : Next.js, FastAPI, Pydantic AI, pgvector — live en production. (2) A déjà scalé : équipe de 12, €2M levés, exit. (3) Esprit produit : parle aux clients, porte la roadmap.
- Containers EN : **AI Platform Architecture** [LLMs, RAG, AI Agents · Product Architecture · Backend & Cloud Systems · MCP servers] / **Fundraising & Scale** [Investor Relations & Fundraising · Lab-to-Industrial Scale-up · R&D Team Leadership (12 people)] / **B2B SaaS** [Scale-up Operations · Enterprise Sales · Marine data intelligence]
- Containers FR : **Architecture plateforme IA** / **Levée & Scale** / **SaaS B2B**

---

# P4 — CUSTOMER SUCCESS / FORWARD DEPLOYED ENGINEER

**Définition** : s'assurer que la solution vendue répond au besoin client + intégration réussie. « Beaucoup plus commercial » que l'architecte, mais orienté delivery (≠ P5 Sales). 2 cases.

## P4×T1 — Startup industrielle (ex. Oplit FDE)

**Crédibilité FR** : le FDE industriel doit gagner la confiance d'opérationnels méfiants et adapter le produit au terrain. Renaud fait ça depuis 15 ans : il a vendu et déployé des solutions data chez DCNS, SBM Offshore, RTE, puis des agents IA chez EnBW et Valorem. Il sait écouter un besoin métier mal formulé, le traduire en config/intégration, et laisser le client autonome.

**Credibility EN**: the industrial FDE must win the trust of sceptical operations people and adapt the product to the field. Renaud has done this for 15 years: deployed data solutions at DCNS, SBM Offshore, RTE, then AI agents at EnBW and Valorem. He hears a poorly-stated business need, turns it into configuration/integration, and leaves the customer autonomous.

- Titre EN : `Forward Deployed Engineer — Industrial AI`
- Titre FR : `Forward Deployed Engineer — IA industrielle`
- About EN : (1) 15+ years deploying technical solutions with industrial clients (energy, marine, infrastructure). (2) Hands-on AI integration: RAG, agents, workflow automation. (3) Trusted by operations: speaks engineering, not just software.
- About FR : (1) 15+ ans à déployer des solutions techniques chez des industriels. (2) Intégration IA hands-on : RAG, agents, automatisation de workflows. (3) La confiance des opérationnels : il parle ingénierie, pas seulement logiciel.
- Containers EN : **Solution Deployment** [LLMs, RAG, AI Agents · Workflow Automation · Process Automation] / **Client Engagement** [Stakeholder & Client Engagement · AI Awareness Training ⊕ · Customer Onboarding & Adoption ⊕] / **Energy & Industry** [Renewable Energy (15+ yrs) · Engineering & Infrastructure · Marine & Environmental Data]
- Containers FR : **Déploiement de solutions** / **Engagement client** / **Énergie & Industrie**

## P4×T5 — Éditeur SaaS IA / Labo (ex. Dust SE 🔥 pipeline actif, OpenAI Solution Eng, Nabla, Zaion)

**Crédibilité FR** : le Solutions Engineer idéal d'un éditeur GenAI a trois jambes : technique (il construit avec l'API : BWC = multi-agents Claude en prod), commercial (démos, POC, closing — 100% des cycles chez Open Ocean) et empathie client enterprise (15 ans côté client industriel). Il a littéralement été l'utilisateur-acheteur que ces éditeurs ciblent. ⚠️ Neutraliser le gap solopreneur : cadrer Blue Green comme delivery multi-clients, insister sur le travail en équipe produit.

**Credibility EN**: the ideal GenAI Solutions Engineer has three legs: technical (he builds with the API: BWC = Claude multi-agent in production), commercial (demos, POCs, closing — 100% of cycles at Open Ocean) and enterprise-customer empathy (15 years on the industrial-client side). He has literally been the user-buyer these vendors target. ⚠️ Neutralise the solopreneur gap: frame Blue Green as multi-client delivery, stress product teamwork.

- Titre EN : `AI Solutions Engineer — Enterprise GenAI Adoption`
- Titre FR : `Solutions Engineer IA — Adoption GenAI enterprise`
- About EN : (1) Builds production systems on frontier-model APIs (multi-agent, RAG, MCP). (2) Runs the full customer cycle: discovery, demo, POC, production. (3) 15+ years of enterprise empathy from the customer side (energy, engineering).
- About FR : (1) Construit des systèmes en production sur les API de modèles frontière. (2) Mène le cycle client complet : discovery, démo, POC, production. (3) 15+ ans d'empathie enterprise, côté client (énergie, ingénierie).
- Containers EN : **Forward Deployed Engineering** [LLMs, RAG, AI Agents · MCP servers · AI Evals & Observability ⊕] / **Customer Success & Adoption** [Customer Onboarding & Adoption ⊕ · Stakeholder & Client Engagement · Enterprise Sales] / **Enterprise Verticals** [Renewable Energy (15+ yrs) · Engineering & Infrastructure · Climate Tech & Sustainability]
- Containers FR : **Forward Deployed Engineering** / **Customer Success & Adoption** / **Verticales enterprise**

---

# P5 — SALES / BIZDEV (nouveau profil)

**Définition** : commercial pur — AE, BDM. Distinct du CS : ici on chasse et on close, le delivery est secondaire. ~5 candidatures (Anthropic AE, ILLUIN Senior AE, Mistral BDM, Fennex, ASN Marine Bidder). 2 cases.

## P5×T3 — ESN / Conseil (ex. ILLUIN Senior AE — 🔥 process en cours, étape 2/4)

**Crédibilité FR** : vendre du conseil GenAI à des DSI exige un commercial qui comprend ce qu'il vend. Renaud a porté des cycles complets de vente de services techniques : Open Ocean (prospection → closing C-level, 8 ans), Artelia (+15% YOY sur portefeuille offshore, contrats enterprise complexes). Il fait les démos lui-même et peut cadrer l'AO avec l'équipe technique — le « selling architect » qui raccourcit les cycles.

**Credibility EN**: selling GenAI consulting to CIOs takes a salesperson who understands what he sells. Renaud has owned full technical-services sales cycles: Open Ocean (prospecting → C-level closing, 8 years), Artelia (+15% YOY on the offshore portfolio, complex enterprise contracts). He runs demos himself and scopes the bid with the technical team — the "selling architect" who shortens cycles.

- Titre EN : `Senior Account Executive — AI Consulting & Services`
- Titre FR : `Senior Account Executive — Conseil & services IA`
- About EN : (1) 20 years selling technical services and solutions to enterprise accounts. (2) Owns the full cycle: prospecting, demo, proposal, C-level closing. (3) Technical enough to scope GenAI projects credibly with CIOs.
- About FR : (1) 20 ans de vente de services et solutions techniques aux grands comptes. (2) Porte le cycle complet : prospection, démo, propale, closing C-level. (3) Assez technique pour cadrer un projet GenAI face à une DSI.
- Containers EN : **AI Solution Selling** [LLMs, RAG, AI Agents · Solution Scoping & Proposals ⊕ · Workflow Automation] / **Complex Sales Cycles** [Enterprise Sales · C-level negotiations · Business Development · Full P&L responsibility] / **Energy & Infrastructure Network** [Renewable Energy (15+ yrs) · Engineering & Infrastructure · Offshore Wind Development]
- Containers FR : **Vente de solutions IA** / **Cycles de vente complexes** / **Réseau Énergie & Infrastructure**

## P5×T5 — Éditeur SaaS IA / Labo (ex. Anthropic AE, Mistral BDM, Fennex)

**Crédibilité FR** : un AE/BDM qui a construit avec le produit qu'il vend : il utilise Claude/Mistral en production tous les jours, et sait montrer la valeur en démo live plutôt qu'en slides. Son réseau énergie/industrie (15 ans, FR-UK-BR) ouvre des verticales que les sales généralistes n'atteignent pas. ⚠️ C'est LA case où le refus Anthropic a été explicite sur le profil solopreneur : le narratif doit ouvrir sur Artelia (quota-carrying corporate, +15% YOY) et Open Ocean (8 ans de cycles enterprise), Blue Green en dernier comme preuve de maîtrise produit.

**Credibility EN**: an AE/BDM who has built with the product he sells: he uses Claude/Mistral in production daily and shows value in live demos, not slides. His energy/industry network (15 years, FR-UK-BR) opens verticals generalist sellers can't reach. ⚠️ THE cell where the Anthropic rejection was explicit about the solopreneur profile: the narrative must open with Artelia (corporate quota-carrying, +15% YOY) and Open Ocean (8 years of enterprise cycles), Blue Green last as product-mastery proof.

- Titre EN : `Account Executive — GenAI for Energy & Industry`
- Titre FR : `Account Executive — GenAI pour l'énergie & l'industrie`
- About EN : (1) Grew an offshore-wind enterprise portfolio +15% YOY in an international group. (2) 8 years owning full B2B sales cycles, prospecting to C-level closing. (3) Sells what he builds: daily production user of frontier-model APIs.
- About FR : (1) +15% YOY sur un portefeuille enterprise éolien offshore en groupe international. (2) 8 ans de cycles de vente B2B complets, prospection → closing C-level. (3) Vend ce qu'il construit : utilisateur quotidien des API de modèles frontière en production.
- Containers EN : **Technical Fluency (GenAI)** [LLMs, RAG, AI Agents · MCP servers · NoCode/LowCode Solutions] / **Enterprise Sales** [Enterprise Sales · C-level negotiations · Business Development] / **Energy & Industry Network** [Renewable Energy (15+ yrs) · Offshore Wind Development · Engineering & Infrastructure]
- Containers FR : **Maîtrise technique GenAI** / **Vente enterprise** / **Réseau Énergie & Industrie**

---

# 6. Implémentation — spécification pour Claude Code

## 6.1 Changements de structure (cv-master.json + generate_cv.py)

1. **Nouveau paramètre** `generate_cv(profile, company_type, lang, ...)` remplaçant `positioning` seul. Rétro-compatibilité : `ai_consulting` → (P1, défaut T4), `cto` → (P3, T1), `business_dev` → (P5, T3).
2. **`cv-master.json`** : ajouter une section `matrix` avec les 15 cases. Chaque case = `{title, about[3], containers: [{title, color, items[3-4]}], credibility_note}`. Tout en FR + EN (clés `fr`/`en`).
3. **Pool de compétences — nouveaux items ⊕ à ajouter** : `Document Intelligence & Reporting`, `AI Awareness Training`, `Solution Scoping & Proposals`, `AI Evals & Observability`, `Customer Onboarding & Adoption` (+ traductions FR).
4. **Fiches descriptives par profil** : créer `profiles/{p1_architecte,p2_lead,p3_cto,p4_cs_fde,p5_sales}.md` — définition, cases couvertes, règles narratives (dont neutralisation solopreneur), exemples de candidatures réelles.
5. **Bullets d'expérience** : décliner les bullets `blue_green`/`artelia`/`open_ocean` par profil (5 jeux au lieu de 3). P4 et P5 réutilisent la base `business_dev` avec ajustements de narratif (ordre des expériences selon la règle solopreneur).
6. **Règle d'ordre des expériences** : pour T4 (grand groupe) et P5×T5, option `corporate_first: true` → le résumé/about met Artelia avant Blue Green.

## 6.2 Contraintes techniques à préserver

- Template SVG inline (weasyprint ne rend pas les emoji) ; vérification 1 page A4 via pikepdf ; couleurs containers fixes (gold/vert/bleu) ; template de référence : `templates/cv_template.html` (migré depuis `~/Projects/MyClaudeSkills/cv-generator/`).

## 6.3 Validation

- Générer les 15 CV FR + 15 EN en batch test (`scripts/batch_validate.py`), vérifier 1 page partout.
- Test prioritaire sur le pipeline actif : Relief (P3×T1), Dust (P4×T5), ILLUIN AE (P5×T3), ILLUIN Lead Architect (P1×T3), Oplit (P4×T1).

## 6.4 Structure marketplace (plugin dans renaud-marketplace)

La migration place le skill dans la structure suivante :

```
plugins/cv-generator/
├── .claude-plugin/
│   └── plugin.json              # name, version, description, author — v0.1.0
├── skills/
│   └── cv-generator/
│       └── SKILL.md             # Instructions Claude (frontmatter + body)
├── scripts/
│   └── generate_cv.py           # Migré + upgradé
├── data/
│   └── cv-master.json           # Migré + section matrix ajoutée
├── templates/
│   └── cv_template.html         # Migré
├── assets/
│   └── photo.jpeg               # GITIGNORE — présent localement uniquement
└── CHANGELOG.md
```

Source à migrer : `~/Projects/MyClaudeSkills/cv-generator/`
Après validation complète : supprimer la source.

## 6.5 Contrainte Cowork — pas de pip install

Remplacer `pip install weasyprint` par invocation à la volée :

```bash
uv run --with weasyprint --with pikepdf python3 $PLUGIN_DIR/scripts/generate_cv.py \
  --profile p1 --company-type t5 --lang en
```

Le `requirements.txt` (si conservé) est un manifeste de documentation uniquement — jamais exécuté au runtime.

## 6.6 Plugin directory resolver (dans SKILL.md)

Le SKILL.md doit résoudre `PLUGIN_DIR` via ce resolver prioritaire :

```bash
PLUGIN_DIR=$(python3 - <<'PYEOF'
import json, os, pathlib, sys, glob as _glob

home = pathlib.Path.home()

# 1. Env var override (dev)
env = os.environ.get('CV_GENERATOR_DIR', '')
if env and pathlib.Path(env, 'scripts', 'generate_cv.py').exists():
    print(env); sys.exit(0)

# 2. Claude Code marketplace cache
cache_root = home / '.claude' / 'plugins' / 'cache' / 'renaud-marketplace' / 'cv-generator'
if cache_root.exists():
    candidates = sorted(
        cache_root.glob('*/scripts/generate_cv.py'),
        key=lambda p: p.stat().st_mtime, reverse=True
    )
    if candidates:
        print(str(candidates[0].parent.parent)); sys.exit(0)

# 3. Cowork sandbox
for pat in ['/sessions/*/mnt/.remote-plugins/*/scripts/generate_cv.py']:
    matches = sorted(_glob.glob(pat), key=os.path.getmtime, reverse=True)
    if matches:
        print(os.path.dirname(os.path.dirname(matches[0]))); sys.exit(0)

# 4. Known dev path
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

## 6.7 Versioning

- Chaque composant versionné indépendamment (voir `docs/skill-marketplace-guide.md` §5).
- Règle de base : `marketplace.json` version === `plugin.json` version. À vérifier avant chaque commit.
- Ce build initial = v0.1.0 pour tous les composants.

---

# 7. Prochaines étapes

1. ✅ Étape 1 — brief (recherche + classification + rédaction). **LIVRÉ.**
2. ✅ Étape 2 — Renaud valide. **VALIDÉ le 03/06/2026.**
3. ⏳ Étape 3 — `/core_piv_loop:plan-feature` → plan d'implémentation détaillé.
4. ⏳ Étape 4 — `/core_piv_loop:execute` → implémentation + batch validation.
5. ⏳ Étape 5 — supprimer `~/Projects/MyClaudeSkills/cv-generator/` après validation.
