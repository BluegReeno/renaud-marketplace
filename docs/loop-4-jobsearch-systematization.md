# Loop 4 — Jobsearch systematization (log + interview-prep) → STOP

> **Repo**: `renaud-marketplace` + Obsidian vault · **Target**: `jobsearch` plugin (new skills).
> **Depends on**: Loop 3 (briefing surfaces the relances) and the existing `cv-generator` (5 profiles).
> Relocated from `hal/docs/features/loop-4-jobsearch-systematization.md` (Archon runs from this repo).
> **This is the last loop. After it merges and is used, development stops.**

## Context (Renaud's own diagnosis)

Six months of job search produced one lesson: **focus**. Each interview currently starts with
"you're a different profile". The fix is a *systematic* process, not more tools:
- when applying → always log the same things (annonce, source, target profile);
- when preparing → always the same structure, adapted to the target profile.

The `cv-generator` already encodes 5 profiles (P1 architecte, P2 lead/manager, P3 CTO,
P4 CS/FDE, P5 sales/bizdev). These two skills reuse that taxonomy — no new positioning system.

## Deliverables (two skills)

### Skill A — `log-application`
On applying to an offer, create/update one **Obsidian candidature note** (jobsearch lives in
Obsidian, not hal) with a fixed shape: société, annonce (text/URL), **source** (LinkedIn / WTTJ /
direct / referral…), date, **target profile (P1–P5)**, stage. Then create a **follow-up relance
task in Obsidian** (via `obsidian-crm`). The morning-briefing (Loop 3) then surfaces it.

### Skill B — `interview-prep`
Given a candidature, produce a prep document with the **always-identical structure**:
1. Société (what they do, context)
2. Résumé de la job description
3. Pitch (positioned for the **target profile** — P1–P5, so the narrative is consistent with the CV)
4. Cas du parcours pertinents pour cette candidature
5. Questions probables de l'interlocuteur

Pulls candidature context from the Obsidian note + the stored annonce. The profile drives the
positioning so each interview presents **one coherent profile**, not a different one each time.

## Non-goals

- **No auto-scraping** of job boards, no auto-apply, no email automation beyond existing
  `gmail-mcp` drafts. Offer *sourcing* stays manual; the skill only classifies a pasted offer
  against the P1–P5 profiles.
- No migration of jobsearch into hal — it stays in Obsidian.
- No new CV system — reuse `cv-generator`'s profiles.
- No interview-feedback/CRM-of-interviews beyond the Obsidian note.

## Acceptance criteria

1. `log-application` with a pasted offer → an Obsidian candidature note with all fixed fields
   populated (incl. source + target profile) **and** a relance task that shows up in tomorrow's brief.
2. `interview-prep` for that candidature → a doc with the 5 fixed sections, the pitch written
   for the declared profile.
3. Two preps for two different profiles produce **consistently structured** docs with
   **profile-appropriate** pitches (not generic).

---

## After this merges

Update `hal/docs/lastdev-plan.md`: mark all loops ✅. **The backend has been frozen since Loop 1;
now skills are done too.** Any further idea goes to the backlog and is weighed against the
stopping rule — does it directly produce a job interview or Blue Green revenue? If not, it waits.
