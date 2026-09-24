from __future__ import annotations

import re
from pathlib import Path

from topic_hub_config import HUB_CONFIG, OLD_SUMMARIES

ROOT = Path(__file__).resolve().parents[2]
FORUM = ROOT / "forum"


def replace_meta(html: str, *, title: str, description: str) -> str:
    html = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", html, count=1, flags=re.S)
    html = re.sub(
        r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="{description}">',
        html,
        count=1,
    )
    for prop in ("og:title", "twitter:title"):
        attr = "property" if prop.startswith("og:") else "name"
        html = re.sub(
            rf'<meta {attr}="{re.escape(prop)}" content="[^"]*">',
            f'<meta {attr}="{prop}" content="{title}">',
            html,
            count=1,
        )
    for prop in ("og:description", "twitter:description"):
        attr = "property" if prop.startswith("og:") else "name"
        html = re.sub(
            rf'<meta {attr}="{re.escape(prop)}" content="[^"]*">',
            f'<meta {attr}="{prop}" content="{description}">',
            html,
            count=1,
        )
    return html


def topic_intro(locale: str, slug: str, config: dict) -> str:
    links = config["links"]
    if locale == "ar":
        related = "مواضيع مرتبطة: " + "، ".join(
            f'<a href="../{target}/">{label}</a>' for target, label in links
        ) + "."
        pillar = ""
        if config.get("pillar"):
            pillar_slug, pillar_label = config["pillar"]
            pillar = f'<p class="rt-topic-pillar">للتعمق: <a href="../guides/{pillar_slug}/">{pillar_label}</a>.</p>'
    else:
        related = "Explore related coverage: " + ", ".join(
            f'<a href="../{target}/">{label}</a>' for target, label in links
        ) + "."
        pillar = ""
        if config.get("pillar"):
            pillar_slug, pillar_label = config["pillar"]
            pillar = f'<p class="rt-topic-pillar">Go deeper: <a href="../guides/{pillar_slug}/">{pillar_label}</a>.</p>'
    return (
        f'<section class="rt-section rt-topic-intro" data-topic-hub="{slug}" aria-labelledby="{slug}-topic-guide">'
        f'<div class="rt-prose"><h2 id="{slug}-topic-guide">{config["heading"]}</h2>'
        f'<p>{config["body"]}</p><p>{related}</p>{pillar}</div></section>'
    )


def enhance(locale: str, slug: str, config: dict) -> bool:
    path = FORUM / locale / slug / "index.html"
    if not path.exists():
        return False

    original = path.read_text(encoding="utf-8")
    html = replace_meta(original, title=config["title"], description=config["description"])

    html = re.sub(
        r'("@type":"CollectionPage"[^{}]*?"name":)"[^"]*"',
        lambda m: m.group(1) + '"' + config["title"].replace('"', '\\"') + '"',
        html,
        count=1,
    )

    old_summary = OLD_SUMMARIES.get(slug, {}).get(locale)
    if old_summary:
        html = html.replace(old_summary, config["summary"])

    html = re.sub(
        r'(<div class="rt-category-title">.*?<p>).*?(</p></div>)',
        lambda m: m.group(1) + config["summary"] + m.group(2),
        html,
        count=1,
        flags=re.S,
    )

    intro = topic_intro(locale, slug, config)
    existing_intro = re.compile(
        r'<section class="rt-section rt-topic-intro"[^>]*>.*?</section>',
        flags=re.S,
    )
    if existing_intro.search(html):
        html = existing_intro.sub(intro, html, count=1)
    else:
        marker = '<div class="rt-toolbar">'
        if marker in html:
            html = html.replace(marker, intro + marker, 1)

    if html == original:
        return False
    path.write_text(html, encoding="utf-8")
    return True


def main() -> int:
    changed: list[str] = []
    for slug, locales in HUB_CONFIG.items():
        for locale, config in locales.items():
            if enhance(locale, slug, config):
                changed.append(f"{locale}/{slug}")
    print("Mikhbar category SEO enhanced: " + (", ".join(changed) if changed else "no changes"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
