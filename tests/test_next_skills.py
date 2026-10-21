"""Text tests of the skills rewritten on `next` for the target hal contract (hal roadmap step 3).

Prose skills have no unit test; these guards catch the drifts that break a run without an error:
a hal tool that the target `hal-mcp` does not register, a workspace chosen by slug or default instead
of by `type`, the `log-cr` → `gtm:call` handoff drifting from what `gtm:call` reads, or a truncated
read that is acted on as if it were whole.

Run: python3 tests/test_next_skills.py
"""
import pathlib
import re
import unittest

REPO = pathlib.Path(__file__).resolve().parent.parent
PREFIX = "mcp__plugin_hal_hal-mcp__"

# The 29 tools of the target hal-mcp (hal `supabase/functions/hal-mcp/index.ts`, read 2026-10-10).
# Same list as bluegreen-marketplace `tests/skilltext.py`; when hal adds, renames or removes a tool,
# both change with the skills.
HAL_TOOLS = frozenset("""
list_projects create_project update_project_stage update_project
create_company list_companies update_company
create_contact list_contacts update_contact
log_interaction list_interactions update_interaction
create_sprint list_sprints update_sprint transition_sprint assign_task_to_sprint
create_task list_tasks update_task_status update_task
save_document list_documents get_document get_document_link
kb_index kb_search whoami
""".split())

# The keys gtm:call reads from log-cr (bluegreen-marketplace plugins/gtm/skills/call/SKILL.md § 0).
GTM_CALL_KEYS = ("caller", "company", "contacts", "date", "granola_id", "format", "heure", "feeling",
                 "type_entretien", "opportunite")

LOG_CR = REPO / "plugins/jobsearch/skills/log-cr/SKILL.md"
BRIEFING = REPO / "plugins/briefing/skills/morning-briefing/SKILL.md"
APPLY = REPO / "plugins/jobsearch/skills/apply-to-offer/SKILL.md"
OFFER = REPO / "plugins/jobsearch/skills/offer-to-cv/SKILL.md"  # replaced the cv-log-worker agent, renaud#176
JUDGE = REPO / "plugins/briefing/agents/cv-judge.md"
LOG_APP = REPO / "plugins/jobsearch/skills/log-application/SKILL.md"
PREP = REPO / "plugins/jobsearch/skills/interview-prep/SKILL.md"
SKILLS = sorted((REPO / "plugins").glob("*/skills/*/SKILL.md")) + sorted((REPO / "plugins").glob("*/agents/*.md"))
REAL_SLUGS = ("renaud-newjob", "rosaslaborbe")
# A workspace slug passed as a literal (`workspace_slug="blue-green"`) rather than a placeholder.
LITERAL_SLUG_ARG = re.compile(r'workspace_slug\s*[=:]\s*"[a-z]')


def read(path):
    return path.read_text(encoding="utf-8")


def flat(text):
    return " ".join(text.split())


def hal_tools(text):
    return set(re.findall(PREFIX + r"([a-z_]+)", text))


class TestHalToolsExist(unittest.TestCase):
    def test_every_hal_tool_a_skill_allows_is_registered(self):
        for path in SKILLS:
            with self.subTest(skill=str(path.relative_to(REPO))):
                self.assertLessEqual(hal_tools(read(path)), HAL_TOOLS)

    def test_no_real_workspace_slug_in_a_skill(self):
        # Workspaces come from whoami, by type; a slug written here is one user's and goes stale.
        for path in SKILLS:
            text = read(path)
            with self.subTest(skill=str(path.relative_to(REPO))):
                self.assertEqual([s for s in REAL_SLUGS if s in text], [])
                self.assertEqual(LITERAL_SLUG_ARG.findall(text), [])


class TestLogCr(unittest.TestCase):
    def setUp(self):
        self.text = read(LOG_CR)

    def test_a_rerun_still_delegates_to_gtm_call(self):
        # hal S01 l2-relance, runs 20261013-104247 and 20261013-105520: the replay skipped gtm:call
        # (« le relancer dupliquerait l'interaction »), so « inchangé » was never checked.
        self.assertIn("**on a re-run too**", read(LOG_CR))

    def test_delegates_to_gtm_call_with_every_key_it_reads(self):
        self.assertIn("Skill(gtm:call)", self.text)
        block = re.search(r'```json\n(\{\n  "caller": "log-cr".*?\})\n```', self.text, re.S)
        self.assertIsNotNone(block)
        for key in GTM_CALL_KEYS:
            self.assertIn(f'"{key}"', block.group(1), key)

    def test_workspace_is_chosen_by_type_never_by_default(self):
        self.assertIn('type: "jobsearch"', self.text)
        self.assertIn("Never `default_workspace_slug`", self.text)
        self.assertIn("archived", self.text)

    def test_the_tag_is_checked_against_the_vocabulary_before_any_write(self):
        self.assertIn("`jobsearch` must be in `WS`'s `allowed_tags`", self.text)

    def test_a_truncated_task_read_is_read_again_not_acted_on(self):
        body = flat(self.text)
        self.assertIn("limit=<total>", body)
        self.assertNotIn("create anyway", body)
        self.assertNotIn("skip silently", body)

    def test_vault_scripts_run_through_jobsearch_vault(self):
        # log-cr has no Bash in allowed-tools: python3 runs inside the jobsearch-vault skill.
        self.assertNotIn("Bash", re.search(r"^allowed-tools: (.*)$", self.text, re.M).group(1))
        self.assertIn("ask `jobsearch-vault` to run `upsert_section.py`", flat(self.text))


class TestMorningBriefing(unittest.TestCase):
    def setUp(self):
        self.text = read(BRIEFING)

    def test_scope_comes_from_whoami(self):
        for needle in ('archived: false', 'type: "personal"', 'type: "jobsearch"', "Never assert an email or a slug"):
            self.assertIn(needle, self.text)

    def test_fixed_blocks_come_from_hal_not_from_the_skill(self):
        self.assertIn("## Blocs fixes", self.text)
        self.assertIn("Fixed blocks come from hal, never from this file", self.text)

    def test_truncated_reads_are_read_whole(self):
        self.assertEqual(flat(self.text).count("limit=<total>"), 2)

    def test_opportunities_read_only_where_the_kind_is_enabled(self):
        self.assertIn("`opportunity` is in the workspace's `kinds_enabled`", flat(self.text))

    def test_daily_log_appends_never_overwrites(self):
        self.assertIn("Never overwrite a log written earlier today", self.text)
        self.assertIn('slug="daily-log-<YYYY-MM-DD>"', self.text)

    def test_the_only_writes_are_logs_and_description_appends(self):
        self.assertEqual(hal_tools(self.text) - {"whoami", "list_sprints", "list_tasks", "list_projects",
                                                 "list_documents", "get_document"},
                         {"save_document", "update_task"})

    # --- renaud#175 lot 3: the job-search half of Step 2c is a deterministic pipeline -------------

    def step_2c(self):
        start = self.text.index("### 2c — Job search")
        return self.text[start:self.text.index("### 2d — ", start)]

    def test_the_mail_window_is_since_the_last_daily_log_not_one_day(self):
        # 2026-10-21: the run was at 06:19 UTC, the six-offer digest came at 07:40 UTC, and
        # `newer_than:1d` never covered it. The window now starts at the last log's created_at.
        step = self.step_2c()
        # No search query of 2c carries the one-day window any more (the prose that explains why
        # it went may still name it).
        self.assertIsNone(re.search(r"linkedin\.com[^`]*newer_than:1d", step))
        self.assertIsNone(re.search(r"\(recruteur[^`]*newer_than:2d", step))
        self.assertIn('kind="daily-log"', step)
        self.assertIn("`created_at`", step)
        self.assertIn("after:<SINCE>", step)
        self.assertIn("now − 3 days", step)
        self.assertIn("list_documents", allowed := re.search(r'allowed-tools: "([^"]+)"', self.text).group(1))
        self.assertIn("mcp__plugin_hal_hal-mcp__list_documents", allowed)

    def test_every_job_id_of_a_digest_body_is_extracted(self):
        step = self.step_2c()
        self.assertIn("`jobs/view/(\\d+)` on the body", step)
        # The regex the skill names, run on a digest body shaped like LinkedIn's: the subject names
        # one offer, the body carries six, each id twice (card link + footer list).
        regex = re.search(r"regex `(jobs/view/\(\\d\+\))`", step).group(1)
        body = (
            "Forward Deployed Engineer\r\nMLabs\r\nParis\r\nView job: https://www.linkedin.com/comm/jobs/view/4481566043/?trackingId=a\r\n"
            "Forward Deployed Engineer\r\nNeev\r\nParis\r\nView job: https://www.linkedin.com/comm/jobs/view/4481552682/?trackingId=b\r\n"
            "Forward Deployed Engineer\r\nmonday.com\r\nParis\r\nView job: https://www.linkedin.com/comm/jobs/view/4464377709/?trackingId=c\r\n"
            "Forward Deployed Engineer\r\nFDE Times\r\nParis\r\nView job: https://www.linkedin.com/comm/jobs/view/4478929145/?trackingId=d\r\n"
            "Founding Forward Deployed Engineer - French Speaking\r\nHappyRobot\r\nParis\r\nView job: https://www.linkedin.com/comm/jobs/view/4478939792/?trackingId=e\r\n"
            "Applied AI Engineer, Digital Natives\r\nOpenAI\r\nParis\r\nView job: https://www.linkedin.com/comm/jobs/view/4480470021/?trackingId=f\r\n"
            "See all jobs: https://www.linkedin.com/comm/jobs/search-results/?originToLandingJobPostings=4481566043,4481552682,4464377709,4478929145,4478939792,4480470021\r\n"
        )
        ids = list(dict.fromkeys(re.findall(regex, body)))
        self.assertEqual(ids, ["4481566043", "4481552682", "4464377709", "4478929145", "4478939792", "4480470021"])

    def test_dedup_runs_on_the_job_id_before_any_enrichment(self):
        step = self.step_2c()
        self.assertIn("Dedup on the job id, before any enrichment", step)
        self.assertIn("`Offres vues ce run :`", step)
        self.assertIn("A **company** match without an id match is\nnot a dedup", step)
        # The log carries the ids the next run must not enrich again.
        self.assertIn("Offres vues ce run : <id> <id> <id> …", self.text)

    def test_every_target_offer_is_enriched_in_headless_too(self):
        step = self.step_2c()
        self.assertIn("in both modes", step)
        self.assertIn("**Safety bound: 20 invocations per run.**", step)
        self.assertNotIn("8 invocations per run at most", step)
        self.assertIn("**Score on the full JD.**", step)
        self.assertIn("**4. CV fan-out** — in both modes.", step)
        self.assertNotIn("skipped in `--headless`", step)
        # The headless table lists differences only; the fan-out is no longer one of them.
        modes = self.text[self.text.index("## Modes"):self.text.index("## Step 0")]
        self.assertNotIn("CV fan-out (Step 2c.4)", modes)
        self.assertNotIn("skipped (headless mode)", self.text)


class TestApplyToOffer(unittest.TestCase):
    """hal S06 run 20261012-065156: a pasted offer with no link, asked « passe les filtres ? »,
    never reached the gates — the skill only knew URLs, and answered from the seed instead."""

    def test_pasted_text_is_a_source(self):
        self.assertIn("**Offer text pasted, no link**", read(APPLY))

    def test_a_stored_summary_is_refused_as_a_jd(self):
        self.assertIn("500", flat(read(APPLY)).split("**An offer stored in hal**")[1].split("**Nothing resolvable**")[0])

    def test_the_filters_question_runs_the_skill_in_gates_only(self):
        text, offer = read(APPLY), read(OFFER)
        self.assertIn("MODE: gates-only", text)
        self.assertIn("## Step A.7 — Stop here in `MODE: gates-only`", offer)

    def test_a_follow_up_never_resumes_the_judge(self):
        self.assertIn("Never\n`SendMessage` the judge", read(APPLY))

    def test_the_form_field_runs_alone_on_the_rows(self):
        self.assertIn("Asked on its own, it runs alone", read(APPLY))

    def test_the_comp_rejection_names_the_floor(self):
        self.assertRegex(read(OFFER), r"ÉCARTÉ \| .*< plancher <comp_floor_eur>€")


class TestJudgeTour2(unittest.TestCase):
    """hal S06 s4-juge: a worker that resumed the judge by SendMessage returned before Tour 2."""

    def test_tour_2_is_a_foreground_spawn(self):
        offer = read(OFFER)
        self.assertIn("TOUR: 2", offer)
        self.assertNotIn("SendMessage", offer.split("---")[1])
        self.assertIn("TOUR_1_VERDICT", read(JUDGE))


class TestLogApplication(unittest.TestCase):
    """hal S06 s5-log: « envoyée » by default, `other` for an unknown source, a contactless relance."""

    def test_a_relance_needs_a_named_contact(self):
        text = read(LOG_APP)
        self.assertIn("## Step 3c — Find the named contact (q14)", text)
        self.assertIn("project_id     = PROJECT_ID", text)

    def test_sent_only_when_renaud_says_so(self):
        self.assertNotIn("default: ✉️", read(LOG_APP))

    def test_other_is_not_unknown(self):
        self.assertIn("never `other` as a stand-in", read(LOG_APP))


class TestInterviewPrep(unittest.TestCase):
    """hal S01 s9-prep-dg: a « valide » with no date became tomorrow's date in three places."""

    def test_the_interview_date_is_never_assumed(self):
        text = read(PREP)
        self.assertNotIn("default: tomorrow", text)
        self.assertIn("a « valide » or « continue » without a date is not a date", text)


class TestTaskLinks(unittest.TestCase):
    """hal S01 l1: the relance and the « note 100 jours » carried no project, no sprint (3 runs / 3).
    Renaud 2026-10-13: every job-search task carries its opportunity and the sprint its due date
    falls in — current or next, so a Friday debrief's relance lands in next week's sprint."""

    def test_every_task_writer_links_project_and_sprint_of_the_due_date(self):
        for path in (LOG_CR, PREP, LOG_APP):
            text = read(path)
            with self.subTest(skill=path.parent.name):
                self.assertIn(PREFIX + "list_sprints", text)
                self.assertIn(PREFIX + "list_projects", text)
                self.assertIn("contains its `due_date`", text.replace("the task's `due_date`", "its `due_date`"))
                self.assertIn("PROJECT_ID", text)
                self.assertNotIn("No `sprint_id`", text)
                self.assertNotIn("sprint-less", text)

    def test_log_cr_turns_renaud_next_steps_into_tasks(self):
        text = read(LOG_CR)
        self.assertIn("**The next steps.**", text)
        self.assertIn("Only\nRenaud's own actions", text)


if __name__ == "__main__":
    unittest.main()
