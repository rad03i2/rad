from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


class PublicationContractTests(unittest.TestCase):
    def _read(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_publishing_settings_keep_twenty_minute_contract(self) -> None:
        settings = json.loads(self._read("automation/forum/config/settings.json"))
        self.assertIs(settings.get("publishingEnabled"), True)
        self.assertIs(settings.get("dryRun"), False)
        self.assertEqual(settings.get("minimumMinutesBetweenPosts"), 20)
        self.assertEqual(settings.get("maxPostsPerRun"), 1)

    def test_primary_publisher_keeps_all_wakeup_paths(self) -> None:
        workflow = self._read(".github/workflows/forum-collector.yml")
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("trigger:", workflow)
        self.assertIn("required: true", workflow)
        self.assertIn("cron: '2,22,42 * * * *'", workflow)
        self.assertIn("group: mikhbar-publication-write", workflow)
        self.assertIn("python automation/forum/publisher_scheduler.py", workflow)

    def test_external_wakeup_matches_twenty_minute_publication_clock(self) -> None:
        wrangler = self._read("automation/external-scheduler/cloudflare/wrangler.toml")
        worker = self._read("automation/external-scheduler/cloudflare/src/index.js")
        self.assertIn('crons = ["2,22,42 * * * *"]', wrangler)
        self.assertIn('const CRON = "2,22,42 * * * *";', worker)
        self.assertIn('inputs: { trigger: "external-20m" }', worker)
        self.assertIn("publication_cadence_source", worker)

    def test_backup_publisher_remains_independent_and_serialized(self) -> None:
        workflow = self._read(".github/workflows/forum-publisher-backup.yml")
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("group: mikhbar-publication-write", workflow)
        self.assertIn("python automation/forum/publisher_scheduler.py", workflow)
        self.assertIn("cron: '8,13,18,28,33,38,48,53,58 * * * *'", workflow)

    def test_social_automation_cannot_commit_forum_publication_files(self) -> None:
        social_path = ROOT / ".github/workflows/mikhbar-social.yml"
        if not social_path.exists():
            self.skipTest("Social workflow is not installed.")
        workflow = social_path.read_text(encoding="utf-8")
        self.assertIn("group: mikhbar-social-state", workflow)
        self.assertIn("git add automation/social/state/facebook.json", workflow)
        self.assertNotIn("git add forum ", workflow)
        self.assertNotIn("git add automation/forum", workflow)


if __name__ == "__main__":
    unittest.main()
