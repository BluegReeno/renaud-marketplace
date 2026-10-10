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
        self.assertEqual(hal_tools(self.text) - {"whoami", "list_sprints", "list_tasks", "list_projects", "get_document"},
                         {"save_document", "update_task"})


if __name__ == "__main__":
    unittest.main()
