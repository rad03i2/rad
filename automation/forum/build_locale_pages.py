from __future__ import annotations

from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORUM = ROOT / "forum"
SITE = "https://rdwan.dev"

CATEGORIES = {
    "ai": {
        "ar": ("الذكاء الاصطناعي", "أخبار النماذج والشركات والأدوات والمساعدات الذكية وتطبيقات الذكاء الاصطناعي."),
        "en": ("Artificial Intelligence", "News on AI models, companies, tools, assistants and real-world artificial intelligence applications."),
    },
    "robotics": {"ar": ("الروبوتات", "الروبوتات البشرية والصناعية والحساسات والتحكم والمصانع الذكية."), "en": ("Robotics", "Humanoid and industrial robots, sensors, control systems and intelligent manufacturing.")},
    "automation": {"ar": ("الأتمتة", "أتمتة الأعمال وسير العمل والسكربتات والوكلاء والأدوات الذكية."), "en": ("Automation", "Workflow automation, scripts, agents and tools that automate digital work.")},
    "mobile": {"ar": ("الهواتف", "Android وiPhone والأجهزة الجديدة والتحديثات والمزايا والتقنيات المحمولة."), "en": ("Mobile", "Android, iPhone, new devices, operating-system updates and mobile technology.")},
    "computers": {"ar": ("الحواسيب", "Windows وLinux والعتاد والمعالجات والرسوميات والحوسبة الشخصية ومراكز البيانات."), "en": ("Computing", "Windows, Linux, hardware, processors, graphics, personal computing and data centers.")},
    "apps": {"ar": ("التطبيقات والبرامج", "برامج سطح المكتب وتطبيقات الهاتف والخدمات الرقمية والأدوات الجديدة."), "en": ("Apps & Software", "Desktop software, mobile apps, digital services and new productivity tools.")},
    "web": {"ar": ("الويب", "المواقع والمتصفحات ومحركات البحث والخدمات وتقنيات تطوير الويب."), "en": ("Web", "Websites, browsers, search engines, online services and modern web technologies.")},
    "social": {"ar": ("التواصل الاجتماعي", "YouTube وTikTok وInstagram وFacebook والمنصات الاجتماعية وتحديثاتها."), "en": ("Social Media", "YouTube, TikTok, Instagram, Facebook and the platforms shaping social media.")},
    "security": {"ar": ("الأمن التقني", "التحديثات الأمنية والخصوصية والحماية الرقمية والثغرات المهمة للمستخدمين."), "en": ("Cybersecurity", "Security updates, privacy, digital protection and vulnerabilities that matter to users.")},
    "announcements": {"ar": ("إعلانات المنصة", "تحديثات RDWAN Tech وإعلانات تطوير المنصة."), "en": ("Announcements", "Updates and product announcements from RDWAN Tech.")},
}

UI = {
    "ar": {
        "dir": "rtl", "edition": "النسخة العربية", "home": "الرئيسية", "about": "عنّي", "projects": "المشاريع", "forum": "المنتدى",
        "coverage": "تغطية تقنية على مدار الساعة", "tagline": "الأخبار والشروحات والتحليلات في التقنية، الذكاء الاصطناعي، الروبوتات، الأتمتة، الهواتف والحواسيب والبرمجيات.",
        "important": "الأهم الآن", "allNews": "كل الأخبار", "explore": "استكشف بسرعة", "search": "ابحث في الأخبار والمواضيع والتقنيات...",
        "searchNote": "بحث فوري داخل المنشورات", "latest": "أحدث المنشورات", "latestDesc": "الأحدث أولًا، مع تحديث مستمر على مدار اليوم.",
        "noResults": "لا توجد نتائج مطابقة", "tryDifferent": "جرّب عبارة بحث مختلفة أو استعرض أحد الأقسام التقنية.", "more": "عرض المزيد",
        "topics": "عالم التقنية في مكان واحد", "topicsDesc": "بنية موضوعية واضحة تساعد القارئ ومحركات البحث على الوصول إلى المحتوى المتخصص.",
        "newsletter": "ابقَ قريبًا من الجديد", "newsletterDesc": "اشترك في التحديثات للحصول على أهم ما نُشر في RDWAN Tech.", "subscribe": "اشترك في التحديثات",
        "skip": "انتقل إلى المحتوى", "menu": "فتح قائمة التنقل", "nav": "التنقل الرئيسي",
    },
    "en": {
        "dir": "ltr", "edition": "English Edition", "home": "Home", "about": "About", "projects": "Projects", "forum": "Tech News",
        "coverage": "Technology coverage around the clock", "tagline": "News, explainers and analysis across technology, artificial intelligence, robotics, automation, mobile, computing and software.",
        "important": "Top stories", "allNews": "All news", "explore": "Explore", "search": "Search news, topics and technologies...",
        "searchNote": "Instant search across published stories", "latest": "Latest stories", "latestDesc": "Newest first, continuously updated throughout the day.",
        "noResults": "No matching results", "tryDifferent": "Try a different search phrase or explore one of the technology sections.", "more": "Load more",
        "topics": "Technology in one place", "topicsDesc": "A clear topic structure for readers and search engines to discover specialized coverage.",
        "newsletter": "Stay close to what’s next", "newsletterDesc": "Subscribe for the most important RDWAN Tech updates.", "subscribe": "Subscribe",
        "skip": "Skip to content", "menu": "Open navigation", "nav": "Main navigation",
    },
}


def category_nav(locale: str, prefix: str = "./") -> str:
    labels = [("ai",), ("robotics",), ("automation",), ("mobile",), ("computers",), ("apps",), ("web",), ("social",), ("security",)]
    home = "الرئيسية" if locale == "ar" else "Home"
    links = [f'<a href="{prefix}" aria-current="page">{home}</a>']
    for (slug,) in labels:
        label = CATEGORIES[slug][locale][0]
        links.append(f'<a href="{prefix}{slug}/">{escape(label)}</a>')
    return "".join(links)


def head(locale: str, path: str, title: str, description: str) -> str:
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
<meta property="og:type" content="website"><meta property="og:site_name" content="RDWAN Tech"><meta property="og:locale" content="{'ar_IQ' if locale == 'ar' else 'en_US'}">
<meta property="og:title" content="{escape(title, quote=True)}"><meta property="og:description" content="{escape(description, quote=True)}"><meta property="og:url" content="{SITE}{path}"><meta property="og:image" content="{SITE}/assets/social/home.jpg">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(title, quote=True)}"><meta name="twitter:description" content="{escape(description, quote=True)}"><meta name="twitter:image" content="{SITE}/assets/social/home.jpg">'''


def header(locale: str, depth: int) -> str:
    ui = UI[locale]
    root = "../" * depth
    forum_root = "../" if depth > 2 else "./"
    return f'''<header class="site-header"><div class="container header-inner">
<a class="brand" href="{root}" aria-label="{'رضوان عبدالهادي، الرئيسية' if locale == 'ar' else 'Radwan Abdulhadi, home'}"><span class="brand-mark">ر.</span><span class="brand-text">رضوان عبدالهادي<small lang="en" dir="ltr">DEVELOPER PORTFOLIO</small></span></a>
<button class="menu-button" type="button" aria-label="{ui['menu']}" aria-expanded="false" aria-controls="navigation"><svg aria-hidden="true" viewBox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h16"/></svg></button>
<nav class="nav-links" id="navigation" aria-label="{ui['nav']}"><a href="{root}#home">{ui['home']}</a><a href="{root}#about">{ui['about']}</a><a href="{root}#projects">{ui['projects']}</a><a class="rad-nav-forum" href="{forum_root}" aria-current="page">{ui['forum']}</a></nav>
</div></header>'''


def home_page(locale: str) -> str:
    ui = UI[locale]
    title = "RDWAN Tech — المنتدى التقني" if locale == "ar" else "RDWAN Tech — Technology News, AI, Robotics and Automation"
    desc = "منصة تقنية عربية تغطي الذكاء الاصطناعي والروبوتات والأتمتة والهواتف والحواسيب والتطبيقات والويب." if locale == "ar" else "RDWAN Tech covers AI, robotics, automation, mobile, computing, software, the web and digital platforms in English."
    topics = "".join(
        f'<a class="rt-category-box" href="./{slug}/"><span>{i:02d} · {slug.upper()}</span><h3>{escape(CATEGORIES[slug][locale][0])}</h3><p>{escape(CATEGORIES[slug][locale][1])}</p></a>'
        for i, slug in enumerate(["ai","robotics","automation","mobile","computers","apps","web","social","security"], 1)
    )
    return f'''<!DOCTYPE html><html lang="{locale}" dir="{ui['dir']}"><head>
{head(locale, f'/forum/{locale}/', title, desc)}
<link rel="alternate" type="application/rss+xml" title="RDWAN Tech {locale.upper()}" href="{SITE}/forum/feed-{locale}.xml">
<link rel="stylesheet" href="../../styles.css"><link rel="stylesheet" href="../forum.css"><link rel="stylesheet" href="../forum-media.css"><link rel="icon" type="image/png" href="../../assets/images/radwan-favicon.png">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"CollectionPage","name":"RDWAN Tech","url":"{SITE}/forum/{locale}/","inLanguage":"{locale}"}}</script>
</head><body class="rt-locale-{locale}" data-locale="{locale}">
<a class="skip-link" href="#main">{ui['skip']}</a>{header(locale,2)}
<main class="rt-main" id="main">
<div class="rt-topline"><div class="rt-shell rt-topline-inner"><span class="rt-live">{ui['coverage']}</span><span class="rt-edition" dir="ltr">RDWAN TECH · {ui['edition'].upper()}</span></div></div>
<section class="rt-brandline"><div class="rt-shell rt-brandrow"><div class="rt-wordmark"><strong>RDWAN Tech</strong><b>TECH</b></div><p class="rt-tagline">{ui['tagline']}</p></div></section>
<nav class="rt-categories" aria-label="Sections"><div class="rt-shell rt-category-scroll">{category_nav(locale)}</div></nav>
<div class="rt-shell">
<section class="rt-hero" aria-label="Top content"><a class="rt-lead" id="rtLead" href="#latest"><img class="rt-lead-media" id="rtLeadImage" src="/assets/social/home.jpg" alt="" width="1600" height="900" fetchpriority="high"><span class="rt-label" id="rtLeadCategory">RDWAN Tech</span><h1 id="rtLeadTitle">{ui['latest']}</h1><p id="rtLeadExcerpt">{ui['tagline']}</p><div class="rt-story-meta"><span id="rtLeadDate"></span><span id="rtLeadRead"></span><span>Radwan Abdulhadi</span></div></a>
<aside class="rt-side"><section class="rt-side-panel"><div class="rt-panel-head"><h2>{ui['important']}</h2><a href="#latest">{ui['allNews']}</a></div><div class="rt-now-list" id="rtNowList"></div></section><section class="rt-side-panel"><div class="rt-panel-head"><h2>{ui['explore']}</h2></div><div class="rt-topic-grid"><a class="rt-topic-card" href="./ai/"><b>{CATEGORIES['ai'][locale][0]}</b><span>AI</span></a><a class="rt-topic-card" href="./robotics/"><b>{CATEGORIES['robotics'][locale][0]}</b><span>ROBOTICS</span></a><a class="rt-topic-card" href="./mobile/"><b>{CATEGORIES['mobile'][locale][0]}</b><span>MOBILE</span></a><a class="rt-topic-card" href="./apps/"><b>{CATEGORIES['apps'][locale][0]}</b><span>APPS</span></a></div></section></aside></section>
<div class="rt-toolbar"><label class="rt-search"><svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" d="m21 21-4.35-4.35M10.8 18a7.2 7.2 0 1 1 0-14.4 7.2 7.2 0 0 1 0 14.4Z"/></svg><input id="rtSearch" type="search" autocomplete="off" placeholder="{ui['search']}" aria-label="{ui['search']}"></label><span class="rt-view-note">{ui['searchNote']}</span></div>
<section class="rt-section" id="latest"><header class="rt-section-head"><div><h2>{ui['latest']}</h2><p>{ui['latestDesc']}</p></div><span class="rt-count" id="rtCount">0</span></header><div class="rt-feed" id="rtFeed"></div><div class="rt-feed-empty" id="rtEmpty" hidden><b>{ui['noResults']}</b><p>{ui['tryDifferent']}</p></div><button class="rt-load-more" id="rtLoadMore" type="button">{ui['more']}</button></section>
<section class="rt-section"><header class="rt-section-head"><div><h2>{ui['topics']}</h2><p>{ui['topicsDesc']}</p></div></header><div class="rt-category-showcase">{topics}</div></section>
<section class="rt-newsletter"><div><h2>{ui['newsletter']}</h2><p>{ui['newsletterDesc']}</p></div><a href="https://omniform1.com/forms/v1/landingPage/6aa951449b0f973742e3f90d/6aa9b7a1f85082d5ccd3f79c">{ui['subscribe']}</a></section>
</div></main><footer class="rt-footer"><div class="rt-shell rt-copyright">© <span data-year></span> RDWAN Tech</div></footer><script src="../forum.js" defer></script></body></html>'''


def category_page(locale: str, slug: str) -> str:
    ui = UI[locale]
    label, desc = CATEGORIES[slug][locale]
    title = f"{label} — RDWAN Tech"
    path = f"/forum/{locale}/{slug}/"
    root = "../../../"
    return f'''<!DOCTYPE html><html lang="{locale}" dir="{ui['dir']}"><head>{head(locale,path,title,desc)}
<link rel="stylesheet" href="{root}styles.css"><link rel="stylesheet" href="../../forum.css"><link rel="stylesheet" href="../../forum-media.css"><link rel="icon" type="image/png" href="{root}assets/images/radwan-favicon.png"></head>
<body class="rt-locale-{locale}" data-locale="{locale}" data-category="{slug}"><a class="skip-link" href="#main">{ui['skip']}</a>{header(locale,3)}
<main class="rt-main" id="main"><nav class="rt-categories"><div class="rt-shell rt-category-scroll">{category_nav(locale,'../')}</div></nav><div class="rt-shell"><section class="rt-category-hero"><nav class="rt-breadcrumbs"><a href="../">RDWAN Tech</a><span>›</span><span>{escape(label)}</span></nav><div class="rt-category-title"><span class="rt-label">{slug.upper()}</span><h1>{escape(label)}</h1><p>{escape(desc)}</p></div></section>
<div class="rt-toolbar"><label class="rt-search"><svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" d="m21 21-4.35-4.35M10.8 18a7.2 7.2 0 1 1 0-14.4 7.2 7.2 0 0 1 0 14.4Z"/></svg><input id="rtSearch" type="search" autocomplete="off" placeholder="{ui['search']}"></label><span class="rt-view-note">{ui['searchNote']}</span></div><section class="rt-section"><header class="rt-section-head"><div><h2>{ui['latest']}</h2><p>{escape(label)}</p></div><span class="rt-count" id="rtCount">0</span></header><div class="rt-feed" id="rtFeed"></div><div class="rt-feed-empty" id="rtEmpty" hidden><b>{ui['noResults']}</b><p>{ui['tryDifferent']}</p></div><button class="rt-load-more" id="rtLoadMore" type="button">{ui['more']}</button></section></div></main><footer class="rt-footer"><div class="rt-shell rt-copyright">© <span data-year></span> RDWAN Tech</div></footer><script src="../../forum.js" defer></script></body></html>'''


def router_page() -> str:
    return f'''<!DOCTYPE html><html lang="en" dir="ltr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>RDWAN Tech</title><meta name="description" content="RDWAN Tech technology news in Arabic and English."><meta name="robots" content="index,follow"><link rel="canonical" href="{SITE}/forum/"><link rel="alternate" hreflang="ar" href="{SITE}/forum/ar/"><link rel="alternate" hreflang="en" href="{SITE}/forum/en/"><link rel="alternate" hreflang="x-default" href="{SITE}/forum/"><script>(()=>{{const langs=navigator.languages?.length?navigator.languages:[navigator.language||'en'];const first=String(langs[0]||'en').toLowerCase();const target=first.startsWith('ar')?'/forum/ar/':'/forum/en/';location.replace(target)}})();</script></head><body><noscript><p><a href="/forum/ar/">العربية</a> · <a href="/forum/en/">English</a></p></noscript></body></html>'''


def redirect_page(target: str) -> str:
    return f'''<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="robots" content="noindex,follow"><link rel="canonical" href="{SITE}{target}"><meta http-equiv="refresh" content="0;url={target}"><script>location.replace({target!r});</script></head><body><a href="{target}">Continue</a></body></html>'''


def main() -> int:
    (FORUM / "index.html").write_text(router_page(), encoding="utf-8")
    written = 1
    for locale in ("ar", "en"):
        root = FORUM / locale
        root.mkdir(parents=True, exist_ok=True)
        (root / "index.html").write_text(home_page(locale), encoding="utf-8")
        written += 1
        for slug in CATEGORIES:
            directory = root / slug
            directory.mkdir(parents=True, exist_ok=True)
            (directory / "index.html").write_text(category_page(locale, slug), encoding="utf-8")
            written += 1
    for slug in CATEGORIES:
        directory = FORUM / slug
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "index.html").write_text(redirect_page(f"/forum/ar/{slug}/"), encoding="utf-8")
        written += 1
    print(f"RDWAN Tech locale pages: written={written}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
