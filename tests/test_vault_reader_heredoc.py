"""The device_bash reader embedded in `jobsearch-vault/SKILL.md` (Case A, issue #174).

The reader is sent whole inside a `device_bash` command, so it lives only in the SKILL.md. This
test extracts that heredoc, runs it against a throwaway vault, and checks it against the plugin's
own `list_notes.py` / `read_note.py` — the scripts Case B runs — so the two cannot drift.

Run: python3 tests/test_vault_reader_heredoc.py
"""
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest

REPO = pathlib.Path(__file__).resolve().parent.parent
SKILL = REPO / "plugins" / "jobsearch" / "skills" / "jobsearch-vault" / "SKILL.md"
SCRIPTS = SKILL.parent / "scripts"

NOTES = {
    "CRM-JobSearch/Opportunites/Forward Deployed Engineer — Cognyx.md": (
        '---\ntype: opportunite-js\nstatut: "✉️ Candidature envoyée"\nentreprise: "[[Cognyx]]"\n'
        'etiquettes: [jobsearch, "fde"]\nscore: 8.5\nremote: true\nvide:\n---\n'
        "## Annonce\n\nForward Deployed Engineer chez OSS Ventures.\n"
    ),
    "CRM-JobSearch/Opportunites/Solutions Engineer — Mistral.md": (
        "---\ntype: opportunite-js\nstatut: ❌ Refus\nentreprise: '[[Mistral]]'\netiquettes:\n"
        "  - jobsearch\n  - se\n---\nCorps.\n"
    ),
    "CRM-JobSearch/Entretiens/Prep OSS Ventures.md": (
        "---\ntype: entretien\ncategorie: Préparation\n---\nOSS Ventures, OSS Ventures.\n"
    ),
    "Taches/Relance OSS Ventures.md": "---\ntype: tache\n---\nOSS Ventures\n",
}


def reader_code():
    text = SKILL.read_text(encoding="utf-8")
    m = re.search(r"```bash\npython3 - list [^\n]*<<'PY'\n(.*?)\nPY\n```", text, re.S)
    assert m, "Case A heredoc not found in jobsearch-vault/SKILL.md"
    return m.group(1)


class VaultReader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code = reader_code()
        cls.tmp = tempfile.TemporaryDirectory()
        cls.vault = pathlib.Path(cls.tmp.name)
        for rel, body in NOTES.items():
            path = cls.vault / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body, encoding="utf-8")
        cls.env = {**os.environ, "OBSIDIAN_VAULT_PATH": str(cls.vault)}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def heredoc(self, *args):
        proc = subprocess.run([sys.executable, "-", *args], input=self.code, env=self.env,
                              capture_output=True, text=True, check=True)
        return json.loads(proc.stdout), proc.stderr

    def plugin(self, script, *args):
        proc = subprocess.run([sys.executable, str(SCRIPTS / script), *args], env=self.env,
                              capture_output=True, text=True, check=True)
        return json.loads(proc.stdout)

    def test_list_matches_list_notes(self):
        got, err = self.heredoc("list", "CRM-JobSearch/Opportunites", "500")
        want = self.plugin("list_notes.py", "CRM-JobSearch/Opportunites", "--limit", "500")
        self.assertEqual(got, want)
        self.assertIn("2 notes returned (of 2 in folder), 0 unreadable", err)

    def test_list_filter_on_list_field(self):
        got, _ = self.heredoc("list", "CRM-JobSearch/Opportunites", "500", "etiquettes", "fde")
        self.assertEqual([n["path"] for n in got],
                         ["CRM-JobSearch/Opportunites/Forward Deployed Engineer — Cognyx.md"])

    def test_read_matches_read_note(self):
        rel = "CRM-JobSearch/Opportunites/Forward Deployed Engineer — Cognyx.md"
        got, _ = self.heredoc("read", rel)
        want = self.plugin("read_note.py", rel)
        for key in ("frontmatter", "content"):
            self.assertEqual(got[key], want[key], key)

    def test_search_defaults_to_crm_jobsearch(self):
        got, _ = self.heredoc("search", "OSS Ventures")
        files = [r["filename"] for r in got]
        self.assertEqual(files[0], "CRM-JobSearch/Entretiens/Prep OSS Ventures.md")
        self.assertEqual(len(files), 2)
        self.assertFalse(any(f.startswith("Taches/") for f in files))

    def test_unreadable_file_is_counted_not_hidden(self):
        bad = self.vault / "CRM-JobSearch" / "Opportunites" / "Zz — Broken.md"
        bad.write_bytes(b"---\ntype: opportunite-js\n---\n\xff\xfe")
        try:
            got, err = self.heredoc("list", "CRM-JobSearch/Opportunites", "500")
        finally:
            bad.unlink()
        self.assertEqual(len(got), 2)
        self.assertIn("1 unreadable", err)
        self.assertIn("# UNREADABLE CRM-JobSearch/Opportunites/Zz — Broken.md", err)

    def test_vault_not_found(self):
        env = {k: v for k, v in self.env.items() if k != "OBSIDIAN_VAULT_PATH"}
        env["HOME"] = self.tmp.name
        proc = subprocess.run([sys.executable, "-", "list", "CRM-JobSearch/Opportunites"],
                              input=self.code, env=env, capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("VAULT_NOT_FOUND", proc.stderr)


if __name__ == "__main__":
    unittest.main()
