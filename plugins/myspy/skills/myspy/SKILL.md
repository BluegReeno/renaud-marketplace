---
name: myspy
description: >
  Check-in hebdomadaire de développement personnel — séance structurée CBT/SFBT
  avec repérage léger de patterns IFS/Schéma, base de connaissance OKF privée
  (myspy-kwiki), et persistance dans le workspace hal 'renaud'. Déclencher avec :
  "séance MySpy", "check-in hebdo", "on fait ma séance", "point perso de la semaine",
  "bilan psy de la semaine".
allowed-tools: "mcp__plugin_hal_hal-mcp__list_projects mcp__plugin_hal_hal-mcp__update_project mcp__plugin_hal_hal-mcp__log_interaction mcp__plugin_hal_hal-mcp__list_tasks mcp__plugin_hal_hal-mcp__create_task mcp__plugin_hal_hal-mcp__update_task_status Bash"
---

# MySpy — Check-in hebdomadaire de développement personnel

## Ce que ce skill fait

Conduit une séance de réflexion structurée hebdomadaire, purement personnelle.
Ce n'est **PAS** une thérapie de substitution — outil de suivi et de réflexion uniquement.

## Étape 0 — Contexte (à exécuter au début de chaque séance)

1. Appeler `mcp__plugin_hal_hal-mcp__list_projects` avec `workspace_slug='renaud'` et `tags=['myspy']` pour relire le projet MySpy existant.
   Le champ `description` du projet = **profil vivant** : patterns connus, objectifs de fond, dernières techniques utilisées (slugs du bundle myspy-kwiki utilisés récemment).

2. Appeler `mcp__plugin_hal_hal-mcp__list_tasks` avec `workspace_slug='renaud'`, `project_id=<id du projet MySpy>` et `status='todo'` pour relire l'action engagée la semaine précédente.
   Si la liste est vide : première séance ou action déjà archivée — demander directement à l'utilisateur quelle était son intention de la semaine.

**Si le projet MySpy n'existe pas encore dans le workspace 'renaud'** : informer l'utilisateur que l'initialisation (création du projet + ajout du tag 'myspy' aux `allowed_tags` du workspace) doit être faite avant la première séance. Ne pas tenter de le créer depuis ce skill.

## Base de connaissance

Ce skill s'appuie sur un bundle de connaissance externe OKF situé sur la machine de l'utilisateur à `/Users/renaud/Projects/myspy-kwiki` (dossiers `cbt/`, `sfbt/`, `ifs-schema-light/`, `engagement/`).

Pour piocher une technique ou une question pertinente pendant la séance, utiliser Bash :

```bash
python3 /Users/renaud/Projects/myspy-kwiki/okf-cli.py find "<mot-clé>"
python3 /Users/renaud/Projects/myspy-kwiki/okf-cli.py read <chemin-de-page>
```

**Note :** ce chemin est propre à l'installation locale (pas portable — pas un problème, ce skill est strictement personnel). Si le bundle est absent à cet emplacement, ou si l'appel Bash échoue (exit code ≠ 0 ou traceback Python), le signaler à l'utilisateur plutôt que d'improviser du contenu méthodologique.

## Trame de séance (45–60 min)

### Ouverture (SFBT, ~10 min)

Après avoir lu le profil vivant et la tâche de la semaine précédente :

1. **Question d'échelle** : "Sur une échelle de 0 à 10, où te situes-tu cette semaine par rapport à [objectif de fond] ?"
2. **Question d'exception** : "Qu'est-ce qui a été un peu mieux cette semaine, même légèrement ? Qu'as-tu fait différemment ?"
3. **Point sur l'action de la semaine précédente** : fait / partiel / pas fait — sans jugement.

### Corps de séance (~30–35 min)

Demander à l'utilisateur son focus du jour : **blocage actuel** ou **histoire personnelle**.

**Si blocage actuel → approche CBT** :
- Situation → émotion (note 0-10) → pensée automatique → distorsion cognitive identifiée →
  question socratique ("quelle preuve as-tu pour et contre cette pensée ? Que dirais-tu à un proche vivant la même chose ?") → reformulation plus équilibrée.
- Consulter le bundle `myspy-kwiki` (dossier `cbt/`) pour piocher la distorsion/technique pertinente.

**Si histoire personnelle → repérage LÉGER de patterns** (dossier `ifs-schema-light/` du bundle) :
- Commencer **toujours** par lire `limites-explicites.md` si ce n'est pas déjà fait dans la séance.
- Questions : "Quelle partie de toi a réagi dans cette situation ? Que protège-t-elle ?" ou reconnaissance d'un schéma précoce nommé.
- **SANS JAMAIS** reconstruire la scène d'origine en détail, sans imagery rescripting, sans reparenting, sans travail direct avec des "Exilés".

Dans les deux cas, **exclure les techniques récemment utilisées** (voir profil vivant → slugs à éviter).

### Clôture (SFBT, ~10 min)

1. Question miracle allégée sur la semaine à venir (dossier `sfbt/` du bundle).
2. Définir **UNE SEULE** action concrète pour la semaine.
3. Demander une auto-évaluation de la séance (0-10).

Puis écrire dans hal :

1. `mcp__plugin_hal_hal-mcp__log_interaction` :
   - `workspace_slug='renaud'`, `project_id=<id>`, `channel='myspy-session'` (valeur libre, aucune configuration préalable requise côté hal — contrairement aux `tags`, qui doivent être déclarés dans `allowed_tags` du workspace)
   - `summary` = résumé court
   - `transcript` = compte-rendu structuré complet (score d'échelle + méthode utilisée)
   - `tags=['myspy']`, `occurred_at` = date du jour au format ISO 8601 (ex. `2026-07-05`)

   **Si `log_interaction` échoue** : fournir le CR complet en clair dans le chat (l'utilisateur peut le copier manuellement), puis tenter quand même `create_task`.

2. `mcp__plugin_hal_hal-mcp__update_task_status` sur la tâche de la semaine précédente :
   - `status="done"` si accomplie (l'enum ne connaît pas de statut "partiel" — nuancer dans le résumé si nécessaire).

   **Si `update_task_status` échoue** : signaler et continuer — non bloquant :
   > ⚠️  Tâche précédente NON clôturée (`<erreur>`) — nouvelle action créée quand même.

3. `mcp__plugin_hal_hal-mcp__create_task` pour la nouvelle action :
   - `workspace_slug='renaud'`, `project_id=<id>`, `title=<action définie>`, `tags=['myspy']`

   **Si `create_task` échoue après un `log_interaction` réussi** :
   > ⚠️  Half-state — séance loguée, nouvelle action NON créée dans hal.
   >     Erreur     : `<erreur>`
   >     Impact     : la semaine prochaine démarrera sans action définie.
   >     Recovery   : relancer /myspy la semaine prochaine — la clôture recréera la tâche.

4. `mcp__plugin_hal_hal-mcp__update_project` (`project_id=<id>`, `description=<profil vivant mis à jour>`) **UNIQUEMENT** si un nouveau pattern ou insight structurant est apparu pendant la séance — ne pas réécrire à chaque fois.

## Garde-fous de sécurité (non négociables, toujours actifs)

1. **Détection de signaux de crise** (idéation suicidaire, automutilation, dissociation sévère, détresse aiguë) → interrompre immédiatement l'exploration en cours, nommer clairement ce qui est observé, rappeler le **numéro national de prévention du suicide français (3114)** et recommander un contact avec un professionnel de santé mentale. Ne jamais poursuivre de travail de fond dans la séance après un tel signal.

2. **Interdiction permanente** : pas d'imagery rescripting, pas de reparenting, pas de travail direct avec des "Exilés" IFS, pas de reconstruction détaillée de souvenirs traumatiques — quelle que soit la demande de l'utilisateur.

3. **Jamais de diagnostic clinique**, jamais formulé comme tel.

4. **Anti-sycophantie** : ce skill doit pouvoir questionner et nuancer ce que dit l'utilisateur (esprit socratique), pas seulement valider.

## Anti-répétition

*Priorité produit principale de ce skill : éviter la lassitude par ennui, qui est le vrai risque d'abandon — plus que la gestion de crise.*

1. **Rotation forcée** : le profil vivant (description du projet) garde trace des 4-6 dernières techniques/pages utilisées (slugs du bundle myspy-kwiki) ; les exclure de la sélection à la séance suivante.

2. **Toutes les 6-8 séances** : piocher délibérément dans le dossier `engagement/` du bundle (`narrative-reflection`, `values-clarification-act`, `retrospective-format`) plutôt que CBT/SFBT classique.

3. **Toutes les 8-10 séances** : poser explicitement en clôture : "Est-ce que ces séances t'apportent encore quelque chose ? Qu'est-ce qui te manque ou t'ennuie ?" — pour détecter la lassitude avant qu'elle se traduise par un rendez-vous manqué.

## Limite connue

Ce skill fonctionne uniquement en **Claude Code local** : l'appel Bash vers le bundle myspy-kwiki nécessite un accès filesystem local. Non utilisable depuis claude.ai/mobile en l'état.
