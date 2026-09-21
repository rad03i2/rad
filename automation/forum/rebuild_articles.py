from __future__ import annotations

from pathlib import Path

from common import load_json
from renderer import FORUM, render_to_file

CONTENT = FORUM / "content"


def main() -> int:
    files = sorted(CONTENT.rglob("*.json")) if CONTENT.exists() else []
    rebuilt = 0
    skipped = 0
    for path in files:
        record = load_json(path, {})
        if not record or record.get("template") != "article" or not record.get("slug") or not record.get("categorySlug"):
            skipped += 1
            continue
        render_to_file(record)
        rebuilt += 1
    print(f"Mikhbar rebuild: rebuilt={rebuilt} skipped={skipped} template=forum/templates/article.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
