from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import generate_entity_hubs as hubs


class EntityDiscoveryTests(unittest.TestCase):
    def test_section_specialist_is_discoverable_among_larger_general_entities(self):
        entities = {
            f"general-{i}": {
                "slug": f"general-{i}", "name": f"General {i}",
                "storyCount": 200 + i, "categories": {"web": 2},
            }
            for i in range(6)
        }
        entities["cloudflare"] = {
            "slug": "cloudflare", "name": "Cloudflare", "storyCount": 76,
            "categories": {"web": 27},
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for locale in ("ar", "en"):
                target = root / locale / "web" / "index.html"
                target.parent.mkdir(parents=True)
                target.write_text("<main><div>Topic hub</div></main>", encoding="utf-8")
            with patch.object(hubs, "FORUM", root):
                hubs.patch_internal_discovery(entities)
                hubs.patch_internal_discovery(entities)
            for locale in ("ar", "en"):
                html = (root / locale / "web" / "index.html").read_text(encoding="utf-8")
                self.assertIn(f'href="/{locale}/entities/cloudflare/"', html)
                self.assertEqual(html.count('class="rt-topic-card"'), 6)
                self.assertEqual(html.count('data-entity-discovery="true"'), 1)


if __name__ == "__main__":
    unittest.main()
