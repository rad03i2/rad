from __future__ import annotations

import json
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORUM = ROOT / "forum"
ORIGIN = "https://mikhbar.website"
LOGO = ORIGIN + "/assets/brand/mikhbar/06-web-ready/icon/mikhbar-app-icon-512.png"

PAGES = {
    "about": {
        "ar_path": "/about/",
        "en_path": "/en/about/",
        "type": "AboutPage",
        "title": "About Mikhbar — Independent Technology Publication",
        "description": "Learn about Mikhbar, an independent bilingual technology publication covering AI, cybersecurity, robotics, automation, software and the web.",
        "label": "ABOUT MIKHBAR",
        "h1": "About Mikhbar",
        "sections": [
            ("What Mikhbar covers", "Mikhbar is an independent technology publication in Arabic and English. Coverage includes artificial intelligence, cybersecurity, robotics, automation, mobile technology, computing, apps, software, the web and social platforms."),
            ("How stories are selected", "Coverage prioritizes timely technology developments with clear reader value. Primary sources such as official newsrooms, product pages, documentation, research papers and original repositories are preferred when they are available."),
            ("How articles are presented", "Each story is published with a stable URL, title, description, publication and update dates, category, author attribution, imagery, sources and structured data. Related stories and topic pages help readers continue exploring the subject."),
            ("Automation and AI", "Automation helps organize sources, build pages and update discovery files. AI tools may assist with analysis and drafting, but they are not treated as sources of truth. The final publication remains subject to Mikhbar's sourcing, accuracy and correction standards."),
            ("Editorial transparency", 'Read the <a href="/en/editorial-policy/">editorial policy</a>, <a href="/en/corrections/">corrections policy</a> and <a href="/en/ai-policy/">AI and automation policy</a>. For editorial feedback or correction requests, use the <a href="/en/contact/">contact page</a>.'),
        ],
    },
    "contact": {
        "ar_path": "/contact/",
        "en_path": "/en/contact/",
        "type": "ContactPage",
        "title": "Contact Mikhbar — Editorial Feedback & Corrections",
        "description": "Official Mikhbar contact information for editorial feedback, correction requests, coverage suggestions and questions about published content.",
        "label": "CONTACT MIKHBAR",
        "h1": "Contact Mikhbar",
        "sections": [
            ("Editorial feedback", 'Use the <a href="https://github.com/rad03i2/rad/issues/new" rel="noopener noreferrer">public Mikhbar issue form on GitHub</a> for editorial feedback, questions or coverage suggestions. Include the relevant Mikhbar URL whenever possible.'),
            ("Correction requests", 'For a correction, first review the <a href="/en/corrections/">corrections policy</a>, then provide the article URL, the information you believe needs review and a supporting source when available.'),
            ("Sources and editorial standards", 'The <a href="/en/editorial-policy/">editorial policy</a> explains how Mikhbar handles sources, headlines, updates and the distinction between reporting and analysis.'),
            ("AI and automation", 'The <a href="/en/ai-policy/">AI and automation policy</a> explains how automated tools may assist the publishing workflow while source verification remains required.'),
            ("Privacy reminder", "GitHub issues are public. Do not post passwords, access tokens, private records or other sensitive information in a public issue."),
        ],
    },
    "editorial-policy": {
        "ar_path": "/editorial-policy/",
        "en_path": "/en/editorial-policy/",
        "type": "WebPage",
        "title": "Editorial Policy & Sources — Mikhbar",
        "description": "Mikhbar's editorial policy covering accuracy, sourcing, headlines, updates, analysis, corrections and the use of AI and automation.",
        "label": "EDITORIAL POLICY",
        "h1": "Editorial Policy",
        "sections": [
            ("Accuracy before speed", "Speed matters in technology news, but an unsupported claim should not be presented as fact. When information is uncertain or disputed, the article should describe that uncertainty instead of overstating what is known."),
            ("Sources", "Primary sources are preferred when available, including official websites, product pages, documentation, company statements, original repositories, research papers and direct statements. Reliable reporting can be used for context and comparison."),
            ("News versus analysis", "Reporting should distinguish documented events and statements from interpretation or analysis. Opinion or analysis should be identifiable to readers rather than blended into factual claims."),
            ("Headlines and updates", 'Headlines should accurately describe the page without unsupported promises. Material updates may change the modified date, while substantive errors are handled under the <a href="/en/corrections/">corrections policy</a>.'),
            ("Automation and accountability", 'Automation and AI may assist discovery, organization and drafting, but source verification remains required. Details are described in the <a href="/en/ai-policy/">AI and automation policy</a>.'),
        ],
    },
    "corrections": {
        "ar_path": "/corrections/",
        "en_path": "/en/corrections/",
        "type": "WebPage",
        "title": "Corrections & Updates Policy — Mikhbar",
        "description": "Mikhbar's corrections policy explains how material errors, developing stories and post-publication updates are handled transparently.",
        "label": "CORRECTIONS",
        "h1": "Corrections & Updates Policy",
        "sections": [
            ("Minor errors", "Typographical, formatting or broken-link issues that do not change the meaning may be corrected directly without being treated as a substantive correction."),
            ("Material errors", "Errors involving names, numbers, dates, specifications, central claims or results that materially affect the story should be corrected and the modification date updated. A correction note may be added when readers need to know that a prior version contained a significant error."),
            ("Developing stories", "Some technology stories change quickly, including outages, launches, investigations, policy changes and product updates. The existing article may be updated when it remains the same story, while a separate follow-up may be appropriate for a materially new development."),
            ("Evidence for corrections", "Corrections should be supported by an appropriate source, with primary evidence preferred when it is available. An unverified comment alone is not sufficient to reverse a well-supported factual statement."),
            ("Requesting a correction", 'Use the <a href="/en/contact/">Mikhbar contact page</a> and include the article URL, the disputed information and a supporting source when available. Requests are reviewed under the same <a href="/en/editorial-policy/">editorial standards</a> applied to published coverage.'),
        ],
    },
    "ai-policy": {
        "ar_path": "/ai-policy/",
        "en_path": "/en/ai-policy/",
        "type": "WebPage",
        "title": "AI & Automation Policy — Mikhbar",
        "description": "Mikhbar's policy for using AI and automation in news discovery, source organization, drafting, page generation and publishing while preserving accuracy and transparency.",
        "label": "AI & AUTOMATION",
        "h1": "AI & Automation Policy",
        "sections": [
            ("News discovery", "Automated systems may monitor technology sources, remove duplicates, classify topics and rank candidate stories. Automated selection does not make a claim true; publishable facts still require verifiable sources."),
            ("Sources come first", "When an official statement, product page, documentation, original repository, research paper or direct source is available, that material takes precedence over model output. AI is not a substitute for a primary source."),
            ("Drafting assistance", "Tools may assist with summarization, structure, headline ideas, metadata and Arabic or English drafting. The final article should not invent details, numbers or claims that are absent from the supporting sources."),
            ("Claims and marketing language", "Company statements about performance, superiority or future expectations should be attributed when independent evidence is insufficient. Marketing language should not be converted into neutral fact merely because it appears in an official release."),
            ("Added value and accountability", 'The goal is not maximum page volume. Published pages should add organization, explanation, context or comparison. Errors in AI-assisted content are subject to the same <a href="/en/corrections/">corrections policy</a> and <a href="/en/editorial-policy/">editorial policy</a> as other coverage.'),
        ],
    },
    "authors/radwan-abdulhadi": {
        "ar_path": "/authors/radwan-abdulhadi/",
        "en_path": "/en/authors/radwan-abdulhadi/",
        "type": "ProfilePage",
        "title": "Radwan Abdulhadi — Editor & Technology Writer at Mikhbar",
        "description": "Author profile for Radwan Abdulhadi at Mikhbar, including editorial role, technology coverage areas and publishing approach.",
        "label": "AUTHOR",
        "h1": "Radwan Abdulhadi",
        "sections": [
            ("Role at Mikhbar", "Radwan Abdulhadi is an editor and technology writer at Mikhbar. His work includes technology coverage as well as contributions to the platform's publishing systems and content presentation."),
            ("Coverage areas", "Coverage interests include artificial intelligence, robotics, automation, Windows, Python, C#, JavaScript, mobile apps, web technology, digital tools and software."),
            ("Publishing approach", 'Reporting uses sources that readers can inspect, with primary sources preferred when available. The <a href="/en/editorial-policy/">editorial policy</a> explains sourcing and accuracy standards, while the <a href="/en/ai-policy/">AI policy</a> describes the role of automated tools.'),
            ("Corrections and transparency", 'Material changes or errors are handled under Mikhbar\'s <a href="/en/corrections/">corrections policy</a>. News pages display publication and modification dates along with their cited sources.'),
        ],
    },
}


def publisher_schema() -> dict:
    return {
        "@type": "NewsMediaOrganization",
        "@id": ORIGIN + "/#publisher",
        "name": "Mikhbar",
        "alternateName": ["مِخبار", "مخبار", "MIKHBAR"],
        "url": ORIGIN + "/",
        "logo": {"@type": "ImageObject", "url": LOGO},
        "publishingPrinciples": ORIGIN + "/editorial-policy/",
        "correctionsPolicy": ORIGIN + "/corrections/",
    }


def header(current: str) -> str:
    return f'''<header class="rt-site-header"><div class="rt-navbar">
<a class="mikhbar-brand" href="/en/" aria-label="Mikhbar"><span class="mikhbar-brand-mark"><img src="/assets/brand/mikhbar/06-web-ready/icon/mikhbar-logo-mark.png" alt="" width="64" height="64"></span><span class="mikhbar-brand-copy"><strong>Mikhbar</strong><small>MIKHBAR</small></span></a>
<button class="menu-button rt-menu-button" type="button" aria-label="Open navigation" aria-expanded="false" aria-controls="navigation"><svg aria-hidden="true" viewBox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h16"/></svg></button>
<nav class="nav-links rt-platform-nav" id="navigation" aria-label="Main navigation"><a href="/en/">Home</a><a href="/en/#latest">Latest</a><a href="/en/guides/">Guides</a><a href="/en/archive/">Archive</a><a href="/en/about/"{' aria-current="page"' if current == "about" else ""}>About Mikhbar</a><a href="/en/contact/"{' aria-current="page"' if current == "contact" else ""}>Contact</a><a class="rt-lang-switch" href="{PAGES[current]['ar_path']}" lang="ar">عربي</a></nav>
</div></header>'''


def footer() -> str:
    return '''<footer class="rt-footer"><div class="rt-shell rt-footer-grid">
<div class="rt-footer-brand"><strong>Mikhbar</strong><p>An independent bilingual technology publication.</p></div>
<div><h3>Publication</h3><div class="rt-footer-links"><a href="/en/archive/">Archive</a><a href="/en/about/">About</a><a href="/en/editorial-policy/">Editorial policy</a><a href="/en/contact/">Contact</a></div></div>
<div><h3>Trust</h3><div class="rt-footer-links"><a href="/en/corrections/">Corrections</a><a href="/en/ai-policy/">AI & automation</a></div></div>
</div><div class="rt-shell rt-copyright">© <span data-year></span> Mikhbar</div></footer>'''


def page_schema(key: str, spec: dict) -> str:
    canonical = ORIGIN + spec["en_path"]
    graph: list[dict] = [publisher_schema()]
    if spec["type"] == "ProfilePage":
        person_id = ORIGIN + "/authors/radwan-abdulhadi/#person"
        graph += [
            {
                "@type": "ProfilePage",
                "@id": canonical + "#profile",
                "url": canonical,
                "name": spec["title"],
                "description": spec["description"],
                "inLanguage": "en",
                "mainEntity": {"@id": person_id},
                "isPartOf": {"@id": ORIGIN + "/#website"},
            },
            {
                "@type": "Person",
                "@id": person_id,
                "name": "Radwan Abdulhadi",
                "alternateName": "رضوان عبدالهادي",
                "url": canonical,
                "jobTitle": "Editor and Technology Writer",
                "worksFor": {"@id": ORIGIN + "/#publisher"},
            },
        ]
    else:
        graph.append({
            "@type": spec["type"],
            "@id": canonical + "#page",
            "url": canonical,
            "name": spec["title"],
            "description": spec["description"],
            "inLanguage": "en",
            "about": {"@id": ORIGIN + "/#publisher"},
            "isPartOf": {"@id": ORIGIN + "/#website"},
        })
    graph.append({
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Mikhbar", "item": ORIGIN + "/en/"},
            {"@type": "ListItem", "position": 2, "name": spec["h1"]},
        ],
    })
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")


def english_page(key: str, spec: dict) -> str:
    canonical = ORIGIN + spec["en_path"]
    ar_url = ORIGIN + spec["ar_path"]
    body = "".join(f"<h2>{escape(title)}</h2><p>{text}</p>" for title, text in spec["sections"])
    return f'''<!DOCTYPE html><html lang="en" dir="ltr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#ffffff">
<title>{escape(spec["title"])}</title><meta name="description" content="{escape(spec["description"], quote=True)}"><meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
<link rel="canonical" href="{canonical}"><link rel="alternate" hreflang="ar" href="{ar_url}"><link rel="alternate" hreflang="en" href="{canonical}"><link rel="alternate" hreflang="x-default" href="{ar_url}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Mikhbar"><meta property="og:locale" content="en_US"><meta property="og:title" content="{escape(spec["title"], quote=True)}"><meta property="og:description" content="{escape(spec["description"], quote=True)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{LOGO}">
<meta name="twitter:card" content="summary"><meta name="twitter:title" content="{escape(spec["title"], quote=True)}"><meta name="twitter:description" content="{escape(spec["description"], quote=True)}"><meta name="twitter:image" content="{LOGO}">
<link rel="stylesheet" href="/styles.css"><link rel="stylesheet" href="/forum.css"><link rel="icon" href="/assets/brand/mikhbar/06-web-ready/favicon/favicon.ico"><link rel="apple-touch-icon" href="/assets/brand/mikhbar/06-web-ready/favicon/apple-touch-icon.png"><link rel="manifest" href="/assets/brand/mikhbar/06-web-ready/favicon/site.webmanifest">
<script type="application/ld+json">{page_schema(key, spec)}</script></head><body>{header(key)}
<main class="rt-shell rt-prose"><nav class="rt-breadcrumbs" aria-label="Breadcrumb"><a href="/en/">Mikhbar</a><span>›</span><span>{escape(spec["h1"])}</span></nav><span class="rt-label">{escape(spec["label"])}</span><h1>{escape(spec["h1"])}</h1>{body}</main>{footer()}<script src="/forum.js" defer></script></body></html>'''


def patch_arabic_page(key: str, spec: dict) -> bool:
    path = FORUM / spec["ar_path"].strip("/") / "index.html"
    if not path.exists():
        raise SystemExit(f"Arabic trust page is missing: {path}")
    text = path.read_text(encoding="utf-8")
    canonical = ORIGIN + spec["ar_path"]
    en_url = ORIGIN + spec["en_path"]
    hreflang = (
        f'<link rel="alternate" hreflang="ar" href="{canonical}">'
        f'<link rel="alternate" hreflang="en" href="{en_url}">'
        f'<link rel="alternate" hreflang="x-default" href="{canonical}">'
    )
    # Replace any previous trust-page hreflang block, otherwise insert after canonical.
    updated = re.sub(
        r'(?:<link rel="alternate" hreflang="(?:ar|en|x-default)" href="[^"]*">){1,3}',
        "",
        text,
        count=1,
    )
    canonical_tag = f'<link rel="canonical" href="{canonical}">'
    if canonical_tag not in updated:
        raise SystemExit(f"Canonical marker missing in Arabic trust page: {path}")
    updated = updated.replace(canonical_tag, canonical_tag + hreflang, 1)

    language_switch = f'href="{spec["en_path"]}" lang="en"'
    updated = re.sub(
        r'href="/en/" lang="en"',
        language_switch,
        updated,
        count=1,
    )
    if updated != text:
        path.write_text(updated, encoding="utf-8")
        return True
    return False



def patch_locale_navigation() -> int:
    changed = 0
    locale_specs = {
        "ar": {
            "brand": "مِخبار",
            "links": (
                '<a href="/ar/archive/">الأرشيف</a> · '
                '<a href="/about/">عن مِخبار</a> · '
                '<a href="/editorial-policy/">السياسة التحريرية</a> · '
                '<a href="/corrections/">التصحيحات</a> · '
                '<a href="/ai-policy/">سياسة الذكاء الاصطناعي</a> · '
                '<a href="/contact/">تواصل</a>'
            ),
        },
        "en": {
            "brand": "Mikhbar",
            "links": (
                '<a href="/en/archive/">Archive</a> · '
                '<a href="/en/about/">About</a> · '
                '<a href="/en/editorial-policy/">Editorial policy</a> · '
                '<a href="/en/corrections/">Corrections</a> · '
                '<a href="/en/ai-policy/">AI policy</a> · '
                '<a href="/en/contact/">Contact</a>'
            ),
        },
    }

    for locale, spec in locale_specs.items():
        for path in (FORUM / locale).rglob("index.html"):
            text = path.read_text(encoding="utf-8")
            updated = text
            if locale == "en":
                updated = updated.replace('href="/about/"', 'href="/en/about/"')

            simple_footer = (
                '<footer class="rt-footer"><div class="rt-shell rt-copyright">'
                f'© <span data-year></span> {spec["brand"]}</div></footer>'
            )
            if simple_footer in updated:
                updated = updated.replace(
                    simple_footer,
                    '<footer class="rt-footer"><div class="rt-shell rt-copyright">'
                    f'© <span data-year></span> {spec["brand"]} · {spec["links"]}</div></footer>',
                    1,
                )

            if updated != text:
                path.write_text(updated, encoding="utf-8")
                changed += 1
    return changed


def main() -> int:
    written = 0
    patched = 0
    for key, spec in PAGES.items():
        target = FORUM / spec["en_path"].strip("/") / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(english_page(key, spec), encoding="utf-8")
        written += 1
        patched += int(patch_arabic_page(key, spec))
    navigation_patched = patch_locale_navigation()
    print(
        f"Mikhbar multilingual trust pages: english_written={written} "
        f"arabic_hreflang_patched={patched} locale_navigation_patched={navigation_patched}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
