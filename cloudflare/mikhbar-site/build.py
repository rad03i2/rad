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


def refresh_article_map() -> None:
    subprocess.run(
        [sys.executable, str(ROOT / "automation" / "forum" / "build_article_map.py")],
        cwd=ROOT,
        check=True,
    )


def rewrite_text(text: str) -> str:
    replacements = (
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
        ('"/forum/', '"/'),
        ("'/forum/", "'/"),
        ("url(/forum/", "url(/"),
        ("url('/forum/", "url('/"),
        ('url("/forum/', 'url("/'),
    )
    for old, new in replacements:
        text = text.replace(old, new)
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
        updated = rewrite_text(original)
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
    if stale:
        raise SystemExit("Legacy rdwan.dev/forum URLs remain in output: " + ", ".join(stale))

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
    write_platform_files()
    validate_output()
    files = sum(1 for path in OUT.rglob("*") if path.is_file())
    print(
        f"Mikhbar Cloudflare build complete: files={files} text_scanned={scanned} "
        f"text_rewritten={changed} static_article_dirs_pruned={pruned} output={OUT.relative_to(ROOT)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
