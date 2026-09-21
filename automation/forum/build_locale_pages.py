from __future__ import annotations

import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORUM = ROOT / "forum"
SITE = "https://rdwan.dev"

CATEGORIES = {
    "ai": {"ar": ("الذكاء الاصطناعي", "أخبار النماذج والشركات والأدوات والمساعدات الذكية وتطبيقات الذكاء الاصطناعي."), "en": ("Artificial Intelligence", "News on AI models, companies, tools, assistants and real-world artificial intelligence applications.")},
    "robotics": {"ar": ("الروبوتات", "الروبوتات البشرية والصناعية والحساسات والتحكم والمصانع الذكية."), "en": ("Robotics", "Humanoid and industrial robots, sensors, control systems and intelligent manufacturing.")},
    "automation": {"ar": ("الأتمتة", "أتمتة الأعمال وسير العمل والسكربتات والوكلاء والأدوات الذكية."), "en": ("Automation", "Workflow automation, scripts, agents and tools that automate digital work.")},
    "mobile": {"ar": ("الهواتف", "Android وiPhone والأجهزة الجديدة والتحديثات والمزايا والتقنيات المحمولة."), "en": ("Mobile", "Android, iPhone, new devices, operating-system updates and mobile technology.")},
    "computers": {"ar": ("الحواسيب", "Windows وLinux والعتاد والمعالجات والرسوميات والحوسبة الشخصية ومراكز البيانات."), "en": ("Computing", "Windows, Linux, hardware, processors, graphics, personal computing and data centers.")},
    "apps": {"ar": ("التطبيقات والبرامج", "برامج سطح المكتب وتطبيقات الهاتف والخدمات الرقمية والأدوات الجديدة."), "en": ("Apps & Software", "Desktop software, mobile apps, digital services and new productivity tools.")},
    "web": {"ar": ("الويب", "المواقع والمتصفحات ومحركات البحث والخدمات وتقنيات تطوير الويب."), "en": ("Web", "Websites, browsers, search engines, online services and modern web technologies.")},
    "social": {"ar": ("التواصل الاجتماعي", "YouTube وTikTok وInstagram وFacebook والمنصات الاجتماعية وتحديثاتها."), "en": ("Social Media", "YouTube, TikTok, Instagram, Facebook and the platforms shaping social media.")},
    "security": {"ar": ("الأمن التقني", "التحديثات الأمنية والخصوصية والحماية الرقمية والثغرات المهمة للمستخدمين."), "en": ("Cybersecurity", "Security updates, privacy, digital protection and vulnerabilities that matter to users.")},
    "announcements": {"ar": ("إعلانات المنصة", "تحديثات مِخبار وإعلانات تطوير المنصة."), "en": ("Announcements", "Updates and product announcements from Mikhbar.")},
}

UI = {
    "ar": {
        "dir": "rtl", "home": "الرئيسية", "about": "عنّي", "projects": "المشاريع", "forum": "مِخبار",
        "coverage": "تغطية تقنية على مدار الساعة", "edition": "ARABIC EDITION",
        "tagline": "أخبار وشروحات وتحليلات موثقة في التقنية والذكاء الاصطناعي والروبوتات والأتمتة والهواتف والحواسيب والبرمجيات.",
        "important": "الأهم الآن", "allNews": "كل الأخبار", "explore": "استكشف بسرعة", "latest": "أحدث المنشورات",
        "latestDesc": "أحدث الأخبار التقنية المنشورة والمحدثة باستمرار.", "search": "ابحث في الأخبار والمواضيع والتقنيات...",
        "searchNote": "بحث فوري داخل المنشورات", "noResults": "لا توجد نتائج مطابقة", "tryDifferent": "جرّب عبارة بحث مختلفة أو استعرض أحد الأقسام التقنية.",
        "more": "عرض المزيد", "topics": "عالم التقنية في مكان واحد", "topicsDesc": "تغطية منظمة حسب الموضوع تساعد القارئ ومحركات البحث على الوصول إلى المحتوى المتخصص.",
        "newsletter": "ابقَ قريبًا من الجديد", "newsletterDesc": "اشترك للحصول على أهم تحديثات مِخبار.", "subscribe": "اشترك في التحديثات",
        "skip": "انتقل إلى المحتوى", "menu": "فتح قائمة التنقل", "nav": "التنقل الرئيسي", "posts": "منشور",
    },
    "en": {
        "dir": "ltr", "home": "Home", "about": "About", "projects": "Projects", "forum": "Mikhbar",
        "coverage": "Technology coverage around the clock", "edition": "ENGLISH EDITION",
        "tagline": "Verified news, explainers and analysis across technology, artificial intelligence, robotics, automation, mobile, computing and software.",
        "important": "Top stories", "allNews": "All news", "explore": "Explore", "latest": "Latest stories",
        "latestDesc": "The latest technology stories, continuously published and updated.", "search": "Search news, topics and technologies...",
        "searchNote": "Instant search across published stories", "noResults": "No matching results", "tryDifferent": "Try a different search phrase or explore one of the technology sections.",
        "more": "Load more", "topics": "Technology in one place", "topicsDesc": "Topic-focused coverage that helps readers and search engines discover specialist reporting.",
        "newsletter": "Stay close to what’s next", "newsletterDesc": "Subscribe for the most important Mikhbar updates.", "subscribe": "Subscribe",
        "skip": "Skip to content", "menu": "Open navigation", "nav": "Main navigation", "posts": "stories",
    },
}


def _load_posts(locale: str) -> list[dict]:
    path = FORUM / f"posts-{locale}.json"
    if not path.exists() and locale == "ar":
        path = FORUM / "posts.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        posts = data if isinstance(data, list) else data.get("posts", [])
        return sorted(posts, key=lambda p: str(p.get("date") or ""), reverse=True)
    except Exception:
        return []


def _category_nav(locale: str, prefix: str = "./", current: str | None = None) -> str:
    home_label = "الرئيسية" if locale == "ar" else "Home"
    links = [f'<a href="{prefix}"{(" aria-current=\"page\"" if current is None else "")}>{home_label}</a>']
    for slug in ("ai", "robotics", "automation", "mobile", "computers", "apps", "web", "social", "security"):
        label = CATEGORIES[slug][locale][0]
        current_attr = ' aria-current="page"' if current == slug else ""
        links.append(f'<a href="{prefix}{slug}/"{current_attr}>{escape(label)}</a>')
    return "".join(links)


def _head(locale: str, path: str, title: str, description: str, image: str = "/assets/social/home.jpg") -> str:
    site_name = "مِخبار" if locale == "ar" else "Mikhbar"
    ar_path = path.replace(f"/forum/{locale}/", "/forum/ar/")
    en_path = path.replace(f"/forum/{locale}/", "/forum/en/")
    return f'''<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#10130f">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description, quote=True)}">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
<link rel="canonical" href="{SITE}{path}">
<link rel="alternate" hreflang="ar" href="{SITE}{ar_path}">
<link rel="alternate" hreflang="en" href="{SITE}{en_path}">
<link rel="alternate" hreflang="x-default" href="{SITE}/forum/">
<link rel="alternate" type="application/rss+xml" title="{site_name} {locale.upper()}" href="{SITE}/forum/feed-{locale}.xml">
<meta property="og:type" content="website"><meta property="og:site_name" content="{site_name}"><meta property="og:locale" content="{'ar_IQ' if locale == 'ar' else 'en_US'}">
<meta property="og:title" content="{escape(title, quote=True)}"><meta property="og:description" content="{escape(description, quote=True)}"><meta property="og:url" content="{SITE}{path}"><meta property="og:image" content="{SITE}{image}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(title, quote=True)}"><meta name="twitter:description" content="{escape(description, quote=True)}"><meta name="twitter:image" content="{SITE}{image}">'''


def _header(locale: str, depth: int) -> str:
    del depth
    ui = UI[locale]
    site_name = "مِخبار" if locale == "ar" else "Mikhbar"
    mark = "م" if locale == "ar" else "M"
    home_label = "الرئيسية" if locale == "ar" else "Home"
    latest_label = "أحدث الأخبار" if locale == "ar" else "Latest"
    about_label = "عن مِخبار" if locale == "ar" else "About Mikhbar"
    lang_label = "EN" if locale == "ar" else "عربي"
    home_url = f"/forum/{locale}/"
    latest_url = home_url + "#latest"
    lang_url = "/forum/en/" if locale == "ar" else "/forum/ar/"
    return f'''<header class="rt-site-header"><div class="rt-navbar">
<a class="mikhbar-brand" href="{home_url}" aria-label="{site_name}"><span class="mikhbar-brand-mark">{mark}</span><span class="mikhbar-brand-copy"><strong>{site_name}</strong><small dir="ltr">MIKHBAR</small></span></a>
<button class="menu-button rt-menu-button" type="button" aria-label="{ui['menu']}" aria-expanded="false" aria-controls="navigation"><svg aria-hidden="true" viewBox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h16"/></svg></button>
<nav class="nav-links rt-platform-nav" id="navigation" aria-label="{ui['nav']}"><a href="{home_url}">{home_label}</a><a href="{latest_url}">{latest_label}</a><a href="/forum/about/">{about_label}</a><a class="rt-lang-switch" href="{lang_url}" lang="{'en' if locale == 'ar' else 'ar'}">{lang_label}</a></nav>
</div></header>'''

def _card(post: dict, locale: str) -> str:
    url = escape(str(post.get("url") or "#"), quote=True)
    title = escape(str(post.get("title") or ""))
    excerpt = escape(str(post.get("excerpt") or ""))
    category = escape(str(post.get("category") or "Technology"))
    date = escape(str(post.get("dateLabel") or ""))
    read = escape(str(post.get("readTime") or ""))
    img = str(post.get("image") or (post.get("images") or {}).get("card") or "/assets/social/home.jpg")
    alt = title
    breaking = '<span class="rt-breaking">عاجل</span>' if locale == "ar" and post.get("breaking") else ('<span class="rt-breaking">Breaking</span>' if post.get("breaking") else "")
    return f'''<a class="rt-feed-item" href="{url}"><div class="rt-feed-copy"><div class="rt-feed-kicker">{breaking}<span>{category}</span></div><h3>{title}</h3><p>{excerpt}</p><div class="rt-feed-time">{date}{(' · ' + read) if read else ''}</div></div><div class="rt-thumb"><img src="{escape(img, quote=True)}" alt="{escape(alt, quote=True)}" width="800" height="450" loading="lazy" decoding="async"></div></a>'''


def _now_item(post: dict, index: int) -> str:
    return f'''<a class="rt-now-item" href="{escape(str(post.get('url') or '#'), quote=True)}"><span class="rt-now-num">{index:02d}</span><span><strong>{escape(str(post.get('title') or ''))}</strong><small>{escape(str(post.get('dateLabel') or ''))}</small></span></a>'''


def _schemas(locale: str, path: str, posts: list[dict], page_name: str) -> str:
    site_name = "مِخبار" if locale == "ar" else "Mikhbar"
    item_list = [{"@type": "ListItem", "position": i + 1, "url": SITE + str(p.get("url") or ""), "name": str(p.get("title") or "")} for i, p in enumerate(posts[:20]) if p.get("url")]
    graph = [
        {"@type": "NewsMediaOrganization", "@id": SITE + "/forum/#publisher", "name": site_name, "alternateName": "Mikhbar" if locale == "ar" else "مِخبار", "url": SITE + "/forum/", "logo": {"@type": "ImageObject", "url": SITE + "/assets/images/radwan-favicon.png"}, "founder": {"@type": "Person", "name": "Radwan Abdulhadi", "url": SITE + "/"}},
        {"@type": "CollectionPage", "@id": SITE + path + "#page", "url": SITE + path, "name": page_name, "inLanguage": locale, "publisher": {"@id": SITE + "/forum/#publisher"}},
    ]
    if item_list:
        graph.append({"@type": "ItemList", "itemListElement": item_list})
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))


def _home_page(locale: str, posts: list[dict]) -> str:
    ui = UI[locale]
    site_name = "مِخبار" if locale == "ar" else "Mikhbar"
    title = "مِخبار — أخبار التقنية والذكاء الاصطناعي والروبوتات" if locale == "ar" else "Mikhbar — Technology News, AI, Robotics & Automation"
    desc = "أخبار تقنية موثقة بالعربية عن الذكاء الاصطناعي والروبوتات والأتمتة والهواتف والحواسيب والبرامج، مع مصادر وصور وتحديثات مستمرة." if locale == "ar" else "Verified technology news in English covering AI, robotics, automation, mobile, computing, software and the web, with sources and continuous updates."
    featured = next((p for p in posts if p.get("featured")), posts[0] if posts else {})
    others = [p for p in posts if p.get("id") != featured.get("id")][:5]
    lead_url = escape(str(featured.get("url") or "#latest"), quote=True)
    lead_img = str(featured.get("image") or (featured.get("images") or {}).get("hero") or "/assets/social/home.jpg")
    lead_title = escape(str(featured.get("title") or ui["latest"]))
    lead_excerpt = escape(str(featured.get("excerpt") or ui["tagline"]))
    lead_category = escape(str(featured.get("category") or site_name))
    lead_date = escape(str(featured.get("dateLabel") or "")); lead_read = escape(str(featured.get("readTime") or ""))
    feed = "".join(_card(p, locale) for p in posts[:12])
    now = "".join(_now_item(p, i + 1) for i, p in enumerate(others))
    topics = "".join(f'<a class="rt-category-box" href="./{slug}/"><span>{i:02d} · {slug.upper()}</span><h3>{escape(CATEGORIES[slug][locale][0])}</h3><p>{escape(CATEGORIES[slug][locale][1])}</p></a>' for i, slug in enumerate(("ai","robotics","automation","mobile","computers","apps","web","social","security"), 1))
    schema = _schemas(locale, f"/forum/{locale}/", posts, title)
    return f'''<!DOCTYPE html><html lang="{locale}" dir="{ui['dir']}"><head>{_head(locale, f'/forum/{locale}/', title, desc, lead_img)}
<link rel="stylesheet" href="../../styles.css"><link rel="stylesheet" href="../forum.css"><link rel="stylesheet" href="../forum-media.css"><link rel="icon" type="image/png" href="../../assets/images/radwan-favicon.png"><script type="application/ld+json">{schema}</script></head>
<body class="rt-locale-{locale}" data-locale="{locale}"><a class="skip-link" href="#main">{ui['skip']}</a>{_header(locale,2)}<main class="rt-main" id="main">
<div class="rt-topline"><div class="rt-shell rt-topline-inner"><span class="rt-live">{ui['coverage']}</span><span class="rt-edition" dir="ltr">{site_name} · {ui['edition']}</span></div></div>
<section class="rt-brandline"><div class="rt-shell rt-brandrow"><div class="rt-wordmark"><strong>{site_name}</strong><b>{"أخبار التقنية" if locale == "ar" else "TECH"}</b></div><p class="rt-tagline">{ui['tagline']}</p></div></section>
<nav class="rt-categories" aria-label="Sections"><div class="rt-shell rt-category-scroll">{_category_nav(locale)}</div></nav><div class="rt-shell">
<section class="rt-hero" aria-label="Top content"><a class="rt-lead" id="rtLead" href="{lead_url}"><img class="rt-lead-media" id="rtLeadImage" src="{escape(lead_img, quote=True)}" alt="{escape(str(featured.get('title') or site_name), quote=True)}" width="1600" height="900" fetchpriority="high" decoding="async"><span class="rt-label" id="rtLeadCategory">{lead_category}</span><h1 id="rtLeadTitle">{lead_title}</h1><p id="rtLeadExcerpt">{lead_excerpt}</p><div class="rt-story-meta"><span id="rtLeadDate">{lead_date}</span><span id="rtLeadRead">{lead_read}</span><span>Radwan Abdulhadi</span></div></a>
<aside class="rt-side"><section class="rt-side-panel"><div class="rt-panel-head"><h2>{ui['important']}</h2><a href="#latest">{ui['allNews']}</a></div><div class="rt-now-list" id="rtNowList">{now}</div></section><section class="rt-side-panel"><div class="rt-panel-head"><h2>{ui['explore']}</h2></div><div class="rt-topic-grid"><a class="rt-topic-card" href="./ai/"><b>{CATEGORIES['ai'][locale][0]}</b><span>AI</span></a><a class="rt-topic-card" href="./robotics/"><b>{CATEGORIES['robotics'][locale][0]}</b><span>ROBOTICS</span></a><a class="rt-topic-card" href="./mobile/"><b>{CATEGORIES['mobile'][locale][0]}</b><span>MOBILE</span></a><a class="rt-topic-card" href="./apps/"><b>{CATEGORIES['apps'][locale][0]}</b><span>APPS</span></a></div></section></aside></section>
<div class="rt-toolbar"><label class="rt-search"><input id="rtSearch" type="search" autocomplete="off" placeholder="{ui['search']}" aria-label="{ui['search']}"></label><span class="rt-view-note">{ui['searchNote']}</span></div>
<section class="rt-section" id="latest"><header class="rt-section-head"><div><h2>{ui['latest']}</h2><p>{ui['latestDesc']}</p></div><span class="rt-count" id="rtCount">{len(posts)} {ui['posts']}</span></header><div class="rt-feed" id="rtFeed">{feed}</div><div class="rt-feed-empty" id="rtEmpty" hidden><b>{ui['noResults']}</b><p>{ui['tryDifferent']}</p></div><button class="rt-load-more" id="rtLoadMore" type="button">{ui['more']}</button></section>
<section class="rt-section"><header class="rt-section-head"><div><h2>{ui['topics']}</h2><p>{ui['topicsDesc']}</p></div></header><div class="rt-category-showcase">{topics}</div></section>
<section class="rt-newsletter"><div><h2>{ui['newsletter']}</h2><p>{ui['newsletterDesc']}</p></div><a href="https://omniform1.com/forms/v1/landingPage/6aa951449b0f973742e3f90d/6aa9b7a1f85082d5ccd3f79c">{ui['subscribe']}</a></section></div></main>
<footer class="rt-footer"><div class="rt-shell rt-copyright">© <span data-year></span> {site_name}</div></footer><script src="../forum.js" defer></script></body></html>'''


def _category_page(locale: str, slug: str, all_posts: list[dict]) -> str:
    ui = UI[locale]; label, desc = CATEGORIES[slug][locale]; posts = [p for p in all_posts if p.get("categorySlug") == slug]
    site_name = "مِخبار" if locale == "ar" else "Mikhbar"
    title = (f"{label}: أحدث الأخبار والشروحات | مِخبار" if locale == "ar" else f"{label} News, Updates & Analysis | Mikhbar")
    path = f"/forum/{locale}/{slug}/"; root = "../../../"; feed = "".join(_card(p, locale) for p in posts[:20]); schema = _schemas(locale, path, posts, title)
    return f'''<!DOCTYPE html><html lang="{locale}" dir="{ui['dir']}"><head>{_head(locale,path,title,desc)}
<link rel="stylesheet" href="{root}styles.css"><link rel="stylesheet" href="../../forum.css"><link rel="stylesheet" href="../../forum-media.css"><link rel="icon" type="image/png" href="{root}assets/images/radwan-favicon.png"><script type="application/ld+json">{schema}</script></head>
<body class="rt-locale-{locale}" data-locale="{locale}" data-category="{slug}"><a class="skip-link" href="#main">{ui['skip']}</a>{_header(locale,3)}<main class="rt-main" id="main">
<nav class="rt-categories" aria-label="Sections"><div class="rt-shell rt-category-scroll">{_category_nav(locale,'../',slug)}</div></nav><div class="rt-shell"><section class="rt-category-hero"><nav class="rt-breadcrumbs"><a href="../">{site_name}</a><span>›</span><span>{escape(label)}</span></nav><div class="rt-category-title"><span class="rt-label">{slug.upper()}</span><h1>{escape(label)}</h1><p>{escape(desc)}</p></div></section>
<div class="rt-toolbar"><label class="rt-search"><input id="rtSearch" type="search" autocomplete="off" placeholder="{ui['search']}" aria-label="{ui['search']}"></label><span class="rt-view-note">{ui['searchNote']}</span></div>
<section class="rt-section"><header class="rt-section-head"><div><h2>{ui['latest']}</h2><p>{escape(desc)}</p></div><span class="rt-count" id="rtCount">{len(posts)} {ui['posts']}</span></header><div class="rt-feed" id="rtFeed">{feed}</div><div class="rt-feed-empty" id="rtEmpty" {'hidden' if posts else ''}><b>{ui['noResults']}</b><p>{ui['tryDifferent']}</p></div><button class="rt-load-more" id="rtLoadMore" type="button">{ui['more']}</button></section></div></main>
<footer class="rt-footer"><div class="rt-shell rt-copyright">© <span data-year></span> RDWAN Tech</div></footer><script src="../../forum.js" defer></script></body></html>'''


def _router_page(posts_ar: list[dict], posts_en: list[dict]) -> str:
    del posts_ar, posts_en
    schema = json.dumps({"@context":"https://schema.org","@graph":[{"@type":"WebSite","name":"Mikhbar","alternateName":"مِخبار","url":SITE+"/forum/","inLanguage":["ar","en"]},{"@type":"NewsMediaOrganization","name":"Mikhbar","alternateName":"مِخبار","url":SITE+"/forum/","founder":{"@type":"Person","name":"Radwan Abdulhadi","url":SITE+"/"}}]}, ensure_ascii=False, separators=(",",":"))
    return f'''<!DOCTYPE html><html lang="en" dir="ltr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#10130f">
<title>Mikhbar | Technology News</title><meta name="description" content="Mikhbar technology news in Arabic and English."><meta name="robots" content="index,follow"><link rel="canonical" href="{SITE}/forum/"><link rel="alternate" hreflang="ar" href="{SITE}/forum/ar/"><link rel="alternate" hreflang="en" href="{SITE}/forum/en/"><link rel="alternate" hreflang="x-default" href="{SITE}/forum/"><script>(()=>{{const lang=String((navigator.languages&&navigator.languages[0])||navigator.language||'en').toLowerCase();const edition=lang.startsWith('ar')?'ar':'en';const target='{SITE}/forum/'+edition+'/'+location.search+location.hash;if(location.href!==target)location.replace(target)}})();</script><script type="application/ld+json">{schema}</script></head><body><noscript><p><a href="/forum/ar/" lang="ar" dir="rtl">النسخة العربية</a> · <a href="/forum/en/" lang="en">English Edition</a></p></noscript></body></html>'''


def _redirect_page(target: str) -> str:
    return f'''<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="robots" content="noindex,follow"><link rel="canonical" href="{SITE}{target}"><meta http-equiv="refresh" content="0;url={target}"><script>location.replace({target!r});</script></head><body><a href="{target}">Continue</a></body></html>'''


def main() -> int:
    posts = {"ar": _load_posts("ar"), "en": _load_posts("en")}
    (FORUM / "index.html").write_text(_router_page(posts["ar"], posts["en"]), encoding="utf-8")
    written = 1
    for locale in ("ar", "en"):
        root = FORUM / locale; root.mkdir(parents=True, exist_ok=True)
        (root / "index.html").write_text(_home_page(locale, posts[locale]), encoding="utf-8"); written += 1
        for slug in CATEGORIES:
            directory = root / slug; directory.mkdir(parents=True, exist_ok=True)
            (directory / "index.html").write_text(_category_page(locale, slug, posts[locale]), encoding="utf-8"); written += 1
    for slug in CATEGORIES:
        directory = FORUM / slug; directory.mkdir(parents=True, exist_ok=True)
        (directory / "index.html").write_text(_redirect_page(f"/forum/ar/{slug}/"), encoding="utf-8"); written += 1
    print(f"Mikhbar locale pages: written={written} ar_posts={len(posts['ar'])} en_posts={len(posts['en'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
