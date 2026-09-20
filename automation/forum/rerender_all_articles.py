from pathlib import Path

from common import load_json
from renderer import ROOT as REPO_ROOT, render_content_file

CONTENT = REPO_ROOT / "forum" / "content"


def main() -> int:
    rendered = 0
    skipped = 0
    for path in sorted(CONTENT.rglob("*.json")):
        record = load_json(path, {})
        if not isinstance(record, dict) or not record.get("slug") or not record.get("categorySlug"):
            skipped += 1
            continue
        outputs = render_content_file(path)
        if outputs:
            rendered += 1
    print(f"Re-rendered {rendered} historical article records; skipped {skipped}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
