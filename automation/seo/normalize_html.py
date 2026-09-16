from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CANONICAL_HOST = "rdwan.dev"
CANONICAL_ORIGIN = "https://rdwan.dev"
SCRIPT_ID = "canonical-host-redirect"
SCRIPT = (
    '<script id="canonical-host-redirect">'
    "(()=>{const h=location.hostname.toLowerCase();"
    "if(h==='www.rdwan.dev'||location.protocol==='http:'){"
    "location.replace('https://rdwan.dev'+location.pathname+location.search+location.hash)"
    "}})();"
    "</script>"
)

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "build"}


def html_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*.html"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        files.append(path)
    return sorted(files)


def normalize_urls(text: str) -> str:
    text = text.replace("http://www.rdwan.dev", CANONICAL_ORIGIN)
    text = text.replace("https://www.rdwan.dev", CANONICAL_ORIGIN)
    text = text.replace("http://rdwan.dev", CANONICAL_ORIGIN)
    return text


def inject_or_replace_redirect(text: str) -> str:
    pattern = re.compile(
        r'<script\s+id=["\']canonical-host-redirect["\'][^>]*>.*?</script>',
        re.I | re.S,
    )
    if pattern.search(text):
        return pattern.sub(SCRIPT, text, count=1)

    head_match = re.search(r"<head(?:\s[^>]*)?>", text, re.I)
    if not head_match:
        return text
    insert_at = head_match.end()
    return text[:insert_at] + SCRIPT + text[insert_at:]


def normalize_file(path: Path) -> bool:
    try:
        original = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False

    updated = normalize_urls(original)
    updated = inject_or_replace_redirect(updated)
    if updated == original:
        return False

    path.write_text(updated, encoding="utf-8")
    return True


def main() -> int:
    changed: list[str] = []
    scanned = 0
    for path in html_files():
        scanned += 1
        if normalize_file(path):
            changed.append(path.relative_to(ROOT).as_posix())

    print(f"Canonical host normalization: scanned={scanned} changed={len(changed)}")
    for item in changed:
        print(f"  normalized: {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
