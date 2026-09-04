---
name: apply-to-offer
description: >
  Turn a job offer Renaud found himself into a CV and a logged candidature, in
  one step. Give it a LinkedIn URL or a job id: it reads the job description via
  read-job-offer, checks the offer is not already in the vault, and spawns the
  cv-log-worker agent, which runs the comp gate, generates the 1-page PDF CV and
  logs the candidature as "📝 À postuler". This is the daytime counterpart of the
  morning-briefing fan-out — same worker, same output, manual trigger. Use when
  Renaud says "postule à cette annonce", "génère le CV pour", "je veux postuler",
  "prépare ma candidature", or simply pastes a `linkedin.com/jobs/view/` URL and
  asks for a CV. It never submits an application and never writes a cover letter.
allowed-tools: "Skill(read-job-offer) Skill(jobsearch-vault) Agent(cv-log-worker)"
---

# Apply To Offer — Skill Instructions

## What this skill does

One offer in, one CV and one logged candidature out — for an offer Renaud found during the day
rather than in the morning digest.

It is deliberately **thin**. It owns no judgement: `read-job-offer` reads, `cv-log-worker` decides
and produces, `log-application` records. Its value is being a trigger and a dedup gate. Anything
else it starts doing is duplication of the morning path, which is the exact drift this skill exists
to prevent.

## Step 1 — Resolve what Renaud pasted

Accept any of: a `linkedin.com/jobs/view/<id>` URL, a search URL carrying `currentJobId=<id>`, a
bare numeric `job_id`, or a URL on another job board.

- **LinkedIn** → extract the `job_id` and build `JOB_URL` as
  `https://www.linkedin.com/jobs/view/<job_id>`.
- **Another board** → keep the URL as `JOB_URL`. `read-job-offer` only covers LinkedIn, so say
  plainly that the JD cannot be auto-read, and ask Renaud to paste the offer text. Do **not**
  invent a JD from the page title.
- **Nothing resolvable** → ask for the link. Never guess an id.

## Step 2 — Read the offer

Invoke `Skill(read-job-offer)` with the resolved `job_id` or URL. Keep `title`, `company`,
`jd_text`, `freshness` and `applicant_count`.

If it returns `status: unavailable`, stop and say so, naming the reason it gave. Offer the fallback:
Renaud pastes the offer text, and this skill passes it through as `JD_TEXT`. Never continue with a
partial read.

## Step 3 — Dedup against the vault

Invoke `Skill(jobsearch-vault)` to list active candidatures, and compare on **company + role**.

- **Match found** → do not spawn anything. Report the existing candidature: its status, its date,
  and the path of its note, so Renaud can pick up the existing process rather than start a second
  one. Ask before proceeding anyway.
- **No match** → continue.

This is the same dedup rule as `morning-briefing` Step 1g. An offer already logged is never
re-processed silently.

## Step 4 — Spawn the worker

Spawn exactly one `cv-log-worker` agent with:

```
JOB_URL: <resolved URL>
DATE: <today, YYYY-MM-DD, Europe/Paris>
JD_TEXT: <jd_text from Step 2 — omit the line entirely if Renaud pasted nothing and Step 2 succeeded>
JOB_TITLE: <title from Step 2, if known>
COMPANY: <company from Step 2, if known>
```

Do **not** pass `SENDER_EMAIL`: its absence is what makes the worker record `source: manual`, which
is how a daytime application is told apart from a digest one in the vault.

<!-- TODO: verify in Cowork — `cv-log-worker` is defined in the `briefing` plugin and spawned here
     from `jobsearch`. Cross-plugin Agent() resolution is unverified; if it fails, the worker
     definition moves to `jobsearch` and `morning-briefing` spawns it across the same boundary
     (it already calls Skill(jobsearch-vault) that way). -->

## Step 5 — Report

Relay the worker's one-line summary verbatim, then add the two things Renaud acts on:

- the **PDF path**, so he can open it;
- what is still his to do — the candidature is `📝 À postuler`, nothing was submitted.

If the worker returned `ÉCARTÉ` (compensation below the floor), say so and stop. If it returned
`ÉCHEC`, relay the reason without retrying: a second attempt on the same failing read produces the
same failure and costs another BrightData call.

## Constraints (load-bearing)

- **Never submit an application.** No form, no "Apply" button, no job portal interaction, ever.
- **Never write a cover letter.** `cover-letter` is a separate, explicitly-invoked skill.
- **Never send a message to a person.** Not to a recruiter, not to a contact.
- **One offer per invocation.** If Renaud pastes several links, process them one at a time and say
  which one you are on — never fan out from here. Parallel fan-out belongs to `morning-briefing`.
- **Never build a CV from a snippet.** If the JD could not be read, the answer is "give me the
  text", never a CV written from a title.
- **Status is `📝 À postuler`** — the worker logs it; Renaud moves the card himself once he has
  actually applied.
- **Compose, do not reimplement.** The read, the comp gate, the CV and the log all live in skills
  that already exist. This skill resolves, dedups, spawns, reports — nothing else.
