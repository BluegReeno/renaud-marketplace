# PLAN — Agent « MySpy » (suivi personnel hebdomadaire)

> **Statut** : plan à valider par Renaud avant implémentation.
> **Portée** : 2 work packages indépendants — **WP1** une base de connaissance méthodologique (bundle OKF, comme `OW-KWiki-llm`) et **WP2** le skill Claude Code + la mécanique de séance côté hal (projet/interactions/tâches, zéro nouvelle table).

---

## 0. Décisions de cadrage (tranchées avec Renaud)

- **Isolation des données de séance** : workspace `renaud` dans hal (déjà existant, déjà séparé de `blue-green`, déjà utilisé pour des tâches personnelles — cf. `log-cr`).
- **Focus des séances** : traumas/histoire personnelle **et** problèmes/blocages actuels (priorité), analyse de situations en complément.
- **Cadence** : hebdomadaire.
- **Le vrai risque à couvrir n'est pas la crise psychologique** (Renaud est clair là-dessus) **mais la lassitude** : qu'après 10 séances les échanges tournent en rond et qu'il arrête de venir. Conséquence directe : investir dans une base de connaissance suffisamment riche et variée (WP1) plutôt que 3 fiches statiques — c'est la meilleure garantie contre la répétition, bien avant tout mécanisme technique.
- **WP1 et WP2 sont découplés** : WP2 (skill + séances) peut démarrer avec un bundle WP1 encore minimal (fallback générique) et s'enrichir au fil du temps sans redéploiement du skill.

---

## Partie A — WP1 : Base de connaissance méthodologique (bundle OKF)

### A.1 Précédent direct : `OW-KWiki-llm`

Renaud a déjà un projet qui fait exactement ça pour un autre domaine (l'éolien offshore) : `/Users/renaud/Projects/OW-KWiki-llm`. C'est une implémentation concrète de l'**Open Knowledge Format** (OKF, spec Google Cloud) appliquée à un "LLM wiki" (idée d'Andrej Karpathy citée dans son propre README) :

```
bundles/offshore-wind/
├── index.md              table des matières (frontmatter okf_version, sections, convention de tags)
├── log.md                journal daté des mises à jour
├── okf-cli.py            CLI Python stdlib-only : index / read <page> / find "<requête>"
├── companies/ projects/   pages-concept : un fichier .md par entité/thème
├── tenders/ technology/
├── policy/ digests/       digests datés générés par le pipeline d'ingestion
└── pipeline/              poll_rss.py + wiki_agent.py : agent curateur automatique
```

Chaque page suit un gabarit strict (vérifié sur `technology/power-to-x.md`, `fixed-bottom-foundations.md`, etc.) :
```markdown
---
type: Technology
title: ...
description: ...
tags: [tag1, tag2, ...]
timestamp: 2026-07-02T00:00:00Z
---
# Overview
...
# <sections thématiques>
...
# Cross-References
- [autre-page.md](autre-page.md) — pourquoi c'est lié
# Citations
- [Titre de la source (éditeur)](url)
```

`okf-cli.py` est **dependency-free** (stdlib Python only), s'exécute depuis n'importe où (il opère toujours sur son propre dossier), et fait une recherche par mots-clés classée (`find`) — **pas d'embeddings, pas de pgvector**. C'est la preuve concrète que la recherche structurée suffit pour ce type de corpus (confirme ce qu'on avait anticipé en §A.5/discussion précédente).

**Décision : répliquer ce pattern tel quel pour MySpy plutôt que d'inventer autre chose.**

### A.2 Nouveau bundle : emplacement et structure

Nouveau dépôt dédié (privé, hors marketplace), par exemple `/Users/renaud/Projects/myspy-kwiki` (nom à ajuster librement) :

```
myspy-kwiki/
├── index.md
├── log.md
├── okf-cli.py                 copié tel quel depuis OW-KWiki-llm (générique, aucune dépendance offshore-wind)
├── cbt/                        distorsions cognitives + techniques (colonnes de pensées, questionnement socratique, expériences comportementales)
├── sfbt/                       familles de questions (miracle, échelle, exception, coping, relationnelles)
├── ifs-schema-light/           archétypes de protecteurs (IFS, surface uniquement) + 18 schémas de Young (reconnaissance uniquement) + page dédiée aux limites explicites
├── engagement/                 techniques de variété/nouveauté (narrative therapy, ACT/valeurs, rétrospectives) — nourrit l'anti-répétition (§B.3)
├── digests/                    si pipeline d'enrichissement activé (§A.6)
└── pipeline/                   optionnel, cf. §A.6
```

S'ouvre aussi comme vault Obsidian (comme `OW-KWiki-llm`), pour parcourir/naviguer visuellement en dehors de Claude Code si besoin.

### A.3 Taxonomie de contenu (point de départ, extensible)

| Dossier | `type` frontmatter | Exemples de pages |
|---|---|---|
| `cbt/` | `Distortion`, `Technique` | `catastrophizing.md`, `all-or-nothing.md`, `thought-record.md`, `socratic-questioning.md`, `behavioral-experiment.md` |
| `sfbt/` | `Question` | `miracle-question.md`, `scaling-question.md`, `exception-finding.md`, `coping-question.md` |
| `ifs-schema-light/` | `Pattern` | `protector-critic.md`, `protector-avoidant.md`, `protector-pleaser.md`, `schema-abandonment.md`, ... (18 schémas Young), `limites-explicites.md` (ce qu'on ne fait JAMAIS — imagery rescripting, reparenting, travail direct avec les Exilés) |
| `engagement/` | `Technique` | `narrative-reflection.md`, `values-clarification-act.md`, `retrospective-format.md` — variété délibérée, cf. §B.3 |

Chaque page = une synthèse originale (pas de texte sous copyright reproduit tel quel), avec sections `Cross-References` et `Citations` vers les vraies sources (livres, papers, articles).

### A.4 Sourcing — ce qui est permis, et comment on travaille

Rappel du cadrage déjà validé avec Renaud : ce bundle est privé, non commercialisé — Renaud peut acheter les livres/PDF et en extraire le contenu (`docling`) pour son usage personnel. Ceci dit, même en usage privé, la bonne pratique reste une **synthèse dans nos propres mots**, citations courtes et attribuées plutôt que des chapitres entiers recopiés — c'est aussi ce qui rend les pages effectivement utiles pour un agent (une synthèse structurée se requête mieux qu'un pavé de texte brut).

Process concret par thème :
1. **Sources déjà identifiées par la recherche précédente** (web, résumés cliniques publics — Psychology Tools, De Jong & Berg via résumés académiques, IFS Institute, etc.) → point de départ immédiat, pages rédigeables dès maintenant.
2. **Livres achetés par Renaud** (Burns *Feeling Good*, J. Beck *CBT: Basics and Beyond*, De Jong & Berg *Interviewing for Solutions*, Schwartz *No Bad Parts*, Young & Klosko *Reinventing Your Life*) → extraction `docling`, puis travail de synthèse assisté (moi + Renaud, en session) pour produire les pages OKF — pas une extraction automatique verbatim.
3. **Articles de recherche / livres blancs / blogs** trouvés en marge (ex. papers cités dans la recherche précédente : DMT-CBT, COCOA, MIND-SAFE pour la partie ingénierie ; papers cliniques IFS/Schema pour la partie preuve) → pages `Citations` sourcées directement.

### A.5 Outillage : réutiliser `okf-cli.py` tel quel

Aucun développement nécessaire — le script est générique (aucune référence à l'éolien offshore dans sa logique), il suffit de le copier dans `myspy-kwiki/`. Commandes disponibles immédiatement :
```bash
python3 okf-cli.py index                     # table des matières
python3 okf-cli.py find "catastrophisme"      # recherche mots-clés classée
python3 okf-cli.py read cbt/thought-record    # lire une page
```

### A.6 Enrichissement continu (optionnel, différé)

`OW-KWiki-llm` garde son bundle à jour via `pipeline/` : `poll_rss.py` (cron) + `wiki_agent.py` (agent curateur `claude -p`, sandboxé Read/Write/Edit/Glob/Grep seulement). Pour un flux RSS public (offshoreWIND.biz), c'est direct. Pour des newsletters psy/dev perso (pas toujours en RSS), Renaud a déjà un connecteur Gmail personnel opérationnel (`gmail-mcp-perso`, cf. mémoire projet) — **plus simple de router les newsletters vers un label Gmail dédié et faire lire ce label périodiquement par un agent curateur**, plutôt que remonter un compte AgentMail (l'historique `OW-KWiki-llm` déconseille explicitement AgentMail quand une alternative plus simple existe — cf. `pipeline/README.md`, section « Why not AgentMail »).

**Hors scope v1** : à activer seulement une fois le bundle initial peuplé et le besoin d'enrichissement continu confirmé à l'usage.

### A.7 Étapes WP1

1. [ ] Créer le dépôt `myspy-kwiki` (structure §A.2), copier `okf-cli.py` depuis `OW-KWiki-llm`.
2. [ ] Rédiger `index.md` (sections, convention de tags) sur le modèle de `bundles/offshore-wind/index.md`.
3. [ ] Rédiger un premier lot de pages **à partir des sources déjà collectées** (recherche web précédente) : les techniques CBT/SFBT cœur + les schémas/parts en usage « léger » + la page `limites-explicites.md`.
4. [ ] Renaud acquiert et fait passer au moins 1-2 livres via `docling` (CBT + SFBT en priorité, méthodes cœur) ; séance de travail commune pour transformer l'extraction en pages OKF.
5. [ ] Mesurer la taille réelle du corpus après ce premier lot — decide si `find` (mots-clés) reste suffisant ou si un besoin de recherche plus fine émerge (cf. limites §D).
6. [ ] (Optionnel) Mettre en place le pipeline d'enrichissement via Gmail (§A.6).

---

## Partie B — WP2 : Skill + séances (hal)

### B.1 Architecture des données de séance — réutilisation du modèle CRM existant, zéro nouvelle table

Vérification faite en conditions réelles (`list_projects(workspace_slug='renaud')`) : il existe déjà un précédent exact — un projet `IT Improvement` (`kind: "internal"`, `stage: "En cours"`, `description` en texte libre servant de synthèse vivante) tournant dans le workspace `renaud`. Pattern répliqué pour MySpy :

| Besoin | Construct CRM réutilisé | Tools |
|---|---|---|
| **Profil vivant** (patterns connus, objectifs de fond, techniques récemment utilisées — §B.3) | `halcrm_projects.description`, projet unique `kind='internal'` | `create_project` (une fois), `update_project`, `list_projects` |
| **Journal de séance** (compte-rendu + transcript) | `halcrm_interactions` liée au projet | `log_interaction` |
| **Action engagée pour la semaine suivante** | `halcrm_tasks` liée au projet | `create_task`, `list_tasks`, `update_task_status` |

Stages `kind='internal'` (vérifié via `list_stages`) : actifs `Backlog / En cours / Livré`, terminaux `Terminé / Annulé`. Le projet MySpy reste en `En cours` en continu.

**Contrainte réelle identifiée** : `log_interaction` existe en écriture, mais **aucun tool `list_interactions`/`get_interactions`** n'existe côté hal-mcp. La continuité réelle d'une séance à l'autre repose donc sur `halcrm_projects.description` (profil vivant) + `halcrm_tasks` (action en cours) — pas sur une relecture des interactions passées. C'est cohérent avec l'usage CRM actuel (journal d'audit, pas mémoire de travail). Amélioration possible plus tard si le besoin se confirme (§C).

**Seule modification DB réelle** :
```sql
update halcrm_workspaces
set allowed_tags = array_append(allowed_tags, 'myspy')
where workspace_slug = 'renaud'
  and not ('myspy' = any(allowed_tags));
```
(`create_project`/`create_task` valident leurs `tags` contre `allowed_tags`.) À vérifier aussi : le rôle `subcontractor` de Renaud sur `workspace_members` pour `renaud` autorise bien l'écriture.

**Convention de séance :**
1. `list_projects(workspace_slug='renaud', tags=['myspy'])` → profil vivant.
2. `list_tasks(project_id=..., status='todo')` → action de la semaine précédente.
3. Conduire la séance (§B.2), en interrogeant le bundle `myspy-kwiki` (WP1) via `okf-cli.py find`/`read` (Bash) pour piocher les techniques/questions.
4. `log_interaction(...)` — compte-rendu + transcript.
5. `update_task_status` + `create_task(...)` pour la nouvelle action.
6. `update_project(description=...)` si le profil a évolué.

### B.2 Le skill `myspy`

```
plugins/myspy/
├── .claude-plugin/plugin.json     (version 0.1.0)
└── skills/myspy/SKILL.md          (version 0.1.0 — trame de séance + garde-fous, reste court)
```
+ entrée dans `.claude-plugin/marketplace.json`, bump version top-level.

**Triggers** : « séance MySpy », « check-in hebdo », « on fait ma séance », « point perso de la semaine ».

**`allowed-tools`** :
```
mcp__hal-mcp__list_projects mcp__hal-mcp__update_project mcp__hal-mcp__log_interaction
mcp__hal-mcp__list_tasks mcp__hal-mcp__create_task mcp__hal-mcp__update_task_status
Bash
```
(`Bash` uniquement pour appeler `okf-cli.py` sur le bundle `myspy-kwiki` — pas d'accès aux tools CRM business.)

**⚠️ Point d'attention explicite** : `okf-cli.py` lit un dossier local sur le disque de Renaud. Ça marche parfaitement en Claude Code local (le cas d'usage visé, séance hebdo à son poste), mais **ne fonctionnerait pas depuis claude.ai/mobile** (pas d'accès filesystem à ce chemin) — contrairement aux tools hal qui, eux, marchent partout. Si l'usage mobile devient un besoin réel, il faudra reconsidérer (ex. synchroniser une partie du bundle vers hal). Non bloquant pour v1 si les séances se font en Claude Code local.

**Trame de séance** (inchangée sur le fond) :
- **Ouverture (SFBT, ~10 min)** : lire profil vivant + tâche de la semaine précédente ; question d'échelle ; question d'exception ; suivi de l'action engagée.
- **Corps (~30-35 min)**, alterné selon focus déclaré : CBT (blocage actuel : situation → émotion → pensée automatique → distorsion → question socratique → reformulation) ou IFS/Schema léger (histoire personnelle : repérage de parts/schémas, sans reconstruction de la scène d'origine) — technique piochée dans `myspy-kwiki` en excluant celles récemment utilisées (§B.3).
- **Clôture (SFBT, ~10 min)** : question miracle allégée, une seule action pour la semaine, auto-évaluation (0-10), écriture (`log_interaction` + `create_task` + `update_project` si pattern nouveau).

**Garde-fous (non négociables, délibérément légers)** :
1. Détection de signaux de crise (idéation suicidaire, automutilation, dissociation sévère) → interruption immédiate, rappel du **3114**, recommandation de contact professionnel.
2. Interdiction explicite : pas d'imagery rescripting, pas de reparenting, pas de travail direct avec des Exilés IFS, pas de reconstruction détaillée de souvenirs traumatiques.
3. Pas de diagnostic clinique.
4. Anti-sycophantie : capacité à questionner/nuancer, pas seulement valider.

### B.3 Anti-répétition — la vraie priorité produit

1. **Rotation forcée** : le profil vivant (`description`) garde une liste courte des dernières techniques utilisées (slugs de pages `myspy-kwiki`) ; le skill les exclut de la sélection à chaque séance — d'où l'intérêt réel de WP1 (plus le bundle est varié, plus la rotation a de marge).
2. **Nouveauté périodique délibérée** : toutes les 6-8 séances, piocher dans `engagement/` (narrative therapy, valeurs ACT, format rétrospective) plutôt que CBT/SFBT classique.
3. **Méta-check explicite** : toutes les 8-10 séances, une question dédiée en clôture — « Est-ce que ces séances t'apportent encore quelque chose ? Qu'est-ce qui te manque ou t'ennuie ? » — pour détecter la lassitude avant qu'elle ne se traduise par un rendez-vous manqué.

### B.4 Étapes WP2

1. [ ] Confirmer le rôle d'écriture de Renaud sur `workspace_members` (workspace `renaud`).
2. [ ] `UPDATE halcrm_workspaces SET allowed_tags = array_append(allowed_tags, 'myspy') ...`.
3. [ ] `create_project(...)` — initialisation du projet MySpy.
4. [ ] Créer `plugins/myspy/.claude-plugin/plugin.json` + `SKILL.md` (trame + garde-fous + anti-répétition + appel `okf-cli.py`).
5. [ ] Ajouter l'entrée `myspy` dans `.claude-plugin/marketplace.json`, bump version top-level.
6. [ ] Tester une séance à blanc (dry-run), avec le bundle WP1 même partiellement peuplé — vérifier le cycle complet lecture profil/tâche/bundle → séance → écriture interaction/tâche/profil.

---

## C. État de l'art et méthodologies retenues (contexte partagé WP1/WP2)

### C.1 État de l'art IA-coach/psy (2023-2026)

- Les outils cliniques encadrés (Woebot, Wysa — TCC, FDA Breakthrough Device) ont des preuves solides. L'essai randomisé **Therabot** (Dartmouth, *NEJM AI*, 2025) montre des bénéfices réels (-51 % symptômes dépressifs sur 4 semaines) **mais avec supervision clinique humaine en veille** — aucun agent IA générique n'est prêt à opérer en autonomie totale sur la santé mentale.
- Une étude **Stanford** (FAccT 2025) documente des défaillances sérieuses des chatbots « thérapeutes » génériques : ~20 % de réponses inadéquates face à une idéation suicidaire simulée, biais de stigmatisation, sycophantie.
- L'**APA** a publié un *Health Advisory* (nov. 2025) formalisant ces risques.
- **Conséquence pour MySpy** : garde-fous minimaux non négociables (§B.2), volontairement légers vu le profil de risque réel exprimé par Renaud (§0).

### C.2 Méthodologies retenues

| Méthode | Rôle | Pourquoi |
|---|---|---|
| **SFBT** | Colonne vertébrale de chaque séance | Conçue nativement pour le format court/hebdo, haute adéquation solo, preuve solide, quasi aucun risque. |
| **CBT** | Corps de séance, blocages actuels | Base de preuve la plus large de toutes les psychothérapies (socle de Woebot/Wysa/Therabot). Mécanisable en texte. |
| **IFS (léger) / Schema Therapy (léger)** | Corps de séance, histoire personnelle, **surface uniquement** | Repérage de patterns sans jamais de travail de reconstruction traumatique — la littérature est unanime sur le risque de re-traumatisation/faux souvenirs sans praticien formé. |

**Principe directeur** : MySpy est un outil de réflexion structurée et de suivi, pas une thérapie de substitution.

### C.3 Architecture mémoire — validée par la littérature produit

Recherche complémentaire (MemGPT, LangGraph, papers DMT-CBT/COCOA, retours produit Replika/Mindsera/Rosebud/Daylio) : consensus sur un modèle à **deux couches** — logs de séance append-only horodatés (`log_interaction`) + profil consolidé mutable (`halcrm_projects.description`), réinjecté en contexte à chaque séance. C'est exactement l'architecture WP2 (§B.1). Second point de convergence : la connaissance méthodologique doit être une bibliothèque de référence consultée à la demande plutôt qu'un bloc statique — exactement le rôle de WP1 (bundle OKF), confirmé indépendamment par le pattern déjà utilisé dans `OW-KWiki-llm`.

---

## D. Améliorations futures (non bloquantes)

- **`list_interactions`/`get_interactions`** sur hal-mcp, si le besoin de relire le détail de séances anciennes se fait sentir (§B.1).
- **Synthèse périodique (mensuelle/trimestrielle)** façon Mindsera/Rosebud — dépend du point précédent.
- **Recherche plus fine que `okf-cli.py find`** (embeddings/RAG) sur `myspy-kwiki` — seulement si le corpus grossit au point que la recherche par mots-clés ne suffit plus. Pas anticipé : `OW-KWiki-llm` fonctionne bien avec `find` seul à ce jour.
- **Pipeline d'enrichissement continu** via newsletters (Gmail, §A.6).
- **Accès mobile/claude.ai** au bundle `myspy-kwiki` si le besoin de faire une séance hors du poste de Renaud se confirme (§B.2).

## E. Limites à garder en tête

- Aucun mécanisme technique de détection de crise (pas de classifieur) — repose sur l'attention du modèle, cadrée par les instructions du skill.
- Le skill (WP2, `plugins/myspy/`) peut rester dans le dépôt marketplace public sans risque : aucune donnée personnelle, aucun contenu sous copyright. Le bundle `myspy-kwiki` (WP1) et les données de séance (hal) restent strictement privés.
- MySpy est un outil de suivi personnel, pas un dispositif médical.
