from __future__ import annotations

from datetime import datetime, timezone

from common import canonicalize_url, normalize_title, stable_id
from trend import is_current_story


def candidate_retry_due(item: dict) -> bool:
    try:
        retry_at = datetime.fromisoformat(str(item.get("publisher_retry_at") or "").replace("Z", "+00:00"))
        if retry_at.tzinfo is None:
            retry_at = retry_at.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) >= retry_at
    except ValueError:
        return True


def pending_queue(items: list[dict], history: dict, settings: dict) -> list[dict]:
    """Reserve queue capacity for current, unpublished stories only."""
    published_urls = {canonicalize_url(item.get("source_url", "")) for item in history.get("items", [])}
    published_ids = {item.get("story_id") for item in history.get("items", []) if item.get("story_id")}
    return [
        item for item in items
        if item.get("status") not in {"published", "quality_rejected"}
        and canonicalize_url(item.get("url", "")) not in published_urls
        and item.get("id") not in published_ids
        and is_current_story(item, settings)
    ]


def reconcile_seen(seen: dict, retained: list[dict], history: dict, previous_items: list[dict]) -> dict:
    """A discovery is durable only when retained, published, or quality-rejected.

    Older collectors marked stories seen before truncating the queue. Releasing
    those orphan entries lets the next feed collection recover them, without
    republishing articles or retrying drafts that failed the quality gate.
    """
    rejected = dict(seen.get("rejected_urls", {}))
    for item in previous_items:
        if item.get("status") == "quality_rejected" and item.get("url"):
            url = canonicalize_url(item["url"])
            rejected[url] = item.get("id") or stable_id(url)

    published = dict(seen.get("published_urls", {}))
    for item in history.get("items", []):
        if item.get("source_url"):
            url = canonicalize_url(item["source_url"])
            published[url] = item.get("story_id") or stable_id(url)
    for item in previous_items:
        if item.get("status") == "published" and item.get("url"):
            url = canonicalize_url(item["url"])
            published[url] = item.get("id") or stable_id(url)
    urls = {**rejected, **published}
    for item in retained:
        if item.get("url"):
            url = canonicalize_url(item["url"])
            urls[url] = item.get("id") or stable_id(url)

    return {
        **seen,
        "urls": urls,
        "titles": {normalize_title(item["title"]): item.get("id") for item in retained if item.get("title")},
        "rejected_urls": rejected,
        "published_urls": published,
    }


def limit_queue(items: list[dict], settings: dict, prepared: dict) -> list[dict]:
    prepared_id = (prepared.get("story") or {}).get("id") if prepared.get("status") == "ready" else None
    items.sort(key=lambda item: (
        bool(prepared_id and item.get("id") == prepared_id),
        item.get("score", 0),
        item.get("published_at") or item.get("discovered_at") or "",
    ), reverse=True)
    return items[:max(1, int(settings.get("maxQueueItems", 500)))]
