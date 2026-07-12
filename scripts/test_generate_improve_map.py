#!/usr/bin/env python3
"""Offline tests for scripts/generate_improve_map.py.

Covers:
- deterministic row sort: local repo first; (plugin, skill) within each group
- table alignment / rendering
- die() abort paths: missing markers, invalid JSON, non-list skill listing
  (no network — gh_api is monkey-patched throughout)

Run: python3 scripts/test_generate_improve_map.py
"""

import base64
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import unittest

# ── load module without triggering __main__ ───────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "generate_improve_map",
    os.path.join(_HERE, "generate_improve_map.py"),
)
gim = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gim)


# ── shared helpers ────────────────────────────────────────────────────────────

def _mkt(name, plugins):
    return {"name": name, "plugins": plugins}


def _no_dirs(_plugin):
    return []


def _b64(obj):
    """Return base64(JSON(obj)) — matches the GitHub Contents API 'content' field."""
    return base64.b64encode(json.dumps(obj).encode()).decode()


def _gh_stub(remote_mkt, skill_dirs=None):
    """Return a gh_api stub that handles marketplace + skills directory calls.

    skill_dirs: dict {plugin_name: [dir_name, ...]} for remote plugins that have
    skills; omit or pass None to return an empty list for every plugin.
    """
    encoded = _b64(remote_mkt)

    def stub(path):
        if "/contents/.claude-plugin/" in path:
            return json.dumps({"content": encoded})
        if "/contents/plugins/" in path and path.endswith("/skills"):
            plugin = path.split("/plugins/")[1].split("/skills")[0]
            dirs = (skill_dirs or {}).get(plugin, [])
            return json.dumps([{"name": d, "type": "dir"} for d in dirs])
        return json.dumps([])

    return stub


class _Tmp:
    def __enter__(self):
        self.path = tempfile.mkdtemp()
        return self.path

    def __exit__(self, *_):
        shutil.rmtree(self.path, ignore_errors=True)


def _write_skill_md(path, with_markers=True):
    content = "# Improve\n\n"
    if with_markers:
        content += f"{gim.START}\n\n| Skill | Plugin | Repo |\n|-------|--------|------|\n\n{gim.END}\n"
    else:
        content += "No markers here.\n"
    with open(path, "w") as fh:
        fh.write(content)


# ── 1. Row-sort determinism ───────────────────────────────────────────────────

class TestRowSortDeterminism(unittest.TestCase):

    def _sorted_rows(self, local_name, remote_name, local_plugins, remote_plugins):
        rows = gim.collect(_mkt(local_name, local_plugins), local_name, _no_dirs)
        rows += gim.collect(_mkt(remote_name, remote_plugins), remote_name, _no_dirs)
        rows.sort(key=lambda r: (0 if r[2] == local_name else 1, r[1], r[0]))
        return rows

    def test_local_first_regardless_of_plugin_name(self):
        """Local rows precede remote rows even if remote plugin sorts alphabetically first."""
        rows = self._sorted_rows(
            "z-local", "a-remote",
            [{"name": "z-plugin", "skills": ["z-skill"]}],
            [{"name": "a-plugin", "skills": ["a-skill"]}],
        )
        self.assertEqual([r[2] for r in rows], ["z-local", "a-remote"])

    def test_within_group_sorted_by_plugin_then_skill(self):
        rows = self._sorted_rows(
            "local", "remote",
            [
                {"name": "b-plugin", "skills": ["z-skill", "a-skill"]},
                {"name": "a-plugin", "skills": ["m-skill"]},
            ],
            [],
        )
        self.assertEqual(rows, [
            ("m-skill", "a-plugin", "local"),
            ("a-skill", "b-plugin", "local"),
            ("z-skill", "b-plugin", "local"),
        ])

    def test_remote_group_sorted_by_plugin_then_skill(self):
        rows = self._sorted_rows(
            "local", "remote",
            [],
            [
                {"name": "b", "skills": ["z", "a"]},
                {"name": "a", "skills": ["m"]},
            ],
        )
        self.assertEqual(rows, [
            ("m", "a", "remote"),
            ("a", "b", "remote"),
            ("z", "b", "remote"),
        ])

    def test_idempotent(self):
        """Two calls with identical inputs produce byte-identical row order."""
        args = (
            "local", "remote",
            [{"name": "p", "skills": ["c", "a", "b"]}],
            [{"name": "q", "skills": ["y", "x"]}],
        )
        self.assertEqual(self._sorted_rows(*args), self._sorted_rows(*args))

    def test_no_rows_when_both_empty(self):
        rows = self._sorted_rows("local", "remote", [], [])
        self.assertEqual(rows, [])


# ── 2. Table rendering / alignment ───────────────────────────────────────────

class TestRenderTable(unittest.TestCase):

    def test_header_columns_present(self):
        first = gim.render_table([("s", "p", "r")]).splitlines()[0]
        self.assertIn("Skill", first)
        self.assertIn("Plugin", first)
        self.assertIn("Repo", first)

    def test_separator_row_present(self):
        sep = gim.render_table([("s", "p", "r")]).splitlines()[1]
        self.assertIn("-", sep)

    def test_all_lines_same_length(self):
        rows = [
            ("short", "plug", "repo"),
            ("a-very-long-skill-name", "plug", "repo"),
        ]
        lengths = [len(l) for l in gim.render_table(rows).splitlines()]
        self.assertEqual(len(set(lengths)), 1, f"misaligned lines: {lengths}")

    def test_every_line_pipe_delimited(self):
        for line in gim.render_table([("s", "p", "r")]).splitlines():
            self.assertTrue(line.startswith("|"), repr(line))
            self.assertTrue(line.endswith("|"), repr(line))

    def test_line_count_header_sep_data(self):
        rows = [("s1", "p", "r"), ("s2", "p", "r")]
        lines = gim.render_table(rows).splitlines()
        self.assertEqual(len(lines), 4)  # header + separator + 2 data rows

    def test_wide_cell_pads_all_rows(self):
        """A long value in column 0 must widen that column for every line."""
        rows = [
            ("x" * 30, "p", "r"),
            ("short", "p", "r"),
        ]
        lines = gim.render_table(rows).splitlines()
        for line in lines:
            self.assertGreaterEqual(len(line), 30 + 4)  # 30 chars + pipes + spaces


# ── 3. die() abort paths ─────────────────────────────────────────────────────

class TestDiePaths(unittest.TestCase):

    def setUp(self):
        self._orig_gh_api = gim.gh_api
        self._orig_local = gim.LOCAL_MARKETPLACE
        self._orig_skill = gim.SKILL_MD

    def tearDown(self):
        gim.gh_api = self._orig_gh_api
        gim.LOCAL_MARKETPLACE = self._orig_local
        gim.SKILL_MD = self._orig_skill

    # -- missing SKILL.md markers -----------------------------------------------

    def test_missing_both_markers_aborts(self):
        with _Tmp() as tmp:
            mkt = os.path.join(tmp, "mkt.json")
            with open(mkt, "w") as f:
                json.dump(_mkt("local", []), f)
            skill_md = os.path.join(tmp, "SKILL.md")
            _write_skill_md(skill_md, with_markers=False)

            gim.LOCAL_MARKETPLACE = mkt
            gim.SKILL_MD = skill_md
            gim.gh_api = _gh_stub(_mkt("remote", []))

            with self.assertRaises(SystemExit):
                gim.main()

    def test_missing_start_marker_aborts(self):
        with _Tmp() as tmp:
            mkt = os.path.join(tmp, "mkt.json")
            with open(mkt, "w") as f:
                json.dump(_mkt("local", []), f)
            skill_md = os.path.join(tmp, "SKILL.md")
            with open(skill_md, "w") as f:
                f.write(f"# Only end\n{gim.END}\n")  # END present, START missing

            gim.LOCAL_MARKETPLACE = mkt
            gim.SKILL_MD = skill_md
            gim.gh_api = _gh_stub(_mkt("remote", []))

            with self.assertRaises(SystemExit):
                gim.main()

    # -- invalid JSON -----------------------------------------------------------

    def test_invalid_local_json_aborts(self):
        with _Tmp() as tmp:
            mkt = os.path.join(tmp, "mkt.json")
            with open(mkt, "w") as f:
                f.write("NOT VALID JSON {{{")
            gim.LOCAL_MARKETPLACE = mkt
            gim.gh_api = _gh_stub(_mkt("remote", []))

            with self.assertRaises(SystemExit):
                gim.main()

    def test_invalid_remote_json_aborts(self):
        """gh_api returning unparseable text for the remote file triggers die()."""
        with _Tmp() as tmp:
            mkt = os.path.join(tmp, "mkt.json")
            with open(mkt, "w") as f:
                json.dump(_mkt("local", []), f)
            gim.LOCAL_MARKETPLACE = mkt
            gim.gh_api = lambda path: "!!!NOT JSON!!!"  # gh_api_json will die()

            with self.assertRaises(SystemExit):
                gim.main()

    # -- non-list skill listing -------------------------------------------------

    def test_non_list_skill_listing_aborts(self):
        """remote_skill_dirs() receiving a non-list from the API must die()."""
        gim.gh_api = lambda path: json.dumps({"type": "file", "name": "oops"})
        with self.assertRaises(SystemExit):
            gim.remote_skill_dirs("any-plugin")

    # -- collect(): bad marketplace shapes -------------------------------------

    def test_plugins_not_list_aborts(self):
        with self.assertRaises(SystemExit):
            gim.collect({"name": "bad", "plugins": "not-a-list"}, "bad", _no_dirs)

    def test_plugin_entry_missing_name_and_id_aborts(self):
        with self.assertRaises(SystemExit):
            gim.collect({"name": "bad", "plugins": [{"version": "0.1.0"}]}, "bad", _no_dirs)


# ── 4. collect() correctness ──────────────────────────────────────────────────

class TestCollect(unittest.TestCase):

    def test_union_of_marketplace_and_dirs(self):
        """Skills from the plugin entry + skill_dirs_fn are merged (no duplicates lost)."""
        mkt = _mkt("repo", [{"name": "plug", "skills": ["plug/skills/a"]}])
        rows = gim.collect(mkt, "repo", lambda _: ["b"])
        skills = {r[0] for r in rows}
        self.assertIn("a", skills)
        self.assertIn("b", skills)

    def test_empty_plugins_returns_no_rows(self):
        self.assertEqual(gim.collect(_mkt("repo", []), "repo", _no_dirs), [])

    def test_row_tuple_is_skill_plugin_repo(self):
        mkt = _mkt("repo", [{"name": "myplugin", "skills": ["myplugin/skills/myskill"]}])
        rows = gim.collect(mkt, "repo", _no_dirs)
        self.assertEqual(len(rows), 1)
        skill, plugin, repo = rows[0]
        self.assertEqual((skill, plugin, repo), ("myskill", "myplugin", "repo"))


# ── entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    unittest.main(verbosity=2)
