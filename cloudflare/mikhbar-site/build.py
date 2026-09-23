from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "forum"
ASSETS = ROOT / "assets"
WELL_KNOWN = ROOT / ".well-known"
OUT = ROOT / "dist" / "mikhbar"
PUBLIC_ORIGIN = "https://mikhbar.website"
INDEXNOW_KEY = "ff7de3f199bfcac8fda652aec7caabcd"
TEXT_SUFFIXES = {".html", ".xml", ".json", ".js", ".css", ".txt", ".webmanifest"}
MAX_WORKER_ASSET_BYTES = 24 * 1024 * 1024
ARTICLE_RUNTIME_PATH = "article/article.js"

CANONICAL_SCRIPT_RE = re.compile(
    r'<script\s+id=["\']canonical-host-redirect["\'][^>]*>.*?</script>',
    re.I | re.S,
)
CANONICAL_SCRIPT = (
    '<script id="canonical-host-redirect">'
    "(()=>{const h=location.hostname.toLowerCase();"
    "if(h==='www.mikhbar.website'||location.protocol==='http:'){"
    "location.replace('https://mikhbar.website'+location.pathname+location.search+location.hash)"
    "}})();"
    "</script>"
)

# Mikhbar is a standalone search/publisher entity. Historical source pages used
# Radwan's personal identity as the NewsMediaOrganization founder. Keep factual
# per-article author attribution, but remove that relationship from the site-level
# publisher entity in the deployable Mikhbar build.
PUBLISHER_FOUNDER_PATTERNS = (
    re.compile(
        r',\s*"founder"\s*:\s*\{\s*"@type"\s*:\s*"Person"\s*,\s*'
        r'"name"\s*:\s*"Radwan Abdulhadi"\s*,\s*'
        r'"url"\s*:\s*"https://(?:rdwan\.dev|mikhbar\.website)/"\s*\}',
        re.I,
    ),
    re.compile(
        r',\s*"founder"\s*:\s*\{\s*"@id"\s*:\s*'
        r'"https://mikhbar\.website/authors/radwan-abdulhadi/#person"\s*\}',
        re.I,
    ),
)
NEWS_PUBLISHER_FOUNDER_RE = re.compile(
    r'"@type"\s*:\s*"NewsMediaOrganization".{0,1400}?"founder"\s*:',
    re.I | re.S,
)

ABSOLUTE_REPLACEMENTS = (
    ("https://www.rdwan.dev/forum/", f"{PUBLIC_ORIGIN}/"),
    ("https://rdwan.dev/forum/", f"{PUBLIC_ORIGIN}/"),
    ("http://www.rdwan.dev/forum/", f"{PUBLIC_ORIGIN}/"),
    ("http://rdwan.dev/forum/", f"{PUBLIC_ORIGIN}/"),
    ("https://www.rdwan.dev/forum", PUBLIC_ORIGIN),
    ("https://rdwan.dev/forum", PUBLIC_ORIGIN),
    ("http://www.rdwan.dev/forum", PUBLIC_ORIGIN),
    ("http://rdwan.dev/forum", PUBLIC_ORIGIN),
    ("https://www.rdwan.dev/assets/", f"{PUBLIC_ORIGIN}/assets/"),
    ("https://rdwan.dev/assets/", f"{PUBLIC_ORIGIN}/assets/"),
    ("http://www.rdwan.dev/assets/", f"{PUBLIC_ORIGIN}/assets/"),
    ("http://rdwan.dev/assets/", f"{PUBLIC_ORIGIN}/assets/"),
)

PATH_REPLACEMENTS = (
    ('"/forum/', '"/'),
    ("'/forum/", "'/"),
    ("url(/forum/", "url(/"),
    ("url('/forum/", "url('/"),
    ('url("/forum/', 'url("/'),
)

# Visible copy left from the pre-split RDWAN Tech era. These replacements are
# intentionally narrow so historical article text and source names remain intact.
STANDALONE_COPY_REPLACEMENTS = (
    ("A bilingual technology publication within rdwan.dev.", "An independent bilingual technology publication."),
    ("Official bilingual technology publication: Mikhbar (مِخبار), within rdwan.dev.", "Official independent bilingual technology publication: Mikhbar (مِخبار)."),
    ("مِخبار منصة أخبار ومحتوى تقني ضمن موقع rdwan.dev،", "مِخبار منصة أخبار ومحتوى تقني مستقلة،"),
    ("© <span data-year></span> RDWAN Tech", "© <span data-year></span> Mikhbar"),
    (
        '<h2>المشاريع البرمجية</h2><p>يمكن الاطلاع على المشاريع والأعمال البرمجية من <a href="../../../">الصفحة الرئيسية rdwan.dev</a>، بينما يخصص مِخبار للأخبار والتحليلات والشروحات التقنية.</p>',
        "",
    ),
)

ROOT_INDEX_HTML = f'''<!doctype html>
<html lang="en" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#ffffff">
<title>Mikhbar | مِخبار — Technology News</title>
<meta name="description" content="Mikhbar is an independent bilingual technology publication covering AI, cybersecurity, software, mobile, computing, robotics and the web in Arabic and English.">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
<link rel="canonical" href="{PUBLIC_ORIGIN}/">
<link rel="alternate" hreflang="ar" href="{PUBLIC_ORIGIN}/ar/">
<link rel="alternate" hreflang="en" href="{PUBLIC_ORIGIN}/en/">
<link rel="alternate" hreflang="x-default" href="{PUBLIC_ORIGIN}/">
<link rel="alternate" type="application/rss+xml" title="مِخبار — العربية" href="{PUBLIC_ORIGIN}/feed-ar.xml">
<link rel="alternate" type="application/rss+xml" title="Mikhbar — English" href="{PUBLIC_ORIGIN}/feed-en.xml">
<link rel="icon" href="/assets/brand/mikhbar/06-web-ready/favicon/favicon.ico">
<link rel="icon" type="image/svg+xml" href="/assets/brand/mikhbar/06-web-ready/favicon/favicon.svg">
<link rel="apple-touch-icon" href="/assets/brand/mikhbar/06-web-ready/favicon/apple-touch-icon.png">
<link rel="manifest" href="/assets/brand/mikhbar/06-web-ready/favicon/site.webmanifest">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Mikhbar">
<meta property="og:title" content="Mikhbar | مِخبار">
<meta property="og:description" content="Independent technology news and analysis in Arabic and English.">
<meta property="og:url" content="{PUBLIC_ORIGIN}/">
<meta property="og:image" content="{PUBLIC_ORIGIN}/assets/social/home.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Mikhbar | مِخبار">
<meta name="twitter:description" content="Independent technology news and analysis in Arabic and English.">
<meta name="twitter:image" content="{PUBLIC_ORIGIN}/assets/social/home.jpg">
<script type="application/ld+json">{{"@context":"https://schema.org","@graph":[{{"@type":"WebSite","@id":"{PUBLIC_ORIGIN}/#website","url":"{PUBLIC_ORIGIN}/","name":"Mikhbar","alternateName":["مِخبار","mikhbar.website"],"inLanguage":["ar","en"],"publisher":{{"@id":"{PUBLIC_ORIGIN}/#publisher"}}}},{{"@type":"NewsMediaOrganization","@id":"{PUBLIC_ORIGIN}/#publisher","name":"Mikhbar","alternateName":"مِخبار","url":"{PUBLIC_ORIGIN}/","logo":{{"@type":"ImageObject","url":"{PUBLIC_ORIGIN}/assets/brand/mikhbar/06-web-ready/icon/mikhbar-app-icon-512.png"}},"description":"Independent technology news and analysis in Arabic and English.","publishingPrinciples":"{PUBLIC_ORIGIN}/editorial-policy/"}}]}}</script>
<style>html{{color-scheme:light}}body{{margin:0;font-family:system-ui,-apple-system,"Segoe UI",sans-serif;background:#f7f7f5;color:#151515;min-height:100vh;display:grid;place-items:center}}main{{width:min(760px,calc(100% - 40px));text-align:center}}img{{width:84px;height:84px;object-fit:contain}}h1{{font-size:clamp(2.2rem,7vw,4.5rem);margin:.45rem 0 .3rem}}p{{font-size:1.05rem;line-height:1.8;color:#565656;max-width:650px;margin:.4rem auto 1.5rem}}nav{{display:flex;flex-wrap:wrap;justify-content:center;gap:12px}}a{{display:inline-flex;align-items:center;justify-content:center;min-width:150px;padding:13px 20px;border-radius:999px;text-decoration:none;font-weight:700;border:1px solid #d8d8d4;color:#151515;background:#fff}}a:first-child{{background:#151515;color:#fff;border-color:#151515}}small{{display:block;margin-top:1.4rem;color:#777}}</style>
</head>
<body>
<main>
<img src="/assets/brand/mikhbar/06-web-ready/icon/mikhbar-logo-mark.png" width="84" height="84" alt="Mikhbar logo">
<h1>Mikhbar <span lang="ar" dir="rtl">| مِخبار</span></h1>
<p>Independent technology news and analysis in Arabic and English.<br><span lang="ar" dir="rtl">منصة تقنية مستقلة للأخبار والتحليلات بالعربية والإنجليزية.</span></p>
<nav aria-label="Choose edition"><a href="/ar/" lang="ar" dir="rtl">النسخة العربية</a><a href="/en/" lang="en">English Edition</a></nav>
<small>mikhbar.website</small>
</main>
</body>
</html>'''


def refresh_article_map() -> None:
    subprocess.run(
        [sys.executable, str(ROOT / "automation" / "forum" / "build_article_map.py")],
        cwd=ROOT,
        check=True,
    )


def rewrite_text(text: str, suffix: str, relative_path: str) -> str:
    for old, new in ABSOLUTE_REPLACEMENTS:
        text = text.replace(old, new)

    # The article fallback runtime deliberately understands both repository-era
    # /forum routes and root production routes. Preserve those guards. Other JS
    # (notably forum.js) is a deployable site asset and must use root paths.
    if relative_path != ARTICLE_RUNTIME_PATH:
        for old, new in PATH_REPLACEMENTS:
            text = text.replace(old, new)

    for old, new in STANDALONE_COPY_REPLACEMENTS:
        text = text.replace(old, new)

    for pattern in PUBLISHER_FOUNDER_PATTERNS:
        text = pattern.sub("", text)

    if suffix == ".html":
        text = CANONICAL_SCRIPT_RE.sub(CANONICAL_SCRIPT, text)
    return text


def rewrite_output() -> tuple[int, int]:
    changed = 0
    scanned = 0
    for path in OUT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        scanned += 1
        try:
            original = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        relative_path = path.relative_to(OUT).as_posix()
        updated = rewrite_text(original, path.suffix.lower(), relative_path)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    return scanned, changed


def prune_dynamic_article_html() -> int:
    map_path = OUT / "article-map.json"
    if not map_path.exists():
        raise SystemExit("article-map.json is missing from Cloudflare output")
    payload = json.loads(map_path.read_text(encoding="utf-8"))
    routes = payload.get("routes", {}) if isinstance(payload, dict) else {}
    removed = 0
    seen_dirs: set[Path] = set()

    for route in routes:
        parts = [part for part in str(route).strip("/").split("/") if part]
        if len(parts) != 3 or parts[0] not in {"ar", "en"}:
            continue
        locale, category, slug = parts
        for directory in (OUT / locale / category / slug, OUT / category / slug):
            if directory in seen_dirs:
                continue
            seen_dirs.add(directory)
            if directory.is_dir():
                shutil.rmtree(directory)
                removed += 1

    return removed


def prune_oversized_assets() -> list[str]:
    removed: list[str] = []
    for path in OUT.rglob("*"):
        if not path.is_file():
            continue
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if size <= MAX_WORKER_ASSET_BYTES:
            continue
        removed.append(f"{path.relative_to(OUT).as_posix()} ({size / 1024 / 1024:.1f} MiB)")
        path.unlink()
    return removed


def validate_article_runtime() -> None:
    runtime = OUT / ARTICLE_RUNTIME_PATH
    if not runtime.exists():
        raise SystemExit("Article runtime is missing from Cloudflare output")

    text = runtime.read_text(encoding="utf-8")
    required_guards = (
        "location.pathname.startsWith('/forum/') ? SOURCE_PREFIX : ''",
        "out.startsWith('/forum/')",
    )
    missing = [guard for guard in required_guards if guard not in text]
    if missing:
        raise SystemExit(
            "Article runtime routing guards were mutated during build: "
            + ", ".join(missing)
        )

    corrupted = (
        "location.pathname.startsWith('/') ? SOURCE_PREFIX : ''",
        "if (out.startsWith('/')) out = out.slice('/forum'.length)",
    )
    found = [needle for needle in corrupted if needle in text]
    if found:
        raise SystemExit(
            "Corrupted article runtime routing logic found in Cloudflare output: "
            + ", ".join(found)
        )


def validate_root_search_identity() -> None:
    text = (OUT / "index.html").read_text(encoding="utf-8")
    required = (
        '"@type":"WebSite"',
        '"name":"Mikhbar"',
        '"alternateName":["مِخبار","mikhbar.website"]',
        f'"url":"{PUBLIC_ORIGIN}/"',
        'hreflang="x-default"',
        'href="/ar/"',
        'href="/en/"',
    )
    missing = [needle for needle in required if needle not in text]
    if missing:
        raise SystemExit("Root search identity is incomplete: " + ", ".join(missing))
    if "navigator.language" in text or "location.replace" in text:
        raise SystemExit("Root x-default page must remain crawlable and must not auto-redirect by browser language")


def validate_output() -> None:
    required = [
        OUT / "index.html",
        OUT / "ar" / "index.html",
        OUT / "en" / "index.html",
        OUT / "article" / "index.html",
        OUT / "article-map.json",
        OUT / "sitemap.xml",
        OUT / "feed-ar.xml",
        OUT / "feed-en.xml",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        raise SystemExit("Missing required Cloudflare output: " + ", ".join(missing))

    stale = []
    publisher_identity_leaks = []
    for path in OUT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if "rdwan.dev/forum" in text:
            stale.append(str(path.relative_to(OUT)))
            if len(stale) >= 20:
                break
        if NEWS_PUBLISHER_FOUNDER_RE.search(text):
            publisher_identity_leaks.append(str(path.relative_to(OUT)))
            if len(publisher_identity_leaks) >= 20:
                break
    if stale:
        raise SystemExit("Legacy rdwan.dev/forum URLs remain in output: " + ", ".join(stale))
    if publisher_identity_leaks:
        raise SystemExit(
            "Personal founder identity remains in Mikhbar publisher schema: "
            + ", ".join(publisher_identity_leaks)
        )

    validate_root_search_identity()
    validate_article_runtime()

    payload = json.loads((OUT / "article-map.json").read_text(encoding="utf-8"))
    leftovers = []
    for route in payload.get("routes", {}):
        parts = [part for part in str(route).strip("/").split("/") if part]
        if len(parts) != 3 or parts[0] not in {"ar", "en"}:
            continue
        if (OUT / parts[0] / parts[1] / parts[2] / "index.html").exists():
            leftovers.append(route)
            if len(leftovers) >= 20:
                break
    if leftovers:
        raise SystemExit("Per-article static HTML still exists for dynamic routes: " + ", ".join(leftovers))

    oversized = [
        str(path.relative_to(OUT))
        for path in OUT.rglob("*")
        if path.is_file() and path.stat().st_size > MAX_WORKER_ASSET_BYTES
    ]
    if oversized:
        raise SystemExit("Oversized Worker assets remain: " + ", ".join(oversized[:20]))


def write_platform_files() -> None:
    # Keep / as a stable x-default landing page. The two language editions are
    # linked explicitly instead of being selected with a client-side redirect.
    (OUT / "index.html").write_text(ROOT_INDEX_HTML, encoding="utf-8")
    (OUT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\n"
        f"Sitemap: {PUBLIC_ORIGIN}/sitemap.xml\n"
        f"Sitemap: {PUBLIC_ORIGIN}/news-sitemap.xml\n",
        encoding="utf-8",
    )
    (OUT / f"{INDEXNOW_KEY}.txt").write_text(INDEXNOW_KEY + "\n", encoding="utf-8")
    (OUT / "404.html").write_text(
        "<!doctype html><html lang=\"ar\" dir=\"rtl\"><meta charset=\"utf-8\">"
        "<meta name=\"robots\" content=\"noindex,follow\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        "<title>404 | مِخبار</title><body style=\"font-family:system-ui;background:#0f1115;color:#fff;"
        "display:grid;place-items:center;min-height:100vh;margin:0\"><main><h1>404</h1>"
        "<p>الصفحة غير موجودة.</p><p><a style=\"color:#9fe870\" href=\"/\">العودة إلى مِخبار</a></p>"
        "</main></body></html>",
        encoding="utf-8",
    )


def main() -> int:
    if not SOURCE.exists():
        raise SystemExit("forum/ source directory is missing")

    refresh_article_map()

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SOURCE, OUT)
    if ASSETS.exists():
        shutil.copytree(ASSETS, OUT / "assets", dirs_exist_ok=True)
    if WELL_KNOWN.exists():
        shutil.copytree(WELL_KNOWN, OUT / ".well-known", dirs_exist_ok=True)

    scanned, changed = rewrite_output()
    pruned = prune_dynamic_article_html()
    oversized = prune_oversized_assets()
    write_platform_files()
    validate_output()
    files = sum(1 for path in OUT.rglob("*") if path.is_file())
    print(
        f"Mikhbar Cloudflare build complete: files={files} text_scanned={scanned} "
        f"text_rewritten={changed} static_article_dirs_pruned={pruned} "
        f"oversized_assets_pruned={len(oversized)} output={OUT.relative_to(ROOT)}"
    )
    for item in oversized:
        print(f"Pruned oversized source asset: {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
