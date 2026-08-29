---
name: mail-triage
description: >
  Scan both mail inboxes (Gmail perso + Gmail pro) over a configurable window
  (default 7 days), cross-reference senders against HAL CRM contacts, companies,
  and projects plus the Obsidian jobsearch vault, then classify each thread into
  domain-specific categories and recommend a concrete action per thread. Trigger: /mail,
  "scan mes mails", "quoi dans ma boîte", "trie mes mails", "classifie mes mails".
allowed-tools: "mcp__plugin_hal_hal-mcp__whoami mcp__plugin_hal_hal-mcp__list_contacts mcp__plugin_hal_hal-mcp__list_companies mcp__plugin_hal_hal-mcp__list_projects mcp__plugin_hal_hal-mcp__list_tasks mcp__plugin_hal_hal-mcp__list_sprints mcp__plugin_briefing_gmail-mcp__search_emails mcp__plugin_briefing_gmail-mcp__read_email mcp__claude_ai_Gmail__search_threads mcp__claude_ai_Gmail__get_thread Skill(jobsearch-vault)"
---

# Mail Triage — Skill Instructions

## What this skill does

Exhaustive triage of both mail inboxes over a configurable window (default **7 days**). For
each thread: resolve the sender/subject against HAL CRM context and the Obsidian jobsearch
vault, classify into a domain-specific category, and recommend a concrete action.

**Parameter**: `N=<days>` in the prompt overrides the default window (e.g. "trie mes mails des 3 derniers jours").

**Relationship with `morning-briefing`**: that skill does a lightweight, daily-integrated mail
pass (Steps 1e/1f) — sufficient for a briefing, not for dedicated triage. This skill is
intentionally deeper: exhaustive scan, explicit per-thread classification, action
recommendations. The two skills are independent by design — running both in the same session
is valid (different depth and goal). Do NOT attempt to call this skill from inside
`morning-briefing` to consolidate logic — the shallow pass in the briefing is intentionally
faster and context-lighter.

Any backend that is unreachable renders a loud `⚠️ <source> DOWN — <reason>` line. Silent
omission is a critical failure.

---

## Step 0 — Pre-flight

Probe each backend independently. Do NOT bail on the first failure — all probes run regardless.

- **hal-mcp probe**: call `mcp__plugin_hal_hal-mcp__whoami`. Assert **resolvability, not identity**: it must answer and return at least one workspace in `workspaces[]`. On call failure → mark `hal:DOWN <reason>`, skip Steps 1a-1c. If it answers but `workspaces[]` is empty → mark `hal:DOWN no workspace — whoami returned <the actual payload received>` and skip Steps 1a-1c: with no workspace there is no CRM context to load. Never assert a specific email or slug — Step 1 iterates on whatever `whoami` returns.
- **Gmail perso probe**: call `mcp__plugin_briefing_gmail-mcp__search_emails` with a minimal query (`after:2000/01/01 maxResults:1`). On failure → mark `gmail-perso:DOWN <reason>`, skip Step 2a.
- **Gmail pro probe**: call `mcp__claude_ai_Gmail__search_threads` with a minimal query. On failure → mark `gmail-pro:DOWN <reason>`, skip Step 2b.
- **jobsearch-vault probe**: attempt a small read (list active candidatures via `Skill(jobsearch-vault)`). On failure → mark `jobsearch:DOWN <reason>`, skip vault matching in Step 3.

---

## Step 1 — Load HAL CRM context

If `hal:DOWN`, skip all sub-steps and proceed to Step 2 with empty context.

Run all sub-steps in parallel.

### 1a — Opportunities, tasks, contacts and companies (one loop over every workspace)

Do NOT hardcode any slug. For **each** workspace `w` in `whoami.workspaces`, in parallel:

```
if w.sprints_enabled:
  mcp__plugin_hal_hal-mcp__list_sprints(workspace_slug=w.workspace_slug, status="actuel")
    → take the first entry's id
  mcp__plugin_hal_hal-mcp__list_tasks(workspace_slug=w.workspace_slug, sprint_id=<id>)
    (or list_tasks without sprint_id if no active sprint)
else:
  mcp__plugin_hal_hal-mcp__list_tasks(workspace_slug=w.workspace_slug)
mcp__plugin_hal_hal-mcp__list_projects(workspace_slug=w.workspace_slug)
mcp__plugin_hal_hal-mcp__list_contacts(workspace_slug=w.workspace_slug)
mcp__plugin_hal_hal-mcp__list_companies(workspace_slug=w.workspace_slug)
```

<!-- TODO: verify in Cowork — list_projects may accept a kind="opportunity" filter. Not confirmed in tool schema. If it does, use kind="opportunity" to narrow results. -->

`list_tasks` returns `{tasks: [...], total: <n>, returned: <n>, truncated: <bool>}`, not a bare
array — read the task list from `.tasks`. If `truncated` is `true`, note it alongside
`tasks_by_ws[w]` (e.g. `tasks_by_ws[w].truncated = true`) so Step 5 can flag that the workspace's
task view was partial instead of silently matching mails against an incomplete list.

Collect, keyed by workspace: `projects_by_ws[w]` (title, stage, key contacts), `tasks_by_ws[w]` (title, tags), and a lookup map `email → {name, company, linked_project_title, workspace_name}` merged across all workspaces for use in Step 3 matching. When two workspaces resolve the same sender email, keep both and prefer the match whose workspace also owns the thread's inbox signal (Step 3).

### 1b — Active jobsearch candidatures

If `jobsearch:UP`: invoke `Skill(jobsearch-vault)` and ask for the list of active candidatures
(company + role + current stage + recruiter email if known). **READ-ONLY** — do not write the vault.

Collect: `active_candidatures[]` (company, role, stage, recruiter_email if any).

---

## Step 2 — Scan inboxes

Run 2a and 2b in parallel.

### 2a — Gmail perso (via `mcp__plugin_briefing_gmail-mcp__*`)

Which inbox is scanned is decided by **which MCP server is called**, never by an address string — this block always targets the perso inbox because it calls `mcp__plugin_briefing_gmail-mcp__*`.

Skip if `gmail-perso:DOWN`.

```
mcp__plugin_briefing_gmail-mcp__search_emails(
  query="newer_than:<N>d -label:newsletters -category:promotions",
  maxResults=50
)
```

For each result, call `mcp__plugin_briefing_gmail-mcp__read_email(id=<email_id>)` to get sender,
subject, snippet, and body. Automated digests (from no-reply addresses) — subject + sender +
snippet is sufficient for classification; skip full body read.

Collect: `perso_threads[]` (id, sender_email, subject, snippet, date).

### 2b — Gmail pro (via `mcp__claude_ai_Gmail__*`)

This block always targets the pro inbox because it calls `mcp__claude_ai_Gmail__*` — the address is never named.

Skip if `gmail-pro:DOWN`.

```
mcp__claude_ai_Gmail__search_threads(
  query="newer_than:<N>d -label:newsletters -label:promotional",
  maxResults=50
)
```

For each result, call `mcp__claude_ai_Gmail__get_thread(id=<thread_id>)` to get sender,
subject, and first-message snippet.

Collect: `pro_threads[]` (id, sender_email, subject, snippet, date).

---

## Step 3 — Classify by domain and context

For each thread in `perso_threads[]` and `pro_threads[]`, apply the following resolution in order:

1. **CRM lookup**: match `sender_email` against the merged HAL contacts map (Step 1a). A match → candidate for the Blue Green (business) domain even if the thread arrived in the perso inbox (forward/CC scenario).
2. **Vault lookup**: match `sender_email` or company name extracted from subject/snippet against `active_candidatures[]` (Step 1b). A match → jobsearch domain.
3. **Inbox signal (default)**: perso inbox threads not matched to CRM → jobsearch domain. Pro inbox threads not matched to vault → Blue Green (business) domain.

### Jobsearch categories (Gmail perso or matched from vault)

| Category | Classification signal |
|----------|-----------------------|
| `réponse_positive` | Keywords: "retenu", "entretien", "invitation", "sélectionné", "interview", "would like to discuss" — from a company/recruiter matching an active candidature or from an inbound recruiter |
| `réponse_négative` | Keywords: "ne pas retenir", "candidature non retenue", "thank you for applying", "n'avons pas retenu", "décliné", "unfortunately" |
| `silence` | Thread matched to active candidature where last inbound reply is older than N days — no new content from the company |
| `relance_possible` | Thread matched to active candidature where the last message was sent BY Renaud and the delay since sending exceeds 7 days with no reply |
| `nouvelle_opportunité` | Inbound recruiter contact or job alert not matched to any active candidature |

### Blue Green categories (Gmail pro or matched from CRM)

| Category | Classification signal |
|----------|-----------------------|
| `nouvelle_demande_client` | Inbound from a sender not in HAL contacts, with keywords: "devis", "projet", "appel d'offres", "besoin", "prestation", "proposition" |
| `relance_commerciale_possible` | Thread matched to a BG project/opportunity where the last sent message is from Renaud and delay > 7 days with no reply |
| `mise_à_jour_projet_en_cours` | Thread matched to an active BG project with a new inbound message (client/partner update) |
| `silence_propale` | Thread matched to a BG opportunity where a proposal was sent (stage ≈ "propale envoyée") with no client reply for > 14 days |
| `administratif` | Invoice, contract notice, subscription, admin communication — not mapped to a CRM opportunity |

### Fallback categories (either inbox)

| Category | Classification signal |
|----------|-----------------------|
| `newsletter` | Automated digest, promotional, no-reply sender, marketing |
| `personnel` | Personal contacts or family — not business-relevant |
| `non_classifié` | Cannot determine domain or intent with available context |

---

## Step 4 — Recommend an action

For each classified thread, attach one concrete action recommendation.

### Jobsearch actions

| Category | Recommended action |
|----------|--------------------|
| `réponse_positive` | Mettre à jour le vault avec la réponse (statut, prochaine étape). Lancer `/interview-prep` si entretien imminent. |
| `réponse_négative` | Archiver la candidature : lancer `/log-application` et mettre le statut à ❌ Refusé. |
| `silence` | Évaluer si une relance est pertinente (délai, contexte, type de poste). Pas d'action automatique. |
| `relance_possible` | Rédiger une relance courte. `/cover-letter` peut aider avec le contexte de relance. |
| `nouvelle_opportunité` | Évaluer le fit (🔥/🟡/❌). Si positif : lancer `/log-application` pour créer la fiche vault. |

### Blue Green actions

| Category | Recommended action |
|----------|--------------------|
| `nouvelle_demande_client` | Qualifier le besoin (BANT : budget, autorité, besoin, timing). Créer une opportunité HAL via `/crm qualify`. |
| `relance_commerciale_possible` | Rédiger une relance propale. Tracer dans HAL : `/crm log`. Mettre à jour le stage : `/crm update`. |
| `mise_à_jour_projet_en_cours` | Répondre et mettre à jour le projet HAL : `/crm update`. |
| `silence_propale` | Décider : relancer ou clore l'opportunité. Tracer la décision : `/crm log`. |
| `administratif` | Traiter ou archiver. Aucune action CRM requise sauf si lié à un projet actif. |

**Note on `/crm` commands**: these refer to the `hal/crm` skill in `bluegreen-marketplace`
(separate repo — not directly callable from `renaud-marketplace`). This skill calls `hal-mcp`
tools for reads. For HAL writes explicitly requested by the user (e.g. logging an interaction),
call `mcp__plugin_hal_hal-mcp__log_interaction` directly rather than delegating to the `/crm` skill.

---

## Step 5 — Render the triage report

Render in **French**. Group by domain. Every classified thread appears exactly once. Skip
empty sub-sections (do not render a section header if it has zero threads).

```
# Triage mails — <date in French> (fenêtre : <N> jours)

## 🎯 Jobsearch — Gmail perso

### réponse_positive (<count>)
- **<company>** — <subject> [<date>]
  → <1-line context : who sent it, what it says>
  → **Action** : <recommended action from Step 4>

### réponse_négative (<count>)
...

### silence (<count>)
...

### relance_possible (<count>)
...

### nouvelle_opportunité (<count>)
...

(aucun mail jobsearch classifié  |  ou : ⚠️ Gmail perso DOWN — <reason>)

## 💼 Blue Green — Gmail pro

### nouvelle_demande_client (<count>)
- **<sender name or company>** — <subject> [<date>]
  → <1-line context>
  → **Action** : <recommended action>

### relance_commerciale_possible / mise_à_jour_projet_en_cours / silence_propale / administratif
(same format)

(aucun mail BG classifié  |  ou : ⚠️ Gmail pro DOWN — <reason>)

## 📌 Non classifié / Personnel / Newsletter
- <sender> — <subject> [<date>] — <category>
(skip section entirely if empty)

## Source status
hal-mcp : ✅ | ⚠️ DOWN (<reason>)
jobsearch-vault : ✅ | ⚠️ DOWN (<reason>)
Gmail perso : ✅ | ⚠️ DOWN (<reason>)
Gmail pro : ✅ | ⚠️ DOWN (<reason>)
```

The "Source status" footer is mandatory and ALWAYS renders all four lines — even when all sources are healthy.

---

## Step 6 — Constraints (load-bearing)

- **Read-only for all mail** — no draft, send, label, or delete calls. Never invoke `create_draft`, `label_thread`, `label_message`, or any write tool on either Gmail connector.
- **Read-only for vault** — never write to `jobsearch-vault`.
- **No automatic action execution** — this skill classifies and recommends. The user decides and acts. Never auto-call `/log-application`, `/interview-prep`, or any HAL write tool without explicit user confirmation.
- **HAL reads are allowed** — `list_contacts`, `list_companies`, `list_projects`, `list_tasks`, `list_sprints` are safe reads. `log_interaction` and other write tools require explicit user request in the conversation.
- **Classify every thread** — no thread is silently dropped. Unclassifiable threads go to `non_classifié`.
- **Never silently omit a source** — any probe or scan failure renders `⚠️` in the relevant section AND in the source-status footer.
- **Compose, do not bypass** — call `Skill(jobsearch-vault)` for vault access. Never read the Obsidian filesystem directly.
- **Window parameter** — default is 7 days. Accept `N=<days>` override from the user's prompt.
- **Tags.** `tags` means functional domain. Pick only from the calling workspace's `allowed_tags`, returned by `whoami`; if nothing fits, use `other`. Never invent a value, and never put in `tags` what another column already carries (`company_id`, `role`, `channel`, `project_id`). hal-mcp states the full doctrine in its server `instructions` and enforces it on every write.
