from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import feedparser
import requests

from common import CONFIG, canonicalize_url, domain_of, now_iso, parse_date, strip_html


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
    sources = __import__("json").loads((CONFIG / "sources.json").read_text(encoding="utf-8"))["sources"]
    max_per_source = int(settings.get("maxItemsPerSource", 30))
    ua = settings.get("userAgent", "RDWAN-Tech-Collector/0.1")
    timeout = 20
    stories: list[dict] = []
    report = {"sources_ok": 0, "sources_failed": 0, "fetched": 0, "errors": []}

    session = requests.Session()
    session.headers.update({"User-Agent": ua, "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*"})

    for source in sources:
        try:
            response = session.get(source["url"], timeout=timeout, allow_redirects=True)
            response.raise_for_status()
            feed = feedparser.parse(response.content)
            if getattr(feed, "bozo", False) and not getattr(feed, "entries", None):
                raise RuntimeError(f"feed parse error: {getattr(feed, 'bozo_exception', 'unknown')}")

            report["sources_ok"] += 1
            for entry in list(getattr(feed, "entries", []))[:max_per_source]:
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

                stories.append({
                    "title": title,
                    "url": url,
                    "domain": domain_of(url),
                    "summary": summary[:1200],
                    "published_at": published_at,
                    "discovered_at": now_iso(),
                    "source": {
                        "name": source["name"],
                        "feed": source["url"],
                        "type": source.get("type", "journalism"),
                        "trust": float(source.get("trust", 0.7)),
                        "priority": int(source.get("priority", 10)),
                        "defaultCategory": source.get("defaultCategory", "apps")
                    }
                })
                report["fetched"] += 1
        except Exception as exc:
            report["sources_failed"] += 1
            report["errors"].append({"source": source.get("name", source.get("url")), "error": str(exc)[:300]})

    return stories, report
