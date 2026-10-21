"""Text guards for the offer → CV path after renaud#176 (lot 2).

What they pin, and the real failure each one comes from:

- the `cv-log-worker` agent is gone and both callers run the `offer-to-cv` skill inline — a
  sub-agent launched in the background had no Agent tool, skipped the judge, and the CV was
  logged « ⚠️ CV non jugé » (HappyRobot, 2026-10-21);
- the skill never logs a CV without a judge score, and Tour 2 is a foreground spawn;
- the judge reads `parcours` and nothing else, never under-sells, routes interview prep to
  « Notes d'entretien » and never proposes « Full P&L » — it had recommended removing Node, OAuth
  and « full-stack » on the strength of a one-month-old retex;
- the P4 EN cells of `cv-master.json` carry the About, the competency blocks and the bullets
  Renaud validated (#176 §4–§6), so the first render is already the sendable structure.

Run: python3 tests/test_offer_to_cv.py
"""
import json
import pathlib
import re
import unittest

REPO = pathlib.Path(__file__).resolve().parent.parent
PLUGINS = REPO / "plugins"
OFFER = PLUGINS / "jobsearch/skills/offer-to-cv/SKILL.md"
APPLY = PLUGINS / "jobsearch/skills/apply-to-offer/SKILL.md"
BRIEFING = PLUGINS / "briefing/skills/morning-briefing/SKILL.md"
JUDGE = PLUGINS / "briefing/agents/cv-judge.md"
WORKER = PLUGINS / "briefing/agents/cv-log-worker.md"
MASTER = PLUGINS / "jobsearch/data/cv-master.json"
README = REPO / "README.md"

VALIDATED_ABOUT = [
    "Forward Deployed Engineer who turns a client's operational problem into a shipped AI system — from the first discovery workshop to the day their team runs it without me.",
    "Built and run production AI agents end to end — RAG over regulatory corpora, ML price forecasting, an on-site field assistant — and the stack beneath them: MCP servers, OAuth, skills and agent harnesses, FastAPI, Supabase / pgvector, React / Next.js.",
    "Co-founder & CTO of a marine data intelligence platform through its acquisition by an international engineering group, then four years signing and renewing its enterprise subscriptions (SBM Offshore, Nexans, ASN).",
]
VALIDATED_BLOCKS = ["Agent Platform & Stack", "AI Agents & LLM Systems", "Client Delivery & Industry"]


def read(path):
    return path.read_text(encoding="utf-8")


def allowed_tools(text):
    return re.search(r"^allowed-tools: \"(.*)\"$", text, re.M).group(1)


class TestWorkerIsGone(unittest.TestCase):
    def test_the_agent_file_no_longer_exists(self):
        self.assertFalse(WORKER.exists(), "cv-log-worker.md must be deleted, not kept as a compat path")

    def test_nothing_spawns_the_worker_any_more(self):
        for path in sorted(PLUGINS.rglob("*.md")) + [README]:
            with self.subTest(file=str(path.relative_to(REPO))):
                self.assertNotIn("Agent(cv-log-worker)", read(path))

    def test_readme_names_the_skill_not_the_agent(self):
        text = read(README)
        self.assertIn("offer-to-cv/SKILL.md", text)
        self.assertNotIn("cv-log-worker", text)


class TestCallersRunTheSkillInline(unittest.TestCase):
    def test_apply_to_offer_invokes_the_skill(self):
        text = read(APPLY)
        self.assertIn("Skill(offer-to-cv)", allowed_tools(text))
        self.assertIn("Invoke `Skill(offer-to-cv)` **inline**", text)
        self.assertNotIn("run_in_background", text)

    def test_morning_briefing_invokes_the_skill_one_offer_at_a_time(self):
        text = read(BRIEFING)
        self.assertIn("Skill(offer-to-cv)", allowed_tools(text))
        self.assertIn("one offer after the\nother", text)
        self.assertNotIn("Agent(cv-log-worker", text)

    def test_headless_still_skips_the_fan_out(self):
        # Out of scope for #176: a scheduled run has no vault; the brief says so.
        self.assertIn("CV pre-generation: skipped (headless mode)", read(BRIEFING))


class TestOfferToCv(unittest.TestCase):
    def setUp(self):
        self.text = read(OFFER)
        self.tools = allowed_tools(self.text)

    def test_it_spawns_the_judge_and_composes_the_existing_skills(self):
        for tool in ("Agent(cv-judge)", "Skill(cv-generator)", "Skill(log-application)", "Skill(read-job-offer)"):
            self.assertIn(tool, self.tools)

    def test_gates_only_mode_is_kept(self):
        self.assertIn("## Step A.7 — Stop here in `MODE: gates-only`", self.text)
        self.assertRegex(self.text, re.compile(r"^PASSE \| ", re.M))

    def test_both_tours_run_in_the_foreground(self):
        self.assertEqual(self.text.count("Agent(cv-judge, run_in_background: false"), 2)
        self.assertIn("TOUR: 2", self.text)
        self.assertIn("TOUR_1_VERDICT", self.text)
        self.assertIn("Never resume the Tour 1 judge with `SendMessage`", self.text)

    def test_no_cv_is_logged_unjudged(self):
        self.assertIn("**No CV is logged unjudged.**", self.text)
        self.assertIn("A CV is never logged without a judge score", self.text)
        # The old worker had a « CV non jugé » degradation that still logged the CV. Gone.
        self.assertNotIn("- `⚠️ CV non jugé", self.text)
        self.assertIn("CV:ok LOG:skip | juge\nindisponible", self.text)

    def test_an_under_selling_recommendation_is_declined(self):
        self.assertIn("**Never take a technology, a product or a result out of the CV because the judge calls it\nunproven.**", self.text)
        self.assertIn("⚠️ recommandation écartée", self.text)

    def test_a_replay_renders_in_scratch_and_logs_nothing(self):
        self.assertIn("`OUTPUT_DIR`", self.text)
        self.assertIn("Skipped when the caller passed an `OUTPUT_DIR`", self.text)
        self.assertIn("⚠️ non loggé : OUTPUT_DIR fourni", self.text)

    def test_overrides_replace_the_scratch_copy_of_the_master(self):
        self.assertIn("never\ncopy `cv-master.json` to a scratch folder", self.text)
        for flag in ("--bullet-overrides", "--container-items", "--containers-override"):
            self.assertIn(flag, self.text)


class TestJudge(unittest.TestCase):
    def setUp(self):
        self.text = read(JUDGE)

    def test_parcours_is_the_only_document(self):
        self.assertIn('slug="parcours"', self.text)
        for slug in ("retex-dust-2026-09", 'slug="memory"', 'slug="context"', "areas/job-search",
                     "topics/recent-work", "areas/blue-green", 'slug="profile"'):
            self.assertNotIn(slug, self.text, slug)
        self.assertIn("**`parcours` is the only document you read.**", self.text)

    def test_the_goal_is_the_interview_and_no_under_sell(self):
        self.assertIn("get Renaud the interview", self.text)
        self.assertIn("**Never under-sell.**", self.text)
        self.assertIn("A claim `parcours` supports stays", self.text)
        for tech in ("Node", "OAuth", "full-stack"):
            self.assertIn(tech, self.text)

    def test_interview_prep_leaves_the_cv(self):
        self.assertIn("**Notes d'entretien**", self.text)
        self.assertIn("never one of the five problems and never a rewrite", self.text)

    def test_full_pnl_is_forbidden(self):
        self.assertIn("**« Full P&L » is forbidden.**", self.text)

    def test_an_unreadable_parcours_stops_the_judge(self):
        self.assertIn("❌ parcours illisible — aucun jugement rendu", self.text)

    def test_the_judge_only_reads(self):
        self.assertEqual(allowed_tools(self.text),
                         "Read mcp__plugin_hal_hal-mcp__whoami mcp__plugin_hal_hal-mcp__get_document")


class TestP4Cells(unittest.TestCase):
    def setUp(self):
        self.text = read(MASTER)
        self.data = json.loads(self.text)
        self.p4 = self.data["matrix"]["p4"]
        self.bg = self.data["experiences"]["blue_green"]["bullets"]["p4"]
        self.artelia = self.data["experiences"]["artelia"]["bullets"]["p4"]["default"]["en"]

    def test_validated_about_on_every_p4_en_cell(self):
        for cell, content in self.p4.items():
            with self.subTest(cell=cell):
                self.assertEqual(content["about"]["en"], VALIDATED_ABOUT)

    def test_validated_blocks_on_every_p4_en_cell(self):
        for cell, content in self.p4.items():
            with self.subTest(cell=cell):
                self.assertEqual([c["title"] for c in content["containers"]["en"]], VALIDATED_BLOCKS)
                self.assertTrue(all(len(c["items"]) == 3 for c in content["containers"]["en"]))
                self.assertNotIn("row-level security", json.dumps(content["containers"]["en"]).lower())

    def test_hal_bullet_on_every_p4_en_bullet_set(self):
        for variant, bullets in self.bg.items():
            with self.subTest(variant=variant):
                self.assertTrue(any(b.startswith("Built hal, a TypeScript MCP server") for b in bullets["en"]), bullets["en"])

    def test_edifice_in_the_past_tense(self):
        for variant, bullets in self.bg.items():
            with self.subTest(variant=variant):
                edifice = [b for b in bullets["en"] if "field assistant" in b]
                self.assertEqual(len(edifice), 1, bullets["en"])
                self.assertTrue(edifice[0].startswith("Shipped a field assistant"))
                self.assertNotIn("used daily", edifice[0])

    def test_artelia_single_past_tense_bullet_without_committees(self):
        self.assertEqual(len(self.artelia), 1)
        self.assertTrue(self.artelia[0].startswith("Took over the enterprise sales pipeline"))
        self.assertNotIn("IT committees", self.artelia[0])

    def test_full_pnl_never_in_the_master(self):
        self.assertNotRegex(self.text, re.compile(r"full p&l", re.I))


if __name__ == "__main__":
    unittest.main()
