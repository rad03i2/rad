from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from common import load_json, save_json
from image_pipeline import prepare_images
from indexes import write_all
from publisher import AR_CATEGORIES, EN_CATEGORIES
from renderer import render_to_files
from writer import _write_locale, build_source_pack

ROOT = Path(__file__).resolve().parents[2]
FORUM = ROOT / "forum"
CONTENT = FORUM / "content"
CONFIG = Path(__file__).resolve().parent / "config"


def _dt(value: str) -> datetime:
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        return datetime.now(timezone.utc)


def _read_minutes(article: dict, divisor: int) -> int:
    words = []
    words.append(str(article.get("deck", "")))
    for item in article.get("summaryBullets", article.get("summary_bullets", [])):
        words.append(str(item))
    for section in article.get("sections", []):
        words.append(str(section.get("heading", "")))
        words.extend(str(x) for x in section.get("paragraphs", []))
    count = len(" ".join(words).split())
    return max(3, (count + divisor - 1) // divisor)


def _post(record: dict, locale: str) -> dict:
    view = record["locales"][locale]
    return {
        "id": record["id"], "locale": locale, "title": view["title"], "slug": record["slug"],
        "url": record["urls"][locale], "category": view["category"], "categorySlug": record["categorySlug"],
        "date": record["datePublished"], "dateModified": record["dateModified"], "dateLabel": view["dateLabel"],
        "excerpt": view["description"], "tags": view.get("tags", []), "featured": True, "breaking": False,
        "readTime": f"{view['readMinutes']} دقائق" if locale == "ar" else f"{view['readMinutes']} min",
        "author": {"name": "رضوان عبدالهادي" if locale == "ar" else "Radwan Abdulhadi", "url": "/forum/authors/radwan-abdulhadi/"},
        "sourceUrl": record.get("sourceUrl"), "trendScore": record.get("trendScore", 0),
        "contentFile": record.get("contentFile"), "image": record["images"]["card"], "images": record["images"],
        "alternates": record["urls"],
    }


def main() -> int:
    settings = load_json(CONFIG / "settings.json", {})
    files = sorted(CONTENT.rglob("*.json")) if CONTENT.exists() else []
    migrated = 0
    for path in files:
        old = load_json(path, {})
        if not old or old.get("schemaVersion", 1) >= 2 or not old.get("title"):
            continue

        source = (old.get("sources") or [{}])[0]
        story = {
            "id": old.get("id"), "title": old.get("sourceTitle") or source.get("title") or old.get("title"),
            "url": old.get("sourceUrl") or source.get("url"), "category": old.get("categorySlug", "apps"),
            "category_label": old.get("category") or AR_CATEGORIES.get(old.get("categorySlug"), "تقنية"),
            "published_at": old.get("datePublished"),
            "source": {"name": source.get("name", "Primary source"), "type": source.get("type", "official")},
            "verification": {"confidence": (old.get("verification") or {}).get("confidence", 1.0), "official": source.get("type") == "official"},
            "trend": {"score": old.get("trendScore", 100), "age_hours": 999},
        }
        source_pack = build_source_pack(story, settings)
        usable = [s for s in source_pack if s.get("ok") and (s.get("text") or s.get("feed_summary"))]
        if not usable:
            print(f"Skip migration without source text: {path}")
            continue
        en = _write_locale(story, usable, "en")
        published = _dt(old.get("datePublished", ""))
        slug = old["slug"]
        images = prepare_images(story, source_pack, slug, published.year, published.month, old["title"], en["title"], settings)
        category_slug = old["categorySlug"]

        ar = {
            "title": old["title"], "description": old.get("description", ""), "deck": old.get("deck", ""),
            "summaryBullets": old.get("summaryBullets", []), "sections": old.get("sections", []),
            "tags": old.get("tags", []), "entities": old.get("entities", []),
            "category": old.get("category") or AR_CATEGORIES.get(category_slug, category_slug),
            "dateLabel": old.get("dateLabel", ""), "modifiedLabel": old.get("modifiedLabel", old.get("dateLabel", "")),
            "readMinutes": old.get("readMinutes") or _read_minutes(old, 190),
        }
        en_view = {
            "title": en["title"], "description": en["description"], "deck": en["deck"],
            "summaryBullets": en.get("summary_bullets", []), "sections": en.get("sections", []),
            "tags": en.get("tags", []), "entities": en.get("entities", []),
            "category": EN_CATEGORIES.get(category_slug, category_slug),
            "dateLabel": published.strftime("%B %d, %Y").replace(" 0", " "),
            "modifiedLabel": published.strftime("%B %d, %Y").replace(" 0", " "),
            "readMinutes": _read_minutes({"deck": en["deck"], "summaryBullets": en.get("summary_bullets", []), "sections": en.get("sections", [])}, 220),
        }
        record = {
            "schemaVersion": 2, "template": "article", "id": old["id"], "slug": slug, "categorySlug": category_slug,
            "urls": {"ar": f"/forum/ar/{category_slug}/{slug}/", "en": f"/forum/en/{category_slug}/{slug}/"},
            "locales": {"ar": ar, "en": en_view}, "datePublished": old["datePublished"],
            "dateModified": old.get("dateModified", old["datePublished"]), "images": images,
            "sources": old.get("sources", []), "sourceUrl": old.get("sourceUrl"), "sourceTitle": old.get("sourceTitle"),
            "trendScore": old.get("trendScore", 0), "verification": old.get("verification", {}),
            "contentFile": path.relative_to(ROOT).as_posix(),
            "generation": {"mode": "migrated-bilingual", "contentSource": "structured-json", "languages": ["ar", "en"]},
        }
        save_json(path, record)
        render_to_files(record)

        ar_doc = load_json(FORUM / "posts-ar.json", load_json(FORUM / "posts.json", {"posts": []}))
        en_doc = load_json(FORUM / "posts-en.json", {"posts": []})
        ar_posts = [p for p in ar_doc.get("posts", []) if p.get("id") != record["id"]]
        en_posts = [p for p in en_doc.get("posts", []) if p.get("id") != record["id"]]
        ar_posts.insert(0, _post(record, "ar")); en_posts.insert(0, _post(record, "en"))
        ar_posts.sort(key=lambda p: p.get("date") or "", reverse=True); en_posts.sort(key=lambda p: p.get("date") or "", reverse=True)
        save_json(FORUM / "posts-ar.json", {"posts": ar_posts})
        save_json(FORUM / "posts-en.json", {"posts": en_posts})
        save_json(FORUM / "posts.json", {"posts": ar_posts})
        write_all({"ar": ar_posts, "en": en_posts}, datetime.now(published.tzinfo or timezone.utc))
        migrated += 1

    print(f"RDWAN Tech legacy migration: migrated={migrated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
