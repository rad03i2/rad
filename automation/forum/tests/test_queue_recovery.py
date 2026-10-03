from __future__ import annotations

import copy
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import run as pipeline
from common import load_json, save_json, stable_id
from deduplicator import deduplicate
from queue_lifecycle import limit_queue, pending_queue, reconcile_seen


def story(name: str, *, age: int = 0, score: int = 30, status: str = "incoming") -> dict:
    url = f"https://vendor.example/{name}"
    return {
        "id": stable_id(url), "title": name, "url": url, "domain": "vendor.example",
        "published_at": (datetime.now(timezone.utc) - timedelta(hours=age)).isoformat(),
        "status": status, "score": score, "category": "ai",
        "source": {"name": "Vendor", "type": "official", "trust": 1, "priority": 30},
        "verification": {"confidence": 1, "publish_eligible": True},
    }


class QueueRecoveryTests(unittest.TestCase):
    settings = {"maxQueueItems": 2, "maxAgeHours": 72, "trendWindowHours": 72, "minimumTrendScore": 0}

    def test_published_and_stale_records_cannot_displace_fresh_news(self):
        items = [story("published", score=100, status="published"), story("stale", age=80, score=100), story("fresh")]
        self.assertEqual([x["title"] for x in pending_queue(items, {}, self.settings)], ["fresh"])

    def test_orphan_recovery_keeps_published_and_quality_rejected_urls_blocked(self):
        lost, published, rejected = story("lost"), story("published"), story("rejected", status="quality_rejected")
        history = {"items": [{"source_url": published["url"], "story_id": published["id"]}]}
        seen = {"urls": {x["url"]: x["id"] for x in [lost, published, rejected]}, "titles": {}}
        reconciled = reconcile_seen(seen, [], history, [rejected])
        # The rejection remains durable even after its queue record is removed.
        reconciled = reconcile_seen(reconciled, [], history, [])
        fresh, duplicates, _ = deduplicate([lost, published, rejected], [], reconciled, .9)
        self.assertEqual([x["title"] for x in fresh], ["lost"])
        self.assertEqual(duplicates, 2)

    def test_capacity_deferral_can_be_recollected_and_ready_story_is_retained(self):
        ready, high, deferred = story("ready", score=1), story("high", score=100), story("deferred", score=90)
        retained = limit_queue([ready, high, deferred], self.settings, {"status": "ready", "story": ready})
        self.assertEqual([x["title"] for x in retained], ["ready", "high"])
        seen = reconcile_seen({"urls": {deferred["url"]: deferred["id"]}}, retained, {}, [])
        fresh, _, _ = deduplicate([deferred], retained, seen, .9)
        self.assertEqual(fresh, [deferred])

    def test_full_collector_recovers_saturated_queue_and_reports_actual_candidates(self):
        old = [story(f"old-{i}", age=80, score=100, status="published") for i in range(5)]
        stale = story("expired unpublished", age=80, score=90)
        lost, published, rejected = story("recover fresh launch"), story("already published"), story("failed draft", status="quality_rejected")
        history = {"items": [{"source_url": published["url"], "story_id": published["id"]}]}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config, state = root / "automation/forum/config", root / "automation/forum/state"
            save_json(config / "settings.json", {**self.settings, "dryRun": False, "publishingEnabled": True})
            save_json(state / "queue.json", {"items": old + [stale, rejected]})
            save_json(state / "published.json", history)
            save_json(state / "seen.json", {"urls": {x["url"]: x["id"] for x in old + [lost, published, rejected]}})
            collection = {"sources_ok": 1, "sources_failed": 0, "fetched": 3, "errors": []}
            with patch.object(pipeline, "CONFIG", config), patch.object(pipeline, "STATE", state), \
                 patch.object(pipeline, "collect", return_value=([lost, published, rejected], collection)), \
                 patch.object(pipeline, "verify_and_score", return_value=(copy.deepcopy([lost, published, rejected]), 0)), \
                 patch.object(sys, "argv", ["run.py"]):
                self.assertEqual(pipeline.main(), 0)
            queue = load_json(state / "queue.json", {})["items"]
            candidates = load_json(state / "candidates.json", {})["items"]
            report = load_json(state / "run_report.json", {})
            self.assertEqual([x["title"] for x in queue], [lost["title"]])
            self.assertEqual([x["title"] for x in candidates], [lost["title"]])
            self.assertEqual(report["publish_eligible"], 1)
            self.assertEqual(report["accepted_new"], 1)
            self.assertEqual(report["removed_terminal_or_expired"], 7)


if __name__ == "__main__":
    unittest.main()
