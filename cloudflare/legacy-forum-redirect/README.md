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

## Deployment safety

Production routing is deliberately scoped only to `rdwan.dev/forum*` and `www.rdwan.dev/forum*`. The Worker must never be attached to `rdwan.dev/*` generally. The deployment workflow verifies that the personal homepage remains outside the Mikhbar migration route.

## SEO purpose

Search engines still have historical Mikhbar URLs under `rdwan.dev/forum/...`. A permanent path-preserving redirect is the clean migration signal that lets crawlers consolidate those old URLs toward the standalone `mikhbar.website` publication without making the two sites one SEO entity going forward.
