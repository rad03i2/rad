from __future__ import annotations

import copy
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import Any
from urllib.parse import urljoin

import feedparser
import requests
from bs4 import BeautifulSoup

from common import CONFIG, STATE, canonicalize_url, domain_of, load_json, now_iso, parse_date, save_json, strip_html
from request_budget import RequestBudgetExceeded, bounded_requests, request_timeout
from trend import is_current_story


def _feed_entries(response, source: dict) -> list:
    if source.get("format") == "intel-newsroom":
        soup = BeautifulSoup(response.text, "html.parser")
        entries = []
        for card in soup.select(".cmp-teaser__link"):
            title = card.select_one(".cmp-teaser__title")
            date = card.select_one(".cmp-teaser__description")
            url = urljoin(response.url, card.get("href", ""))
            published = parse_date(date.get_text(" ", strip=True)) if date else None
            if title and published and domain_of(url) == "intel.com" and "/newsroom/news/" in url:
                entries.append(feedparser.FeedParserDict(title=title.get_text(" ", strip=True), link=url, published=published))
        if not entries:
            raise RuntimeError("Intel newsroom did not contain dated news cards")
        return entries
    feed = feedparser.parse(response.content)
    if not getattr(feed, "version", "") and not getattr(feed, "entries", None):
        raise RuntimeError("Expected RSS/Atom; source returned a non-feed page")
    return list(getattr(feed, "entries", []))


def _retry_delay(response, failures: int, now: datetime) -> int:
    delay = min(3600, 300 * 2 ** min(failures - 1, 4))
    if response is not None and response.status_code == 429:
        delay = max(delay, 600)
        value = response.headers.get("Retry-After", "")
        try:
            delay = max(delay, int(value))
        except ValueError:
            try:
                delay = max(delay, int((parsedate_to_datetime(value) - now).total_seconds()))
            except (TypeError, ValueError, OverflowError):
                pass
    return min(86400, delay)


def _entry_link(entry: Any) -> str:
    link = getattr(entry, "link", "") or ""
    if link:
        return canonicalize_url(link)
    for item in getattr(entry, "links", []) or []:
        href = item.get("href") if isinstance(item, dict) else ""
        if href:
            return canonicalize_url(href)
    return ""


def collect(settings: dict) -> tuple[list[dict], dict]:
    with bounded_requests(180):
        return _collect_with_budget(settings)


def _collect_with_budget(settings: dict) -> tuple[list[dict], dict]:
    sources = load_json(CONFIG / "sources.json", {"sources": []})["sources"]
    cache_path = STATE / "feed_cache.json"
    cache_document = load_json(cache_path, {"sources": {}})
    cache = cache_document.get("sources", {})
    resume_source = cache_document.get("resume_source")
    start = next((index for index, source in enumerate(sources) if source["url"] == resume_source), 0)
    ordered_sources = sources[start:] + sources[:start]
    next_resume = None
    max_per_source = int(settings.get("maxItemsPerSource", 30))
    ua = settings.get("userAgent", "RDWAN-Tech-Collector/0.1")
    timeout = 20
    stories: list[dict] = []
    report = {"sources_ok": 0, "sources_failed": 0, "sources_cached": 0, "fetched": 0, "errors": []}

    session = requests.Session()
    session.headers.update({"User-Agent": ua, "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*"})

    for source in ordered_sources:
        now = datetime.now(timezone.utc)
        cached = cache.get(source["url"], {})
        response = None
        deferred = False
        try:
            retry_at = cached.get("retry_at")
            if retry_at and datetime.fromisoformat(retry_at) > now:
                deferred = True
                raise RuntimeError("Source retry deferred after an upstream failure")
            response = session.get(source["url"], timeout=request_timeout(timeout), allow_redirects=True)
            response.raise_for_status()
            entries = _feed_entries(response, source)

            report["sources_ok"] += 1
            source_stories = []
            old_discovered = {item.get("url"): item.get("discovered_at") for item in cached.get("stories", [])}
            for entry in entries[:max_per_source]:
                title = strip_html(getattr(entry, "title", ""))
                url = _entry_link(entry)
                if not title or not url:
                    continue

                summary = strip_html(
                    getattr(entry, "summary", "")
                    or getattr(entry, "description", "")
                    or ""
                )
                published = (
                    getattr(entry, "published", None)
                    or getattr(entry, "updated", None)
                    or getattr(entry, "created", None)
                )
                published_at = parse_date(published)

                source_stories.append({
                    "title": title,
                    "url": url,
                    "domain": domain_of(url),
                    "summary": summary[:1200],
                    "published_at": published_at,
                    "discovered_at": old_discovered.get(url) or now_iso(),
                    "source": {
                        "name": source["name"],
                        "feed": source["url"],
                        "type": source.get("type", "journalism"),
                        "trust": float(source.get("trust", 0.7)),
                        "priority": int(source.get("priority", 10)),
                        "defaultCategory": source.get("defaultCategory", "apps")
                    }
                })
            stories.extend(source_stories)
            report["fetched"] += len(source_stories)
            cache[source["url"]] = {
                "last_success_at": now_iso(),
                "stories": [item for item in source_stories if is_current_story(item, settings)],
            }
        except Exception as exc:
            report["sources_failed"] += 1
            report["errors"].append({"source": source.get("name", source.get("url")), "error": str(exc)[:300]})
            recovered = [copy.deepcopy(item) for item in cached.get("stories", []) if is_current_story(item, settings)]
            if recovered:
                stories.extend(recovered)
                report["sources_cached"] += 1
                report["fetched"] += len(recovered)
            if isinstance(exc, RequestBudgetExceeded) and next_resume is None:
                next_resume = source["url"]
            if not isinstance(exc, RequestBudgetExceeded) and not deferred:
                failures = int(cached.get("failures", 0)) + 1
                cache[source["url"]] = {
                    **cached, "failures": failures,
                    "retry_at": (now + timedelta(seconds=_retry_delay(response, failures, now))).isoformat(),
                }

    session.close()
    save_json(cache_path, {
        "sources": {source["url"]: cache[source["url"]] for source in sources if source["url"] in cache},
        "resume_source": next_resume,
    })
    return stories, report
