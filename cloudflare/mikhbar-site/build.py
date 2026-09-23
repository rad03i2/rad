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
# per-article author attribution, but remove that personal relationship from the
# site-level publisher entity in the deployable build.
PUBLISHER_FOUNDER_RE = re.compile(
    r',\s*"founder"\s*:\s*\{\s*"@type"\s*:\s*"Person"\s*,\s*'
    r'"name"\s*:\s*"Radwan Abdulhadi"\s*,\s*'
    r'"url"\s*:\s*"https://rdwan\.dev/"\s*\}',
    re.I,
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
)


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

    text = PUBLISHER_FOUNDER_RE.sub("", text)

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
        if PUBLISHER_FOUNDER_RE.search(text):
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
