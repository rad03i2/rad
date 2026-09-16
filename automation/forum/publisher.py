from __future__ import annotations

import json
import math
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from common import CONFIG, STATE, load_json, now_iso, save_json
from indexes import write_all
from renderer import render_to_file
from trend import rank_candidates
from writer import build_source_pack, write_article

ROOT = Path(__file__).resolve().parents[2]
FORUM = ROOT / "forum"
CONTENT = FORUM / "content"
TZ = timezone(timedelta(hours=3))
AR_MONTHS = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def _arabic_date(dt: datetime) -> str:
    local = dt.astimezone(TZ)
    return f"{local.day} {AR_MONTHS[local.month - 1]} {local.year}"


def _slugify(title: str, fallback: str) -> str:
    text = (title or "").lower()
    text = re.sub(r"[^a-z0-9\s-]", " ", text)
    words = [word for word in text.split() if len(word) > 1][:11]
    slug = re.sub(r"-+", "-", "-".join(words)).strip("-")
    return slug[:88] if slug else f"story-{fallback[:12]}"


def _word_count(article: dict) -> int:
    parts = [str(article.get("deck", ""))]
    parts.extend(str(x) for x in article.get("summary_bullets", []))
    for section in article.get("sections", []):
        parts.append(str(section.get("heading", "")))
        parts.extend(str(x) for x in section.get("paragraphs", []))
    return len(re.findall(r"\S+", " ".join(parts)))


def _quality_gate(story: dict, sources: list[dict], article: dict) -> tuple[bool, list[str]]:
    errors: list[str] = []
    title = str(article.get("title", "")).strip()
    description = str(article.get("description", "")).strip()
    bullets = article.get("summary_bullets", [])
    sections = article.get("sections", [])
    words = _word_count(article)

    if len(title) < 25 or len(title) > 120:
        errors.append("title_length")
    if len(description) < 80 or len(description) > 190:
        errors.append("description_length")
    if not isinstance(bullets, list) or len(bullets) < 3:
        errors.append("summary_bullets")
    if not isinstance(sections, list) or len(sections) < 4:
        errors.append("sections")
    if words < 480:
        errors.append("article_too_short")
    if any(not isinstance(section, dict) or not section.get("heading") or not section.get("paragraphs") for section in sections):
        errors.append("malformed_sections")

    usable = [source for source in sources if source.get("ok") and (source.get("text") or source.get("feed_summary"))]
    primary_official = story.get("source", {}).get("type") == "official"
    if primary_official and len(usable) < 1:
        errors.append("missing_primary_source")
    if not primary_official and len(usable) < 2:
        errors.append("journalism_requires_two_sources")

    forbidden = ["كمساعد", "لا أستطيع التحقق", "حسب معلوماتي", "مصدر غير متاح"]
    joined = json.dumps(article, ensure_ascii=False)
    if any(phrase in joined for phrase in forbidden):
        errors.append("model_meta_language")
    return not errors, errors


def _clean_sources(source_pack: list[dict]) -> list[dict]:
    result = []
    seen = set()
    for source in source_pack:
        url = str(source.get("url") or "").strip()
        if not url or url in seen:
            continue
        seen.add(url)
        result.append({
            "name": source.get("name") or source.get("domain") or "المصدر",
            "url": url,
            "type": source.get("kind") or source.get("type") or "source",
            "title": source.get("feed_title") or source.get("title") or "",
        })
    return result


def _make_content_record(story: dict, article: dict, source_pack: list[dict], slug: str, now: datetime, read_minutes: int) -> dict:
    category_slug = story.get("category", "apps")
    category_label = story.get("category_label", category_slug)
    return {
        "schemaVersion": 1,
        "template": "article",
        "id": story.get("id"),
        "slug": slug,
        "url": f"/forum/{category_slug}/{slug}/",
        "category": category_label,
        "categorySlug": category_slug,
        "title": str(article.get("title", "")).strip(),
        "description": str(article.get("description", "")).strip(),
        "deck": str(article.get("deck", "")).strip(),
        "summaryBullets": [str(x).strip() for x in article.get("summary_bullets", []) if str(x).strip()],
        "sections": article.get("sections", []),
        "tags": [str(x).strip() for x in article.get("tags", []) if str(x).strip()][:8],
        "entities": [str(x).strip() for x in article.get("entities", []) if str(x).strip()][:12],
        "datePublished": now.isoformat(),
        "dateModified": now.isoformat(),
        "dateLabel": _arabic_date(now),
        "modifiedLabel": _arabic_date(now),
        "readMinutes": read_minutes,
        "image": "https://rdwan.dev/assets/social/home.jpg",
        "author": {
            "name": "رضوان عبدالهادي",
            "url": "/forum/authors/radwan-abdulhadi/",
        },
        "sources": _clean_sources(source_pack),
        "sourceUrl": story.get("url"),
        "sourceTitle": story.get("title"),
        "trendScore": round(float(story.get("trend", {}).get("score", 0)), 2),
        "verification": {
            "confidence": story.get("verification", {}).get("confidence"),
            "reason": story.get("verification", {}).get("reason"),
            "official": story.get("verification", {}).get("official", False),
        },
        "generation": {
            "createdAt": now_iso(),
            "mode": "automated",
            "contentSource": "structured-json",
        },
    }


def _post_from_record(record: dict, story: dict) -> dict:
    trend_score = float(record.get("trendScore", 0))
    age_hours = float(story.get("trend", {}).get("age_hours", 999))
    return {
        "id": record["id"],
        "title": record["title"],
        "slug": record["slug"],
        "url": record["url"],
        "category": record["category"],
        "categorySlug": record["categorySlug"],
        "date": record["datePublished"],
        "dateModified": record["dateModified"],
        "dateLabel": record["dateLabel"],
        "excerpt": record["description"],
        "tags": record.get("tags", []),
        "featured": trend_score >= 105,
        "breaking": trend_score >= 120 and age_hours <= 3,
        "readTime": f"{record['readMinutes']} دقائق",
        "author": record["author"],
        "sourceUrl": record.get("sourceUrl"),
        "trendScore": trend_score,
        "contentFile": record.get("contentFile"),
    }


def _save_report(status: str, **extra) -> None:
    save_json(STATE / "publisher_report.json", {"status": status, "at": now_iso(), **extra})


def main() -> int:
    settings = load_json(CONFIG / "settings.json", {})
    if not settings.get("publishingEnabled", False) or settings.get("dryRun", False):
        _save_report("publishing_disabled")
        print("Hourly publisher: publishing is disabled.")
        return 0

    posts_doc = load_json(FORUM / "posts.json", {"posts": []})
    posts = list(posts_doc.get("posts", []))
    queue_doc = load_json(STATE / "queue.json", {"items": []})
    queue = list(queue_doc.get("items", []))
    history = load_json(STATE / "published.json", {"last_published_at": None, "items": []})

    now = datetime.now(TZ)
    last = _parse_dt(history.get("last_published_at"))
    minimum_gap = int(settings.get("minimumMinutesBetweenPosts", 55))
    if last and (now.astimezone(timezone.utc) - last.astimezone(timezone.utc)).total_seconds() < minimum_gap * 60:
        _save_report("cooldown", last_published_at=history.get("last_published_at"))
        print("Hourly publisher: cooldown active; no post published.")
        return 0

    published_urls = {item.get("source_url") for item in history.get("items", []) if item.get("source_url")}
    published_ids = {item.get("story_id") for item in history.get("items", []) if item.get("story_id")}
    queue = [item for item in queue if item.get("url") not in published_urls and item.get("id") not in published_ids and item.get("status") != "published"]
    ranked = rank_candidates(queue, settings, posts)
    if not ranked:
        _save_report("no_candidate")
        print("Hourly publisher: no eligible trend candidate.")
        return 0

    story = ranked[0]
    source_pack = build_source_pack(story, settings)
    article = write_article(story, source_pack, settings)
    ok, errors = _quality_gate(story, source_pack, article)
    if not ok:
        _save_report("quality_rejected", story=story.get("title"), errors=errors)
        raise RuntimeError("Quality gate rejected generated article: " + ", ".join(errors))

    words = _word_count(article)
    read_minutes = max(3, math.ceil(words / 190))
    slug = _slugify(story.get("title", ""), story.get("id", "story"))
    category_slug = story.get("category", "apps")

    existing_urls = {post.get("url") for post in posts}
    candidate_url = f"/forum/{category_slug}/{slug}/"
    if candidate_url in existing_urls:
        slug = f"{slug}-{str(story.get('id', ''))[:6]}"

    record = _make_content_record(story, article, source_pack, slug, now, read_minutes)
    content_path = CONTENT / f"{now.year:04d}" / f"{now.month:02d}" / f"{slug}.json"
    record["contentFile"] = content_path.relative_to(ROOT).as_posix()
    save_json(content_path, record)

    rendered_path = render_to_file(record)
    post = _post_from_record(record, story)
    posts = [p for p in posts if p.get("id") != post["id"] and p.get("url") != post["url"]]
    posts.insert(0, post)
    posts.sort(key=lambda p: p.get("date") or "", reverse=True)
    save_json(FORUM / "posts.json", {"posts": posts})
    write_all(posts, now)

    for item in queue_doc.get("items", []):
        if item.get("id") == story.get("id"):
            item["status"] = "published"
            item["published_url"] = record["url"]
            item["content_file"] = record["contentFile"]
    queue_doc["updated_at"] = now_iso()
    save_json(STATE / "queue.json", queue_doc)

    history_items = list(history.get("items", []))
    history_items.insert(0, {
        "story_id": story.get("id"),
        "source_url": story.get("url"),
        "published_url": record["url"],
        "content_file": record["contentFile"],
        "published_at": now.isoformat(),
        "trend_score": record["trendScore"],
        "category": category_slug,
        "title": record["title"],
    })
    save_json(STATE / "published.json", {
        "last_published_at": now.isoformat(),
        "items": history_items[:1000],
    })

    _save_report(
        "published",
        story_id=story.get("id"),
        source_url=story.get("url"),
        published_url=record["url"],
        content_file=record["contentFile"],
        rendered_file=rendered_path.relative_to(ROOT).as_posix(),
        title=record["title"],
        category=category_slug,
        trend_score=record["trendScore"],
        word_count=words,
        read_minutes=read_minutes,
        source_count=len(record["sources"]),
        template="forum/templates/article.html",
    )
    print(f"Published: {record['url']} from {record['contentFile']} ({words} words)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
