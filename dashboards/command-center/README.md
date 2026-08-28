# Command Center — a published web page, by decision

> **Decision, 2026-08-18 (Renaud), in force until explicitly revisited.**
> The Command Center **is a web page** — this `index.html`, published as a claude.ai artifact.
> One tab per hal workspace plus a Daily-log tab. Improvements are made **here, on this file**.
> Packaging it inside a plugin, or turning it into a plugin-distributed artifact, is
> **deferred, not planned** — reconsider only on an explicit decision, never in passing.

Read this before proposing a different shape for the dashboard. `#69` (closed 2026-08-18)
carries the history; this file carries the rule.

## Where it lives

| | |
|---|---|
| Source of truth | `dashboards/command-center/index.html` — versioned here, in git |
| Published page | https://claude.ai/code/artifact/a9aa59b2-bd53-4461-87bd-8fb62efd98f2 |
| Offline tests | `tests/test_command_center_parser.js` — `node tests/test_command_center_parser.js` |

## How to change it

1. Edit `index.html` in this repo, commit.
2. Republish **from the same file path** — that redeploys to the **same URL**, so bookmarks and
   open tabs keep working, and the artifact keeps a version history.

There is no build step, no bundler, no dependency to install. The page is self-contained by
constraint: a published artifact may not load anything from another host.

## The one real risk: publish/source drift

The failure to guard against is not a missing feature — it is the published page quietly
diverging from this file. It has already happened once in this portfolio: `edifice-front` carried
~1 600 bytes of hand-injected script that was never committed back, so the repo could no longer
reproduce the page that actually worked.

**Never hand-edit the published page.** Any fix goes into this file first, then gets republished.

Verified 2026-08-18: the published body matches this file exactly (1174 lines, the only
difference being the `</body></html>` the platform appends). To re-check, fetch the artifact
URL, strip everything up to `<!-- /frame-runtime -->` and the injected `<head>`, and `diff` the
remainder against this file.

## What the page needs at runtime

- The `hal-mcp` connector, connected on the claude.ai account. Without it the page renders a
  plain explanation instead of data — it never shows an empty dashboard as if hal were empty.
- `list_tasks` returns `{ tasks, total, returned, truncated }` (see
  [hal#105](https://github.com/BluegReeno/hal/issues/105)). The page reads `truncated` and
  `total` straight from the payload rather than guessing from a row-count cap, and says how many
  rows were withheld instead of pretending the list is complete.
- `list_documents` returns `{ documents, total, returned, truncated }` (see
  [hal#119](https://github.com/BluegReeno/hal/issues/119), deployed 2026-08-28). The daily-log
  index reads `payload.documents` and **fails visibly** on any other shape. It used to guard with
  `Array.isArray(r.payload) ? r.payload : []`, which turned the hal#119 deploy into an empty
  daily-log list with no error — the shape change was invisible precisely because the guard was
  written to be forgiving.
- `list_sprints` still returns a bare array; hal#119 did not touch it.

## Rules that outlived `#69`

- **One dashboard, not two.** `command-center-quotidien` was deleted on 2026-08-17 precisely
  because two dashboards had drifted apart. Do not reintroduce a second one.
- **Reading the UI is not proof of a write.** Ticking a task is verified by re-reading it from
  hal, and the writes were checked in SQL directly against `halcrm_tasks`, not through the
  connector.
