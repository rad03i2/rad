from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORUM = ROOT / "forum"
ORIGIN = "https://mikhbar.website"
UPDATED = "2026-09-24"
PILLAR_SLUGS = ("artificial-intelligence", "cybersecurity", "robotics")


def _alternate_links(path: str) -> str:
    return (
        f'<xhtml:link rel="alternate" hreflang="ar" href="{ORIGIN}/ar/{path}"/>'
        f'<xhtml:link rel="alternate" hreflang="en" href="{ORIGIN}/en/{path}"/>'
        f'<xhtml:link rel="alternate" hreflang="x-default" href="{ORIGIN}/en/{path}"/>'
    )


def integrate_sitemap() -> int:
    path = FORUM / "sitemap.xml"
    if not path.exists():
        raise SystemExit("forum/sitemap.xml is missing before pillar discovery integration")
    text = path.read_text(encoding="utf-8")
    if "</urlset>" not in text:
        raise SystemExit("forum/sitemap.xml does not contain a closing urlset")

    rows: list[str] = []
    for locale in ("ar", "en"):
        loc = f"{ORIGIN}/{locale}/guides/"
        if f"<loc>{loc}</loc>" not in text:
            rows.append(
                f'  <url><loc>{loc}</loc><lastmod>{UPDATED}</lastmod><changefreq>weekly</changefreq><priority>0.85</priority>'
                f'{_alternate_links("guides/")}</url>'
            )
        for slug in PILLAR_SLUGS:
            loc = f"{ORIGIN}/{locale}/guides/{slug}/"
            if f"<loc>{loc}</loc>" in text:
                continue
            rows.append(
                f'  <url><loc>{loc}</loc><lastmod>{UPDATED}</lastmod><changefreq>weekly</changefreq><priority>0.90</priority>'
                f'{_alternate_links(f"guides/{slug}/")}</url>'
            )

    if rows:
        text = text.replace("</urlset>", "\n".join(rows) + "\n</urlset>", 1)
        path.write_text(text, encoding="utf-8")
    return len(rows)


def integrate_llms() -> int:
    path = FORUM / "llms.txt"
    if not path.exists():
        raise SystemExit("forum/llms.txt is missing before pillar discovery integration")
    text = path.read_text(encoding="utf-8")
    marker = "## Evergreen technology guides"
    if marker in text:
        return 0
    block = [
        "",
        marker,
        f"- Arabic guides: {ORIGIN}/ar/guides/",
        f"- English guides: {ORIGIN}/en/guides/",
        f"- Artificial intelligence guide (AR): {ORIGIN}/ar/guides/artificial-intelligence/",
        f"- Artificial intelligence guide (EN): {ORIGIN}/en/guides/artificial-intelligence/",
        f"- Cybersecurity guide (AR): {ORIGIN}/ar/guides/cybersecurity/",
        f"- Cybersecurity guide (EN): {ORIGIN}/en/guides/cybersecurity/",
        f"- Robotics guide (AR): {ORIGIN}/ar/guides/robotics/",
        f"- Robotics guide (EN): {ORIGIN}/en/guides/robotics/",
    ]
    path.write_text(text.rstrip() + "\n" + "\n".join(block) + "\n", encoding="utf-8")
    return 1


def integrate_pillar_discovery() -> tuple[int, int]:
    sitemap_rows = integrate_sitemap()
    llms_sections = integrate_llms()
    return sitemap_rows, llms_sections


if __name__ == "__main__":
    sitemap_rows, llms_sections = integrate_pillar_discovery()
    print(f"Mikhbar pillar discovery integrated: sitemap_rows={sitemap_rows} llms_sections={llms_sections}")
