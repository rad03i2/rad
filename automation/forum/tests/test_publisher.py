import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from publisher import _quality_gate


class PublisherQualityTests(unittest.TestCase):
    def test_complete_article_passes(self):
        article = {
            "title": "شركة تقنية تكشف منصة جديدة لتسريع تطبيقات الذكاء الاصطناعي",
            "description": "إعلان تقني جديد يوضح منصة موجهة لتسريع تطبيقات الذكاء الاصطناعي، مع تفاصيل عن الاستخدامات والسياق التقني وما يعنيه للمطورين.",
            "deck": "أعلنت الشركة عن منصة جديدة تستهدف تشغيل أعباء الذكاء الاصطناعي بكفاءة أعلى ضمن بيئات الحوسبة الحديثة.",
            "summary_bullets": ["نقطة أولى مفيدة", "نقطة ثانية مفيدة", "نقطة ثالثة مفيدة"],
            "sections": [
                {"heading": f"قسم {i}", "paragraphs": [" ".join(["هذه فقرة عربية تقنية موثقة بالمصدر وتشرح التفاصيل والسياق بدون مبالغة"] * 8), " ".join(["فقرة ثانية تضيف سياقاً تقنياً واضحاً وتفصل ما أعلنته الشركة عن ما يمكن استنتاجه مباشرة"] * 8)]}
                for i in range(1, 5)
            ],
            "tags": ["تقنية", "ذكاء اصطناعي", "منصة"]
        }
        story = {"source": {"type": "official"}}
        sources = [{"ok": True, "text": "source text", "url": "https://example.com"}]
        ok, errors = _quality_gate(story, sources, article)
        self.assertTrue(ok, errors)

    def test_short_article_fails(self):
        article = {"title": "عنوان قصير جداً", "description": "وصف", "deck": "قصير", "summary_bullets": [], "sections": [], "tags": []}
        ok, errors = _quality_gate({"source": {"type": "official"}}, [{"ok": True, "text": "x"}], article)
        self.assertFalse(ok)
        self.assertIn("article_too_short", errors)


if __name__ == "__main__":
    unittest.main()
