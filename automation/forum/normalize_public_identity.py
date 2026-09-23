from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORUM = ROOT / "forum"

PUBLIC_SHELL_FILES = {
    "sitemap.xml",
    "news-sitemap.xml",
    "feed-ar.xml",
    "feed-en.xml",
    "robots.txt",
    "llms.txt",
}
DEPLOYMENT_INDEX_FILES = {
    "posts.json",
    "posts-ar.json",
    "posts-en.json",
}


def _is_public_shell(path: Path, include_post_indexes: bool) -> bool:
    rel = path.relative_to(FORUM)
    if path.suffix.lower() == ".html" and len(rel.parts) <= 3:
        return True
    rel_path = rel.as_posix()
    if rel_path in PUBLIC_SHELL_FILES:
        return True
    return include_post_indexes and rel_path in DEPLOYMENT_INDEX_FILES


def _normalize(text: str) -> str:
    # Canonical public identity: Mikhbar is a standalone publication.
    text = text.replace("https://www.rdwan.dev/forum", "https://mikhbar.website")
    text = text.replace("https://rdwan.dev/forum", "https://mikhbar.website")
    text = text.replace("https://www.rdwan.dev", "https://mikhbar.website")
    text = text.replace("https://rdwan.dev", "https://mikhbar.website")
    text = text.replace("www.rdwan.dev", "www.mikhbar.website")
    text = text.replace("rdwan.dev", "mikhbar.website")

    # Remove legacy personal-founder coupling from publication-level schema.
    text = re.sub(r',\s*"founder"\s*:\s*\{[^{}]*\}', "", text)

    text = text.replace("RDWAN Tech", "Mikhbar")
    text = text.replace("RDWAN TECH", "MIKHBAR")
    text = text.replace("Radwan Tech", "Mikhbar")
    text = text.replace("مؤسس ومحرر مِخبار", "محرر وكاتب تقني في مِخبار")
    text = text.replace("Founder and editor, Mikhbar", "Editor and technology writer, Mikhbar")
    text = text.replace(
        "Official bilingual technology publication: Mikhbar (مِخبار), within mikhbar.website.",
        "Official bilingual technology publication: Mikhbar (مِخبار).",
    )

    # Public deployment lives at the domain root. Keep real assets such as
    # /forum.css and /forum.js intact while removing only the /forum/ route prefix.
    text = text.replace('"/forum/', '"/')
    text = text.replace("'/forum/", "'/")
    text = text.replace("url=/forum/", "url=/")
    text = text.replace("https://mikhbar.website/forum/", "https://mikhbar.website/")
    return text


def normalize_public_identity(*, include_post_indexes: bool = False) -> tuple[int, int]:
    """Normalize public Mikhbar shells.

    Repository post indexes intentionally keep their internal /forum/... contract.
    Deployment-only callers set include_post_indexes=True so the published copies
    use root /ar/... and /en/... routes without mutating the repository contract.
    """
    changed = 0
    checked = 0
    for path in FORUM.rglob("*"):
        if not path.is_file() or not _is_public_shell(path, include_post_indexes):
            continue
        checked += 1
        original = path.read_text(encoding="utf-8")
        normalized = _normalize(original)
        if normalized != original:
            path.write_text(normalized, encoding="utf-8")
            changed += 1

    leftovers: list[str] = []
    for path in FORUM.rglob("*"):
        if not path.is_file() or not _is_public_shell(path, include_post_indexes):
            continue
        text = path.read_text(encoding="utf-8")
        if "rdwan.dev" in text:
            leftovers.append(path.relative_to(ROOT).as_posix())

    if leftovers:
        raise RuntimeError(
            "Legacy rdwan.dev identity remains in public Mikhbar shells: "
            + ", ".join(leftovers[:20])
        )

    return checked, changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--deployment",
        action="store_true",
        help="Also normalize deployment copies of posts*.json to public root routes.",
    )
    args = parser.parse_args()
    checked, changed = normalize_public_identity(include_post_indexes=args.deployment)
    print(
        "Mikhbar public identity normalized: "
        f"checked={checked} changed={changed} deployment={args.deployment}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
