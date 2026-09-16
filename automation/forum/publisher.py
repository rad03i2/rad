from __future__ import annotations

import argparse
import json
import math
import re
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from html import escape
from pathlib import Path
from urllib.parse import urlparse

from common import CONFIG, STATE, load_json, now_iso, save_json
from trend import rank_candidates
from writer import build_source_pack, write_article

ROOT = Path(__file__).resolve().parents[2]
FORUM = ROOT / "forum"
SITE = "https://rdwan.dev"
TZ = timezone(timedelta(hours=3))
AR_MONTHS = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]

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


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        d = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def _arabic_date(dt: datetime) -> str:
    local = dt.astimezone(TZ)
    return f"{local.day} {AR_MONTHS[local.month - 1]} {local.year}"


def _slugify(title: str, fallback: str) -> str:
    text = title.lower()
    text = re.sub(r"[^a-z0-9\s-]", " ", text)
    words = [w for w in text.split() if len(w) > 1][:11]
    slug = "-".join(words)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug[:88] if slug else f"story-{fallback[:12]}"


def _word_count(article: dict) -> int:
    parts = [article.get("deck", "")]
    parts.extend(article.get("summary_bullets", []))
    for section in article.get("sections", []):
        parts.append(section.get("heading", ""))
        parts.extend(section.get("paragraphs", []))
    return len(re.findall(r"\S+", " ".join(parts)))


def _quality_gate(story: dict, sources: list[dict], article: dict) -> tuple[bool, list[str]]:
    errors = []
    title = str(article.get("title", "")).strip()
    description = str(article.get("description", "")).strip()
    bullets = article.get("summary_bullets", [])
    sections = article.get("sections", [])
    words = _word_count(article)

    if len(title) < 25 or len(title) > 120:
        errors.append("title_length")
    if len(description) < 80 or len(description) > 190:
        errors.append("description_length")
    if not isinstance(bullets, list) or len(bullets) < 3:
        errors.append("summary_bullets")
    if not isinstance(sections, list) or len(sections) < 4:
        errors.append("sections")
    if words < 480:
        errors.append("article_too_short")
    if any(not isinstance(s, dict) or not s.get("heading") or not s.get("paragraphs") for s in sections):
        errors.append("malformed_sections")

    usable = [s for s in sources if s.get("ok") and (s.get("text") or s.get("feed_summary"))]
    primary_official = story.get("source", {}).get("type") == "official"
    if primary_official and len(usable) < 1:
        errors.append("missing_primary_source")
    if not primary_official and len(usable) < 2:
        errors.append("journalism_requires_two_sources")

    forbidden = ["كمساعد", "لا أستطيع التحقق", "حسب معلوماتي", "مصدر غير متاح"]
    joined = json.dumps(article, ensure_ascii=False)
    if any(x in joined for x in forbidden):
        errors.append("model_meta_language")
    return not errors, errors


def _render_article(story: dict, article: dict, source_pack: list[dict], slug: str, published: datetime, read_minutes: int) -> str:
    category_slug = story.get("category", "apps")
    category_label = story.get("category_label", category_slug)
    url = f"{SITE}/forum/{category_slug}/{slug}/"
    title = article["title"].strip()
    description = article["description"].strip()
    deck = article["deck"].strip()
    tags = [str(t).strip() for t in article.get("tags", []) if str(t).strip()][:8]
    keywords_json = json.dumps(tags, ensure_ascii=False)
    date_iso = published.isoformat()
    date_label = _arabic_date(published)

    bullets_html = "".join(f"<li>{escape(str(x))}</li>" for x in article.get("summary_bullets", []))
    body_parts = []
    for section in article.get("sections", []):
        body_parts.append(f"<h2>{escape(str(section.get('heading', '')))}</h2>")
        for paragraph in section.get("paragraphs", []):
            body_parts.append(f"<p>{escape(str(paragraph))}</p>")
    sources_html = []
    for src in source_pack:
        if not src.get("url"):
            continue
        sources_html.append(
            f'<li><a href="{escape(src["url"], quote=True)}" rel="nofollow noopener noreferrer">{escape(str(src.get("name", urlparse(src["url"]).netloc)))}</a>'
            f'<small>{escape(str(src.get("feed_title") or src.get("title") or ""))}</small></li>'
        )
    tags_html = "".join(f'<span>{escape(tag)}</span>' for tag in tags)

    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "NewsArticle",
                "@id": url + "#article",
                "headline": title,
                "description": description,
                "datePublished": date_iso,
                "dateModified": date_iso,
                "inLanguage": "ar",
                "mainEntityOfPage": url,
                "image": [f"{SITE}/assets/social/home.jpg"],
                "author": {"@type": "Person", "name": "رضوان عبدالهادي", "url": f"{SITE}/forum/authors/radwan-abdulhadi/"},
                "publisher": {"@type": "Person", "name": "رضوان عبدالهادي", "url": SITE + "/"},
                "articleSection": category_label,
                "keywords": tags,
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "RDWAN Tech", "item": f"{SITE}/forum/"},
                    {"@type": "ListItem", "position": 2, "name": category_label, "item": f"{SITE}/forum/{category_slug}/"},
                    {"@type": "ListItem", "position": 3, "name": title},
                ],
            },
        ],
    }

    return f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#10130f">
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(description, quote=True)}">
  <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
  <link rel="canonical" href="{url}">
  <link rel="stylesheet" href="../../../styles.css"><link rel="stylesheet" href="../../forum.css"><link rel="icon" type="image/png" href="../../../assets/images/radwan-favicon.png">
  <meta property="og:type" content="article"><meta property="og:site_name" content="RDWAN Tech"><meta property="og:locale" content="ar_IQ"><meta property="og:title" content="{escape(title, quote=True)}"><meta property="og:description" content="{escape(description, quote=True)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{SITE}/assets/social/home.jpg"><meta property="article:published_time" content="{date_iso}"><meta property="article:modified_time" content="{date_iso}"><meta property="article:author" content="رضوان عبدالهادي">
  <meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(title, quote=True)}"><meta name="twitter:description" content="{escape(description, quote=True)}"><meta name="twitter:image" content="{SITE}/assets/social/home.jpg">
  <script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, separators=(',', ':'))}</script>
</head>
<body>
  <a class="skip-link" href="#article">انتقل إلى المقال</a>
  <header class="site-header"><div class="container header-inner"><a class="brand" href="../../../" aria-label="رضوان عبدالهادي، الرئيسية"><span class="brand-mark">ر.</span><span class="brand-text">رضوان عبدالهادي<small lang="en" dir="ltr">DEVELOPER PORTFOLIO</small></span></a><button class="menu-button" type="button" aria-label="فتح قائمة التنقل" aria-expanded="false" aria-controls="navigation"><svg aria-hidden="true" viewBox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h16"/></svg></button><nav class="nav-links" id="navigation" aria-label="التنقل الرئيسي"><a href="../../../#home">الرئيسية</a><a href="../../../#about">عنّي</a><a href="../../../#projects">المشاريع</a><a class="rad-nav-forum" href="../../">المنتدى</a></nav></div></header>
  <main class="rt-article" id="article"><article class="rt-article-shell">
    <nav class="rt-breadcrumbs" aria-label="مسار التنقل"><a href="../../">RDWAN Tech</a><span>›</span><a href="../">{escape(category_label)}</a><span>›</span><span>{escape(title)}</span></nav>
    <header class="rt-article-head"><span class="rt-label">{escape(category_label)}</span><h1>{escape(title)}</h1><p class="rt-deck">{escape(deck)}</p><div class="rt-byline"><a class="rt-author" href="../../authors/radwan-abdulhadi/"><span class="rt-avatar">ر</span><span><strong>رضوان عبدالهادي</strong><small>مؤسس ومحرر RDWAN Tech</small></span></a><div class="rt-dates">نُشر: {date_label}<br>آخر تحديث: {date_label} · {read_minutes} دقائق قراءة</div></div></header>
    <div class="rt-article-cover" role="img" aria-label="{escape(title, quote=True)}"></div>
    <aside class="rt-summary"><h2>الخلاصة</h2><ul>{bullets_html}</ul></aside>
    <div class="rt-article-body">{''.join(body_parts)}
      <h2>المصادر</h2><ul class="rt-source-list">{''.join(sources_html)}</ul>
    </div>
    <footer class="rt-article-footer"><div class="rt-article-tags">{tags_html}</div><p class="rt-source-note">هذا الخبر صيغ اعتمادًا على المصادر المدرجة أعلاه، مع فصل المعلومات المؤكدة عن ادعاءات الشركات أو التقديرات.</p></footer>
  </article></main>
  <footer class="rt-footer"><div class="rt-shell rt-footer-grid"><div class="rt-footer-brand"><strong>RDWAN Tech</strong><p>منصة تقنية عربية ضمن rdwan.dev.</p></div><div><h3>عن المنصة</h3><div class="rt-footer-links"><a href="../../about/">عن RDWAN Tech</a><a href="../../editorial-policy/">السياسة التحريرية</a></div></div><div><h3>الثقة</h3><div class="rt-footer-links"><a href="../../corrections/">التصحيحات</a><a href="../../ai-policy/">سياسة AI</a></div></div></div><div class="rt-shell rt-copyright">© <span data-year></span> RDWAN Tech</div></footer>
  <script src="../../forum.js" defer></script>
</body>
</html>'''


def _write_feed(posts: list[dict], now: datetime) -> None:
    items = []
    for p in posts[:30]:
        dt = _parse_dt(p.get("date")) or now
        items.append(
            "    <item>\n"
            f"      <title>{escape(str(p.get('title', '')))}</title>\n"
            f"      <link>{SITE}{p.get('url')}</link>\n"
            f"      <guid isPermaLink=\"true\">{SITE}{p.get('url')}</guid>\n"
            f"      <pubDate>{format_datetime(dt.astimezone(timezone.utc), usegmt=True)}</pubDate>\n"
            f"      <category>{escape(str(p.get('category', 'تقنية')))}</category>\n"
            f"      <description>{escape(str(p.get('excerpt', '')))}</description>\n"
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


def _write_sitemap(posts: list[dict], today: str) -> None:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for route, freq, priority in STATIC_SITEMAP_ROUTES:
        lines.append(f"  <url><loc>{SITE}{route}</loc><lastmod>{today}</lastmod><changefreq>{freq}</changefreq><priority>{priority}</priority></url>")
    for p in posts:
        lastmod = (_parse_dt(p.get("dateModified")) or _parse_dt(p.get("date")) or datetime.now(timezone.utc)).date().isoformat()
        lines.append(f"  <url><loc>{SITE}{p.get('url')}</loc><lastmod>{lastmod}</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>")
    lines.append("</urlset>")
    (FORUM / "sitemap.xml").write_text("\n".join(lines), encoding="utf-8")


def _write_news_sitemap(posts: list[dict], now: datetime) -> None:
    cutoff = now.astimezone(timezone.utc) - timedelta(hours=48)
    rows = []
    for p in posts:
        dt = _parse_dt(p.get("date"))
        if not dt or dt.astimezone(timezone.utc) < cutoff or p.get("categorySlug") == "announcements":
            continue
        rows.append(
            "  <url>\n"
            f"    <loc>{SITE}{p.get('url')}</loc>\n"
            "    <news:news>\n"
            "      <news:publication><news:name>RDWAN Tech</news:name><news:language>ar</news:language></news:publication>\n"
            f"      <news:publication_date>{dt.isoformat()}</news:publication_date>\n"
            f"      <news:title>{escape(str(p.get('title', '')))}</news:title>\n"
            "    </news:news>\n"
            "  </url>"
        )
    content = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">\n' + "\n".join(rows) + '\n</urlset>\n'
    (FORUM / "news-sitemap.xml").write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish one RDWAN Tech article from the verified queue")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    settings = load_json(CONFIG / "settings.json", {})
    publishing_enabled = bool(settings.get("publishingEnabled", False)) and not args.dry_run
    posts_doc = load_json(FORUM / "posts.json", {"posts": []})
    posts = list(posts_doc.get("posts", []))
    queue_doc = load_json(STATE / "queue.json", {"items": []})
    queue = list(queue_doc.get("items", []))
    history = load_json(STATE / "published.json", {"last_published_at": None, "items": []})

    now = datetime.now(TZ)
    last = _parse_dt(history.get("last_published_at"))
    minimum_gap = int(settings.get("minimumMinutesBetweenPosts", 55))
    if last and (now.astimezone(timezone.utc) - last.astimezone(timezone.utc)).total_seconds() < minimum_gap * 60:
        print("Hourly publisher: cooldown active; no post published.")
        return 0

    published_urls = {x.get("source_url") for x in history.get("items", []) if x.get("source_url")}
    published_ids = {x.get("story_id") for x in history.get("items", []) if x.get("story_id")}
    queue = [x for x in queue if x.get("url") not in published_urls and x.get("id") not in published_ids and x.get("status") != "published"]
    ranked = rank_candidates(queue, settings, posts)
    if not ranked:
        print("Hourly publisher: no eligible trend candidate.")
        return 0

    story = ranked[0]
    source_pack = build_source_pack(story, settings)
    article = write_article(story, source_pack, settings)
    ok, errors = _quality_gate(story, source_pack, article)
    if not ok:
        save_json(STATE / "publisher_report.json", {
            "status": "quality_rejected", "at": now_iso(), "story": story.get("title"), "errors": errors
        })
        raise RuntimeError("Quality gate rejected generated article: " + ", ".join(errors))

    words = _word_count(article)
    read_minutes = max(3, math.ceil(words / 190))
    slug = _slugify(story.get("title", ""), story.get("id", "story"))
    category_slug = story.get("category", "apps")
    article_dir = FORUM / category_slug / slug
    if article_dir.exists():
        slug = f"{slug}-{story.get('id', '')[:6]}"
        article_dir = FORUM / category_slug / slug
    article_dir.mkdir(parents=True, exist_ok=True)

    html = _render_article(story, article, source_pack, slug, now, read_minutes)
    article_path = article_dir / "index.html"
    article_path.write_text(html, encoding="utf-8")

    url = f"/forum/{category_slug}/{slug}/"
    post = {
        "id": story.get("id"),
        "title": article["title"].strip(),
        "slug": slug,
        "url": url,
        "category": story.get("category_label", category_slug),
        "categorySlug": category_slug,
        "date": now.isoformat(),
        "dateModified": now.isoformat(),
        "dateLabel": _arabic_date(now),
        "excerpt": article["description"].strip(),
        "tags": article.get("tags", [])[:8],
        "featured": story.get("trend", {}).get("score", 0) >= 105,
        "breaking": story.get("trend", {}).get("score", 0) >= 120 and story.get("trend", {}).get("age_hours", 99) <= 3,
        "readTime": f"{read_minutes} دقائق",
        "author": {"name": "رضوان عبدالهادي", "url": "/forum/authors/radwan-abdulhadi/"},
        "sourceUrl": story.get("url"),
        "trendScore": story.get("trend", {}).get("score"),
    }
    posts.insert(0, post)

    if not publishing_enabled:
        article_path.unlink(missing_ok=True)
        try:
            article_dir.rmdir()
        except OSError:
            pass
        save_json(STATE / "publisher_report.json", {
            "status": "dry_run", "at": now_iso(), "candidate": story, "article": article, "quality_errors": []
        })
        print(f"Hourly publisher dry-run: selected {story.get('title')} trend={story.get('trend', {}).get('score')}")
        return 0

    save_json(FORUM / "posts.json", {"posts": posts})
    _write_feed(posts, now)
    _write_sitemap(posts, now.date().isoformat())
    _write_news_sitemap(posts, now)

    history_items = list(history.get("items", []))
    history_items.insert(0, {
        "story_id": story.get("id"),
        "source_url": story.get("url"),
        "published_url": url,
        "published_at": now.isoformat(),
        "trend_score": story.get("trend", {}).get("score"),
        "category": category_slug,
        "title": article["title"].strip(),
    })
    save_json(STATE / "published.json", {"last_published_at": now.isoformat(), "items": history_items[:1000]})

    for item in queue_doc.get("items", []):
        if item.get("id") == story.get("id"):
            item["status"] = "published"
            item["published_url"] = url
            item["published_at"] = now.isoformat()
    queue_doc["updated_at"] = now.isoformat()
    save_json(STATE / "queue.json", queue_doc)

    save_json(STATE / "publisher_report.json", {
        "status": "published",
        "at": now_iso(),
        "story_id": story.get("id"),
        "source_url": story.get("url"),
        "published_url": url,
        "title": article["title"].strip(),
        "category": category_slug,
        "trend_score": story.get("trend", {}).get("score"),
        "word_count": words,
        "read_minutes": read_minutes,
        "source_count": len([s for s in source_pack if s.get("ok")]),
    })
    print(f"Published {url} trend={story.get('trend', {}).get('score')} words={words}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
