from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORUM = ROOT / "forum"

AI_CONFIG = {
    "ar": {
        "path": FORUM / "ar" / "ai" / "index.html",
        "title": "أخبار الذكاء الاصطناعي وأدوات AI وتطبيقاته | مِخبار",
        "description": "تابع أخبار الذكاء الاصطناعي وأحدث برامج وأدوات AI وتطبيقاته، من ChatGPT وGemini وجوجل وOpenAI إلى نماذج الصور والوكلاء الذكيين، مع مصادر واضحة.",
        "intro": (
            '<section class="rt-section rt-topic-intro" aria-labelledby="ai-topic-guide">'
            '<div class="rt-prose"><h2 id="ai-topic-guide">أخبار وأدوات الذكاء الاصطناعي في مكان واحد</h2>'
            '<p>يجمع هذا القسم أخبار الذكاء الاصطناعي وتحديثات برامجه وأدواته وتطبيقاته، بما يشمل ChatGPT وGemini وGoogle AI وOpenAI وClaude ونماذج الصور والوكلاء الذكيين والنماذج مفتوحة الأوزان. نربط الأخبار بمصادرها ونحدّث التفاصيل عندما تتغير.</p>'
            '<p>للمواضيع المتقاطعة تابع أيضًا <a href="../apps/">التطبيقات والبرامج</a>، <a href="../automation/">الأتمتة</a>، <a href="../robotics/">الروبوتات</a> و<a href="../security/">الأمن التقني</a>.</p>'
            '</div></section>'
        ),
    },
    "en": {
        "path": FORUM / "en" / "ai" / "index.html",
        "title": "Artificial Intelligence News Updates & AI Tools | Mikhbar",
        "description": "Follow artificial intelligence news updates on OpenAI, Google, Microsoft, open-source models, AI tools, agents and generative AI with source-linked reporting.",
        "intro": (
            '<section class="rt-section rt-topic-intro" aria-labelledby="ai-topic-guide">'
            '<div class="rt-prose"><h2 id="ai-topic-guide">Artificial intelligence news, tools and model updates</h2>'
            '<p>This hub tracks artificial intelligence news updates across OpenAI, Google AI, Microsoft, Anthropic, open-source models, generative AI tools, coding agents and multimodal systems. Stories link back to their sources and are updated when material details change.</p>'
            '<p>For related coverage, browse <a href="../apps/">apps and software</a>, <a href="../automation/">automation</a>, <a href="../robotics/">robotics</a> and <a href="../security/">security</a>.</p>'
            '</div></section>'
        ),
    },
}


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


def enhance(path: Path, *, title: str, description: str, intro: str) -> bool:
    if not path.exists():
        return False
    original = path.read_text(encoding="utf-8")
    html = replace_meta(original, title=title, description=description)

    # Keep CollectionPage naming aligned with the title presented to search engines.
    html = re.sub(
        r'("@type":"CollectionPage"[^{}]*?"name":)"[^"]*"',
        lambda m: m.group(1) + '"' + title.replace('"', '\\"') + '"',
        html,
        count=1,
    )

    # Replace the short AI category summary wherever the generator repeats it.
    if path.parts[-3] == "ar":
        old = "أخبار النماذج والشركات والأدوات والمساعدات الذكية وتطبيقات الذكاء الاصطناعي."
        visible = "أخبار الذكاء الاصطناعي وأدواته وبرامجه وتطبيقاته، مع متابعة النماذج والشركات والوكلاء الذكيين."
    else:
        old = "News on models, companies, AI tools, assistants and artificial intelligence applications."
        visible = "Artificial intelligence news updates, AI tools, models, agents and applications with source-linked coverage."
    html = html.replace(old, visible)

    marker = '<div class="rt-toolbar">'
    if "rt-topic-intro" not in html and marker in html:
        html = html.replace(marker, intro + marker, 1)

    if html == original:
        return False
    path.write_text(html, encoding="utf-8")
    return True


def main() -> int:
    changed = []
    for locale, config in AI_CONFIG.items():
        if enhance(**config):
            changed.append(locale)
    print("Mikhbar category SEO enhanced: " + (", ".join(changed) if changed else "no changes"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
