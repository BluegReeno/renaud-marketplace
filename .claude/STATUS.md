# STATUS — renaud-marketplace

Last updated: 2026-08-29

## Current Focus

### 2026-08-29 — lot D shipped: `#111` merged, briefing **0.16.2** / jobsearch **0.11.6** / mycoach **0.4.4**

[`#111`](https://github.com/BluegReeno/renaud-marketplace/issues/111) →
[PR #112](https://github.com/BluegReeno/renaud-marketplace/pull/112), merged as a **merge commit**
(`33ae4be`), 7/7 CI checks green including `Version sync + CHANGELOG`. The 6 files carry the
one-line pointer, each keeping its own formatting (bulleted for the five `briefing`/`jobsearch`
copies, plain paragraph for `mycoach`); `git grep 'hal://vocabulary' -- 'plugins/*.md'` returns
nothing. Top-level **0.6.31**. Ran in parallel with
[`bluegreen-marketplace#89`](https://github.com/BluegReeno/bluegreen-marketplace/issues/89) rather
than after it: the replacement wording was written verbatim into both issues, so the first run had
nothing left to teach the second. **`hal#135` is closed.**

⚠️ **The issue body had to be corrected before launching.** It asked for "a `CHANGELOG.md` entry",
which in this repo means the **single root** `CHANGELOG.md` grouped per plugin under
`## <plugin> <version>` — the shape `scripts/check_version_sync.sh` parses. There are no per-plugin
CHANGELOGs here (that is [`#102`](https://github.com/BluegReeno/renaud-marketplace/issues/102)), and
a run told only "add a CHANGELOG entry" creates three new files and fails the check. The correction
went into the **issue body**, not the run prompt: the prompt is consumed once, the issue is re-read
by every later run.

⚠️ **`skill-improve` still enforces the `version:` frontmatter of `SKILL.md`**, a field this repo
dropped (`CLAUDE.md` l.57), and its `verify-all-versions` node is told to repair divergence and
push. The run refused; the workflow did not. Filed as
[`archon-workflows#30`](https://github.com/BluegReeno/archon-workflows/issues/30). It also ignores
`scripts/release.sh`, which does the whole bump in one validated pass.

Left by hand: `/plugin marketplace update` in Cowork to confirm the bump is picked up.
`BLUEGREEN_MAP.md` (in `archon-workflows`) is up to date.

### 2026-08-28 — mycoach stops writing an about-to-be-rejected channel (shipped)

[PR #110](https://github.com/BluegReeno/renaud-marketplace/pull/110) closes
[#109](https://github.com/BluegReeno/renaud-marketplace/issues/109): `mycoach` writes
`channel='note'` instead of `channel='mycoach-session'`, and the SKILL.md line that described
`channel` as free text now says the opposite — it is a controlled vocabulary, like `tags`.

The value was never free text for much longer: [hal#124](https://github.com/BluegReeno/hal/issues/124)
gives `halcrm_interactions.channel` a controlled vocabulary (`email · call · meeting · whatsapp ·
linkedin · note · other`) in which `mycoach-session` is deliberately absent — it names a *kind of
session*, not a channel. Once hal deploys it, a `mycoach` still writing the old value fails its
`log_interaction` silently, week after week, because the skill degrades gracefully.

**Nothing is lost by the change, and it was measured rather than assumed.** The skill never reads
its own interactions (`allowed-tools` has no interaction-read tool, and `list_interactions` does
not exist server-side — hal#106). Two stronger retrieval keys already sit on all four historical
rows: `project_id` on "MyCoach — Développement personnel", and `tags = ["mycoach"]`, a conforming
tag. No replacement discriminator was invented.

Verified against the branch, not the run report: 4 files, +8/−4; `git grep mycoach-session` under
`plugins/` returns nothing; **zero `+version:` front-matter lines** — the known `skill-improve`
trap did not fire; `mycoach` 0.4.2 → 0.4.3 in both `plugin.json` and `marketplace.json`, top-level
0.6.29 → 0.6.30, CHANGELOG written, `check_version_sync.sh` exit 0, 7 CI checks green.

**Shipped and verified the same evening.** PR #110 merged as a real merge commit (`b29d87e`),
#109 auto-closed by its `closes` line. `/plugin marketplace update` then landed **`mycoach`
0.4.3** in the client — checked in the cache, not taken from the command's "3 plugins bumped":

```
~/.claude/plugins/cache/renaud-marketplace/mycoach/
  0.3.0/…/SKILL.md   channel='mycoach-session'   ← what the client had been running
  0.4.0/…/SKILL.md   channel='mycoach-session'
  0.4.3/…/SKILL.md   channel='note'              ✅
```

Only then was `hal#124` deployed (`hal-mcp` v67). A live probe against the deployed function now
refuses the old value — `log_interaction(renaud, channel="mycoach-session")` →
*Channel 'mycoach-session' not allowed* — while the shipped skill writes `note`. The ordering
bought exactly what it was meant to: zero broken sessions.

`archon-gc.sh --apply` removed the worktree, as it must for `skill-improve`: the environment is
registered as `archon/task-skill-improve-<ts>` while the work happens on `fix/skill-issue-109`, so
`archon complete` refuses with "branch has never been pushed to remote". `BLUEGREEN_MAP.md`
updated from `archon-workflows` (`mycoach` 0.4.3, top-level 0.6.30).

## In Progress

- [ ] Nothing on the vocabulary contract. 10 stale local `fix/skill-issue-*` branches could be
      swept whenever convenient.


### 2026-08-27 — gmail-mcp OAuth works from OpenClaw: GitHub Pages was never enabled

The consent page had been committed since June (`oauth/consent/index.html`) and the task file
claimed GitHub Pages was enabled on 2026-06-10. It was not — `gh api repos/BluegReeno/renaud-marketplace/pages`
returned 404. Every OAuth attempt therefore ended on GitHub's "There isn't a GitHub Pages site
here" *after* Supabase Auth had correctly issued an `authorization_id`, which reads like an
authentication failure and is not one.

Enabled on `main` / root. Verified rather than assumed: the page returns 200 with
`content-type: text/html`, the served SHA256 matches `oauth/consent/index.html` byte for byte,
and `/oauth/consent` → 301 → `/oauth/consent/` **preserves the query string**, so the
`authorization_id` survives the redirect. Flow confirmed end to end from OpenClaw.

The false checkbox is corrected in `.claude/tasks/_archive/gmail-mcp-oauth-github-pages.md`
(both OAuth task files are archived — the feature is done and validated end to end), and
`docs/mcp-server-supabase-edge.md` §10 now carries the one-command check instead of a
declarative "enable Pages" step. `servers/gmail-mcp/README.md` gained the two sections it was
missing: the `user` mode's dependency on the GitHub Pages consent page, and the one-mailbox
-per-deployment limit.

**Known limit, unchanged:** one deployment = one mailbox. `GOOGLE_REFRESH_TOKEN` is a single
project-level secret read at `servers/gmail-mcp/supabase/functions/gmail-mcp/index.ts:37`; the
bearer only authorises (`index.ts:357`), it never selects an account, and no tool takes an
`account` parameter. Two Supabase users would still share one inbox. Separating perso from pro
needs either a second deployment reading a distinct secret name (project-level secrets are
shared across a project's functions) or a per-account token map — the latter also requires
keying the `cachedToken` singleton (`index.ts:26`) per account.

### 2026-08-27 — the identity guard covers all four plugins, and reads the index instead of the tree

`#101` closed via [PR #104](https://github.com/BluegReeno/renaud-marketplace/pull/104).
`scripts/check_no_identity_literals.sh` now enumerates candidates with `git ls-files` rather
than walking the filesystem, and its `SCOPE` covers `briefing`, `mycoach`, `jobsearch` and
`improve` — it covered the first two.

Reading the index rather than the tree is what made widening the scope safe:
`plugins/jobsearch/data/contact.local.json` is gitignored by design, holds real contact data,
and a filesystem walk would have failed CI on a file that is deliberately never committed.
It is now a test case, so the property stays true.

Re-measured locally after the merge, not taken from the run's report: `test_check_no_identity_literals.sh`
→ **7 passed, 0 failed**; the guard itself → `OK: no identity literal in plugins/briefing
plugins/mycoach plugins/jobsearch plugins/improve`, exit 0.

Companion still open: `#89` — the values already readable in this repo's git history. This
issue stops new ones landing; `#89` is the purge, and needs a human-authorised force-push.

### ✅ Command Center — forme arrêtée le 2026-08-18 : c'est une page web, `#69` est close

**Lire `dashboards/command-center/README.md` en premier** — il porte la décision et la règle.
`#69` est **close** ; son corps garde l'historique et les mesures, mais il n'est plus le point
d'entrée. La décision, dans les mots de Renaud : *« on part sur une page web jusqu'à nouvel
ordre »* — un onglet par workspace + le daily log, les améliorations se font sur
`dashboards/command-center/index.html`. Le packaging dans le plugin est **reporté, pas
abandonné**, et ne se rouvre que sur décision explicite.

Vérifié le 2026-08-18 : **la page publiée est exactement le fichier du dépôt** (1174 lignes,
seul `</body></html>` ajouté par la plateforme). Le cycle éditer → commit → republier au même
chemin (donc même URL) est prouvé, pas supposé.

Un dashboard, un onglet par workspace hal, où cocher une tâche écrit dans `halcrm_tasks`. La
question de runtime qui bloquait depuis le 13 juillet a été tranchée le 2026-08-14, et le
producteur du daily log est corrigé : le travail est débloqué.

**Où est le code**

| | |
|---|---|
| **Source, ce dépôt** | `dashboards/command-center/index.html` — build 1 publié le 2026-08-14 : `https://claude.ai/code/artifact/a9aa59b2-bd53-4461-87bd-8fb62efd98f2`. Republier **le même chemin** conserve l'URL. |
| Tests hors-ligne | `tests/test_command_center_parser.js` — 17 vérifications sur le parseur du daily log (les deux formats) et la jointure par id. `node tests/test_command_center_parser.js` |
| Snapshot d'origine (figé) | `~/Documents/Claude/Artifacts/command-center-v2/index.html` — payload statique du 12/08, remplacé par les lectures live |
| Référence lecture live | `~/Documents/Claude/Artifacts/command-center-quotidien/index.html` — lit hal via `window.cowork` (l'autre runtime), n'écrit jamais. **À retirer une fois le build 1 validé en vrai.** |
| Sonde, rejouable | `probes/hal-runtime-probe.html` (ce dépôt) — en ligne : `https://claude.ai/code/artifact/ea76b71e-85c6-4107-af19-8cb416bbd98b` |

✅ **Build 1 validé dans le navigateur le 2026-08-15** — commit `9c03576` sur `main`, CI verte.
Deux tâches `rosaslaborbe` cochées, relues **en SQL direct sur `halcrm_tasks`** (pas via le
connecteur) : `done` + `completed_at` stampé, exactement deux lignes touchées, zéro document, zéro
sprint. Le garde-fou sprint a rendu sa bande sur `renaud` (sprint 7 clos depuis le 7/08, toujours
`actuel`). 11 des 15 cases de `#69` sont cochées.

Les deux tâches cochées pendant le test **étaient réellement faites** — l'état en base est juste,
il n'y a rien à corriger.

`command-center-quotidien` a été **supprimé du disque le 2026-08-17** : plus deux dashboards qui
divergent, ce qui était la raison d'être de `#69`. Le snapshot `command-center-v2` reste dans
`~/Documents/Claude/Artifacts/` — figé au 12/08, sans usage depuis que la source vit ici.

**Reste une case** : exercer un code d'erreur en débranchant le connecteur. Le chemin nominal est
prouvé ; c'est le chemin dégradé qui n'a jamais été vu tourner pour de vrai.

### ⚠️ Question ouverte — Cowork n'a jamais été disqualifié pour l'écriture

**Ne pas relire `#69` comme si Cowork avait échoué : ce n'est pas ce qui a été établi.** La sonde du
14/08 a testé le runtime **claude.ai** et prouvé qu'il écrit. Elle n'a jamais testé Cowork. Or
`command-center-quotidien` **lisait déjà hal depuis Cowork** — l'issue le dit. Ce qui n'a jamais été
essayé, c'est `window.cowork.callMcpTool("mcp__hal-mcp__update_task_status", …)`.

Le chemin claude.ai a été retenu parce qu'il a été *prouvé*, pas parce que Cowork avait *échoué*.
La conséquence pratique — le dashboard quitte Cowork pour le navigateur — **n'a été explicitée à
Renaud que le 17/08**, après trois semaines de travail passées à croire l'inverse. La leçon vaut
au-delà de ce dossier : une décision consignée dans une issue n'est pas une décision comprise, et
« ne pas rouvrir le débat » n'exempte pas de vérifier que la conséquence est voulue.

**Sonde prête, non lancée** : `probes/cowork-write-probe.html`. Lectures automatiques, écriture
derrière un clic, cible retrouvée par son titre (`[TEST #69]`, déjà `cancelled`) — aller-retour
`cancelled → todo → cancelled` avec relecture, aucun identifiant en dur, aucun nouveau résidu. Elle
rapporte aussi la surface réelle de `window.cowork`, aujourd'hui inconnue au-delà de `callMcpTool`.
**À publier depuis une session Cowork** — l'outil de publication Cowork n'existe pas dans une
session Claude Code.

Renaud a mis la question de côté le 17/08 (lien du dashboard en favori, usage navigateur). Si elle
revient : lancer la sonde d'abord, décider ensuite. Et savoir que même si Cowork écrit, le portage
coûte le rafraîchissement automatique, la fraîcheur attestée et le branchement par code d'erreur —
ce runtime n'expose que `isError` + un texte libre.

⚠️ **Résidu assumé dans hal** : la tâche `renaud/ba1e8781846d436db176c15fb71b6aef`
(« [TEST #69] Sonde d'écriture Command Center ») a servi à observer `update_task_status` avant de
publier. Elle est en `cancelled` avec son motif — hal n'expose aucune suppression via MCP.

**Tranché le 2026-08-14 — ne pas rouvrir le débat**

- **Runtime** : une page publiée par l'outil `Artifact` depuis une session Claude Code **atteint
  hal**. `window.claude.mcp` présent, `window.cowork` **absent**, connecteur account-level nommé
  **`hal-mcp`**. Cowork n'est pas dans la chaîne.
- **Versionnage** : republier le **même `file_path` conserve la même URL** (build 1 → 2 vérifié
  dans le navigateur). Ce dépôt possède la source — c'était le point 1 de `#69`.
- **Déclaration** : `capabilities: {mcp: {servers: [{server: "hal-mcp", tools: [...]}]}}`. Ne
  déclarer que les outils réellement appelés — le manifeste est un consentement du lecteur.
- **Cocher ne touche jamais le markdown du daily log.** `halcrm_tasks` porte l'état ; le log porte
  la *sélection* du jour. Le dashboard joint sur `<workspace_slug>/<id>` et écrit via
  `update_task_status`.
- **Le sprint est un bandeau de cadrage, pas un filtre** — conditionné à `sprints_enabled`
  (`blue-green` et `renaud` oui, `rosaslaborbe` et `ic-ingenieurs-conseils` non). Réutiliser le
  garde-fou absent/périmé/ambigu de `briefing` 0.14.0.

**Trois contraintes mesurées — à intégrer, pas à redécouvrir**

1. **2,4 à 3,5 s par appel connecteur.** Quatre workspaces en série ≈ 14 s. Paralléliser, afficher
   depuis le cache d'abord, piloter la fraîcheur avec `result.cache.storedAt` (jamais `Date.now()`).
2. **`list_tasks` tronque silencieusement à 100** — `LIMIT 100` dans `get_tasks_with_assignee` avec
   `ORDER BY created_at DESC`, donc la coupe emporte **les plus anciennes**. Lire **filtré par
   statut**, jamais sans filtre. `blue-green` est à 76 `todo` pour un plafond de 100 : la marge est
   mince. Suivi : [`hal#105`](https://github.com/BluegReeno/hal/issues/105).
3. **La frame de l'artefact est sandboxée** : `navigator.clipboard` **et** `prompt()` sont tous deux
   refusés. Un bouton « copier » qui s'appuie sur l'un ou l'autre reste muet, sans la moindre
   erreur. Utiliser un `textarea` readonly + `select()`.

**Cinq statuts de tâche** — `todo | in_progress | done | blocked | cancelled` (`hal#98`, livrée le
2026-08-14). « Annuler » est une action de premier plan dans l'UI ; écrire `done` pour dire
« abandonné » est exactement la confusion que cette issue a supprimée. hal n'expose **aucune
suppression** : une tâche créée par erreur ne peut pas être retirée via MCP.

⚠️ **Redémarrer la session avant de toucher à `cancelled`.** Un client MCP fige sa liste d'outils à
la connexion ; une session ouverte avant le déploiement de `#98` voit encore quatre statuts et
refuse `cancelled` côté client.

⚠️ **Deux clones de ce dépôt existent.** Celui-ci, `~/Projects/renaud-marketplace`, est le clone de
travail. L'autre, `~/.claude/plugins/marketplaces/renaud-marketplace`, est le **cache
d'installation des plugins** — y éditer fonctionne (même remote) mais laisse le marketplace
installé sur une branche de feature. Travailler ici.

---

✅ **`#80` est bouclée end-to-end : secret posé, `gmail-mcp` déployé v7 → v10, allowlist vérifiée sur
un appel réel.** `list_labels` via le plugin `jobsearch` renvoie les 50 labels — l'authentification
passe *et* l'appel Gmail aboutit. À noter : les chemins `?key=` et `secret:gmail_api_key` ne portent
aucune identité par utilisateur et **restent hors allowlist** — secrets partagés propriétaire-seul,
non couverts par ce correctif.

**Trois découvertes de ce déploiement, chacune plus coûteuse que le correctif lui-même :**

1. ⚠️ **La v7 en production datait du 2026-06-10 — trois commits de retard, pas un.** Déployer `#80`
   a mis en prod du même coup `e2af44c` (encodage RFC 2047 du sujet, le correctif des accents) et
   `cbd34b1` (pièces jointes dans `draft_email`), mergés le 2026-07-01 et jamais déployés. Pendant
   cinq semaines, deux bugs « connus » étaient corrigés dans `main` et vivants en prod. **Ce dépôt n'a
   aucun déploiement automatique et rien ne signale l'écart** entre `main` et la fonction déployée.
2. ⚠️ **La doc affirmait que `gmail-mcp` n'avait pas de serveur OAuth — c'était faux**, et c'est ce qui
   a fait sous-estimer l'impact de `#80`. Le plugin `jobsearch` se connecte en **mode `user` JWT**
   (`.mcp.json` porte l'URL nue, la fonction annonce son authorization server, le projet fait
   discovery + DCR — vérifié le 2026-08-05). L'allowlist gouverne donc le chemin principal, pas un cas
   marginal : le premier appel après déploiement est parti en `403`. `docs/connectors-and-skills.md` et
   `servers/gmail-mcp/README.md` corrigés le 2026-08-05.
3. ⚠️ **Le CLI Supabase (jusqu'à 2.111.0) rejette un PAT nouveau format `sbp_v0_…`** contre
   `/^sbp_(oauth_)?[a-f0-9]{40}$/`, en local, avant tout appel réseau — le message parle de privilèges
   et induit en erreur. Le même token fonctionne sur l'API Management, qui a servi à poser le secret et
   à déployer. Recette dans `servers/gmail-mcp/README.md` §When the CLI refuses your token.

⚠️ **Le compte Supabase dépend du répertoire, via direnv.** `~/Projects/hal/.envrc` et
`edifice/.envrc` portent le token Blue Green ; `renaud-marketplace/.envrc` (créé le 2026-08-05) porte
celui du compte perso, propriétaire de `isdyvrwnxqcfalmlkzui`. Lancer une commande `supabase` depuis le
mauvais dossier vise le bon projet avec le mauvais compte. `.envrc` est ignoré via
`~/.config/git/ignore` — vérifié, rien ne fuit dans ce dépôt public.

**`briefing` perd `sprint-planner` et `sprint-review`** — ils vivent désormais dans le plugin `pm` de `bluegreen-marketplace`, issu du découpage du monolithe `hal` ([bluegreen#66](https://github.com/BluegReeno/bluegreen-marketplace/issues/66), PR #67 mergée le 2026-08-02). Les deux skills planifient et clôturent des sprints hal : leur place est avec la gestion de projet, pas avec le briefing quotidien. PR ouverte sur ce dépôt, en attente de relecture.

Second utilisateur humain : Cris a un compte hal depuis le 2026-07-31 et partage le workspace `rosaslaborbe`. Les skills ne portent plus l'identité de leur auteur — ils résolvent workspaces et calendriers à l'exécution via `whoami`. Suite immédiate : l'écriture calendrier (#78), qui a maintenant une destination connaissable.

## In Progress

- [ ] Command Center v2 — **build 1 publié, en attente de validation navigateur**
      ([#69](https://github.com/BluegReeno/renaud-marketplace/issues/69)). Reste : accorder le
      connecteur à la page, exercer les 10 critères d'acceptation, puis retirer
      `command-center-quotidien`.

## Done (2026-08-18)

- [x] **Commande `/briefing` retirée — `morning-briefing` s'invoque directement** — 2026-08-18.
  - `plugins/briefing/commands/briefing.md` supprimé : simple pass-through vers le skill, dont la
    description avait dérivé (« read-only, 3 sources » pour un skill qui en lit 6 et écrit un daily
    log par workspace hal).
  - Contrat headless réécrit `/morning-briefing --headless` (SKILL.md:30) ; aucune étape, source ni
    rendu modifié.
  - 12 mentions `/briefing` réécrites dans `log-application`, `interview-prep`, `log-cr`
    (messages utilisateur + justification du miroir hal).
  - briefing 0.16.0 · jobsearch 0.11.2 · marketplace 0.6.27.

## Done (2026-08-14)

- [x] **Command Center v2 — build 1 : lectures live, cochage, jointure du daily log**
      (`dashboards/command-center/index.html`) — 2026-08-14.
  - **Onglets pilotés par `whoami`** — aucun slug en dur ; un workspace ajouté au compte apparaît
    sans toucher au code.
  - **Lectures via `watchTool`**, une par `(workspace, statut)` : `todo`, `in_progress`, `blocked`
    au chargement ; `done` et `cancelled` seulement à l'ouverture du Daily log, qui en a besoin
    pour joindre. Jamais de `list_tasks` non filtré — et une ligne d'alerte dès qu'une lecture
    ramène exactement 100 lignes, la troncature muette de [`hal#105`](https://github.com/BluegReeno/hal/issues/105).
  - **Pas de polling** : `refetchInterval` non déclaré, un bouton « Rafraîchir » fait
    `invalidate` et les watchers re-livrent. À 2,4-3,5 s l'appel, un poll de fond coûte plus
    qu'il ne rend.
  - **Cocher écrit puis relit.** `update_task_status`, UI optimiste, puis un `list_tasks` sur le
    statut cible pour confirmer — c'est hal qui prouve, pas l'UI. `server_unavailable` /
    `upstream_error` / `cancelled` ne déclenchent **ni rollback ni réécriture** : l'issue est
    ambiguë, la page le dit et propose de relire.
  - **Cinq statuts, l'annulation de premier plan** — sélecteur par tâche + champ de motif inline
    (`prompt()` est refusé dans la frame, `navigator.clipboard` aussi).
  - **Un message par code d'erreur**, jamais une bannière fourre-tout : reconnexion, connecteur
    absent, doublon à choisir, politique, hors manifeste, transitoire. Une section qui échoue
    n'emporte pas les autres ; les refus d'autorisation retirent les données affichées, les
    erreurs transitoires les gardent avec leur heure (`result.cache.storedAt`).
  - **Garde-fou sprint** conditionné à `sprints_enabled` : zéro `actuel`, plusieurs, ou un dont
    `ends_at` est passé rendent chacun une ligne bruyante. `rosaslaborbe` et
    `ic-ingenieurs-conseils` n'affichent **aucun** bandeau. Cas réel disponible pour l'exercer :
    `renaud #7` est clos depuis le 07/08 et toujours `actuel`.
  - **Daily log en lecture seule** — `save_document` n'est même pas dans le manifeste MCP, donc
    l'écriture est structurellement impossible, pas seulement évitée. La page affiche la
    *sélection* du log et va chercher l'*état* dans hal ; un écart est signalé.
  - **Le join tient sur les deux formats** : id complet 32 car. (0.14.0) en exact, id tronqué des
    logs existants résolu par préfixe **seulement s'il est unique**, sinon marqué non résolu.
    17 tests hors-ligne (`tests/test_command_center_parser.js`) épinglent le parseur, dont le
    piège trouvé en les écrivant : `jobs/view/4452451971` d'une URL LinkedIn a la forme d'un id.
  - **Formes observées avant publication**, jamais devinées : les 5 lectures et l'écriture ont été
    appelées pour de vrai dans la session. `done` stampe `completed_at`, le retour à `todo`
    l'efface, `cancelled` ne le porte jamais.

- [x] **`briefing` 0.14.0 — le daily log porte la sélection du jour, jamais l'état des tâches**
      ([PR #94](https://github.com/BluegReeno/renaud-marketplace/pull/94)) — 2026-08-14.
  - Plus de `- [ ]` nulle part : les tâches du sprint sont une liste numérotée, **une ligne = une
    tâche**, chacune avec son **id complet 32 caractères** — la clé de jointure du Command Center.
  - Mesuré sur le daily log `renaud` du 2026-08-12, trois défauts rendaient toute jointure
    impossible : une entrée portant **cinq** `réf. hal`, des ids tronqués à 8 caractères, et des
    titres reformulés (le log disait « MyCoach S3 — débrief du dîner du 31/07 », la base
    « MyCoach S3 — Vendredi 31/07 : poser la question… »).
  - Step 1a garde désormais le sprint au lieu de prendre la première entrée `actuel` : zéro
    `actuel`, plusieurs `actuel`, ou un dont `ends_at` est passé rendent chacun une ligne bruyante.
    Le 2026-08-13, `renaud #7` était `actuel` depuis six jours après sa clôture et le briefing
    présentait ses restes comme le plan de la semaine.
  - ⚠️ **N'a d'effet qu'après un `plugin update`** : une session lit le SKILL.md depuis le cache
    numéroté par version, donc `/briefing` tourne en 0.13.0 tant que le plugin n'est pas réinstallé.
- [x] **Sonde de runtime — une page publiée atteint le connecteur hal**, verdict consigné dans
      `#69` — 2026-08-14. `probes/hal-runtime-probe.html`, deux exécutions sur le compte réel.

## Done (2026-08-04)

- [x] **#80 / PR #84 — `gmail-mcp` : allowlist `user_id` en mode JWT** — jobsearch 0.9.1, marketplace top-level 0.6.17 — 2026-08-04
  - Issue venue du `📋 Portfolio plan — 2026-08-03` ([archon-workflows#14](https://github.com/BluegReeno/archon-workflows/issues/14)), classée `no-brainer`, lancée en `skill-improve` pendant la nuit. 7 fichiers, +76/−7.
  - **Ce que prouvait réellement l'authentification avant** : `verifyAuth(auth: ["user", "secret:gmail_api_key"])` établissait que l'appelant était *un* utilisateur provisionné sur le projet Supabase `isdyvrwnxqcfalmlkzui` — **pas** qu'il possédait cette boîte. Un second compte sur ce projet, ou quiconque détenant `GMAIL_API_KEY`, lisait et rédigeait depuis la boîte du propriétaire. Exactement le scénario ouvert par l'arrivée d'un second utilisateur hal le 2026-07-31.
  - **Le correctif est fail-closed, et c'est un piège de déploiement** — secret à poser avant le déploiement, voir Current Focus.
  - **Déployé et vérifié le 2026-08-05** (v7 → v10, `verify_jwt:false` préservé). Le premier `user_id`
    posé était celui d'un autre compte : `403 This Supabase account is not authorized for this mailbox`
    — refus propre, exactement le comportement voulu, mais qui ressemble à une panne. Corrigé avec le
    bon `auth.users.id` du projet `isdyvrwnxqcfalmlkzui`, puis redéploiement **obligatoire** : la
    valeur est lue au chargement du module, un isolate chaud garde l'ancienne allowlist. Le cas négatif
    a donc été exercé pour de vrai, sans second compte à créer.
  - ⚠️ **PR forcée en draft après coup** (`gh pr ready --undo`) : `skill-improve` n'ouvre pas de drafts, or un correctif de sécurité ne doit pas arriver mergeable sans qu'un humain l'ait exercé. Mergée par Renaud le 2026-08-04 à 06:47.

## Done (2026-08-02)

- [x] **`briefing` 0.12.0 — retrait de `sprint-planner` et `sprint-review`** — 2026-08-02
  - Les deux skills et leurs deux commandes sont supprimés ; ils sont livrés par `pm@bluegreen-marketplace` depuis le 2026-08-02. **L'ordre était contraint** : les retirer avant que `pm` existe publiquement les aurait rendus non installables. Vérifié avant suppression : les quatre fichiers étaient **identiques** aux copies faites côté `bluegreen` — aucun delta à reporter (le dernier commit qui les touchait, `0999867`, est antérieur à la copie).
  - **Aucun renvoi à repointer** : `morning-briefing` et `mail-triage` ne référencent ni l'un ni l'autre. Les seules mentions restantes sont le `CHANGELOG` (historique) et la table générée du skill `improve`.
  - **Un bug de CI trouvé et corrigé au passage** : `scripts/generate_improve_map.py` énumérait `plugins/<name>/skills` pour **chaque** plugin distant et mourait sur l'échec. `hal` n'ayant plus de `skills/` (connecteur seul), l'API répondait 404 et le générateur s'arrêtait — donc le job CI aussi, puisqu'il lance le générateur puis `git diff --exit-code`. Un 404 sur ce chemin ne produit plus de lignes, comme le fait déjà `local_skill_dirs()` ; **seul** « HTTP 404 » est traité ainsi, un token invalide ou un dépôt renommé continue d'aborter, et un 404 sur un fichier requis (le `marketplace.json` distant) meurt toujours. Deux tests hors-ligne épinglent les deux moitiés.
  - **Table `/improve` régénérée** : `sprint-planner` / `sprint-review` → `pm`, `crm` / `linkedin` → `gtm`, `edifice` → `edifice`. README : ligne `briefing` rafraîchie, ligne `mycoach` qui traînait en 0.3.0 corrigée.
  - **À trancher, non corrigé ici** : `scripts/test_release.sh` échoue sur son cas « happy path », **et échouait déjà sur `main`** — il n'est lancé par aucun job de `ci.yml`. Cause : `check_version_sync.sh:69` boucle sur `plugins/*/skills/*/SKILL.md` et passe le motif littéral à Python quand le glob ne correspond à rien ; la fixture du test n'a aucun `SKILL.md`, d'où un `FileNotFoundError`. Même famille de défaut que le bug ci-dessus — un plugin sans skill casse l'outillage — et désormais un cas réel dans le portfolio.

## Done (2026-08-01)

- [x] **#77 skills utilisables par un second utilisateur (PR #79, merged)** — briefing v0.11.0, mycoach v0.4.0, marketplace top-level 0.6.15 — 2026-08-01
  - **Dépendance amont livrée dans `hal` (#92, déployée avant le merge)** : deux colonnes `calendar_id` — sur `halcrm_workspaces` (calendrier **partagé** du workspace) et sur `workspace_members` (calendrier **du membre**) — exposées par `whoami` avec `name`, `allowed_tags`, `sprints_enabled`. Le double niveau suit la frontière de partage : un calendrier unique sur le workspace aurait servi l'agenda de Renaud à tout futur collaborateur de `blue-green`.
  - **Principe directeur (correction de Renaud, 2026-07-31)** : le workspace est un **périmètre de partage**, le tag un **sujet**. Aucun routage de tâche par les tags. Conséquence assumée : le tag `rosaslaborbe` **reste** dans `allowed_tags` de `renaud` (tâches familiales non partagées, ex. Saint-Valentin surprise) — l'étape 6 du doc `hal/docs/family-workspace-onboarding.md` est caduque sur ce point.
  - **5 skills refondus** : `morning-briefing`, `mail-triage`, `sprint-planner`, `sprint-review`, `mycoach`. Sonde `whoami` avant tout appel hal (le vrai bug : `sprint-planner`/`sprint-review` sondaient *après* un `get_document` sur slug en dur ; `mycoach` ne sondait pas du tout et écrivait). Itération sur les workspaces retournés, un bloc rendu seulement s'il a du contenu ; calendriers = union des `calendar_id`/`member_calendar_id` déclarés ; mailboxes décidées par le serveur MCP appelé, jamais par une adresse.
  - **`mycoach`** résout son workspace par le tag `mycoach` dans `allowed_tags`, **jamais** par `default_workspace_slug` — le défaut de Renaud est `blue-green`, une séance perso ne doit pas y atterrir.
  - **`sprint-review`** : un bilan **par workspace clôturé**, écrit dans ce workspace, `domain="memory"`. Remplace le bilan unique routé vers le workspace portant le tag `jobsearch`, avec repli sur le workspace par défaut — une écriture non résolue.
  - **Dégradation fail-closed** : un `sprints_enabled` absent arrête avant écriture et demande, au lieu de retenir tous les workspaces. Une information manquante ferme le périmètre d'écriture, jamais l'élargit.
  - **Garde CI** `scripts/check_no_identity_literals.sh` (job `identity-guard`) : échoue sur tout ID de calendrier, adresse mail ou `workspace_slug` littéral sous `plugins/briefing` et `plugins/mycoach`. `author.email` des manifestes exclu. Vérifiée verte sur la branche et rouge sur deux régressions injectées.
  - **#76 partiellement traitée** : identifiants nettoyés dans 10 fichiers, dont 5 que l'issue ne listait pas (`docs/loop-3-morning-briefing.md`, `.claude/docs/features/sprint-planner-SKILL.md`, `.agents/plans/gmail-mcp-plan.md`, `.claude/tasks/gmail-mcp-oauth-consent-github-pages.md`, `plugins/briefing/CHANGELOG.md`). **`cv-master.json` volontairement reporté** (email, téléphone, adresse postale) → #76 reste ouverte.
  - **Données hal seedées** : agenda pro sur `blue-green`, agenda perso sur `renaud`, agenda famille partagé sur `rosaslaborbe`, `sprints_enabled=false` sur `rosaslaborbe` et `ic-ingenieurs-conseils`.
  - **Convention actée** : les briefs vivent dans les **issues GitHub**, plus dans des fichiers du dépôt — les deux coexistaient et on s'y perdait.
  - **Défaut relevé côté hal, non traité** : `save_document` annonce que `domain` doit appartenir au vocabulaire du workspace, mais ne le valide jamais (`validateTags` ne couvre que les tags).

## Done (2026-07-31)

- [x] **#73 renommage `myspy` → `mycoach` (PR #75, merged)** — mycoach v0.3.0, marketplace top-level 0.6.14 — 2026-07-31
  - `plugins/myspy/` → `plugins/mycoach/`, `skills/myspy/` → `skills/mycoach/` ; frontmatter, déclencheurs, `release.sh`, README, `docs/features/`, plan `.agents/`, table improve-map régénérée.
  - **Bundle de connaissance couplé** : `BluegReeno/myspy-kwiki` renommé en `mycoach-kwiki` (redirection GitHub conservée), dossier local et remote suivis. Le SKILL.md code le chemin en dur (`/Users/renaud/Projects/mycoach-kwiki`) — les deux renommages ne valent que faits ensemble.
  - **Données hal retaguées** (SQL direct sur `zgkvbjqlvebttbnkklpo` — le MCP hal n'expose ni `list`/`update` d'interactions ni écriture des `allowed_tags`) : vocabulaire du workspace `renaud`, 1 projet, 4 tâches, 3 interactions, channel `myspy-session` → `mycoach-session`. Zéro résidu vérifié.
  - **Pas d'alias de transition** : le déclencheur « séance MySpy » est supprimé.
  - **Résidus assumés** : les entrées historiques du CHANGELOG gardent leur titre `myspy` (les réécrire ferait mentir le changelog), et l'historique git porte l'ancien nom de toute façon — le renommage nettoie la surface courante, pas le passé.
  - Table de versions du README rafraîchie au passage : `jobsearch`, `briefing` et `improve` étaient périmés de plusieurs releases.

## Done (2026-07-23)

- [x] **Consolidation des noms d'outils MCP** — briefing v0.10.0, jobsearch v0.9.0, myspy v0.2.0 — 2026-07-23
  - `plugins/briefing/.mcp.json` **supprimé** : il déclarait la même URL `hal-mcp` que `bluegreen-marketplace/plugins/hal/.mcp.json`. Claude Code déduplique par URL et montait arbitrairement l'un des deux → nom d'outil non déterministe. Le plugin `hal` est seul propriétaire.
  - 88 références réécrites : `mcp__hal-mcp__*` → `mcp__plugin_hal_hal-mcp__*`, `mcp__claude_ai_gmail-mcp__*` → `mcp__plugin_jobsearch_gmail-mcp__*`. Les anciens noms visaient le serveur user manuel et le connecteur claude.ai, tous deux supprimés.
  - `mcp__claude_ai_Gmail__*` / `mcp__claude_ai_Google_Calendar__*` intacts — connecteurs toujours actifs.
  - **Dépendance nouvelle** : briefing, jobsearch et mycoach (alors `myspy`) exigent le plugin `hal` installé pour que leurs appels hal-mcp résolvent.

## Done (sprint Archon 2026-07-12)

- [x] **#56 `release.sh` fail-loud (PR #61, merged)** — retrait du `2>/dev/null` sur la lecture de version (les erreurs Python remontent au lieu d'être englouties). — 2026-07-12
- [x] **#57 doc dépendance CI improve-map (PR #62, merged)** — note dans `docs/skill-marketplace-guide.md` : le CI improve-map dépend du repo sibling public `bluegreen-marketplace` + mitigation PAT si privatisation. — 2026-07-12
- [x] **#50 CI validation schéma `marketplace.json` (PR #64, merged)** — `scripts/check_marketplace_schema.sh` + job CI : champs requis, `source` existe, ≥1 SKILL.md découvrable (adapté à l'auto-discovery post-#59). — 2026-07-12
- [x] **#51 CI validation frontmatter SKILL.md (PR #66, merged)** — Invariant 3 dans `check_version_sync.sh` : `name` (= dossier), `description`, `allowed-tools` présents. — 2026-07-12
- [x] **#55 tests offline `generate_improve_map.py` (PR #68, merged)** — `scripts/test_generate_improve_map.py` (stub `gh_api`, déterminisme tri, rendu tableau, chemins `die()`) + job CI. — 2026-07-12
- [x] **#43 narratif P4 cv-generator (PR #63, merged)** — correction du framing faux « côté client » → vendeur/fondateur. — 2026-07-12
- [x] **#52 sprint-review jours de semaine (PR #65, merged)** — labels de jours recalculés programmatiquement via `date`. — 2026-07-12

Plan source : issue #60 (`📋 Dev plan — 2026-07-11`, généré par le workflow `issue-portfolio-plan`). Runs `skill-improve` lancés depuis Cowork ; merges tooling/CI autonomes, PRs métier laissées en relecture.

## In Progress

- [ ] **#44 comp-gate cv-log-worker (PR #67)** — plancher salarial. Seuil corrigé par Renaud : double-marge erronée (76 950 €) → plancher simple **80 000 €** (cible 90 k€, haut de fourchette). En relecture avant merge.

## Done (sprint Archon 2026-07-01)

- [x] **#38 `log-cr` générique BANT (PR #40, merged)** — skill jobsearch + `docs/bant-cr-template.md` (template BANT partagé, référencé par `/crm log` côté `bluegreen-marketplace`). Domaine Blue Green non implémenté ici par design (redirection vers `/crm log` plutôt que fuzzy-match cross-repo) — jobsearch v0.8.0. — 2026-07-01
- [x] **#39 `mail-triage` générique (PR #41, merged)** — nouveau skill `plugins/briefing/skills/mail-triage`, scan des 2 boîtes (perso + pro), 10 catégories (5 jobsearch + 5 Blue Green), lookup hal/vault. Volontairement indépendant de `morning-briefing` (pas de DRY forcé) — briefing v0.8.0. — 2026-07-01
- [x] **#32 `gmail-mcp` — fix encodage accents Subject (PR #34, merged)** — RFC 2047 encoded-word sur l'en-tête Subject. — 2026-07-01
- [x] **#33 `gmail-mcp` — pièces jointes sur `draft_email` (PR #37, merged)** — `multipart/mixed` + limite 25 Mo. Conflit avec #34 (même fichier) résolu par rebase manuel avant merge. — 2026-07-01

marketplace.json top-level → 0.5.9. Repo local resynchronisé (`main` rebasé + poussé, aucune divergence restante).

## Backlog (CV — reprendre quand job search actif)

- [ ] **P6 Digital Innovation — Bureau d'ingénierie ENR** — session dédiée
- [ ] **P1 Architecte IA** — session dédiée
- [ ] **P3 Late CTO** — session dédiée
- [ ] **P2 Lead IA** — session dédiée (profil le plus faible, à reconsidérer)

**Ressources CV prêtes :**
- Parcours source de vérité → HAL workspace `renaud`, slug `parcours` (màj 2026-06-19)
- Fichier local → `~/Library/CloudStorage/SynologyDrive-MyAssistant/jobsearch/parcours-renaud.md`
- Briefs marché par profil → `~/Library/CloudStorage/SynologyDrive-MyAssistant/jobsearch/research/P{1,2,3,4,6}-*.md`

## Done (current sprint)

- [x] **fix(skill:cv-log-worker): statut '📝 À postuler' + chemin CV dans la fiche (briefing v0.7.1 · jobsearch v0.6.2 / PR #31)** — `cv-log-worker` passait un statut `📋 CV préparé — à envoyer` inexistant dans le Kanban Job Search (8 colonnes) → carte orpheline. Corrigé en `📝 À postuler` (statut existant). `log-application` accepte désormais ce statut et écrit une section `## CV généré` dans le body de la fiche `opportunite-js` (chemin PDF + profil retenu) quand `cv_path` est fourni. Scope automatique avait manqué `log-application` (validation stricte des statuts) — rattrapé pendant l'implémentation. Closes #30. — 2026-07-01

- [x] **fix(jobsearch): log-application relance task in hal renaud only, drop Obsidian tache (jobsearch v0.6.1 / PR #28)** — Step 4 crée directement la tâche relance dans hal (`renaud`, tag `jobsearch`). Step 4b (miroir hal) supprimé — hal est la source unique. Closes #27. — 2026-06-29

- [x] **feat(briefing): morning-briefing v2 (#18) — Gmail perso+pro, scoring offres BrightData, plan du jour 6 blocs (briefing v0.6.0 / PR #24)** — 2026-06-24

- [x] **research(brightdata): pipeline extraction JD LinkedIn validé (#22)** — `web_data_linkedin_job_listings` retenu (JSON structuré, zéro bruit). gmail-mcp retourne plain text, job IDs extractibles par regex `jobs/view/(\d+)`. Pipeline : email → job IDs → URL slug → web_data_linkedin_job_listings → job_summary → LLM. `scrape_as_markdown` éliminé (85% bruit, LinkedIn bloque). Bonus : `web_data_linkedin_posts` disponible pour analyse tendances (likes/comments, pas d'impressions). Issue #22 commentée + fermée. Débloque #18. — 2026-06-24

- [x] **fix(briefing): sprint-planner clôture sprints actuel avant création (briefing v0.4.4 / PR #19)** — Nouvelle étape 6b : `list_sprints(status="actuel")` sur blue-green + renaud → `update_sprint(status="passes")` avant `create_sprint`. Closes #17. — 2026-06-24

- [x] **fix(jobsearch): P4×T5 About rewrite — technical-first, drop false buyer claim (jobsearch v0.5.1 / PR #20)** — About EN réécrit (technique → delivery → empathie), HAL + BlueWind comme ancres, suppression "15 years client side" → "4 years DSI Artelia", suppression "user-buyer GenAI vendors target". credibility_note + profiles/p4_cs_fde.md corrigés. Closes #14. — 2026-06-24

- [x] **fix(cv-generator): auto-fit itératif 3 niveaux + doc cold start (jobsearch v0.5.2 / PR #21)** — `COMPACT_CSS` → `COMPACT_CSS_LEVELS[3]` (gentle → moderate → ultra-compact). Retry binaire → boucle itérative niveau 1-2-3 jusqu'à 1 page. SKILL.md : doc cold start + commande pre-warm. Closes #15. — 2026-06-24

- [x] **Mistral AI — CVs killer P4×T5 EN (jobsearch v0.5.1)** — 2 CVs générés et validés (FDE + Prototyping). Nouveaux params `--about-override` / `--title-override` ajoutés au générateur. Règles éditoriales EN gravées dans SKILL.md (premier lecteur = RH, pas ingénieur). P4×T5 EN containers mis à jour (AI Solutions 3 items, Open Ocean 1 bullet). — 2026-06-20

- [x] **cv-generator P4 fix (jobsearch v0.4.9 / PR #13)** — Refonte complète profil P4 (FDE/Solutions Engineer) : about P4×T5 triangle différenciateur (vendeur B2B Artelia / DSI insider / constructeur IA), containers restructurés, bullets BG (BlueWind 91 docs 5 agents 8.6/10), bullets Artelia créés (pipeline grands comptes + comités DSI), bullets OO créés (co-fondateur/CTO, pas Sales). Fix généré par `archon workflow run skill-improve "#12"` — premier run end-to-end réussi. — 2026-06-18

- [x] **fix(improve): mcp__github__issue_write + workflow self-contained (v0.1.2)** — 2 bugs : (1) SKILL.md utilisait `gh` (non dispo Cowork) → remplacé par `mcp__github__issue_write`, `allowed-tools` et section IMPORTANT corrigés ; (2) `skill-improve.yaml` node 2 référençait `archon-fix-github-issue-experimental` (commande inexistante) → remplacé par prompt self-contained en 6 étapes. Closes #11. — 2026-06-18

- [x] **plugin `improve` v0.1.1 + workflow `skill-improve.yaml` (marketplace v0.5.0 / PR #9)** — Un skill Cowork générique `/improve <skill-name>` : auto-détecte le repo depuis le nom du skill, 1 seule question (delta observé/attendu), crée l'issue GitHub avec la commande Archon dedans. Archon workflow `skill-improve.yaml` wrape `archon-fix-github-issue-experimental` + verify-version-bump. Remplace PR #7 (bg-improve + renaud-improve dupliqués). Follow-up P2 : copier `skill-improve.yaml` dans `bluegreen-marketplace`. — 2026-06-17

- [x] **cv-generator about FR + experience order (jobsearch v0.4.8 / cv-generator v0.2.7)** — 15 about.fr réécrits en forme nominale, ordre fixe BG→Artelia→OO (suppression CORPORATE_FIRST_CELLS), 3 bullets corrigés (OO Business Angels→institutionnels, BG stack→Edifice/IC, Artelia default→P&L spécifique). Règle style FR ajoutée SKILL.md. — 2026-06-16

- [x] **cv-generator FR quality pass (jobsearch v0.4.7 / cv-generator v0.2.6)** — 14 corrections sur P1–P5 : openers "Cumuler" → "Fort de", infinitif passé P2×T1, "Manager" verbe → "Diriger", "ventures" → "startups", bullet vague BG P1 → Edifice/IC Ingénieurs, "delivery agile" → "livraison agile", P5 20 ans → 15 ans (factuel), Artelia period 2019–2022 → 2019–2023 (factuel), CPTEC "Analyste Données" → "Analyste Climatique — Événements Extrêmes". — 2026-06-16

- [x] **update_sprint wiring — briefing v0.4.3** — `mcp__hal-mcp__update_sprint` ajouté aux `allowed-tools` de sprint-planner + sprint-review. Section "6a bis" dans sprint-planner ÉTAPE 6 : correction statut post-création via `update_sprint` avant de recréer. 4-field version sync : briefing 0.4.2 → 0.4.3. — 2026-06-15

- [x] **fix(sprint-planner): SPRINT_STATUS dynamique — briefing v0.4.2** — `SPRINT_STATUS = "actuel"` si `NEXT_MON <= TODAY` (planning lundi matin / rattrapage), `"suivant"` sinon. Corrige `list_sprints` idempotence (ÉTAPE 6a) et `create_sprint status=` (ÉTAPE 6b). Sprint-review drift 0.4.0 → 0.4.2 corrigé au passage. — 2026-06-15

- [x] **sprint-review + sprint-planner skills (briefing v0.4.0)** — `sprint-review` : bilan sprint hal (blue-green + renaud), métriques jobsearch, projets BG, shortlist semaine suivante, clôture hal après validation explicite. `sprint-planner` : report/abandon décisions, métriques vault, scan LinkedIn gmail-mcp, conflit calendriers, calcul capacité 35h, plan MUST/SHOULD/COULD/BACKLOG, création sprint hal avec sprint_number auto-incrémenté + idempotence. Mode schedule : autonome pour étapes 0-4/0-5, gate sur création. — 2026-06-14

- [x] **cv-generator tooling upgrade (jobsearch v0.4.5 / cv-generator v0.2.4)** — `--company`+`--job-title` → filename lisible (ex: `CV_Renaud_Laborbe_forward_deployed_engineer_yotta_FR.pdf`). `--data-dir` pour Cowork read-only. `--container-titles` JSON array pour override sans toucher le JSON. `--bullet-overrides` pour injecter les bullets Step 3b. Auto 1-page check (pikepdf) + compact layout fallback. P4×T5 FR defaults: "Architecture & agents IA" + "Cycle client & déploiement". 30/30 validés. — 2026-06-14
- [x] **cv-generator editorial upgrade — FR infinitif + labels + Step 3b personnalisation (jobsearch v0.4.4 / cv-generator v0.2.3)** — Tous les bullets FR réécrits à l'infinitif (P1–P5 × BG/Artelia/OO, ~80 bullets + 15 about.fr). Labels human-readable ajoutés aux 15 cellules. Step 3b : personnalisation LLM (1–2 bullets/entreprise adaptés aux signaux de l'offre, ancres factuelles toujours intactes). 30/30 CVs 1-page validés. — 2026-06-14

- [x] **cover-letter skill + cv-generator methodology (jobsearch v0.4.3)** — New `/cover-letter` command: LLM-native 3-paragraph letter, 15-cell matrix, factual anchors, banned phrases, solopreneur counter. cv-generator SKILL.md v0.2.2: added narrative methodology section (experience order rules, T/P signals, factual anchors, banned phrases). — 2026-06-14

- [x] **cv-generator quality sprint — cell-specific bullets P1/P2/P3 + factual fixes (30/30 CVs validated)** — Added T3/T4/T5 bullets for P2 (Lead/Manager) × all 3 companies; T1+T5 bullets for P3 (CTO) × all 3 companies; fixed Artelia P3 "investor presentations" lie (was Open Ocean), fixed "Business Angels" → institutional investors, fixed "DCNS" → Naval Group, fixed franglais "delivery" → "livraison" in FR bullets. All 30 CVs 1-page validated. — 2026-06-14

- [x] **cv-generator multi-company-type differentiation — P1×T3/T4/T5 (30/30 CVs, commit 6162a0c)** — Restructured cv-master.json: bullets[profile] now has `default` + per-cell overrides. P1×T5 counters solopreneur (Open Ocean first, institutional VCs), P1×T4 frontloads Artelia (corporate credibility), P1×T3 technical delivery emphasis. "urban planning automation" banned → replaced with accurate PLU analysis. Real client names + verifiable metrics throughout. generate_cv.py updated for cell-specific title overrides + bullet fallback. — 2026-06-14

- [x] **WP-D — hal tags wired into renaud skills (briefing v0.3.0 · jobsearch v0.4.2 · PR #5 merged)** — `morning-briefing` groups `renaud` tasks by unified tag (jobsearch → rosaslaborbe → personal → finance → hr → laborbe → other); `log-application` + `interview-prep` create hal mirror task tagged `jobsearch` (best-effort, Obsidian stays canonical). `mcp__hal-mcp__create_task` + `list_tasks` added to `allowed-tools`. Requires hal-mcp v39. AC validated by static inspection + review fixes (H1 list_tasks allowed-tool, H2 README versions, M1/M2 Step 4b/5 failure semantics). 4-field version sync clean — 2026-06-14

- [x] **cv-generator FR quality pass (jobsearch 0.4.1 / cv-generator 0.2.1)** — applied Renaud's P4 (Customer Success / Solutions Engineer) feedback: de-anglicised FR titles (Open Ocean p2/p4/p5 → "Directeur Technique & Co-Fondateur", Blue Green p2 → "Responsable Solutions IA — Consultant"), container titles across P4×T5 + 6 p2/p3 cells, P4×T5 `about`/items reworded as skills-not-tasks, P4 bullets cleaned of franglais (discovery/delivery/workflows/data marines), `generate_cv.py` renders "Aujourd'hui" not "Present" in FR. CSM competencies researched + woven in (adoption, multi-level relationship, +15% retention proof). P4×T5 FR CV re-rendered live, 1 page, zero franglais. Umbrella version 0.4.0→0.4.1 (4-field sync). — 2026-06-12

- [x] **`jobsearch-vault` skill** (all 5 phases) — filesystem-only skill (5 JS note types, REST backend stripped) + 3 consumers re-pointed (Option A) + versions bumped (jobsearch 0.4.0, briefing 0.2.0, marketplace top-level 0.4.0, 4-field sync) + CHANGELOGs. Schema self-test 30/30; AC1/AC2/AC3 re-validated live vs the real vault (Anthropic P1 + Yotta P4 intact); `obsidian-crm` untouched. Committed direct to main `3a2b138` — 2026-06-12

- [x] Loop 4 — jobsearch v0.3.0 (`log-application` + `interview-prep`) — composition via `obsidian-crm`, P1–P5 reused, 5-section interview contract, idempotent relance; **AC1/AC2/AC3 smoke-tested live** + 4 findings fixed — PR #3 merged — 2026-06-12
- [x] Loop 3 — plugin `briefing` v0.1.0 (skill `morning-briefing`) — read-only daily dashboard (3 calendriers + hal tasks business/perso + Obsidian jobsearch), AC3 loud-failure, hal-mcp dedup — PR #2 merged — 2026-06-12

- [x] cv-generator v0.1.0 — 30/30 CVs validated (1 page each) — 2026-06-03
- [x] cv-generator v0.1.1 — fix FR language mixing — 2026-06-05
- [x] cv-generator v0.1.2 — add spontaneous mode — 2026-06-05
- [x] photo.jpeg bundled in plugin — 2026-06-05
- [x] gmail-mcp Supabase Edge Function deployed — fixes: McpServer import, webStandardStreamableHttp, registerTool API, export default — 2026-06-09
- [x] gmail-mcp auth fixed — SUPABASE_SECRET_KEYS env override workaround — 2026-06-09
- [x] All 4 MCP tools tested live: list_labels, search_emails, read_email, draft_email — 2026-06-09
- [x] Plugin renamed cv-generator → jobsearch, .mcp.json added for gmail-mcp server — 2026-06-09
- [x] Bumped to v0.2.0 (all 4 files in sync) — 2026-06-09
- [x] docs/mcp-server-supabase-edge.md — SUPABASE_SECRET_KEYS gotcha documented — 2026-06-09
- [x] README — versioning rules + .mcp.json format + repo structure — 2026-06-09
- [x] .gitignore — added tmp, breif-gmail.md, pycache, supabase temp dirs — 2026-06-09
- [x] gmail-mcp v0.2.0 — ?key= query-param auth for headerless connectors (Cowork/claude.ai), deployed + 401 behaviors verified — 2026-06-10
- [x] docs/mcp-server-supabase-edge.md §10 — OAuth prerequisites (feature_disabled gotcha) + query-param fallback — 2026-06-10
- [x] gmail-mcp OAuth consent page `oauth/consent/index.html` créée + Edge Function oauth supprimée — 2026-06-10
- [x] docs/mcp-server-supabase-edge.md §10a — HTML limitation Edge Functions + solution GitHub Pages documentée — 2026-06-10
- [x] gmail-mcp OAuth flow complet — consent page GitHub Pages + Google Auth + claude.ai connecteur validé — 2026-06-10
- [x] gmail-mcp OAuth flow testé — vrais appels Gmail API confirmés (pas de stubs) — 2026-06-10

## Backlog

- [ ] **#78 — écriture calendrier** : créer un rendez-vous dans le calendrier résolu depuis le workspace (`calendar_id` partagé, sinon `member_calendar_id`, sinon arrêt). Débloqué par #77 ; garde-fous à définir (confirmation avant écriture, interdiction en `--headless`, quel skill porte la fonction, doublons).
- [ ] **#80 — `gmail-mcp` sans allowlist `user_id`** : tout compte authentifié sur le projet `isdyvrwnxqcfalmlkzui` (et tout porteur de `GMAIL_API_KEY` via `?key=`, qui court-circuite `verifyAuth`) lit la boîte perso de Renaud — `GOOGLE_REFRESH_TOKEN` est un secret unique. Mitigation en vigueur : ne pas installer le plugin `jobsearch` chez un second utilisateur (seul déclarant du serveur). **Multi-compte écarté le 2026-08-01** (consent Google par user + table de tokens + abandon du chemin `?key=` dont dépend Cowork) : un second utilisateur qui veut ses mails branche le connecteur Gmail natif de claude.ai, qui fait déjà l'OAuth par utilisateur.
- [ ] **#76 — reste : `cv-master.json`** : email, téléphone, **adresse postale + lien maps** dans un dépôt public. Reporté volontairement le 2026-07-31. Décider séparément du sort de l'email et du téléphone (imprimés sur le CV généré).
- [ ] **#10 — skill mail** : scanner/classifier boîte jobsearch Gmail. Dépend de #18 (✅ mergé).
- [ ] **#10 — skill mail** : scanner/classifier boîte jobsearch Gmail. Dépend de #18.
- [ ] Visual review of priority CVs (p1×t4, p3×t1, p2×t5)
- [ ] gmail-mcp: test OAuth flow end-to-end from claude.ai (connector validated 2026-06-10)
- [ ] Notion job search skill
