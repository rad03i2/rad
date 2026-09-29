# Mikhbar legacy `/forum` redirect

This Worker is a migration-only component for the old Mikhbar URLs that were historically published under `rdwan.dev/forum/...`.

## Scope

It is intentionally limited to the old publication path only:

- `https://rdwan.dev/forum` → `https://mikhbar.website/ar/`
- `https://rdwan.dev/forum/` → `https://mikhbar.website/ar/`
- `https://rdwan.dev/forum/ar/...` → `https://mikhbar.website/ar/...`
- `https://rdwan.dev/forum/en/...` → `https://mikhbar.website/en/...`
- `https://rdwan.dev/forum/about/` → `https://mikhbar.website/about/`
- the same migration applies to `https://www.rdwan.dev/forum...`
- query strings are preserved
- status: **308 Permanent Redirect**

It must **not** be attached to `rdwan.dev/*` generally and must not change the personal site's homepage, portfolio, assets or other routes.

## Deployment status

`rdwan.dev` is currently served by **Appwrite Sites**, not by the Cloudflare zone used for `mikhbar.website`. Therefore this Worker is retained as a tested migration reference only and is not auto-deployed.

The live migration layer is source-controlled in `rad03i2/rad2`: legacy `/forum` landing pages carry cross-domain canonicals and immediate migration navigation toward `mikhbar.website`, while the personal site's remaining paths stay independent.

## SEO purpose

Search engines still have historical Mikhbar URLs under `rdwan.dev/forum/...`. A permanent path-preserving redirect is the clean migration signal that lets crawlers consolidate those old URLs toward the standalone `mikhbar.website` publication without making the two sites one SEO entity going forward.
