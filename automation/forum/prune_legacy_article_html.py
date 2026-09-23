from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORUM = ROOT / "forum"
MAP_PATH = FORUM / "article-map.json"
MIN_EXPECTED_ROUTES = 400


def load_map() -> dict:
    payload = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    routes = payload.get("routes", {}) if isinstance(payload, dict) else {}
    if not isinstance(routes, dict):
        raise RuntimeError("article-map.json routes must be an object")
    if len(routes) < MIN_EXPECTED_ROUTES:
        raise RuntimeError(
            f"Refusing cleanup: only {len(routes)} dynamic routes found; expected at least {MIN_EXPECTED_ROUTES}."
        )
    return routes


def candidate_indexes(routes: dict) -> tuple[list[Path], list[str]]:
    candidates: set[Path] = set()
    errors: list[str] = []

    for route, entry in routes.items():
        parts = [part for part in str(route).strip("/").split("/") if part]
        if len(parts) == 4 and parts[0] == "forum":
            _, locale, category, slug = parts
        elif len(parts) == 3 and parts[0] in {"ar", "en"}:
            locale, category, slug = parts
        else:
            errors.append(f"Unexpected dynamic route shape: {route}")
            continue

        if locale not in {"ar", "en"}:
            errors.append(f"Unexpected locale in dynamic route: {route}")
            continue

        content = str((entry or {}).get("content") or "").lstrip("/")
        if not content:
            errors.append(f"Route has no structured content path: {route}")
            continue
        content_path = ROOT / content
        if not content_path.exists() or content_path.suffix.lower() != ".json":
            errors.append(f"Structured JSON missing for {route}: {content}")
            continue

        # Locale-specific legacy page, e.g. forum/ar/ai/slug/index.html.
        candidates.add(FORUM / locale / category / slug / "index.html")
        # Pre-bilingual legacy page, e.g. forum/ai/slug/index.html.
        candidates.add(FORUM / category / slug / "index.html")

    return sorted(candidates), errors


def remove_empty_parents(path: Path) -> None:
    current = path.parent
    # Never remove category roots or anything above forum/<locale>/<category>.
    while current != FORUM and current.parent != FORUM:
        try:
            current.rmdir()
        except OSError:
            break
        current = current.parent


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Remove or detect legacy per-article HTML already covered by structured JSON + dynamic SSR."
    )
    parser.add_argument("--apply", action="store_true", help="Actually delete covered legacy HTML files.")
    parser.add_argument(
        "--check-clean",
        action="store_true",
        help="Fail if any covered legacy article HTML exists; intended for CI regression protection.",
    )
    args = parser.parse_args()

    if args.apply and args.check_clean:
        parser.error("--apply and --check-clean are mutually exclusive")

    routes = load_map()
    candidates, errors = candidate_indexes(routes)
    existing = [path for path in candidates if path.is_file()]

    protected = FORUM / "announcements" / "rdwan-tech-launch" / "index.html"
    if protected in existing:
        errors.append("Protected legacy launch page unexpectedly matched cleanup candidates")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    removed = 0
    if args.apply:
        for path in existing:
            path.unlink()
            remove_empty_parents(path)
            removed += 1

    remaining = [path for path in candidates if path.is_file()]
    mode = "apply" if args.apply else ("check-clean" if args.check_clean else "dry-run")
    print(
        "Mikhbar legacy article HTML cleanup: "
        f"mode={mode} dynamic_routes={len(routes)} candidate_paths={len(candidates)} "
        f"existing_before={len(existing)} removed={removed} remaining={len(remaining)}"
    )

    if args.apply and remaining:
        for path in remaining[:20]:
            print(f"ERROR: legacy article HTML remained: {path.relative_to(ROOT)}", file=sys.stderr)
        return 1

    if args.check_clean and existing:
        for path in existing[:20]:
            print(f"ERROR: covered legacy article HTML reappeared: {path.relative_to(ROOT)}", file=sys.stderr)
        if len(existing) > 20:
            print(f"ERROR: {len(existing) - 20} additional covered legacy HTML files omitted", file=sys.stderr)
        return 1

    if not protected.exists():
        print(
            "WARNING: protected legacy launch page is not present; cleanup did not remove it because it is outside the dynamic map.",
            file=sys.stderr,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
