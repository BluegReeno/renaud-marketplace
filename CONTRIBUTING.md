# Contributing — Versioning rules

## Versioning — règle critique Cowork

**Cowork détecte les mises à jour exclusivement par numéro de version.**
Sans bump de version, les utilisateurs installés ne reçoivent jamais le fix.

### Les 2 champs à garder en sync (par plugin)

Pour **chaque plugin**, ces 2 champs doivent être identiques :

| Fichier | Champ | Exemple (`briefing`) |
|---------|-------|----------------------|
| `.claude-plugin/marketplace.json` | `plugins[].version` (entrée du plugin) | `"0.8.0"` |
| `plugins/<plugin>/.claude-plugin/plugin.json` | `version` | `"0.8.0"` |

Si un seul dérive → Cowork ne détecte plus les mises à jour ou refuse l'installation.

Les `SKILL.md` **ne portent plus** de champ `version:` — la version vit au niveau du plugin uniquement.

### `CHANGELOG.md` — une entrée par version courante

Chaque plugin doit avoir une entrée `## <plugin> <version>` dans `CHANGELOG.md` pour sa version courante. Sans elle, `scripts/check_version_sync.sh` échoue (exit 1).

### Invariant vérifié par CI

`scripts/check_version_sync.sh` (lancé en CI) applique, en exit 1 :
1. `plugin.json.version` == entrée `marketplace.json` du plugin ;
2. `CHANGELOG.md` documente la version courante de chaque plugin.

Le `version` top-level de `marketplace.json` est un compteur monotone (règle de process, non vérifié statiquement).

### Top-level `marketplace.json` `version` — compteur monotone

Le `version` **top-level** de `.claude-plugin/marketplace.json` est un **compteur monotone** indépendant des versions de plugins. Il s'incrémente d'un PATCH (`+0.0.1`) à chaque fois qu'un plugin quelconque est modifié — il sert de signal à Cowork qu'une nouvelle release existe.

Exemple : top-level à `0.5.3`, on bumpe `briefing` de `0.4.4` → `0.5.0` → le top-level passe à `0.5.4` (pas à `0.5.0`).

### Quand bumper

| Type de changement | Bump |
|-------------------|------|
| Fix bug script, template, data | PATCH `0.x.Y+1` |
| Nouveau comportement, nouvel outil, nouveau skill | MINOR `0.X+1.0` |
| Refonte majeure | MAJOR `X+1.0.0` |

Le serveur MCP (`.mcp.json` → `version`) suit sa propre version indépendante.
Il NE force PAS un bump du plugin — sauf si l'interface MCP change.

### Checklist avant chaque commit

```
□ Ai-je modifié scripts/, templates/, data/, ou SKILL.md d'un plugin ?
  → Oui : bump PATCH dans les 2 champs du plugin concerné
□ Ai-je ajouté un outil ou changé le comportement visible ?
  → Oui : bump MINOR dans les 2 champs du plugin concerné
□ Les 2 versions du plugin sont-elles identiques ?
  → grep -E '"version"' .claude-plugin/marketplace.json plugins/<plugin>/.claude-plugin/plugin.json
□ Ai-je ajouté l'entrée `## <plugin> <version>` dans CHANGELOG.md ?
□ Ai-je incrémenté le `version` top-level de marketplace.json d'un PATCH (+0.0.1) ?
  (compteur monotone — toujours +0.0.1 à chaque release, indépendant des versions plugins)
□ `bash scripts/check_version_sync.sh` passe (exit 0) ?
```
