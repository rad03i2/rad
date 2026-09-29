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
    def run_publisher(self, article_url, *, duplicate=False, wrong_page=False):
        workflow = (ROOT / ".github/workflows/mikhbar-social.yml").read_text()
        code = textwrap.dedent(
            workflow.split("python - <<'PY'\n", 1)[1].split("\n          PY", 1)[0]
        )
        calls = []

        def urlopen_stub(req, timeout):
            calls.append(req)
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

    def test_external_article_url_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "outside the Mikhbar"):
            self.run_publisher("https://example.net/ar/ai/story/")


if __name__ == "__main__":
    unittest.main()
