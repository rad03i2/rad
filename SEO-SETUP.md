# SEO deployment checklist

The technical SEO layer targets the expected GitHub Pages URL: `https://rad03i2.github.io/rad/`.

## One-time publishing step
1. Repository **Settings → Pages**.
2. Under **Build and deployment**, set Source to **GitHub Actions**.
3. Run the **Deploy GitHub Pages** workflow.

## Search engines
- Verify `https://rad03i2.github.io/rad/` in Google Search Console, then submit `https://rad03i2.github.io/rad/sitemap.xml`.
- Verify/import the site in Bing Webmaster Tools. IndexNow is already configured in `.github/workflows/indexnow.yml`; it starts submitting automatically once the public URL responds successfully.

## Important
IndexNow and sitemap submission speed up discovery, but no search engine guarantees immediate crawling, indexing, or first-place rankings.
