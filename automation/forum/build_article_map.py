from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORUM = ROOT / "forum"
OUTPUT = FORUM / "article-map.json"


def _load_posts(locale: str) -> list[dict]:
    path = FORUM / f"posts-{locale}.json"
    if locale == "ar" and not path.exists():
        path = FORUM / "posts.json"
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    if isinstance(payload, list):
        return payload
    return list((payload or {}).get("posts", []))


def _normalize_route(value: str) -> str:
    route = str(value or "").strip()
    if not route:
        return ""
    if not route.startswith("/"):
        route = "/" + route
    while "//" in route:
        route = route.replace("//", "/")
    if not route.endswith("/"):
        route += "/"
    return route


def _content_url(value: str) -> str:
    raw = str(value or "").strip().replace("\\", "/")
    if not raw:
        return ""
    relative = raw.lstrip("/")
    candidate = (ROOT / relative).resolve()
    forum_content = (FORUM / "content").resolve()
    try:
        candidate.relative_to(forum_content)
    except ValueError:
        return ""
    if not candidate.is_file() or candidate.suffix.lower() != ".json":
        return ""
    return "/" + relative


def build_routes() -> dict[str, dict]:
    routes: dict[str, dict] = {}
    for locale in ("ar", "en"):
        for post in _load_posts(locale):
            route = _normalize_route(post.get("url"))
            content = _content_url(post.get("contentFile"))
            if not route or not content:
                continue
            routes[route] = {
                "content": content,
                "locale": locale,
                "id": post.get("id"),
                "slug": post.get("slug"),
                "category": post.get("categorySlug"),
                "updated": post.get("dateModified") or post.get("date"),
            }
    return dict(sorted(routes.items()))


def main() -> int:
    routes = build_routes()
    payload = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "template": "/forum/article/",
        "routeCount": len(routes),
        "routes": routes,
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Mikhbar dynamic article map: {len(routes)} routes -> {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
