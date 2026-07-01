---
name: mail
description: >
  Scans the Gmail jobsearch inbox (rlaborbe@gmail.com) for the last 7 days of
  unprocessed recruiter and application emails, classifies each one into one of
  five categories (réponse_positive, réponse_négative, silence, relance_possible,
  nouvelle_opportunité), then proposes the appropriate action with the exact steps
  to execute via the relevant skill (log-application, interview-prep, jobsearch-vault).
  Use when the user says "scan mes mails jobsearch", "nouveaux mails recruteurs",
  "quoi dans ma boîte jobsearch", "emails recruteurs", "vérifie mes mails candidature",
  or asks what recruiters have sent recently.
version: 0.7.0
allowed-tools: "mcp__gmail-mcp__search_emails mcp__gmail-mcp__read_email Skill(jobsearch-vault) Skill(log-application) Skill(interview-prep)"
---

# Mail — Skill Instructions

## What this skill does

Orchestrate a three-step job-search email triage:
1. **Scan** — fetch relevant emails from the last 7 days via `gmail-mcp`
2. **Classify** — assign each email to one of five categories
3. **Act** — present classified emails with the exact action and steps to execute, one by one, waiting for user confirmation

This skill NEVER marks emails as read (the gmail-mcp does not expose that capability). It NEVER touches the vault directly — vault reads and writes flow through `jobsearch-vault`.

---

## Step 1 — Scan Gmail

Call `mcp__gmail-mcp__search_emails` with the following queries (run them sequentially or as many calls as needed):

```
query: "from:linkedin.com OR from:welcometothejungle.com OR from:jobalerts-noreply@ OR subject:recruteur OR subject:candidature OR subject:entretien OR subject:opportunité newer_than:7d"
```

Also run a broader catch-all for direct outreach:
```
query: "subject:(entretien OR interview OR recrutement OR poste OR mission OR opportunité OR relance) newer_than:7d -from:me"
```

Deduplicate results by message ID before proceeding. If `search_emails` returns no results, report:

```
📭 Aucun email recruteur ou candidature trouvé dans les 7 derniers jours.
```

and stop.

<!-- TODO: verify in Cowork — confirm actual parameter names accepted by mcp__gmail-mcp__search_emails (query, limit, etc.) and whether the account is fixed by OAuth or requires a parameter -->

For each email returned by the search, call `mcp__gmail-mcp__read_email` to fetch the full body (subject, sender, date, body snippet). Truncate body to 1000 chars if needed — classification only needs the gist.

---

## Step 2 — Classify each email

For each email, assign exactly **one** category based on the table below. Do not invent categories. When ambiguous, default to `nouvelle_opportunité` and surface the ambiguity to the user.

### Classification table

| Category | Signals |
|---|---|
| `réponse_positive` | Invitation to interview; "nous aimerions discuter"; "entretien" in body; "intéressé par votre profil"; recruiter proposing a call or meeting |
| `réponse_négative` | "nous n'avons pas retenu"; "votre candidature n'a pas été"; "désolé"; "nous avons décidé de ne pas donner suite"; explicit rejection |
| `relance_possible` | Recruiter email with no clear call-to-action; "j'aurais une opportunité"; "je suis chasseur de tête"; InMail without explicit rejection; no reply from a known contact in > 5 days |
| `nouvelle_opportunité` | Job alert from LinkedIn, WTTJ, or ATS; unsolicited offer not yet logged in the vault; direct outreach describing a role not in `CRM-JobSearch/Opportunites/` |
| `silence` | *Not an email* — see §Silence detection below |

### Silence detection (vault cross-query)

`silence` is NOT an incoming email — it is a **known candidature** in the vault that has received no response past its `date_relance`. To detect it:

1. Invoke `Skill(jobsearch-vault)` and ask it to run `list_notes.py` for type `opportunite-js` in `CRM-JobSearch/Opportunites/` where `statut == "✉️ Candidature envoyée"`.
2. Filter client-side: keep notes where `date_relance` ≤ today (2026-07-01).
3. Cross-check the sender list from Step 1 — if one of the retrieved emails is a reply matching the same `entreprise`, do NOT classify that candidature as `silence` (it has a reply).
4. Each remaining note with overdue `date_relance` and no matching inbound email is classified as `silence`.

<!-- TODO: verify in Cowork — confirm that list_notes.py accepts a statut filter or returns all notes (requiring client-side filter) -->

---

## Step 3 — Present and propose actions

Group emails by category and present a structured triage report in French. Then, for each item, propose the exact action with steps — and **wait for user confirmation** before invoking any skill.

### Report format

```
## 📬 Triage Gmail jobsearch — 7 derniers jours

### ✅ Réponses positives (<N>)
1. **<Entreprise>** — <Poste ou sujet>
   De : <sender> le <date>
   Action : préparer l'entretien via `interview-prep`
   Étapes :
     • Invoquer : Skill(interview-prep)
     • Inputs : entreprise=<Entreprise>, poste=<Poste>, date_entretien=<date proposée ou "à confirmer">, type_entretien=RH
   → Confirmer ? (o/n)

### ❌ Refus (<N>)
1. **<Entreprise>** — <Poste ou sujet>
   De : <sender> le <date>
   Action : marquer refus dans le vault via `jobsearch-vault`
   Étapes :
     • Invoquer : Skill(jobsearch-vault)
     • Demander : update_frontmatter "<Poste> — <Entreprise>.md" statut "❌ Refus"
   → Confirmer ? (o/n)

### 🔄 Relances possibles (<N>)
1. **<sender name>** — <sujet>
   De : <sender> le <date>
   Action : créer une tâche relance dans hal via `jobsearch-vault`
   Étapes :
     • Invoquer : Skill(jobsearch-vault)
     • Demander : create_note type=tache, titre="Relance recruteur — <nom>", echeance=<aujourd'hui>, description=<gist de l'email>
   → Confirmer ? (o/n)

### 🆕 Nouvelles opportunités (<N>)
1. **<Entreprise>** — <Poste>
   De : <sender> le <date>
   Source auto-détectée : <linkedin-alert|wttj|headhunter|other>
   Action : logger via `log-application`
   Étapes :
     • Invoquer : Skill(log-application)
     • Inputs : entreprise=<Entreprise>, poste=<Poste>, source=<source>, source_detail=<sender name>
     • Coller le texte de l'offre quand demandé
   → Confirmer ? (o/n)

### 😶 Silences — relance à envisager (<N>)
1. **<Entreprise>** — <Poste>
   Candidature du <date_candidature> · relance due le <date_relance>
   Action : relancer ou abandonner
   Options :
     A. Créer tâche relance → Skill(jobsearch-vault) create_note tache
     B. Marquer abandon → Skill(jobsearch-vault) update_frontmatter statut "🚫 Abandonné"
   → Choisir A, B, ou ignorer ?
```

### Execution after confirmation

- **o / oui / yes / A / B** — invoke the corresponding skill immediately with the pre-filled inputs listed in the step. Do NOT re-ask inputs already extracted.
- **n / non / no / ignorer** — skip, move to the next item.
- **Skip all** — if the user types "tout ignorer" or "next" without confirming, skip remaining items of the current category and move to the next.

### Source auto-detection for `nouvelle_opportunité`

Use the same table as `log-application` (VERBATIM — do not invent new mappings):

| Sender email contains | `source` |
|---|---|
| `jobalerts-noreply@` or `jobs-listings@linkedin.com` | `linkedin-alert` |
| `messaging-digest-noreply@linkedin.com` | `linkedin-inmail` |
| `welcometothejungle.com` | `wttj` |
| `collective.work` or `malt.com` | `freelance` |
| `taleez` / `myworkday` / `smartrecruiters` / `lever` / `greenhouse` | `direct-ats` |
| named recruitment firm (cabinet) | `headhunter` |
| not matched | `other` |

---

## Constraints (load-bearing)

- **No direct vault access.** All vault reads/writes go through `Skill(jobsearch-vault)`. This skill never calls `Read` or `Write` on the vault filesystem.
- **No mark-as-read.** The gmail-mcp does not expose `mark_as_read` or `label_message`. Do NOT promise or attempt to mark emails as processed.
- **Confirmation before action.** NEVER invoke a skill without explicit user confirmation for each item. Present → confirm → execute.
- **Silence is vault-derived, not email-derived.** It comes from overdue `date_relance` in existing `opportunite-js` notes, not from any incoming email.
- **Date filter is client-side.** DQL in `jobsearch-vault` does not support date arithmetic — filter `date_relance <= today` in this skill, not in the DQL query.
- **No auto-log of offers.** `log-application` requires the full offer text pasted by the user. Pre-fill everything extractable from the email (entreprise, poste, source, source_detail), but prompt for the offer body text if missing.
- **Empty categories are silent.** If a category has 0 items, omit its section entirely from the report.
