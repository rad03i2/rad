import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from trend import rank_candidates


class TrendTests(unittest.TestCase):
    def test_official_fresh_story_ranks(self):
        now = datetime.now(timezone.utc).isoformat()
        items = [{
            "id": "a",
            "title": "OpenAI launches new AI automation model",
            "url": "https://openai.com/test",
            "domain": "openai.com",
            "published_at": now,
            "category": "ai",
            "score": 70,
            "source": {"name": "OpenAI", "type": "official"},
            "verification": {"confidence": 1.0, "publish_eligible": True},
        }]
        ranked = rank_candidates(items, {"trendWindowHours": 24, "minimumTrendScore": 40, "minimumVerificationConfidence": .9}, [])
        self.assertEqual(ranked[0]["id"], "a")
        self.assertGreater(ranked[0]["trend"]["score"], 70)

    def test_journalism_can_be_corroborated(self):
        now = datetime.now(timezone.utc).isoformat()
        base = {
            "published_at": now,
            "category": "robotics",
            "score": 60,
            "verification": {"confidence": .86, "publish_eligible": False},
        }
        items = [
            {**base, "id": "a", "title": "Company launches new humanoid robot platform", "url": "https://news-a.example/a", "domain": "news-a.example", "source": {"name": "A", "type": "journalism"}},
            {**base, "id": "b", "title": "New humanoid robot platform launched by company", "url": "https://news-b.example/b", "domain": "news-b.example", "source": {"name": "B", "type": "journalism"}},
        ]
        ranked = rank_candidates(items, {"trendWindowHours": 24, "minimumTrendScore": 40, "minimumVerificationConfidence": .9}, [])
        self.assertTrue(ranked)
        self.assertTrue(ranked[0]["verification"]["publish_eligible"])
        self.assertGreaterEqual(ranked[0]["trend"]["corroboration_count"], 1)

    def test_any_verified_tech_story_can_fallback_when_quiet(self):
        now = datetime.now(timezone.utc).isoformat()
        items = [{
            "id": "quiet-tech",
            "title": "Vendor updates desktop software documentation",
            "url": "https://vendor.example/update",
            "domain": "vendor.example",
            "published_at": now,
            "category": "apps",
            "score": 1,
            "source": {"name": "Vendor", "type": "official"},
            "verification": {"confidence": .95, "publish_eligible": True},
        }]
        ranked = rank_candidates(items, {
            "trendWindowHours": 24,
            "minimumTrendScore": 999,
            "minimumVerificationConfidence": .9,
            "allowAnyVerifiedTechStory": True,
        }, [])
        self.assertEqual([item["id"] for item in ranked], ["quiet-tech"])


if __name__ == "__main__":
    unittest.main()
