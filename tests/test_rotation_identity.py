import copy
import json
import subprocess
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

from scripts import cli, core


def completed(key, day, **extra):
    return dict(topic_id=key, published_date=day, github_status="complete",
                notion_status="complete", blog_status="complete", **extra)


class RotationTests(unittest.TestCase):
    def setUp(self):
        self.queue = ["a1", "a2", "b1", "b2", "c1", "c2"]
        self.catalog = {key: dict(category=key[0].upper(), prerequisites=[key[0] + "1"] if key[1] == "2" else [])
                        for key in self.queue}
        self.state = {"topics": {}}

    def choose(self, today="2026-11-05"):
        return core.select_topic(self.catalog, self.queue, self.state, today, category_order=["A", "B", "C"])

    def test_round_robin_keeps_each_subject_order_and_exhausts_once(self):
        before = copy.deepcopy((self.catalog, self.queue))
        selected = []
        for i in range(6):
            day = (date(2026, 11, 5) + timedelta(days=i)).isoformat()
            action, key = self.choose(day)
            self.assertEqual(action, "new")
            selected.append(key)
            self.state["topics"][key] = completed(key, day)
        self.assertEqual(selected, ["a1", "b1", "c1", "a2", "b2", "c2"])
        self.assertEqual(self.choose("2026-12-01"), ("exhausted", None))
        self.assertEqual((self.catalog, self.queue), before)

    def test_recovery_precedes_rotation_even_on_the_same_date(self):
        self.state["topics"]["b1"] = completed("b1", "2026-11-05")
        self.state["topics"]["b1"]["notion_status"] = "failed"
        self.assertEqual(self.choose(), ("recover", "b1"))
        self.state["topics"]["b1"]["notion_status"] = "complete"
        self.assertEqual(self.choose("2026-11-06"), ("new", "c1"))

    def test_same_day_does_not_select_another_subject(self):
        self.state["topics"]["a1"] = completed("a1", "2026-11-05")
        self.assertEqual(self.choose(), ("daily-limit", None))

    def test_unmet_prerequisite_skips_subject_without_skipping_its_head(self):
        self.catalog["c1"]["prerequisites"] = ["b2"]
        self.state["topics"] = {"a1": completed("a1", "2026-11-03"), "b1": completed("b1", "2026-11-04")}
        self.assertEqual(self.choose(), ("new", "a2"))
        self.state["topics"]["a2"] = completed("a2", "2026-11-05")
        self.assertEqual(self.choose("2026-11-06"), ("new", "b2"))
        self.state["topics"]["b2"] = completed("b2", "2026-11-06")
        self.assertEqual(self.choose("2026-11-07"), ("new", "c1"))

    def test_exhausted_subjects_are_skipped(self):
        for i, key in enumerate(["a1", "a2", "b1", "b2"]):
            self.state["topics"][key] = completed(key, f"2026-10-{27+i}")
        self.assertEqual(self.choose(), ("new", "c1"))

    def test_withdrawn_prerequisite_does_not_satisfy_readiness(self):
        for i, key in enumerate(["a1", "a2", "b1", "b2"]):
            self.state["topics"][key] = completed(key, f"2026-10-{27+i}")
        self.state["topics"]["a1"]["publication_status"] = "withdrawn"
        self.catalog["c1"]["prerequisites"] = ["a1"]
        with self.assertRaisesRegex(core.PublisherError, "no-publishable-topic-prerequisites"):
            self.choose()

    def test_invalid_category_order_fails_closed(self):
        with self.assertRaisesRegex(core.PublisherError, "rotation-category-order-invalid"):
            core.select_topic(self.catalog, self.queue, self.state, "2026-11-05", category_order=["A", "B"])


class CommitIdentityTests(unittest.TestCase):
    def test_real_commit_uses_configured_author_and_committer_without_network(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            def local(*args):
                return subprocess.run(["git", "-C", str(root), *args], check=True,
                                      capture_output=True, text=True, encoding="utf-8").stdout.strip()
            local("init", "-b", "master")
            local("remote", "add", "origin", "https://github.com/example/test")
            core.write_json(root / "config/publisher.json", dict(branch="master", public_repository="example/test",
                blog_url="https://example.test", categories={}, commit_identity=dict(name="Test Owner", email="owner@example.test")))
            core.write_json(root / ".publisher/state.json", dict(schema_version=1, topics={}, notion_hierarchy={}, notion_uncertain={}))
            (root / "README.md").write_text("# Public test fixture\n", encoding="utf-8")
            core.write_json(root / "blog/_data/publisher.json", {})
            real_git = cli.git
            def no_push(path, *args):
                if args[0] == "push":
                    return ""
                return real_git(path, *args)
            with patch.object(cli, "git", side_effect=no_push):
                cli.commit(root, "test: actual commit identity")
            self.assertEqual(local("log", "-1", "--format=%an|%ae|%cn|%ce"),
                             "Test Owner|owner@example.test|Test Owner|owner@example.test")

    def test_missing_or_unsafe_identity_fails_before_git_mutation(self):
        for identity in ([], {}, {"name": "Owner", "email": "invalid"}, {"name": "Owner\nInjected", "email": "owner@example.test"}, {"name":"Owner", "email":"ow\x00ner@example.test"}):
            with self.subTest(identity=identity), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                core.write_json(root / "config/publisher.json", {"commit_identity": identity})
                with patch.object(cli, "git") as git, self.assertRaisesRegex(core.PublisherError, "valid-commit-identity-required"):
                    cli.commit(root, "test")
                git.assert_not_called()


if __name__ == "__main__":
    unittest.main()
