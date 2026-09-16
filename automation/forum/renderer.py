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


def _e(value) -> str:
    return escape(str(value or ""))


def _ea(value) -> str:
    return escape(str(value or ""), quote=True)


def _schema(record: dict) -> dict:
    canonical = SITE + record["url"]
    tags = record.get("tags", [])
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "NewsArticle",
                "@id": canonical + "#article",
                "headline": record["title"],
                "description": record["description"],
                "datePublished": record["datePublished"],
                "dateModified": record.get("dateModified", record["datePublished"]),
                "inLanguage": "ar",
                "mainEntityOfPage": canonical,
                "image": [record.get("image", SITE + "/assets/social/home.jpg")],
                "author": {
                    "@type": "Person",
                    "name": "رضوان عبدالهادي",
                    "url": SITE + "/forum/authors/radwan-abdulhadi/",
                },
                "publisher": {
                    "@type": "Person",
                    "name": "رضوان عبدالهادي",
                    "url": SITE + "/",
                },
                "articleSection": record["category"],
                "keywords": tags,
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "RDWAN Tech", "item": SITE + "/forum/"},
                    {"@type": "ListItem", "position": 2, "name": record["category"], "item": SITE + f"/forum/{record['categorySlug']}/"},
                    {"@type": "ListItem", "position": 3, "name": record["title"]},
                ],
            },
        ],
    }


def render_record(record: dict) -> str:
    template = Template(TEMPLATE.read_text(encoding="utf-8"))
    summary_html = "".join(f"<li>{_e(item)}</li>" for item in record.get("summaryBullets", []))

    body = []
    for section in record.get("sections", []):
        body.append(f"<h2>{_e(section.get('heading'))}</h2>")
        for paragraph in section.get("paragraphs", []):
            body.append(f"<p>{_e(paragraph)}</p>")

    sources_html = []
    for src in record.get("sources", []):
        url = str(src.get("url") or "")
        if not url:
            continue
        name = src.get("name") or urlparse(url).netloc
        label = src.get("title") or src.get("feedTitle") or ""
        sources_html.append(
            f'<li><a href="{_ea(url)}" rel="nofollow noopener noreferrer">{_e(name)}</a>'
            f'<small>{_e(label)}</small></li>'
        )

    tags_html = "".join(f"<span>{_e(tag)}</span>" for tag in record.get("tags", [])[:8])
    canonical = SITE + record["url"]
    image = record.get("image", SITE + "/assets/social/home.jpg")

    return template.substitute(
        TITLE=_e(record["title"]),
        TITLE_ATTR=_ea(record["title"]),
        DESCRIPTION_ATTR=_ea(record["description"]),
        CANONICAL=_ea(canonical),
        IMAGE=_ea(image),
        DATE_PUBLISHED=_ea(record["datePublished"]),
        DATE_MODIFIED=_ea(record.get("dateModified", record["datePublished"])),
        SCHEMA_JSON=json.dumps(_schema(record), ensure_ascii=False, separators=(",", ":")),
        CATEGORY_LABEL=_e(record["category"]),
        DECK=_e(record.get("deck", "")),
        DATE_LABEL=_e(record.get("dateLabel", "")),
        MODIFIED_LABEL=_e(record.get("modifiedLabel", record.get("dateLabel", ""))),
        READ_MINUTES=_e(record.get("readMinutes", 3)),
        SUMMARY_HTML=summary_html,
        BODY_HTML="".join(body),
        SOURCES_HTML="".join(sources_html),
        TAGS_HTML=tags_html,
    )


def output_path(record: dict) -> Path:
    return FORUM / record["categorySlug"] / record["slug"] / "index.html"


def render_to_file(record: dict) -> Path:
    path = output_path(record)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_record(record), encoding="utf-8")
    return path


def render_content_file(path: Path) -> Path:
    return render_to_file(load_json(path, {}))
