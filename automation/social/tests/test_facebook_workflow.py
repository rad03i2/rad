from __future__ import annotations

import io
import json
import os
import tempfile
import textwrap
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]


class FacebookWorkflowTests(unittest.TestCase):
    def run_publisher(self, article_url, *, duplicate=False, wrong_page=False,
                      with_image=False, site_ready=True, image_ready=True, automatic=False):
        workflow = (ROOT / ".github/workflows/mikhbar-social.yml").read_text()
        code = textwrap.dedent(
            workflow.split("python - <<'PY'\n", 1)[1].split("\n          PY", 1)[0]
        )
        calls = []

        def urlopen_stub(req, timeout):
            calls.append(req)
            if req.full_url.startswith("https://mikhbar.website/"):
                from urllib.error import HTTPError
                if not site_ready:
                    raise HTTPError(req.full_url, 404, "Not Found", {}, io.BytesIO(b""))
                is_image = req.full_url.endswith(".jpg")
                body = (b"\xff\xd8\xffimage" if image_ready else b"not an image") if is_image else (
                    b'<html data-ssr-rendered="true"><link rel="canonical" href="https://mikhbar.website/ar/ai/example/"></html>'
                )
                response = io.BytesIO(body)
                response.headers = {"Content-Type": "image/jpeg" if is_image else "text/html"}
                return response
            if req.method == "POST":
                return io.BytesIO(b'{"id":"123_post"}')
            result = {"id": "999" if wrong_page and "/123?" in req.full_url else "123", "name": "Mikhbar"}
            return io.BytesIO(json.dumps(result).encode())

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            content_file = "forum/content/story.json"
            (root / content_file).parent.mkdir(parents=True)
            (root / content_file).write_text(json.dumps({
                "id": "story-1", "urls": {"ar": article_url},
                "images": {"social": "/forum/assets/posts/story/social.jpg"} if with_image else {},
                "locales": {"ar": {"title": "خبر موثق", "description": "ملخص الخبر"}},
            }))
            published = root / "automation/forum/state/published.json"
            published.parent.mkdir(parents=True)
            published.write_text(json.dumps({"items": [{
                "story_id": "story-1", "content_file": content_file,
            }]}))
            state = root / "automation/social/state/facebook.json"
            state.parent.mkdir(parents=True)
            state.write_text(json.dumps({"published_story_ids": ["story-1"] if duplicate else []}))
            previous = Path.cwd()
            try:
                os.chdir(root)
                with patch.dict(os.environ, {
                    "FACEBOOK_PAGE_ID": "123", "FACEBOOK_PAGE_ACCESS_TOKEN": "test-token",
                    "GITHUB_EVENT_NAME": "workflow_run" if automatic else "workflow_dispatch",
                    "MANUAL_STORY_IDS": "",
                }), patch("urllib.request.urlopen", side_effect=urlopen_stub), redirect_stdout(io.StringIO()):
                    try:
                        exec(compile(code, "facebook-workflow", "exec"), {})
                    except SystemExit as error:
                        self.assertEqual(error.code, 0)
                result = json.loads(state.read_text())
            finally:
                os.chdir(previous)
        return calls, result

    def test_legacy_url_publishes_canonical_mikhbar_link_and_records_success(self):
        calls, state = self.run_publisher("https://rdwan.dev/forum/ar/ai/example/?old=1")
        post = calls[-1]
        from urllib.parse import parse_qs
        data = parse_qs(post.data.decode())
        self.assertEqual(post.method, "POST")
        self.assertEqual(
            data["link"][0],
            "https://mikhbar.website/ar/ai/example/?utm_source=facebook&utm_medium=social&utm_campaign=mikhbar_social",
        )
        self.assertNotIn("rdwan.dev", data["message"][0])
        self.assertEqual(state["published_story_ids"], ["story-1"])
        self.assertEqual(state["last_success"]["facebook_post_id"], "123_post")

    def test_duplicate_does_not_call_facebook_or_require_token_refresh(self):
        calls, state = self.run_publisher("/forum/ar/ai/example/", duplicate=True)
        self.assertEqual(calls, [])
        self.assertEqual(state["published_story_ids"], ["story-1"])

    def test_wrong_page_cannot_publish(self):
        with self.assertRaisesRegex(RuntimeError, "expected 123"):
            self.run_publisher("/ar/ai/example/", wrong_page=True)

    def test_automatic_run_defers_unavailable_page_without_graph_calls_or_state_change(self):
        calls, state = self.run_publisher("/ar/ai/example/", site_ready=False, automatic=True)
        self.assertFalse(any("graph.facebook.com" in req.full_url for req in calls))
        self.assertEqual(state, {"published_story_ids": []})

    def test_automatic_run_defers_invalid_image_without_graph_calls_or_state_change(self):
        calls, state = self.run_publisher(
            "/ar/ai/example/", with_image=True, image_ready=False, automatic=True,
        )
        self.assertFalse(any("graph.facebook.com" in req.full_url for req in calls))
        self.assertEqual(state, {"published_story_ids": []})

    def test_valid_image_is_checked_before_photo_publish(self):
        calls, state = self.run_publisher("/ar/ai/example/", with_image=True)
        self.assertEqual(calls[1].full_url, "https://mikhbar.website/forum/assets/posts/story/social.jpg")
        self.assertTrue(calls[-1].full_url.endswith("/123/photos"))
        self.assertEqual(state["last_success"]["publish_mode"], "photo")

    def test_manual_run_rejects_invalid_image(self):
        with self.assertRaisesRegex(RuntimeError, "social image"):
            self.run_publisher("/ar/ai/example/", with_image=True, image_ready=False)

    def test_automatic_trigger_waits_for_site_deployment(self):
        workflow = (ROOT / ".github/workflows/mikhbar-social.yml").read_text()
        self.assertIn("workflows: ['Mikhbar Cloudflare Deploy']", workflow)
        self.assertNotIn("workflows: ['Mikhbar 20-Minute Publisher']", workflow)

    def test_external_article_url_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "outside the Mikhbar"):
            self.run_publisher("https://example.net/ar/ai/story/")


if __name__ == "__main__":
    unittest.main()
