import unittest

from renderer import render_record


class RendererTests(unittest.TestCase):
    def test_shared_template_renders_article(self):
        record = {
            "id": "x1",
            "slug": "sample-story",
            "url": "/forum/ai/sample-story/",
            "category": "الذكاء الاصطناعي",
            "categorySlug": "ai",
            "title": "عنوان تقني اختباري طويل بما يكفي",
            "description": "وصف اختباري للمقال يوضح المحتوى بشكل مناسب لمحركات البحث والقراء.",
            "deck": "مقدمة مختصرة للمقال.",
            "summaryBullets": ["نقطة أولى", "نقطة ثانية", "نقطة ثالثة"],
            "sections": [{"heading": "قسم", "paragraphs": ["فقرة اختبارية"]}],
            "tags": ["AI"],
            "datePublished": "2026-09-16T17:00:00+03:00",
            "dateModified": "2026-09-16T17:00:00+03:00",
            "dateLabel": "16 سبتمبر 2026",
            "modifiedLabel": "16 سبتمبر 2026",
            "readMinutes": 3,
            "sources": [{"name": "Example", "url": "https://example.com", "title": "Source"}],
        }
        html = render_record(record)
        self.assertIn(record["title"], html)
        self.assertIn("NewsArticle", html)
        self.assertIn("https://rdwan.dev/forum/ai/sample-story/", html)
        self.assertNotIn("${TITLE}", html)


if __name__ == "__main__":
    unittest.main()
