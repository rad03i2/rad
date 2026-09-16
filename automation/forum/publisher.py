from __future__ import annotations

import json
import math
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from common import CONFIG, STATE, load_json, now_iso, save_json
from image_pipeline import prepare_images
from indexes import write_all
from renderer import render_to_files
from trend import rank_candidates
from writer import build_source_pack, write_article

ROOT = Path(__file__).resolve().parents[2]
FORUM = ROOT / "forum"
CONTENT = FORUM / "content"
TZ = timezone(timedelta(hours=3))
AR_MONTHS = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
EN_MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
AR_CATEGORIES = {
    "ai": "الذكاء الاصطناعي", "robotics": "الروبوتات", "automation": "الأتمتة", "mobile": "الهواتف",
    "computers": "الحواسيب", "apps": "التطبيقات والبرامج", "web": "الويب", "social": "التواصل الاجتماعي",
    "security": "الأمن التقني", "announcements": "إعلانات المنصة",
}
EN_CATEGORIES = {
    "ai": "Artificial Intelligence", "robotics": "Robotics", "automation": "Automation", "mobile": "Mobile",
    "computers": "Computing", "apps": "Apps & Software", "web": "Web", "social": "Social Media",
    "security": "Cybersecurity", "announcements": "Announcements",
}


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def _date_label(dt: datetime, locale: str) -> str:
    local = dt.astimezone(TZ)
    if locale == "ar":
        return f"{local.day} {AR_MONTHS[local.month - 1]} {local.year}"
    return f"{EN_MONTHS[local.month - 1]} {local.day}, {local.year}"


def _slugify(title: str, fallback: str) -> str:
    text = (title or "").lower()
    text = re.sub(r"[^a-z0-9\s-]", " ", text)
    words = [word for word in text.split() if len(word) > 1][:12]
    slug = re.sub(r"-+", "-", "-".join(words)).strip("-")
    return slug[:92] if slug else f"story-{fallback[:12]}"


def _word_count(article: dict) -> int:
    parts = [str(article.get("deck", ""))]
    parts.extend(str(x) for x in article.get("summary_bullets", []))
    for section in article.get("sections", []):
        parts.append(str(section.get("heading", "")))
        parts.extend(str(x) for x in section.get("paragraphs", []))
    return len(re.findall(r"\S+", " ".join(parts)))


def _quality_gate_locale(locale: str, article: dict) -> list[str]:
    errors = []
    title = str(article.get("title", "")).strip()
    description = str(article.get("description", "")).strip()
    bullets = article.get("summary_bullets", [])
    sections = article.get("sections", [])
    words = _word_count(article)
    if len(title) < 25 or len(title) > 125:
        errors.append(f"{locale}:title_length")
    if len(description) < 80 or len(description) > 195:
        errors.append(f"{locale}:description_length")
    if not isinstance(bullets, list) or len(bullets) < 3:
        errors.append(f"{locale}:summary_bullets")
    if not isinstance(sections, list) or len(sections) < 4:
        errors.append(f"{locale}:sections")
    if words < 450:
        errors.append(f"{locale}:article_too_short")
    if any(not isinstance(section, dict) or not section.get("heading") or not section.get("paragraphs") for section in sections):
        errors.append(f"{locale}:malformed_sections")
    forbidden = ["كمساعد", "لا أستطيع التحقق", "حسب معلوماتي", "as an ai", "i cannot verify", "i can't verify"]
    joined = json.dumps(article, ensure_ascii=False).lower()
    if any(phrase in joined for phrase in forbidden):
        errors.append(f"{locale}:model_meta_language")
    return errors


def _quality_gate(story: dict, sources: list[dict], editions: dict) -> tuple[bool, list[str]]:
    errors = []
    for locale in ("ar", "en"):
        article = editions.get(locale)
        if not isinstance(article, dict):
            errors.append(f"{locale}:missing_edition")
            continue
        errors.extend(_quality_gate_locale(locale, article))

    usable = [source for source in sources if source.get("ok") and (source.get("text") or source.get("feed_summary"))]
    primary_official = story.get("source", {}).get("type") == "official"
    if primary_official and len(usable) < 1:
        errors.append("missing_primary_source")
    if not primary_official and len(usable) < 2:
        errors.append("journalism_requires_two_sources")
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
            "name": source.get("name") or source.get("domain") or "Source",
            "url": url,
            "type": source.get("kind") or source.get("type") or "source",
            "title": source.get("feed_title") or source.get("title") or "",
        })
    return result


def _locale_record(article: dict, locale: str, category_slug: str, now: datetime) -> dict:
    words = _word_count(article)
    read_minutes = max(3, math.ceil(words / (190 if locale == "ar" else 220)))
    return {
        "title": str(article.get("title", "")).strip(),
        "description": str(article.get("description", "")).strip(),
        "deck": str(article.get("deck", "")).strip(),
        "summaryBullets": [str(x).strip() for x in article.get("summary_bullets", []) if str(x).strip()],
        "sections": article.get("sections", []),
        "tags": [str(x).strip() for x in article.get("tags", []) if str(x).strip()][:8],
        "entities": [str(x).strip() for x in article.get("entities", []) if str(x).strip()][:12],
        "category": (AR_CATEGORIES if locale == "ar" else EN_CATEGORIES).get(category_slug, category_slug),
        "dateLabel": _date_label(now, locale),
        "modifiedLabel": _date_label(now, locale),
        "readMinutes": read_minutes,
        "wordCount": words,
    }


def _make_content_record(story: dict, editions: dict, source_pack: list[dict], slug: str, now: datetime, images: dict) -> dict:
    category_slug = story.get("category", "apps")
    ar = _locale_record(editions["ar"], "ar", category_slug, now)
    en = _locale_record(editions["en"], "en", category_slug, now)
    return {
        "schemaVersion": 2,
        "template": "article",
        "id": story.get("id"),
        "slug": slug,
        "categorySlug": category_slug,
        "urls": {
            "ar": f"/forum/ar/{category_slug}/{slug}/",
            "en": f"/forum/en/{category_slug}/{slug}/",
        },
        "locales": {"ar": ar, "en": en},
        "datePublished": now.isoformat(),
        "dateModified": now.isoformat(),
        "images": images,
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
            "mode": "automated-bilingual",
            "contentSource": "structured-json",
            "languages": ["ar", "en"],
        },
    }


def _post_from_record(record: dict, locale: str, story: dict) -> dict:
    view = record["locales"][locale]
    trend_score = float(record.get("trendScore", 0))
    age_hours = float(story.get("trend", {}).get("age_hours", 999))
    url = record["urls"][locale]
    other = "en" if locale == "ar" else "ar"
    return {
        "id": record["id"],
        "locale": locale,
        "title": view["title"],
        "slug": record["slug"],
        "url": url,
        "category": view["category"],
        "categorySlug": record["categorySlug"],
        "date": record["datePublished"],
        "dateModified": record["dateModified"],
        "dateLabel": view["dateLabel"],
        "excerpt": view["description"],
        "tags": view.get("tags", []),
        "featured": trend_score >= 105,
        "breaking": trend_score >= 120 and age_hours <= 3,
        "readTime": f"{view['readMinutes']} دقائق" if locale == "ar" else f"{view['readMinutes']} min",
        "author": {"name": "رضوان عبدالهادي" if locale == "ar" else "Radwan Abdulhadi", "url": "/forum/authors/radwan-abdulhadi/"},
        "sourceUrl": record.get("sourceUrl"),
        "trendScore": trend_score,
        "contentFile": record.get("contentFile"),
        "image": record["images"].get("card"),
        "images": record["images"],
        "alternates": {"ar": record["urls"]["ar"], "en": record["urls"]["en"], other: record["urls"][other]},
    }


def _save_report(status: str, **extra) -> None:
    save_json(STATE / "publisher_report.json", {"status": status, "at": now_iso(), **extra})


def _load_posts() -> dict[str, list[dict]]:
    ar_doc = load_json(FORUM / "posts-ar.json", None)
    if not ar_doc:
        ar_doc = load_json(FORUM / "posts.json", {"posts": []})
    en_doc = load_json(FORUM / "posts-en.json", {"posts": []})
    return {"ar": list((ar_doc or {}).get("posts", [])), "en": list((en_doc or {}).get("posts", []))}


def main() -> int:
    settings = load_json(CONFIG / "settings.json", {})
    if not settings.get("publishingEnabled", False) or settings.get("dryRun", False):
        _save_report("publishing_disabled")
        print("Hourly publisher: publishing is disabled.")
        return 0

    posts_by_locale = _load_posts()
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
    ranked = rank_candidates(queue, settings, posts_by_locale["ar"])
    if not ranked:
        _save_report("no_candidate")
        print("Hourly publisher: no eligible trend candidate.")
        return 0

    story = ranked[0]
    source_pack = build_source_pack(story, settings)
    editions = write_article(story, source_pack, settings)
    ok, errors = _quality_gate(story, source_pack, editions)
    if not ok:
        _save_report("quality_rejected", story=story.get("title"), errors=errors)
        raise RuntimeError("Quality gate rejected generated article: " + ", ".join(errors))

    slug = _slugify(story.get("title", ""), story.get("id", "story"))
    category_slug = story.get("category", "apps")
    used_urls = {p.get("url") for posts in posts_by_locale.values() for p in posts}
    if f"/forum/ar/{category_slug}/{slug}/" in used_urls or f"/forum/en/{category_slug}/{slug}/" in used_urls:
        slug = f"{slug}-{str(story.get('id', ''))[:6]}"

    images = prepare_images(
        story, source_pack, slug, now.year, now.month,
        str(editions["ar"].get("title", "")), str(editions["en"].get("title", "")), settings,
    )
    record = _make_content_record(story, editions, source_pack, slug, now, images)
    content_path = CONTENT / f"{now.year:04d}" / f"{now.month:02d}" / f"{slug}.json"
    record["contentFile"] = content_path.relative_to(ROOT).as_posix()
    save_json(content_path, record)

    rendered = render_to_files(record)
    for locale in ("ar", "en"):
        post = _post_from_record(record, locale, story)
        posts = [p for p in posts_by_locale[locale] if p.get("id") != post["id"] and p.get("url") != post["url"]]
        posts.insert(0, post)
        posts.sort(key=lambda p: p.get("date") or "", reverse=True)
        posts_by_locale[locale] = posts

    save_json(FORUM / "posts-ar.json", {"posts": posts_by_locale["ar"]})
    save_json(FORUM / "posts-en.json", {"posts": posts_by_locale["en"]})
    save_json(FORUM / "posts.json", {"posts": posts_by_locale["ar"]})
    write_all(posts_by_locale, now)

    for item in queue_doc.get("items", []):
        if item.get("id") == story.get("id"):
            item["status"] = "published"
            item["published_url"] = record["urls"]["ar"]
            item["published_urls"] = record["urls"]
            item["content_file"] = record["contentFile"]
    queue_doc["updated_at"] = now_iso()
    save_json(STATE / "queue.json", queue_doc)

    history_items = list(history.get("items", []))
    history_items.insert(0, {
        "story_id": story.get("id"), "source_url": story.get("url"), "published_url": record["urls"]["ar"],
        "published_urls": record["urls"], "content_file": record["contentFile"], "published_at": now.isoformat(),
        "trend_score": record["trendScore"], "category": category_slug, "title": record["locales"]["ar"]["title"],
    })
    save_json(STATE / "published.json", {"last_published_at": now.isoformat(), "items": history_items[:1000]})

    _save_report(
        "published", story_id=story.get("id"), source_url=story.get("url"), published_urls=record["urls"],
        content_file=record["contentFile"], rendered_files={k: v.relative_to(ROOT).as_posix() for k, v in rendered.items()},
        title_ar=record["locales"]["ar"]["title"], title_en=record["locales"]["en"]["title"], category=category_slug,
        trend_score=record["trendScore"], word_count_ar=record["locales"]["ar"]["wordCount"],
        word_count_en=record["locales"]["en"]["wordCount"], source_count=len(record["sources"]),
        image_source=record["images"].get("sourceUrl"), image_fallback=record["images"].get("generatedFallback"),
        template="forum/templates/article.html",
    )
    print(f"Published bilingual story: {record['urls']['ar']} + {record['urls']['en']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
