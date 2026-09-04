# STATUS — renaud-marketplace

Last updated: 2026-09-04

> History up to 2026-08-29 lives in [`STATUS-ARCHIVE.md`](./STATUS-ARCHIVE.md), verbatim.
> Nothing below repeats it.

## Current Focus

The offer→CV pipeline is **validated end to end and fail-open on the comp gate**. The 2026-09-04 run
produced 3 CVs from real JDs — and only rejected a 50–60 k€ offer because the workers found the
thresholds with a manual `find`. Order of work: the six lots in the Backlog, in order.

## In Progress

- [ ] **Have the CV judged again.** The independent recruiter agent that failed the 2026-08-28
      `p4×t5` batch has not seen the corrected output. The mechanical criteria of `#105` all pass;
      whether the content now convinces is unmeasured. Unchanged by the 2026-09-04 run, which
      generated 3 CVs with no review at all — see `#116`.

## Backlog

**Ordered 2026-09-04, after the first real `morning-briefing` run.** Six lots, in sequence. Each lot
is one release per plugin touched. Do not reorder without a reason written here.

**Lot 1 — `briefing`: the two defects that cost something every day**

Same file (`morning-briefing/SKILL.md`), two short fixes, one release. Best ratio of the queue.

- [ ] [#123](https://github.com/BluegReeno/renaud-marketplace/issues/123) — read today's daily log
      before overwriting it. A headless run wrote the four logs at 06h17 on 2026-09-04; the 13h38
      interactive run replaced `renaud/daily-log-2026-09-04` without reading it, and the morning
      version is gone. Step 0.5 (`:63`) reads **yesterday** only; Step 4 (`:437`) documents the
      overwrite as intended — an assumption that held while one author wrote per day, and that the
      headless + interactive pair broke.
- [ ] [#124](https://github.com/BluegReeno/renaud-marketplace/issues/124) — a closed sprint must not
      filter. Step 1a `:112` shows `that sprint's tasks` when `ends_at` is past; on 2026-09-03 that
      surfaced 6 tasks out of ~50 open. The 2026-09-04 session had to disobey the skill to render a
      usable brief. Also name the `suivant` sprint covering today (`Renaud-12` existed, never
      transitioned) so the fix reads as `transition_sprint`, not a replan.

**Lot 2 — `jobsearch`: make the unattended path fail closed**

One release. `#125` first — it is the only open defect that produces a *false application*.

- [ ] [#125](https://github.com/BluegReeno/renaud-marketplace/issues/125) — the plugin resolver is
      blind to the `synced/` layout. The three cascades (`cv-generator:119/258`, `cv-log-worker:72`,
      `jobsearch-vault:83`) know `.remote-plugins/` but not `~/.claude/plugins/synced/`, and
      `cv-log-worker:89` documents the fallback as **skip the comp gate**. Reported independently by
      all three workers on 2026-09-04.
- [ ] [#98](https://github.com/BluegReeno/renaud-marketplace/issues/98) — a missing contact file must
      fail by default, not behind an opt-in flag. Exact same class as `#125`: a guard that fails
      *open*, on the same unattended path. Fix it before automating further.
- [ ] [#106](https://github.com/BluegReeno/renaud-marketplace/issues/106) — generate from Cowork
      without the `--data-dir` workaround. Its `mkdtemp` fix and `#125`'s `synced/` glob are the same
      "Cowork layout" problem; treating them apart means visiting the same code twice.
- [ ] [#128](https://github.com/BluegReeno/renaud-marketplace/issues/128) — a scheduled interview
      never reaches the candidature. Only `log-cr` writes `prochain_rdv`, i.e. *after* the interview;
      `interview-prep` writes the `entretien` note and the hal task and nothing else. Hence 118 notes
      with an empty `prochain_rdv` and a briefing blaming Renaud for a tooling hole. Side effect:
      `📞 Entretien prévu` exists in `note_schemas.py:78` and no skill ever writes it.
- [ ] [#126](https://github.com/BluegReeno/renaud-marketplace/issues/126) — recognise
      `jobs-noreply@linkedin.com`. One table line in two files; rides along.
- [ ] [#121](https://github.com/BluegReeno/renaud-marketplace/issues/121) — P4 must stop claiming
      "15 yrs client-side". **The issue body was corrected on 2026-09-04**: the file is
      `plugins/jobsearch/profiles/p4_cs_fde.md:13`, versioned here — a one-line PR, not the
      out-of-repo edit the first draft described. Resync the private mirror afterwards.

**Lot 3 — `#89`, its own session, with the queue empty**

- [ ] [#89](https://github.com/BluegReeno/renaud-marketplace/issues/89) — purge personal contact PII
      from this public repo's git history. Re-verified reachable on 2026-09-04 (`84189dc`, `f642f7d`,
      `d7b18b1`, …). Needs a human-authorised force-push, so: no PR in flight, the ten stale
      `fix/skill-issue-*` branches swept first, and the GitHub Support request filed after — the
      rewrite alone does not purge the cached SHAs.

**Lot 4 — the offer→CV path gets judgement**

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

**Lot 5 — `jobsearch-vault`**

- [ ] [#127](https://github.com/BluegReeno/renaud-marketplace/issues/127) — the `statut` enum rejects
      what the vault and the process use. `note_schemas.py:74` lists 9 values; **29 of 118 notes carry
      one that is not among them**, including the 20 in `🗄️ Sans suite` — the very value the daily
      relance-cleanup ritual prescribes. Those notes cannot be updated by the tooling at all. Ranks
      above its stated `medium`.
- [ ] [#119](https://github.com/BluegReeno/renaud-marketplace/issues/119) — opportunité ↔ entretien
      navigable both ways. A decision session first (options A–E), then the implementation; 22 of 25
      linked opportunities have no back-link today.

**Lot 6 — debt, on no clock**

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
