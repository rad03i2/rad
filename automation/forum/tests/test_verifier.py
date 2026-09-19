import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from verifier import refresh_queue_verification, verify_and_score


class VerifierPolicyTests(unittest.TestCase):
    def _story(self, trust=0.86):
        return {
            "title": "Technology company launches a new AI platform",
            "summary": "A detailed product announcement for developers.",
            "url": "https://news.example/story",
            "domain": "news.example",
            "published_at": datetime.now(timezone.utc).isoformat(),
            "source": {
                "name": "Trusted Tech News",
                "type": "journalism",
                "trust": trust,
                "priority": 20,
                "defaultCategory": "ai",
            },
        }

    def _settings(self):
        return {
            "maxAgeHours": 72,
            "minimumVerificationConfidence": 0.90,
            "allowTrustedJournalismSingleSource": True,
            "trustedJournalismSingleSourceThreshold": 0.84,
        }

    def test_trusted_journalism_can_be_single_source_publishable(self):
        accepted, rejected = verify_and_score([self._story(0.86)], self._settings())
        self.assertEqual(rejected, 0)
        self.assertTrue(accepted[0]["verification"]["publish_eligible"])
        self.assertTrue(accepted[0]["verification"]["single_source_trusted"])
        self.assertEqual(accepted[0]["verification"]["reason"], "trusted_journalism_single_source")

    def test_lower_trust_journalism_still_requires_corroboration(self):
        accepted, rejected = verify_and_score([self._story(0.80)], self._settings())
        self.assertEqual(rejected, 0)
        self.assertFalse(accepted[0]["verification"]["publish_eligible"])
        self.assertFalse(accepted[0]["verification"]["single_source_trusted"])

    def test_existing_queue_item_is_refreshed(self):
        item = self._story(0.88)
        item["status"] = "incoming"
        item["verification"] = {"confidence": 0.88, "publish_eligible": False}
        refreshed = refresh_queue_verification([item], self._settings())
        self.assertTrue(refreshed[0]["verification"]["publish_eligible"])


if __name__ == "__main__":
    unittest.main()
