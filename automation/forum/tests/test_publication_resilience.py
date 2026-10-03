from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import collector
import publication_deployment as deployment
import publisher
import publisher_scheduler as scheduler
import request_budget as budget
import writer
from common import save_json
from deduplicator import deduplicate
from queue_lifecycle import candidate_retry_due, reconcile_seen


class RequestAndWriterTests(unittest.TestCase):
    def setUp(self):
        writer._unavailable_until.clear()

    def tearDown(self):
        writer._unavailable_until.clear()

    def test_nested_budget_cannot_extend_outer_deadline_and_recovers_after_exit(self):
        with patch.object(budget.time, "monotonic", return_value=100) as clock:
            with budget.bounded_requests(10):
                self.assertEqual(budget.request_timeout(180), 10)
                with budget.bounded_requests(60):
                    clock.return_value = 111
                    with self.assertRaises(budget.RequestBudgetExceeded):
                        budget.request_timeout(180)
            self.assertEqual(budget.request_timeout(180), 180)

    def test_quota_error_is_not_retried_for_every_draft(self):
        response = SimpleNamespace(status_code=429, text="quota exceeded")
        with patch.object(writer.requests, "post", return_value=response) as post:
            for _ in range(3):
                with self.assertRaises(RuntimeError):
                    writer._call_openai_compatible("prompt", "test", "https://api.example", "model", "Provider")
            self.assertEqual(post.call_count, 1)

    def test_gemini_service_failure_moves_to_next_model(self):
        bad = SimpleNamespace(status_code=503, text="temporary service failure")
        good = Mock(status_code=200)
        good.json.return_value = {"status": "completed", "steps": [{"type": "model_output", "content": [{"type": "text", "text": '{"title":"Working model"}'}]}]}
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test"}), patch.object(writer.requests, "post", side_effect=[bad, good]) as post:
            result = writer._call_gemini("prompt", ["failed", "healthy"])
            self.assertEqual(result["title"], "Working model")
            self.assertEqual(post.call_count, 2)

    def test_provider_timeout_does_not_consume_the_next_providers_budget(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": "test", "GEMINI_API_KEY": "test"}), \
             patch.object(writer, "_call_groq", side_effect=budget.RequestBudgetExceeded("slow provider")), \
             patch.object(writer, "_call_gemini", return_value={"title": "Fallback succeeded"}):
            with budget.bounded_requests(600):
                self.assertEqual(writer._call_model("prompt", {})["title"], "Fallback succeeded")

    def test_exhausted_budget_stops_draft_retries(self):
        write = Mock(side_effect=budget.RequestBudgetExceeded("exhausted"))
        editions, _, attempts, status = publisher._generate_qualified_editions({}, [], {"publisherDraftAttempts": 3}, write)
        self.assertIsNone(editions)
        self.assertEqual(status, "generation_error")
        self.assertEqual(len(attempts), 1)
        write.assert_called_once()

    def test_json_with_trailing_text_or_duplicate_object_can_be_recovered(self):
        self.assertEqual(writer._extract_json('```json\n{"title":"Valid"}\n```\nExtra explanation'), {"title": "Valid"})
        self.assertEqual(writer._extract_json('{"title":"First"}\n{"title":"Second"}'), {"title": "First"})
        with self.assertRaises(ValueError):
            writer._extract_json('["not an article"]')


class CollectorRecoveryTests(unittest.TestCase):
    def test_sources_skipped_by_the_budget_are_first_in_the_next_cycle(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sources = [{"name": str(index), "url": f"https://source.example/{index}"} for index in range(3)]
            save_json(root / "config/sources.json", {"sources": sources})
            good = Mock(status_code=200, headers={})
            good.content = b'<rss version="2.0"><channel><title>News</title></channel></rss>'
            session = Mock()
            session.get.return_value = good
            with patch.object(collector, "CONFIG", root / "config"), patch.object(collector, "STATE", root / "state"), patch.object(collector.requests, "Session", return_value=session):
                with patch.object(collector, "request_timeout", side_effect=[20, budget.RequestBudgetExceeded("spent"), budget.RequestBudgetExceeded("spent")]):
                    collector.collect({})
                session.get.reset_mock()
                collector.collect({})
                self.assertEqual([call.args[0] for call in session.get.call_args_list], [sources[1]["url"], sources[2]["url"], sources[0]["url"]])
                self.assertIsNone(json.loads((root / "state/feed_cache.json").read_text())["resume_source"])

    def test_intel_migrated_page_requires_real_dated_article_cards(self):
        html = '''<a class="cmp-teaser__link" href="/content/www/us/en/newsroom/news/real.html"><h2 class="cmp-teaser__title">Real announcement</h2><div class="cmp-teaser__description">October 2,2026</div></a>
        <a class="cmp-teaser__link" href="/content/www/us/en/newsroom/news/undated.html"><h2 class="cmp-teaser__title">Undated feature</h2></a>'''
        response = SimpleNamespace(text=html, url="https://www.intel.com/content/www/us/en/newsroom/home.html")
        entries = collector._feed_entries(response, {"format": "intel-newsroom"})
        self.assertEqual([entry.title for entry in entries], ["Real announcement"])
        self.assertTrue(entries[0].published.startswith("2026-10-02"))

    def test_rate_limit_preserves_recent_feed_and_respects_retry_after(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config, state = root / "config", root / "state"
            save_json(config / "sources.json", {"sources": [{"name": "Source", "url": "https://source.example/feed", "type": "official"}]})
            date = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
            good = Mock(status_code=200, headers={}, url="https://source.example/feed")
            good.content = f'<rss version="2.0"><channel><title>News</title><item><title>Fresh announcement</title><link>https://source.example/story</link><pubDate>{date}</pubDate></item></channel></rss>'.encode()
            bad = Mock(status_code=429, headers={"Retry-After": "3600"})
            bad.raise_for_status.side_effect = RuntimeError("HTTP 429")
            session = Mock()
            session.get.side_effect = [good, bad]
            with patch.object(collector, "CONFIG", config), patch.object(collector, "STATE", state), patch.object(collector.requests, "Session", return_value=session):
                first, _ = collector.collect({"maxAgeHours": 72, "trendWindowHours": 72})
                recovered, report = collector.collect({"maxAgeHours": 72, "trendWindowHours": 72})
                deferred, _ = collector.collect({"maxAgeHours": 72, "trendWindowHours": 72})
                self.assertEqual(recovered, first)
                self.assertEqual(deferred, first)
                self.assertEqual(report["sources_cached"], 1)
                self.assertEqual(session.get.call_count, 2)
                cached = json.loads((state / "feed_cache.json").read_text())["sources"]["https://source.example/feed"]
                retry = datetime.fromisoformat(cached["retry_at"])
                self.assertGreater((retry - datetime.now(timezone.utc)).total_seconds(), 3500)

    def test_stale_cached_news_is_never_relabelled_as_fresh(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            save_json(root / "config/sources.json", {"sources": [{"name": "Source", "url": "https://source.example/feed"}]})
            old = {"title": "Old", "url": "https://source.example/old", "published_at": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat()}
            save_json(root / "state/feed_cache.json", {"sources": {"https://source.example/feed": {"stories": [old]}}})
            session = Mock()
            session.get.side_effect = RuntimeError("temporarily unavailable")
            with patch.object(collector, "CONFIG", root / "config"), patch.object(collector, "STATE", root / "state"), patch.object(collector.requests, "Session", return_value=session):
                stories, report = collector.collect({"maxAgeHours": 72, "trendWindowHours": 72})
            self.assertEqual(stories, [])
            self.assertEqual(report["sources_cached"], 0)


class QueueRetryTests(unittest.TestCase):
    def test_unreadable_high_ranked_story_cannot_starve_other_news(self):
        bad = {"id": "bad", "url": "https://example.com/bad", "status": "incoming"}
        good = {"id": "good", "url": "https://example.com/good", "status": "incoming"}
        queue = {"items": [bad, good]}
        publisher._mark_candidate_result(queue, bad, "source_error", ["unreadable"], [])
        self.assertEqual([item["id"] for item in scheduler._eligible_queue(queue, {})], ["good"])
        self.assertEqual(bad["status"], "incoming")
        bad["publisher_retry_at"] = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
        self.assertTrue(candidate_retry_due(bad))

    def test_publication_deduplication_survives_history_truncation(self):
        history = {"items": [{"source_url": "https://example.com/published", "story_id": "old"}]}
        seen = reconcile_seen({}, [], history, [])
        seen = reconcile_seen(seen, [], {"items": []}, [])
        fresh, duplicates, _ = deduplicate([{"title": "Updated feed title", "url": "https://example.com/published"}], [], seen, .9)
        self.assertEqual(fresh, [])
        self.assertEqual(duplicates, 1)


class DeploymentRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.date = "2026-10-03T10:21:56+03:00"
        self.local = {locale: [{"id": "new", "date": self.date, "title": f"Article {locale}", "url": f"/forum/{locale}/ai/new/", "contentFile": "forum/content/new.json"}] for locale in ("ar", "en")}

    def fetch(self, path):
        if path.startswith("/posts-"):
            locale = "en" if "en" in path else "ar"
            return json.dumps({"posts": self.local[locale]})
        if path.endswith(".json"):
            return json.dumps({"id": "new", "datePublished": self.date})
        locale = path.split("/")[1]
        return f'<link rel="canonical" href="https://mikhbar.website{path}"><meta property="article:published_time" content="{self.date}"><body data-ssr-rendered="true"><h1 id="article-title">Article {locale}</h1></body>'

    def test_latest_bilingual_article_is_verified(self):
        self.assertEqual(deployment.verify_latest(self.local, self.fetch), "new")

    def test_old_working_site_cannot_pass_a_new_publication_verification(self):
        def fetch(path):
            if path == "/posts-ar.json":
                return '{"posts":[{"id":"old"}]}'
            return self.fetch(path)
        with self.assertRaisesRegex(RuntimeError, "live index"):
            deployment.verify_latest(self.local, fetch)

    def test_missing_english_ssr_is_detected(self):
        def fetch(path):
            return '<body>Loading</body>' if path.startswith("/en/") else self.fetch(path)
        with self.assertRaisesRegex(RuntimeError, "en article"):
            deployment.verify_latest(self.local, fetch)

    def test_failed_dispatch_is_retried_without_losing_indexnow(self):
        with patch.object(deployment.subprocess, "run", side_effect=[subprocess.CalledProcessError(1, ["gh"]), None, None]) as run, patch.object(deployment.time, "sleep"):
            deployment.dispatch()
            self.assertEqual(run.call_count, 3)
            self.assertIn("deploy-mikhbar-cloudflare.yml", run.call_args_list[1].args[0])
            self.assertIn("indexnow.yml", run.call_args_list[2].args[0])

    def test_production_without_credentials_fails_and_preview_keeps_build_only_mode(self):
        path = Path(__file__).resolve().parents[3] / ".github/workflows/deploy-mikhbar-cloudflare.yml"
        block = path.read_text().split("- name: Deploy Worker and static assets when Cloudflare credentials exist", 1)[1].split("- name: Verify live production", 1)[0]
        script = block.split("run: |", 1)[1]
        script = "\n".join(line[10:] for line in script.splitlines())
        for target, expected in [("production", 1), ("preview", 0)]:
            result = subprocess.run(["bash", "-c", script], env={"PATH": os.environ["PATH"], "DEPLOY_TARGET": target}, capture_output=True, text=True)
            self.assertEqual(result.returncode, expected, result.stderr)


if __name__ == "__main__":
    unittest.main()
