from __future__ import annotations

from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORUM = ROOT / "forum"
SITE = "https://rdwan.dev"

STATIC_SITEMAP_ROUTES = [
    ("/forum/", "hourly", "1.0"),
    ("/forum/ai/", "hourly", "0.9"),
    ("/forum/robotics/", "hourly", "0.9"),
    ("/forum/automation/", "hourly", "0.9"),
    ("/forum/mobile/", "hourly", "0.9"),
    ("/forum/computers/", "hourly", "0.9"),
    ("/forum/apps/", "hourly", "0.9"),
    ("/forum/web/", "hourly", "0.9"),
    ("/forum/social/", "hourly", "0.9"),
    ("/forum/security/", "hourly", "0.9"),
    ("/forum/announcements/", "weekly", "0.5"),
    ("/forum/about/", "monthly", "0.5"),
    ("/forum/authors/radwan-abdulhadi/", "monthly", "0.6"),
    ("/forum/editorial-policy/", "monthly", "0.4"),
    ("/forum/corrections/", "monthly", "0.4"),
    ("/forum/ai-policy/", "monthly", "0.4"),
]


def parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def write_feed(posts: list[dict], now: datetime) -> None:
    items = []
    for post in posts[:30]:
        dt = parse_dt(post.get("date")) or now
        items.append(
            "    <item>\n"
            f"      <title>{escape(str(post.get('title', '')))}</title>\n"
            f"      <link>{SITE}{post.get('url')}</link>\n"
            f"      <guid isPermaLink=\"true\">{SITE}{post.get('url')}</guid>\n"
            f"      <pubDate>{format_datetime(dt.astimezone(timezone.utc), usegmt=True)}</pubDate>\n"
            f"      <category>{escape(str(post.get('category', 'تقنية')))}</category>\n"
            f"      <description>{escape(str(post.get('excerpt', '')))}</description>\n"
            "    </item>"
        )
    content = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>RDWAN Tech</title>
    <link>{SITE}/forum/</link>
    <description>أخبار التقنية والذكاء الاصطناعي والروبوتات والأتمتة والهواتف والحواسيب والتطبيقات والويب.</description>
    <language>ar</language>
    <atom:link href="{SITE}/forum/feed.xml" rel="self" type="application/rss+xml" />
    <lastBuildDate>{format_datetime(now.astimezone(timezone.utc), usegmt=True)}</lastBuildDate>
{chr(10).join(items)}
  </channel>
</rss>
'''
    (FORUM / "feed.xml").write_text(content, encoding="utf-8")


def write_sitemap(posts: list[dict], today: str) -> None:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for route, freq, priority in STATIC_SITEMAP_ROUTES:
        lines.append(f"  <url><loc>{SITE}{route}</loc><lastmod>{today}</lastmod><changefreq>{freq}</changefreq><priority>{priority}</priority></url>")
    for post in posts:
        modified = (post.get("dateModified") or post.get("date") or today)[:10]
        lines.append(f"  <url><loc>{SITE}{post.get('url')}</loc><lastmod>{modified}</lastmod><changefreq>daily</changefreq><priority>0.8</priority></url>")
    lines.append("</urlset>")
    (FORUM / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_news_sitemap(posts: list[dict], now: datetime) -> None:
    cutoff = now.astimezone(timezone.utc) - timedelta(hours=48)
    rows = []
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
            "<news:publication><news:name>RDWAN Tech</news:name><news:language>ar</news:language></news:publication>"
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


def write_all(posts: list[dict], now: datetime) -> None:
    write_feed(posts, now)
    write_sitemap(posts, now.date().isoformat())
    write_news_sitemap(posts, now)
