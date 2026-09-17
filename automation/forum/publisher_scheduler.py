from __future__ import annotations

from datetime import datetime, timedelta, timezone

import publisher
from common import CONFIG, STATE, load_json, now_iso, save_json

PREPARED_PATH = STATE / "prepared_article.json"


def _elapsed_seconds(last: datetime | None, now: datetime) -> float:
    if last is None:
        return float("inf")
    return (now.astimezone(timezone.utc) - last.astimezone(timezone.utc)).total_seconds()


def _is_due(last: datetime | None, now: datetime, minimum_gap_minutes: int) -> bool:
    return _elapsed_seconds(last, now) >= minimum_gap_minutes * 60


def _target_publish_at(last: datetime | None, now: datetime, minimum_gap_minutes: int) -> datetime:
    if last is None:
        return now
    return last.astimezone(publisher.TZ) + timedelta(minutes=minimum_gap_minutes)


def _published_sets(history: dict) -> tuple[set[str], set[str]]:
    urls = {item.get("source_url") for item in history.get("items", []) if item.get("source_url")}
    ids = {item.get("story_id") for item in history.get("items", []) if item.get("story_id")}
    return urls, ids


def _eligible_queue(queue_doc: dict, history: dict) -> list[dict]:
    published_urls, published_ids = _published_sets(history)
    terminal_statuses = {"published", "quality_rejected"}
    return [
        item for item in queue_doc.get("items", [])
        if item.get("url") not in published_urls
        and item.get("id") not in published_ids
        and item.get("status") not in terminal_statuses
    ]


def _prepared_is_valid(prepared: dict, queue_doc: dict, history: dict, settings: dict, now: datetime) -> bool:
    if not isinstance(prepared, dict) or prepared.get("status") != "ready":
        return False
    story = prepared.get("story")
    editions = prepared.get("editions")
    if not isinstance(story, dict) or not story.get("id") or not story.get("url"):
        return False
    if not isinstance(editions, dict) or not isinstance(editions.get("ar"), dict) or not isinstance(editions.get("en"), dict):
        return False
    if not isinstance(prepared.get("source_pack"), list) or not isinstance(prepared.get("images"), dict):
        return False

    published_urls, published_ids = _published_sets(history)
    if story.get("url") in published_urls or story.get("id") in published_ids:
        return False

    queue_ids = {
        item.get("id") for item in queue_doc.get("items", [])
        if item.get("status") not in {"published", "quality_rejected"}
    }
    if story.get("id") not in queue_ids:
        return False

    prepared_at = publisher._parse_dt(prepared.get("prepared_at"))
    max_age_minutes = int(settings.get("preparedDraftMaxAgeMinutes", 60))
    if prepared_at and _elapsed_seconds(prepared_at, now) > max_age_minutes * 60:
        return False
    return True


def _choose_slug(story: dict, posts_by_locale: dict[str, list[dict]]) -> str:
    slug = publisher._slugify(story.get("title", ""), story.get("id", "story"))
    category_slug = story.get("category", "apps")
    used_urls = {post.get("url") for posts in posts_by_locale.values() for post in posts}
    if f"/forum/ar/{category_slug}/{slug}/" in used_urls or f"/forum/en/{category_slug}/{slug}/" in used_urls:
        slug = f"{slug}-{str(story.get('id', ''))[:6]}"
    return slug


def _prepare_next(settings: dict, queue_doc: dict, history: dict, now: datetime, target: datetime) -> dict | None:
    posts_by_locale = publisher._load_posts()
    queue = _eligible_queue(queue_doc, history)
    ranked = publisher.rank_candidates(queue, settings, posts_by_locale["ar"])
    if not ranked:
        publisher._save_report("no_candidate_to_prepare")
        print("20-minute pipeline: no eligible candidate available for preparation.")
        return None

    max_candidates = publisher._bounded_int(settings, "publisherCandidateAttempts", 3, 1, 5)
    candidate_reports: list[dict] = []

    for candidate_rank, candidate in enumerate(ranked[:max_candidates], 1):
        try:
            source_pack = publisher.build_source_pack(candidate, settings)
        except Exception as exc:
            report = {
                "rank": candidate_rank,
                "story_id": candidate.get("id"),
                "title": candidate.get("title"),
                "status": "source_error",
                "errors": [f"{type(exc).__name__}: {exc}"],
                "attempts": [],
            }
            candidate_reports.append(report)
            publisher._mark_candidate_result(queue_doc, candidate, "source_error", report["errors"], [])
            continue

        editions, errors, attempts, status = publisher._generate_qualified_editions(candidate, source_pack, settings)
        report = {
            "rank": candidate_rank,
            "story_id": candidate.get("id"),
            "title": candidate.get("title"),
            "status": status,
            "errors": errors,
            "attempts": attempts,
        }
        candidate_reports.append(report)

        if editions is None:
            publisher._mark_candidate_result(queue_doc, candidate, status, errors, attempts)
            continue

        slug = _choose_slug(candidate, posts_by_locale)
        images = publisher.prepare_images(
            candidate,
            source_pack,
            slug,
            target.astimezone(publisher.TZ).year,
            target.astimezone(publisher.TZ).month,
            str(editions["ar"].get("title", "")),
            str(editions["en"].get("title", "")),
            settings,
        )

        prepared = {
            "status": "ready",
            "prepared_at": now_iso(),
            "target_publish_at": target.isoformat(),
            "story": candidate,
            "source_pack": source_pack,
            "editions": editions,
            "selected_attempts": attempts,
            "candidate_reports": candidate_reports,
            "slug": slug,
            "images": images,
        }
        save_json(PREPARED_PATH, prepared)

        for item in queue_doc.get("items", []):
            if item.get("id") == candidate.get("id"):
                item["last_publisher_status"] = "prepared"
                item["last_publisher_at"] = now_iso()
                item["publisher_attempts"] = attempts
                break
        queue_doc["updated_at"] = now_iso()
        save_json(STATE / "queue.json", queue_doc)

        publisher._save_report(
            "prepared",
            story_id=candidate.get("id"),
            source_url=candidate.get("url"),
            target_publish_at=target.isoformat(),
            title_ar=editions["ar"].get("title"),
            title_en=editions["en"].get("title"),
            candidates_considered=candidate_reports,
        )
        print(f"20-minute pipeline: prepared next story for {target.isoformat()}.")
        return prepared

    queue_doc["updated_at"] = now_iso()
    save_json(STATE / "queue.json", queue_doc)
    publisher._save_report("no_publishable_candidate_to_prepare", candidates=candidate_reports)
    print("20-minute pipeline: preparation completed but no candidate passed the quality gate.")
    return None


def _publish_prepared(prepared: dict) -> int:
    story = prepared["story"]
    source_pack = prepared["source_pack"]
    editions = prepared["editions"]
    attempts = prepared.get("selected_attempts", [])
    slug = prepared["slug"]
    images = prepared["images"]

    original_rank = publisher.rank_candidates
    original_build_sources = publisher.build_source_pack
    original_generate = publisher._generate_qualified_editions
    original_slugify = publisher._slugify
    original_prepare_images = publisher.prepare_images

    def prepared_rank(_queue, _settings, _posts):
        return [story]

    def prepared_sources(candidate, settings):
        if candidate.get("id") == story.get("id"):
            return source_pack
        return original_build_sources(candidate, settings)

    def prepared_editions(candidate, candidate_sources, settings, writer_fn=publisher.write_article):
        if candidate.get("id") == story.get("id"):
            return editions, [], attempts, "passed"
        return original_generate(candidate, candidate_sources, settings, writer_fn)

    def prepared_slugify(_title, _fallback):
        return slug

    def prepared_images(*_args, **_kwargs):
        return images

    publisher.rank_candidates = prepared_rank
    publisher.build_source_pack = prepared_sources
    publisher._generate_qualified_editions = prepared_editions
    publisher._slugify = prepared_slugify
    publisher.prepare_images = prepared_images
    try:
        result = publisher.main()
    finally:
        publisher.rank_candidates = original_rank
        publisher.build_source_pack = original_build_sources
        publisher._generate_qualified_editions = original_generate
        publisher._slugify = original_slugify
        publisher.prepare_images = original_prepare_images

    history = load_json(STATE / "published.json", {"items": []})
    latest = (history.get("items") or [{}])[0]
    if latest.get("story_id") == story.get("id"):
        save_json(PREPARED_PATH, {
            "status": "empty",
            "cleared_at": now_iso(),
            "last_published_story_id": story.get("id"),
        })
        print("20-minute pipeline: prepared story published successfully and slot cleared.")
    else:
        print("20-minute pipeline: publish returned without confirming the prepared story; keeping it for recovery.")
    return result


def main() -> int:
    settings = load_json(CONFIG / "settings.json", {})
    if not settings.get("publishingEnabled", False) or settings.get("dryRun", False):
        publisher._save_report("publishing_disabled")
        return 0

    now = datetime.now(publisher.TZ)
    history = load_json(STATE / "published.json", {"last_published_at": None, "items": []})
    queue_doc = load_json(STATE / "queue.json", {"items": []})
    last = publisher._parse_dt(history.get("last_published_at"))
    minimum_gap = int(settings.get("minimumMinutesBetweenPosts", 20))
    target = _target_publish_at(last, now, minimum_gap)
    due = _is_due(last, now, minimum_gap)

    prepared = load_json(PREPARED_PATH, {})
    if not _prepared_is_valid(prepared, queue_doc, history, settings, now):
        if prepared:
            save_json(PREPARED_PATH, {"status": "empty", "cleared_at": now_iso(), "reason": "invalid_or_stale"})
        prepared = _prepare_next(settings, queue_doc, history, now, target)

    if not due:
        if prepared:
            remaining = max(0, int((target.astimezone(timezone.utc) - now.astimezone(timezone.utc)).total_seconds()))
            print(f"20-minute pipeline: next story is ready; publication due in about {remaining} seconds.")
        return 0

    if not prepared:
        print("20-minute pipeline: publication is due, but no quality-approved prepared story is available.")
        return 0

    return _publish_prepared(prepared)


if __name__ == "__main__":
    raise SystemExit(main())
