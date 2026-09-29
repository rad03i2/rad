from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORUM = ROOT / "forum"
ORIGIN = "https://mikhbar.website"

MONTHS = {
    "ar": ("", "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"),
    "en": ("", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"),
}


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
    path = str(value or "").strip()
    if path.startswith("/forum/"):
        path = path[len("/forum"):]
    if path and not path.startswith("/"):
        path = "/" + path
    return path


def post_datetime(post: dict) -> datetime | None:
    raw = str(post.get("datePublished") or post.get("date") or "").strip()
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def month_key(post: dict) -> str:
    dt = post_datetime(post)
    return f"{dt.year:04d}-{dt.month:02d}" if dt else "0000-00"


def month_label(key: str, locale: str) -> str:
    if key == "0000-00":
        return "أقدم الأخبار" if locale == "ar" else "Older stories"
    year, month = (int(part) for part in key.split("-", 1))
    return f"{MONTHS[locale][month]} {year}"


def display_date(post: dict, locale: str) -> str:
    label = str(post.get("dateLabel") or "").strip()
    if label:
        return label
    dt = post_datetime(post)
    if not dt:
        return ""
    if locale == "ar":
        return f"{dt.day} {MONTHS['ar'][dt.month]} {dt.year}"
    return f"{MONTHS['en'][dt.month]} {dt.day}, {dt.year}"


def archive_schema(locale: str, count: int) -> str:
    is_ar = locale == "ar"
    canonical = f"{ORIGIN}/{locale}/archive/"
    name = "أرشيف أخبار مِخبار" if is_ar else "Mikhbar News Archive"
    description = (
        "أرشيف كامل ومنظم لجميع أخبار مِخبار المنشورة، مرتب زمنيًا للوصول إلى التغطيات القديمة بسهولة."
        if is_ar else
        "A complete chronological archive of published Mikhbar technology stories for direct access to older coverage."
    )
    graph = [
        {
            "@type": "CollectionPage",
            "@id": canonical + "#page",
            "url": canonical,
            "name": name,
            "description": description,
            "inLanguage": locale,
            "isPartOf": {"@id": ORIGIN + "/#website"},
            "publisher": {"@id": ORIGIN + "/#publisher"},
            "mainEntity": {"@type": "ItemList", "numberOfItems": count},
        },
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "مِخبار" if is_ar else "Mikhbar", "item": f"{ORIGIN}/{locale}/"},
                {"@type": "ListItem", "position": 2, "name": "الأرشيف" if is_ar else "Archive"},
            ],
        },
    ]
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")


def archive_page(locale: str, posts: list[dict]) -> str:
    is_ar = locale == "ar"
    other = "en" if is_ar else "ar"
    canonical = f"{ORIGIN}/{locale}/archive/"
    other_url = f"{ORIGIN}/{other}/archive/"
    title = "أرشيف أخبار مِخبار — جميع الأخبار حسب التاريخ" if is_ar else "Mikhbar News Archive — All Stories by Date"
    description = (
        "تصفح الأرشيف الكامل لأخبار مِخبار التقنية بالعربية، مرتبًا حسب الشهر والتاريخ للوصول السريع إلى الأخبار والتغطيات السابقة."
        if is_ar else
        "Browse the complete English Mikhbar technology news archive, organized by month and date for fast access to earlier stories and coverage."
    )
    heading = "أرشيف الأخبار" if is_ar else "News archive"
    deck = (
        "جميع الأخبار المنشورة في مِخبار مرتبة من الأحدث إلى الأقدم. هذه الصفحة تمنح كل خبر مسارًا داخليًا مباشرًا وثابتًا."
        if is_ar else
        "Every published Mikhbar story, ordered from newest to oldest. This page provides a stable direct internal path to older coverage."
    )
    home = "الرئيسية" if is_ar else "Home"
    latest = "أحدث الأخبار" if is_ar else "Latest"
    guides = "الأدلة" if is_ar else "Guides"
    about = "عن مِخبار" if is_ar else "About Mikhbar"
    archive = "الأرشيف" if is_ar else "Archive"
    count_label = "خبر" if is_ar else "stories"
    lang_label = "EN" if is_ar else "عربي"
    about_url = "/about/" if is_ar else "/en/about/"
    trust_base = "" if is_ar else "/en"

    grouped: dict[str, list[dict]] = defaultdict(list)
    for post in posts:
        href = public_path(post.get("url"))
        # The Arabic launch announcement intentionally keeps its historical,
        # pre-bilingual URL. Because the input list is already locale-scoped,
        # include every valid story URL instead of requiring a locale prefix.
        if not href.startswith("/"):
            continue
        grouped[month_key(post)].append(post)

    sections = []
    for key in sorted(grouped, reverse=True):
        rows = []
        for post in grouped[key]:
            href = public_path(post.get("url"))
            title_text = str(post.get("title") or "").strip()
            if not href or not title_text:
                continue
            category = str(post.get("category") or post.get("categorySlug") or "").strip()
            date = display_date(post, locale)
            meta = " · ".join(part for part in (category, date) if part)
            rows.append(
                f'<li><a data-archive-article="true" href="{escape(href, quote=True)}">'
                f'<strong>{escape(title_text)}</strong>'
                f'{f"<span>{escape(meta)}</span>" if meta else ""}</a></li>'
            )
        if rows:
            sections.append(
                f'<section class="rt-section rt-archive-month" data-archive-month="{escape(key, quote=True)}">'
                f'<header class="rt-section-head"><div><h2>{escape(month_label(key, locale))}</h2></div>'
                f'<span class="rt-count">{len(rows)}</span></header>'
                f'<ol class="rt-archive-list">{"".join(rows)}</ol></section>'
            )

    footer_links = (
        f'<a href="/{locale}/archive/">{archive}</a>'
        f'<a href="{trust_base}/about/">{about}</a>'
        f'<a href="{trust_base}/editorial-policy/">{"السياسة التحريرية" if is_ar else "Editorial policy"}</a>'
        f'<a href="{trust_base}/corrections/">{"التصحيحات" if is_ar else "Corrections"}</a>'
        f'<a href="{trust_base}/ai-policy/">{"سياسة الذكاء الاصطناعي" if is_ar else "AI policy"}</a>'
        f'<a href="{trust_base}/contact/">{"تواصل" if is_ar else "Contact"}</a>'
    )

    style = """.rt-archive-list{list-style:none;margin:0;padding:0;display:grid;gap:0}.rt-archive-list li{border-top:1px solid #e8e8e4}.rt-archive-list a{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:16px;align-items:baseline;padding:14px 0;text-decoration:none;color:inherit}.rt-archive-list strong{line-height:1.55}.rt-archive-list span{font-size:.88rem;white-space:nowrap;opacity:.68}@media(max-width:700px){.rt-archive-list a{grid-template-columns:1fr;gap:5px}.rt-archive-list span{white-space:normal}}"""

    return f'''<!DOCTYPE html><html lang="{locale}" dir="{"rtl" if is_ar else "ltr"}"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#ffffff">
<title>{escape(title)}</title><meta name="description" content="{escape(description, quote=True)}"><meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
<link rel="canonical" href="{canonical}"><link rel="alternate" hreflang="ar" href="{ORIGIN}/ar/archive/"><link rel="alternate" hreflang="en" href="{ORIGIN}/en/archive/"><link rel="alternate" hreflang="x-default" href="{ORIGIN}/ar/archive/">
<meta property="og:type" content="website"><meta property="og:site_name" content="{"مِخبار" if is_ar else "Mikhbar"}"><meta property="og:title" content="{escape(title, quote=True)}"><meta property="og:description" content="{escape(description, quote=True)}"><meta property="og:url" content="{canonical}">
<link rel="stylesheet" href="/styles.css"><link rel="stylesheet" href="/forum.css?v=20260929-layout4"><link rel="stylesheet" href="/forum-media.css?v=20260929-layout4"><link rel="icon" href="/assets/brand/mikhbar/06-web-ready/favicon/favicon.ico"><style>{style}</style>
<script type="application/ld+json">{archive_schema(locale, len(posts))}</script></head>
<body class="rt-locale-{locale}" data-news-archive="true" data-archive-count="{len(posts)}">
<header class="rt-site-header"><div class="rt-navbar"><a class="mikhbar-brand" href="/{locale}/" aria-label="{"مِخبار" if is_ar else "Mikhbar"}"><span class="mikhbar-brand-mark"><img src="/assets/brand/mikhbar/06-web-ready/icon/mikhbar-logo-mark.png" alt="" width="64" height="64"></span><span class="mikhbar-brand-copy"><strong>{"مِخبار" if is_ar else "Mikhbar"}</strong><small dir="ltr">MIKHBAR</small></span></a>
<button class="menu-button rt-menu-button" type="button" aria-label="{"فتح قائمة التنقل" if is_ar else "Open navigation"}" aria-expanded="false" aria-controls="navigation"><svg aria-hidden="true" viewBox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h16"/></svg></button>
<nav class="nav-links rt-platform-nav" id="navigation" aria-label="{"التنقل الرئيسي" if is_ar else "Main navigation"}"><a href="/{locale}/">{home}</a><a href="/{locale}/#latest">{latest}</a><a href="/{locale}/guides/">{guides}</a><a href="/{locale}/archive/" aria-current="page">{archive}</a><a href="{about_url}">{about}</a><a class="rt-lang-switch" href="/{other}/archive/" lang="{other}">{lang_label}</a></nav></div></header>
<main class="rt-main" id="main"><div class="rt-shell"><section class="rt-category-hero"><nav class="rt-breadcrumbs"><a href="/{locale}/">{"مِخبار" if is_ar else "Mikhbar"}</a><span>›</span><span>{archive}</span></nav><div class="rt-category-title"><span class="rt-label">ARCHIVE</span><h1>{heading}</h1><p>{deck}</p><span class="rt-count">{len(posts)} {count_label}</span></div></section>{"".join(sections)}</div></main>
<footer class="rt-footer"><div class="rt-shell rt-copyright">© <span data-year></span> {"مِخبار" if is_ar else "Mikhbar"} · <span class="rt-footer-links">{footer_links}</span></div></footer>
<script src="/forum.js" defer></script></body></html>'''


def main() -> int:
    total = 0
    for locale in ("ar", "en"):
        posts = load_posts(locale)
        target = FORUM / locale / "archive" / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(archive_page(locale, posts), encoding="utf-8")
        total += len(posts)
        print(f"Mikhbar archive generated: locale={locale} stories={len(posts)} path={target.relative_to(ROOT)}")
    print(f"Mikhbar archive generation complete: stories={total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
