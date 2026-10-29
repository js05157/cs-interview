import copy
import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import cli, core, notion
from test_publisher import FakeNotion

PARENT = "40547f4c-2c25-8012-9548-c463380659f7"


class PreflightNotion(FakeNotion):
    def __init__(self):
        super().__init__()
        self.blocks = {PARENT: []}
        self.title = "CS 기술 면접 공부"
        self.archived = False
        self.auth_error = None
        self.create_error = None
        self.lose_create = False

    def request(self, method, path, payload=None):
        if path == "users/me":
            if self.auth_error:
                raise core.PublisherError(self.auth_error)
            return {"object": "user", "id": "integration-user", "type": "bot"}
        if path == "pages/" + PARENT:
            return {"id": PARENT, "archived": self.archived,
                    "properties": {"title": {"type": "title", "title": notion.rich(self.title)}}}
        return super().request(method, path, payload)

    def create_page(self, parent, title, children=None):
        if self.create_error:
            raise core.PublisherError(self.create_error)
        page = super().create_page(parent, title, children)
        if self.lose_create:
            self.lose_create = False
            raise notion.AmbiguousWrite("notion-write-uncertain")
        return page


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "README.md").write_text("# Notes\n", encoding="utf-8")
        self.state = dict(schema_version=1, topics={}, notion_hierarchy={}, notion_uncertain={})
        self.config = dict(categories={"Operating-System": "운영체제"}, blog_url="https://example.com/cs")
        self.topic = dict(topic_id="os-process-thread", category="Operating-System", subcategory="Process")
        self.policy = dict(allowed_topic_ids=["os-process-thread"], expected_notion_parent_page_id=PARENT,
                           expected_notion_parent_title="CS 기술 면접 공부")
        self.fake = PreflightNotion()

    def tearDown(self):
        self.temp.cleanup()

    def check(self, parent=PARENT):
        return notion.preflight(self.root, self.state, self.config, self.topic, self.policy, self.fake, parent)

    def test_creates_only_approved_hierarchy_before_public_documents(self):
        result = self.check()
        self.assertEqual(result["insert_permission"], "verified-by-created-page")
        self.assertEqual(self.fake.posts, 2)
        self.assertEqual(self.state["topics"], {})
        self.assertFalse((self.root / "Operating-System").exists())
        self.assertEqual(self.fake.blocks[PARENT][0]["child_page"]["title"], "운영체제")

    def test_existing_hierarchy_reused_without_duplicate_pages(self):
        self.check(); result = self.check()
        self.assertEqual(self.fake.posts, 2)
        self.assertEqual(result["hierarchy_pages_created"], 0)

    def test_authentication_failure_does_not_write(self):
        self.fake.auth_error = "notion-http-401"
        with self.assertRaisesRegex(core.PublisherError, "401"):
            self.check()
        self.assertEqual(self.fake.posts, 0)
        self.assertFalse((self.root / ".publisher/state.json").exists())

    def test_wrong_secret_parent_stops_before_writes(self):
        with self.assertRaisesRegex(core.PublisherError, "approved-page"):
            self.check("00000000-0000-0000-0000-000000000000")
        self.assertEqual(self.fake.posts, 0)

    def test_wrong_page_title_stops_before_writes(self):
        self.fake.title = "Different page"
        with self.assertRaisesRegex(core.PublisherError, "title"):
            self.check()
        self.assertEqual(self.fake.posts, 0)

    def test_archived_parent_stops_before_writes(self):
        self.fake.archived = True
        with self.assertRaisesRegex(core.PublisherError, "archived"):
            self.check()
        self.assertEqual(self.fake.posts, 0)

    def test_insert_permission_failure_keeps_publication_count_zero(self):
        self.fake.create_error = "notion-http-403"
        with self.assertRaisesRegex(core.PublisherError, "403"):
            self.check()
        self.assertEqual(self.state["topics"], {})
        self.assertFalse(self.state["notion_uncertain"])
        self.assertFalse((self.root / "blog/_posts").exists())

    def test_lost_hierarchy_create_response_is_reconciled(self):
        self.fake.lose_create = True
        with self.assertRaises(notion.AmbiguousWrite):
            self.check()
        self.check()
        self.assertEqual(self.fake.posts, 2)
        self.assertFalse(self.state["notion_uncertain"])

    def test_second_topic_blocked_even_on_another_day(self):
        with self.assertRaisesRegex(core.PublisherError, "not-approved"):
            cli.enforce_approval(self.state, dict(topic_id="os-context-switch"), self.policy)

    def test_first_topic_recovery_and_daily_limit_are_allowed(self):
        cli.enforce_approval(self.state, dict(topic_id="os-process-thread", action="recover"), self.policy)
        cli.enforce_approval(self.state, dict(topic_id=None, action="daily-limit"), self.policy)

    def test_existing_other_publications_fail_closed(self):
        state = copy.deepcopy(self.state); state["topics"]["unapproved"] = {}
        with self.assertRaisesRegex(core.PublisherError, "outside-approved"):
            cli.enforce_approval(state, dict(topic_id=None), self.policy)

    def test_fixed_queue_hash_approval_does_not_approve_future_topics(self):
        self.policy["allowed_topic_id_hashes"] = [core.digest("os-context-switch")]
        cli.enforce_approval(self.state, dict(topic_id="os-context-switch", action="new"), self.policy)
        with self.assertRaisesRegex(core.PublisherError, "not-approved"):
            cli.enforce_approval(self.state, dict(topic_id="future-topic", action="new"), self.policy)

    def test_hash_approved_publication_can_recover_and_reach_daily_limit(self):
        self.policy["allowed_topic_id_hashes"] = [core.digest("os-context-switch")]
        state = copy.deepcopy(self.state)
        state["topics"]["os-context-switch"] = {}
        cli.enforce_approval(state, dict(topic_id="os-context-switch", action="recover"), self.policy)
        cli.enforce_approval(state, dict(topic_id=None, action="daily-limit"), self.policy)
        state["topics"]["future-topic"] = {}
        with self.assertRaisesRegex(core.PublisherError, "outside-approved"):
            cli.enforce_approval(state, dict(topic_id=None), self.policy)

    def test_cli_auth_error_stops_before_public_source_materialization(self):
        core.write_json(self.root / "config/publication_policy.json", self.policy)
        core.write_json(self.root / "config/publisher.json", self.config)
        preview = dict(topic_id="os-process-thread", action="new")
        def preview_only(*args, **kwargs):
            self.assertTrue(kwargs.get("dry_run"), "public source must not be materialized after auth failure")
            return preview
        with patch.dict(os.environ, {"NOTION_API_KEY":"test", "NOTION_PARENT_PAGE_ID":PARENT,"CONTENT_REPO_TOKEN":"test"}), \
             patch.object(cli, "git", return_value=""), patch.object(cli,"commit") as commit, \
             patch.object(cli,"prepare",side_effect=preview_only), patch.object(cli,"load_state",return_value=self.state), \
             patch.object(cli,"load_catalog",return_value=({"os-process-thread":self.topic},[])), \
             patch.object(notion,"preflight",side_effect=core.PublisherError("notion-http-401")), \
             patch("sys.stderr",new_callable=io.StringIO):
            result = cli.main(["prepare","--root",str(self.root),"--private",str(self.root/"private"),"--mode","publish","--commit"])
        self.assertEqual(result,1)
        commit.assert_not_called()
        self.assertFalse((self.root/"Operating-System").exists())


if __name__ == "__main__":
    unittest.main()
