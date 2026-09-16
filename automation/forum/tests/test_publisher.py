import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from publisher import _make_content_record, _post_from_record, _quality_gate


class PublisherQualityTests(unittest.TestCase):
    def _article(self):
        return {
            "title": "شركة تقنية تكشف منصة جديدة لتسريع تطبيقات الذكاء الاصطناعي",
            "description": "إعلان تقني جديد يوضح منصة موجهة لتسريع تطبيقات الذكاء الاصطناعي، مع تفاصيل عن الاستخدامات والسياق التقني وما يعنيه للمطورين.",
            "deck": "أعلنت الشركة عن منصة جديدة تستهدف تشغيل أعباء الذكاء الاصطناعي بكفاءة أعلى ضمن بيئات الحوسبة الحديثة.",
            "summary_bullets": ["نقطة أولى مفيدة", "نقطة ثانية مفيدة", "نقطة ثالثة مفيدة"],
            "sections": [
                {"heading": f"قسم {i}", "paragraphs": [" ".join(["هذه فقرة عربية تقنية موثقة بالمصدر وتشرح التفاصيل والسياق بدون مبالغة"] * 8), " ".join(["فقرة ثانية تضيف سياقاً تقنياً واضحاً وتفصل ما أعلنته الشركة عن ما يمكن استنتاجه مباشرة"] * 8)]}
                for i in range(1, 5)
            ],
            "tags": ["تقنية", "ذكاء اصطناعي", "منصة"],
            "entities": ["Example AI"]
        }

    def test_complete_article_passes(self):
        article = self._article()
        story = {"source": {"type": "official"}}
        sources = [{"ok": True, "text": "source text", "url": "https://example.com"}]
        ok, errors = _quality_gate(story, sources, article)
        self.assertTrue(ok, errors)

    def test_short_article_fails(self):
        article = {"title": "عنوان قصير جداً", "description": "وصف", "deck": "قصير", "summary_bullets": [], "sections": [], "tags": []}
        ok, errors = _quality_gate({"source": {"type": "official"}}, [{"ok": True, "text": "x"}], article)
        self.assertFalse(ok)
        self.assertIn("article_too_short", errors)

    def test_publication_uses_structured_content_record(self):
        story = {
            "id": "abc123",
            "url": "https://example.com/news",
            "title": "Example AI platform launch",
            "category": "ai",
            "category_label": "الذكاء الاصطناعي",
            "source": {"type": "official"},
            "verification": {"confidence": 1.0, "reason": "official_source", "official": True},
            "trend": {"score": 110, "age_hours": 1},
        }
        sources = [{"name": "Example", "url": story["url"], "kind": "official", "feed_title": story["title"]}]
        record = _make_content_record(story, self._article(), sources, "example-ai-platform-launch", datetime(2026, 9, 16, 14, 0, tzinfo=timezone.utc), 4)
        self.assertEqual(record["template"], "article")
        self.assertEqual(record["categorySlug"], "ai")
        self.assertEqual(record["url"], "/forum/ai/example-ai-platform-launch/")
        post = _post_from_record(record, story)
        self.assertEqual(post["url"], record["url"])
        self.assertEqual(post["title"], record["title"])


if __name__ == "__main__":
    unittest.main()
