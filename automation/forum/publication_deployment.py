"""Dispatch publication jobs safely and verify the newest live editions."""
from __future__ import annotations

import argparse
import json
import subprocess
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

from request_budget import RequestBudgetExceeded, bounded_requests, request_timeout

ORIGIN = "https://mikhbar.website"
FORUM = Path(__file__).resolve().parents[2] / "forum"


def dispatch() -> None:
    for workflow, extra in [("deploy-mikhbar-cloudflare.yml", ["-f", "target=production"]), ("indexnow.yml", [])]:
        for attempt in range(3):
            try:
                subprocess.run(["gh", "workflow", "run", workflow, "--ref", "main", *extra], check=True, timeout=30)
                break
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                if attempt == 2:
                    raise
                time.sleep(3 * (attempt + 1))


def fetch_text(path: str) -> str:
    request = Request(ORIGIN + path, headers={"Cache-Control": "no-cache", "User-Agent": "Mikhbar-Publication-Verification/1.0"})
    with urlopen(request, timeout=request_timeout(20)) as response:
        return response.read().decode("utf-8")


def public_path(path: str) -> str:
    return path[len("/forum"):] if path.startswith("/forum/") else path


def posts(doc) -> list[dict]:
    return doc if isinstance(doc, list) else doc.get("posts", [])


class ArticleMetadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonical = None
        self.published_at = None
        self.ssr = False
        self.headline = ""
        self.in_headline = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "body":
            self.ssr = attrs.get("data-ssr-rendered") == "true"
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href")
        if tag == "meta" and attrs.get("property") == "article:published_time":
            self.published_at = attrs.get("content")
        if tag == "h1" and attrs.get("id") == "article-title":
            self.in_headline = True

    def handle_endtag(self, tag):
        if tag == "h1":
            self.in_headline = False

    def handle_data(self, data):
        if self.in_headline:
            self.headline += data


def verify_latest(local: dict[str, list[dict]], fetch=fetch_text) -> str:
    if not local.get("ar") or not local.get("en"):
        raise RuntimeError("Local bilingual publication indexes are empty")
    latest = max(local["ar"], key=lambda post: post.get("date", ""))
    story_id = latest["id"]
    for locale in ("ar", "en"):
        expected = next((post for post in local[locale] if post.get("id") == story_id), None)
        if expected is None:
            raise RuntimeError(f"Newest article is missing its {locale} edition")
        live = posts(json.loads(fetch(f"/posts-{locale}.json")))
        actual = next((post for post in live if post.get("id") == story_id), None)
        if actual is None or actual.get("date") != expected.get("date"):
            raise RuntimeError(f"Newest {locale} article has not reached the live index")
        content_path = public_path("/" + str(expected["contentFile"]).lstrip("/"))
        record = json.loads(fetch(content_path))
        if record.get("id") != story_id or record.get("datePublished") != expected.get("date"):
            raise RuntimeError(f"Live structured record differs from the newest {locale} article")
        route = public_path(expected["url"])
        metadata = ArticleMetadata()
        metadata.feed(fetch(route))
        if not metadata.ssr or metadata.canonical != ORIGIN + route or metadata.published_at != expected.get("date") or metadata.headline.strip() != expected.get("title", "").strip():
            raise RuntimeError(f"Newest {locale} article did not render correctly on production")
    return story_id


def verify_production() -> None:
    local = {locale: posts(json.loads((FORUM / f"posts-{locale}.json").read_text(encoding="utf-8"))) for locale in ("ar", "en")}
    with bounded_requests(90):
        for attempt in range(6):
            try:
                story_id = verify_latest(local)
                print(f"Newest Arabic and English publication verified on production: {story_id}")
                return
            except RequestBudgetExceeded:
                raise
            except Exception:
                if attempt == 5:
                    raise
                delay = min(5, request_timeout(5))
                time.sleep(delay)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=["dispatch", "verify"])
    operation = parser.parse_args().operation
    dispatch() if operation == "dispatch" else verify_production()
