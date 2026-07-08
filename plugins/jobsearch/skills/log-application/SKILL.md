---
name: log-application
description: >
  Log a job application end-to-end: classify the pasted offer against the P1–P5
  profile taxonomy from `cv-generator`, then invoke the `jobsearch-vault`
  skill to create (or update) one `opportunite-js` candidature note with all
  fixed fields (`entreprise`, `statut`, `source`, `target_profile`,
  `date_candidature`, `date_relance`, `lien_offre`, body = pasted offer) and
  create one hal task (relance) tagged `jobsearch` with `due_date: today + 7d`
  so it surfaces in `/briefing` on its due date. The `opportunite-js` note stays
  in the vault; the relance task lives in hal (`renaud` workspace) like all
  other tasks. Use when the user says "log application", "j'ai postulé",
  "candidature envoyée", "je viens de candidater", "track application",
  "log apply", or pastes a job offer with intent to file it.
allowed-tools: "Skill(jobsearch-vault) mcp__hal-mcp__list_tasks mcp__hal-mcp__create_task"
---

# Log Application — Skill Instructions

## What this skill does

Take a pasted job offer plus a declared source (LinkedIn / WTTJ / direct / referral / other), classify it against the existing P1–P5 profile taxonomy from `cv-generator`, then invoke the `jobsearch-vault` skill to write the candidature trail into Obsidian: one `opportunite-js` note in `CRM-JobSearch/Opportunites/` with every fixed field populated. Then create one hal task (relance) in the `renaud` workspace tagged `jobsearch` with `due_date` 7 days out — consistent with where all other tasks live (mobile, Codex, Dust all read from hal). This skill NEVER touches the vault directly — all vault reads and writes flow through `jobsearch-vault`.

## Step 0 — Inputs you need from the user

Collect (and confirm) the following before doing anything else:

1. **Pasted offer text** (required) — the job description body. The skill will not fetch URLs; the user pastes the text.
2. **Company name** and **role title** — extract from the offer body if obvious, otherwise ASK. They drive the candidature title `<Poste> — <Entreprise>` and the `entreprise` frontmatter.
3. **`source`** (required, one of: `linkedin-alert` / `linkedin-inmail` / `wttj` / `freelance` / `direct-ats` / `headhunter` / `referral` / `other`) — **auto-detected from sender email** when invoked by the `cv-log-worker` sub-agent (see table below). **ASK** if not provided and not auto-detectable. No silent default.

   **Auto-detection table (sender → source)**:

   | Sender email contains | `source` |
   |-----------------------|----------|
   | `jobalerts-noreply@` or `jobs-listings@linkedin.com` | `linkedin-alert` |
   | `messaging-digest-noreply@linkedin.com` | `linkedin-inmail` |
   | `welcometothejungle.com` | `wttj` |
   | `collective.work` or `malt.com` | `freelance` |
   | `taleez` / `myworkday` / `smartrecruiters` / `lever` / `greenhouse` | `direct-ats` |
   | named recruitment firm (cabinet) | `headhunter` |
   | not matched | `other` |

4. **`source_detail`** (optional, free text) — sender name or cabinet identifier, e.g. `"LinkedIn Job Alerts"` or `"Yotta — Expert recrutement Data/AI"`. Enables per-channel conversion tracking. **Omit entirely** if not available — do NOT pass an empty string.

5. **`lien_offre`** (optional URL) — **omit the key entirely** if the user has no link (e.g. referral-only). Do NOT pass an empty string `""`: the `url`-typed field warns on it (see Step 3).

6. **`statut`** (optional, default: `"✉️ Candidature envoyée"`) — pass `"📝 À postuler"` when invoked from the `cv-log-worker` fan-out context (CV generated, not yet sent). **Only two values are valid**: `"✉️ Candidature envoyée"` and `"📝 À postuler"`. Any other value → reject with an explicit error before proceeding.

7. **`cv_path`** (optional) — relative path of the generated PDF (e.g. `jobsearch/CV_Poste_Entreprise.pdf`). Provided by `cv-log-worker` when a CV was successfully generated. If present, a `## CV généré` section is appended to the note body. Omit if no CV was generated.

8. **`cv_profile`** (optional) — detected profile slug (e.g. `P4`). Provided alongside `cv_path` by `cv-log-worker`. Omit if no CV was generated.

Do not proceed until `source` and `entreprise` + `poste` are settled.

## Step 1 — Classify the offer against P1–P5

Use the profile detection table from `cv-generator` (REUSED VERBATIM — do not invent a new classifier):

| Profile | Key signals in the job offer |
|---------|------------------------------|
| **P1** `p1` — AI Architect / Solution Architect | "architect", "solution architect", "applied AI", "technical lead" (client-facing), "GenAI deployment", "pre-sales architect" |
| **P2** `p2` — AI Lead / Manager | "AI lead", "head of AI", "practice lead", "manager", "team lead", "responsable IA" |
| **P3** `p3` — CTO | "CTO", "Chief Technology Officer", "technical co-founder", "VP Engineering" |
| **P4** `p4` — Customer Success / FDE | "customer success", "forward deployed engineer", "solutions engineer", "SE", "FDE", "customer onboarding" |
| **P5** `p5` — Sales / BizDev | "account executive", "AE", "business development", "BDM", "sales", "commercial" |

Default if ambiguous: **P1** (`target_profile: "P1"`). When two profiles plausibly match, report it to the user as "ambiguous between P<x>/P<y>, defaulting to P1 — say P<y> to override" and proceed. The candidature note only needs the profile half; T1–T5 company-type is a `cv-generator` concern and is NOT written here.

Set `target_profile` to one of the literal strings `"P1"`, `"P2"`, `"P3"`, `"P4"`, `"P5"`.

## Step 2 — Resolve dates

- `date_candidature` = today, formatted `YYYY-MM-DD`, Europe/Paris.
- `date_relance` = `date_candidature + 7 days`, formatted `YYYY-MM-DD`.

## Step 3 — Check for existing candidature (idempotency)

macOS APFS is case-insensitive; two candidatures with the same name will collide. Re-applying to the same role must not silently fail. Invoke `jobsearch-vault` to search `CRM-JobSearch/Opportunites/` for a note matching `entreprise` + `poste`:

**Match semantics** (binding): exact filename `"<Poste> — <Entreprise>.md"` (em-dash with spaces, case-insensitive — APFS-equivalent). Substring or fuzzy matches MUST NOT be treated as hits. If `jobsearch-vault` returns >1 result for the exact filename (theoretically impossible but allow for upstream bugs), ASK the user which one — do NOT auto-pick.

- **If found** → ask `jobsearch-vault` to update the candidature (`update_frontmatter`), refreshing `statut`, `source`, `target_profile`, `date_relance` (keep the original `date_candidature` from the existing note). Report to the user that an existing candidature was updated, not created.
- **If not found** → ask `jobsearch-vault` to create the note with the full payload below.

### `opportunite-js` creation payload

Invoke `jobsearch-vault` and ask it to **create a note** with exactly this structured request (it runs `create_note.py` internally):

```json
{
  "name":"<Poste> — <Entreprise>",
  "type":"opportunite-js",
  "folder":"CRM-JobSearch/Opportunites",
  "fields":{
    "entreprise":"[[<Entreprise>]]",
    "statut":"<statut — default: ✉️ Candidature envoyée>",
    "source":"<linkedin-alert|linkedin-inmail|wttj|freelance|direct-ats|headhunter|referral|other>",
    "source_detail":"<source_detail — OMIT KEY if empty>",
    "date_candidature":"<YYYY-MM-DD>",
    "date_relance":"<YYYY-MM-DD +7d>",
    "lien_offre":"<url — OMIT KEY if no URL>",
    "target_profile":"P<1-5>"
  },
  "body":"## Annonce\n\n<pasted offer text, verbatim>\n"
}
```

When `cv_path` is provided (i.e. invoked from `cv-log-worker` after a successful CV generation), append a `## CV généré` section to the body:

```
## CV généré

- Profil : <cv_profile>
- Fichier : <cv_path>
```

Omit the section entirely when `cv_path` is not provided.

`source_detail` — **include the key ONLY when a value exists; omit it entirely otherwise** (same rule as `lien_offre`). If `jobsearch-vault` returns an `unknown field 'source_detail'` warning on stderr, apply the same AC1 contract: exit 0 + this specific warning → ACCEPT (non-blocking unknown field, same as `target_profile`).

`target_profile` is NOT in the `opportunite-js` schema → `jobsearch-vault` prints a non-blocking warning to stderr (the documented escape hatch — the field is still written). The agreed contract is:

- **Exit 0 + stderr contains `unknown field 'target_profile'`** → ACCEPT. The candidature was written. Do not retry.
- **Exit 0 + any OTHER stderr warning** → SURFACE the warning to the user verbatim, then proceed. Do not silently swallow it (a future `jobsearch-vault` schema change might surface here first).
- **Non-zero exit** → FAIL HARD per the rule below. The candidature was NOT written.

Adding `target_profile` to the global schema is out of scope for this skill — the warning is the agreed-upon escape hatch.

`lien_offre` is a `url`-typed field: **include the `"lien_offre"` key ONLY when a real URL exists; omit it entirely otherwise** (referral / no-link cases). Passing an empty string `""` triggers a spurious `value "" does not look like a URL` warning that the contract above would force you to surface to the user on every link-less application — so drop the key instead of sending `""`.

**Check Step 3's exit code before proceeding.** `create_note.py` / `update_frontmatter.py` exit 0 on success (including the non-blocking `target_profile` warning above). Any non-zero exit means the candidature was NOT written: report `❌ Échec création candidature — <stderr>` to the user and **DO NOT proceed to Step 4 or fire the Step 5 success report.** This is the AC1 invariant — no half-states, no silent success.

## Step 4 — Create the relance task in hal

The relance lives in hal (`renaud` workspace), not the Obsidian vault. This makes it accessible from any instance (mobile, Codex, Dust) consistent with all other tasks.

**Idempotency on re-apply.** Before creating, call `mcp__hal-mcp__list_tasks(workspace_slug="renaud")` and skip if a non-closed task with the exact same title already exists. Match on title equality (not substring). If found, skip creation — the relance is already tracked.

**If `list_tasks` fails**, proceed with `create_task` anyway and prepend a warning to the Step 5 output:
`⚠️ idempotency pre-check failed (<error>) — attempting create; re-run may create a duplicate if the task was already present.`
Then apply the standard failure handling below if `create_task` also fails.

Invoke `mcp__hal-mcp__create_task` exactly once with:

```
mcp__hal-mcp__create_task(
  workspace_slug = "renaud",
  title          = "Relance — <Entreprise> — <YYYY-MM-DD candidature>",
  description    = "Relance — <statut_label: 'candidature envoyée' si ✉️, 'à postuler' si 📝> le <YYYY-MM-DD> via <source><, source_detail if present>. Vérifier réponse, sinon LinkedIn message au recruteur.",
  tags           = ["jobsearch"],
  due_date       = "<YYYY-MM-DD +7d>"
)
```

No `sprint_id` — jobsearch tasks track tags, not sprints; `/briefing` falls back to open tasks when no active sprint is set on the workspace.

**Failure handling.** If `mcp__hal-mcp__create_task` fails (non-zero / exception) but Step 3 succeeded, the vault is in a **half-state**: the candidature note exists, the relance task does not, `/briefing` will silently miss the relance. Report explicitly:

```
⚠️  Half-state — candidature loguée, relance NON créée dans hal.
    Erreur        : <error>
    Impact        : la relance n'apparaîtra pas dans /briefing ni dans hal renaud/jobsearch.
    Recovery A    : re-run /log-application (Step 3 idempotency court-circuite vers Step 4)
    Recovery B    : créer manuellement une tâche hal renaud avec
                    tags: ["jobsearch"] · due_date: <YYYY-MM-DD +7d>
                    · title: "Relance — <Entreprise> — <YYYY-MM-DD>"
```

Do NOT fire Step 5's success report on a half-state.

## Step 5 — Report to the user (in French)

Render a concise summary, in French:

```
✅ Candidature loguée — <Poste> chez <Entreprise>
   📁 Note     : CRM-JobSearch/Opportunites/<Poste> — <Entreprise>.md
   🎯 Profil   : P<n> (<short label, e.g. "CTO" or "Architect">)
   🔄 Relance  : <YYYY-MM-DD +7d> — tâche hal renaud/jobsearch créée, apparaîtra dans /briefing
   🔗 Source   : <source> (<source_detail if present, else omit>)
   📌 Statut   : <statut>
```

If the candidature already existed and was updated rather than created, change the first line to `🔁 Candidature mise à jour — …` and include the original `date_candidature`.

If the user has not yet generated a CV for this offer, suggest running `/cv-generator` next (with the same offer text and target profile).

## Step 6 — Constraints (load-bearing)

- **All vault I/O via `jobsearch-vault`.** NEVER `Read` or `Write` the vault filesystem directly. `allowed-tools` lists `Skill(jobsearch-vault)` for vault I/O, `mcp__hal-mcp__list_tasks` for Step 4 idempotency, and `mcp__hal-mcp__create_task` for the hal relance task — do not work around it.
- **Relance lives in hal only.** The `opportunite-js` note in `CRM-JobSearch/Opportunites/` is the canonical candidature trail in the vault. The relance task is in hal (`renaud` workspace, tag `jobsearch`) — not a vault `tache`. This is consistent with all other tasks (accessible from mobile, Codex, Dust).
- **First-apply `statut` default is `✉️ Candidature envoyée`** (with emoji, verbatim). When called from the `cv-log-worker` fan-out context, use `"📝 À postuler"` instead (CV generated but not yet submitted). Only these two values are accepted — reject any other value explicitly in Step 0. Do NOT set `🔄 Relance à faire` here; the relance is carried by the `tache`, not the candidature `statut`.
- **Relance `etat` is `Pas commencée`** (verbatim, including accent).
- **Wikilinks**: `entreprise` is `"[[<Entreprise>]]"`, the task's `opportunite` is `"[[<Poste> — <Entreprise>]]"` (em-dash with spaces, matching the candidature title exactly).
- **`target_profile` warning is expected.** It is non-blocking. Do not retry without the field; do not patch the global schema from here.
- **`source_detail` warning may appear.** If `jobsearch-vault` returns `unknown field 'source_detail'` on stderr at exit 0, apply the same AC1 contract as `target_profile`: non-blocking, ACCEPT. Surface any OTHER exit-0 stderr warning verbatim.
- **`source` is mandatory.** If the user did not state one, the skill ASKS in Step 0 before proceeding. No silent default. Valid values: `linkedin-alert` / `linkedin-inmail` / `wttj` / `freelance` / `direct-ats` / `headhunter` / `referral` / `other`.
- **`source_detail` is optional.** Include the key ONLY when a non-empty value is available. Never pass an empty string.
- **Idempotency on re-apply.** Step 3 must search before creating, and switch to `update_frontmatter.py` when the note exists. Do not let `create_note.py` fail-then-retry-by-rename.
- **No auto-apply, no email, no CV attach.** The skill files the trail; the user submits the application themselves. `cv-generator` handles the PDF — invoke it separately via `/cv-generator`.
- **Compose, do not reimplement.** This skill is orchestration: classify, compose JSON payloads, and call `jobsearch-vault`. It does not re-implement vault writes.
