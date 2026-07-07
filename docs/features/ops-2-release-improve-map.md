# Brief — Ops 2 (renaud-marketplace): release script + generated /improve map

> **Context**: Ops 1 (merged) reduced the version invariant to two enforced fields.
> Releases are still a manual multi-location bump, and the `/improve` skill routes
> observations to repos via a hand-maintained lookup table that is already stale
> (missing `log-cr`, `mail-triage`, `myspy`, `sprint-review`). The sibling repo
> bluegreen-marketplace has an identical `scripts/release.sh` (its Ops 2, merged
> first — mirror it). Part of a multi-repo ops track; self-contained.
>
> Read `CLAUDE.md`, `CONTRIBUTING.md`, and
> `plugins/improve/skills/improve/SKILL.md` first.

## Objective

One-command releases, and a skill→plugin→repo map for `/improve` that is generated
from the two marketplaces' actual content and CI-guarded against drift.

## Non-goals

- No behavior change to `/improve` beyond the table content and its markers (the
  skill's flow — observation → GitHub issue labeled `ai-improvable` — is
  untouched).
- No runtime fetching in the skill itself (`/improve` runs in Cowork without
  Bash; the map must be baked in at build time).
- No morning-briefing changes (separate brief).

## Deliverables

### D1 — `scripts/release.sh <plugin> <new-version> "<changelog line>"`

Mirror bluegreen-marketplace's `scripts/release.sh` line-for-line as closely as
possible, adapted for this repo's four plugins. Same contract: validate everything
before writing anything; update plugin.json + marketplace entry + top-level
counter + CHANGELOG; run `scripts/check_version_sync.sh`; commit
`chore(<plugin>): release v<new-version>`; never push. Refuse (exit 1, clear
message) on: unknown plugin, non-increasing semver, dirty tree, existing CHANGELOG
entry, missing changelog line.

### D2 — Generated skill→repo map for `/improve`

- `scripts/generate_improve_map.py` (Python 3, stdlib + `gh` CLI):
  - enumerate local plugins/skills from `.claude-plugin/marketplace.json` and
    `plugins/*/skills/*/` directory names;
  - enumerate bluegreen-marketplace's plugins/skills via
    `gh api repos/BluegReeno/bluegreen-marketplace/contents/...` (marketplace.json
    + skills directories);
  - any network/parse failure ⇒ exit 1 with the error — never write a partial
    table;
  - rewrite the table between `<!-- improve-map:start -->` and
    `<!-- improve-map:end -->` markers in
    `plugins/improve/skills/improve/SKILL.md`, mapping
    skill → plugin → repo (`BluegReeno/renaud-marketplace` or
    `BluegReeno/bluegreen-marketplace`);
  - idempotent: second run produces zero diff.
- Add the markers around the existing table and regenerate (this fixes the four
  missing skills).
- CI (`.github/workflows/ci.yml`): add a step
  `python3 scripts/generate_improve_map.py && git diff --exit-code` so a stale
  map fails the build.
- Release the plugin: `bash scripts/release.sh improve 0.2.0 "generated
  skill→repo map"`.

### D3 — CONTRIBUTING.md

New-skill checklist gains one line: "run `scripts/generate_improve_map.py`".

## Acceptance criteria

```bash
python3 scripts/generate_improve_map.py && git diff --exit-code   # idempotent
grep -n "log-cr\|mail-triage\|myspy\|sprint-review" plugins/improve/skills/improve/SKILL.md
bash scripts/check_version_sync.sh                                 # green post-release
bash scripts/release.sh; echo $?                                   # 1 + usage
```

## Final reminders

- `set -euo pipefail` in shell; loud errors; no partial writes anywhere.
- Scripts never push, never merge.
