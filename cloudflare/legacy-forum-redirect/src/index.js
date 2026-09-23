const TARGET_ORIGIN = "https://mikhbar.website";

export default {
  async fetch(request) {
    const source = new URL(request.url);

    // This Worker is intentionally scoped for a future rdwan.dev/forum* route.
    // It must never be attached to the rest of the personal site.
    if (source.pathname !== "/forum" && !source.pathname.startsWith("/forum/")) {
      return new Response("Not Found", {
        status: 404,
        headers: { "Cache-Control": "no-store" },
      });
    }

    const target = new URL(TARGET_ORIGIN);
    target.pathname = source.pathname === "/forum"
      ? "/"
      : source.pathname.slice("/forum".length) || "/";
    target.search = source.search;
    target.hash = source.hash;

    return Response.redirect(target.toString(), 308);
  },
};
