from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORUM = ROOT / "forum"

HUB_CONFIG = {
    "ai": {
        "ar": {
            "title": "أخبار الذكاء الاصطناعي وأدوات AI وتطبيقاته | مِخبار",
            "description": "تابع أخبار الذكاء الاصطناعي وأحدث برامج وأدوات AI وتطبيقاته، من ChatGPT وGemini وOpenAI إلى النماذج التوليدية والوكلاء الذكيين.",
            "summary": "أخبار الذكاء الاصطناعي وأدواته وبرامجه وتطبيقاته، مع متابعة النماذج والشركات والوكلاء الذكيين.",
            "heading": "أخبار وأدوات الذكاء الاصطناعي في مكان واحد",
            "body": "يجمع هذا القسم أخبار الذكاء الاصطناعي وتحديثات النماذج والأدوات والتطبيقات، بما يشمل OpenAI وChatGPT وGemini وClaude والنماذج مفتوحة الأوزان والوكلاء الذكيين والذكاء الاصطناعي التوليدي. نربط الأخبار بمصادرها ونحدّث التفاصيل عندما تتغير.",
            "links": (("apps", "التطبيقات والبرامج"), ("automation", "الأتمتة"), ("robotics", "الروبوتات"), ("security", "الأمن السيبراني")),
        },
        "en": {
            "title": "Artificial Intelligence News Updates & AI Tools | Mikhbar",
            "description": "Follow artificial intelligence news updates on OpenAI, Google, Microsoft, open-source models, AI tools, agents and generative AI with source-linked reporting.",
            "summary": "Artificial intelligence news updates, AI tools, models, agents and applications with source-linked coverage.",
            "heading": "Artificial intelligence news, tools and model updates",
            "body": "This hub tracks artificial intelligence news across OpenAI, Google AI, Microsoft, Anthropic, open-source models, generative AI tools, coding agents and multimodal systems. Stories link back to their sources and are updated when material details change.",
            "links": (("apps", "apps and software"), ("automation", "automation"), ("robotics", "robotics"), ("security", "cybersecurity")),
        },
    },
    "security": {
        "ar": {
            "title": "أخبار الأمن السيبراني والثغرات والحماية الرقمية | مِخبار",
            "description": "تابع أخبار الأمن السيبراني والثغرات والهجمات والبرمجيات الخبيثة والخصوصية وتحديثات الحماية الرقمية مع تغطية موثقة ومصادر واضحة.",
            "summary": "أخبار الأمن السيبراني والثغرات والخصوصية والهجمات وتحديثات الحماية الرقمية المهمة للمستخدمين والمؤسسات.",
            "heading": "الأمن السيبراني: ثغرات وهجمات وحماية رقمية",
            "body": "يركز هذا القسم على الثغرات الأمنية والهجمات النشطة والبرمجيات الخبيثة وتسريبات البيانات والخصوصية وتحديثات الحماية من Microsoft وGoogle وCISA وشركات الأمن. نوضح أثر الخبر ومن يتأثر وما إذا كان هناك تحديث أو تصحيح متاح.",
            "links": (("web", "أمن الويب"), ("apps", "التطبيقات والبرامج"), ("computers", "الحواسيب"), ("ai", "الذكاء الاصطناعي")),
        },
        "en": {
            "title": "Cybersecurity News, Vulnerabilities & Digital Security | Mikhbar",
            "description": "Follow cybersecurity news, active vulnerabilities, malware, privacy incidents, data breaches and digital security updates with source-linked reporting.",
            "summary": "Cybersecurity news covering vulnerabilities, malware, privacy, breaches and security updates that matter to users and organizations.",
            "heading": "Cybersecurity news, vulnerabilities and digital protection",
            "body": "This hub covers actively exploited vulnerabilities, malware, data breaches, privacy incidents and security updates from vendors and agencies including Microsoft, Google and CISA. Coverage explains who is affected, what changed and whether a patch or mitigation is available.",
            "links": (("web", "web security"), ("apps", "apps and software"), ("computers", "computing"), ("ai", "artificial intelligence")),
        },
    },
    "automation": {
        "ar": {
            "title": "أخبار الأتمتة والوكلاء وسير العمل الذكي | مِخبار",
            "description": "أخبار الأتمتة وأدوات سير العمل والوكلاء الذكيين والسكربتات وRPA وGitHub Actions والأدوات التي تقلل العمل اليدوي وتربط الخدمات.",
            "summary": "أخبار أتمتة الأعمال وسير العمل والوكلاء والسكربتات والأدوات التي تربط الخدمات وتقلل العمل اليدوي.",
            "heading": "الأتمتة وسير العمل والوكلاء الذكيون",
            "body": "يجمع هذا القسم أخبار أتمتة الأعمال وسير العمل والوكلاء الذكيين والسكربتات وRPA وأدوات المطورين والتكامل بين الخدمات. نتابع الأدوات التي تحول المهام المتكررة إلى عمليات قابلة للتشغيل والمراقبة والتوسع.",
            "links": (("ai", "الذكاء الاصطناعي"), ("apps", "التطبيقات والبرامج"), ("web", "الويب"), ("robotics", "الروبوتات")),
        },
        "en": {
            "title": "Automation News, AI Agents & Workflow Tools | Mikhbar",
            "description": "Follow automation news, workflow tools, AI agents, scripts, RPA, GitHub Actions and integrations that connect services and reduce repetitive work.",
            "summary": "Automation news covering workflows, AI agents, scripts, integrations and tools that reduce repetitive digital work.",
            "heading": "Automation, workflow tools and AI agents",
            "body": "This hub follows workflow automation, AI agents, scripts, RPA, developer automation and service integrations. Coverage focuses on tools and systems that turn repetitive tasks into reliable processes that can be monitored, reused and scaled.",
            "links": (("ai", "artificial intelligence"), ("apps", "apps and software"), ("web", "web technology"), ("robotics", "robotics")),
        },
    },
    "robotics": {
        "ar": {
            "title": "أخبار الروبوتات والروبوتات البشرية والأنظمة الذكية | مِخبار",
            "description": "تابع أخبار الروبوتات البشرية والصناعية والروبوتات المتنقلة والحساسات والتحكم وPhysical AI والأتمتة في المصانع والأنظمة الذكية.",
            "summary": "أخبار الروبوتات البشرية والصناعية والأنظمة الذاتية والحساسات والتحكم والذكاء الاصطناعي المادي.",
            "heading": "الروبوتات البشرية والصناعية والذكاء الاصطناعي المادي",
            "body": "يغطي هذا القسم الروبوتات البشرية والصناعية والروبوتات المتنقلة والأنظمة الذاتية والحساسات والتحكم وPhysical AI والتصنيع الذكي. نتابع الشركات والمنصات والتجارب التي تنقل الذكاء الاصطناعي من البرمجيات إلى العالم المادي.",
            "links": (("ai", "الذكاء الاصطناعي"), ("automation", "الأتمتة"), ("computers", "الحواسيب"), ("security", "الأمن السيبراني")),
        },
        "en": {
            "title": "Robotics News, Humanoids & Intelligent Systems | Mikhbar",
            "description": "Follow robotics news on humanoids, industrial robots, autonomous systems, sensors, control, physical AI and intelligent manufacturing.",
            "summary": "Robotics news covering humanoids, industrial robots, autonomous systems, sensors, control and physical AI.",
            "heading": "Robotics, humanoids and physical AI",
            "body": "This hub tracks humanoid and industrial robots, autonomous machines, sensors, control systems, physical AI and intelligent manufacturing. Coverage follows the companies, platforms and experiments moving artificial intelligence into the physical world.",
            "links": (("ai", "artificial intelligence"), ("automation", "automation"), ("computers", "computing"), ("security", "cybersecurity")),
        },
    },
    "apps": {
        "ar": {
            "title": "أخبار التطبيقات والبرامج وأدوات الإنتاجية | مِخبار",
            "description": "تابع أخبار التطبيقات والبرامج وتحديثات الأدوات والخدمات الرقمية وبرامج سطح المكتب والهاتف وأدوات الإنتاجية الجديدة.",
            "summary": "أخبار التطبيقات والبرامج والخدمات الرقمية وتحديثات الأدوات وبرامج الإنتاجية على الهاتف وسطح المكتب.",
            "heading": "التطبيقات والبرامج والخدمات الرقمية",
            "body": "يركز هذا القسم على التطبيقات والبرامج والخدمات الرقمية وأدوات الإنتاجية، من تحديثات سطح المكتب والهاتف إلى المنصات والخدمات التي تغير طريقة العمل والاستخدام اليومي. نوضح المزايا الجديدة والتغييرات المهمة وتأثيرها العملي.",
            "links": (("mobile", "الهواتف"), ("ai", "الذكاء الاصطناعي"), ("web", "الويب"), ("security", "الأمن السيبراني")),
        },
        "en": {
            "title": "Apps & Software News, Updates & Productivity Tools | Mikhbar",
            "description": "Follow apps and software news, product updates, digital services, desktop and mobile software, productivity tools and important platform changes.",
            "summary": "Apps and software news covering product updates, digital services, desktop and mobile tools and productivity software.",
            "heading": "Apps, software and productivity tools",
            "body": "This hub covers apps, software, digital services and productivity tools, from desktop and mobile releases to platforms that change how people work and use technology. Coverage highlights meaningful features, updates and practical impact.",
            "links": (("mobile", "mobile"), ("ai", "artificial intelligence"), ("web", "web technology"), ("security", "cybersecurity")),
        },
    },
    "web": {
        "ar": {
            "title": "أخبار الويب والمتصفحات ومحركات البحث وتطوير الويب | مِخبار",
            "description": "أخبار الويب والمتصفحات ومحركات البحث والخدمات السحابية وتقنيات تطوير الويب وواجهات API وServerless والمنصات التي تشغل الإنترنت.",
            "summary": "أخبار الويب والمتصفحات ومحركات البحث والخدمات والمنصات وتقنيات تطوير الويب الحديثة.",
            "heading": "الويب والمتصفحات ومحركات البحث وتقنيات التطوير",
            "body": "يجمع هذا القسم أخبار الويب والمتصفحات ومحركات البحث والخدمات السحابية وواجهات API وServerless وأدوات تطوير المواقع والمنصات. نتابع التغييرات التي تؤثر في المطورين والمواقع وطريقة الوصول إلى المعلومات والخدمات على الإنترنت.",
            "links": (("security", "الأمن السيبراني"), ("apps", "التطبيقات والبرامج"), ("automation", "الأتمتة"), ("ai", "الذكاء الاصطناعي")),
        },
        "en": {
            "title": "Web Technology News, Browsers, Search & Development | Mikhbar",
            "description": "Follow web technology news across browsers, search engines, cloud services, APIs, serverless platforms and modern web development tools.",
            "summary": "Web technology news covering browsers, search engines, online services, APIs, cloud platforms and modern web development.",
            "heading": "Web technology, browsers, search and development",
            "body": "This hub follows browsers, search engines, cloud services, APIs, serverless platforms and modern web development tools. Coverage focuses on changes that affect developers, websites and how people discover and use services on the internet.",
            "links": (("security", "cybersecurity"), ("apps", "apps and software"), ("automation", "automation"), ("ai", "artificial intelligence")),
        },
    },
}

OLD_SUMMARIES = {
    "ai": {
        "ar": "أخبار النماذج والشركات والأدوات والمساعدات الذكية وتطبيقات الذكاء الاصطناعي.",
        "en": "News on AI models, companies, tools, assistants and real-world artificial intelligence applications.",
    },
    "security": {
        "ar": "التحديثات الأمنية والخصوصية والحماية الرقمية والثغرات المهمة للمستخدمين.",
        "en": "Security updates, privacy, digital protection and vulnerabilities that matter to users.",
    },
    "automation": {
        "ar": "أتمتة الأعمال وسير العمل والسكربتات والوكلاء والأدوات الذكية.",
        "en": "Workflow automation, scripts, agents and tools that automate digital work.",
    },
    "robotics": {
        "ar": "الروبوتات البشرية والصناعية والحساسات والتحكم والمصانع الذكية.",
        "en": "Humanoid and industrial robots, sensors, control systems and intelligent manufacturing.",
    },
    "apps": {
        "ar": "برامج سطح المكتب وتطبيقات الهاتف والخدمات الرقمية والأدوات الجديدة.",
        "en": "Desktop software, mobile apps, digital services and new productivity tools.",
    },
    "web": {
        "ar": "المواقع والمتصفحات ومحركات البحث والخدمات وتقنيات تطوير الويب.",
        "en": "Websites, browsers, search engines, online services and modern web technologies.",
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


def topic_intro(locale: str, slug: str, config: dict) -> str:
    links = config["links"]
    if locale == "ar":
        related = "مواضيع مرتبطة: " + "، ".join(
            f'<a href="../{target}/">{label}</a>' for target, label in links
        ) + "."
    else:
        related = "Explore related coverage: " + ", ".join(
            f'<a href="../{target}/">{label}</a>' for target, label in links
        ) + "."
    return (
        f'<section class="rt-section rt-topic-intro" data-topic-hub="{slug}" aria-labelledby="{slug}-topic-guide">'
        f'<div class="rt-prose"><h2 id="{slug}-topic-guide">{config["heading"]}</h2>'
        f'<p>{config["body"]}</p><p>{related}</p></div></section>'
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
