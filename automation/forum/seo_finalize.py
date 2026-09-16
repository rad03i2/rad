from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORUM = ROOT / "forum"
SITE = "https://rdwan.dev"
CATEGORIES = ("ai", "robotics", "automation", "mobile", "computers", "apps", "web", "social", "security", "announcements")
TRUST_PAGES = (
    ("/forum/about/", "about/index.html", "0.7"),
    ("/forum/editorial-policy/", "editorial-policy/index.html", "0.7"),
    ("/forum/corrections/", "corrections/index.html", "0.6"),
    ("/forum/ai-policy/", "ai-policy/index.html", "0.6"),
    ("/forum/authors/radwan-abdulhadi/", "authors/radwan-abdulhadi/index.html", "0.8"),
)
INDEX_ROBOTS = "index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1"
NOINDEX_ROBOTS = "noindex,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1"
RELATED_START = "<!-- SEO_RELATED_START -->"
RELATED_END = "<!-- SEO_RELATED_END -->"
PERSON_PUBLISHER = '"publisher":{"@type":"Person","name":"Radwan Abdulhadi","url":"https://rdwan.dev/"}'
ORG_PUBLISHER = (
    '"publisher":{"@type":"NewsMediaOrganization","@id":"https://rdwan.dev/forum/#publisher",'
    '"name":"RDWAN Tech","url":"https://rdwan.dev/forum/",'
    '"logo":{"@type":"ImageObject","url":"https://rdwan.dev/assets/images/radwan-favicon.png"},'
    '"founder":{"@type":"Person","name":"Radwan Abdulhadi",'
    '"url":"https://rdwan.dev/forum/authors/radwan-abdulhadi/"}}'
)


def _load_posts(locale: str) -> list[dict]:
    path = FORUM / f"posts-{locale}.json"
    if locale == "ar" and not path.exists():
        path = FORUM / "posts.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        posts = list(value if isinstance(value, list) else value.get("posts", []))
        return sorted(posts, key=lambda p: str(p.get("date") or ""), reverse=True)
    except Exception:
        return []


def _set_robots(path: Path, indexable: bool) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    desired = INDEX_ROBOTS if indexable else NOINDEX_ROBOTS
    updated = re.sub(
        r'<meta\s+name=["\']robots["\']\s+content=["\'][^"\']*["\']\s*/?>',
        f'<meta name="robots" content="{desired}">',
        text,
        count=1,
        flags=re.I,
    )
    if updated == text and "<head>" in text:
        updated = text.replace("<head>", f'<head><meta name="robots" content="{desired}">', 1)
    if updated != text:
        path.write_text(updated, encoding="utf-8")
        return True
    return False


def _fix_router_language() -> bool:
    path = FORUM / "index.html"
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    updated = re.sub(r'<html(?:\s+[^>]*)?>', '<html lang="en" dir="ltr">', text, count=1, flags=re.I)
    if updated != text:
        path.write_text(updated, encoding="utf-8")
        return True
    return False


def _prune_empty_categories(active: dict[str, set[str]]) -> int:
    path = FORUM / "sitemap.xml"
    if not path.exists():
        return 0
    text = path.read_text(encoding="utf-8")
    removed = 0
    pattern = re.compile(r'\s*<url>.*?<loc>https://rdwan\.dev/forum/(ar|en)/([a-z-]+)/</loc>.*?</url>\s*', re.S)

    def repl(match: re.Match[str]) -> str:
        nonlocal removed
        locale, slug = match.group(1), match.group(2)
        if slug in CATEGORIES and slug not in active.get(locale, set()):
            removed += 1
            return "\n"
        return match.group(0)

    updated = pattern.sub(repl, text)
    if updated != text:
        path.write_text(updated, encoding="utf-8")
    return removed


def _ensure_trust_pages() -> int:
    path = FORUM / "sitemap.xml"
    if not path.exists():
        return 0
    text = path.read_text(encoding="utf-8")
    stamp = datetime.now(timezone.utc).date().isoformat()
    additions: list[str] = []
    for url_path, file_path, priority in TRUST_PAGES:
        if not (FORUM / file_path).exists():
            continue
        absolute = SITE + url_path
        if f"<loc>{absolute}</loc>" in text:
            continue
        additions.append(
            f'  <url><loc>{absolute}</loc><lastmod>{stamp}</lastmod>'
            f'<changefreq>monthly</changefreq><priority>{priority}</priority></url>'
        )
    if additions and "</urlset>" in text:
        text = text.replace("</urlset>", "\n".join(additions) + "\n</urlset>", 1)
        path.write_text(text, encoding="utf-8")
    return len(additions)


def _tag_set(post: dict) -> set[str]:
    return {str(tag).strip().casefold() for tag in (post.get("tags") or []) if str(tag).strip()}


def _related_posts(current: dict, posts: list[dict], limit: int = 3) -> list[dict]:
    current_url = str(current.get("url") or "")
    current_id = str(current.get("id") or "")
    current_category = str(current.get("categorySlug") or "")
    current_tags = _tag_set(current)
    ranked: list[tuple[int, int, dict]] = []
    for index, candidate in enumerate(posts):
        if str(candidate.get("url") or "") == current_url or (current_id and str(candidate.get("id") or "") == current_id):
            continue
        if candidate.get("categorySlug") == "announcements" and current_category != "announcements":
            continue
        tags = _tag_set(candidate)
        overlap = len(current_tags & tags)
        same_category = str(candidate.get("categorySlug") or "") == current_category
        score = (10 if same_category else 0) + overlap * 3
        ranked.append((score, -index, candidate))
    ranked.sort(key=lambda row: (row[0], row[1]), reverse=True)
    return [row[2] for row in ranked[:limit]]


def _article_path(post: dict, locale: str) -> Path | None:
    url = str(post.get("url") or "")
    prefix = f"/forum/{locale}/"
    if not url.startswith(prefix):
        return None
    relative = url.removeprefix("/forum/").strip("/")
    return FORUM / relative / "index.html"


def _related_card(post: dict) -> str:
    url = escape(str(post.get("url") or "#"), quote=True)
    title_raw = str(post.get("title") or "")
    title = escape(title_raw)
    excerpt = escape(str(post.get("excerpt") or ""))
    category = escape(str(post.get("category") or "Technology"))
    date = escape(str(post.get("dateLabel") or ""))
    image = str(post.get("image") or (post.get("images") or {}).get("card") or "/assets/social/home.jpg")
    return (
        f'<a class="rt-feed-item" href="{url}">'
        f'<div class="rt-feed-copy"><div class="rt-feed-kicker"><span>{category}</span></div>'
        f'<h3>{title}</h3><p>{excerpt}</p><div class="rt-feed-time">{date}</div></div>'
        f'<div class="rt-thumb"><img src="{escape(image, quote=True)}" alt="{escape(title_raw, quote=True)}" '
        f'width="800" height="450" loading="lazy" decoding="async"></div></a>'
    )


def _related_block(locale: str, related: list[dict]) -> str:
    if not related:
        return ""
    heading = "أخبار مرتبطة" if locale == "ar" else "Related stories"
    description = "مواضيع أخرى مرتبطة قد تهمك." if locale == "ar" else "More coverage related to this story."
    cards = "".join(_related_card(post) for post in related)
    return (
        f'\n{RELATED_START}\n'
        f'<section class="rt-article-shell rt-related" aria-label="{escape(heading, quote=True)}">'
        f'<header class="rt-section-head"><div><h2>{escape(heading)}</h2><p>{escape(description)}</p></div></header>'
        f'<div class="rt-feed">{cards}</div></section>'
        f'\n{RELATED_END}\n'
    )


def _optimize_article_pages(posts_by_locale: dict[str, list[dict]]) -> tuple[int, int]:
    pages_changed = 0
    schema_changed = 0
    marker = re.compile(re.escape(RELATED_START) + r".*?" + re.escape(RELATED_END), re.S)
    for locale, posts in posts_by_locale.items():
        for post in posts:
            path = _article_path(post, locale)
            if not path or not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            upgraded = text.replace(PERSON_PUBLISHER, ORG_PUBLISHER)
            if upgraded != text:
                schema_changed += 1
            cleaned = marker.sub("", upgraded)
            related = _related_posts(post, posts)
            block = _related_block(locale, related)
            if block and "</article>" in cleaned:
                updated = cleaned.replace("</article>", "</article>" + block, 1)
            else:
                updated = cleaned
            if updated != text:
                path.write_text(updated, encoding="utf-8")
                pages_changed += 1
    return pages_changed, schema_changed


def main() -> int:
    posts = {locale: _load_posts(locale) for locale in ("ar", "en")}
    active = {
        locale: {str(post.get("categorySlug")) for post in items if post.get("categorySlug")}
        for locale, items in posts.items()
    }

    changed_pages = 0
    for locale in ("ar", "en"):
        for slug in CATEGORIES:
            page = FORUM / locale / slug / "index.html"
            if _set_robots(page, slug in active[locale]):
                changed_pages += 1

    router_changed = _fix_router_language()
    removed = _prune_empty_categories(active)
    trust_added = _ensure_trust_pages()
    article_pages_changed, schema_changed = _optimize_article_pages(posts)
    print(
        "SEO finalize: "
        f"category_pages_changed={changed_pages} "
        f"empty_category_sitemap_entries_removed={removed} "
        f"trust_pages_added={trust_added} "
        f"article_pages_changed={article_pages_changed} "
        f"publisher_schema_upgraded={schema_changed} "
        f"router_lang_fixed={router_changed} "
        f"active_ar={sorted(active['ar'])} active_en={sorted(active['en'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
