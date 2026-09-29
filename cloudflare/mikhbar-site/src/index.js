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

function preferredEdition(request) {
  const header = String(request.headers.get("Accept-Language") || "");
  const languages = header
    .split(",")
    .map((entry, index) => {
      const parts = entry.trim().split(";");
      const tag = String(parts.shift() || "").trim().toLowerCase();
      let q = 1;
      for (const param of parts) {
        const match = param.trim().match(/^q=([0-9.]+)$/i);
        if (match) {
          const parsed = Number.parseFloat(match[1]);
          q = Number.isFinite(parsed) ? parsed : 0;
        }
      }
      return { tag, q, index };
    })
    .filter((item) => item.tag && item.q > 0)
    .sort((a, b) => (b.q - a.q) || (a.index - b.index));

  const language = languages[0]?.tag || "";
  return language === "ar" || language.startsWith("ar-") ? "ar" : "en";
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

export function selectChronologicalNeighbors(posts, pathname) {
  const match = String(pathname || "").match(ARTICLE_PARTS);
  if (!match || !Array.isArray(posts)) return { newer: null, older: null };
  const [, locale, category] = match;
  const current = publicPath(pathname);
  const ordered = posts
    .filter((post) => {
      if (String(post?.locale || locale).toLowerCase() !== locale.toLowerCase()) return false;
      if (String(post?.categorySlug || "") !== category) return false;
      return Boolean(publicPath(post?.url || ""));
    })
    .sort((a, b) => {
      const aTime = Date.parse(String(a?.dateModified || a?.date || "")) || 0;
      const bTime = Date.parse(String(b?.dateModified || b?.date || "")) || 0;
      return bTime - aTime;
    });

  const index = ordered.findIndex((post) => publicPath(post?.url || "") === current);
  if (index < 0) return { newer: null, older: null };
  return {
    newer: index > 0 ? ordered[index - 1] : null,
    older: index + 1 < ordered.length ? ordered[index + 1] : null,
  };
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

function chronologicalHtml(neighbors, pathname) {
  const match = String(pathname || "").match(ARTICLE_PARTS);
  if (!match) return "";
  const [, locale] = match;
  const isAr = locale.toLowerCase() === "ar";
  const title = isAr ? "تابع التسلسل الزمني" : "Continue chronologically";
  const newerLabel = isAr ? "الخبر الأحدث" : "Newer story";
  const olderLabel = isAr ? "الخبر الأقدم" : "Older story";
  const cards = [];

  for (const [kind, post] of [["newer", neighbors?.newer], ["older", neighbors?.older]]) {
    const href = publicPath(post?.url || "");
    const postTitle = String(post?.title || "").trim();
    if (!href || !postTitle) continue;
    const label = kind === "newer" ? newerLabel : olderLabel;
    cards.push(`<a class="rt-topic-card" data-chronology="${esc(kind)}" href="${esc(href)}"><span>${esc(label)}</span><b>${esc(postTitle)}</b></a>`);
  }

  if (!cards.length) return "";
  return `<section class="rt-section rt-article-chronology" aria-labelledby="article-chronology-title"><header class="rt-section-head"><div><h2 id="article-chronology-title">${esc(title)}</h2></div></header><div class="rt-topic-grid">${cards.join("")}</div></section>`;
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
  const chronology = selectChronologicalNeighbors(posts, pathname);
  const html = chronologicalHtml(chronology, pathname) + relatedHtml(related, pathname);
  if (!html) return response;
  return new HTMLRewriter()
    .on("#article-body", new AppendHtmlHandler(html))
    .transform(response);
}

function shouldNoIndexTechnicalPath(pathname) {
  const path = String(pathname || "").toLowerCase();
  return path === "/healthz"
    || path.endsWith(".json")
    || /^\/feed(?:-(?:ar|en))?\.xml$/.test(path)
    || /^\/[a-f0-9]{32}\.txt$/.test(path);
}

function withHeaders(response, pathname = "") {
  const headers = new Headers(response.headers);
  headers.set("X-Content-Type-Options", "nosniff");
  headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
  headers.set("Permissions-Policy", "camera=(), microphone=(), geolocation=()");
  headers.set("X-Frame-Options", "SAMEORIGIN");
  headers.set("Strict-Transport-Security", "max-age=31536000; includeSubDomains; preload");

  if (shouldNoIndexTechnicalPath(pathname) || response.status >= 400) {
    headers.set("X-Robots-Tag", "noindex, follow");
  }

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

    if (url.pathname === "/") {
      const edition = preferredEdition(request);
      const target = canonicalUrl(url);
      target.pathname = `/${edition}/`;
      return withHeaders(new Response(null, {
        status: 302,
        headers: {
          "Location": target.toString(),
          "Cache-Control": "private, no-store",
          "Vary": "Accept-Language",
        },
      }), url.pathname);
    }

    if (url.pathname === "/healthz") {
      return withHeaders(Response.json({
        ok: true,
        service: "mikhbar",
        canonicalHost: CANONICAL_HOST,
        articleMode: "single-template-ssr",
        now: new Date().toISOString(),
      }, {
        headers: { "Cache-Control": "no-store" },
      }), url.pathname);
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
        return withHeaders(enriched, url.pathname);
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

    return withHeaders(response, url.pathname);
  },
};
