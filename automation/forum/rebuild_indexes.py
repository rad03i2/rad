from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from indexes import FORUM, write_all
from normalize_public_identity import normalize_public_identity

TZ = timezone(timedelta(hours=3))


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError):
        return default


def main() -> int:
    ar_fallback = load_json(FORUM / "posts.json", {"posts": []})
    ar_payload = load_json(FORUM / "posts-ar.json", ar_fallback)
    en_payload = load_json(FORUM / "posts-en.json", {"posts": []})
    ar_posts = list(ar_payload.get("posts", []) if isinstance(ar_payload, dict) else ar_payload or [])
    en_posts = list(en_payload.get("posts", []) if isinstance(en_payload, dict) else en_payload or [])
    write_all({"ar": ar_posts, "en": en_posts}, datetime.now(TZ))

    # rebuild_indexes is used for public discovery/deployment output, so its
    # working-tree copies of posts*.json are normalized to root public routes.
    # Publisher workflows use the normalizer without this flag and preserve the
    # repository's internal /forum/... contract.
    checked, changed = normalize_public_identity(include_post_indexes=True)
    print(
        f"Mikhbar indexes rebuilt: ar={len(ar_posts)} en={len(en_posts)} "
        f"normalized={changed}/{checked} deployment_indexes=true"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
