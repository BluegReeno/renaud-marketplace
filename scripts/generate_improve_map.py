#!/usr/bin/env python3
"""Generate the /improve skill->plugin->repo lookup table from both marketplaces.

Enumerates every skill from:
  - this repo (local): .claude-plugin/marketplace.json plugin entries UNION the
    plugins/*/skills/* directory names;
  - bluegreen-marketplace (remote): its marketplace.json plugin entries UNION the
    plugins/<plugin>/skills/ directory listings, fetched via the `gh` CLI;
  - EXTRA_TARGETS: valid `/improve` destinations that carry no skill directory
    in either marketplace, because the real code lives in a third repo.

It then rewrites, in plugins/improve/skills/improve/SKILL.md:
  - the routing table between `<!-- improve-map:start -->` / `:end`;
  - the Step 1 `AskUserQuestion` options list between
    `<!-- improve-options:start -->` / `:end`, rendered from the same rows so
    it cannot drift from the table.

Contract:
  - any network / parse / missing-marker failure aborts with a non-zero exit and
    writes NOTHING (no partial table);
  - idempotent: a second run produces a byte-identical file (zero git diff).

Dependencies: Python 3 stdlib + `gh` CLI (authenticated).
"""

import base64
import json
import os
import re
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL_MARKETPLACE = os.path.join(REPO_ROOT, ".claude-plugin", "marketplace.json")
SKILL_MD = os.path.join(
    REPO_ROOT, "plugins", "improve", "skills", "improve", "SKILL.md"
)
REMOTE_REPO = "BluegReeno/bluegreen-marketplace"
START = "<!-- improve-map:start -->"
END = "<!-- improve-map:end -->"
OPTIONS_START = "<!-- improve-options:start -->"
OPTIONS_END = "<!-- improve-options:end -->"

# Targets that are valid `/improve` destinations but carry no skill directory
# in either marketplace — the real code lives in a third repo entirely.
# `hal` is connector-only in bluegreen-marketplace (remote_skill_dirs() below
# returns no rows for it by design), but the MCP server it wraps lives in
# BluegReeno/hal (see hal-mcp#94) — without this entry, `/improve hal` has
# nowhere to land and falls back to the nearest marketplace wrapper.
EXTRA_TARGETS = [
    ("hal", "—", "hal"),
]


def die(msg):
    sys.exit(f"ERROR    {msg}")


# --- gh CLI helpers ----------------------------------------------------------


MISSING = object()  # sentinel: the remote path does not exist (HTTP 404)


def gh_api(path):
    """Return the raw response body, or MISSING when the path does not exist.

    Only a 404 yields MISSING — every other failure still aborts, so a broken
    token or a renamed repo can never be mistaken for an absent directory.
    """
    try:
        result = subprocess.run(
            ["gh", "api", path], capture_output=True, text=True, check=True
        )
    except FileNotFoundError:
        die("`gh` CLI not found — required to enumerate the remote marketplace")
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        if "HTTP 404" in stderr:
            return MISSING
        die(f"gh api {path} failed: {stderr}")
    return result.stdout


def gh_api_json(path):
    raw = gh_api(path)
    if raw is MISSING:
        return MISSING
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        die(f"gh api {path} returned invalid JSON: {exc}")


def remote_file(rel_path):
    """Fetch a text file from the remote repo via the Contents API."""
    data = gh_api_json(f"repos/{REMOTE_REPO}/contents/{rel_path}")
    if data is MISSING:
        die(f"remote {rel_path} not found in {REMOTE_REPO}")
    if not isinstance(data, dict) or "content" not in data:
        die(f"remote {rel_path} has no file content")
    try:
        return base64.b64decode(data["content"]).decode("utf-8")
    except (ValueError, UnicodeDecodeError) as exc:
        die(f"cannot decode remote {rel_path}: {exc}")


def remote_skill_dirs(plugin):
    """List skill directory names under the remote plugin's skills/ folder.

    A plugin with no skills/ directory returns no rows instead of aborting —
    `hal` is a connector-only plugin and carries no skill at all. Mirrors
    local_skill_dirs(), which has always tolerated the directory being absent.
    """
    data = gh_api_json(f"repos/{REMOTE_REPO}/contents/plugins/{plugin}/skills")
    if data is MISSING:
        return []
    if not isinstance(data, list):
        die(f"remote plugins/{plugin}/skills is not a directory listing")
    return sorted(d["name"] for d in data if d.get("type") == "dir")


# --- local helpers -----------------------------------------------------------


def local_skill_dirs(plugin):
    skills_dir = os.path.join(REPO_ROOT, "plugins", plugin, "skills")
    if not os.path.isdir(skills_dir):
        return []
    return sorted(
        name
        for name in os.listdir(skills_dir)
        if os.path.isdir(os.path.join(skills_dir, name))
    )


def load_local_marketplace():
    try:
        with open(LOCAL_MARKETPLACE, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        die(f"cannot read {LOCAL_MARKETPLACE}: {exc}")


# --- collection --------------------------------------------------------------


def collect(marketplace, repo_name, skill_dirs_fn):
    """Return (skill, plugin, repo) rows for one marketplace.

    Skills are the UNION of the marketplace.json `skills` basenames and the
    on-disk / remote skill directory names, so an entry missing from either
    source is still surfaced.
    """
    rows = []
    plugins = marketplace.get("plugins", [])
    if not isinstance(plugins, list):
        die(f"marketplace for {repo_name} has no 'plugins' array")
    for entry in plugins:
        plugin = entry.get("name") or entry.get("id")
        if not plugin:
            die(f"marketplace for {repo_name} has a plugin entry with no name/id")
        skills = {os.path.basename(s.rstrip("/")) for s in entry.get("skills", [])}
        skills.update(skill_dirs_fn(plugin))
        for skill in skills:
            rows.append((skill, plugin, repo_name))
    return rows


def render_table(rows):
    headers = ("Skill", "Plugin", "Repo")
    grid = [headers] + list(rows)
    widths = [max(len(row[col]) for row in grid) for col in range(3)]

    def fmt(cells):
        return "| " + " | ".join(c.ljust(w) for c, w in zip(cells, widths)) + " |"

    lines = [fmt(headers), "|-" + "-|-".join("-" * w for w in widths) + "-|"]
    lines.extend(fmt(row) for row in rows)
    return "\n".join(lines)


def render_options(rows):
    """Render the Step 1 `AskUserQuestion` skill list from the same rows as the table.

    Single source of truth: this list can no longer drift from the routing
    table, because both are rendered from the same `rows`.
    """
    return ", ".join(f"`{skill}`" for skill, _plugin, _repo in rows)


def main():
    local = load_local_marketplace()
    local_name = local.get("name", "renaud-marketplace")

    remote = json.loads(remote_file(".claude-plugin/marketplace.json"))
    remote_name = remote.get("name", "bluegreen-marketplace")

    rows = collect(local, local_name, local_skill_dirs)
    rows += collect(remote, remote_name, remote_skill_dirs)

    # Deterministic order: local repo first, then remote; within each, by
    # (plugin, skill). Guarantees idempotency regardless of set iteration order.
    rows.sort(key=lambda r: (0 if r[2] == local_name else 1, r[1], r[0]))

    # Non-marketplace targets are appended last, in their own group.
    rows += EXTRA_TARGETS

    table = render_table(rows)
    options = render_options(rows)

    try:
        with open(SKILL_MD, encoding="utf-8") as handle:
            content = handle.read()
    except OSError as exc:
        die(f"cannot read {SKILL_MD}: {exc}")

    if START not in content or END not in content:
        die(f"markers {START} / {END} not found in {SKILL_MD}")
    if OPTIONS_START not in content or OPTIONS_END not in content:
        die(f"markers {OPTIONS_START} / {OPTIONS_END} not found in {SKILL_MD}")

    table_pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
    new_content = table_pattern.sub(
        lambda _m: f"{START}\n\n{table}\n\n{END}", content, count=1
    )

    options_pattern = re.compile(
        re.escape(OPTIONS_START) + r".*?" + re.escape(OPTIONS_END), re.DOTALL
    )
    new_content = options_pattern.sub(
        lambda _m: f"{OPTIONS_START}{options}{OPTIONS_END}", new_content, count=1
    )

    if new_content != content:
        with open(SKILL_MD, "w", encoding="utf-8") as handle:
            handle.write(new_content)
        sys.stderr.write(f"updated {os.path.relpath(SKILL_MD, REPO_ROOT)} ({len(rows)} skills)\n")
    else:
        sys.stderr.write(f"up to date ({len(rows)} skills)\n")


if __name__ == "__main__":
    main()
