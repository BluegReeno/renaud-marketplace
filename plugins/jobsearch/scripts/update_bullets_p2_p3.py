#!/usr/bin/env python3
"""
Update cv-master.json: fix P2/P3 defaults + add cell-specific bullets for P2 (T3/T4/T5) and P3 (T1/T5).
Run once: python update_bullets_p2_p3.py
"""
import json
from pathlib import Path

DATA = Path(__file__).parent.parent / 'data' / 'cv-master.json'

with open(DATA, encoding='utf-8') as f:
    data = json.load(f)

exp = data['experiences']

# ─────────────────────────────────────────────────────────────
# 1. FIX DEFAULTS (factual errors + franglais)
# ─────────────────────────────────────────────────────────────

# Blue Green P2 default FR — "delivery" is anglicism
exp['blue_green']['bullets']['p2']['default']['fr'] = [
    "Piloté la livraison IA complète pour des clients enterprise (EnBW France, Valorem) : cadrage, architecture, mise en production",
    "Architecture de plateforme GenAI multi-agents (BlueWind Companion v2.2) : RAG, agents IA, serveurs MCP — live en production",
    "Animé des ateliers de sensibilisation à l'IA et facilité l'adoption cross-fonctionnelle",
]

# Blue Green P3 default EN — "solo at maximum velocity" removed
exp['blue_green']['bullets']['p3']['default']['en'] = [
    "Built and shipped full-stack AI SaaS platform (BlueWind Companion v2.2): Next.js, FastAPI, Pydantic AI, pgvector — live in France",
    "Architected and deployed production GenAI systems for enterprise clients (EnBW France, Valorem)",
    "Defined technical roadmap, selected the full stack, and shipped production systems end to end",
]

# Blue Green P3 default FR — "delivery bout-en-bout en solo à vélocité maximale" removed
exp['blue_green']['bullets']['p3']['default']['fr'] = [
    "Construit et livré une plateforme SaaS IA full-stack (BlueWind Companion v2.2) — live en France",
    "Architecture et déploiement de systèmes GenAI en production pour des clients enterprise (EnBW France, Valorem)",
    "Défini la roadmap technique, choisi le stack, livré des systèmes en production de bout en bout",
]

# Artelia P3 default EN — "Led investor presentations" was WRONG (Open Ocean, not Artelia)
exp['artelia']['bullets']['p3']['default']['en'] = [
    "Directed product strategy for marine data intelligence platform within Artelia (6,000-person engineering group)",
    "Full P&L responsibility — renewables & energy BU: budget, team management, C-level client portfolio in London",
    "Managed delivery for SBM Offshore, Nexans, Alcatel Submarine Networks, Cadeler — long-term framework clients",
]

# Artelia P3 default FR — same fix
exp['artelia']['bullets']['p3']['default']['fr'] = [
    "Direction stratégie produit de la plateforme data marine au sein du groupe Artelia (6 000 personnes)",
    "Responsabilité P&L complète, BU renouvelables & énergie : budget, équipe, portefeuille clients C-level à Londres",
    "Livraison pour SBM Offshore, Nexans, Alcatel Submarine Networks, Cadeler — clients en contrat cadre long terme",
]

# Open Ocean P3 default EN — fix "DCNS" and "Business Angels"
exp['open_ocean']['bullets']['p3']['default']['en'] = [
    "Architected and scaled marine data intelligence SaaS from prototype to industrial deployment",
    "Led product development with a 12-person team: roadmap, agile delivery, clients Naval Group, SBM Offshore, RTE",
    "Raised €2M from institutional investors (Seventure Partners, Cap Décisif/FNA) — acquired by Artelia (2019)",
]

# Open Ocean P3 default FR — fix "DCNS" and "Business Angels et VCs"
exp['open_ocean']['bullets']['p3']['default']['fr'] = [
    "Architecture et scale-up d'un SaaS de données marines du prototype au déploiement industriel",
    "Développement produit avec une équipe de 12 : roadmap, delivery agile, clients Naval Group, SBM Offshore, RTE",
    "Levée de 2 M€ auprès d'institutionnels (Seventure Partners, Cap Décisif/FNA) — cédé à Artelia (2019)",
]

# ─────────────────────────────────────────────────────────────
# 2. P2 × T3 — ESN/Consulting signal (ILLUIN, Capgemini type)
#    → delivery management, technical seniority, client advisory
# ─────────────────────────────────────────────────────────────

exp['blue_green']['bullets']['p2']['t3'] = {
    'en': [
        "Delivered GenAI solutions for EnBW France and Valorem: full project lifecycle from architecture design to production handover",
        "Designed BlueWind Companion v2.2 architecture (RAG, 5 Pydantic AI agents, MCP) — live in production, reused across clients",
        "Trained renewable energy developers on GenAI adoption: workshops, tooling, and ongoing advisory",
    ],
    'fr': [
        "Livraison de solutions GenAI pour EnBW France et Valorem : cycle complet, de la conception à la mise en production",
        "Architecture BlueWind Companion v2.2 (RAG, 5 agents Pydantic AI, MCP) — en production, réutilisé multi-clients",
        "Formation de développeurs de projets EnR à la GenAI : ateliers, outillage, accompagnement continu",
    ],
}

exp['artelia']['bullets']['p2']['t3'] = {
    'en': [
        "Led cross-functional delivery teams for offshore wind data services: SBM Offshore, Nexans, Alcatel Submarine Networks, Cadeler",
        "Client advisory on digital transformation: technology selection to deployment in operational engineering workflows",
        "Drove 15% YOY portfolio growth through structured account management and framework contract renewals",
    ],
    'fr': [
        "Pilotage d'équipes pluridisciplinaires pour les services data éolien offshore : SBM Offshore, Nexans, ASN, Cadeler",
        "Conseil client transformation numérique : sélection technologique jusqu'au déploiement en workflow opérationnel",
        "Croissance portefeuille +15%/an par gestion de comptes structurée et renouvellements de contrats cadres",
    ],
}

exp['open_ocean']['bullets']['p2']['t3'] = {
    'en': [
        "Built and led a 12-person product team (engineers, data scientists, web devs) delivering SaaS to offshore wind clients",
        "Scaled marine data intelligence platform from MVP to multi-client industrial deployment",
        "Raised €2M from institutional investors (Seventure Partners, Cap Décisif) — acquired by Artelia (2019)",
    ],
    'fr': [
        "Construit et dirigé une équipe de 12 personnes (ingénieurs, data scientists, web) pour un SaaS offshore wind",
        "Scale de la plateforme data marine du MVP au déploiement multi-clients en environnement industriel",
        "Levée de 2 M€ auprès d'institutionnels (Seventure Partners, Cap Décisif) — cession à Artelia (2019)",
    ],
}

# ─────────────────────────────────────────────────────────────
# 3. P2 × T4 — Grand groupe corporate (TotalEnergies, ASN type)
#    → governance, P&L, enterprise delivery, change management
#    NOTE: Artelia appears FIRST in T4 (CORPORATE_FIRST_CELLS)
# ─────────────────────────────────────────────────────────────

exp['blue_green']['bullets']['p2']['t4'] = {
    'en': [
        "Delivered production-grade AI systems for major energy groups (EnBW France, Valorem): regulatory compliance, auditability built-in",
        "Architected BlueWind Companion v2.2 for regulated energy environments: France-hosted, full traceability, pgvector",
        "Ran GenAI adoption programs for senior stakeholders and project development teams across energy sector",
    ],
    'fr': [
        "Systèmes IA production pour EnBW France et Valorem : conformité réglementaire, traçabilité, hébergement France",
        "Architecture BlueWind v2.2 en environnement réglementé : hébergement France, auditabilité, pipeline RAG maîtrisé",
        "Programmes d'adoption IA pour cadres dirigeants et équipes développement de projets d'énergies renouvelables",
    ],
}

exp['artelia']['bullets']['p2']['t4'] = {
    'en': [
        "Full P&L responsibility for the offshore wind business unit: budget, team, client portfolio — London-based",
        "Grew client portfolio 15% YOY: C-level negotiations, framework renewals with SBM Offshore, Nexans, ASN, Cadeler",
        "Led digital product strategy — adapted marine data platform to enterprise maritime clients across Europe",
    ],
    'fr': [
        "Responsabilité P&L complète de la BU éolien offshore : budget, équipe, portefeuille clients — base Londres",
        "Croissance portefeuille +15%/an : négociations C-level, renouvellements cadres (SBM Offshore, Nexans, ASN, Cadeler)",
        "Stratégie produit numérique — adaptation de la plateforme data marine aux clients maritime enterprise Europe",
    ],
}

exp['open_ocean']['bullets']['p2']['t4'] = {
    'en': [
        "Led 12-person product team (engineers, data scientists, web devs) serving Naval Group, RTE, Doris Engineering",
        "Grew SaaS revenue through enterprise framework contracts; delivered to offshore wind and maritime clients",
        "Raised €2M from institutional investors — successful acquisition by Artelia (2019)",
    ],
    'fr': [
        "Dirigé une équipe de 12 personnes livrant à Naval Group, RTE (contrat cadre) et Doris Engineering",
        "Croissance SaaS via contrats cadres enterprise ; livraison éolien offshore et industrie maritime",
        "Levée 2 M€ institutionnels — cession à Artelia (2019)",
    ],
}

# ─────────────────────────────────────────────────────────────
# 4. P2 × T5 — AI Lab/Startup (Anthropic, Mistral type)
#    → velocity, LLM expertise, team leadership, product innovation
# ─────────────────────────────────────────────────────────────

exp['blue_green']['bullets']['p2']['t5'] = {
    'en': [
        "Shipped production GenAI systems for enterprise clients (EnBW France, Valorem) — zero to production in under 3 months",
        "Built BlueWind Companion v2.2: LLM-native architecture (MCP, pgvector, Pydantic AI agents) — live and battle-tested",
        "Delivered GenAI literacy programs and adoption workshops for energy sector development teams",
    ],
    'fr': [
        "Déployé des systèmes GenAI en production pour EnBW France et Valorem — zéro à prod en moins de 3 mois",
        "BlueWind Companion v2.2 : architecture LLM-native (MCP, pgvector, agents Pydantic AI) — live et éprouvé",
        "Programmes GenAI et ateliers d'adoption pour équipes de développement de projets d'énergies renouvelables",
    ],
}

exp['artelia']['bullets']['p2']['t5'] = {
    'en': [
        "Business Development & Project Director — grew offshore wind data portfolio 15% YOY at Artelia (6,000-person group)",
        "Full P&L responsibility: enterprise procurement, C-level client engagement, long-term framework contracts",
        "Contributed to marine data platform product roadmap: engineering strategy at group level",
    ],
    'fr': [
        "Directeur BD & Projets — portefeuille éolien offshore +15%/an chez Artelia (groupe 6 000 personnes)",
        "Responsabilité P&L complète : procurement enterprise, C-level, contrats cadres long terme",
        "Contribution à la feuille de route produit data marine : stratégie technique au niveau groupe",
    ],
}

exp['open_ocean']['bullets']['p2']['t5'] = {
    'en': [
        "Co-founded and led a 12-person team — built a SaaS data platform, raised €2M from institutional VCs, achieved exit",
        "Clients: Naval Group (ex-DCNS), RTE (framework contract), Doris Engineering — maritime and energy industries",
        "Scaled from prototype to industrial deployment; acquired by Artelia (2019) — successful entrepreneurial exit",
    ],
    'fr': [
        "Co-fondé et dirigé une équipe de 12 — plateforme SaaS, 2 M€ levés auprès d'institutionnels, exit réalisé",
        "Clients : Naval Group (ex-DCNS), RTE (contrat cadre), Doris Engineering — secteurs maritime et énergie",
        "Scale prototype → déploiement industriel ; cédé à Artelia (2019) — exit entrepreneurial réussi",
    ],
}

# ─────────────────────────────────────────────────────────────
# 5. P3 × T1 — Scale-up industriel
#    → architecture at scale, technical ownership, product roadmap
# ─────────────────────────────────────────────────────────────

exp['blue_green']['bullets']['p3']['t1'] = {
    'en': [
        "Architected and deployed production AI stack for energy industry: Next.js, FastAPI, Supabase pgvector, Pydantic AI agents",
        "Shipped BlueWind Companion v2.2 (22,800-chunk RAG, 5 specialized AI agents) — full technical ownership, live in France",
        "Designed technical roadmap for AI product suite: Edifice (building diagnostics), WattCast (price forecasting), EnerCast",
    ],
    'fr': [
        "Architecture et déploiement du stack IA production pour l'énergie : Next.js, FastAPI, Supabase pgvector, agents Pydantic AI",
        "Livré BlueWind Companion v2.2 (RAG 22 800 chunks, 5 agents IA) — propriété technique complète, live en France",
        "Roadmap produit IA : Edifice (diagnostics bâtiment), WattCast (prévision prix), EnerCast (ML énergie)",
    ],
}

exp['artelia']['bullets']['p3']['t1'] = {
    'en': [
        "Directed marine data intelligence product strategy within Artelia (6,000-person engineering group) — London-based",
        "Full P&L ownership for renewables & energy BU: revenue targets, team management, C-level client engagement",
        "Managed delivery for SBM Offshore, Nexans, Alcatel Submarine Networks, Cadeler — long-term framework clients",
    ],
    'fr': [
        "Direction stratégie produit data marine au sein du groupe Artelia (6 000 personnes) — base Londres",
        "Responsabilité P&L, BU renouvelables & énergie : objectifs revenus, management équipe, engagement C-level",
        "Livraison pour SBM Offshore, Nexans, Alcatel Submarine Networks, Cadeler — clients en contrat cadre long terme",
    ],
}

exp['open_ocean']['bullets']['p3']['t1'] = {
    'en': [
        "CTO & Co-founder: architected and scaled marine data SaaS from prototype to multi-client industrial deployment",
        "Led 12-person product team: roadmap, agile delivery, clients Naval Group, SBM Offshore, RTE (framework contract)",
        "Raised €2M from institutional investors (Seventure Partners, Cap Décisif/FNA) — acquired by Artelia (2019)",
    ],
    'fr': [
        "CTO & Co-fondateur : architecture et scale du SaaS data marine du prototype au déploiement industriel multi-clients",
        "Équipe de 12 personnes : roadmap produit, delivery agile, clients Naval Group, SBM Offshore, RTE (cadre)",
        "Levée 2 M€ institutionnels (Seventure Partners, Cap Décisif) — cession à Artelia (2019)",
    ],
}

# ─────────────────────────────────────────────────────────────
# 6. P3 × T5 — AI Lab/Startup CTO (Anthropic, Mistral type)
#    → product velocity, LLM depth, team building, exit story
# ─────────────────────────────────────────────────────────────

exp['blue_green']['bullets']['p3']['t5'] = {
    'en': [
        "Built and shipped production LLM systems (BlueWind v2.2) in under 3 months: RAG, MCP, Pydantic AI — battle-tested",
        "Full-stack technical ownership: architecture, stack selection, core development, production deployment — end to end",
        "Running WattCast (ML price forecasting), EnerCast (ML framework), Edifice (AI diagnostics) simultaneously in production",
    ],
    'fr': [
        "Systèmes LLM en production livrés en moins de 3 mois (BlueWind v2.2) : RAG, MCP, agents Pydantic AI — éprouvés",
        "Propriété technique complète : architecture, stack, développement cœur, déploiement prod — de bout en bout",
        "WattCast (prévision prix ML), EnerCast (framework ML), Edifice (diagnostics IA) en production simultanément",
    ],
}

exp['artelia']['bullets']['p3']['t5'] = {
    'en': [
        "Led product direction for marine data intelligence platform within Artelia (6,000-person engineering group)",
        "Full P&L ownership, renewables & energy BU: revenue targets, team management, C-level client engagement",
        "Drove SaaS adaptation strategy for maritime industry: coordinated R&D, product, and commercial functions",
    ],
    'fr': [
        "Direction produit de la plateforme data marine chez Artelia — groupe ingénierie 6 000 personnes",
        "Responsabilité P&L, BU renouvelables & énergie : objectifs revenus, management équipe, engagement C-level",
        "Stratégie d'adaptation SaaS pour l'industrie maritime : coordination R&D, produit et commercial",
    ],
}

exp['open_ocean']['bullets']['p3']['t5'] = {
    'en': [
        "Co-founded and scaled a 12-person team: hired engineers, data scientists, web devs — SaaS from zero to multi-client",
        "Raised €2M from institutional VCs (Seventure Partners, Cap Décisif/FNA) — profitable, acquired by Artelia (2019)",
        "Clients Naval Group (ex-DCNS), RTE (framework contract), Doris Engineering — full commercial + technical ownership",
    ],
    'fr': [
        "Co-fondé et scalé une équipe de 12 : ingénieurs, data scientists, web — SaaS de zéro à multi-clients",
        "Levée 2 M€ auprès d'institutionnels (Seventure Partners, Cap Décisif/FNA) — rentable, cédé à Artelia (2019)",
        "Clients Naval Group (ex-DCNS), RTE (contrat cadre), Doris Engineering — propriété commerciale + technique complète",
    ],
}

# ─────────────────────────────────────────────────────────────
# WRITE BACK
# ─────────────────────────────────────────────────────────────

with open(DATA, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("cv-master.json updated successfully.")

# Quick sanity check — count bullets per profile/cell
for company in ['blue_green', 'artelia', 'open_ocean']:
    job = exp[company]
    for profile in ['p2', 'p3']:
        cells = list(job['bullets'][profile].keys())
        print(f"  {company}/{profile}: {cells}")
