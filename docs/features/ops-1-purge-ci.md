# Brief — Ops 1 (renaud-marketplace): version policy + stale docs + CI

> **Context**: the four plugins are healthy, but the repo documents a 3-field
> version-sync rule that its own check script does not enforce (SKILL.md drift is
> INFO-only and already real), the README plugin table is stale, and there is no CI.
> Part of a multi-repo ops track; this brief is self-contained for this repo.
>
> Read `CLAUDE.md` and `CONTRIBUTING.md` before starting. Scope: version-policy
> simplification, doc fixes, CI bootstrap ONLY.

## Objective

Reduce the version invariant to two enforced fields, fix stale docs, add CI running
the sync check + type checks.

## Non-goals (do NOT implement)

- No skill behavior changes (all SKILL.md edits are frontmatter/doc only).
- No release automation script and no /improve map generation (separate Ops 2
  briefs).
- No gmail-mcp code changes (`deno check` only).
- Local branch pruning and root clutter (`CV_*.pdf`, `tmp/`, `oauth/`) are manual
  steps outside this run — do not reference them.

## Deliverables

### D1 — Simplify the version policy (2 fields, not 3)

- Drop the `version:` field from every `plugins/*/skills/*/SKILL.md` frontmatter.
- Update CLAUDE.md + CONTRIBUTING.md: the enforced invariant is
  `plugin.json.version == marketplace.json plugin entry`, plus the top-level
  monotonic counter.
- Harden `scripts/check_version_sync.sh`: remove the SKILL.md INFO-only code path
  entirely; the remaining 2-field invariant is exit-1 enforced; also exit 1 if
  CHANGELOG.md lacks an entry for a plugin's current version.

### D2 — Fix stale docs

- README plugin table still lists `jobsearch 0.4.8` / `briefing 0.4.3` (reality:
  `0.8.3` / `0.8.0`). Rewrite the table by hand from
  `.claude-plugin/marketplace.json` values. (Automated generation is out of
  scope.)
- Rename `breif-gmail.md` → delete if obsolete or move under `docs/` with a
  correct name — decide by reading it; it must not stay misspelled at root if
  tracked. If untracked, ignore it.

### D3 — CI: `.github/workflows/ci.yml`

On `pull_request` + `push` to main:
- `bash scripts/check_version_sync.sh`
- `deno check servers/gmail-mcp/supabase/functions/gmail-mcp/index.ts`
- Run existing pytest suites under `plugins/` if any exist (check first; if none,
  omit the job — do not create placeholder tests).

## Acceptance criteria

```bash
grep -rn "^version:" plugins/*/skills/*/SKILL.md | wc -l    # 0
bash scripts/check_version_sync.sh                           # exit 0
grep -c "0.4.8" README.md                                    # 0
ls .github/workflows/ci.yml
```

## Final reminders

- No placeholder tests, no TODO comments.
- CI must fail on failure — no `|| true`, no `continue-on-error`.
- PR description lists every doc correction and the exact new invariant.
