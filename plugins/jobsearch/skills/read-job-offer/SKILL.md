---
name: read-job-offer
description: >
  Read the full text of a LinkedIn job posting from its job id or URL, without a
  login and without opening a browser. Runs a two-step cascade — the cached
  BrightData dataset first, the LinkedIn guest endpoint on failure — and returns
  one structured block: JD text, freshness, applicant count, seniority,
  employment type, job function, industries. This is a shared primitive: callers
  are `morning-briefing` (Step 1g scoring), and any skill or sub-agent handed a
  LinkedIn offer URL. Use when a skill needs the JD behind a
  `linkedin.com/jobs/view/<id>` link, or when the user pastes such a link and
  asks what the offer says.
allowed-tools: "mcp__brightdata__web_data_linkedin_job_listings mcp__brightdata__scrape_as_markdown"
---

# Read Job Offer — Skill Instructions

## What this skill does

One job in, one JD out. Given a LinkedIn `job_id` (or any URL carrying one), return the full job
description plus the four LinkedIn classification fields, or an explicit `unavailable` verdict.

It exists so that **every** caller reads an offer the same way. The two-step cascade below was
established against a posting **32 minutes old** (`4461607259`, 2026-09-03): one call, full JD, no
login, no browser, no keychain prompt. Do not reimplement it inline in a calling skill — extend it
here.

## Input

A single value, in any of these shapes:

- a bare numeric id — `4461607259`
- a canonical URL — `https://www.linkedin.com/jobs/view/4461607259`
- a search/collection URL carrying `currentJobId=<id>`

**Step 0 — normalise.** Extract the id with `jobs/view/(\d+)`, else `currentJobId=(\d+)`, else accept
the input if it is entirely digits. If no id can be extracted, return `status: unavailable` with
`reason: no job id in input` — never guess an id, never fall back to a text search.

## Step 1 — Cached dataset (first attempt)

```
mcp__brightdata__web_data_linkedin_job_listings(
  url="https://www.linkedin.com/jobs/view/<job_id>"
)
```

On success, read `job_summary` for the JD text and the response's own fields for the metadata.

This path returns clean structured JSON, but it is a **lookup in a cached dataset**: a posting that
is not yet indexed fails here, and freshly published offers are exactly the ones that are not
indexed. Treat a failure as normal, not as an error worth reporting.

## Step 2 — Guest endpoint (fallback, no login)

If Step 1 errors or returns no `job_summary`:

```
mcp__brightdata__scrape_as_markdown(
  url="https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/<job_id>"
)
```

This endpoint serves the posting to anonymous callers. It answers on offers published minutes
earlier, which is the whole reason it is here.

### Parsing the guest response — two facts that decide the outcome

1. **The JD is wrapped in authentication chrome.** `Join or sign in`, email and password fields,
   `/uas/login` links appear around and after the posting itself. Strip them. Their presence is
   **not** a failure signal — a naive "did we hit a login wall?" check discards a perfectly good
   response. Judge the outcome on whether a title and a body were found, never on the chrome.
2. **The payload truncates after `Industries`** — that is, after every field worth extracting. A
   response that ends there is complete, not cut short.

Extract, when present: the job title, company, location, publication age (`X hours/days ago`),
applicant count (`Be among the first N applicants`, `N applicants`), the posting body, and the four
trailing fields `Seniority level`, `Employment type`, `Job function`, `Industries`.

## Step 3 — Output contract

Return exactly this block. Callers depend on the field names.

```
status:           ok | unavailable
job_id:           <id>
source:           dataset | guest
title:            <job title, or empty>
company:          <company name, or empty>
location:         <location, or empty>
freshness:        <"32 minutes ago" / "2 days ago", or empty>
applicant_count:  <integer, or empty>
seniority_level:  <value, or empty>
employment_type:  <value, or empty>
job_function:     <value, or empty>
industries:       <value, or empty>
jd_text:          <full posting body, auth chrome stripped>
reason:           <why it is unavailable — only when status is unavailable>
```

`status: unavailable` only when **both** steps failed. An empty optional field is normal; an empty
`jd_text` with `status: ok` is not — that combination means the parse failed, so return
`unavailable` instead.

## Constraints (load-bearing)

- **Never scrape `linkedin.com/jobs/view/<id>`** — that URL is behind the login wall. It is the
  argument to the Step 1 dataset lookup and nothing else.
- **Never open a browser on LinkedIn** — no `preview_start`, no `get_page_text`, no built-in
  browser, no matter how both steps failed. LinkedIn serves its sign-up page, and macOS raises a
  keychain / password-manager prompt at the user. This has happened once (2026-09-02) and must not
  happen again.
- **The cascade is one BrightData call for quota purposes** — a caller enforcing a per-run call cap
  counts one invocation of this skill as one call, whether it stopped at Step 1 or ran both steps.
- **Never fabricate a JD.** No summarising from a digest snippet, no reconstructing from the title.
  If the text was not read, `status: unavailable` is the answer.
- **Never authenticate.** No credentials, no cookies, no session — the guest endpoint needs none.
