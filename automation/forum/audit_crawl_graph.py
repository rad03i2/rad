from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict, deque
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
FORUM = ROOT / "forum"
ORIGIN = "https://mikhbar.website"
ARTICLE_RE = re.compile(r"^/(ar|en)/([a-z0-9-]+)/([^/]+)/$")

AR_TRUST = ("/about/", "/contact/", "/editorial-policy/", "/corrections/", "/ai-policy/", "/authors/radwan-abdulhadi/")
EN_TRUST = tuple("/en" + path for path in AR_TRUST)


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        for key, value in attrs:
            if key.lower() == "href" and value:
                self.links.append(value)


def load_posts(locale: str) -> list[dict]:
    path = FORUM / f"posts-{locale}.json"
    if locale == "ar" and not path.exists():
        path = FORUM / "posts.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError):
        return []
    posts = list(payload if isinstance(payload, list) else payload.get("posts", []))
    return sorted(posts, key=lambda p: str(p.get("dateModified") or p.get("date") or ""), reverse=True)


def public_path(value: str | None) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    if raw.startswith(("http://", "https://")):
        parsed = urlsplit(raw)
        if parsed.netloc not in {"mikhbar.website", "www.mikhbar.website"}:
            return ""
        raw = parsed.path
    if raw.startswith("/forum/"):
        raw = raw[len("/forum"):]
    if not raw.startswith("/"):
        return ""
    raw = raw.split("#", 1)[0].split("?", 1)[0]
    if not raw:
        return "/"
    return raw if raw.endswith("/") or "." in raw.rsplit("/", 1)[-1] else raw + "/"


def file_for_route(route: str) -> Path | None:
    route = public_path(route)
    if not route or route == "/":
        return None
    return FORUM / route.strip("/") / "index.html"


def html_links(path: Path) -> set[str]:
    parser = LinkParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return {link for raw in parser.links if (link := public_path(raw))}


def sitemap_routes() -> set[str]:
    sitemap = FORUM / "sitemap.xml"
    if not sitemap.exists():
        return set()
    root = ET.parse(sitemap).getroot()
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    routes = set()
    for node in root.findall(".//s:loc", ns):
        if node.text and (route := public_path(node.text)):
            # The source discovery file briefly contains the language-negotiating
            # root before the Cloudflare build prunes it. It is a redirect, not an
            # indexable content node, so exclude it from crawl-depth calculations.
            if route == "/":
                continue
            routes.add(route)
    return routes


def related_article_edges(posts: list[dict], locale: str) -> dict[str, set[str]]:
    by_category: dict[str, list[dict]] = defaultdict(list)
    for post in posts:
        by_category[str(post.get("categorySlug") or "")].append(post)

    edges: dict[str, set[str]] = {}
    for category, rows in by_category.items():
        ordered = sorted(rows, key=lambda p: str(p.get("dateModified") or p.get("date") or ""), reverse=True)
        urls = [public_path(row.get("url")) for row in ordered]
        for index, current in enumerate(urls):
            if not current:
                continue
            links = {
                f"/{locale}/",
                f"/{locale}/archive/",
                f"/{locale}/{category}/",
                "/about/" if locale == "ar" else "/en/about/",
                "/authors/radwan-abdulhadi/" if locale == "ar" else "/en/authors/radwan-abdulhadi/",
            }
            if index > 0 and urls[index - 1]:
                links.add(urls[index - 1])
            if index + 1 < len(urls) and urls[index + 1]:
                links.add(urls[index + 1])
            edges[current] = links
    return edges


def bfs(graph: dict[str, set[str]], starts: tuple[str, ...]) -> dict[str, int]:
    depth: dict[str, int] = {}
    queue: deque[str] = deque()
    for start in starts:
        if start in graph:
            depth[start] = 0
            queue.append(start)
    while queue:
        node = queue.popleft()
        for target in graph.get(node, set()):
            if target not in graph or target in depth:
                continue
            depth[target] = depth[node] + 1
            queue.append(target)
    return depth


def main() -> int:
    errors: list[str] = []
    posts_by_locale = {locale: load_posts(locale) for locale in ("ar", "en")}
    article_urls = {
        locale: {public_path(post.get("url")) for post in posts if public_path(post.get("url"))}
        for locale, posts in posts_by_locale.items()
    }

    for locale in ("ar", "en"):
        archive_route = f"/{locale}/archive/"
        archive_file = file_for_route(archive_route)
        if not archive_file or not archive_file.exists():
            errors.append(f"{archive_route}: archive page missing")
            continue
        html = archive_file.read_text(encoding="utf-8")
        expected_canonical = f'<link rel="canonical" href="{ORIGIN}{archive_route}">'
        if expected_canonical not in html:
            errors.append(f"{archive_route}: canonical missing")
        if 'data-news-archive="true"' not in html:
            errors.append(f"{archive_route}: archive marker missing")
        if re.search(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\'][^"\']*noindex', html, re.I):
            errors.append(f"{archive_route}: unexpectedly noindex")
        if f'href="/{locale}/"' not in html:
            errors.append(f"{archive_route}: missing home link")
        other = "en" if locale == "ar" else "ar"
        if f'hreflang="{other}" href="{ORIGIN}/{other}/archive/"' not in html:
            errors.append(f"{archive_route}: missing reciprocal hreflang")
        missing = [url for url in article_urls[locale] if f'href="{url}"' not in html]
        if missing:
            errors.append(f"{archive_route}: missing {len(missing)} article links; examples={missing[:5]}")
        count = html.count('data-archive-article="true"')
        if count != len(article_urls[locale]):
            errors.append(f"{archive_route}: article link count={count} expected={len(article_urls[locale])}")

        home = FORUM / locale / "index.html"
        if not home.exists() or f'href="/{locale}/archive/"' not in home.read_text(encoding="utf-8"):
            errors.append(f"/{locale}/: missing direct archive link")

    routes = sitemap_routes()
    for locale in ("ar", "en"):
        archive_route = f"/{locale}/archive/"
        if archive_route not in routes:
            errors.append(f"sitemap missing {archive_route}")

    graph: dict[str, set[str]] = {route: set() for route in routes}

    # Static indexable pages contribute their real HTML links.
    for route in list(routes):
        is_article = route in article_urls["ar"] or route in article_urls["en"]
        # Dynamic bilingual articles are modeled below. The protected launch
        # announcement predates locale-prefixed routes and remains a real static
        # page, so crawl its actual HTML like any other static node.
        if is_article and ARTICLE_RE.fullmatch(route):
            continue
        path = file_for_route(route)
        if path and path.exists():
            graph[route].update(link for link in html_links(path) if link in graph)

    # Dynamic article pages: model the guaranteed server-rendered navigation plus
    # chronological neighbors that the Worker exposes.
    for locale in ("ar", "en"):
        for route, links in related_article_edges(posts_by_locale[locale], locale).items():
            if route in graph and ARTICLE_RE.fullmatch(route):
                graph[route].update(link for link in links if link in graph)

    inbound: dict[str, int] = {route: 0 for route in graph}
    for source, targets in graph.items():
        for target in targets:
            if target != source and target in inbound:
                inbound[target] += 1

    orphans = sorted(route for route, count in inbound.items() if count == 0 and route not in {"/ar/", "/en/"})
    if orphans:
        errors.append(f"indexable orphan routes={len(orphans)} examples={orphans[:12]}")

    depth = bfs(graph, ("/ar/", "/en/"))
    unreachable = sorted(route for route in graph if route not in depth)
    if unreachable:
        errors.append(f"unreachable indexable routes={len(unreachable)} examples={unreachable[:12]}")

    article_depths: list[int] = []
    for locale in ("ar", "en"):
        home_depth = bfs(graph, (f"/{locale}/",))
        for route in article_urls[locale]:
            if route not in graph:
                errors.append(f"article missing sitemap node: {route}")
                continue
            value = home_depth.get(route)
            if value is None:
                errors.append(f"article unreachable from /{locale}/: {route}")
            else:
                article_depths.append(value)
                if value > 2:
                    errors.append(f"article crawl depth exceeds 2 ({value}): {route}")

    if errors:
        for error in errors:
            print("ERROR:", error, file=sys.stderr)
        print(
            f"Mikhbar crawl graph audit failed: nodes={len(graph)} "
            f"articles={sum(len(v) for v in article_urls.values())} errors={len(errors)}",
            file=sys.stderr,
        )
        return 1

    max_depth = max(depth.values()) if depth else 0
    max_article_depth = max(article_depths) if article_depths else 0
    print(
        "Mikhbar crawl graph audit: "
        f"nodes={len(graph)} edges={sum(len(v) for v in graph.values())} "
        f"articles={sum(len(v) for v in article_urls.values())} "
        f"orphans=0 unreachable=0 max_depth={max_depth} max_article_depth={max_article_depth}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
