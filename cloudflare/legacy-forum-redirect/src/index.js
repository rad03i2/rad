const TARGET_ORIGIN = "https://mikhbar.website";

export function legacyForumTarget(input) {
  const source = input instanceof URL ? input : new URL(input);

  // Only the former Mikhbar publication path is migrated. A broad Cloudflare
  // route is used so query strings are also matched, but lookalike personal
  // paths such as /forumanything must fall through to the original site.
  if (source.pathname !== "/forum" && !source.pathname.startsWith("/forum/")) {
    return null;
  }

  const target = new URL(TARGET_ORIGIN);
  target.pathname = source.pathname === "/forum"
    ? "/"
    : source.pathname.slice("/forum".length) || "/";
  target.search = source.search;
  return target.toString();
}

export default {
  async fetch(request) {
    const target = legacyForumTarget(request.url);

    if (!target) {
      // Preserve every non-publication path on rdwan.dev exactly as-is.
      return fetch(request);
    }

    return new Response(null, {
      status: 308,
      headers: {
        Location: target,
        "Cache-Control": "public, max-age=86400",
        "X-Mikhbar-Migration": "legacy-forum",
      },
    });
  },
};
