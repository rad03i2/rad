from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[1]))

import pipeline


class SocialPipelineTests(unittest.TestCase):
    def setUp(self):
        self.content = {
            "id": "story-123",
            "categorySlug": "ai",
            "urls": {"ar": "/forum/ar/ai/example-story/", "en": "/forum/en/ai/example-story/"},
            "locales": {
                "ar": {
                    "title": "شركة تقنية تطلق تحديثًا جديدًا لأدوات الذكاء الاصطناعي",
                    "description": "أعلنت الشركة تحديثًا موثقًا يضيف أدوات جديدة للمطورين ويحسن إدارة المشاريع التقنية.",
                    "deck": "التحديث يركز على أدوات المطورين وتحسين سير العمل.",
                }
            },
            "trendScore": 120,
            "verification": {"confidence": 1.0, "official": True},
            "images": {"social": "/forum/assets/posts/2026/09/example/social.jpg", "generatedFallback": False},
        }
        self.rules = {
            "platforms": {
                "facebook": {"enabled": True, "min_score": 72},
                "instagram": {"enabled": True, "min_score": 78},
                "threads": {"enabled": True, "min_score": 66},
                "tiktok": {"enabled": True, "min_score": 84, "preferred_categories": ["ai"]},
            }
        }

    def test_canonical_never_contains_utm(self):
        self.assertEqual(pipeline.canonical_url(self.content), "https://rdwan.dev/forum/ar/ai/example-story/")
        tagged = pipeline.with_utm(pipeline.canonical_url(self.content), "facebook")
        self.assertIn("utm_source=facebook", tagged)
        self.assertNotIn("utm_", pipeline.canonical_url(self.content))

    def test_story_id_prefers_stable_content_id(self):
        self.assertEqual(pipeline.story_id(self.content), "story-123")
        no_id = dict(self.content)
        no_id.pop("id")
        self.assertEqual(pipeline.story_id(no_id), pipeline.story_id(no_id))

    def test_platform_selection_is_editorial(self):
        score = pipeline.social_score(self.content)
        selected = pipeline.select_platforms(self.content, score, self.rules)
        self.assertIn("threads", selected)
        self.assertIn("facebook", selected)
        self.assertIn("instagram", selected)
        self.assertIn("tiktok", selected)

    def test_missing_image_removes_visual_networks(self):
        content = dict(self.content)
        content["images"] = {}
        selected = pipeline.select_platforms(content, 95, self.rules)
        self.assertIn("facebook", selected)
        self.assertIn("threads", selected)
        self.assertNotIn("instagram", selected)
        self.assertNotIn("tiktok", selected)

    def test_platform_copy_is_not_reused(self):
        facebook = pipeline.generate_copy(self.content, "facebook")["text"]
        instagram = pipeline.generate_copy(self.content, "instagram")["text"]
        threads = pipeline.generate_copy(self.content, "threads")["text"]
        self.assertNotEqual(facebook, instagram)
        self.assertNotEqual(facebook, threads)
        self.assertIn("utm_source=facebook", facebook)
        self.assertNotIn("utm_source=instagram", instagram)

    def test_retry_is_exponential(self):
        with patch.object(pipeline, "now_local", return_value=pipeline.datetime(2026, 9, 22, 1, 0, tzinfo=pipeline.TZ)):
            first = pipeline.parse_dt(pipeline.retry_at(1))
            third = pipeline.parse_dt(pipeline.retry_at(3))
            self.assertEqual(int((first - pipeline.now_local()).total_seconds() / 60), 15)
            self.assertEqual(int((third - pipeline.now_local()).total_seconds() / 60), 60)

    def test_live_mode_fails_closed_without_credentials(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(pipeline.SocialConfigError):
                pipeline._metricool_credentials()


if __name__ == "__main__":
    unittest.main()
