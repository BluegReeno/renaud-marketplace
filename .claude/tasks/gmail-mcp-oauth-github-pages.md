# Feature: OAuth Consent Page via GitHub Pages

## Goal
Héberger la consent page OAuth sur GitHub Pages car les Edge Functions Supabase ne peuvent pas servir du HTML aux browsers.

## Context
- **Plan Reference**: `.claude/tasks/gmail-mcp-oauth-consent-github-pages.md`
- **Related Files**: `servers/gmail-mcp/supabase/functions/oauth/`, `servers/gmail-mcp/supabase/config.toml`, `docs/mcp-server-supabase-edge.md`

## Tasks

### Phase 1: Cleanup Edge Function oauth
- [x] Supprimer la Edge Function `oauth` sur Supabase (supabase functions delete) ✓ 2026-06-10
- [x] Supprimer `servers/gmail-mcp/supabase/functions/oauth/` (répertoire) ✓ 2026-06-10
- [x] Retirer `[functions.oauth]` de `servers/gmail-mcp/supabase/config.toml` ✓ 2026-06-10

### Phase 2: Créer la consent page
- [x] Créer `oauth/consent/index.html` (HTML standalone, SDK Supabase via CDN) ✓ 2026-06-10

### Phase 3: Actions manuelles (user)
- [x] Activer GitHub Pages (Settings → Pages → branch main, root) ✓ 2026-06-10
- [x] Mettre à jour Supabase URL config (Site URL + redirect URLs, lowercase) ✓ 2026-06-10
- [x] Corriger Google Client ID + Client Secret dans Supabase Auth → Providers → Google ✓ 2026-06-10
- [x] Ajouter redirect URI Supabase dans Google Cloud Console ✓ 2026-06-10
- [x] Tester la consent page directement sur GitHub Pages ✓ 2026-06-10
- [x] Tester le flow complet depuis claude.ai ✓ 2026-06-10

### Phase 4: Docs
- [x] Mettre à jour `docs/mcp-server-supabase-edge.md` §10 (limitation HTML + solution GitHub Pages) ✓ 2026-06-10
- [x] Mettre à jour `.claude/STATUS.md` ✓ 2026-06-10

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `oauth/consent/index.html` | Create | Consent page OAuth standalone |
| `servers/gmail-mcp/supabase/config.toml` | Modify | Retirer [functions.oauth] |
| `servers/gmail-mcp/supabase/functions/oauth/` | Delete | Supprimer la Edge Function inutile |
| `docs/mcp-server-supabase-edge.md` | Modify | Documenter limitation HTML + GitHub Pages |
| `.claude/STATUS.md` | Modify | Mise à jour sprint |

## Notes
- SUPABASE_URL = "https://isdyvrwnxqcfalmlkzui.supabase.co"
- SUPABASE_ANON_KEY = "sb_publishable_Mlh9cZMB0OTXZyizUexoLw_E512UMqU"
- GitHub Pages URL = "https://BluegReeno.github.io/renaud-marketplace/"
- Google Client ID réel = "869205050842-2854bvloooeelgt4tdtpsuso42bj9n2e.apps.googleusercontent.com"
- Utiliser endpoints REST directs (fetch) plutôt que SDK pour les appels auth avancés

## Completion
- **Started**: 2026-06-10
- **Completed**: 2026-06-10
- **Commit**: 7fca10e
