from __future__ import annotations

import json
from html import escape
from pathlib import Path
from string import Template
from urllib.parse import urlparse

from common import load_json

ROOT = Path(__file__).resolve().parents[2]
FORUM = ROOT / "forum"
TEMPLATE = FORUM / "templates" / "article.html"
SITE = "https://rdwan.dev"

LOCALE_UI = {
    "ar": {
        "dir": "rtl", "og": "ar_IQ", "skip": "انتقل إلى المقال", "brandAria": "رضوان عبدالهادي، الرئيسية",
        "menuAria": "فتح قائمة التنقل", "navAria": "التنقل الرئيسي", "home": "الرئيسية", "about": "عنّي",
        "projects": "المشاريع", "forum": "مِخبار", "navHome": "الرئيسية", "navLatest": "أحدث الأخبار", "navAbout": "عن مِخبار", "navLang": "EN", "breadcrumbAria": "مسار التنقل", "published": "نُشر",
        "updated": "آخر تحديث", "read": "دقائق قراءة", "summary": "الخلاصة", "sources": "المصادر",
        "sourceNote": "صيغ هذا الخبر اعتمادًا على المصادر المدرجة أعلاه، مع فصل المعلومات المؤكدة عن ادعاءات الشركات أو التقديرات.",
        "authorName": "رضوان عبدالهادي", "authorRole": "مؤسس ومحرر مِخبار",
        "footerDesc": "منصة تقنية عربية وإنجليزية ضمن rdwan.dev.", "aboutPlatform": "عن المنصة", "aboutRdwan": "عن مِخبار",
        "editorial": "السياسة التحريرية", "trust": "الثقة", "corrections": "التصحيحات", "aiPolicy": "سياسة AI",
    },
    "en": {
        "dir": "ltr", "og": "en_US", "skip": "Skip to article", "brandAria": "Radwan Abdulhadi, home",
        "menuAria": "Open navigation", "navAria": "Main navigation", "home": "Home", "about": "About",
        "projects": "Projects", "forum": "Mikhbar", "navHome": "Home", "navLatest": "Latest", "navAbout": "About Mikhbar", "navLang": "عربي", "breadcrumbAria": "Breadcrumb", "published": "Published",
        "updated": "Updated", "read": "min read", "summary": "Key points", "sources": "Sources",
        "sourceNote": "This report was produced from the sources listed above, separating confirmed information from company claims or estimates.",
        "authorName": "Radwan Abdulhadi", "authorRole": "Founder and editor, Mikhbar",
        "footerDesc": "A bilingual technology publication within rdwan.dev.", "aboutPlatform": "Publication", "aboutRdwan": "About Mikhbar",
        "editorial": "Editorial policy", "trust": "Trust", "corrections": "Corrections", "aiPolicy": "AI policy",
    },
}


def _e(value) -> str:
    return escape(str(value or ""))


def _ea(value) -> str:
    return escape(str(value or ""), quote=True)


def _safe_http_url(value: str | None) -> str:
    value = str(value or "").strip()
    parsed = urlparse(value)
    return value if parsed.scheme in {"http", "https"} and parsed.netloc else ""


def _render_paragraph(paragraph) -> str:
    if not isinstance(paragraph, dict):
        return _e(paragraph)

    text = str(paragraph.get("text") or "")
    links = paragraph.get("links") if isinstance(paragraph.get("links"), list) else []
    placements = []
    occupied = []

    for link in links:
        if not isinstance(link, dict):
            continue
        label = str(link.get("text") or "").strip()
        url = _safe_http_url(link.get("url"))
        if not label or not url:
            continue
        start = text.find(label)
        while start >= 0 and any(not (start + len(label) <= a or start >= b) for a, b in occupied):
            start = text.find(label, start + len(label))
        if start < 0:
            continue
        end = start + len(label)
        occupied.append((start, end))
        placements.append((start, end, label, url))

    placements.sort(key=lambda item: item[0])
    if not placements:
        return _e(text)

    pieces = []
    cursor = 0
    for start, end, label, url in placements:
        pieces.append(_e(text[cursor:start]))
        pieces.append(
            f'<a href="{_ea(url)}" rel="noopener noreferrer" target="_blank">{_e(label)}</a>'
        )
        cursor = end
    pieces.append(_e(text[cursor:]))
    return "".join(pieces)


def _localized_value(value, locale: str, fallback: str = "") -> str:
    if isinstance(value, dict):
        return str(value.get(locale) or value.get("en") or value.get("ar") or fallback)
    return str(value or fallback)


def _render_inline_figure(image: dict, locale: str) -> str:
    src = _absolute(image.get("src"))
    if not src:
        return ""
    alt = _localized_value(image.get("alt"), locale, "")
    caption = _localized_value(image.get("caption"), locale, "")
    credit = str(image.get("credit") or "").strip()
    source_url = _safe_http_url(image.get("sourceUrl"))
    width = int(image.get("width") or 1200)
    height = int(image.get("height") or 675)

    caption_bits = []
    if caption:
        caption_bits.append(_e(caption))
    if credit:
        prefix = "المصدر: " if locale == "ar" else "Source: "
        if source_url:
            caption_bits.append(
                f'{_e(prefix)}<a href="{_ea(source_url)}" rel="nofollow noopener noreferrer" target="_blank">{_e(credit)}</a>'
            )
        else:
            caption_bits.append(_e(prefix + credit))
    figcaption = f'<figcaption>{" · ".join(caption_bits)}</figcaption>' if caption_bits else ""
    return (
        f'<figure class="rt-inline-media">'
        f'<img src="{_ea(src)}" alt="{_ea(alt)}" width="{width}" height="{height}" loading="lazy" decoding="async">'
        f'{figcaption}</figure>'
    )


def _inline_media_slots(section_count: int, image_count: int) -> dict[int, list[int]]:
    slots: dict[int, list[int]] = {}
    if section_count <= 0 or image_count <= 0:
        return slots
    last_slot = -1
    for image_index in range(image_count):
        raw = round((image_index + 1) * section_count / (image_count + 1)) - 1
        slot = max(0, min(section_count - 1, raw))
        if slot <= last_slot and last_slot < section_count - 1:
            slot = last_slot + 1
        last_slot = slot
        slots.setdefault(slot, []).append(image_index)
    return slots


def _absolute(value: str | None) -> str:
    value = str(value or "")
    if value.startswith("http://") or value.startswith("https://"):
        return value
    if value.startswith("/"):
        return SITE + value
    return SITE + "/" + value.lstrip("/")


def _locale_data(record: dict, locale: str) -> dict:
    locales = record.get("locales") or {}
    if locale in locales:
        return locales[locale]
    if locale == "ar" and record.get("title"):
        return {
            "title": record.get("title"), "description": record.get("description"), "deck": record.get("deck"),
            "summaryBullets": record.get("summaryBullets", []), "sections": record.get("sections", []),
            "tags": record.get("tags", []), "entities": record.get("entities", []), "category": record.get("category"),
            "dateLabel": record.get("dateLabel"), "modifiedLabel": record.get("modifiedLabel"), "readMinutes": record.get("readMinutes", 3),
        }
    return {}


def _url(record: dict, locale: str) -> str:
    urls = record.get("urls") or {}
    if urls.get(locale):
        return urls[locale]
    return f"/forum/{locale}/{record['categorySlug']}/{record['slug']}/"


def _schema(record: dict, locale: str, view: dict) -> dict:
    canonical = SITE + _url(record, locale)
    tags = view.get("tags", [])
    images = record.get("images") or {}
    image = _absolute(images.get("social") or record.get("image") or "/assets/social/home.jpg")
    schema_images = [image]
    for item in images.get("inline") or []:
        inline_src = _absolute(item.get("src"))
        if inline_src and inline_src not in schema_images:
            schema_images.append(inline_src)
    author_name = LOCALE_UI[locale]["authorName"]
    category = view.get("category") or record.get("category") or record.get("categorySlug")
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "NewsArticle",
                "@id": canonical + "#article",
                "headline": view["title"],
                "description": view["description"],
                "datePublished": record["datePublished"],
                "dateModified": record.get("dateModified", record["datePublished"]),
                "inLanguage": locale,
                "mainEntityOfPage": canonical,
                "image": schema_images,
                "author": {"@type": "Person", "name": author_name, "url": SITE + "/forum/authors/radwan-abdulhadi/"},
                "publisher": {
                    "@type": "NewsMediaOrganization",
                    "@id": SITE + "/forum/#publisher",
                    "name": "مِخبار" if locale == "ar" else "Mikhbar",
                    "alternateName": "Mikhbar" if locale == "ar" else "مِخبار",
                    "url": SITE + "/forum/",
                    "logo": {"@type": "ImageObject", "url": SITE + "/assets/images/mikhbar-favicon.png"},
                    "founder": {"@type": "Person", "name": "Radwan Abdulhadi", "url": SITE + "/forum/authors/radwan-abdulhadi/"},
                },
                "articleSection": category,
                "keywords": tags,
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "مِخبار" if locale == "ar" else "Mikhbar", "item": SITE + f"/forum/{locale}/"},
                    {"@type": "ListItem", "position": 2, "name": category, "item": SITE + f"/forum/{locale}/{record['categorySlug']}/"},
                    {"@type": "ListItem", "position": 3, "name": view["title"]},
                ],
            },
        ],
    }


def render_record(record: dict, locale: str = "ar") -> str:
    view = _locale_data(record, locale)
    if not view:
        raise ValueError(f"Record {record.get('id')} has no {locale} locale")
    ui = LOCALE_UI[locale]
    template = Template(TEMPLATE.read_text(encoding="utf-8"))

    summary_html = "".join(f"<li>{_e(item)}</li>" for item in view.get("summaryBullets", []))
    images = record.get("images") or {}
    inline_images = list(images.get("inline") or [])
    sections = list(view.get("sections", []))
    media_slots = _inline_media_slots(len(sections), len(inline_images))

    body = []
    for section_index, section in enumerate(sections):
        body.append(f"<h2>{_e(section.get('heading'))}</h2>")
        for paragraph in section.get("paragraphs", []):
            body.append(f"<p>{_render_paragraph(paragraph)}</p>")
        for image_index in media_slots.get(section_index, []):
            body.append(_render_inline_figure(inline_images[image_index], locale))

    sources_html = []
    for src in record.get("sources", []):
        url = str(src.get("url") or "")
        if not url:
            continue
        name = src.get("name") or urlparse(url).netloc
        label = src.get("title") or src.get("feedTitle") or ""
        sources_html.append(
            f'<li><a href="{_ea(url)}" rel="nofollow noopener noreferrer">{_e(name)}</a><small>{_e(label)}</small></li>'
        )

    tags_html = "".join(f"<span>{_e(tag)}</span>" for tag in view.get("tags", [])[:8])
    canonical = SITE + _url(record, locale)
    ar_url = SITE + _url(record, "ar")
    en_url = SITE + _url(record, "en")
    hero_image = _absolute(images.get("hero") or record.get("image") or "/assets/social/home.jpg")
    card_image = _absolute(images.get("card") or images.get("hero") or record.get("image") or "/assets/social/home.jpg")
    social_image = _absolute(images.get("social") or images.get("hero") or record.get("image") or "/assets/social/home.jpg")
    alt_map = images.get("alt") or {}
    image_alt = alt_map.get(locale) or view.get("title", "")
    credit = str(images.get("credit") or "").strip()
    credit_url = str(images.get("sourceUrl") or "").strip()
    if credit:
        if credit_url:
            image_credit_html = f'<figcaption>{_e("الصورة: " if locale == "ar" else "Image: ")}<a href="{_ea(credit_url)}" rel="nofollow noopener noreferrer">{_e(credit)}</a></figcaption>'
        else:
            image_credit_html = f'<figcaption>{_e("الصورة: " if locale == "ar" else "Image: ")}{_e(credit)}</figcaption>'
    else:
        image_credit_html = ""

    author_url = "/forum/authors/radwan-abdulhadi/"
    return template.substitute(
        LANG=locale,
        DIR=ui["dir"],
        SITE_NAME=_e("مِخبار" if locale == "ar" else "Mikhbar"),
        SITE_NAME_ATTR=_ea("مِخبار" if locale == "ar" else "Mikhbar"),
        NAV_MARK=_e("م" if locale == "ar" else "M"),
        NAV_HOME_TEXT=_e(ui["navHome"]),
        NAV_LATEST_TEXT=_e(ui["navLatest"]),
        NAV_ABOUT_TEXT=_e(ui["navAbout"]),
        NAV_LANG_TEXT=_e(ui["navLang"]),
        NAV_HOME_URL=_ea(f"/forum/{locale}/"),
        NAV_LATEST_URL=_ea(f"/forum/{locale}/#latest"),
        NAV_ABOUT_URL=_ea("/forum/about/"),
        NAV_LANG_URL=_ea("/forum/en/" if locale == "ar" else "/forum/ar/"),
        OG_LOCALE=ui["og"],
        TITLE=_e(view["title"]),
        TITLE_ATTR=_ea(view["title"]),
        DESCRIPTION_ATTR=_ea(view["description"]),
        CANONICAL=_ea(canonical),
        HREFLANG_AR=_ea(ar_url),
        HREFLANG_EN=_ea(en_url),
        HREFLANG_DEFAULT=_ea(SITE + "/forum/"),
        HERO_IMAGE=_ea(hero_image),
        CARD_IMAGE=_ea(card_image),
        SOCIAL_IMAGE=_ea(social_image),
        IMAGE_ALT=_ea(image_alt),
        IMAGE_CREDIT_HTML=image_credit_html,
        DATE_PUBLISHED=_ea(record["datePublished"]),
        DATE_MODIFIED=_ea(record.get("dateModified", record["datePublished"])),
        SCHEMA_JSON=json.dumps(_schema(record, locale, view), ensure_ascii=False, separators=(",", ":")),
        CATEGORY_LABEL=_e(view.get("category") or record.get("category") or record["categorySlug"]),
        DECK=_e(view.get("deck", "")),
        DATE_LABEL=_e(view.get("dateLabel") or record.get("dateLabel", "")),
        MODIFIED_LABEL=_e(view.get("modifiedLabel") or view.get("dateLabel") or record.get("modifiedLabel", "")),
        READ_MINUTES=_e(view.get("readMinutes") or record.get("readMinutes", 3)),
        SUMMARY_HTML=summary_html,
        BODY_HTML="".join(body),
        SOURCES_HTML="".join(sources_html),
        TAGS_HTML=tags_html,
        SKIP_TEXT=_e(ui["skip"]), BRAND_ARIA=_ea(ui["brandAria"]), MENU_ARIA=_ea(ui["menuAria"]), NAV_ARIA=_ea(ui["navAria"]),
        HOME_TEXT=_e(ui["home"]), ABOUT_TEXT=_e(ui["about"]), PROJECTS_TEXT=_e(ui["projects"]), FORUM_TEXT=_e(ui["forum"]),
        BREADCRUMB_ARIA=_ea(ui["breadcrumbAria"]), PUBLISHED_TEXT=_e(ui["published"]), UPDATED_TEXT=_e(ui["updated"]), READ_TEXT=_e(ui["read"]),
        SUMMARY_TEXT=_e(ui["summary"]), SOURCES_TEXT=_e(ui["sources"]), SOURCE_NOTE=_e(ui["sourceNote"]),
        AUTHOR_NAME=_e(ui["authorName"]), AUTHOR_ROLE=_e(ui["authorRole"]), AUTHOR_URL=_ea(author_url),
        FOOTER_DESC=_e(ui["footerDesc"]), ABOUT_PLATFORM=_e(ui["aboutPlatform"]), ABOUT_RDWAN=_e(ui["aboutRdwan"]), EDITORIAL_TEXT=_e(ui["editorial"]),
        TRUST_TEXT=_e(ui["trust"]), CORRECTIONS_TEXT=_e(ui["corrections"]), AI_POLICY_TEXT=_e(ui["aiPolicy"]),
        ABOUT_URL=_ea("/forum/about/"), EDITORIAL_URL=_ea("/forum/editorial-policy/"), CORRECTIONS_URL=_ea("/forum/corrections/"), AI_POLICY_URL=_ea("/forum/ai-policy/"),
    )


def output_path(record: dict, locale: str = "ar") -> Path:
    return FORUM / locale / record["categorySlug"] / record["slug"] / "index.html"


def legacy_output_path(record: dict) -> Path:
    return FORUM / record["categorySlug"] / record["slug"] / "index.html"


def _legacy_redirect(record: dict) -> str:
    target = _url(record, "ar")
    canonical = SITE + target
    return f'''<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><meta name="robots" content="noindex,follow"><link rel="canonical" href="{_ea(canonical)}"><meta http-equiv="refresh" content="0;url={_ea(target)}"><script>location.replace({json.dumps(target)});</script></head><body><a href="{_ea(target)}">انتقل إلى الخبر</a></body></html>'''


def render_to_files(record: dict) -> dict[str, Path]:
    outputs: dict[str, Path] = {}
    for locale in ("ar", "en"):
        if not _locale_data(record, locale):
            continue
        path = output_path(record, locale)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_record(record, locale), encoding="utf-8")
        outputs[locale] = path
    legacy = legacy_output_path(record)
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text(_legacy_redirect(record), encoding="utf-8")
    outputs["legacy"] = legacy
    return outputs


def render_to_file(record: dict) -> Path:
    outputs = render_to_files(record)
    return outputs.get("ar") or outputs["legacy"]


def render_content_file(path: Path) -> dict[str, Path]:
    return render_to_files(load_json(path, {}))
