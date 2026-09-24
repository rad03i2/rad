from __future__ import annotations

import sys
from html import escape

from generate_pillar_pages import FORUM, ORIGIN, PILLARS


def main() -> int:
    errors: list[str] = []
    checked = 0

    for locale in ("ar", "en"):
        index_path = FORUM / locale / "guides" / "index.html"
        if not index_path.exists():
            errors.append(f"{locale}/guides: missing guides index")
        else:
            html = index_path.read_text(encoding="utf-8")
            checked += 1
            if 'data-guide-index="true"' not in html:
                errors.append(f"{locale}/guides: missing guide index marker")
            if f'<link rel="canonical" href="{ORIGIN}/{locale}/guides/">' not in html:
                errors.append(f"{locale}/guides: missing canonical")
            for slug in PILLARS:
                if f'href="/{locale}/guides/{slug}/"' not in html:
                    errors.append(f"{locale}/guides: missing link to {slug}")
            if "rdwan.dev" in html or "radwan-abdulhadi" in html or "Radwan Abdulhadi" in html or "رضوان عبدالهادي" in html:
                errors.append(f"{locale}/guides: personal SEO identity leaked into Mikhbar guide index")

        for slug, spec in PILLARS.items():
            config = spec[locale]
            path = FORUM / locale / "guides" / slug / "index.html"
            label = f"{locale}/guides/{slug}"
            if not path.exists():
                errors.append(f"{label}: missing pillar page")
                continue
            html = path.read_text(encoding="utf-8")
            checked += 1
            expected = {
                "title": f"<title>{escape(config['title'])}</title>",
                "description": f'<meta name="description" content="{escape(config["description"], quote=True)}">',
                "canonical": f'<link rel="canonical" href="{ORIGIN}/{locale}/guides/{slug}/">',
                "pillar marker": f'data-pillar-guide="{slug}"',
                "organization author": '"author":{"@type":"Organization","name":"Mikhbar Editorial"',
                "publisher": '"@id":"https://mikhbar.website/#publisher"',
                "category link": f'href="/{locale}/{spec["category"]}/"',
            }
            for name, needle in expected.items():
                if needle not in html:
                    errors.append(f"{label}: missing {name}")
            if html.count("<h2>") < 4:
                errors.append(f"{label}: guide body is too thin")
            for target in spec["related"]:
                if f'href="/{locale}/guides/{target}/"' not in html:
                    errors.append(f"{label}: missing related guide {target}")
            if "rdwan.dev" in html or "radwan-abdulhadi" in html or "Radwan Abdulhadi" in html or "رضوان عبدالهادي" in html:
                errors.append(f"{label}: personal SEO identity leaked into Mikhbar pillar")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Mikhbar pillar audit failed: checked={checked} errors={len(errors)}", file=sys.stderr)
        return 1

    print(f"Mikhbar pillar audit: checked={checked} errors=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
