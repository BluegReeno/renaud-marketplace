#!/usr/bin/env python3
"""Generate the /improve skill->plugin->repo lookup table from both marketplaces.

Enumerates every skill from:
  - this repo (local): .claude-plugin/marketplace.json plugin entries UNION the
    plugins/*/skills/* directory names;
  - bluegreen-marketplace (remote): its marketplace.json plugin entries UNION the
    plugins/<plugin>/skills/ directory listings, fetched via the `gh` CLI.

It then rewrites the table between the `<!-- improve-map:start -->` and
`<!-- improve-map:end -->` markers in plugins/improve/skills/improve/SKILL.md.

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


def die(msg):
    sys.exit(f"ERROR    {msg}")


# --- gh CLI helpers ----------------------------------------------------------


def gh_api(path):
    try:
        result = subprocess.run(
            ["gh", "api", path], capture_output=True, text=True, check=True
        )
    except FileNotFoundError:
        die("`gh` CLI not found — required to enumerate the remote marketplace")
    except subprocess.CalledProcessError as exc:
        die(f"gh api {path} failed: {exc.stderr.strip()}")
    return result.stdout


def gh_api_json(path):
    try:
        return json.loads(gh_api(path))
    except json.JSONDecodeError as exc:
        die(f"gh api {path} returned invalid JSON: {exc}")


def remote_file(rel_path):
    """Fetch a text file from the remote repo via the Contents API."""
    data = gh_api_json(f"repos/{REMOTE_REPO}/contents/{rel_path}")
    if not isinstance(data, dict) or "content" not in data:
        die(f"remote {rel_path} has no file content")
    try:
        return base64.b64decode(data["content"]).decode("utf-8")
    except (ValueError, UnicodeDecodeError) as exc:
        die(f"cannot decode remote {rel_path}: {exc}")


def remote_skill_dirs(plugin):
    """List skill directory names under the remote plugin's skills/ folder."""
    data = gh_api_json(f"repos/{REMOTE_REPO}/contents/plugins/{plugin}/skills")
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

    table = render_table(rows)

    try:
        with open(SKILL_MD, encoding="utf-8") as handle:
            content = handle.read()
    except OSError as exc:
        die(f"cannot read {SKILL_MD}: {exc}")

    if START not in content or END not in content:
        die(f"markers {START} / {END} not found in {SKILL_MD}")

    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
    replacement = f"{START}\n\n{table}\n\n{END}"
    new_content = pattern.sub(lambda _m: replacement, content, count=1)

    if new_content != content:
        with open(SKILL_MD, "w", encoding="utf-8") as handle:
            handle.write(new_content)
        sys.stderr.write(f"updated {os.path.relpath(SKILL_MD, REPO_ROOT)} ({len(rows)} skills)\n")
    else:
        sys.stderr.write(f"up to date ({len(rows)} skills)\n")


if __name__ == "__main__":
    main()
