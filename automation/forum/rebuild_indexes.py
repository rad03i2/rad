from __future__ import annotations

from datetime import datetime, timedelta, timezone

from common import load_json
from indexes import FORUM, write_all

TZ = timezone(timedelta(hours=3))


def main() -> int:
    ar_posts = list(load_json(FORUM / "posts-ar.json", load_json(FORUM / "posts.json", {"posts": []})).get("posts", []))
    en_posts = list(load_json(FORUM / "posts-en.json", {"posts": []}).get("posts", []))
    write_all({"ar": ar_posts, "en": en_posts}, datetime.now(TZ))
    print(f"RDWAN Tech indexes rebuilt: ar={len(ar_posts)} en={len(en_posts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
