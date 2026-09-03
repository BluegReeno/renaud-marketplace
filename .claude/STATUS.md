# STATUS — renaud-marketplace

Last updated: 2026-09-03

> History up to 2026-08-29 lives in [`STATUS-ARCHIVE.md`](./STATUS-ARCHIVE.md), verbatim.
> Nothing below repeats it.

## Current Focus

Four plugins published — `briefing` **0.16.2**, `jobsearch` **0.11.6**, `mycoach` **0.4.4**,
`improve` **0.3.0**, marketplace top-level **0.6.31** (read from `marketplace.json`). Work has moved
to the offer→CV pipeline: `#115` then `#117` then `#105`, in that order, one fresh session each.
The `cv-generator` content defects and the PII purge stay open behind them.

## In Progress

- [ ] Nothing in flight.

## Backlog

**Offer→CV pipeline — sequenced, run in this order**

Decided 2026-09-03. Each step is a prerequisite of the next; do not start one before the previous
merges.

- [ ] [#115](https://github.com/BluegReeno/renaud-marketplace/issues/115) — read a LinkedIn JD via
      the `jobs-guest` endpoint. **Proved live on a 32-minute-old posting** (ChapsVision
      `4461607259`, 2026-09-03): one call, full JD, no login, no keychain prompt. The cached-dataset
      path cannot serve a fresh posting — the freshness bias is structural. Ship it as a **reusable
      primitive**, not a second inline branch in `Step 1g`; `#117` consumes it.
- [ ] [#117](https://github.com/BluegReeno/renaud-marketplace/issues/117) — one offer-processing
      path, two triggers. `cv-log-worker` stays an agent (only `Agent` spawns in parallel) but takes
      `JOB_URL` alone; new `apply-to-offer` skill gives the pasted-URL path a trigger. Lifts the
      3-offer fan-out cap — **which is coupled to the 5-call BrightData cap**: raise only the first
      and the 6th offer yields a CV built from a digest snippet, unmarked.
- [ ] [#105](https://github.com/BluegReeno/renaud-marketplace/issues/105) — must land before the
      first real 5-offer morning. `#117` multiplies CV output; `#105` is what makes the output
      truthful.
- [ ] [#116](https://github.com/BluegReeno/renaud-marketplace/issues/116) — two-round judge loop and
      fit × freshness ordering. After `#117`, so the judge sits on a single consolidated path.

**`cv-generator` — remaining defects, same skill**

- [ ] [#106](https://github.com/BluegReeno/renaud-marketplace/issues/106) — generate from Cowork without the `--data-dir` workaround
- [ ] [#98](https://github.com/BluegReeno/renaud-marketplace/issues/98) — a missing contact file must fail by default, not behind an opt-in flag

**Security / hygiene**

- [ ] [#89](https://github.com/BluegReeno/renaud-marketplace/issues/89) — purge personal contact PII
      from this repo's public git history. `#101` stopped new ones landing; this is the purge, and
      it needs a human-authorised force-push.
- [ ] [#103](https://github.com/BluegReeno/renaud-marketplace/issues/103) — `jobsearch` hardcodes
      `workspace_slug="renaud"` in three skills; never covered by `#77`
- [ ] [#102](https://github.com/BluegReeno/renaud-marketplace/issues/102) — no per-plugin CHANGELOG,
      unlike the sibling marketplace. Until this changes, a run told only "add a CHANGELOG entry"
      creates three new files and fails `check_version_sync.sh` — correct the **issue body**, not
      the run prompt.
- [ ] Ten stale local `fix/skill-issue-*` branches to sweep whenever convenient.

**Features**

- [ ] [#95](https://github.com/BluegReeno/renaud-marketplace/issues/95) — add the Google Drive tools
      to `gmail-mcp`, then rename the server to `google-mcp`

**Known limits, not bugs — decided, do not re-litigate**

- `gmail-mcp`: one deployment = one mailbox. `GOOGLE_REFRESH_TOKEN` is a single project-level secret;
  the bearer authorises but never selects an account. Separating perso from pro needs a second
  deployment or a per-account token map (which also means keying the `cachedToken` singleton).
- This repo has **no automatic deploy** and nothing signals the gap between `main` and the deployed
  function. The v7 in production once lagged `main` by three commits for five weeks.
- The Supabase account depends on the directory, through direnv: `renaud-marketplace/.envrc` carries
  the **personal** account, `hal/.envrc` and `edifice/.envrc` the Blue Green one. Running `supabase`
  from the wrong folder targets the right project with the wrong account.
- Two clones of this repo exist. `~/Projects/renaud-marketplace` is the working clone;
  `~/.claude/plugins/marketplaces/renaud-marketplace` is the plugin install cache — editing there
  works but leaves the installed marketplace on a feature branch.
- Cowork was never disqualified for **writing**. The claude.ai runtime was chosen because it was
  *proved*, not because Cowork *failed*. Probe ready and unlaunched: `probes/cowork-write-probe.html`
  — publish it from a Cowork session before reopening the question.

## Done (current sprint)

- [x] `#111` / PR #112 — `hal#135` lot D: the tag doctrine became a one-line pointer in six files;
      briefing **0.16.2** / jobsearch **0.11.6** / mycoach **0.4.4** — 2026-08-29
- [x] `#109` / PR #110 — `mycoach` writes `channel='note'`, shipped **before** hal deployed the
      closed `channel` vocabulary, so zero sessions broke — 2026-08-28
- [x] `#101` / PR #104 — the identity guard covers all four plugins and reads the git index rather
      than the filesystem tree — 2026-08-27
- [x] GitHub Pages enabled on `main` / root: `gmail-mcp` OAuth works end to end from OpenClaw. The
      consent page had been committed since June; Pages had never actually been enabled — 2026-08-27
