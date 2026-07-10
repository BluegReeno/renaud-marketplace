# Claude Code Skill Marketplace — Field Guide

> Lessons learned building `bluegreen-marketplace` and `renaud-marketplace`.
> This doc is the reference when starting or evolving a marketplace repo.

---

## 1. Public vs Private — Decide First

This is the most important architectural decision. Get it wrong and you'll either
expose sensitive data or break the client install flow.

| Repo type | When to use | Examples |
|-----------|-------------|---------|
| **Public** | Client-installable plugins, tools you distribute to others | `bluegreen-marketplace`, `renaud-marketplace` |
| **Private** | Skills bundling secrets or unpublished personal data that can't be gitignored | — |

**Rule of thumb**: if a skill file *bundles* personal info (phone, address, strategy notes,
financial data, active job pipelines) that you can't keep out via gitignore, the repo must be
private. `renaud-marketplace` is public because its sensitive data is gitignored, not committed.

### How clients install from a public marketplace

```bash
/plugin marketplace add BluegReeno/bluegreen-marketplace
```

### How you install from a private repo (yourself only)

If a marketplace genuinely must stay private, add a GitHub PAT with `repo` read scope to
`~/.claude/settings.json`:

```json
{
  "plugins": {
    "sources": [
      {
        "repo": "BluegReeno/your-private-marketplace",
        "token": "ghp_xxxxxxxxxxxx"
      }
    ]
  }
}
```

You get the same "update = git push" UX without exposing anything.

---

## 2. Repo Structure

Every marketplace repo follows the same layout, whether public or private:

```
my-marketplace/
├── .claude-plugin/
│   └── marketplace.json          # Registry entry point (required by Claude Code)
├── plugins/
│   ├── my-plugin/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json       # name, version, description, author
│   │   ├── .mcp.json             # MCP server if needed (SSE endpoint + version)
│   │   ├── skills/
│   │   │   └── my-skill/
│   │   │       └── SKILL.md      # The skill instructions (frontmatter + body)
│   │   ├── scripts/              # Python scripts invoked by skills
│   │   ├── templates/            # Any assets (DOCX, HTML, etc.)
│   │   ├── data/                 # Static data files (JSON, etc.)
│   │   └── CHANGELOG.md
│   └── another-plugin/
│       └── .gitkeep              # Placeholder for future plugin
└── docs/
    └── skill-marketplace-guide.md  # This file
```

### marketplace.json — the registry entry point

```json
{
  "version": "0.1.0",
  "name": "my-marketplace",
  "description": "My personal skill marketplace",
  "plugins": [
    {
      "name": "my-plugin",
      "version": "0.1.0",
      "description": "What this plugin does",
      "path": "plugins/my-plugin"
    }
  ]
}
```

**Critical rule**: for each plugin, the `marketplace.json` `plugins[].version` entry must
equal that plugin's `plugin.json` `version`. They are kept in sync manually at every release.
Drift on the per-plugin entry breaks installs. (The top-level `marketplace.json` `version`
is a separate monotonic release counter — see §5.)

### plugin.json — the plugin manifest

```json
{
  "name": "my-plugin",
  "version": "0.1.2",
  "description": "Short description",
  "author": { "name": "Renaud Laborbe", "email": "renaud@bluegreen.ai" }
}
```

---

## 3. SKILL.md Structure

Every skill has a YAML frontmatter block followed by the instructions.

```markdown
---
name: my-skill
description: >
  One sentence that Claude uses to decide when to load this skill.
  Good triggers: "when the user does X", "when file Y exists".
allowed-tools: "Bash(uv *) Bash(python3 *) Read Write Edit"
---

# My Skill — Title

## What it does (brief)

## Step 1: ...

## Step 2: ...
```

**Tips from experience:**
- The `description` field is what Claude uses to decide when to auto-load the skill.
  Write it as a trigger sentence, not a marketing blurb.
- `allowed-tools` should be minimal — only what the skill actually uses.
- SKILL.md is the source of truth for instructions. Don't duplicate logic in scripts.

---

## 4. The Cowork Constraint — The Most Important Technical Rule

Claude Cowork mounts a **fresh ephemeral directory every session**. Nothing is pre-installed.
If your skill requires a `pip install` step before it works, it will break the UX.

### Decision tree for script dependencies

| Situation | Pattern |
|-----------|---------|
| Pure stdlib (`json`, `pathlib`, `urllib`, `re`…) | `python3 script.py` |
| 1–2 small packages unavoidable | `uv run --with pkg1 --with pkg2 script.py` |
| Heavy SDK (`supabase`, `langchain`…) | **Refactor to stdlib first.** If impossible, `uv run --with` |

**Reference implementation**: `bluegreen-marketplace/plugins/hal/scripts/build_context.py`
uses only stdlib. It was refactored away from the `supabase` Python SDK to use `urllib`
directly — zero download at session start, instant cold start.

```bash
# NEVER in a skill:
pip install -r requirements.txt

# CORRECT: one-shot install at invocation time
uv run --with "docxtpl>=0.18" --with pillow python3 $PLUGIN_DIR/scripts/render.py
```

Keep the `uv --with` package list as short as possible. `requirements.txt` is a human
manifest only — never executed at runtime.

---

## 5. Versioning Policy

Each component tracks its version independently. This prevents false "breaking change"
signals when only one piece changes.

SKILL.md frontmatter no longer carries a `version:` field — a plugin's version
lives at the plugin level only.

| Component | Version field | File |
|-----------|--------------|------|
| Plugin | `"version"` | `plugins/my-plugin/.claude-plugin/plugin.json` |
| MCP server | `"version"` | `plugins/my-plugin/.mcp.json` |
| Marketplace (per plugin) | `plugins[].version` | `.claude-plugin/marketplace.json` |
| Marketplace (top-level) | `"version"` | `.claude-plugin/marketplace.json` |

### Bump rules

- `PATCH` (`0.x.Y+1`) — bugfix, internal improvement, optional field added
- `MINOR` (`0.X+1.0`) — interface change: new required command, renamed CLI flag, new
  required JSON field, new observable behavior

**Per release (the enforced 2-field invariant):**
1. Bump each component that changed → its own PATCH or MINOR
2. Plugin → always PATCH+1 once per release (regardless of how many components changed)
3. Sync **two fields** per-plugin: `plugin.json` `version` === `marketplace.json`
   `plugins[].version` for that entry. `scripts/check_version_sync.sh` enforces this
   (exit 1 on drift) and also fails if `CHANGELOG.md` lacks an entry for the current version.
4. Top-level `marketplace.json` `version` is a **monotonic release counter** — bump it
   `+0.0.1` on every release, independent of plugin version numbers. It only signals
   Cowork that a new release exists; it is a process rule, not statically checked.

---

## 6. Bundling MCP Servers

If your plugin uses an MCP server, bundle it via `.mcp.json` at the plugin root.
This removes connector setup friction during client onboarding — the MCP starts
automatically when the plugin is installed.

```json
{
  "mcpServers": {
    "my-mcp": {
      "type": "sse",
      "url": "https://my-mcp-server.com/sse",
      "version": "0.1.0"
    }
  }
}
```

**Lesson learned**: before `.mcp.json` bundling, clients had to manually configure the
connector in their Claude Code settings — a friction point at onboarding that was
eliminated by the bundle approach.

### Sharing an MCP server across plugins (dedup convention)

When the same MCP server is bundled by two plugins (e.g. `hal-mcp` declared in both
`bluegreen-marketplace/plugins/hal/.mcp.json` and
`renaud-marketplace/plugins/briefing/.mcp.json`), Claude Code dedupes the two
declarations into a single connection **only if** the entries match on three fields:

| Field | Must match across all declarations |
|-------|-----------------------------------|
| `mcpServers.<name>` key | Same string (e.g. `"hal-mcp"`) |
| `url` | Byte-identical URL |
| `version` | Identical version string |

If any of the three drifts, the user gets two parallel sessions — double OAuth prompt,
double tool listings, double quota.

**The dedup `version` is not the upstream server version — it's a coordination token.**
Pick the value once, document it in both `.mcp.json` files, and bump in both
simultaneously. A reader who "corrects" `hal-mcp` dedup version `"0.1.0"` to the upstream
`"38.0.0"` will silently break dedup.

---

## 7. Plugin Directory Resolution in SKILL.md

Skills need to locate the plugin directory at runtime, whether installed from the
marketplace cache, running in Cowork, or running from a local dev path. Use a
priority-ordered resolver:

```bash
PLUGIN_DIR=$(python3 - <<'PYEOF'
import json, os, pathlib, sys, glob as _glob

home = pathlib.Path.home()

# 1. Env var override (for dev)
env = os.environ.get('MY_PLUGIN_DIR', '')
if env and pathlib.Path(env, 'scripts', 'my_script.py').exists():
    print(env); sys.exit(0)

# 2. Claude Code marketplace cache
for mkt in ['renaud-marketplace', 'bluegreen-marketplace']:
    cache_root = home / '.claude' / 'plugins' / 'cache' / mkt / 'my-plugin'
    if cache_root.exists():
        candidates = sorted(
            cache_root.glob('*/scripts/my_script.py'),
            key=lambda p: p.stat().st_mtime, reverse=True
        )
        if candidates:
            print(str(candidates[0].parent.parent)); sys.exit(0)

# 3. Cowork sandbox
for pat in ['/sessions/*/mnt/.remote-plugins/*/scripts/my_script.py']:
    matches = sorted(_glob.glob(pat), key=os.path.getmtime, reverse=True)
    if matches:
        print(os.path.dirname(os.path.dirname(matches[0]))); sys.exit(0)

# 4. Known dev paths
for dev in [
    home / 'Projects' / 'renaud-marketplace' / 'plugins' / 'my-plugin',
    home / 'Projects' / 'bluegreen-marketplace' / 'plugins' / 'my-plugin',
]:
    if dev.joinpath('scripts', 'my_script.py').exists():
        print(str(dev)); sys.exit(0)

print('PLUGIN_DIR_NOT_FOUND')
PYEOF
)
if [ "$PLUGIN_DIR" = "PLUGIN_DIR_NOT_FOUND" ]; then
  echo "ERROR: Plugin dir not found. Set MY_PLUGIN_DIR=<path> in your shell."
  exit 1
fi
```

---

## 8. Release Process (one command + CI check)

Use the release orchestrator — it performs the whole bump in one validated pass and
commits (it never pushes, merges, or tags; you do that after review):

```bash
./scripts/release.sh <plugin> <new-version> "<changelog line>" [--mcp-version <v>]
# e.g. ./scripts/release.sh improve 0.2.0 "generated skill→repo map"
```

It bumps `plugin.json`, syncs the `marketplace.json` plugin entry, inserts the
`CHANGELOG.md` entry, bumps the top-level monotonic counter, runs
`check_version_sync.sh`, and commits — all validation runs *before* any file is
written, so a failed check leaves the tree clean.

CI (`.github/workflows/ci.yml`) then verifies the invariant on every push and pull
request via `scripts/check_version_sync.sh`, and re-runs `scripts/generate_improve_map.py`
with `git diff --exit-code` to reject a stale `/improve` table.

**Under the hood** — what `release.sh` does by hand, if you ever need to bump manually:

```bash
# 1. Bump version in each modified component (see Versioning Policy)
# 2. Bump plugin version in plugin.json
# 3. Sync the per-plugin entry in marketplace.json (plugins[].version) to plugin.json
# 4. Add a `## <plugin> <version>` entry to CHANGELOG.md
# 5. Bump the top-level marketplace.json version by +0.0.1 (monotonic counter)
# 6. Commit and push
git add plugins/my-plugin/.claude-plugin/plugin.json
git add .claude-plugin/marketplace.json CHANGELOG.md
git commit -m "chore(my-plugin): release vX.Y.Z"
git push
```

Before releasing: verify the per-plugin pair is identical — `plugin.json` `version`
and `marketplace.json` `plugins[].version` for that entry — and that `CHANGELOG.md`
has an entry for the current version. `scripts/check_version_sync.sh` (run in CI)
enforces both. The top-level `marketplace.json` `version` is a separate monotonic
release counter (see §5): bump it `+0.0.1` on every release.

---

## 9. What to Keep Out of a Plugin

Things that do NOT belong in the plugin directory:

| What | Where instead |
|------|--------------|
| API keys, tokens | Shell env vars or `~/.claude/settings.json` |
| Personal data files (CV data, contacts) | Local `data/` outside repo, or gitignored |
| Large binary assets | Git LFS or external storage (signed URLs) |
| Python virtualenvs, `__pycache__` | `.gitignore` (already handled) |
| Test fixtures with sensitive data | Separate private test repo |

---

## 10. CLAUDE.md for a Marketplace Repo

Keep it lean. The most important rules:

```markdown
## Plugin Skill Constraint — No pre-install step
Skills must never require pip install. Use stdlib or uv run --with.

## Versioning — 2-field invariant + CHANGELOG
plugin.json version == marketplace.json plugins[].version; CHANGELOG.md documents the
current version. Verified by scripts/check_version_sync.sh.

## Source of truth for shared scripts
If scripts are shared across plugins, pick ONE location as canonical.
Never sync from external repos at runtime.

## Release cadence
Manual bump → commit → push; CI (check_version_sync.sh + deno check) runs on every PR and push.
```

---

## Checklist — New Plugin

- [ ] `plugins/my-plugin/.claude-plugin/plugin.json` created
- [ ] `plugins/my-plugin/skills/my-skill/SKILL.md` created with frontmatter
- [ ] `.claude-plugin/marketplace.json` updated with new plugin entry
- [ ] `marketplace.json` version synced to `plugin.json` version
- [ ] Scripts use stdlib or `uv run --with` (no pip install)
- [ ] Plugin directory resolver in SKILL.md covers: env var → cache → Cowork → dev path
- [ ] `CHANGELOG.md` created with initial entry
- [ ] `.mcp.json` added if plugin uses an MCP server
