#!/usr/bin/env python3
"""Offline tests for jobsearch-vault's backfill_entretien_links.py (#119).

Builds a throwaway vault and checks that the backfill:
- writes a chronological `## Entretiens` section (prep before CR on the same day),
- follows `opportunite_secondaire` as well as `opportunite`,
- is a no-op on re-run and skips a line a skill already wrote,
- leaves a dry run's vault untouched and reports unresolved links.

Run: python3 tests/test_backfill_entretien_links.py
"""

import contextlib
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent / (
    "plugins/jobsearch/skills/jobsearch-vault/scripts"
)
sys.path.insert(0, str(_SCRIPTS))

import backfill_entretien_links as bel  # noqa: E402

OPP = "CRM-JobSearch/Opportunites"
ENT = "CRM-JobSearch/Entretiens"


def note(fields: dict, body: str = "## Notes clés\n\n- x\n") -> str:
    fm = "\n".join(f"{k}: {v}" for k, v in fields.items())
    return f"---\n{fm}\n---\n{body}"


class BackfillTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.vault = Path(self._tmp.name)
        (self.vault / OPP).mkdir(parents=True)
        (self.vault / ENT).mkdir(parents=True)
        os.environ["OBSIDIAN_VAULT_PATH"] = str(self.vault)

        self.write(OPP, "Solutions Engineer — Dust", note({"type": '"opportunite-js"'},
                                                         "## Annonce\n\nTexte.\n"))
        self.write(OPP, "Responsable Commercial - ASN", note({"type": '"opportunite-js"'}))
        self.write(ENT, "CR Dust — Frank Aloia — 09-07-2026", note({
            "categorie": '"Compte-rendu"', "date": '"2026-07-09"',
            "opportunite": '"[[Solutions Engineer — Dust]]"'}))
        self.write(ENT, "Prep Dust — Frank Aloia — 09-07-2026", note({
            "categorie": '"Préparation"', "date": '"2026-07-09"',
            "opportunite": '"[[Solutions Engineer — Dust]]"'}))
        self.write(ENT, "Prep Dust — Ru — 04-06-2026", note({
            "categorie": '"Préparation"',
            "opportunite": '"[[Solutions Engineer — Dust]]"',
            "opportunite_secondaire": '"[[Responsable Commercial - ASN]]"'}))
        self.write(ENT, "Glossaire — Dust", note({
            "opportunite": '"[[Solutions Engineer — Dust|Dust]]"'}))
        self.write(ENT, "CR Ghost — X — 01-01-2026", note({
            "categorie": '"Compte-rendu"', "date": '"2026-01-01"',
            "opportunite": '"[[Nowhere — Ghost]]"'}))

    def tearDown(self):
        self._tmp.cleanup()
        os.environ.pop("OBSIDIAN_VAULT_PATH", None)

    def write(self, folder, name, content):
        (self.vault / folder / f"{name}.md").write_text(content, encoding="utf-8")

    def read(self, folder, name):
        return (self.vault / folder / f"{name}.md").read_text(encoding="utf-8")

    def run_script(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        sys.argv = ["backfill_entretien_links.py", *argv]
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            bel.main()
        return out.getvalue(), err.getvalue()

    def test_apply_writes_chronological_section(self):
        self.run_script("--apply")
        dust = self.read(OPP, "Solutions Engineer — Dust")
        self.assertTrue(dust.startswith('---\ntype: "opportunite-js"\n---\n## Annonce'))
        self.assertIn(
            "## Entretiens\n\n"
            "- 2026-06-04 — Prep — [[Prep Dust — Ru — 04-06-2026]]\n"
            "- 2026-07-09 — Prep — [[Prep Dust — Frank Aloia — 09-07-2026]]\n"
            "- 2026-07-09 — CR — [[CR Dust — Frank Aloia — 09-07-2026]]\n"
            "- sans date — Note — [[Glossaire — Dust]]\n",
            dust,
        )

    def test_secondary_opportunite_is_linked(self):
        self.run_script("--apply")
        asn = self.read(OPP, "Responsable Commercial - ASN")
        self.assertIn("## Entretiens\n\n- 2026-06-04 — Prep — [[Prep Dust — Ru — 04-06-2026]]\n",
                      asn)

    def test_rerun_is_noop_and_respects_skill_written_lines(self):
        # A line interview-prep already wrote must not be duplicated.
        path = self.vault / OPP / "Solutions Engineer — Dust.md"
        path.write_text(path.read_text(encoding="utf-8") + "\n## Entretiens\n\n"
                        "- 2026-07-09 — Prep — [[Prep Dust — Frank Aloia — 09-07-2026]]\n",
                        encoding="utf-8")
        self.run_script("--apply")
        once = self.read(OPP, "Solutions Engineer — Dust")
        self.assertEqual(once.count("[[Prep Dust — Frank Aloia — 09-07-2026]]"), 1)

        out, err = self.run_script("--apply")
        self.assertEqual(self.read(OPP, "Solutions Engineer — Dust"), once)
        self.assertEqual(out, "")
        self.assertIn("nothing to backfill", err)

    def test_dry_run_writes_nothing_and_reports_unresolved(self):
        before = self.read(OPP, "Solutions Engineer — Dust")
        out, err = self.run_script()
        self.assertEqual(self.read(OPP, "Solutions Engineer — Dust"), before)
        self.assertIn("- 2026-07-09 — CR — [[CR Dust — Frank Aloia — 09-07-2026]]", out)
        self.assertIn("unresolved", err)
        self.assertIn("[[Nowhere — Ghost]]", err)
        self.assertIn("dry run: 5 line(s) on 2 note(s)", err)

    def test_hand_written_link_is_not_duplicated(self):
        # 2501.ai case: the section already links the CR in its own words.
        path = self.vault / OPP / "Solutions Engineer — Dust.md"
        path.write_text(path.read_text(encoding="utf-8") + "\n## Entretiens\n\n"
                        "- 09/07 — debrief, feeling 🔥 → [[CR Dust — Frank Aloia — 09-07-2026]]\n",
                        encoding="utf-8")
        self.run_script("--apply")
        dust = self.read(OPP, "Solutions Engineer — Dust")
        self.assertEqual(dust.count("[[CR Dust — Frank Aloia — 09-07-2026]]"), 1)
        self.assertIn("- 2026-07-09 — Prep — [[Prep Dust — Frank Aloia — 09-07-2026]]", dust)

    def test_prefix_of_a_longer_name_is_not_taken_as_linked(self):
        body = "## Entretiens\n\n- [[Prep Dust — Frank Aloia — 09-07-2026 (EN)]]\n"
        self.assertFalse(bel.linked_in_section(body, "[[Prep Dust — Frank Aloia — 09-07-2026]]"))
        self.assertTrue(bel.linked_in_section(body.replace(" (EN)", "|EN"),
                                              "[[Prep Dust — Frank Aloia — 09-07-2026]]"))

    def test_bullet_after_prose_or_rule_gets_a_blank_line(self):
        # Cognyx case: a hand-written section ending on a `---` rule.
        body = "## Entretiens\n\nÉtat au 22/09.\n\n---\n\n## Annonce\n"
        out = bel.ObsidianAPI._upsert_section_body(body, "Entretiens", "- a", None)
        self.assertIn("---\n\n- a\n\n## Annonce", out)
        out = bel.ObsidianAPI._upsert_section_body(out, "Entretiens", "- b", None)
        self.assertIn("\n- a\n- b\n", out)

    def test_date_falls_back_to_filename_then_undated(self):
        self.assertEqual(bel.entretien_date({}, "Prep X — Y — 04-06-2026"), "2026-06-04")
        self.assertEqual(bel.entretien_date({"date": "2026-02-17T10:00:00.000+01:00"}, "n"),
                         "2026-02-17")
        self.assertEqual(bel.entretien_date({}, "Glossaire — X"), bel.UNDATED)


if __name__ == "__main__":
    unittest.main(verbosity=2)
