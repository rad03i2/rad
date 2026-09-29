from __future__ import annotations

import json
from pathlib import Path

from entity_hub_config import MIN_PAIRED_STORIES

ROOT = Path(__file__).resolve().parents[2]
FORUM = ROOT / "forum"
ORIGIN = "https://mikhbar.website"


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def main() -> int:
    errors: list[str] = []
    manifest = load_json(FORUM / "entity-hubs.json", {})
    entities = manifest.get("entities", []) if isinstance(manifest, dict) else []
    if not entities:
        errors.append("entity manifest has no qualified entities")

    sitemap = (FORUM / "sitemap.xml").read_text(encoding="utf-8")
    posts_by_locale = {}
    posts_by_id = {}
    for locale in ("ar", "en"):
        payload = load_json(FORUM / f"posts-{locale}.json", {"posts": []})
        posts = payload.get("posts", []) if isinstance(payload, dict) else payload
        posts_by_locale[locale] = posts
        posts_by_id[locale] = {str(post.get("id") or ""): post for post in posts}

        index = FORUM / locale / "entities" / "index.html"
        if not index.exists():
            errors.append(f"{locale}: missing entity index")
        else:
            html = index.read_text(encoding="utf-8")
            if 'data-entity-index="true"' not in html:
                errors.append(f"{locale}: entity index marker missing")
            if f'rel="canonical" href="{ORIGIN}/{locale}/entities/"' not in html:
                errors.append(f"{locale}: entity index canonical missing")
            if 'hreflang="ar"' not in html or 'hreflang="en"' not in html:
                errors.append(f"{locale}: entity index hreflang incomplete")

        home = FORUM / locale / "index.html"
        if home.exists() and f'href="/{locale}/entities/"' not in home.read_text(encoding="utf-8"):
            errors.append(f"{locale}: homepage missing entity directory link")

    qualified_slugs = {str(entity.get("slug") or "") for entity in entities}
    for locale in ("ar", "en"):
        root = FORUM / locale / "entities"
        if root.exists():
            actual = {
                child.name
                for child in root.iterdir()
                if child.is_dir() and (child / "index.html").exists()
            }
            stale = actual - qualified_slugs
            if stale:
                errors.append(f"{locale}: stale/unqualified entity pages {sorted(stale)}")

    for entity in entities:
        slug = str(entity.get("slug") or "")
        name = str(entity.get("name") or "")
        story_count = int(entity.get("storyCount") or 0)
        story_ids = [str(value) for value in entity.get("storyIds", []) if str(value)]
        if story_count < MIN_PAIRED_STORIES:
            errors.append(f"{slug}: thin entity hub count={story_count}")
        if len(story_ids) != story_count:
            errors.append(f"{slug}: story ID count mismatch")
        if not entity.get("categories"):
            errors.append(f"{slug}: coverage map empty")

        for locale in ("ar", "en"):
            route = f"/{locale}/entities/{slug}/"
            target = FORUM / locale / "entities" / slug / "index.html"
            if not target.exists():
                errors.append(f"{route}: missing")
                continue
            html = target.read_text(encoding="utf-8")
            checks = {
                "marker": f'data-entity="{slug}"',
                "canonical": f'rel="canonical" href="{ORIGIN}{route}"',
                "hreflang ar": 'hreflang="ar"',
                "hreflang en": 'hreflang="en"',
                "schema organization": '"@type":"Organization"',
            }
            for label, needle in checks.items():
                if needle not in html:
                    errors.append(f"{route}: missing {label}")
            link_count = html.count('data-entity-story="true"')
            if link_count < MIN_PAIRED_STORIES:
                errors.append(f"{route}: too few story links ({link_count})")
            if f"{ORIGIN}{route}" not in sitemap:
                errors.append(f"{route}: sitemap entry missing")

            for story_id in story_ids:
                post = posts_by_id[locale].get(story_id)
                if not post:
                    errors.append(f"{route}: paired story missing from {locale} index: {story_id}")
                    continue
                hubs = post.get("entityHubs") or []
                if not any(str(hub.get("slug") or "") == slug for hub in hubs if isinstance(hub, dict)):
                    errors.append(f"{route}: story {story_id} missing entityHubs annotation")

        inbound_found = False
        for locale in ("ar", "en"):
            for category in entity.get("categories", {}):
                hub = FORUM / locale / category / "index.html"
                if hub.exists() and f'/entities/{slug}/' in hub.read_text(encoding="utf-8"):
                    inbound_found = True
                    break
            if inbound_found:
                break
        if not inbound_found:
            errors.append(f"{slug}: no topic-hub inbound discovery link")

    for locale in ("ar", "en"):
        if f"{ORIGIN}/{locale}/entities/" not in sitemap:
            errors.append(f"sitemap missing /{locale}/entities/")

    if errors:
        print("Mikhbar entity architecture audit failed:")
        for error in errors[:100]:
            print(" -", error)
        return 1

    print(
        f"Mikhbar entity architecture audit: qualified={len(entities)} "
        f"threshold={MIN_PAIRED_STORIES} thin=0 stale=0 bilingual=ok annotations=ok"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
