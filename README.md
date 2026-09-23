# Mikhbar — مِخبار

Bilingual technology publication and automated publishing system.

مِخبار هو مشروع نشر تقني عربي/إنجليزي مستقل، مع أتمتة لجمع الأخبار والتحقق منها وتجهيز المقالات ونشرها دوريًا.

## Production

- Canonical domain: https://mikhbar.website/
- Arabic edition: https://mikhbar.website/ar/
- English edition: https://mikhbar.website/en/
- Repository: rad03i2/rad
- Production branch: main
- Hosting target: Cloudflare Workers + Static Assets

## Repository layout

- `forum/` — generated publication, feeds, sitemaps and article pages
- `automation/forum/` — collection, verification, writing, scheduling and rendering
- `automation/social/` — isolated social publishing state and tooling
- `.github/workflows/` — publisher, watchdog, CI, IndexNow and social workflows
- `assets/brand/mikhbar/` — Mikhbar brand assets
- `cloudflare/mikhbar-site/` — Cloudflare Worker/Static Assets deployment layer

The personal portfolio has been separated into `rad03i2/rad2` and is not part of this repository.
