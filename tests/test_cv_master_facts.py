"""Fact guards on `plugins/jobsearch/data/cv-master.json`.

The source of truth is the hal document `parcours` (workspace `renaud`). These guards pin the
facts that have shipped wrong on real CVs, so they cannot come back through the data file:
a Bachelor degree Renaud does not hold, and Artelia dated 2019 – 2022 instead of 2019 – 2023.

Run: python3 tests/test_cv_master_facts.py
"""
import json
import pathlib
import re
import unittest

REPO = pathlib.Path(__file__).resolve().parent.parent
MASTER = REPO / "plugins" / "jobsearch" / "data" / "cv-master.json"
FORBIDDEN = re.compile(r"\bbachelor|coastal engineering|génie côtier|\bb\.?sc\b", re.IGNORECASE)


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

    def test_artelia_period(self):
        self.assertEqual(self.data["experiences"]["artelia"]["period"], "2019 – 2023")


if __name__ == "__main__":
    unittest.main()
