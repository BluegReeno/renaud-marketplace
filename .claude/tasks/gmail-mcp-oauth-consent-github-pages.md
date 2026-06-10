# Plan : Page consent OAuth via GitHub Pages

## Contexte
La Edge Function `oauth` ne peut pas servir du HTML aux browsers — Supabase force
`Content-Type: text/plain` + `CSP: default-src 'none'; sandbox` sur toutes les Edge
Functions accédées par un browser. Seule solution : héberger la consent page en dehors
de Supabase.

## Solution retenue : GitHub Pages sur ce repo

- Fichier : `oauth/consent/index.html` dans `renaud-marketplace`
- URL résultante : `https://BluegReeno.github.io/renaud-marketplace/oauth/consent`
- SITE_URL Supabase : `https://BluegReeno.github.io/renaud-marketplace`
- La page appelle les endpoints Supabase Auth directement via fetch (pas via Edge Function)

---

## Étapes

### 1. Supprimer la Edge Function `oauth` (inutile)
```bash
cd servers/gmail-mcp
supabase functions delete oauth --project-ref isdyvrwnxqcfalmlkzui
```
Supprimer aussi :
- `servers/gmail-mcp/supabase/functions/oauth/` (répertoire entier)
- La ligne `[functions.oauth]` dans `servers/gmail-mcp/supabase/config.toml`

### 2. Créer `oauth/consent/index.html`

Fichier HTML standalone (pas de build, pas de framework). Logique :
1. Lit `?authorization_id=<uuid>` dans l'URL
2. Vérifie la session Supabase (`sb.auth.getSession()`)
3. Si pas de session → bouton "Connexion avec Google" (`sb.auth.signInWithOAuth`)
4. Si session → `GET /auth/v1/oauth/authorizations/{id}` avec Bearer token
5. Si réponse contient `redirect_url` → auto-approve, redirect immédiat
6. Sinon → affiche nom de l'app + scopes + boutons "Autoriser" / "Refuser"
7. `POST /auth/v1/oauth/authorizations/{id}/consent` avec `{ action: "approve"|"deny" }`
8. Redirect vers `redirect_url` retourné

Variables à injecter en dur dans le HTML (clés publiques, sûres) :
- `SUPABASE_URL = "https://isdyvrwnxqcfalmlkzui.supabase.co"`
- `SUPABASE_ANON_KEY = "sb_publishable_Mlh9cZMB0OTXZyizUexoLw_E512UMqU"`

SDK Supabase via CDN :
```html
<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/umd/supabase.min.js"></script>
```

Attention `redirectTo` dans `signInWithOAuth` : doit pointer vers
`https://BluegReeno.github.io/renaud-marketplace/oauth/consent?authorization_id=<id>`
→ utiliser `location.href` (inclut déjà le `?authorization_id=`)

### 3. Activer GitHub Pages

Dans GitHub → Settings → Pages :
- Source : `Deploy from a branch`
- Branch : `main`, folder : `/ (root)`
- Sauvegarder → GitHub génère `https://BluegReeno.github.io/renaud-marketplace/`

### 4. Mettre à jour Supabase (projet perso `isdyvrwnxqcfalmlkzui`)

**Authentication → URL Configuration :**
- Site URL : `https://BluegReeno.github.io/renaud-marketplace`
- Additional Redirect URLs : ajouter `https://BluegReeno.github.io/renaud-marketplace/**`

**Authentication → OAuth Server :**
- Authorization Path : `/oauth/consent` (déjà configuré, laisser tel quel)
- Vérifier que "Enable Supabase OAuth Server" est ON
- Vérifier que "Allow Dynamic OAuth Apps" est ON

### 5. Tester la consent page directement

```
https://BluegReeno.github.io/renaud-marketplace/oauth/consent
```
→ Doit afficher "Paramètre authorization_id manquant." en rouge (page rendue, pas source)

### 6. Tester le flow complet

Dans claude.ai :
1. Supprimer l'ancien connecteur gmail-mcp
2. Ajouter nouveau connecteur : `https://isdyvrwnxqcfalmlkzui.supabase.co/functions/v1/gmail-mcp`
3. claude.ai → 401 → OAuth discovery → redirige vers la consent page
4. Se connecter avec Google (`rlaborbe@gmail.com`)
5. Cliquer "Autoriser"
6. Vérifier que le connecteur est actif dans claude.ai

### 7. Mettre à jour STATUS.md et docs

- `.claude/STATUS.md` : cocher les tâches OAuth
- `docs/mcp-server-supabase-edge.md` §10 : noter la limitation HTML des Edge Functions
  et documenter la solution GitHub Pages

---

## Gotchas connus

- **`supabase.auth.oauth` namespace** : incertain dans `@supabase/supabase-js@2` via CDN.
  Utiliser les endpoints REST directs (`fetch`) plutôt que le SDK pour
  `getAuthorizationDetails` et `approveAuthorization` — plus fiable.
- **Encodage UTF-8** : dans le fichier HTML statique, les accents fonctionnent normalement
  (c'est un vrai fichier HTML servi par GitHub, pas une Edge Function).
- **Premier déploiement GitHub Pages** : peut prendre 1-2 minutes avant d'être accessible.
- **Google Client ID** : le champ "SecondBrain" dans Supabase Auth → Google est invalide.
  Le vrai Client ID est `869205050842-2854bvloooeelgt4tdtpsuso42bj9n2e.apps.googleusercontent.com`.
  À corriger dans Authentication → Providers → Google avant de tester.
