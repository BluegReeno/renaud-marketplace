"""Fact guards on `plugins/jobsearch/data/cv-master.json`.

The source of truth is the hal document `parcours` (workspace `renaud`). These guards pin the
facts that have shipped wrong on real CVs, so they cannot come back through the data file:
a Bachelor degree Renaud does not hold, Artelia dated 2019 – 2022 instead of 2019 – 2023,
Edifice described as live or used daily (stopped October 2026), and the Tender agent's
8.65/10 rounded to 8.6, which is the Strategy agent's score. It also keeps out figures no
recruiter cares about — a product version number, a chunk count: a BlueWind line carries the
client outcome (a tender question answered in under a minute instead of hours).

Run: python3 tests/test_cv_master_facts.py
"""
import json
import pathlib
import re
import unittest

REPO = pathlib.Path(__file__).resolve().parent.parent
MASTER = REPO / "plugins" / "jobsearch" / "data" / "cv-master.json"
FORBIDDEN = re.compile(r"\bbachelor|coastal engineering|génie côtier|\bb\.?sc\b", re.IGNORECASE)
STALE = re.compile(r"used daily|au quotidien|\b8[.,]6/10|\bv\d+(\.\d+)?\b|\d[\d ,.]*\s*chunks", re.IGNORECASE)


class CvMasterFacts(unittest.TestCase):
    def setUp(self):
        self.text = MASTER.read_text(encoding="utf-8")
        self.data = json.loads(self.text)

    def test_no_bachelor_anywhere(self):
        hit = FORBIDDEN.search(self.text)
        self.assertIsNone(hit, f"cv-master.json claims a degree Renaud does not hold: {hit and hit.group()!r}")

    def test_education_is_dea_then_maitrise(self):
        degrees = [e["degree"] for e in self.data["education"]]
        self.assertEqual(len(degrees), 2)
        self.assertTrue(degrees[0].startswith("DEA"), degrees[0])
        self.assertTrue(degrees[1].startswith("Maîtrise in Mechanics"), degrees[1])

    def test_no_stale_product_claims(self):
        hits = sorted({m.group() for m in STALE.finditer(self.text)})
        self.assertEqual(hits, [], f"cv-master.json carries stale product claims: {hits}")

    def test_edifice_never_live(self):
        for line in self.text.splitlines():
            if "Edifice" in line or "field assistant" in line:
                self.assertNotRegex(line.lower(), r"edifice[^.;]*\b(live|in production|en production|en prod)\b", line.strip())

    def test_artelia_period(self):
        self.assertEqual(self.data["experiences"]["artelia"]["period"], "2019 – 2023")


if __name__ == "__main__":
    unittest.main()
