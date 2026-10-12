---
name: apply-to-offer
description: >
  Turn a job offer Renaud found himself into a CV and a logged candidature, in
  one step. Give it a LinkedIn URL, a job id or the offer's text: it reads the
  job description via read-job-offer when there is no text, checks the offer is not already in the vault, and spawns the
  cv-log-worker agent, which runs the comp gate and the qualitative role gate,
  generates the 1-page PDF CV and logs the candidature as "📝 À postuler". This
  is the daytime counterpart of the
  morning-briefing fan-out — same worker, same output, manual trigger. Use when
  Renaud says "postule à cette annonce", "génère le CV pour", "je veux postuler",
  "prépare ma candidature", or simply pastes a `linkedin.com/jobs/view/` URL and
  asks for a CV. Asked only whether an offer passes the filters, it runs the two
  gates and stops — nothing generated, nothing written. On request it also drafts the short answer an application form asks
  for ("why us", "pourquoi ce poste", a few hundred characters). It never submits an
  application and never writes a full cover letter.
allowed-tools: "Skill(read-job-offer) Skill(jobsearch-vault) Agent(cv-log-worker) mcp__plugin_hal_hal-mcp__whoami mcp__plugin_hal_hal-mcp__list_documents mcp__plugin_hal_hal-mcp__get_document"
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
bare numeric `job_id`, a URL on another job board, the offer's text pasted in the message, or an
offer already stored in hal.

- **LinkedIn** → extract the `job_id` and build `JOB_URL` as
  `https://www.linkedin.com/jobs/view/<job_id>`.
- **Another board** → keep the URL as `JOB_URL`. `read-job-offer` only covers LinkedIn, so say
  plainly that the JD cannot be auto-read, and ask Renaud to paste the offer text. Do **not**
  invent a JD from the page title.
- **Offer text pasted, no link** → that text, verbatim, is `JD_TEXT`; `JOB_URL` stays empty.
  Take `JOB_TITLE` and `COMPANY` from the text when it states them. Skip Step 2: there is nothing
  to read, and the paste is the only source — never complete it from a company row or from what
  such a role usually says.
- **An offer stored in hal** (« l'offre X qu'on a dans hal ») → after `whoami`, find the
  `job-posting` document with `list_documents` on the live `type: "jobsearch"` workspace and read
  it with `get_document`. Its body (`content_md`) is `JD_TEXT` only when it holds at least 500
  characters of posting text. A shorter document — a title and a few facts (salary, place,
  reporting line) — is a summary, not a job description: say so, naming what it holds, ask for
  the offer's URL or its full text, and stop. No gate is scored and no CV is built on a summary.
- **Nothing resolvable** → ask for the link or the text. Never guess an id.

## Step 1.5 — What Renaud asked: the filters only, or the whole flow

- **The filters only** — « est-ce que l'offre passe les filtres ? », « est-ce que je postule ? »,
  « elle passe le plancher ? » → the worker of Step 4 runs with `MODE: gates-only`: it reads the
  thresholds and the disqualifiers, runs both gates, and stops — no CV, no log, nothing written.
  Report its line (Step 5). Offer to continue to the CV only if it passed; never continue
  unprompted.
- **Anything else** (« génère le CV », « postule », a bare link) → the whole flow, `MODE: full`.

The gates are the worker's, in both modes — this skill never reads `comp-thresholds.json` or
`role-criteria.json` itself, and never answers « does it pass? » without the worker's line.

## Step 2 — Read the offer

Skipped when Step 1 already holds the text (pasted, or a stored posting long enough).

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

Spawn exactly one `cv-log-worker` agent, in the foreground (`run_in_background: false`), with:

```
MODE: <gates-only | full, from Step 1.5>
JOB_URL: <resolved URL — omit the line when Step 1 holds pasted text and no link>
DATE: <today, YYYY-MM-DD, Europe/Paris>
JD_TEXT: <the text from Step 1 or Step 2 — omit the line only when Step 2 was skipped for a link the worker reads itself>
JOB_TITLE: <title, if known>
COMPANY: <company, if known>
```

Do **not** pass `SENDER_EMAIL`: its absence is what makes the worker record `source: manual`, which
is how a daytime application is told apart from a digest one in the vault.

<!-- TODO: verify in Cowork — `cv-log-worker` is defined in the `briefing` plugin and spawned here
     from `jobsearch`. Cross-plugin Agent() resolution is unverified; if it fails, the worker
     definition moves to `jobsearch` and `morning-briefing` spawns it across the same boundary
     (it already calls Skill(jobsearch-vault) that way). -->

## Step 5 — Report

Relay the worker's one-line summary verbatim.

`MODE: gates-only` → the line is `PASSE` or `ÉCARTÉ`, with the offer's figure and the floor it was
held against, both as the worker read them. Say nothing was written, and offer the CV if it
passed. Stop there.

`MODE: full` → add the two things Renaud acts on:

- the **PDF path**, so he can open it;
- what is still his to do — the candidature is `📝 À postuler`, nothing was submitted.

If the worker returned `ÉCARTÉ` (compensation below the floor, or a qualitative disqualifier
matched), say so and stop. If it returned
`ÉCHEC`, relay the reason without retrying: a second attempt on the same failing read produces the
same failure and costs another BrightData call.

## Step 6 — Short form-field answer (only on request)

Run this step only when Renaud asks for it — in the same message as the link ("et le champ
'why X'"), or after Step 5. Never by default: most applications have no such field.

Collect, from what Renaud pasted:

- **the field's question**, verbatim (`Why do you want to join X?`, `Pourquoi ce poste ?`);
- **its limit** in characters. If none is given, write for 200 characters and say so.

Read the facts before writing a word. Read the hal document `parcours`. These documents may sit in the job-search or the personal workspace (the split moved only the `jobsearch`-domain ones), so never name a workspace: after `whoami`, try `get_document` on each live workspace of `type: "jobsearch"`, then each live one of `type: "personal"`, and keep the first that answers.
`parcours` is the only source for a claim
about Renaud: an employer, a client, a figure that is not in it does not go in the answer. If the
read fails, stop and say so — never write the answer from memory.

Write one answer:

- in the language of the offer (French offer → French, English → English, never a translation);
- **within the limit**, counted on the final text, and state the count: `(187/200 caractères)`;
- tied to the offer read in Step 2: one concrete thing about this company or role, one fact from
  `parcours` that answers it. No formula (« Je me permets… », "I am pleased to apply…"), no
  greeting, no signature — it is a form field, not a letter.

Output the answer in a code block, so it copies cleanly, and nothing else. It is not saved
anywhere: if Renaud asks to keep it, it goes to the candidature note via
`jobsearch-vault`.

## Constraints (load-bearing)

- **Never submit an application.** No form, no "Apply" button, no job portal interaction, ever.
- **Never write a full cover letter.** The only text this skill writes is the short form-field
  answer of Step 6, and only on request.
- **Never send a message to a person.** Not to a recruiter, not to a contact.
- **One offer per invocation.** If Renaud pastes several links, process them one at a time and say
  which one you are on — never fan out from here. Parallel fan-out belongs to `morning-briefing`.
- **Never build a CV from a snippet.** If the JD could not be read, the answer is "give me the
  text", never a CV written from a title.
- **Status is `📝 À postuler`** — the worker logs it; Renaud moves the card himself once he has
  actually applied.
- **Compose, do not reimplement.** The read, the comp gate, the CV and the log all live in skills
  that already exist. This skill resolves, dedups, spawns, reports — and, on request, writes the
  short form-field answer of Step 6, which no other skill owns.
