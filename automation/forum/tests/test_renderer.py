import unittest

from renderer import render_record


class RendererTests(unittest.TestCase):
    def _record(self):
        return {
            "schemaVersion": 2,
            "id": "x1",
            "slug": "sample-story",
            "categorySlug": "ai",
            "urls": {"ar": "/forum/ar/ai/sample-story/", "en": "/forum/en/ai/sample-story/"},
            "locales": {
                "ar": {
                    "title": "عنوان تقني اختباري طويل بما يكفي",
                    "description": "وصف اختباري للمقال يوضح المحتوى بشكل مناسب لمحركات البحث والقراء ويقدم سياقاً واضحاً للموضوع التقني.",
                    "deck": "مقدمة مختصرة للمقال.",
                    "summaryBullets": ["نقطة أولى", "نقطة ثانية", "نقطة ثالثة"],
                    "sections": [{"heading": "قسم", "paragraphs": ["فقرة اختبارية"]}],
                    "tags": ["AI"], "category": "الذكاء الاصطناعي", "dateLabel": "16 سبتمبر 2026", "modifiedLabel": "16 سبتمبر 2026", "readMinutes": 3,
                },
                "en": {
                    "title": "A sufficiently long sample technology headline for testing",
                    "description": "A test description that clearly explains the technology article for readers and search engines with useful context.",
                    "deck": "A short introduction to the test story.",
                    "summaryBullets": ["First point", "Second point", "Third point"],
                    "sections": [{"heading": "Section", "paragraphs": ["Test paragraph"]}],
                    "tags": ["AI"], "category": "Artificial Intelligence", "dateLabel": "September 16, 2026", "modifiedLabel": "September 16, 2026", "readMinutes": 3,
                },
            },
            "datePublished": "2026-09-16T17:00:00+03:00",
            "dateModified": "2026-09-16T17:00:00+03:00",
            "images": {"hero": "/forum/assets/test/hero.webp", "social": "/forum/assets/test/social.jpg", "alt": {"ar": "صورة", "en": "Image"}, "credit": "Example", "sourceUrl": "https://example.com"},
            "sources": [{"name": "Example", "url": "https://example.com", "title": "Source"}],
        }

    def test_shared_template_renders_arabic_article(self):
        record = self._record()
        html = render_record(record, "ar")
        self.assertIn(record["locales"]["ar"]["title"], html)
        self.assertIn("NewsArticle", html)
        self.assertIn("https://rdwan.dev/forum/ar/ai/sample-story/", html)
        self.assertIn('hreflang="en"', html)
        self.assertIn("hero.webp", html)
        self.assertNotIn("${TITLE}", html)

    def test_shared_template_renders_english_article(self):
        record = self._record()
        html = render_record(record, "en")
        self.assertIn('lang="en"', html)
        self.assertIn('dir="ltr"', html)
        self.assertIn(record["locales"]["en"]["title"], html)
        self.assertIn("https://rdwan.dev/forum/en/ai/sample-story/", html)
        self.assertIn('hreflang="ar"', html)


if __name__ == "__main__":
    unittest.main()
