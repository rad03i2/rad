from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORUM = ROOT / "forum"

DISCOVERY_FILES = {
    "sitemap.xml",
    "news-sitemap.xml",
    "feed-ar.xml",
    "feed-en.xml",
    "robots.txt",
    "llms.txt",
}


def _is_public_shell(path: Path) -> bool:
    rel = path.relative_to(FORUM)
    if path.suffix.lower() == ".html" and len(rel.parts) <= 3:
        return True
    return rel.as_posix() in DISCOVERY_FILES


def _normalize(text: str) -> str:
    text = text.replace("https://rdwan.dev/forum", "https://mikhbar.website")
    text = text.replace("https://www.rdwan.dev/forum", "https://mikhbar.website")
    text = text.replace("https://rdwan.dev", "https://mikhbar.website")
    text = text.replace("https://www.rdwan.dev", "https://mikhbar.website")
    text = text.replace("www.rdwan.dev", "www.mikhbar.website")

    # Public Mikhbar lives at the domain root. Keep asset files such as
    # /forum.css and /forum.js intact while removing only the /forum/ URL prefix.
    text = text.replace('"/forum/', '"/')
    text = text.replace("'/forum/", "'/")
    text = text.replace("url=/forum/", "url=/")
    text = text.replace("https://mikhbar.website/forum/", "https://mikhbar.website/")
    return text


def normalize_public_identity() -> tuple[int, int]:
    changed = 0
    checked = 0
    for path in FORUM.rglob("*"):
        if not path.is_file() or not _is_public_shell(path):
            continue
        checked += 1
        original = path.read_text(encoding="utf-8")
        normalized = _normalize(original)
        if normalized != original:
            path.write_text(normalized, encoding="utf-8")
            changed += 1

    leftovers: list[str] = []
    for path in FORUM.rglob("*"):
        if not path.is_file() or not _is_public_shell(path):
            continue
        text = path.read_text(encoding="utf-8")
        if "rdwan.dev" in text:
            leftovers.append(path.relative_to(ROOT).as_posix())

    if leftovers:
        raise RuntimeError("Legacy rdwan.dev identity remains in public Mikhbar shells: " + ", ".join(leftovers[:20]))

    return checked, changed


def main() -> int:
    checked, changed = normalize_public_identity()
    print(f"Mikhbar public identity normalized: checked={checked} changed={changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
