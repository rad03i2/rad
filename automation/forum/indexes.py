from __future__ import annotations

from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORUM = ROOT / "forum"
SITE = "https://rdwan.dev"
CATEGORY_SLUGS = ["ai", "robotics", "automation", "mobile", "computers", "apps", "web", "social", "security", "announcements"]
TRUST_PATHS = [
    ("/forum/about/", "0.7"),
    ("/forum/contact/", "0.7"),
    ("/forum/editorial-policy/", "0.7"),
    ("/forum/corrections/", "0.6"),
    ("/forum/ai-policy/", "0.6"),
    ("/forum/authors/radwan-abdulhadi/", "0.8"),
]


def parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def _posts_map(value) -> dict[str, list[dict]]:
    if isinstance(value, dict):
        return {"ar": list(value.get("ar", [])), "en": list(value.get("en", []))}
    return {"ar": list(value or []), "en": []}


def _absolute(url: str | None) -> str:
    value = str(url or "").strip()
    if not value:
        return ""
    return value if value.startswith("http://") or value.startswith("https://") else SITE + (value if value.startswith("/") else "/" + value)


def _plain(value) -> str:
    return " ".join(str(value or "").split())


def write_feed(posts: list[dict], now: datetime, locale: str) -> None:
    is_ar = locale == "ar"
    items = []
    for post in posts[:40]:
        dt = parse_dt(post.get("date")) or now
        image = _absolute(post.get("image") or (post.get("images") or {}).get("card"))
        enclosure = f'\n      <enclosure url="{escape(image, quote=True)}" type="image/webp" />' if image else ""
        items.append(
            "    <item>\n"
            f"      <title>{escape(str(post.get('title', '')))}</title>\n"
            f"      <link>{SITE}{post.get('url')}</link>\n"
            f"      <guid isPermaLink=\"true\">{SITE}{post.get('url')}</guid>\n"
            f"      <pubDate>{format_datetime(dt.astimezone(timezone.utc), usegmt=True)}</pubDate>\n"
            f"      <category>{escape(str(post.get('category', 'Technology')))}</category>\n"
            f"      <description>{escape(str(post.get('excerpt', '')))}</description>"
            f"{enclosure}\n"
            "    </item>"
        )
    filename = f"feed-{locale}.xml"
    title = "مِخبار — العربية" if is_ar else "Mikhbar — English"
    description = "أخبار التقنية والذكاء الاصطناعي والروبوتات والأتمتة والهواتف والحواسيب والتطبيقات والويب." if is_ar else "Technology news covering AI, robotics, automation, mobile, computing, software, the web and digital platforms."
    content = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{title}</title>
    <link>{SITE}/forum/{locale}/</link>
    <description>{description}</description>
    <language>{locale}</language>
    <atom:link href="{SITE}/forum/{filename}" rel="self" type="application/rss+xml" />
    <lastBuildDate>{format_datetime(now.astimezone(timezone.utc), usegmt=True)}</lastBuildDate>
{chr(10).join(items)}
  </channel>
</rss>
'''
    (FORUM / filename).write_text(content, encoding="utf-8")
    if locale == "ar":
        (FORUM / "feed.xml").write_text(content.replace(f"feed-{locale}.xml", "feed.xml"), encoding="utf-8")


def _explicit_alternates(post: dict) -> tuple[str, str]:
    alternates = post.get("alternates") or {}
    return str(alternates.get("ar") or "").strip(), str(alternates.get("en") or "").strip()


def _locale_links(ar_url: str, en_url: str, x_default: str) -> str:
    return (
        f'<xhtml:link rel="alternate" hreflang="ar" href="{SITE}{ar_url}"/>'
        f'<xhtml:link rel="alternate" hreflang="en" href="{SITE}{en_url}"/>'
        f'<xhtml:link rel="alternate" hreflang="x-default" href="{SITE}{x_default}"/>'
    )


def _image_extension(post: dict) -> str:
    images = post.get("images") or {}
    image = _absolute(images.get("hero") or post.get("image") or images.get("card"))
    if not image:
        return ""
    title = escape(str(post.get("title") or ""))
    return f'<image:image><image:loc>{escape(image)}</image:loc><image:title>{title}</image:title></image:image>'


def _category_has_posts(posts: list[dict], slug: str) -> bool:
    return any(str(post.get("categorySlug") or "") == slug for post in posts)


def write_sitemap(posts_by_locale: dict[str, list[dict]], today: str) -> None:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">',
        f'  <url><loc>{SITE}/forum/</loc><lastmod>{today}</lastmod><changefreq>hourly</changefreq><priority>1.0</priority>{_locale_links("/forum/ar/", "/forum/en/", "/forum/")}</url>',
    ]
    for locale in ("ar", "en"):
        lines.append(
            f'  <url><loc>{SITE}/forum/{locale}/</loc><lastmod>{today}</lastmod><changefreq>hourly</changefreq><priority>1.0</priority>'
            f'{_locale_links("/forum/ar/", "/forum/en/", "/forum/")}</url>'
        )
        for slug in CATEGORY_SLUGS:
            if not _category_has_posts(posts_by_locale.get(locale, []), slug):
                continue
            ar_url = f"/forum/ar/{slug}/"; en_url = f"/forum/en/{slug}/"
            both = _category_has_posts(posts_by_locale.get("ar", []), slug) and _category_has_posts(posts_by_locale.get("en", []), slug)
            alternates = _locale_links(ar_url, en_url, ar_url) if both else ""
            lines.append(
                f'  <url><loc>{SITE}/forum/{locale}/{slug}/</loc><lastmod>{today}</lastmod><changefreq>hourly</changefreq><priority>0.9</priority>'
                f'{alternates}</url>'
            )

    for path, priority in TRUST_PATHS:
        lines.append(
            f'  <url><loc>{SITE}{path}</loc><lastmod>{today}</lastmod><changefreq>monthly</changefreq><priority>{priority}</priority></url>'
        )

    seen = set()
    for _, posts in posts_by_locale.items():
        for post in posts:
            url = str(post.get("url") or "")
            if not url or url in seen:
                continue
            seen.add(url)
            modified = (post.get("dateModified") or post.get("date") or today)[:10]
            ar_url, en_url = _explicit_alternates(post)
            alternates = _locale_links(ar_url, en_url, ar_url) if ar_url and en_url else ""
            lines.append(
                f'  <url><loc>{SITE}{url}</loc><lastmod>{modified}</lastmod><changefreq>daily</changefreq><priority>0.8</priority>'
                f'{alternates}{_image_extension(post)}</url>'
            )
    lines.append("</urlset>")
    (FORUM / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_news_sitemap(posts_by_locale: dict[str, list[dict]], now: datetime) -> None:
    cutoff = now.astimezone(timezone.utc) - timedelta(hours=48)
    rows = []
    for locale, posts in posts_by_locale.items():
        for post in posts:
            if post.get("categorySlug") == "announcements":
                continue
            dt = parse_dt(post.get("date"))
            if not dt or dt.astimezone(timezone.utc) < cutoff:
                continue
            title = escape(str(post.get("title", "")))
            loc = SITE + str(post.get("url", ""))
            pub = dt.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
            rows.append(
                "  <url>"
                f"<loc>{loc}</loc>"
                "<news:news>"
                f"<news:publication><news:name>{'مِخبار' if locale == 'ar' else 'Mikhbar'}</news:name><news:language>{locale}</news:language></news:publication>"
                f"<news:publication_date>{pub}</news:publication_date>"
                f"<news:title>{title}</news:title>"
                "</news:news>"
                "</url>"
            )
    content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">\n'
        + "\n".join(rows)
        + "\n</urlset>\n"
    )
    (FORUM / "news-sitemap.xml").write_text(content, encoding="utf-8")


def write_llms(posts_by_locale: dict[str, list[dict]], now: datetime) -> None:
    lines = [
        "# مِخبار / Mikhbar",
        "",
        "Official independent bilingual technology publication: Mikhbar (مِخبار).",
        "Arabic and English coverage of artificial intelligence, robotics, automation, mobile, computers, software, the web, social platforms and security.",
        "",
        "## Primary URLs",
        f"- Publication: {SITE}/forum/",
        f"- Arabic edition: {SITE}/forum/ar/",
        f"- English edition: {SITE}/forum/en/",
        f"- About: {SITE}/forum/about/",
        f"- Contact: {SITE}/forum/contact/",
        f"- Author: {SITE}/forum/authors/radwan-abdulhadi/",
        f"- Editorial policy: {SITE}/forum/editorial-policy/",
        f"- Corrections policy: {SITE}/forum/corrections/",
        f"- AI and automation policy: {SITE}/forum/ai-policy/",
        f"- Sitemap: {SITE}/forum/sitemap.xml",
        f"- News sitemap: {SITE}/forum/news-sitemap.xml",
        f"- Arabic RSS: {SITE}/forum/feed-ar.xml",
        f"- English RSS: {SITE}/forum/feed-en.xml",
        "",
        f"Last generated: {now.astimezone(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')}",
    ]
    labels = {"ar": "Latest Arabic stories", "en": "Latest English stories"}
    for locale in ("ar", "en"):
        lines.extend(["", f"## {labels[locale]}"])
        for post in posts_by_locale.get(locale, [])[:25]:
            title = _plain(post.get("title"))
            url = _absolute(post.get("url"))
            excerpt = _plain(post.get("excerpt"))
            category = _plain(post.get("category"))
            date = _plain(post.get("dateLabel") or str(post.get("date") or "")[:10])
            meta = " · ".join(part for part in (category, date) if part)
            suffix = f" — {excerpt}" if excerpt else ""
            lines.append(f"- [{title}]({url})" + (f" ({meta})" if meta else "") + suffix)
    (FORUM / "llms.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_root_sitemap_index(now: datetime) -> None:
    stamp = now.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    content = f'''<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap><loc>{SITE}/sitemap-main.xml</loc><lastmod>{stamp}</lastmod></sitemap>
  <sitemap><loc>{SITE}/forum/sitemap.xml</loc><lastmod>{stamp}</lastmod></sitemap>
  <sitemap><loc>{SITE}/forum/news-sitemap.xml</loc><lastmod>{stamp}</lastmod></sitemap>
</sitemapindex>
'''
    (ROOT / "sitemap.xml").write_text(content, encoding="utf-8")


def write_all(posts, now: datetime) -> None:
    mapped = _posts_map(posts)
    write_feed(mapped["ar"], now, "ar")
    write_feed(mapped["en"], now, "en")
    write_sitemap(mapped, now.date().isoformat())
    write_news_sitemap(mapped, now)
    write_llms(mapped, now)
    write_root_sitemap_index(now)
