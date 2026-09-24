import { isArticlePath, renderDynamicArticle } from "./article.js";

const CANONICAL_HOST = "mikhbar.website";
const ARTICLE_PARTS = /^\/(ar|en)\/([a-z0-9-]+)\/([^/]+)\/$/i;

const RELATED_HUBS = {
  ai: ["automation", "apps", "robotics", "security"],
  security: ["web", "apps", "computers", "ai"],
  automation: ["ai", "apps", "web", "robotics"],
  robotics: ["ai", "automation", "computers", "security"],
  apps: ["mobile", "ai", "web", "security"],
  web: ["security", "apps", "automation", "ai"],
  mobile: ["apps", "computers", "security", "ai"],
  computers: ["security", "apps", "ai", "web"],
  social: ["apps", "web", "security", "ai"],
};

const HUB_LABELS = {
  ar: {
    ai: "الذكاء الاصطناعي",
    security: "الأمن السيبراني",
    automation: "الأتمتة",
    robotics: "الروبوتات",
    apps: "التطبيقات والبرامج",
    web: "الويب",
    mobile: "الهواتف",
    computers: "الحواسيب",
    social: "التواصل الاجتماعي",
  },
  en: {
    ai: "Artificial Intelligence",
    security: "Cybersecurity",
    automation: "Automation",
    robotics: "Robotics",
    apps: "Apps & Software",
    web: "Web Technology",
    mobile: "Mobile",
    computers: "Computing",
    social: "Social Media",
  },
};

function canonicalUrl(url) {
  const next = new URL(url.toString());
  next.protocol = "https:";
  next.hostname = CANONICAL_HOST;
  next.port = "";
  return next;
}

function publicPath(value) {
  let path = String(value || "/").trim();
  if (path.startsWith("/forum/")) path = path.slice("/forum".length);
  if (!path.startsWith("/")) path = "/" + path;
  return path;
}

function esc(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

async function assetJson(env, request, path) {
  const url = new URL(path, request.url);
  const response = await env.ASSETS.fetch(new Request(url, request));
  if (!response.ok) return null;
  try { return await response.json(); } catch { return null; }
}

export function selectRelatedPosts(posts, pathname, limit = 4) {
  const match = String(pathname || "").match(ARTICLE_PARTS);
  if (!match || !Array.isArray(posts)) return [];
  const [, locale, category] = match;
  const current = publicPath(pathname);

  return posts
    .filter((post) => {
      if (String(post?.locale || locale).toLowerCase() !== locale.toLowerCase()) return false;
      if (String(post?.categorySlug || "") !== category) return false;
      const url = publicPath(post?.url || "");
      return url && url !== current;
    })
    .sort((a, b) => {
      const aTime = Date.parse(String(a?.dateModified || a?.date || "")) || 0;
      const bTime = Date.parse(String(b?.dateModified || b?.date || "")) || 0;
      return bTime - aTime;
    })
    .slice(0, Math.max(0, limit));
}

function topicHubHtml(locale, category) {
  const lang = locale.toLowerCase();
  const labels = HUB_LABELS[lang] || HUB_LABELS.en;
  const hubs = RELATED_HUBS[category] || [];
  if (!hubs.length) return "";

  const isAr = lang === "ar";
  const title = isAr ? "مواضيع مرتبطة" : "Related topics";
  const note = isAr ? "استكشف التغطية المتخصصة" : "Explore specialist coverage";
  const cards = hubs.map((slug) => {
    const label = labels[slug] || slug;
    return `<a class="rt-topic-card" href="/${esc(lang)}/${esc(slug)}/"><b>${esc(label)}</b><span>${esc(note)}</span></a>`;
  }).join("");

  return `<section class="rt-section rt-related-topics" aria-labelledby="related-topics-title"><header class="rt-section-head"><div><h2 id="related-topics-title">${esc(title)}</h2></div></header><div class="rt-topic-grid">${cards}</div></section>`;
}

function relatedHtml(posts, pathname) {
  const match = String(pathname || "").match(ARTICLE_PARTS);
  if (!match) return "";
  const [, locale, category] = match;
  const isAr = locale.toLowerCase() === "ar";
  const title = isAr ? "أخبار مرتبطة" : "Related stories";
  const more = isAr ? "المزيد من هذا القسم" : "More from this section";
  const categoryUrl = `/${locale}/${category}/`;
  const topicHubs = topicHubHtml(locale, category);

  const cards = posts.map((post) => {
    const href = publicPath(post?.url || "");
    const postTitle = String(post?.title || "").trim();
    const excerpt = String(post?.excerpt || "").trim();
    const date = String(post?.dateLabel || "").trim();
    if (!href || !postTitle) return "";
    return `<a class="rt-feed-item" href="${esc(href)}"><div class="rt-feed-copy"><h3>${esc(postTitle)}</h3>${excerpt ? `<p>${esc(excerpt)}</p>` : ""}${date ? `<div class="rt-feed-time">${esc(date)}</div>` : ""}</div></a>`;
  }).filter(Boolean).join("");

  const stories = cards
    ? `<section class="rt-section rt-related-stories" aria-labelledby="related-stories-title"><header class="rt-section-head"><div><h2 id="related-stories-title">${esc(title)}</h2></div><a href="${esc(categoryUrl)}">${esc(more)}</a></header><div class="rt-feed">${cards}</div></section>`
    : "";

  return stories + topicHubs;
}

class AppendHtmlHandler {
  constructor(html) { this.html = html; }
  element(element) { element.append(this.html, { html: true }); }
}

async function addRelatedStories(response, request, env, pathname) {
  const match = String(pathname || "").match(ARTICLE_PARTS);
  if (!match || !response?.ok) return response;
  const locale = match[1].toLowerCase();
  const payload = await assetJson(env, request, `/posts-${locale}.json`);
  const posts = Array.isArray(payload) ? payload : (Array.isArray(payload?.posts) ? payload.posts : []);
  const related = selectRelatedPosts(posts, pathname, 4);
  const html = relatedHtml(related, pathname);
  if (!html) return response;
  return new HTMLRewriter()
    .on("#article-body", new AppendHtmlHandler(html))
    .transform(response);
}

function withHeaders(response) {
  const headers = new Headers(response.headers);
  headers.set("X-Content-Type-Options", "nosniff");
  headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
  headers.set("Permissions-Policy", "camera=(), microphone=(), geolocation=()");
  headers.set("X-Frame-Options", "SAMEORIGIN");
  headers.set("Strict-Transport-Security", "max-age=31536000; includeSubDomains; preload");

  const type = (headers.get("content-type") || "").toLowerCase();
  if (type.includes("text/html") || type.includes("xml") || type.includes("json")) {
    headers.set("Cache-Control", "public, max-age=60, s-maxage=300, stale-while-revalidate=86400");
  } else if (type.includes("image/") || type.includes("text/css") || type.includes("javascript") || type.includes("font/")) {
    headers.set("Cache-Control", "public, max-age=86400, s-maxage=604800, immutable");
  }

  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers,
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.hostname === `www.${CANONICAL_HOST}` || url.protocol === "http:") {
      return Response.redirect(canonicalUrl(url).toString(), 308);
    }

    if (url.pathname === "/healthz") {
      return Response.json({
        ok: true,
        service: "mikhbar",
        canonicalHost: CANONICAL_HOST,
        articleMode: "single-template-ssr",
        now: new Date().toISOString(),
      }, {
        headers: { "Cache-Control": "no-store" },
      });
    }

    if (url.pathname === "/forum" || url.pathname.startsWith("/forum/")) {
      const canonical = canonicalUrl(url);
      canonical.pathname = url.pathname === "/forum" ? "/" : url.pathname.slice("/forum".length) || "/";
      return Response.redirect(canonical.toString(), 308);
    }

    if (isArticlePath(url.pathname) && !url.pathname.endsWith("/")) {
      const canonical = canonicalUrl(url);
      canonical.pathname = url.pathname + "/";
      return Response.redirect(canonical.toString(), 308);
    }

    if (isArticlePath(url.pathname)) {
      const article = await renderDynamicArticle(request, env, url.pathname);
      if (article) {
        const enriched = await addRelatedStories(article, request, env, url.pathname);
        return withHeaders(enriched);
      }
    }

    let response = await env.ASSETS.fetch(request);
    if (response.status === 404) {
      const fallbackUrl = new URL("/404.html", request.url);
      const fallback = await env.ASSETS.fetch(new Request(fallbackUrl, request));
      if (fallback.ok) {
        response = new Response(fallback.body, {
          status: 404,
          headers: fallback.headers,
        });
      }
    }

    return withHeaders(response);
  },
};
