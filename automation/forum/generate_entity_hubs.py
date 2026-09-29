from __future__ import annotations

import json
import re
import shutil
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from html import escape
from pathlib import Path

from entity_hub_config import (
    ENTITY_CANDIDATES,
    GENERIC_THEME_TERMS,
    MIN_PAIRED_STORIES,
    MIN_THEME_COUNT,
    PILLAR_BY_CATEGORY,
)

ROOT = Path(__file__).resolve().parents[2]
FORUM = ROOT / "forum"
ORIGIN = "https://mikhbar.website"
MANIFEST = FORUM / "entity-hubs.json"

CATEGORY_LABELS = {
    "ai": {"ar": "الذكاء الاصطناعي", "en": "Artificial Intelligence"},
    "security": {"ar": "الأمن السيبراني", "en": "Cybersecurity"},
    "automation": {"ar": "الأتمتة", "en": "Automation"},
    "robotics": {"ar": "الروبوتات", "en": "Robotics"},
    "apps": {"ar": "التطبيقات والبرامج", "en": "Apps & Software"},
    "web": {"ar": "الويب", "en": "Web"},
    "mobile": {"ar": "الهواتف", "en": "Mobile"},
    "computers": {"ar": "الحواسيب", "en": "Computing"},
    "social": {"ar": "التواصل الاجتماعي", "en": "Social Media"},
}

PILLAR_LABELS = {
    "artificial-intelligence": {"ar": "دليل الذكاء الاصطناعي", "en": "Artificial Intelligence Guide"},
    "cybersecurity": {"ar": "دليل الأمن السيبراني", "en": "Cybersecurity Guide"},
    "robotics": {"ar": "دليل الروبوتات", "en": "Robotics Guide"},
}


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError):
        return default


def save_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def public_path(value: str | None) -> str:
    path = str(value or "").strip()
    if not path:
        return ""
    if path.startswith("/forum/"):
        path = path[len("/forum"):]
    if not path.startswith("/"):
        path = "/" + path
    if not path.endswith("/"):
        path += "/"
    return path


def normalize_term(value: str | None) -> str:
    text = unicodedata.normalize("NFKD", str(value or "")).lower()
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[\u064B-\u065F\u0670\u0640]", "", text)
    text = text.translate(str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا", "ى": "ي", "ؤ": "و", "ئ": "ي"}))
    text = re.sub(r"[^\w+#.\- ]+", " ", text, flags=re.UNICODE)
    return " ".join(text.split()).strip()


GENERIC_NORMALIZED = {normalize_term(value) for value in GENERIC_THEME_TERMS}


def unique_strings(values, limit: int = 50) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values or []:
        text = " ".join(str(value or "").split()).strip()
        key = normalize_term(text)
        if not text or not key or key in seen:
            continue
        seen.add(key)
        result.append(text)
        if len(result) >= limit:
            break
    return result


def load_posts(locale: str) -> list[dict]:
    path = FORUM / f"posts-{locale}.json"
    if locale == "ar" and not path.exists():
        path = FORUM / "posts.json"
    payload = load_json(path, {"posts": []})
    if isinstance(payload, list):
        return list(payload)
    return list((payload or {}).get("posts", []))


def content_record(post: dict) -> dict:
    raw = str(post.get("contentFile") or "").strip().replace("\\", "/")
    if not raw:
        return {}
    candidate = (ROOT / raw.lstrip("/")).resolve()
    content_root = (FORUM / "content").resolve()
    try:
        candidate.relative_to(content_root)
    except ValueError:
        return {}
    return load_json(candidate, {}) if candidate.is_file() else {}


def locale_view(post: dict, locale: str) -> dict:
    record = content_record(post)
    if not record:
        return {}
    return ((record.get("locales") or {}).get(locale) or {})


def semantic_fields(post: dict, locale: str) -> tuple[list[str], list[str], str]:
    view = locale_view(post, locale)
    entities = unique_strings(list(post.get("entities") or []) + list(view.get("entities") or []), 30)
    tags = unique_strings(list(post.get("tags") or []) + list(view.get("tags") or []), 30)
    title = str(post.get("title") or view.get("title") or "").strip()
    return entities, tags, title


def alias_set(spec: dict, locale: str) -> set[str]:
    return {
        normalize_term(alias)
        for alias in spec.get("aliases", {}).get(locale, ())
        if normalize_term(alias)
    }


def contains_alias(title: str, aliases: set[str]) -> bool:
    haystack = f" {normalize_term(title)} "
    return any(f" {alias} " in haystack for alias in aliases if alias)


def post_matches(post: dict, locale: str, spec: dict) -> bool:
    aliases = alias_set(spec, locale)
    entities, tags, title = semantic_fields(post, locale)
    values = {normalize_term(value) for value in [*entities, *tags]}
    if aliases & values:
        return True
    return contains_alias(title, aliases)


def top_themes(posts: list[dict], locale: str, spec: dict, limit: int = 8) -> list[tuple[str, int]]:
    alias_norm = alias_set(spec, locale)
    counts: Counter[str] = Counter()
    display: dict[str, str] = {}
    for post in posts:
        _, tags, _ = semantic_fields(post, locale)
        for tag in tags:
            key = normalize_term(tag)
            if not key or key in GENERIC_NORMALIZED or key in alias_norm:
                continue
            counts[key] += 1
            display.setdefault(key, tag)
    return [(display[key], count) for key, count in counts.most_common(limit)]


def paired_story_data(posts_by_locale: dict[str, list[dict]]) -> tuple[dict[str, dict[str, dict]], dict[str, set[str]]]:
    by_id: dict[str, dict[str, dict]] = defaultdict(dict)
    for locale, posts in posts_by_locale.items():
        for post in posts:
            story_id = str(post.get("id") or "").strip()
            if story_id:
                by_id[story_id][locale] = post

    matched: dict[str, set[str]] = {}
    for slug, spec in ENTITY_CANDIDATES.items():
        ids: set[str] = set()
        for story_id, pair in by_id.items():
            if "ar" not in pair or "en" not in pair:
                continue
            if post_matches(pair["ar"], "ar", spec) or post_matches(pair["en"], "en", spec):
                ids.add(story_id)
        matched[slug] = ids
    return by_id, matched


def qualify_entities(posts_by_locale: dict[str, list[dict]]) -> dict[str, dict]:
    by_id, matched = paired_story_data(posts_by_locale)
    qualified: dict[str, dict] = {}

    for slug, spec in ENTITY_CANDIDATES.items():
        story_ids = matched[slug]
        if len(story_ids) < MIN_PAIRED_STORIES:
            continue

        locale_posts = {
            locale: [by_id[story_id][locale] for story_id in story_ids if locale in by_id[story_id]]
            for locale in ("ar", "en")
        }
        themes = {
            locale: top_themes(locale_posts[locale], locale, spec)
            for locale in ("ar", "en")
        }
        combined_theme_keys = {
            normalize_term(label)
            for locale in ("ar", "en")
            for label, _ in themes[locale]
        }
        if len(combined_theme_keys) < MIN_THEME_COUNT:
            continue

        categories = Counter(
            str(pair["en"].get("categorySlug") or pair["ar"].get("categorySlug") or "")
            for story_id in story_ids
            if (pair := by_id[story_id])
        )
        categories.pop("", None)
        pillars = [
            PILLAR_BY_CATEGORY[category]
            for category, _ in categories.most_common()
            if category in PILLAR_BY_CATEGORY
        ]

        qualified[slug] = {
            "slug": slug,
            "name": spec["name"],
            "storyIds": sorted(story_ids),
            "storyCount": len(story_ids),
            "categories": dict(categories),
            "pillars": list(dict.fromkeys(pillars)),
            "themes": {
                locale: [{"label": label, "count": count} for label, count in themes[locale]]
                for locale in ("ar", "en")
            },
            "posts": locale_posts,
        }

    # Add graph relationships only among qualified entities.
    for slug, entity in qualified.items():
        current_ids = set(entity["storyIds"])
        related = []
        for other_slug, other in qualified.items():
            if other_slug == slug:
                continue
            shared = len(current_ids & set(other["storyIds"]))
            if shared:
                related.append({"slug": other_slug, "name": other["name"], "sharedStories": shared})
        entity["related"] = sorted(
            related,
            key=lambda item: (-item["sharedStories"], item["name"].casefold()),
        )[:4]

    return qualified


def date_key(post: dict) -> tuple[float, str]:
    raw = str(post.get("dateModified") or post.get("date") or "")
    try:
        stamp = datetime.fromisoformat(raw.replace("Z", "+00:00")).timestamp()
    except Exception:
        stamp = 0.0
    return stamp, str(post.get("title") or "")


def article_rows(posts: list[dict], locale: str) -> str:
    rows = []
    for post in sorted(posts, key=date_key, reverse=True):
        href = public_path(post.get("url"))
        title = str(post.get("title") or "").strip()
        excerpt_text = str(post.get("excerpt") or "").strip()
        date = str(post.get("dateLabel") or str(post.get("date") or "")[:10]).strip()
        category = str(post.get("category") or "").strip()
        if not href or not title:
            continue
        rows.append(
            '<article class="rt-feed-item" data-entity-story="true">'
            f'<a href="{escape(href, quote=True)}"><div class="rt-feed-copy">'
            f'<h3>{escape(title)}</h3>'
            f'{f"<p>{escape(excerpt_text)}</p>" if excerpt_text else ""}'
            f'<div class="rt-feed-time">{escape(" · ".join(x for x in (category, date) if x))}</div>'
            '</div></a></article>'
        )
    return "".join(rows)


def schema_json(locale: str, entity: dict) -> str:
    canonical = f"{ORIGIN}/{locale}/entities/{entity['slug']}/"
    item_list = []
    for position, post in enumerate(sorted(entity["posts"][locale], key=date_key, reverse=True)[:20], 1):
        href = public_path(post.get("url"))
        if not href:
            continue
        item_list.append({
            "@type": "ListItem",
            "position": position,
            "url": ORIGIN + href,
            "name": str(post.get("title") or ""),
        })

    payload = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "CollectionPage",
                "@id": canonical + "#page",
                "url": canonical,
                "name": f"{entity['name']} — Mikhbar",
                "inLanguage": locale,
                "isPartOf": {"@id": ORIGIN + "/#website"},
                "publisher": {"@id": ORIGIN + "/#publisher"},
                "about": {"@type": "Organization", "name": entity["name"]},
                "mainEntity": {
                    "@type": "ItemList",
                    "numberOfItems": entity["storyCount"],
                    "itemListElement": item_list,
                },
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": "مِخبار" if locale == "ar" else "Mikhbar",
                        "item": f"{ORIGIN}/{locale}/",
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": "الكيانات" if locale == "ar" else "Entities",
                        "item": f"{ORIGIN}/{locale}/entities/",
                    },
                    {
                        "@type": "ListItem",
                        "position": 3,
                        "name": entity["name"],
                    },
                ],
            },
        ],
    }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")


def entity_page(locale: str, entity: dict) -> str:
    is_ar = locale == "ar"
    other = "en" if is_ar else "ar"
    name = entity["name"]
    canonical = f"{ORIGIN}/{locale}/entities/{entity['slug']}/"
    other_url = f"{ORIGIN}/{other}/entities/{entity['slug']}/"
    title = (
        f"{name}: الأخبار والتحديثات والتغطية التقنية | مِخبار"
        if is_ar else
        f"{name}: News, Updates & Technology Coverage | Mikhbar"
    )
    description = (
        f"مركز تغطية مِخبار حول {name}: أحدث الأخبار والتحديثات والموضوعات المرتبطة، مع أرشيف مباشر لجميع التغطيات المنشورة."
        if is_ar else
        f"Mikhbar's {name} coverage hub: recent news, related themes and a direct archive of all published reporting."
    )
    deck = (
        f"صفحة موضوعية تجمع تغطية مِخبار عن {name} في مكان واحد، وتربط الأخبار الجديدة والقديمة بالموضوعات والأدلة ذات الصلة."
        if is_ar else
        f"A focused Mikhbar hub that brings {name} reporting together and connects recent and older stories with relevant topics and evergreen guides."
    )

    category_cards = []
    for category, count in sorted(entity["categories"].items(), key=lambda item: (-item[1], item[0])):
        label = CATEGORY_LABELS.get(category, {}).get(locale, category)
        category_cards.append(
            f'<a class="rt-topic-card" href="/{locale}/{escape(category, quote=True)}/">'
            f'<b>{escape(label)}</b><span>{count} {"خبرًا" if is_ar else "stories"}</span></a>'
        )

    theme_chips = "".join(
        f'<span class="rt-entity-theme">{escape(theme["label"])}</span>'
        for theme in entity["themes"][locale]
    )

    pillar_links = []
    for pillar in entity["pillars"]:
        label = PILLAR_LABELS.get(pillar, {}).get(locale, pillar)
        pillar_links.append(
            f'<a class="rt-topic-card" href="/{locale}/guides/{escape(pillar, quote=True)}/">'
            f'<b>{escape(label)}</b><span>{"مرجع دائم" if is_ar else "Evergreen reference"}</span></a>'
        )

    related_links = []
    for related in entity["related"]:
        related_links.append(
            f'<a class="rt-topic-card" href="/{locale}/entities/{escape(related["slug"], quote=True)}/">'
            f'<b>{escape(related["name"])}</b>'
            f'<span>{related["sharedStories"]} {"تغطيات مشتركة" if is_ar else "shared stories"}</span></a>'
        )

    latest_label = "أحدث التغطيات" if is_ar else "Latest coverage"
    coverage_label = "خريطة التغطية" if is_ar else "Coverage map"
    themes_label = "موضوعات متكررة في التغطية" if is_ar else "Recurring coverage themes"
    guides_label = "أدلة مرتبطة" if is_ar else "Related evergreen guides"
    related_label = "كيانات مرتبطة" if is_ar else "Related entities"
    count_label = "تغطية منشورة" if is_ar else "published stories"
    lang_label = "EN" if is_ar else "عربي"
    entity_index_label = "كل الكيانات" if is_ar else "All entities"

    style = """.rt-entity-stats{display:flex;gap:12px;flex-wrap:wrap;margin-top:16px}.rt-entity-stat{border:1px solid #e6e6e1;border-radius:14px;padding:10px 14px;background:#fff}.rt-entity-themes{display:flex;gap:8px;flex-wrap:wrap}.rt-entity-theme{border:1px solid #e6e6e1;border-radius:999px;padding:7px 11px;background:#fff;font-size:.92rem}.rt-entity-story-list{display:grid;gap:0}.rt-entity-story-list .rt-feed-item{border-top:1px solid #e8e8e4}"""

    return f'''<!DOCTYPE html><html lang="{locale}" dir="{"rtl" if is_ar else "ltr"}"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#ffffff">
<title>{escape(title)}</title><meta name="description" content="{escape(description, quote=True)}"><meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
<link rel="canonical" href="{canonical}"><link rel="alternate" hreflang="ar" href="{ORIGIN}/ar/entities/{entity["slug"]}/"><link rel="alternate" hreflang="en" href="{ORIGIN}/en/entities/{entity["slug"]}/"><link rel="alternate" hreflang="x-default" href="{ORIGIN}/ar/entities/{entity["slug"]}/">
<meta property="og:type" content="website"><meta property="og:site_name" content="{"مِخبار" if is_ar else "Mikhbar"}"><meta property="og:title" content="{escape(title, quote=True)}"><meta property="og:description" content="{escape(description, quote=True)}"><meta property="og:url" content="{canonical}">
<link rel="stylesheet" href="/styles.css"><link rel="stylesheet" href="/forum.css?v=20260929-layout4"><link rel="stylesheet" href="/forum-media.css?v=20260929-layout4"><link rel="icon" href="/assets/brand/mikhbar/06-web-ready/favicon/favicon.ico"><style>{style}</style>
<script type="application/ld+json">{schema_json(locale, entity)}</script></head>
<body class="rt-locale-{locale}" data-entity-hub="true" data-entity="{escape(entity["slug"], quote=True)}" data-entity-stories="{entity["storyCount"]}">
<header class="rt-site-header"><div class="rt-navbar"><a class="mikhbar-brand" href="/{locale}/" aria-label="{"مِخبار" if is_ar else "Mikhbar"}"><span class="mikhbar-brand-mark"><img src="/assets/brand/mikhbar/06-web-ready/icon/mikhbar-logo-mark.png" alt="" width="64" height="64"></span><span class="mikhbar-brand-copy"><strong>{"مِخبار" if is_ar else "Mikhbar"}</strong><small dir="ltr">MIKHBAR</small></span></a>
<nav class="nav-links rt-platform-nav"><a href="/{locale}/">{"الرئيسية" if is_ar else "Home"}</a><a href="/{locale}/entities/">{entity_index_label}</a><a href="/{locale}/guides/">{"الأدلة" if is_ar else "Guides"}</a><a class="rt-lang-switch" href="/{other}/entities/{entity["slug"]}/" lang="{other}">{lang_label}</a></nav></div></header>
<main class="rt-main" id="main"><div class="rt-shell"><section class="rt-category-hero"><nav class="rt-breadcrumbs"><a href="/{locale}/">{"مِخبار" if is_ar else "Mikhbar"}</a><span>›</span><a href="/{locale}/entities/">{entity_index_label}</a><span>›</span><span>{escape(name)}</span></nav><div class="rt-category-title"><span class="rt-label">ENTITY COVERAGE</span><h1>{escape(name)}</h1><p>{escape(deck)}</p><div class="rt-entity-stats"><span class="rt-entity-stat"><b>{entity["storyCount"]}</b> {count_label}</span><span class="rt-entity-stat"><b>{len(entity["categories"])}</b> {"أقسام" if is_ar else "sections"}</span></div></div></section>
<section class="rt-section"><header class="rt-section-head"><div><h2>{coverage_label}</h2></div></header><div class="rt-topic-grid">{"".join(category_cards)}</div></section>
<section class="rt-section"><header class="rt-section-head"><div><h2>{themes_label}</h2></div></header><div class="rt-entity-themes">{theme_chips}</div></section>
{f'<section class="rt-section"><header class="rt-section-head"><div><h2>{guides_label}</h2></div></header><div class="rt-topic-grid">{"".join(pillar_links)}</div></section>' if pillar_links else ""}
{f'<section class="rt-section"><header class="rt-section-head"><div><h2>{related_label}</h2></div></header><div class="rt-topic-grid">{"".join(related_links)}</div></section>' if related_links else ""}
<section class="rt-section"><header class="rt-section-head"><div><h2>{latest_label}</h2></div><span class="rt-count">{entity["storyCount"]}</span></header><div class="rt-feed rt-entity-story-list">{article_rows(entity["posts"][locale], locale)}</div></section>
</div></main><footer class="rt-footer"><div class="rt-shell rt-copyright">© <span data-year></span> {"مِخبار" if is_ar else "Mikhbar"} · <a href="/{locale}/entities/">{entity_index_label}</a></div></footer><script src="/forum.js" defer></script></body></html>'''


def entity_index_page(locale: str, entities: dict[str, dict]) -> str:
    is_ar = locale == "ar"
    other = "en" if is_ar else "ar"
    canonical = f"{ORIGIN}/{locale}/entities/"
    title = "كيانات التقنية في مِخبار: الشركات والمنصات الأكثر تغطية" if is_ar else "Technology Entities on Mikhbar: Companies & Platforms"
    description = (
        "دليل كيانات مِخبار يجمع الشركات والمنصات التقنية التي تمتلك تغطية كافية ومستمرة، مع روابط إلى الأخبار والأدلة ذات الصلة."
        if is_ar else
        "Mikhbar's entity directory groups technology companies and platforms with substantial ongoing coverage, linking their news and related evergreen guides."
    )
    deck = (
        "لا تظهر هنا كل شركة ورد اسمها في خبر؛ نعرض فقط الكيانات التي تجاوزت حدًا أدنى من التغطية حتى تبقى الصفحات مفيدة وغير رقيقة."
        if is_ar else
        "This is not a page for every name mentioned in a story. Only entities with enough sustained coverage qualify, keeping the directory useful and avoiding thin pages."
    )
    cards = []
    for slug, entity in sorted(entities.items(), key=lambda item: (-item[1]["storyCount"], item[1]["name"].casefold())):
        categories = [
            CATEGORY_LABELS.get(category, {}).get(locale, category)
            for category, _ in sorted(entity["categories"].items(), key=lambda item: (-item[1], item[0]))[:3]
        ]
        cards.append(
            f'<a class="rt-topic-card" data-entity-card="true" href="/{locale}/entities/{escape(slug, quote=True)}/">'
            f'<b>{escape(entity["name"])}</b><span>{entity["storyCount"]} {"تغطية" if is_ar else "stories"}'
            f'{f" · {escape("، ".join(categories))}" if categories else ""}</span></a>'
        )

    schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "@id": canonical + "#page",
        "url": canonical,
        "name": title,
        "inLanguage": locale,
        "isPartOf": {"@id": ORIGIN + "/#website"},
        "publisher": {"@id": ORIGIN + "/#publisher"},
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": len(entities),
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": index,
                    "name": entity["name"],
                    "url": f"{ORIGIN}/{locale}/entities/{slug}/",
                }
                for index, (slug, entity) in enumerate(
                    sorted(entities.items(), key=lambda item: (-item[1]["storyCount"], item[1]["name"].casefold())),
                    1,
                )
            ],
        },
    }, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")

    return f'''<!DOCTYPE html><html lang="{locale}" dir="{"rtl" if is_ar else "ltr"}"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>{escape(title)}</title><meta name="description" content="{escape(description, quote=True)}"><meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1"><link rel="canonical" href="{canonical}"><link rel="alternate" hreflang="ar" href="{ORIGIN}/ar/entities/"><link rel="alternate" hreflang="en" href="{ORIGIN}/en/entities/"><link rel="alternate" hreflang="x-default" href="{ORIGIN}/ar/entities/"><meta property="og:type" content="website"><meta property="og:site_name" content="{"مِخبار" if is_ar else "Mikhbar"}"><meta property="og:title" content="{escape(title, quote=True)}"><meta property="og:description" content="{escape(description, quote=True)}"><meta property="og:url" content="{canonical}"><link rel="stylesheet" href="/styles.css"><link rel="stylesheet" href="/forum.css?v=20260929-layout4"><link rel="stylesheet" href="/forum-media.css?v=20260929-layout4"><script type="application/ld+json">{schema}</script></head><body class="rt-locale-{locale}" data-entity-index="true" data-entity-count="{len(entities)}"><header class="rt-site-header"><div class="rt-navbar"><a class="mikhbar-brand" href="/{locale}/"><span class="mikhbar-brand-mark"><img src="/assets/brand/mikhbar/06-web-ready/icon/mikhbar-logo-mark.png" alt="" width="64" height="64"></span><span class="mikhbar-brand-copy"><strong>{"مِخبار" if is_ar else "Mikhbar"}</strong><small dir="ltr">MIKHBAR</small></span></a><nav class="nav-links rt-platform-nav"><a href="/{locale}/">{"الرئيسية" if is_ar else "Home"}</a><a href="/{locale}/guides/">{"الأدلة" if is_ar else "Guides"}</a><a class="rt-lang-switch" href="/{other}/entities/" lang="{other}">{"EN" if is_ar else "عربي"}</a></nav></div></header><main class="rt-main" id="main"><div class="rt-shell"><section class="rt-category-hero"><div class="rt-category-title"><span class="rt-label">ENTITY DIRECTORY</span><h1>{"كيانات التقنية" if is_ar else "Technology entities"}</h1><p>{escape(deck)}</p></div></section><section class="rt-section"><header class="rt-section-head"><div><h2>{"الكيانات المؤهلة" if is_ar else "Qualified coverage hubs"}</h2></div><span class="rt-count">{len(entities)}</span></header><div class="rt-topic-grid">{"".join(cards)}</div></section></div></main><footer class="rt-footer"><div class="rt-shell rt-copyright">© <span data-year></span> {"مِخبار" if is_ar else "Mikhbar"}</div></footer><script src="/forum.js" defer></script></body></html>'''


def write_entity_pages(entities: dict[str, dict]) -> None:
    for locale in ("ar", "en"):
        root = FORUM / locale / "entities"
        if root.exists():
            shutil.rmtree(root)
        root.mkdir(parents=True, exist_ok=True)
        (root / "index.html").write_text(entity_index_page(locale, entities), encoding="utf-8")
        for slug, entity in entities.items():
            target = root / slug / "index.html"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(entity_page(locale, entity), encoding="utf-8")


def annotate_posts(posts_by_locale: dict[str, list[dict]], entities: dict[str, dict]) -> None:
    memberships: dict[str, list[str]] = defaultdict(list)
    for slug, entity in entities.items():
        for story_id in entity["storyIds"]:
            memberships[story_id].append(slug)

    for locale, posts in posts_by_locale.items():
        for post in posts:
            story_id = str(post.get("id") or "")
            hubs = memberships.get(story_id, [])
            post["entityHubs"] = [
                {
                    "slug": slug,
                    "name": entities[slug]["name"],
                    "url": f"/{locale}/entities/{slug}/",
                }
                for slug in hubs
            ]
        save_json(FORUM / f"posts-{locale}.json", {"posts": posts})
    save_json(FORUM / "posts.json", {"posts": posts_by_locale["ar"]})


def xhtml_links(ar_path: str, en_path: str) -> str:
    return (
        f'<xhtml:link rel="alternate" hreflang="ar" href="{ORIGIN}{ar_path}"/>'
        f'<xhtml:link rel="alternate" hreflang="en" href="{ORIGIN}{en_path}"/>'
        f'<xhtml:link rel="alternate" hreflang="x-default" href="{ORIGIN}{ar_path}"/>'
    )


def patch_sitemap(entities: dict[str, dict]) -> None:
    path = FORUM / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    lines = [
        line for line in text.splitlines()
        if not re.search(r"<loc>https://mikhbar\.website/(?:ar|en)/entities/", line)
    ]
    closing = "</urlset>"
    if lines and lines[-1].strip() == closing:
        lines.pop()

    today = datetime.now(timezone.utc).date().isoformat()
    ar_index = "/ar/entities/"
    en_index = "/en/entities/"
    for locale in ("ar", "en"):
        lines.append(
            f'  <url><loc>{ORIGIN}/{locale}/entities/</loc><lastmod>{today}</lastmod>'
            f'<changefreq>daily</changefreq><priority>0.75</priority>{xhtml_links(ar_index, en_index)}</url>'
        )

    for slug, entity in sorted(entities.items()):
        ar_path = f"/ar/entities/{slug}/"
        en_path = f"/en/entities/{slug}/"
        for locale in ("ar", "en"):
            path_value = f"/{locale}/entities/{slug}/"
            lines.append(
                f'  <url><loc>{ORIGIN}{path_value}</loc><lastmod>{today}</lastmod>'
                f'<changefreq>daily</changefreq><priority>0.72</priority>{xhtml_links(ar_path, en_path)}</url>'
            )
    lines.append(closing)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def patch_llms(entities: dict[str, dict]) -> None:
    path = FORUM / "llms.txt"
    text = path.read_text(encoding="utf-8")
    marker = "## Entity coverage hubs"
    if marker in text:
        text = text.split(marker, 1)[0].rstrip()
    rows = [
        "",
        marker,
        f"- Entity directory (AR): {ORIGIN}/ar/entities/",
        f"- Entity directory (EN): {ORIGIN}/en/entities/",
    ]
    for slug, entity in sorted(entities.items(), key=lambda item: (-item[1]["storyCount"], item[1]["name"])):
        rows.append(
            f"- {entity['name']} ({entity['storyCount']} stories): "
            f"{ORIGIN}/en/entities/{slug}/ | {ORIGIN}/ar/entities/{slug}/"
        )
    path.write_text(text + "\n" + "\n".join(rows) + "\n", encoding="utf-8")


ENTITY_SECTION_RE = re.compile(
    r'<section class="rt-section rt-entity-discovery" data-entity-discovery="true">.*?</section>',
    re.S,
)
ENTITY_INDEX_LINK_RE = re.compile(
    r'<a[^>]+data-entity-index-link="true"[^>]*>.*?</a>',
    re.S,
)


def entity_discovery_section(locale: str, entities: list[dict], heading: str) -> str:
    cards = "".join(
        f'<a class="rt-topic-card" href="/{locale}/entities/{escape(entity["slug"], quote=True)}/">'
        f'<b>{escape(entity["name"])}</b><span>{entity["storyCount"]} {"تغطية" if locale == "ar" else "stories"}</span></a>'
        for entity in entities
    )
    index_label = "دليل الكيانات" if locale == "ar" else "Entity directory"
    return (
        '<section class="rt-section rt-entity-discovery" data-entity-discovery="true">'
        f'<header class="rt-section-head"><div><h2>{escape(heading)}</h2></div>'
        f'<a href="/{locale}/entities/">{index_label}</a></header>'
        f'<div class="rt-topic-grid">{cards}</div></section>'
    )


def append_before_main_close(text: str, block: str) -> str:
    marker = "</div></main>"
    pos = text.rfind(marker)
    if pos >= 0:
        return text[:pos] + block + text[pos:]
    marker = "</main>"
    pos = text.rfind(marker)
    if pos >= 0:
        return text[:pos] + block + text[pos:]
    return text


def patch_internal_discovery(entities: dict[str, dict]) -> None:
    ranked = sorted(entities.values(), key=lambda item: (-item["storyCount"], item["name"].casefold()))

    for locale in ("ar", "en"):
        # Home: keep the index discoverable without a large visual block.
        home = FORUM / locale / "index.html"
        if home.exists():
            text = ENTITY_INDEX_LINK_RE.sub("", home.read_text(encoding="utf-8"))
            label = "كيانات التقنية" if locale == "ar" else "Technology entities"
            link = f'<a data-entity-index-link="true" href="/{locale}/entities/">{label}</a>'
            footer_pos = text.rfind("</footer>")
            if footer_pos >= 0:
                text = text[:footer_pos] + link + text[footer_pos:]
            home.write_text(text, encoding="utf-8")

        # Topic hubs: show entities with actual coverage in that section.
        for category in CATEGORY_LABELS:
            target = FORUM / locale / category / "index.html"
            if not target.exists():
                continue
            relevant = [
                entity for entity in ranked
                if int(entity["categories"].get(category, 0)) >= 2
            ][:6]
            text = ENTITY_SECTION_RE.sub("", target.read_text(encoding="utf-8"))
            if relevant:
                heading = "كيانات بارزة في هذا القسم" if locale == "ar" else "Key entities in this section"
                text = append_before_main_close(text, entity_discovery_section(locale, relevant, heading))
            target.write_text(text, encoding="utf-8")

        # Pillars: connect evergreen knowledge to the entity clusters.
        for category, pillar in PILLAR_BY_CATEGORY.items():
            target = FORUM / locale / "guides" / pillar / "index.html"
            if not target.exists():
                continue
            relevant = [
                entity for entity in ranked
                if int(entity["categories"].get(category, 0)) >= 2
            ][:6]
            text = ENTITY_SECTION_RE.sub("", target.read_text(encoding="utf-8"))
            if relevant:
                heading = "كيانات مرتبطة بهذا الدليل" if locale == "ar" else "Entities connected to this guide"
                text = append_before_main_close(text, entity_discovery_section(locale, relevant, heading))
            target.write_text(text, encoding="utf-8")

        # Guide index gets the highest-coverage entities, useful as a bridge:
        # Home -> Guides -> Entity Hub -> News.
        guide_index = FORUM / locale / "guides" / "index.html"
        if guide_index.exists() and ranked:
            text = ENTITY_SECTION_RE.sub("", guide_index.read_text(encoding="utf-8"))
            heading = "كيانات ذات تغطية موسعة" if locale == "ar" else "Entities with expanded coverage"
            text = append_before_main_close(text, entity_discovery_section(locale, ranked[:8], heading))
            guide_index.write_text(text, encoding="utf-8")


def manifest_payload(entities: dict[str, dict]) -> dict:
    return {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "minimumPairedStories": MIN_PAIRED_STORIES,
        "qualifiedCount": len(entities),
        "entities": [
            {
                "slug": slug,
                "name": entity["name"],
                "storyCount": entity["storyCount"],
                "storyIds": entity["storyIds"],
                "categories": entity["categories"],
                "pillars": entity["pillars"],
                "related": entity["related"],
                "urls": {
                    "ar": f"/ar/entities/{slug}/",
                    "en": f"/en/entities/{slug}/",
                },
            }
            for slug, entity in sorted(entities.items(), key=lambda item: (-item[1]["storyCount"], item[1]["name"]))
        ],
    }


def main() -> int:
    posts_by_locale = {"ar": load_posts("ar"), "en": load_posts("en")}
    entities = qualify_entities(posts_by_locale)
    if not entities:
        raise SystemExit("No Mikhbar entities passed the non-thin coverage threshold.")

    write_entity_pages(entities)
    annotate_posts(posts_by_locale, entities)
    patch_sitemap(entities)
    patch_llms(entities)
    patch_internal_discovery(entities)
    save_json(MANIFEST, manifest_payload(entities))

    summary = ", ".join(
        f"{entity['name']}={entity['storyCount']}"
        for entity in sorted(entities.values(), key=lambda item: (-item["storyCount"], item["name"]))
    )
    print(
        f"Mikhbar entity architecture: qualified={len(entities)} "
        f"threshold={MIN_PAIRED_STORIES} paired stories :: {summary}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
