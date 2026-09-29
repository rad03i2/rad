from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "dist" / "mikhbar"
ORIGIN = "https://mikhbar.website"
NS = {
    "s": "http://www.sitemaps.org/schemas/sitemap/0.9",
    "xhtml": "http://www.w3.org/1999/xhtml",
    "news": "http://www.google.com/schemas/sitemap-news/0.9",
}
CANONICAL_RE = re.compile(
    r'<link\b(?=[^>]*\brel=["\']canonical["\'])(?=[^>]*\bhref=["\']([^"\']+)["\'])[^>]*>',
    re.I,
)
ROBOTS_NOINDEX_RE = re.compile(
    r'<meta\b(?=[^>]*\bname=["\']robots["\'])(?=[^>]*\bcontent=["\'][^"\']*\bnoindex\b[^"\']*["\'])[^>]*>',
    re.I,
)


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


def local_static_index(url: str) -> Path | None:
    parsed = urlparse(url)
    path = parsed.path
    if not path.endswith("/") or path == "/":
        return None
    return DIST / path.lstrip("/") / "index.html"


def load_dynamic_routes() -> set[str]:
    path = DIST / "article-map.json"
    if not path.exists():
        return set()
    payload = json.loads(path.read_text(encoding="utf-8"))
    routes = payload.get("routes", {}) if isinstance(payload, dict) else {}
    return {str(route) for route in routes}


def audit_static_target(url: str, errors: list[str]) -> None:
    page = local_static_index(url)
    if page is None:
        return
    if not page.exists():
        errors.append(f"sitemap URL has no static page: {url}")
        return

    text = page.read_text(encoding="utf-8", errors="replace")
    if ROBOTS_NOINDEX_RE.search(text):
        errors.append(f"sitemap URL is noindex: {url}")

    match = CANONICAL_RE.search(text)
    if not match:
        errors.append(f"sitemap URL has no canonical tag: {url}")
        return
    canonical = str(match.group(1) or "").strip()
    if canonical != url:
        errors.append(f"sitemap canonical mismatch: {url} -> {canonical}")


def audit_news_sitemap(main_urls: set[str], errors: list[str]) -> tuple[int, int]:
    path = DIST / "news-sitemap.xml"
    if not path.exists():
        errors.append("news-sitemap.xml is missing")
        return 0, 0

    root = ET.parse(path).getroot()
    rows = root.findall("s:url", NS)
    seen: set[str] = set()

    for row in rows:
        loc = str(row.findtext("s:loc", default="", namespaces=NS) or "").strip()
        if not loc:
            errors.append("news sitemap entry without loc")
            continue
        if loc in seen:
            errors.append(f"duplicate news sitemap URL: {loc}")
        seen.add(loc)

        if loc not in main_urls:
            errors.append(f"news sitemap URL missing from main sitemap: {loc}")

        parsed = urlparse(loc)
        if parsed.scheme != "https" or parsed.netloc != "mikhbar.website":
            errors.append(f"non-canonical news sitemap host: {loc}")
        if parsed.path.startswith("/forum/") or "rdwan.dev" in loc:
            errors.append(f"legacy URL in news sitemap: {loc}")
        if parsed.query or parsed.fragment:
            errors.append(f"query/fragment in news sitemap URL: {loc}")

        news = row.find("news:news", NS)
        if news is None:
            errors.append(f"news sitemap entry missing news:news: {loc}")
            continue

        language = str(news.findtext("news:publication/news:language", default="", namespaces=NS) or "").strip()
        publication = str(news.findtext("news:publication/news:name", default="", namespaces=NS) or "").strip()
        title = str(news.findtext("news:title", default="", namespaces=NS) or "").strip()
        published = str(news.findtext("news:publication_date", default="", namespaces=NS) or "").strip()

        if language not in {"ar", "en"}:
            errors.append(f"invalid news language for {loc}: {language!r}")
        expected_publication = "مِخبار" if language == "ar" else "Mikhbar"
        if publication != expected_publication:
            errors.append(f"unexpected news publication name for {loc}: {publication!r}")
        if not title:
            errors.append(f"empty news title: {loc}")
        if not published:
            errors.append(f"missing news publication date: {loc}")

    return len(rows), len(seen)


def main() -> int:
    errors: list[str] = []
    sitemap_path = DIST / "sitemap.xml"
    if not sitemap_path.exists():
        print("ERROR: dist/mikhbar/sitemap.xml is missing", file=sys.stderr)
        return 1

    root = ET.parse(sitemap_path).getroot()
    url_nodes = root.findall("s:url", NS)
    locs = [
        str(node.findtext("s:loc", default="", namespaces=NS) or "").strip()
        for node in url_nodes
        if str(node.findtext("s:loc", default="", namespaces=NS) or "").strip()
    ]
    loc_set = set(locs)

    if len(locs) != len(loc_set):
        errors.append(f"duplicate sitemap URLs: total={len(locs)} unique={len(loc_set)}")

    if ORIGIN + "/" in loc_set:
        errors.append("redirecting language-negotiation root must not be submitted in sitemap")

    dynamic_routes = load_dynamic_routes()

    for node, url in zip(url_nodes, locs):
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.netloc != "mikhbar.website":
            errors.append(f"non-canonical sitemap host: {url}")
        if parsed.path == "/forum" or parsed.path.startswith("/forum/"):
            errors.append(f"legacy /forum path in public sitemap: {url}")
        if "rdwan.dev" in url:
            errors.append(f"legacy rdwan.dev URL in public sitemap: {url}")
        if parsed.query or parsed.fragment:
            errors.append(f"query/fragment in sitemap URL: {url}")
        if not parsed.path.endswith("/"):
            errors.append(f"non-final page URL in sitemap (missing trailing slash): {url}")

        route = parsed.path
        if route in dynamic_routes:
            pass
        else:
            audit_static_target(url, errors)

        for alt in node.findall("xhtml:link", NS):
            hreflang = str(alt.attrib.get("hreflang") or "").strip()
            href = str(alt.attrib.get("href") or "").strip()
            if hreflang in {"ar", "en"} and href and href not in loc_set:
                errors.append(f"hreflang target missing from sitemap: {url} -> {hreflang} {href}")
            if hreflang == "x-default" and href and href != ORIGIN + "/" and href not in loc_set:
                errors.append(f"x-default target is not a canonical sitemap URL: {url} -> {href}")

    expected_articles: set[str] = set()
    source_rows = 0
    for locale in ("ar", "en"):
        for post in load_posts(locale):
            source_rows += 1
            url = absolute_public_url(post.get("url"))
            if not url:
                errors.append(f"{locale}: post without URL")
                continue
            expected_articles.add(url)

    missing_articles = sorted(expected_articles - loc_set)
    if missing_articles:
        errors.append(
            f"{len(missing_articles)} indexed article URLs missing from sitemap; "
            f"examples: {', '.join(missing_articles[:8])}"
        )

    required_pages = {
        ORIGIN + "/ar/",
        ORIGIN + "/en/",
        ORIGIN + "/about/",
        ORIGIN + "/contact/",
        ORIGIN + "/editorial-policy/",
        ORIGIN + "/corrections/",
        ORIGIN + "/ai-policy/",
        ORIGIN + "/authors/radwan-abdulhadi/",
        ORIGIN + "/en/about/",
        ORIGIN + "/en/contact/",
        ORIGIN + "/en/editorial-policy/",
        ORIGIN + "/en/corrections/",
        ORIGIN + "/en/ai-policy/",
        ORIGIN + "/en/authors/radwan-abdulhadi/",
        ORIGIN + "/ar/archive/",
        ORIGIN + "/en/archive/",
    }
    missing_required = sorted(required_pages - loc_set)
    if missing_required:
        errors.append("required public pages missing from sitemap: " + ", ".join(missing_required))

    news_rows, news_unique = audit_news_sitemap(loc_set, errors)

    print(
        "Mikhbar deployed indexing audit: "
        f"sitemap_urls={len(locs)} unique={len(loc_set)} "
        f"post_rows={source_rows} expected_article_urls={len(expected_articles)} "
        f"missing_articles={len(missing_articles)} news_urls={news_rows} "
        f"news_unique={news_unique} errors={len(errors)}"
    )

    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
