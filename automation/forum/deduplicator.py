from __future__ import annotations

from common import canonicalize_url, jaccard_title, normalize_title, stable_id


def deduplicate(stories: list[dict], queue_items: list[dict], seen: dict, threshold: float) -> tuple[list[dict], int, dict]:
    existing_by_url = {canonicalize_url(item.get("url", "")): item for item in queue_items if item.get("url")}
    existing_titles = [(item, item.get("title", "")) for item in queue_items]
    seen_urls = seen.setdefault("urls", {})
    seen_titles = seen.setdefault("titles", {})

    fresh: list[dict] = []
    duplicates = 0

    for story in stories:
        url = canonicalize_url(story.get("url", ""))
        title = story.get("title", "")
        norm_title = normalize_title(title)

        if url in seen_urls or url in existing_by_url:
            duplicates += 1
            continue

        duplicate_item = None
        best_similarity = 0.0
        for item, old_title in existing_titles:
            sim = jaccard_title(title, old_title)
            if sim > best_similarity:
                best_similarity = sim
                duplicate_item = item
            if sim >= threshold:
                break

        if duplicate_item is not None and best_similarity >= threshold:
            duplicates += 1
            source_name = story.get("source", {}).get("name")
            verification = duplicate_item.setdefault("verification", {})
            corroborating = verification.setdefault("corroborating_sources", [])
            if source_name and source_name != duplicate_item.get("source", {}).get("name") and source_name not in corroborating:
                corroborating.append(source_name)
                verification["confidence"] = round(min(0.99, float(verification.get("confidence", 0.7)) + 0.04), 3)
            continue

        story["id"] = stable_id(url, title)
        fresh.append(story)
        existing_by_url[url] = story
        existing_titles.append((story, title))
        seen_urls[url] = story["id"]
        if norm_title:
            seen_titles[norm_title] = story["id"]

    return fresh, duplicates, seen
