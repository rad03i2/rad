from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORUM = ROOT / "forum"
SITE = "https://rdwan.dev"
CATEGORIES = ("ai", "robotics", "automation", "mobile", "computers", "apps", "web", "social", "security", "announcements")
INDEX_ROBOTS = "index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1"
NOINDEX_ROBOTS = "noindex,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1"


def _load_posts(locale: str) -> list[dict]:
    path = FORUM / f"posts-{locale}.json"
    if locale == "ar" and not path.exists():
        path = FORUM / "posts.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return list(value if isinstance(value, list) else value.get("posts", []))
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
    print(
        "SEO finalize: "
        f"category_pages_changed={changed_pages} "
        f"empty_category_sitemap_entries_removed={removed} "
        f"router_lang_fixed={router_changed} "
        f"active_ar={sorted(active['ar'])} active_en={sorted(active['en'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
