from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from indexes import FORUM, write_all
from normalize_public_identity import normalize_public_identity
from pillar_discovery import integrate_pillar_discovery

TZ = timezone(timedelta(hours=3))


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError):
        return default


def _unique_strings(values, limit: int) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values or []:
        text = " ".join(str(value or "").split()).strip()
        key = text.casefold()
        if not text or key in seen:
            continue
        seen.add(key)
        result.append(text)
        if len(result) >= limit:
            break
    return result


def _content_record(post: dict) -> dict:
    raw = str(post.get("contentFile") or "").strip().replace("\\", "/")
    if not raw:
        return {}
    root = FORUM.parent.resolve()
    candidate = (root / raw.lstrip("/")).resolve()
    content_root = (FORUM / "content").resolve()
    try:
        candidate.relative_to(content_root)
    except ValueError:
        return {}
    return load_json(candidate, {}) if candidate.is_file() else {}


def enrich_semantic_metadata(posts: list[dict], locale: str) -> tuple[int, int, int]:
    content_backed = 0
    tags_backfilled = 0
    entities_backfilled = 0
    for post in posts:
        record = _content_record(post)
        if not record:
            continue
        content_backed += 1
        view = ((record.get("locales") or {}).get(locale) or {})
        tags = _unique_strings(view.get("tags") or post.get("tags") or [], 12)
        entities = _unique_strings(view.get("entities") or post.get("entities") or [], 16)
        if tags:
            if tags != list(post.get("tags") or []):
                tags_backfilled += 1
            post["tags"] = tags
        if entities:
            if entities != list(post.get("entities") or []):
                entities_backfilled += 1
            post["entities"] = entities
    return content_backed, tags_backfilled, entities_backfilled


def save_posts(path: Path, posts: list[dict]) -> None:
    path.write_text(json.dumps({"posts": posts}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    ar_fallback = load_json(FORUM / "posts.json", {"posts": []})
    ar_payload = load_json(FORUM / "posts-ar.json", ar_fallback)
    en_payload = load_json(FORUM / "posts-en.json", {"posts": []})
    ar_posts = list(ar_payload.get("posts", []) if isinstance(ar_payload, dict) else ar_payload or [])
    en_posts = list(en_payload.get("posts", []) if isinstance(en_payload, dict) else en_payload or [])

    ar_semantic = enrich_semantic_metadata(ar_posts, "ar")
    en_semantic = enrich_semantic_metadata(en_posts, "en")
    save_posts(FORUM / "posts-ar.json", ar_posts)
    save_posts(FORUM / "posts-en.json", en_posts)
    save_posts(FORUM / "posts.json", ar_posts)

    write_all({"ar": ar_posts, "en": en_posts}, datetime.now(TZ))

    # rebuild_indexes is used for public discovery/deployment output, so its
    # working-tree copies of posts*.json are normalized to root public routes.
    # Publisher workflows use the normalizer without this flag and preserve the
    # repository's internal /forum/... contract.
    checked, changed = normalize_public_identity(include_post_indexes=True)
    sitemap_rows, llms_sections = integrate_pillar_discovery()
    print(
        f"Mikhbar indexes rebuilt: ar={len(ar_posts)} en={len(en_posts)} "
        f"normalized={changed}/{checked} deployment_indexes=true "
        f"semantic_ar={ar_semantic[0]}:{ar_semantic[1]}:{ar_semantic[2]} "
        f"semantic_en={en_semantic[0]}:{en_semantic[1]}:{en_semantic[2]} "
        f"pillar_sitemap_rows={sitemap_rows} pillar_llms_sections={llms_sections}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
