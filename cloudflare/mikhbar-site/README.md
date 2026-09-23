# Mikhbar on Cloudflare Workers

This directory is the hosting layer for **mikhbar.website**.

## Architecture

- Source publication: `forum/`
- Build command: `python cloudflare/mikhbar-site/build.py`
- Build output: `dist/mikhbar/`
- Runtime: Cloudflare Worker + Static Assets
- Preview config: `wrangler.preview.toml`
- Production config: `wrangler.production.toml`

The build keeps the GitHub publishing engine unchanged while transforming the deployable copy from legacy `https://rdwan.dev/forum/...` URLs to `https://mikhbar.website/...` URLs. It also copies the assets required by Mikhbar and creates `robots.txt`, a 404 page and the IndexNow key file.

## Deploy

Preview:

```bash
python build.py
npx wrangler@latest deploy --config wrangler.preview.toml
```

Production after `mikhbar.website` is an active Cloudflare zone:

```bash
python build.py
npx wrangler@latest deploy --config wrangler.production.toml
```

GitHub Actions uses the repository secrets `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` when they are available.
