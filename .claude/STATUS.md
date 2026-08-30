# STATUS — renaud-marketplace

Last updated: 2026-08-30

> History up to 2026-08-29 lives in [`STATUS-ARCHIVE.md`](./STATUS-ARCHIVE.md), verbatim.
> Nothing below repeats it.

## Current Focus

Four plugins published — `briefing` **0.16.2**, `jobsearch` **0.11.6**, `mycoach` **0.4.4**,
`improve` **0.3.0**, marketplace top-level **0.6.31** (read from `marketplace.json`). The hal
vocabulary contract is closed on this side: no skill promises `hal://vocabulary` any more, and none
writes a value the server will refuse. The Command Center is shipped and in daily use. What is
open is a cluster of `cv-generator` defects and one security debt.

## In Progress

- [ ] Nothing in flight.

## Backlog

**`cv-generator` — four open defects, same skill**

- [ ] [#106](https://github.com/BluegReeno/renaud-marketplace/issues/106) — generate from Cowork without the `--data-dir` workaround
- [ ] [#105](https://github.com/BluegReeno/renaud-marketplace/issues/105) — real skills and exact facts in cell p4×t5
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
