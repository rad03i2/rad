import sys
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from writer import _extract_link_candidates, _extract_media_candidates


class WriterRichContentTests(unittest.TestCase):
    def test_extracts_article_media_and_links(self):
        html = """
        <article>
          <p>Story body with <a href="/company/product">Product page</a>.</p>
          <figure>
            <img src="/images/product-large.jpg" width="1200" height="700" alt="Product hardware">
            <figcaption>Product shown during the announcement</figcaption>
          </figure>
          <img src="/icons/logo.png" width="64" height="64" alt="Logo">
        </article>
        """
        root = BeautifulSoup(html, "html.parser").article
        media = _extract_media_candidates(root, "https://example.com/news")
        links = _extract_link_candidates(root, "https://example.com/news")
        self.assertEqual(len(media), 1)
        self.assertEqual(media[0]["url"], "https://example.com/images/product-large.jpg")
        self.assertEqual(media[0]["caption"], "Product shown during the announcement")
        self.assertEqual(links[0]["url"], "https://example.com/company/product")


if __name__ == "__main__":
    unittest.main()
