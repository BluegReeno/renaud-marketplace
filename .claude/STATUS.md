# STATUS — renaud-marketplace

Last updated: 2026-09-05

> History up to 2026-08-29 lives in [`STATUS-ARCHIVE.md`](./STATUS-ARCHIVE.md), verbatim.
> Nothing below repeats it.

## Current Focus

The unattended offer→CV path now **fails closed**: unreadable thresholds abort the worker, a
missing contact file refuses to render, and every resolver knows the Cowork `synced/` layout. Next
up is `#89` (PII purge) — which needs the queue empty and the stale branches swept first.

## In Progress

- [ ] **Have the CV judged again.** The independent recruiter agent that failed the 2026-08-28
      `p4×t5` batch has not seen the corrected output. The mechanical criteria of `#105` all pass;
      whether the content now convinces is unmeasured. Unchanged by the 2026-09-04 run, which
      generated 3 CVs with no review at all — see `#116`.

## Backlog

**Ordered 2026-09-04, after the first real `morning-briefing` run.** Four lots left, in sequence —
the `briefing` and `jobsearch` lots that opened the queue both shipped, the order below is otherwise
unchanged. Each lot is one release per plugin touched. Do not reorder without a reason written here.

**Lot 1 — `#89`, its own session, with the queue empty**

- [ ] [#89](https://github.com/BluegReeno/renaud-marketplace/issues/89) — purge personal contact PII
      from this public repo's git history. Re-verified reachable on 2026-09-04 (`84189dc`, `f642f7d`,
      `d7b18b1`, …). Needs a human-authorised force-push, so: no PR in flight, the stale
      branches swept first, and the GitHub Support request filed after — the rewrite alone does not
      purge the cached SHAs. **16 stale remote branches counted 2026-09-04** (8 `fix/skill-issue-*`,
      6 `archon/*`, `claude/gemini-connector-skill-setup-exupqr`, `feat/capture-improve-skills`) —
      the earlier "ten" was wrong.

**Lot 2 — the offer→CV path gets judgement**

`#129` before `#116`: the gate sits upstream of the judge, and on the Stakha case the CV should never
have been written at all.

- [ ] [#129](https://github.com/BluegReeno/renaud-marketplace/issues/129) — no qualitative gate. The
      worker's only filter is the comp gate; the disqualifiers live as prose in Step 1g's `❌` row and
      are never read by `cv-log-worker`. On 2026-09-04 that produced a full CV + vault note + relance
      task for Stakha, which Renaud discarded on sight ("trop infra pour moi"). His criterion is
      recorded in hal and nowhere in this repo, so the next fan-out repeats it. Proposed:
      `plugins/jobsearch/data/role-criteria.json`, on the documented model of `comp-thresholds.json`.
- [ ] [#116](https://github.com/BluegReeno/renaud-marketplace/issues/116) — two-round judge loop and
      fit × freshness ordering. **Unblocked**: the validation run it was held for passed on
      2026-09-04, and gave it its best argument — 3 CVs generated unreviewed. `read-job-offer`
      already returns `freshness` and `applicant_count`.

**Lot 3 — `jobsearch-vault`**

- [ ] [#127](https://github.com/BluegReeno/renaud-marketplace/issues/127) — the `statut` enum rejects
      what the vault and the process use. `note_schemas.py:74` lists 9 values; **29 of 118 notes carry
      one that is not among them**, including the 20 in `🗄️ Sans suite` — the very value the daily
      relance-cleanup ritual prescribes. Those notes cannot be updated by the tooling at all. Ranks
      above its stated `medium`.
- [ ] [#119](https://github.com/BluegReeno/renaud-marketplace/issues/119) — opportunité ↔ entretien
      navigable both ways. A decision session first (options A–E), then the implementation; 22 of 25
      linked opportunities have no back-link today.

**Lot 4 — debt, on no clock**

- [ ] [#103](https://github.com/BluegReeno/renaud-marketplace/issues/103) — `jobsearch` hardcodes
      `workspace_slug="renaud"` in three skills; 11 occurrences, never covered by `#77`. A real design
      pass plus one out-of-repo hal config (`allowed_tags`). The CI exclusion
      `JOBSEARCH_WORKSPACE_DEBT` disappears when this closes.
- [ ] [#102](https://github.com/BluegReeno/renaud-marketplace/issues/102) — **rewritten 2026-09-04**.
      It used to ask for per-plugin CHANGELOGs, which breaks `check_version_sync.sh`; it now describes
      what is actually wrong with the root file: `jobsearch` documents 15 of 38 shipped versions,
      `briefing` 19 of 31, a ghost `## myspy` section survives at `:250`/`:254`, and the versioning
      preamble lives only in `CLAUDE.md`.
- [ ] [#95](https://github.com/BluegReeno/renaud-marketplace/issues/95) — add the Google Drive tools
      to `gmail-mcp`, then rename the server to `google-mcp`. Last: the manual workaround costs
      thirty seconds, and the blocking step is an OAuth re-consent, not code.

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

- [x] **The unattended path fails closed** — `#125`, `#98`, `#106`, `#126`, `#121`, `#128` in one lot
      ([PR #131](https://github.com/BluegReeno/renaud-marketplace/pull/131), jobsearch **0.15.0** /
      briefing **0.18.0**). Four resolvers learned the `synced/` layout (not three — `interview-prep`
      had one too) and the canonical resolver in the marketplace guide with them; unreadable
      thresholds now abort `cv-log-worker` instead of skipping the comp gate; a missing
      `contact.local.json` exits 1 instead of rendering `contact@example.com`; `.cv_temp` moved to
      `mkdtemp()`; new `--container-items`; `@linkedin.com` matched by domain; P4's false
      "15 yrs client-side" replaced by the vault-traceable Artelia anchor, with a Step 2 rule that
      cross-checks every career fact against the vault; new Step 4c carries a scheduled interview
      back onto the candidature. **Found in passing:** `interview-prep` resolved the mounted private
      mirror *first*, so a committed profile fix could never reach a machine holding the mirror —
      demoted to last resort, which is what makes `#121` actually take effect — 2026-09-05

- [x] **`#128` backfilled from the calendar** — Cognyx `2026-09-07` and OSS Ventures `2026-09-10`,
      both promoted to `📞 Entretien prévu`. The issue's list was wrong: there is **no InsideBoard
      event in either calendar** (its note already carried `2026-09-07`, entered by hand), the 07/09
      slot is a **second Cognyx round** (`DS HSA: Renaud`, booked by `matthias@cognyx.io` minutes
      after the first interview), and OSS has **two** slots — 10/09 and a founder interview on 16/09.
      InsideBoard left untouched, pending confirmation that the interview exists — 2026-09-05

- [x] [#123](https://github.com/BluegReeno/renaud-marketplace/issues/123) +
      [#124](https://github.com/BluegReeno/renaud-marketplace/issues/124) — the two `morning-briefing`
      defects that cost something every day, one release
      ([PR #130](https://github.com/BluegReeno/renaud-marketplace/pull/130), briefing **0.17.1**).
      Step 0.5 now reads today's daily log too and holds it verbatim in full; Step 4 appends under a
      dated `## Run <HH:MM>` separator instead of replacing it. A closed `actuel` sprint no longer
      filters — all three failure rows show the unfiltered list — and the skill resolves the
      `suivant`/`a_venir` sprint covering today, naming `transition_sprint` with its id (diagnostic
      only, never called from the brief). Archon was **not** used: `skill-improve.yaml` still
      enforces the removed `SKILL.md` `version:` field and ignores `CHANGELOG.md` and `release.sh` —
      [archon-workflows#30](https://github.com/BluegReeno/archon-workflows/issues/30) is open, and
      `#32` was closed as its duplicate without a fix — 2026-09-04

- [x] **First real `morning-briefing` run** — the validation three merges waited on. `jobs-guest`
      reads a fresh JD in the real flow (`#115`); `Agent(cv-log-worker)` resolves across plugins and
      the sub-agents inherit MCP tools (`#117`); no keychain prompt. 3 CVs generated and logged,
      Albatross correctly rejected at 50–60 k€ — but only because the workers bypassed the resolver
      by hand. Five issues filed from the run (`#123`–`#127`), two more found while reviewing them
      (`#128`, `#129`) — 2026-09-04

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
