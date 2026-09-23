# Mikhbar SEO deployment checklist

Canonical production origin: **https://mikhbar.website/**

## Search and discovery
- Arabic: `https://mikhbar.website/ar/`
- English: `https://mikhbar.website/en/`
- Sitemap: `https://mikhbar.website/sitemap.xml`
- News sitemap: `https://mikhbar.website/news-sitemap.xml`
- RSS Arabic: `https://mikhbar.website/feed-ar.xml`
- RSS English: `https://mikhbar.website/feed-en.xml`
- LLM discovery: `https://mikhbar.website/llms.txt`

## Canonical rules
All new article canonical URLs, Open Graph URLs, schema identifiers, feeds and sitemaps must use `https://mikhbar.website` as the public origin. Legacy `https://rdwan.dev/forum/...` links will be handled separately as migration redirects.

## Hosting
Production hosting is Cloudflare Workers + Static Assets. GitHub remains the source of truth for article generation and automation.
