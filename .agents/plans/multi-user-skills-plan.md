# Plan — make the skills usable by a second user (#77, and #76 minus the CV data)

Written 2026-07-31. Phase 2 of a two-repo effort. Phase 1 lives in the private `hal` repo
(`docs/features/workspace-calendar-identity.md`) and enriches `whoami`; this phase makes the
skills consume it and stop naming anyone.

**This repository is public.** No calendar ID, mailbox address, phone number or postal
address may appear in any file this plan touches — including in the plan itself, in commit
messages, or in the PR body.

---

## Problem

Five skills encode the identity of the person who wrote them — workspace slugs, calendar IDs
and mailbox addresses as literals in prompt text. A second human user was provisioned on
2026-07-31 and cannot run any of them.

Two distinct failure modes, only one of which is acceptable:

- **Fails by design** — `morning-briefing` (line 51) and `mail-triage` (line 39) probe
  `whoami` and assert a specific identity. A foreign user gets a clean refusal. The *stopping*
  is right; asserting *whose* identity it is, is wrong.
- **Fails by accident** — `mycoach` has no probe at all; `sprint-planner` (line 60) and
  `sprint-review` (line 76) do have one, but it fires *after* their ÉTAPE 0 has already called
  `get_document` against a hardcoded slug. Under RLS that call returns `Workspace not found`,
  no instruction covers it, and the agent improvises — it can invent a sprint review from
  nothing. **This is the real bug and the priority.**

## Dependency — the enriched `whoami` contract

Phase 1 makes `mcp__plugin_hal_hal-mcp__whoami` return, per workspace:

```
workspace_slug, name, role, is_default,
allowed_tags[], sprints_enabled, calendar_id, member_calendar_id
```

`calendar_id` is the calendar **shared** by the whole workspace (a household or site agenda);
`member_calendar_id` is **this member's own** agenda for that workspace. Either may be null.
`user_email` and `default_workspace_slug` keep their current meaning.

**Write the skills against this contract now, and degrade explicitly while it ships.** A skill
that receives a `whoami` payload without the new fields must say so in its rendered output and
carry on with what it has — never guess a calendar, never fall back to a hardcoded slug. This
is the same rule as everywhere else in this plan: visible degradation, never silent omission.

Do not merge this PR before phase 1 is deployed.

---

## Rules that decide every case below

1. **The workspace is the sharing perimeter; the tag is the subject.** Never infer a
   destination workspace from a task's tags.
2. **Iterate on what `whoami` returns.** No slug literal anywhere. A workspace is rendered
   only if it has something to show (an active sprint when `sprints_enabled`, otherwise open
   tasks) — that property, never a name, is what hides an empty workspace.
3. **Calendars come from the workspaces.** The set read is the union of every non-null
   `calendar_id` and `member_calendar_id`, deduplicated. Calendars the user owns but that no
   workspace declares are not read. No `#holiday` / `import` heuristic is needed or wanted.
4. **A skill that cannot establish its context stops and says why** — with the actual values
   it received, never with an expected identity.
5. **Visible degradation.** Any missing source, field or calendar renders a `⚠️` line.

---

## Per-skill work

### `morning-briefing` (496 lines — the bulk of the work)

- **Step 0 probe** (line 51): drop the expected email and the expected slug list. Assert
  resolvability instead: `whoami` answers, and returns at least one workspace. Empty
  membership list → stop with an explicit message. Keep the existing `hal:DOWN` behaviour and
  the `--headless` abort contract untouched.
- **Steps 1a/1b** (lines 79-101): replace the two hardcoded blocks with one loop over
  `whoami.workspaces`. Per workspace: if `sprints_enabled`, resolve the active sprint then
  `list_tasks(sprint_id=…)`; otherwise `list_tasks` with no sprint filter and no
  "(no active sprint)" note — a sprintless workspace is not a workspace missing a sprint.
- **Task labels**: `[business]` / `[perso]` (line 91, 95, and the Step 5 constraint
  "Label every hal task") are author artefacts. Label with the workspace `name`, falling back
  to `workspace_slug` when `name` is null.
- **Tag grouping** (line 97-99): drop the fixed seven-tag list. Group by first tag, ordered by
  the workspace's own `allowed_tags`; untagged tasks last. Applies to every workspace, not to
  one named one.
- **Step 1d calendars** (lines 115-123): replace the three literal IDs with the union defined
  in rule 3. Tag each event with the name of the workspace that declared its calendar. If no
  workspace declares any calendar → render `⚠️ Aucun calendrier déclaré sur tes workspaces`
  and keep going. `list_calendars` stays as the health probe only. Europe/Paris windows,
  `hangoutLink` capture and the +7-day fallback are unchanged.
- **Mailboxes** (lines 119-120, 129, 151, 164, 174, 333-334): which inbox is queried is
  decided by *which MCP server is called*, never by the address string. Replace the display
  labels with `Gmail perso` / `Gmail pro` and drop the `?authuser=<address>` parameter from
  built Gmail links. Document the resulting limitation in the skill: with several Google
  accounts signed in, such a link opens the browser's active account. Accepted — a wrong tab
  is cheaper than a published address.
- **Step 4** (line 358) already iterates on `whoami` — keep it. Rewrite the
  "Any other workspace returned by `whoami`" fallback (line 467): there is no longer a
  reference shape to fall back *to*, so define one uniform daily-log shape for every
  workspace. Keep the `Liens` and `▶️ prochaines actions` sub-lines, and the rule that a link
  type absent from Step 1 is omitted rather than invented.
- Leave untouched: the jobsearch block, LinkedIn scoring, the `cv-log-worker` fan-out and its
  cap, the BrightData cap, the read-only constraints, the two-write limit.

### `mail-triage` (257 lines)

- Same probe rewrite (line 39).
- Replace hardcoded slugs (lines 55-59, 76-77) with the `whoami` loop; cross-reference
  contacts, companies and projects per workspace.
- Same mailbox treatment as above (lines 4, 88, 105, 131, 141, 200, 221, 240-241) — labels
  only, no addresses.

### `sprint-planner` (445 lines) and `sprint-review` (339 lines)

- **Move the `whoami` probe ahead of ÉTAPE 0.** This is the priority fix: today ÉTAPE 0 calls
  `get_document` on a hardcoded slug *before* the probe runs.
- ÉTAPE 0's context documents: iterate over the resolved workspaces instead of the two literal
  `get_document` calls. A missing document stays non-blocking (already the case).
- **Only handle workspaces where `sprints_enabled` is true.** Skip the others with one visible
  line naming them — planning a sprint in a sprintless workspace is meaningless. If no
  workspace has sprints enabled, stop and say so.
- Replace the `_bg` / `_rn` paired variables (planner 47-76, 326-427; review 65-89, 236-321)
  with per-workspace iteration.
- Calendars (planner 210-220, review 259-269): union rule, as above.

### `mycoach` (123 lines)

- **Add a `whoami` probe** — it has none, and it writes.
- Resolve its workspace by the convention the skill already documents (line ~25: initialising
  MyCoach adds the `mycoach` tag to the workspace's `allowed_tags`): pick the workspace whose
  `allowed_tags` contains `mycoach`. None → stop with the existing initialisation message.
  Several → ask which one. Never fall back to `default_workspace_slug`: the author's default
  is a business workspace, and a personal session must never be written there.
  This reads a tag to find *which workspace is enabled for MyCoach* — it is not routing a task
  by its subject, and does not contradict rule 1.
- Replace the four hardcoded slugs (lines 21, 24, 77, 91) with the resolved one. Keep the
  existing half-state error handling (`log_interaction` / `update_task_status` / `create_task`)
  exactly as it is.
- The local knowledge-bundle path stays as is — out of scope.

---

## Sweep for #76 (the published-identifiers half)

Grep the whole repo for calendar IDs, `@gmail.com`, `@bluegreen.ai`, `+33` and postal
patterns. Found on 2026-07-31 in 16 files; treat them as follows.

**Clean** — the five skill files above, plus these, which the issue does not list:

| File | What |
|---|---|
| `docs/loop-3-morning-briefing.md` | mailbox addresses |
| `.claude/docs/features/sprint-planner-SKILL.md` | a calendar ID + mailbox addresses |
| `.agents/plans/gmail-mcp-plan.md` | mailbox address |
| `.claude/tasks/gmail-mcp-oauth-consent-github-pages.md` | mailbox address |
| `plugins/briefing/CHANGELOG.md` | mailbox address |

Use a neutral placeholder (`<mailbox-perso>`, `<calendar-id>`), never a realistic-looking fake.
The CHANGELOG entry is rewritten despite the usual "history stays true" rule: that rule exists
so a changelog does not lie about *what shipped*, and a redacted address still tells that
story. Personal data does not earn republication through historical accuracy.

**Leave alone**:
- `author.email` in `plugins/*/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`
  — a plugin author field, published on purpose.
- `plugins/jobsearch/data/cv-master.json` — email, phone, **postal address and a maps link to
  the street**. Deliberately deferred by Renaud on 2026-07-31; #76 stays open for it. Do not
  touch it in this PR.
- Git history. Out of scope, as stated in #76: removing from `main` reduces future exposure
  and retracts nothing.

---

## Release chores (`CLAUDE.md` — mandatory)

Prefer `scripts/release.sh <plugin> <version> "<changelog line>"`, which does steps 1-4 in one
validated pass and commits without pushing.

- `briefing` → MINOR bump (new behaviour, not a fix)
- `mycoach` → MINOR bump
- `.claude-plugin/marketplace.json` plugin entries synced to the same versions; top-level
  version +0.0.1 **once** for the release
- `CHANGELOG.md` entries for both
- `scripts/check_version_sync.sh` must pass
- No skill was added or renamed → `generate_improve_map.py` is not needed; run it only if the
  CI table check complains.
- Update `.claude/STATUS.md` in the same session (workspace `CLAUDE.md` rule).
- `~/Projects/BLUEGREEN_MAP.md` version tables go stale on release — update them too.

---

## Out of scope

- Writing to a calendar (creating the ophthalmologist appointment). Separate issue.
- The `jobsearch` plugin and `improve` — no workspace slug, no second user.
- `cv-master.json` (above).
- Anything in the `hal` repo — phase 1, handled in its own session.

## Acceptance

- A user who belongs to exactly one workspace, and to none of the author's, can run
  `morning-briefing`, `sprint-planner` and `sprint-review` and get a correct result for *their*
  workspace.
- No workspace slug, calendar ID or mailbox address remains as a literal in any
  `plugins/briefing/**` or `plugins/mycoach/**` file.
- Every skill that reads hal probes first, and stops with an explicit message — quoting what it
  actually received — when it cannot resolve its context. No skill improvises on an empty or
  unexpected result.
- `mycoach` never writes to a workspace it did not resolve through the `mycoach` tag.
- Renaud's own run renders the same information as before, plus the household workspace, which
  is currently invisible to it — `rosaslaborbe` holds 6 open tasks that no skill reads today.
- `check_version_sync.sh` exits 0.
