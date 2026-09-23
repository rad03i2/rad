from __future__ import annotations

import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
FORUM = ROOT / "forum"
LOCALES = ("ar", "en")
CATEGORIES = {"ai", "robotics", "automation", "mobile", "computers", "apps", "web", "social", "security", "announcements"}
ROUTE_RE = re.compile(r"^/forum/(ar|en)/([a-z0-9-]+)/([a-z0-9-]+)/$")


def load_posts(locale: str) -> list[dict]:
    path = FORUM / f"posts-{locale}.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    posts = payload.get("posts", []) if isinstance(payload, dict) else payload
    if not isinstance(posts, list):
        raise ValueError(f"{path.name}: posts must be a list")
    return posts


def valid_http_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False


def normalized_title(value: str) -> str:
    return " ".join(str(value or "").casefold().split())


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    by_locale = {locale: load_posts(locale) for locale in LOCALES}
    all_posts = [post for locale in LOCALES for post in by_locale[locale]]

    urls: list[str] = []
    titles_by_locale: dict[str, list[str]] = {locale: [] for locale in LOCALES}
    route_sets = {locale: {str(p.get("url") or "") for p in by_locale[locale]} for locale in LOCALES}

    for locale, posts in by_locale.items():
        for index, post in enumerate(posts, start=1):
            label = f"{locale}[{index}] {post.get('slug') or post.get('id') or '<unknown>'}"
            required = ("id", "title", "slug", "url", "category", "categorySlug", "date", "excerpt", "contentFile", "sourceUrl")
            for field in required:
                if not str(post.get(field) or "").strip():
                    errors.append(f"{label}: missing {field}")

            if post.get("locale") != locale:
                errors.append(f"{label}: locale field is {post.get('locale')!r}, expected {locale!r}")

            title = str(post.get("title") or "").strip()
            excerpt = str(post.get("excerpt") or "").strip()
            if title:
                titles_by_locale[locale].append(normalized_title(title))
                if len(title) < 18:
                    warnings.append(f"{label}: title is unusually short ({len(title)} chars)")
                elif len(title) > 105:
                    warnings.append(f"{label}: title is long ({len(title)} chars)")
            if excerpt:
                if len(excerpt) < 70:
                    warnings.append(f"{label}: excerpt/meta description is short ({len(excerpt)} chars)")
                elif len(excerpt) > 220:
                    warnings.append(f"{label}: excerpt/meta description is long ({len(excerpt)} chars)")

            url = str(post.get("url") or "")
            if url:
                urls.append(url)
                match = ROUTE_RE.fullmatch(url)
                if not match:
                    errors.append(f"{label}: invalid article route {url}")
                else:
                    route_locale, route_category, route_slug = match.groups()
                    if route_locale != locale:
                        errors.append(f"{label}: route locale mismatch in {url}")
                    if route_category != str(post.get("categorySlug") or ""):
                        errors.append(f"{label}: categorySlug does not match route")
                    if route_slug != str(post.get("slug") or ""):
                        errors.append(f"{label}: slug does not match route")

            category = str(post.get("categorySlug") or "")
            if category and category not in CATEGORIES:
                errors.append(f"{label}: unsupported categorySlug {category!r}")

            try:
                datetime.fromisoformat(str(post.get("date") or "").replace("Z", "+00:00"))
            except Exception:
                errors.append(f"{label}: invalid date {post.get('date')!r}")

            source_url = str(post.get("sourceUrl") or "")
            if source_url and not valid_http_url(source_url):
                errors.append(f"{label}: invalid sourceUrl")

            author = post.get("author") or {}
            if not str(author.get("name") or "").strip():
                errors.append(f"{label}: missing author name")
            if str(author.get("url") or "") != "/forum/authors/radwan-abdulhadi/":
                errors.append(f"{label}: unexpected author profile URL")

            images = post.get("images") or {}
            for image_field in ("hero", "card", "social"):
                if not str(images.get(image_field) or "").strip():
                    errors.append(f"{label}: missing images.{image_field}")
            alt = images.get("alt") or {}
            if not str(alt.get(locale) or "").strip():
                errors.append(f"{label}: missing {locale} image alt text")

            alternates = post.get("alternates") or {}
            ar_alt = str(alternates.get("ar") or "")
            en_alt = str(alternates.get("en") or "")
            if not ar_alt or not en_alt:
                errors.append(f"{label}: missing bilingual alternates")
            else:
                if ar_alt not in route_sets["ar"]:
                    errors.append(f"{label}: Arabic alternate has no matching indexed post: {ar_alt}")
                if en_alt not in route_sets["en"]:
                    errors.append(f"{label}: English alternate has no matching indexed post: {en_alt}")

            content_file = str(post.get("contentFile") or "")
            if content_file:
                content_path = ROOT / content_file
                if not content_path.exists():
                    errors.append(f"{label}: contentFile does not exist: {content_file}")

    duplicate_urls = [url for url, count in Counter(urls).items() if count > 1]
    if duplicate_urls:
        errors.append("duplicate article URLs: " + ", ".join(duplicate_urls[:10]))

    for locale, titles in titles_by_locale.items():
        duplicates = [title for title, count in Counter(titles).items() if count > 1 and title]
        if duplicates:
            errors.append(f"duplicate {locale} titles: " + ", ".join(duplicates[:10]))

    # A bilingual article pair should resolve to the same structured content file.
    en_by_url = {str(p.get("url") or ""): p for p in by_locale["en"]}
    for ar_post in by_locale["ar"]:
        en_url = str((ar_post.get("alternates") or {}).get("en") or "")
        en_post = en_by_url.get(en_url)
        if not en_post:
            continue
        if str(ar_post.get("contentFile") or "") != str(en_post.get("contentFile") or ""):
            errors.append(f"bilingual pair uses different content files: {ar_post.get('url')} / {en_url}")

    print(
        f"Mikhbar search-quality audit: ar={len(by_locale['ar'])} en={len(by_locale['en'])} "
        f"errors={len(errors)} warnings={len(warnings)}"
    )
    for warning in warnings[:80]:
        print(f"WARNING: {warning}")
    if len(warnings) > 80:
        print(f"WARNING: {len(warnings) - 80} additional warnings omitted")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
