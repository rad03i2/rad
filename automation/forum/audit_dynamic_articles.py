from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORUM = ROOT / "forum"
DYNAMIC_ROUTE = re.compile(r"^/forum/(ar|en)/[a-z0-9-]+/[^/]+/?$", re.I)


def _load_posts(locale: str) -> list[dict]:
    path = FORUM / f"posts-{locale}.json"
    if locale == "ar" and not path.exists():
        path = FORUM / "posts.json"
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, list) else list(payload.get("posts", []))


def main() -> int:
    total = 0
    ready = 0
    legacy = 0
    missing: list[str] = []
    bad_json: list[str] = []
    seen: set[tuple[str, str]] = set()

    for locale in ("ar", "en"):
        for post in _load_posts(locale):
            url = str(post.get("url") or "").strip()
            if not url:
                continue
            if not DYNAMIC_ROUTE.match(url):
                legacy += 1
                continue
            key = (locale, url)
            if key in seen:
                continue
            seen.add(key)
            total += 1
            content_file = str(post.get("contentFile") or "").strip()
            if not content_file:
                missing.append(f"{locale}:{url}:missing-contentFile")
                continue
            path = ROOT / content_file
            if not path.is_file():
                missing.append(f"{locale}:{url}:{content_file}:missing-file")
                continue
            try:
                record = json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                bad_json.append(f"{locale}:{url}:{content_file}:{type(exc).__name__}")
                continue
            if not isinstance(record, dict) or not isinstance(record.get("locales", {}).get(locale), dict):
                bad_json.append(f"{locale}:{url}:{content_file}:missing-locale-record")
                continue
            ready += 1

    print(f"Mikhbar dynamic article audit: total={total} ready={ready} missing={len(missing)} invalid={len(bad_json)} legacy_static={legacy}")
    for item in missing[:50]:
        print("MISSING", item)
    for item in bad_json[:50]:
        print("INVALID", item)

    if missing or bad_json or ready != total:
        raise SystemExit(1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
