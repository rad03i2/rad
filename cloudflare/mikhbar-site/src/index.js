import { isArticlePath, renderDynamicArticle } from "./article.js";

const CANONICAL_HOST = "mikhbar.website";
const ARTICLE_PARTS = /^\/(ar|en)\/(?!(?:entities)(?:\/|$))([a-z0-9-]+)\/(?!archive(?:\/|$))([^/]+)\/$/i;

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

const GENERIC_SEMANTIC_TERMS = new Set([
  "ai", "artificial intelligence", "technology", "tech", "software", "apps", "app",
  "security", "cybersecurity", "mobile", "web", "computing", "computer", "robotics",
  "automation", "news", "update", "updates", "platform", "model", "models",
  "الذكاء الاصطناعي", "تقنية", "التقنية", "برمجيات", "تطبيقات", "تطبيق",
  "الأمن السيبراني", "امن سيبراني", "الهواتف", "الويب", "الحواسيب", "الروبوتات",
  "الأتمتة", "اخبار", "أخبار", "تحديث", "تحديثات", "منصة", "نموذج", "نماذج",
]);

const TITLE_STOP_WORDS = new Set([
  "with", "from", "into", "over", "after", "before", "that", "this", "their", "about",
  "using", "launches", "launch", "new", "adds", "gets", "more", "will", "your",
  "على", "إلى", "الى", "عن", "من", "في", "مع", "بعد", "قبل", "هذا", "هذه", "التي",
  "الذي", "جديد", "جديدة", "عبر", "لدى", "بين", "حول",
]);

function normalizeSemanticTerm(value) {
  return String(value ?? "")
    .normalize("NFKD")
    .toLowerCase()
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[\u064B-\u065F\u0670\u0640]/g, "")
    .replace(/[أإآٱ]/g, "ا")
    .replace(/ى/g, "ي")
    .replace(/ؤ/g, "و")
    .replace(/ئ/g, "ي")
    .replace(/[^\p{L}\p{N}+#. -]+/gu, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function semanticSet(values) {
  const output = new Set();
  for (const value of Array.isArray(values) ? values : []) {
    const term = normalizeSemanticTerm(value);
    if (!term || term.length < 2 || GENERIC_SEMANTIC_TERMS.has(term)) continue;
    output.add(term);
  }
  return output;
}

function titleTokens(value) {
  const normalized = normalizeSemanticTerm(value);
  const output = new Set();
  for (const token of normalized.split(/\s+/)) {
    if (!token || token.length < 4 || TITLE_STOP_WORDS.has(token) || GENERIC_SEMANTIC_TERMS.has(token)) continue;
    output.add(token);
  }
  return output;
}

function intersectionCount(a, b, excluded = new Set()) {
  let count = 0;
  for (const item of a) {
    if (!excluded.has(item) && b.has(item)) count += 1;
  }
  return count;
}

export function semanticRelatedScore(currentPost, candidatePost) {
  if (!currentPost || !candidatePost) return { score: 0, signals: 0 };

  const currentEntities = semanticSet(currentPost.entities);
  const candidateEntities = semanticSet(candidatePost.entities);
  const currentTags = semanticSet(currentPost.tags);
  const candidateTags = semanticSet(candidatePost.tags);

  const entityMatches = intersectionCount(currentEntities, candidateEntities);
  const entityTagMatches = (
    intersectionCount(currentEntities, candidateTags)
    + intersectionCount(currentTags, candidateEntities)
  );
  const entityTerms = new Set([...currentEntities, ...candidateEntities]);
  const tagMatches = intersectionCount(currentTags, candidateTags, entityTerms);

  const currentTitle = titleTokens(currentPost.title);
  const candidateTitle = titleTokens(candidatePost.title);
  const titleMatches = Math.min(4, intersectionCount(currentTitle, candidateTitle));

  const sameCategory = String(currentPost.categorySlug || "") === String(candidatePost.categorySlug || "");
  const signals = entityMatches + entityTagMatches + tagMatches + titleMatches;
  let score = (
    entityMatches * 12
    + entityTagMatches * 7
    + tagMatches * 5
    + titleMatches * 1.5
    + (sameCategory ? 1.5 : 0)
  );

  // Crossing topic hubs should require a meaningful semantic relationship,
  // not a single generic keyword or recency coincidence.
  if (!sameCategory && entityMatches === 0 && entityTagMatches === 0 && tagMatches < 2 && titleMatches < 2) {
    score = 0;
  }
  if (sameCategory && signals === 0) score = 0;

  return { score, signals, sameCategory };
}

function newestFirst(a, b) {
  const aTime = Date.parse(String(a?.dateModified || a?.date || "")) || 0;
  const bTime = Date.parse(String(b?.dateModified || b?.date || "")) || 0;
  return bTime - aTime;
}

export function selectRelatedPosts(posts, pathname, limit = 4) {
  const match = String(pathname || "").match(ARTICLE_PARTS);
  if (!match || !Array.isArray(posts)) return [];
  const [, locale, category] = match;
  const current = publicPath(pathname);
  const wanted = Math.max(0, limit);
  if (!wanted) return [];

  const currentPost = posts.find((post) => publicPath(post?.url || "") === current);
  const candidates = posts.filter((post) => {
    if (String(post?.locale || locale).toLowerCase() !== locale.toLowerCase()) return false;
    const url = publicPath(post?.url || "");
    return url && url !== current;
  });

  // If an older/index-only article lacks semantic metadata, preserve the safe
  // chronological same-section fallback instead of inventing weak relevance.
  if (!currentPost) {
    return candidates
      .filter((post) => String(post?.categorySlug || "") === category)
      .sort(newestFirst)
      .slice(0, wanted);
  }

  const ranked = candidates
    .map((post) => {
      const semantic = semanticRelatedScore(currentPost, post);
      return { post, ...semantic };
    })
    .filter((item) => item.score > 0)
    .sort((a, b) => (
      b.score - a.score
      || Number(b.sameCategory) - Number(a.sameCategory)
      || newestFirst(a.post, b.post)
    ));

  const selected = ranked.slice(0, wanted).map((item) => ({
    ...item.post,
    _semanticScore: item.score,
    _semanticSignals: item.signals,
  }));
  const used = new Set(selected.map((post) => publicPath(post?.url || "")));

  if (selected.length < wanted) {
    const fallback = candidates
      .filter((post) => String(post?.categorySlug || "") === category)
      .filter((post) => !used.has(publicPath(post?.url || "")))
      .sort(newestFirst);
    for (const post of fallback) {
      selected.push({ ...post, _semanticScore: 0, _semanticSignals: 0 });
      if (selected.length >= wanted) break;
    }
  }

  return selected.slice(0, wanted);
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

function entityHubHtml(post, locale) {
  const hubs = Array.isArray(post?.entityHubs) ? post.entityHubs.slice(0, 4) : [];
  if (!hubs.length) return "";
  const isAr = String(locale || "").toLowerCase() === "ar";
  const title = isAr ? "تغطية الكيانات المرتبطة" : "Related entity coverage";
  const note = isAr ? "كل أخبار الكيان" : "All entity coverage";
  const cards = hubs.map((hub) => {
    const href = publicPath(hub?.url || "");
    const name = String(hub?.name || "").trim();
    if (!href || !name) return "";
    return `<a class="rt-topic-card" data-article-entity-hub="true" href="${esc(href)}"><b>${esc(name)}</b><span>${esc(note)}</span></a>`;
  }).filter(Boolean).join("");
  if (!cards) return "";
  return `<section class="rt-section rt-article-entity-hubs" data-article-entity-hubs="true" aria-labelledby="article-entity-hubs-title"><header class="rt-section-head"><div><h2 id="article-entity-hubs-title">${esc(title)}</h2></div></header><div class="rt-topic-grid">${cards}</div></section>`;
}

function postCardImage(post) {
  return String(
    post?.image
    || post?.images?.card
    || post?.images?.hero
    || post?.images?.social
    || "/assets/social/home.jpg"
  ).trim();
}

function chronologicalHtml(neighbors, currentPost, pathname) {
  const match = String(pathname || "").match(ARTICLE_PARTS);
  if (!match) return "";
  const [, locale] = match;
  const isAr = locale.toLowerCase() === "ar";
  const title = isAr ? "تابع التسلسل الزمني" : "Continue chronologically";
  const newerLabel = isAr ? "الخبر الأحدث" : "Newer story";
  const olderLabel = isAr ? "الخبر الأقدم" : "Older story";
  const currentLabel = isAr ? "أنت تقرأ الآن" : "You are reading";
  const steps = [];

  for (const [kind, post] of [["newer", neighbors?.newer], ["older", neighbors?.older]]) {
    const href = publicPath(post?.url || "");
    const postTitle = String(post?.title || "").trim();
    if (!href || !postTitle) continue;
    const label = kind === "newer" ? newerLabel : olderLabel;
    const image = postCardImage(post);
    const date = String(post?.dateLabel || "").trim();
    const readTime = String(post?.readTime || "").trim();
    const meta = [date, readTime].filter(Boolean).join(" · ");
    steps.push({
      kind,
      html: `<a class="rt-chronology-step rt-chronology-${esc(kind)}" data-chronology="${esc(kind)}" href="${esc(href)}"><span class="rt-chronology-node" aria-hidden="true"></span><div class="rt-thumb rt-chronology-thumb"><img src="${esc(image)}" alt="${esc(postTitle)}" width="800" height="450" loading="lazy" decoding="async"></div><div class="rt-chronology-copy"><span class="rt-chronology-label">${esc(label)}</span><b>${esc(postTitle)}</b>${meta ? `<small>${esc(meta)}</small>` : ""}</div></a>`
    });
  }

  if (!steps.length) return "";
  const newer = steps.find((item) => item.kind === "newer")?.html || "";
  const older = steps.find((item) => item.kind === "older")?.html || "";
  const currentTitle = String(currentPost?.title || "").trim();
  const current = currentTitle
    ? `<div class="rt-chronology-current" aria-current="step"><span class="rt-chronology-node" aria-hidden="true"></span><div><small>${esc(currentLabel)}</small><strong>${esc(currentTitle)}</strong></div></div>`
    : "";

  return `<section class="rt-section rt-article-chronology" aria-labelledby="article-chronology-title"><header class="rt-section-head"><div><h2 id="article-chronology-title">${esc(title)}</h2></div></header><div class="rt-chronology-timeline">${newer}${current}${older}</div></section>`;
}
function relatedHtml(posts, pathname) {
  const match = String(pathname || "").match(ARTICLE_PARTS);
  if (!match) return "";
  const [, locale, category] = match;
  const isAr = locale.toLowerCase() === "ar";
  const title = isAr ? "أخبار مرتبطة" : "Related stories";
  const more = isAr ? "المزيد حول هذا الموضوع" : "More on this topic";
  const categoryUrl = `/${locale}/${category}/`;
  const topicHubs = topicHubHtml(locale, category);

  const cards = posts.map((post) => {
    const href = publicPath(post?.url || "");
    const postTitle = String(post?.title || "").trim();
    const excerpt = String(post?.excerpt || "").trim();
    const date = String(post?.dateLabel || "").trim();
    const readTime = String(post?.readTime || "").trim();
    const categoryLabel = String(post?.category || "").trim();
    const image = postCardImage(post);
    const meta = [date, readTime].filter(Boolean).join(" · ");
    if (!href || !postTitle) return "";
    return `<a class="rt-feed-item rt-related-card" href="${esc(href)}"><div class="rt-feed-copy">${categoryLabel ? `<div class="rt-feed-kicker"><span>${esc(categoryLabel)}</span></div>` : ""}<h3>${esc(postTitle)}</h3>${excerpt ? `<p>${esc(excerpt)}</p>` : ""}${meta ? `<div class="rt-feed-time">${esc(meta)}</div>` : ""}</div><div class="rt-thumb"><img src="${esc(image)}" alt="${esc(postTitle)}" width="800" height="450" loading="lazy" decoding="async"></div></a>`;
  }).filter(Boolean).join("");

  const stories = cards
    ? `<section class="rt-section rt-related-stories" data-related-strategy="semantic" aria-labelledby="related-stories-title"><header class="rt-section-head"><div><h2 id="related-stories-title">${esc(title)}</h2></div><a href="${esc(categoryUrl)}">${esc(more)}</a></header><div class="rt-feed">${cards}</div></section>`
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
  const current = publicPath(pathname);
  const currentPost = posts.find((post) => publicPath(post?.url || "") === current);
  const html = chronologicalHtml(chronology, currentPost, pathname)
    + entityHubHtml(currentPost, locale)
    + relatedHtml(related, pathname);
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
