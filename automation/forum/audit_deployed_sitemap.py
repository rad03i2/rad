from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "dist" / "mikhbar"
ORIGIN = "https://mikhbar.website"
NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}


def load_posts(locale: str) -> list[dict]:
    path = DIST / f"posts-{locale}.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    posts = payload.get("posts", []) if isinstance(payload, dict) else payload
    if not isinstance(posts, list):
        raise ValueError(f"{path}: posts must be a list")
    return posts


def absolute_public_url(value: str) -> str:
    value = str(value or "").strip()
    if not value:
        return ""
    if value.startswith("http://") or value.startswith("https://"):
        return value
    if not value.startswith("/"):
        value = "/" + value
    return ORIGIN + value


def main() -> int:
    errors: list[str] = []
    sitemap_path = DIST / "sitemap.xml"
    if not sitemap_path.exists():
        print("ERROR: dist/mikhbar/sitemap.xml is missing", file=sys.stderr)
        return 1

    root = ET.parse(sitemap_path).getroot()
    locs = [
        str(node.text or "").strip()
        for node in root.findall("s:url/s:loc", NS)
        if str(node.text or "").strip()
    ]
    loc_set = set(locs)

    if len(locs) != len(loc_set):
        errors.append(f"duplicate sitemap URLs: total={len(locs)} unique={len(loc_set)}")

    for url in locs:
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.netloc != "mikhbar.website":
            errors.append(f"non-canonical sitemap host: {url}")
        if parsed.path == "/forum" or parsed.path.startswith("/forum/"):
            errors.append(f"legacy /forum path in public sitemap: {url}")
        if "rdwan.dev" in url:
            errors.append(f"legacy rdwan.dev URL in public sitemap: {url}")

    expected_articles: set[str] = set()
    source_rows = 0
    for locale in ("ar", "en"):
        for post in load_posts(locale):
            source_rows += 1
            url = absolute_public_url(post.get("url"))
            if not url:
                errors.append(f"{locale}: post without URL")
                continue
            # The one retained legacy announcement is not a dynamic bilingual
            # article route; include it only if it is actually present publicly.
            expected_articles.add(url)

    missing_articles = sorted(expected_articles - loc_set)
    if missing_articles:
        errors.append(
            f"{len(missing_articles)} indexed article URLs missing from sitemap; "
            f"examples: {', '.join(missing_articles[:8])}"
        )

    required_pages = {
        ORIGIN + "/",
        ORIGIN + "/ar/",
        ORIGIN + "/en/",
        ORIGIN + "/about/",
        ORIGIN + "/contact/",
        ORIGIN + "/editorial-policy/",
        ORIGIN + "/corrections/",
        ORIGIN + "/ai-policy/",
        ORIGIN + "/authors/radwan-abdulhadi/",
    }
    missing_required = sorted(required_pages - loc_set)
    if missing_required:
        errors.append("required public pages missing from sitemap: " + ", ".join(missing_required))

    print(
        "Mikhbar deployed sitemap audit: "
        f"sitemap_urls={len(locs)} unique={len(loc_set)} "
        f"post_rows={source_rows} expected_article_urls={len(expected_articles)} "
        f"missing_articles={len(missing_articles)} errors={len(errors)}"
    )

    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
