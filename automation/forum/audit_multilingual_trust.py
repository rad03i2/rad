from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORUM = ROOT / "forum"
ORIGIN = "https://mikhbar.website"

# Arabic trust URLs stay stable; English equivalents live under /en/.
PAIRS = {
    "/about/": "/en/about/",
    "/contact/": "/en/contact/",
    "/editorial-policy/": "/en/editorial-policy/",
    "/corrections/": "/en/corrections/",
    "/ai-policy/": "/en/ai-policy/",
    "/authors/radwan-abdulhadi/": "/en/authors/radwan-abdulhadi/",
}


def local_file(public_path: str) -> Path:
    return FORUM / public_path.strip("/") / "index.html"


def check_page(path: str, locale: str, ar_path: str, en_path: str, errors: list[str]) -> None:
    file = local_file(path)
    label = path
    if not file.exists():
        errors.append(f"{label}: missing page")
        return
    html = file.read_text(encoding="utf-8")
    expected = {
        "lang": f'<html lang="{locale}"',
        "canonical": f'<link rel="canonical" href="{ORIGIN}{path}">',
        "hreflang ar": f'<link rel="alternate" hreflang="ar" href="{ORIGIN}{ar_path}">',
        "hreflang en": f'<link rel="alternate" hreflang="en" href="{ORIGIN}{en_path}">',
        "publisher": '"@id":"https://mikhbar.website/#publisher"',
    }
    for name, needle in expected.items():
        if needle not in html:
            errors.append(f"{label}: missing {name}")
    if re.search(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\'][^"\']*noindex', html, re.I):
        errors.append(f"{label}: unexpectedly noindex")
    if "rdwan.dev" in html:
        errors.append(f"{label}: legacy rdwan.dev identity remains")
    if locale == "en" and 'href="/about/"' in html:
        errors.append(f"{label}: English page links to Arabic About instead of /en/about/")


def main() -> int:
    errors: list[str] = []
    for ar_path, en_path in PAIRS.items():
        check_page(ar_path, "ar", ar_path, en_path, errors)
        check_page(en_path, "en", ar_path, en_path, errors)

    sitemap = (FORUM / "sitemap.xml").read_text(encoding="utf-8")
    for ar_path, en_path in PAIRS.items():
        for path in (ar_path, en_path):
            if f"<loc>{ORIGIN}{path}</loc>" not in sitemap:
                errors.append(f"sitemap missing trust URL: {path}")

    localized_trust = {
        "ar": ("/about/", "/contact/", "/editorial-policy/", "/corrections/", "/ai-policy/"),
        "en": ("/en/about/", "/en/contact/", "/en/editorial-policy/", "/en/corrections/", "/en/ai-policy/"),
    }
    for locale, trust_paths in localized_trust.items():
        home = (FORUM / locale / "index.html").read_text(encoding="utf-8")
        for trust_path in trust_paths:
            if f'href="{trust_path}"' not in home:
                errors.append(f"{locale} homepage missing localized trust link {trust_path}")

        # Topic hubs are one click from the locale home and should keep a route
        # back into the publication/trust graph rather than becoming dead ends.
        for slug in ("ai", "security", "automation", "robotics", "apps", "web", "mobile", "computers", "social"):
            hub = FORUM / locale / slug / "index.html"
            if not hub.exists():
                continue
            html = hub.read_text(encoding="utf-8")
            about_path = "/about/" if locale == "ar" else "/en/about/"
            if f'href="{about_path}"' not in html:
                errors.append(f"{locale}/{slug}: missing localized About link")

    for path in (
        FORUM / "en" / "guides" / "index.html",
        FORUM / "en" / "guides" / "artificial-intelligence" / "index.html",
        FORUM / "en" / "guides" / "cybersecurity" / "index.html",
        FORUM / "en" / "guides" / "robotics" / "index.html",
    ):
        if path.exists() and 'href="/en/about/"' not in path.read_text(encoding="utf-8"):
            errors.append(f"{path.relative_to(FORUM)}: English guide missing localized About link")

    if errors:
        for error in errors:
            print("ERROR:", error, file=sys.stderr)
        print(f"Mikhbar multilingual trust audit failed: errors={len(errors)}", file=sys.stderr)
        return 1
    print(f"Mikhbar multilingual trust audit: pairs={len(PAIRS)} errors=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
