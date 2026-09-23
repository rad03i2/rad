from __future__ import annotations

import publisher
import publisher_scheduler
from common import CONFIG, load_json


def _data_only_render(_record: dict) -> dict:
    """Keep article delivery data-only during scheduled publication.

    The structured JSON record, indexes, feeds and hub pages are still updated,
    but no per-article HTML files are created. Existing legacy HTML files remain
    untouched until the dynamic template phase is complete.
    """
    return {}


def main() -> int:
    settings = load_json(CONFIG / "settings.json", {})
    mode = str(settings.get("articleDeliveryMode") or "static-html").strip().lower()

    if mode != "data-only":
        print(f"Mikhbar publication mode: {mode}; using legacy static article rendering.")
        return publisher_scheduler.main()

    original_render = publisher.render_to_files
    publisher.render_to_files = _data_only_render
    try:
        print("Mikhbar publication mode: data-only; per-article HTML generation is disabled.")
        return publisher_scheduler.main()
    finally:
        publisher.render_to_files = original_render


if __name__ == "__main__":
    raise SystemExit(main())
