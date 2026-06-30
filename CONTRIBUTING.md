# Contributing — Versioning rules

## Versioning — règle critique Cowork

**Cowork détecte les mises à jour exclusivement par numéro de version.**
Sans bump de version, les utilisateurs installés ne reçoivent jamais le fix.

### Les 3 champs à garder en sync (par plugin)

Pour **chaque plugin**, ces 3 champs doivent être identiques :

| Fichier | Champ | Exemple (`briefing`) |
|---------|-------|----------------------|
| `.claude-plugin/marketplace.json` | `plugins[].version` (entrée du plugin) | `"0.1.0"` |
| `plugins/<plugin>/.claude-plugin/plugin.json` | `version` | `"0.1.0"` |
| `plugins/<plugin>/skills/<skill>/SKILL.md` | `version:` frontmatter | `0.1.0` |

Si un seul dérive → Cowork ne détecte plus les mises à jour ou refuse l'installation.

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
  → Oui : bump PATCH dans les 3 champs du plugin concerné
□ Ai-je ajouté un outil ou changé le comportement visible ?
  → Oui : bump MINOR dans les 3 champs du plugin concerné
□ Les 3 versions du plugin sont-elles identiques ?
  → grep -E '"version"' .claude-plugin/marketplace.json plugins/<plugin>/.claude-plugin/plugin.json
  → grep "^version:" plugins/<plugin>/skills/*/SKILL.md
□ Ai-je incrémenté le `version` top-level de marketplace.json d'un PATCH (+0.0.1) ?
  (compteur monotone — toujours +0.0.1 à chaque release, indépendant des versions plugins)
```
