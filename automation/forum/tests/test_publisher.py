import copy
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from publisher import _generate_qualified_editions, _make_content_record, _post_from_record, _quality_gate


class PublisherQualityTests(unittest.TestCase):
    def _article_ar(self):
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

    def _article_en(self):
        return {
            "title": "Technology company unveils a new platform for faster AI applications",
            "description": "A new technology platform aims to accelerate artificial intelligence workloads, with details on use cases, architecture and developer impact.",
            "deck": "The company introduced a new platform designed to run modern AI workloads more efficiently across current computing environments.",
            "summary_bullets": ["First useful point", "Second useful point", "Third useful point"],
            "sections": [
                {"heading": f"Section {i}", "paragraphs": [" ".join(["This technical paragraph explains confirmed details from the source without exaggeration or unsupported claims."] * 9), " ".join(["A second paragraph adds useful context while clearly separating company statements from directly supported facts."] * 9)]}
                for i in range(1, 5)
            ],
            "tags": ["Technology", "Artificial Intelligence", "Platform"],
            "entities": ["Example AI"]
        }

    def _editions(self):
        return {"ar": self._article_ar(), "en": self._article_en()}

    def _short_ar_editions(self):
        editions = self._editions()
        editions["ar"]["sections"] = [
            {"heading": f"قسم {i}", "paragraphs": ["فقرة عربية قصيرة تشرح جزءاً محدوداً من الخبر والمصدر."]}
            for i in range(1, 5)
        ]
        return editions

    def _story(self):
        return {
            "id": "abc123", "url": "https://example.com/news", "title": "Example AI platform launch",
            "category": "ai", "category_label": "الذكاء الاصطناعي", "source": {"type": "official"},
            "verification": {"confidence": 1.0, "reason": "official_source", "official": True},
            "trend": {"score": 110, "age_hours": 1},
        }

    def _sources(self):
        return [{"ok": True, "text": "source text", "url": "https://example.com", "kind": "official"}]

    def test_complete_bilingual_article_passes(self):
        ok, errors = _quality_gate(self._story(), self._sources(), self._editions())
        self.assertTrue(ok, errors)

    def test_missing_english_fails(self):
        ok, errors = _quality_gate(self._story(), self._sources(), {"ar": self._article_ar()})
        self.assertFalse(ok)
        self.assertIn("en:missing_edition", errors)

    def test_short_first_draft_is_retried_with_quality_feedback(self):
        calls = []

        def fake_writer(story, sources, settings, feedback):
            calls.append(copy.deepcopy(feedback))
            if len(calls) == 1:
                return self._short_ar_editions()
            return self._editions()

        editions, errors, attempts, status = _generate_qualified_editions(
            self._story(), self._sources(), {"publisherDraftAttempts": 2}, writer_fn=fake_writer
        )
        self.assertIsNotNone(editions)
        self.assertEqual(status, "passed")
        self.assertEqual(errors, [])
        self.assertEqual(len(attempts), 2)
        self.assertEqual(attempts[0]["status"], "quality_rejected")
        self.assertIn("ar:article_too_short", calls[1])
        self.assertEqual(attempts[1]["status"], "passed")

    def test_all_short_drafts_fail_gracefully_without_lowering_gate(self):
        def fake_writer(story, sources, settings, feedback):
            return self._short_ar_editions()

        editions, errors, attempts, status = _generate_qualified_editions(
            self._story(), self._sources(), {"publisherDraftAttempts": 2}, writer_fn=fake_writer
        )
        self.assertIsNone(editions)
        self.assertEqual(status, "quality_rejected")
        self.assertIn("ar:article_too_short", errors)
        self.assertEqual(len(attempts), 2)
        self.assertTrue(all(a["status"] == "quality_rejected" for a in attempts))

    def test_publication_uses_bilingual_structured_record(self):
        story = self._story()
        sources = [{"name": "Example", "url": story["url"], "kind": "official", "feed_title": story["title"]}]
        images = {"hero": "/forum/assets/test/hero.webp", "card": "/forum/assets/test/card.webp", "social": "/forum/assets/test/social.jpg", "alt": {"ar": "صورة", "en": "Image"}, "credit": "Example", "sourceUrl": story["url"]}
        record = _make_content_record(story, self._editions(), sources, "example-ai-platform-launch", datetime(2026, 9, 16, 14, 0, tzinfo=timezone.utc), images)
        self.assertEqual(record["schemaVersion"], 2)
        self.assertEqual(record["template"], "article")
        self.assertEqual(record["urls"]["ar"], "/forum/ar/ai/example-ai-platform-launch/")
        self.assertEqual(record["urls"]["en"], "/forum/en/ai/example-ai-platform-launch/")
        ar_post = _post_from_record(record, "ar", story)
        en_post = _post_from_record(record, "en", story)
        self.assertEqual(ar_post["image"], images["card"])
        self.assertEqual(en_post["alternates"]["ar"], record["urls"]["ar"])


if __name__ == "__main__":
    unittest.main()
