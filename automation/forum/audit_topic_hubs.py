from __future__ import annotations

import sys
from pathlib import Path

from enhance_category_seo import FORUM, HUB_CONFIG


def main() -> int:
    errors: list[str] = []
    checked = 0

    for slug, locales in HUB_CONFIG.items():
        for locale, config in locales.items():
            path = FORUM / locale / slug / "index.html"
            label = f"{locale}/{slug}"
            if not path.exists():
                errors.append(f"{label}: missing category hub page")
                continue

            html = path.read_text(encoding="utf-8")
            checked += 1

            expected = {
                "title": f"<title>{config['title']}</title>",
                "description": f'<meta name="description" content="{config["description"]}">',
                "topic marker": f'data-topic-hub="{slug}"',
                "topic heading": f'id="{slug}-topic-guide"',
            }
            for name, needle in expected.items():
                if needle not in html:
                    errors.append(f"{label}: missing {name}")

            for target, _link_label in config["links"]:
                if f'href="../{target}/"' not in html:
                    errors.append(f"{label}: missing related hub link ../{target}/")

            if "rdwan.dev" in html:
                errors.append(f"{label}: legacy rdwan.dev identity remains")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Mikhbar topic hub audit failed: checked={checked} errors={len(errors)}", file=sys.stderr)
        return 1

    print(f"Mikhbar topic hub audit: checked={checked} errors=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
