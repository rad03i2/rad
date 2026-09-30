from __future__ import annotations

import json
import subprocess
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import publisher_scheduler as scheduler
import publisher_wakeup as wakeup


class WakeupRecoveryTests(unittest.TestCase):
    def load(self, path, default):
        if path.name == "settings.json":
            return {"publishingEnabled": True, "minimumMinutesBetweenPosts": 20}
        return {"last_published_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()}

    @patch.dict("os.environ", {"GITHUB_REPOSITORY": "rad03i2/rad"})
    def test_overdue_checks_both_publishers_with_get_then_dispatches(self):
        with patch.object(wakeup, "load_json", side_effect=self.load), patch.object(wakeup.subprocess, "run") as run:
            run.return_value = subprocess.CompletedProcess([], 0, stdout=json.dumps({"workflow_runs": []}))
            self.assertEqual(wakeup.wake("test-recovery", 18), 0)
            self.assertEqual(run.call_count, 3)
            for call in run.call_args_list[:2]:
                self.assertIn("GET", call.args[0])
                self.assertIsNone(call.kwargs.get("stderr"))
            payload = json.loads(run.call_args.kwargs["input"])
            self.assertEqual(payload, {"ref": "main", "inputs": {"trigger": "test-recovery"}})

    @patch.dict("os.environ", {"GITHUB_REPOSITORY": "rad03i2/rad"})
    def test_active_backup_prevents_competing_dispatch(self):
        with patch.object(wakeup, "load_json", side_effect=self.load), patch.object(wakeup.subprocess, "run") as run:
            run.side_effect = [
                subprocess.CompletedProcess([], 0, stdout='{"workflow_runs": []}'),
                subprocess.CompletedProcess([], 0, stdout='{"workflow_runs": [{"status": "pending"}]}'),
            ]
            wakeup.wake("test-recovery", 18)
            self.assertEqual(run.call_count, 2)

    @patch.dict("os.environ", {"GITHUB_REPOSITORY": "rad03i2/rad"})
    def test_api_failure_is_not_reported_as_success(self):
        with patch.object(wakeup, "load_json", side_effect=self.load), patch.object(wakeup.subprocess, "run") as run:
            run.side_effect = subprocess.CalledProcessError(1, ["gh", "api"])
            with self.assertRaises(subprocess.CalledProcessError):
                wakeup.wake("test-recovery", 18)
            self.assertEqual(run.call_count, 1)


class PreparationBoundaryTests(unittest.TestCase):
    def test_ready_article_waits_for_slot_and_publishes_without_early_release(self):
        last = datetime(2026, 9, 29, 12, 0, tzinfo=timezone.utc)
        start = last + timedelta(minutes=19, seconds=35)
        early_wakeup = last + timedelta(minutes=19, seconds=50)
        due = last + timedelta(minutes=20)
        prepared = {"status": "ready", "story": {"id": "approved"}}

        def load(path, default):
            if path.name == "settings.json":
                return {"publishingEnabled": True, "minimumMinutesBetweenPosts": 20}
            if path.name == "published.json":
                return {"last_published_at": last.isoformat(), "items": []}
            if path.name == "prepared_article.json":
                return prepared
            return default

        with patch.object(scheduler, "load_json", side_effect=load), \
             patch.object(scheduler, "datetime") as clock, \
             patch.object(scheduler, "_prepared_is_valid", return_value=True), \
             patch.object(scheduler.time, "sleep") as sleep, \
             patch.object(scheduler, "_publish_prepared", return_value=0) as publish:
            clock.now.side_effect = [start, start, early_wakeup, due]
            self.assertEqual(scheduler.main(), 0)
            publish.assert_called_once_with(prepared, ignore_cooldown=False)
            self.assertEqual([call.args[0] for call in sleep.call_args_list], [25, 10])

    def test_distant_slot_does_not_hold_runner(self):
        target = datetime(2026, 9, 29, 12, 20, tzinfo=timezone.utc)
        now = target - timedelta(minutes=6)
        with patch.object(scheduler.time, "sleep") as sleep:
            self.assertEqual(scheduler._wait_for_near_boundary(target, now), now)
            sleep.assert_not_called()

    def test_near_boundary_wait_is_bounded_even_if_clock_moves_back(self):
        target = datetime(2026, 9, 29, 12, 20, tzinfo=timezone.utc)
        now = target - timedelta(minutes=1)
        with patch.object(scheduler, "datetime") as clock, \
             patch.object(scheduler.time, "monotonic", side_effect=[0, 0, 301]), \
             patch.object(scheduler.time, "sleep") as sleep:
            clock.now.return_value = now - timedelta(minutes=1)
            returned = scheduler._wait_for_near_boundary(target, now)
            self.assertLess(returned, target)
            sleep.assert_called_once_with(30)

    def test_draft_finishing_after_boundary_publishes_in_same_run(self):
        last = datetime(2026, 9, 29, 12, 0, tzinfo=timezone.utc)
        before = last + timedelta(minutes=19, seconds=59)
        after = last + timedelta(minutes=20, seconds=1)
        def load(path, default):
            if path.name == "settings.json":
                return {"publishingEnabled": True, "minimumMinutesBetweenPosts": 20}
            if path.name == "published.json":
                return {"last_published_at": last.isoformat(), "items": []}
            return default
        with patch.object(scheduler, "load_json", side_effect=load), \
             patch.object(scheduler, "datetime") as clock, \
             patch.object(scheduler, "_prepared_is_valid", return_value=False), \
             patch.object(scheduler, "_prepare_next", return_value={"story": {"id": "approved"}}), \
             patch.object(scheduler, "_publish_prepared", return_value=0) as publish:
            clock.now.side_effect = [before, after]
            scheduler.main()
            publish.assert_called_once_with({"story": {"id": "approved"}}, ignore_cooldown=False)


if __name__ == "__main__":
    unittest.main()
