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

function renderRadwanTestPage() {
  const html = "<!doctype html>\n<html lang=\"ar\" dir=\"rtl\">\n<head>\n<meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width,initial-scale=1,viewport-fit=cover\">\n<meta name=\"theme-color\" content=\"#ffffff\">\n<title>عارض شعارات مِخبار</title>\n<meta name=\"robots\" content=\"noindex,nofollow,noarchive,nosnippet\">\n<link rel=\"canonical\" href=\"https://mikhbar.website/ar/radwantest/\">\n<link rel=\"icon\" href=\"/assets/brand/mikhbar/06-web-ready/favicon/favicon.svg\">\n<style>\n*{box-sizing:border-box}\nhtml,body{width:100%;height:100%;margin:0;background:#fff}\nbody{overflow:hidden;font-family:system-ui,-apple-system,\"Segoe UI\",sans-serif;color:#111;user-select:none}\n.logo-stage{position:fixed;inset:0;display:grid;place-items:center;background:#fff}\n.logo-wrap{width:100%;height:100%;display:grid;place-items:center;padding:8vh 7vw}\n#brandAsset{display:block;object-fit:contain;object-position:center;opacity:1;transform:scale(1);transition:opacity .16s ease,transform .22s cubic-bezier(.2,.7,.2,1);filter:none}\n#brandAsset.mark{width:min(60vmin,680px);height:min(60vmin,680px);max-width:82vw;max-height:72vh}\n#brandAsset.icon{width:min(60vmin,680px);height:min(60vmin,680px);max-width:82vw;max-height:72vh}\n#brandAsset.wide{width:min(82vw,1180px);height:auto;max-height:70vh}\n#brandAsset.is-changing{opacity:0;transform:scale(.965)}\n.publish-countdown{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);z-index:10;display:flex;align-items:center;gap:8px;direction:rtl;padding:9px 14px;border:1px solid rgba(17,17,17,.08);border-radius:999px;background:rgba(255,255,255,.88);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);box-shadow:0 6px 22px rgba(0,0,0,.05);font-size:13px;font-weight:650;color:#555;white-space:nowrap}\n.publish-countdown strong{font-variant-numeric:tabular-nums;font-size:14px;color:#111;letter-spacing:.02em}\n.publish-countdown.is-publishing strong{color:#111}\n@media(max-width:720px){\n  .logo-wrap{padding:7vh 5vw}\n  #brandAsset.mark,#brandAsset.icon{width:min(74vmin,580px);height:min(74vmin,580px)}\n  #brandAsset.wide{width:92vw;max-height:66vh}\n  .publish-countdown{bottom:18px;font-size:12px;padding:8px 12px}\n  .publish-countdown strong{font-size:13px}\n}\n</style>\n</head>\n<body>\n<main class=\"logo-stage\" aria-label=\"عارض شعارات مِخبار\">\n  <div class=\"logo-wrap\">\n    <img id=\"brandAsset\" class=\"mark\" alt=\"شعار مِخبار\" decoding=\"async\">\n  </div>\n</main>\n<div class=\"publish-countdown\" id=\"publishCountdown\" role=\"status\" aria-live=\"polite\"><span>المنشور التالي بعد</span><strong id=\"publishCountdownValue\">--:--</strong></div>\n<script>\nconst assets = [\n  {src:\"/assets/brand/mikhbar/06-web-ready/icon/mikhbar-logo-mark.png\", kind:\"mark\"},\n  {src:\"/assets/brand/mikhbar/01-logo-mark/transparent/mikhbar-logo-mark-transparent-master-4096.png\", kind:\"mark\"},\n  {src:\"/assets/brand/mikhbar/02-full-logo/transparent/mikhbar-full-logo-transparent-4096w.png\", kind:\"wide\"},\n  {src:\"/assets/images/06_Mikhbar_Sticker_Animated_512.webp\", kind:\"mark\", animated:true, fileName:\"06_Mikhbar_Sticker_Animated_512.gif\"},\n  {src:\"/assets/brand/mikhbar/04-animated-logo-mark/web-optimized/mikhbar-logo-mark-web-alpha.webp\", kind:\"mark\", animated:true, gifSrc:\"/assets/brand/mikhbar/04-animated-logo-mark/white-background/mikhbar-logo-mark-animated-white.gif\", fileName:\"Mikhbar_Logo_Mark_Animated.gif\"},\n  {src:\"/assets/brand/mikhbar/05-animated-full-logo/web-optimized/mikhbar-full-logo-web-alpha.webp\", kind:\"wide\", animated:true, gifSrc:\"/assets/brand/mikhbar/05-animated-full-logo/white-background/mikhbar-full-logo-animated-white.gif\", fileName:\"Mikhbar_Full_Logo_Animated.gif\"},\n  {src:\"/assets/brand/mikhbar/03-icon/svg/mikhbar-icon-preserved-artwork.svg\", kind:\"icon\"},\n  {src:\"/assets/brand/mikhbar/01-logo-mark/monochrome/mikhbar-logo-mark-black-2048.png\", kind:\"mark\"},\n  {src:\"/assets/brand/mikhbar/02-full-logo/monochrome/mikhbar-full-logo-black-2400w.png\", kind:\"wide\"},\n  {src:\"/assets/brand/mikhbar/01-logo-mark/svg/mikhbar-logo-mark-monochrome-vector.svg\", kind:\"mark\"},\n  {src:\"/assets/brand/mikhbar/02-full-logo/svg/mikhbar-full-logo-monochrome-vector.svg\", kind:\"wide\"},\n  {src:\"/assets/brand/mikhbar/01-logo-mark/svg/mikhbar-logo-mark-preserved-artwork.svg\", kind:\"mark\"},\n  {src:\"/assets/brand/mikhbar/02-full-logo/svg/mikhbar-full-logo-preserved-artwork.svg\", kind:\"wide\"},\n  {src:\"/assets/brand/mikhbar/06-web-ready/header-logo/mikhbar-header-logo-transparent.png\", kind:\"wide\"},\n  {src:\"/assets/brand/mikhbar/04-animated-logo-mark/white-background/mikhbar-logo-mark-animated-white.gif\", kind:\"mark\", animated:true, gifSrc:\"/assets/brand/mikhbar/04-animated-logo-mark/white-background/mikhbar-logo-mark-animated-white.gif\", fileName:\"Mikhbar_Logo_Mark_Animated.gif\"},\n  {src:\"/assets/brand/mikhbar/05-animated-full-logo/white-background/mikhbar-full-logo-animated-white.gif\", kind:\"wide\", animated:true, gifSrc:\"/assets/brand/mikhbar/05-animated-full-logo/white-background/mikhbar-full-logo-animated-white.gif\", fileName:\"Mikhbar_Full_Logo_Animated.gif\"}\n];\n\nlet index = 0;\nlet saveInProgress = false;\nconst image = document.getElementById(\"brandAsset\");\nconst countdown = document.getElementById(\"publishCountdown\");\nconst countdownValue = document.getElementById(\"publishCountdownValue\");\nlet targetPublishAt = null;\n\nfunction formatRemaining(ms){\n  const totalSeconds = Math.max(0, Math.ceil(ms / 1000));\n  const hours = Math.floor(totalSeconds / 3600);\n  const minutes = Math.floor((totalSeconds % 3600) / 60);\n  const seconds = totalSeconds % 60;\n  const mm = String(minutes).padStart(2, \"0\");\n  const ss = String(seconds).padStart(2, \"0\");\n  return hours > 0 ? String(hours).padStart(2, \"0\") + \":\" + mm + \":\" + ss : mm + \":\" + ss;\n}\n\nfunction renderPublishCountdown(){\n  if (!targetPublishAt) {\n    countdown.classList.remove(\"is-publishing\");\n    countdown.querySelector(\"span\").textContent = \"المنشور التالي بعد\";\n    countdownValue.textContent = \"--:--\";\n    return;\n  }\n  const remaining = targetPublishAt - Date.now();\n  if (remaining <= 0) {\n    countdown.classList.add(\"is-publishing\");\n    countdown.querySelector(\"span\").textContent = \"حالة النشر\";\n    countdownValue.textContent = \"جارٍ النشر…\";\n    return;\n  }\n  countdown.classList.remove(\"is-publishing\");\n  countdown.querySelector(\"span\").textContent = \"المنشور التالي بعد\";\n  countdownValue.textContent = formatRemaining(remaining);\n}\n\nasync function refreshPublisherStatus(){\n  try {\n    const response = await fetch(\"/feed-ar.xml?t=\" + Date.now(), {cache:\"no-store\"});\n    if (!response.ok) throw new Error(\"feed status \" + response.status);\n    const xml = await response.text();\n    const doc = new DOMParser().parseFromString(xml, \"application/xml\");\n    const latestPubDate = doc.querySelector(\"channel > item > pubDate\")?.textContent?.trim() || \"\";\n    const latestPublishedAt = Date.parse(latestPubDate);\n    if (!Number.isFinite(latestPublishedAt)) throw new Error(\"latest pubDate unavailable\");\n    targetPublishAt = latestPublishedAt + (20 * 60 * 1000);\n    renderPublishCountdown();\n  } catch (error) {\n    console.error(\"Could not refresh publisher countdown:\", error);\n  }\n}\n\nfunction startPublisherCountdown(){\n  renderPublishCountdown();\n  setInterval(renderPublishCountdown, 1000);\n  refreshPublisherStatus();\n  setInterval(refreshPublisherStatus, 15000);\n}\n\nfunction show(nextIndex, animate=true){\n  index = (nextIndex + assets.length) % assets.length;\n  const item = assets[index];\n  if (animate) image.classList.add(\"is-changing\");\n  const apply = () => {\n    image.className = item.kind;\n    image.alt = \"شعار مِخبار\";\n    const shouldRestart = item.animated;\n    image.src = item.src + (shouldRestart ? \"?slide=\" + Date.now() : \"\");\n    requestAnimationFrame(() => image.classList.remove(\"is-changing\"));\n  };\n  animate ? setTimeout(apply, 120) : apply();\n}\n\nfunction downloadBlob(blob, fileName){\n  const url = URL.createObjectURL(blob);\n  const a = document.createElement(\"a\");\n  a.href = url;\n  a.download = fileName;\n  document.body.appendChild(a);\n  a.click();\n  a.remove();\n  setTimeout(() => URL.revokeObjectURL(url), 4000);\n}\n\nasync function downloadExistingGif(url, fileName){\n  const response = await fetch(url, {cache:\"no-store\"});\n  if (!response.ok) throw new Error(\"GIF download failed\");\n  const blob = await response.blob();\n  downloadBlob(blob, fileName);\n}\n\nasync function convertAnimatedWebpToGif(url, fileName){\n  if (!(\"ImageDecoder\" in window)) throw new Error(\"ImageDecoder is unavailable\");\n  const response = await fetch(url, {cache:\"no-store\"});\n  if (!response.ok) throw new Error(\"Animation fetch failed\");\n  const data = await response.arrayBuffer();\n  const type = response.headers.get(\"content-type\") || \"image/webp\";\n  if (ImageDecoder.isTypeSupported && !(await ImageDecoder.isTypeSupported(type))) {\n    throw new Error(\"Animated image decoding is unsupported\");\n  }\n\n  const decoder = new ImageDecoder({data, type});\n  await decoder.tracks.ready;\n  const track = decoder.tracks.selectedTrack;\n  const frameCount = Math.max(1, track?.frameCount || 1);\n  const {GIFEncoder, quantize, applyPalette} = await import(\"https://cdn.jsdelivr.net/npm/gifenc@1.0.3/+esm\");\n  const gif = GIFEncoder();\n  const canvas = document.createElement(\"canvas\");\n  const ctx = canvas.getContext(\"2d\", {willReadFrequently:true});\n\n  for (let i = 0; i < frameCount; i++) {\n    const decoded = await decoder.decode({frameIndex:i});\n    const frame = decoded.image;\n    if (!canvas.width || !canvas.height) {\n      canvas.width = frame.displayWidth || frame.codedWidth;\n      canvas.height = frame.displayHeight || frame.codedHeight;\n    }\n    ctx.clearRect(0,0,canvas.width,canvas.height);\n    ctx.fillStyle = \"#ffffff\";\n    ctx.fillRect(0,0,canvas.width,canvas.height);\n    ctx.drawImage(frame,0,0,canvas.width,canvas.height);\n    const rgba = ctx.getImageData(0,0,canvas.width,canvas.height).data;\n    const palette = quantize(rgba, 256);\n    const indexed = applyPalette(rgba, palette);\n    const delay = Math.max(20, Math.round((frame.duration || 100000) / 1000));\n    gif.writeFrame(indexed, canvas.width, canvas.height, {\n      palette,\n      delay,\n      repeat: i === 0 ? 0 : undefined\n    });\n    frame.close();\n  }\n\n  gif.finish();\n  downloadBlob(new Blob([gif.bytes()], {type:\"image/gif\"}), fileName);\n  decoder.close();\n}\n\nasync function saveCurrentAnimation(){\n  const item = assets[index];\n  if (!item?.animated || saveInProgress) return;\n  saveInProgress = true;\n  try {\n    if (item.gifSrc) {\n      await downloadExistingGif(item.gifSrc, item.fileName || \"Mikhbar_Animated.gif\");\n    } else {\n      await convertAnimatedWebpToGif(item.src, item.fileName || \"Mikhbar_Animated.gif\");\n    }\n  } catch (error) {\n    console.error(\"Could not create GIF:\", error);\n  } finally {\n    saveInProgress = false;\n  }\n}\n\ndocument.addEventListener(\"keydown\", (event) => {\n  if (event.key === \"ArrowRight\") { event.preventDefault(); show(index + 1); return; }\n  if (event.key === \"ArrowLeft\") { event.preventDefault(); show(index - 1); return; }\n\n  const digitNine = event.code === \"Digit9\" || event.key === \"9\";\n  const saveShortcut = digitNine && (event.metaKey || (event.ctrlKey && event.altKey));\n  if (saveShortcut) {\n    event.preventDefault();\n    saveCurrentAnimation();\n  }\n});\n\nlet touchStartX = null;\ndocument.addEventListener(\"touchstart\", e => { touchStartX = e.changedTouches[0]?.clientX ?? null; }, {passive:true});\ndocument.addEventListener(\"touchend\", e => {\n  if (touchStartX == null) return;\n  const endX = e.changedTouches[0]?.clientX ?? touchStartX;\n  const dx = endX - touchStartX;\n  if (Math.abs(dx) > 45) show(index + (dx < 0 ? 1 : -1));\n  touchStartX = null;\n}, {passive:true});\n\nshow(0,false);\nstartPublisherCountdown();\n</script>\n</body>\n</html>";
  return new Response(html, {
    headers: {
      "Content-Type": "text/html; charset=UTF-8",
      "Cache-Control": "no-store",
    },
  });
}

async function renderRadwanPublisherStatus() {
  try {
    const cacheBucket = Math.floor(Date.now() / 10000);
    const source = "https://raw.githubusercontent.com/rad03i2/rad/main/automation/forum/state/publisher_report.json?v=" + cacheBucket;
    const response = await fetch(source, {
      headers: { "Accept": "application/json" },
      cf: { cacheTtl: 0, cacheEverything: false },
    });
    if (!response.ok) {
      return Response.json({ ok: false, error: "publisher_status_unavailable" }, {
        status: 502,
        headers: { "Cache-Control": "no-store" },
      });
    }
    const report = await response.json();
    return Response.json({
      ok: true,
      status: report.status || null,
      target_publish_at: report.target_publish_at || null,
      title_ar: report.title_ar || null,
      story_id: report.story_id || null,
    }, {
      headers: { "Cache-Control": "no-store" },
    });
  } catch (error) {
    return Response.json({ ok: false, error: "publisher_status_error" }, {
      status: 502,
      headers: { "Cache-Control": "no-store" },
    });
  }
}

function shouldNoIndexTechnicalPath(pathname) {
  const path = String(pathname || "").toLowerCase();
  return path === "/healthz"
    || path === "/ar/radwantest"
    || path === "/ar/radwantest/"
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
  if (String(pathname || "").toLowerCase().startsWith("/ar/radwantest")) {
    headers.set("Cache-Control", "no-store");
  } else if (type.includes("text/html") || type.includes("xml") || type.includes("json")) {
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

    if (url.pathname === "/ar/radwantest") {
      const canonical = canonicalUrl(url);
      canonical.pathname = "/ar/radwantest/";
      return Response.redirect(canonical.toString(), 308);
    }

    if (url.pathname === "/ar/radwantest/") {
      return withHeaders(renderRadwanTestPage(), url.pathname);
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
