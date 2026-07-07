# Brief — Ops 2 (renaud-marketplace): /briefing --headless + gmail-mcp deploy script

> **Context**: the morning-briefing skill already anticipates scheduled runs (plan
> marked `[proposé — non validé]`), but the mode is inferred, not contracted, and
> two `TODO: verify in Cowork` questions linger around the CV fan-out. A nightly
> scheduler (Ops 3, separate repo) will call `/briefing --headless` via `claude -p`
> — the contract must be explicit. gmail-mcp deploys are also still manual. Part of
> a multi-repo ops track; self-contained. Run this AFTER the release-script brief
> is merged (it uses `scripts/release.sh`).
>
> Read `plugins/briefing/skills/morning-briefing/SKILL.md` fully first.

## Objective

`/briefing --headless` is an explicit, documented mode safe to run unattended; and
gmail-mcp gets a one-command deploy with verification.

## Non-goals

- No new briefing data sources, no layout changes to the 6-block brief.
- No scheduling, no launchd (Ops 3, separate repo).
- No gmail-mcp code changes (deploy script only).
- Interactive behavior (no flag) must remain byte-for-byte unchanged.

## Deliverables

### D1 — Explicit `--headless` contract in morning-briefing

Edit `plugins/briefing/skills/morning-briefing/SKILL.md`:

- `/briefing --headless` ⇒
  - Step 1h (CV fan-out via sub-agents) is not executed; the brief contains the
    line `CV pre-generation: skipped (headless mode)` — the omission is visible,
    never silent;
  - the "plan du jour" carries the `[proposé — non validé]` marker and is NOT
    written to hal;
  - daily-log writes (`save_document` per workspace) still happen — they are the
    point of the headless run;
  - a connector that fails (calendar, gmail, brightdata) ⇒ its block states
    `<source>: UNAVAILABLE (<error>)` and the run continues — visible
    degradation. Exception: hal unreachable ⇒ abort with an error, since the
    daily-log write is the run's purpose.
- Replace the current "scheduled/automated run" inference prose with this
  explicit flag contract.
- Resolve (delete) the two `TODO: verify in Cowork` comments: in headless mode
  the sub-agent question is moot (no fan-out); interactive mode keeps current
  behavior.
- Release: `bash scripts/release.sh briefing 0.9.0 "explicit --headless mode"`.

### D2 — `servers/gmail-mcp/scripts/deploy.sh`

- Assert the linked project is `isdyvrwnxqcfalmlkzui` (parse
  `supabase projects list`); otherwise exit 1 printing the exact
  `supabase link --project-ref isdyvrwnxqcfalmlkzui` fix.
- `supabase functions deploy gmail-mcp --no-verify-jwt`.
- Verify: curl the function URL; 401/400/405 ⇒ alive and auth-rejecting, exit 0;
  404/5xx/timeout ⇒ exit 1 printing the code.
- Document the script in `servers/gmail-mcp/README.md`.

## Acceptance criteria

```bash
grep -n "\-\-headless" plugins/briefing/skills/morning-briefing/SKILL.md   # contract present
grep -c "TODO: verify in Cowork" plugins/briefing/skills/morning-briefing/SKILL.md  # 0
bash servers/gmail-mcp/scripts/deploy.sh    # exit 0, function verified
bash scripts/check_version_sync.sh           # green after release
```

## Final reminders

- Degradation must always be visible in output ("skipped (headless mode)",
  "UNAVAILABLE") — never silent.
- `set -euo pipefail` in the deploy script; loud, actionable errors.
