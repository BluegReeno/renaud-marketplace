# Brief — `update_sprint` MCP tool · repo `hal`

**Contexte** : le sprint-planner crée les sprints avec le bon statut depuis la v0.4.2
(`SPRINT_STATUS = "actuel"` si `NEXT_MON <= TODAY`), mais il n'existe aucun outil pour
corriger un statut après coup. `update_sprint` comble ce vide et permet aussi de renommer
ou déplacer un sprint (dates) sans le supprimer/recréer.

---

## Fichiers à modifier

| Fichier | Nature |
|---|---|
| `hal/supabase/migrations/<timestamp>_halcrm_sprints_updated_at.sql` | Nouvelle migration |
| `hal/supabase/functions/hal-mcp/index.ts` | Nouveau tool + fix list_sprints |

---

## 1. Migration — ajouter `updated_at` à `halcrm_sprints`

**Fichier** : `hal/supabase/migrations/20260616000000_halcrm_sprints_updated_at.sql`

```sql
-- Add updated_at to halcrm_sprints (missing vs. all other CRM tables)
ALTER TABLE halcrm_sprints
  ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT now();
```

Appliquer via `mcp__supabase__apply_migration` (ne jamais utiliser `db push`).

---

## 2. `list_sprints` — inclure `updated_at` dans le SELECT

**Fichier** : `hal/supabase/functions/hal-mcp/index.ts`  
**Localisation** : outil `list_sprints`, lignes ~842–867  
**Chercher** :

```typescript
.select("id, name, sprint_number, status, starts_at, ends_at")
```

**Remplacer par** :

```typescript
.select("id, name, sprint_number, status, starts_at, ends_at, updated_at")
```

---

## 3. Nouveau tool `update_sprint`

**Insérer après l'outil `list_sprints`** (ligne ~867), avant `assign_task_to_sprint`.

### Constante de statuts valides

Les statuts existent déjà en dur dans `create_sprint`. Vérifier si une constante
`SPRINT_STATUSES` est déjà déclarée ; si non, la déclarer au même endroit que les
autres constantes de statuts (près de `TASK_STATUSES`) :

```typescript
const SPRINT_STATUSES = ["passes", "dernier", "actuel", "suivant", "a_venir"] as const;
```

### Implémentation

```typescript
registerTool(
  "update_sprint",
  {
    title: "Update Sprint",
    description:
      "Update an existing sprint: rename it, change its status, or adjust its dates. " +
      "At least one optional field must be provided. " +
      "Valid status values: 'passes' | 'dernier' | 'actuel' | 'suivant' | 'a_venir'. " +
      "Returns the updated sprint object.",
    inputSchema: z.object({
      workspace_slug: z.string().describe("Workspace slug (e.g. 'blue-green' or 'renaud')"),
      sprint_id: z.string().describe("ID of the sprint to update"),
      name: z.string().optional().describe("New sprint name"),
      status: z.enum(SPRINT_STATUSES).optional().describe(
        "New status — 'actuel' for the running sprint, 'suivant' for next week, " +
        "'dernier' for last, 'passes' for archived, 'a_venir' for future"
      ),
      starts_at: z.string().optional().describe("New start date (ISO format YYYY-MM-DD)"),
      ends_at: z.string().optional().describe("New end date (ISO format YYYY-MM-DD)"),
    }),
  },
  async (params, extra: unknown) => {
    const { workspace_slug, sprint_id, name, status, starts_at, ends_at } = params;
    const db = getDb(extra);

    const patch: Record<string, unknown> = {};
    if (name !== undefined) patch.name = name;
    if (status !== undefined) patch.status = status;
    if (starts_at !== undefined) patch.starts_at = starts_at;
    if (ends_at !== undefined) patch.ends_at = ends_at;

    if (Object.keys(patch).length === 0) {
      return errorResult("No fields to update — provide at least one of: name, status, starts_at, ends_at");
    }

    patch.updated_at = new Date().toISOString();

    const { data, error } = await db
      .from("halcrm_sprints")
      .update(patch)
      .eq("id", sprint_id)
      .eq("workspace_slug", workspace_slug)
      .select()
      .maybeSingle();

    if (error) return errorResult(error.message);
    if (!data) return errorResult(`Sprint '${sprint_id}' not found in workspace '${workspace_slug}'`);
    return okResult(data);
  }
);
```

---

## 4. Bump version MCP server

**Chercher** (ligne ~26) :

```typescript
const server = new McpServer({
  name: "hal-mcp-poc",
  version: "0.2.0",
```

**Remplacer** `"0.2.0"` par `"0.2.1"`.

---

## 5. Deploy

```bash
cd hal
supabase link --project-ref zgkvbjqlvebttbnkklpo
supabase functions deploy --no-verify-jwt hal-mcp
```

---

## Cas de test

| Scénario | Paramètres | Résultat attendu |
|---|---|---|
| Statut lundi matin | `status="actuel"` | sprint visible dans morning-briefing |
| Renommer | `name="Sprint 42 — ..."` | nom mis à jour |
| Déplacer dates | `starts_at`, `ends_at` | dates corrigées |
| Aucun champ | — | erreur `"No fields to update"` |
| sprint_id inconnu | ID inexistant | erreur `"not found in workspace"` |
| Mauvais workspace | workspace_slug erroné | 0 row → erreur not found |

---

## Notes

- `sprint_number` est intentionnellement **non modifiable** via ce tool (clé logique, risque
  de collision). Si besoin futur → ajouter après validation UNIQUE en base.
- RLS `halcrm_sprints` existante : `workspace_member access FOR ALL` — déjà couverte,
  aucune migration RLS supplémentaire.
- `getDb` suffit (pas besoin de `getDbAdmin`).
