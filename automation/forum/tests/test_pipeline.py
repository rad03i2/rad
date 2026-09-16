from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from common import canonicalize_url, jaccard_title, normalize_title, stable_id
from deduplicator import deduplicate


class PipelineTests(unittest.TestCase):
    def test_tracking_params_removed(self):
        url = canonicalize_url("https://example.com/news/item/?utm_source=x&id=5#top")
        self.assertEqual(url, "https://example.com/news/item?id=5")

    def test_title_similarity(self):
        a = "OpenAI launches a new AI model for developers"
        b = "OpenAI launches new AI model for developers"
        self.assertGreaterEqual(jaccard_title(a, b), 0.8)

    def test_stable_id(self):
        self.assertEqual(stable_id("https://example.com/a"), stable_id("https://example.com/a/"))

    def test_dedup_same_url(self):
        story = {"title":"Test story","url":"https://example.com/a","source":{"name":"A"},"verification":{"confidence":0.9}}
        seen = {"urls":{"https://example.com/a":"old"},"titles":{}}
        fresh, duplicates, _ = deduplicate([story], [], seen, 0.9)
        self.assertEqual(fresh, [])
        self.assertEqual(duplicates, 1)


if __name__ == "__main__":
    unittest.main()
