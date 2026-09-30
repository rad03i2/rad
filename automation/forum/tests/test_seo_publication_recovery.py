from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import audit_multilingual_trust as trust_audit
import audit_pillar_pages as pillar_audit
import audit_topic_hubs as hub_audit
import build_locale_pages as locales
import enhance_category_seo as hubs
import generate_pillar_pages as pillars
import generate_trust_pages as trust
import normalize_public_identity as identity


class SeoPublicationRecoveryTests(unittest.TestCase):
    def test_generated_publication_hubs_pass_with_external_brand_reference(self):
        # Exercise the same generators, normalizer and audits that blocked every
        # scheduled publication after the external sameAs reference was added.
        with tempfile.TemporaryDirectory() as directory, contextlib.ExitStack() as stack:
            forum = Path(directory)
            for module in (locales, hubs, pillars, identity, hub_audit, pillar_audit, trust_audit):
                stack.enter_context(patch.object(module, "FORUM", forum))
            stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
            stack.enter_context(contextlib.redirect_stderr(io.StringIO()))
            (forum / "posts.json").write_text("[]", encoding="utf-8")
            self.assertEqual(locales.main(), 0)
            self.assertEqual(hubs.main(), 0)
            self.assertEqual(pillars.main(), 0)
            identity.normalize_public_identity()
            self.assertEqual(hub_audit.main(), 0)
            self.assertEqual(pillar_audit.main(), 0)
            html = (forum / "ar/ai/index.html").read_text(encoding="utf-8")
            self.assertIn(identity.BRAND_REFERENCE_URL, html)
            self.assertIn('href="https://mikhbar.website/ar/ai/"', html)
            self.assertFalse(identity.has_legacy_identity(html))

            # A real old canonical URL must still block the publication.
            (forum / "ar/ai/index.html").write_text(
                html + '<link rel="canonical" href="https://rdwan.dev/forum/ar/ai/">',
                encoding="utf-8",
            )
            self.assertEqual(hub_audit.main(), 1)

    def test_generated_english_trust_page_accepts_sameas_reference(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(trust_audit, "FORUM", Path(directory)), patch.object(trust, "FORUM", Path(directory)):
            spec = trust.PAGES["about"]
            target = Path(directory) / "en/about/index.html"
            target.parent.mkdir(parents=True)
            target.write_text(trust.english_page("about", spec), encoding="utf-8")
            trust.patch_locale_navigation()
            errors = []
            trust_audit.check_page("/en/about/", "en", "/about/", "/en/about/", errors)
            self.assertEqual(errors, [])

    def test_only_exact_brand_reference_is_allowed(self):
        reference = identity.BRAND_REFERENCE_URL
        self.assertFalse(identity.has_legacy_identity(json.dumps({"sameAs": [reference]})))
        for url in (
            "https://rdwan.dev/forum/ar/ai/",
            reference + "/old-page/",
            reference + ".old",
            reference + "?old=1",
            "https://www.rdwan.dev/mikhbar.html",
        ):
            with self.subTest(url=url):
                self.assertTrue(identity.has_legacy_identity(json.dumps({"url": url})))
                self.assertNotIn("rdwan.dev", identity._normalize(json.dumps({"url": url})))
        self.assertEqual(identity._normalize(json.dumps([reference])), json.dumps([reference]))

    def test_deployment_audit_reports_real_legacy_files_without_mutating_them(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            allowed = root / "index.html"
            allowed.write_text(json.dumps({"sameAs": [identity.BRAND_REFERENCE_URL]}), encoding="utf-8")
            old = root / "feed.xml"
            old.write_text("<loc>https://rdwan.dev/forum/ar/ai/</loc>", encoding="utf-8")
            before = old.read_bytes()
            (root / "image.png").write_bytes(b"\x89PNG\xff\x00")
            self.assertEqual(identity.audit_identity_tree(root), ["feed.xml"])
            self.assertEqual(old.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
