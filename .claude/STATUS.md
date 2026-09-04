# STATUS — renaud-marketplace

Last updated: 2026-09-04

> History up to 2026-08-29 lives in [`STATUS-ARCHIVE.md`](./STATUS-ARCHIVE.md), verbatim.
> Nothing below repeats it.

## Current Focus

The offer→CV pipeline is **built and unvalidated**. `#115`, `#117` and `#105` all merged on
2026-09-04 (`jobsearch` **0.14.0**, `briefing` **0.17.0**, `improve` **0.3.2**, marketplace
top-level **0.6.38**). Nothing more ships on it until one real morning run says it works.

## In Progress

- [ ] **One `morning-briefing` run on a digest carrying a recent posting.** It is the single
      validation for three merges at once, and it answers four questions no test here could:
      1. does the `jobs-guest` endpoint read a fresh JD in the real flow (`#115`);
      2. does `Agent(cv-log-worker)` resolve across plugins — the worker lives in `briefing`,
         `apply-to-offer` spawns it from `jobsearch` (`#117`, marked `TODO: verify in Cowork`);
      3. does a sub-agent inherit MCP tools — `read-job-offer` consumes BrightData, where every
         prior `Skill()` call from that worker used scripts only (`#117`);
      4. **no macOS keychain prompt**, ever (`#115`).
- [ ] **Have the CV judged again.** The independent recruiter agent that failed the 2026-08-28
      `p4×t5` batch has not seen the corrected output. The mechanical criteria of `#105` all pass;
      whether the content now convinces is unmeasured.

## Backlog

**Offer→CV pipeline — what is left**

- [ ] [#116](https://github.com/BluegReeno/renaud-marketplace/issues/116) — two-round judge loop and
      fit × freshness ordering, inside `cv-log-worker`. Held until the validation run passes: it
      would sit on a path nobody has seen work end to end. `read-job-offer` already returns
      `freshness` and `applicant_count`, so the ordering signal is in hand.

**CV content — the factual family opened by `#105`**

- [ ] [#121](https://github.com/BluegReeno/renaud-marketplace/issues/121) — `interview-prep` still
      asserts "15 yrs client-side" for P4. Same defect class as `#105`: a claim the `parcours`
      record does not support. The rule now exists in `cv-generator`'s SKILL.md; `interview-prep`
      does not read it.
- [ ] [#106](https://github.com/BluegReeno/renaud-marketplace/issues/106) — generate from Cowork without the `--data-dir` workaround
- [ ] [#98](https://github.com/BluegReeno/renaud-marketplace/issues/98) — a missing contact file must fail by default, not behind an opt-in flag

**Security / hygiene**

- [ ] [#89](https://github.com/BluegReeno/renaud-marketplace/issues/89) — purge personal contact PII
      from this repo's public git history. `#101` stopped new ones landing; this is the purge, and
      it needs a human-authorised force-push.
- [ ] [#103](https://github.com/BluegReeno/renaud-marketplace/issues/103) — `jobsearch` hardcodes
      `workspace_slug="renaud"` in three skills; never covered by `#77`. It nearly became four on
      2026-09-04: the first draft of `#105`'s source-of-truth rule wrote the slug literally, and
      `check_no_identity_literals.sh` caught it. The guard works; the three existing sites remain.
- [ ] [#102](https://github.com/BluegReeno/renaud-marketplace/issues/102) — no per-plugin CHANGELOG,
      unlike the sibling marketplace. Until this changes, a run told only "add a CHANGELOG entry"
      creates three new files and fails `check_version_sync.sh` — correct the **issue body**, not
      the run prompt.
- [ ] Ten stale local `fix/skill-issue-*` branches to sweep whenever convenient.

**Features**

- [ ] [#95](https://github.com/BluegReeno/renaud-marketplace/issues/95) — add the Google Drive tools
      to `gmail-mcp`, then rename the server to `google-mcp`
- [ ] [#119](https://github.com/BluegReeno/renaud-marketplace/issues/119) — `jobsearch-vault`: make
      the opportunité ↔ entretien link navigable in both directions

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

- [x] [#105](https://github.com/BluegReeno/renaud-marketplace/issues/105) — `p4×t5` rewritten
      against the `parcours` record ([PR #122](https://github.com/BluegReeno/renaud-marketplace/pull/122)).
      Open Ocean was titled `Managing Director` in **three** profiles, not one; SAT-OCEAN carried
      wrong dates and a weakened title; a bullet claimed eight years of commercial cycles the record
      attributes to the sales director. Contact links now produce real `/URI` annotations — the PDF
      had none — verified by the new `scripts/check_pdf_links.py` — 2026-09-04
- [x] [#117](https://github.com/BluegReeno/renaud-marketplace/issues/117) — one offer→CV path, two
      triggers ([PR #120](https://github.com/BluegReeno/renaud-marketplace/pull/120)). New
      `apply-to-offer`; `cv-log-worker` takes `JOB_URL` alone; the 3-offer product cap replaced by an
      announced safety bound of 8; comp thresholds moved to a single definition site — 2026-09-04
- [x] [#115](https://github.com/BluegReeno/renaud-marketplace/issues/115) — LinkedIn JD read via the
      `jobs-guest` endpoint, extracted as the shared skill `jobsearch/read-job-offer`
      ([PR #118](https://github.com/BluegReeno/renaud-marketplace/pull/118)) — 2026-09-03
- [x] [archon-workflows#32](https://github.com/BluegReeno/archon-workflows/issues/32) filed —
      `skill-improve.yaml` enforces a release contract this repo no longer has, so it was **not**
      used for `#115`. Fix it before routing any further issue through it — 2026-09-03
- [x] `#111` / PR #112 — `hal#135` lot D: the tag doctrine became a one-line pointer in six files;
      briefing **0.16.2** / jobsearch **0.11.6** / mycoach **0.4.4** — 2026-08-29
- [x] `#109` / PR #110 — `mycoach` writes `channel='note'`, shipped **before** hal deployed the
      closed `channel` vocabulary, so zero sessions broke — 2026-08-28
- [x] `#101` / PR #104 — the identity guard covers all four plugins and reads the git index rather
      than the filesystem tree — 2026-08-27
- [x] GitHub Pages enabled on `main` / root: `gmail-mcp` OAuth works end to end from OpenClaw. The
      consent page had been committed since June; Pages had never actually been enabled — 2026-08-27
