const ORIGIN = "https://mikhbar.website";

const UI = {
  ar: {
    dir: "rtl", site: "مِخبار", home: "الرئيسية", latest: "أحدث الأخبار", sections: "الأقسام", top: "الأهم الآن", newsletter: "النشرة", about: "عن مِخبار", lang: "EN",
    breadcrumb: "مسار التنقل", published: "نُشر", updated: "آخر تحديث", read: "دقائق قراءة", summary: "الخلاصة", sources: "المصادر",
    author: "رضوان عبدالهادي", role: "مؤسس ومحرر مِخبار", sourceNote: "صيغ هذا الخبر اعتمادًا على المصادر المدرجة أعلاه، مع فصل المعلومات المؤكدة عن ادعاءات الشركات أو التقديرات.",
    footerDesc: "منصة تقنية عربية وإنجليزية مستقلة.", publication: "عن المنصة", editorial: "السياسة التحريرية", trust: "الثقة", corrections: "التصحيحات", ai: "سياسة AI"
  },
  en: {
    dir: "ltr", site: "Mikhbar", home: "Home", latest: "Latest", sections: "Sections", top: "Top stories", newsletter: "Newsletter", about: "About Mikhbar", lang: "عربي",
    breadcrumb: "Breadcrumb", published: "Published", updated: "Updated", read: "min read", summary: "Key points", sources: "Sources",
    author: "Radwan Abdulhadi", role: "Founder and editor, Mikhbar", sourceNote: "This report was produced from the sources listed above, separating confirmed information from company claims or estimates.",
    footerDesc: "An independent bilingual technology publication.", publication: "Publication", editorial: "Editorial policy", trust: "Trust", corrections: "Corrections", ai: "AI policy"
  }
};

const ARTICLE_ROUTE = /^\/(ar|en)\/([a-z0-9-]+)\/([^/]+)\/?$/i;

function esc(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function safeUrl(value) {
  const raw = String(value || "").trim();
  try {
    const u = new URL(raw);
    return ["http:", "https:"].includes(u.protocol) ? u.toString() : "";
  } catch {
    return "";
  }
}

function localize(value, locale, fallback = "") {
  if (value && typeof value === "object" && !Array.isArray(value)) {
    return String(value[locale] || value.en || value.ar || fallback);
  }
  return String(value || fallback);
}

function publicPath(value) {
  let path = String(value || "/");
  if (path.startsWith("/forum/")) path = path.slice("/forum".length);
  if (!path.startsWith("/")) path = "/" + path;
  return path;
}

function absoluteAsset(value) {
  const raw = String(value || "").trim();
  if (!raw) return "";
  if (/^https?:\/\//i.test(raw)) return raw;
  return ORIGIN + publicPath(raw);
}

async function assetJson(env, request, path) {
  const url = new URL(path, request.url);
  const response = await env.ASSETS.fetch(new Request(url, request));
  if (!response.ok) return null;
  try { return await response.json(); } catch { return null; }
}

async function resolveRecord(env, request, pathname) {
  const map = await assetJson(env, request, "/article-map.json");
  const keys = [pathname, "/forum" + pathname];
  let entry = null;
  for (const key of keys) {
    if (map?.routes?.[key]) { entry = map.routes[key]; break; }
  }
  if (!entry?.content) return null;
  const contentPath = publicPath(entry.content);
  const record = await assetJson(env, request, contentPath);
  return record ? { entry, record, contentPath } : null;
}

function linkedParagraph(paragraph) {
  const text = typeof paragraph === "object" && paragraph ? String(paragraph.text || "") : String(paragraph || "");
  const links = typeof paragraph === "object" && paragraph && Array.isArray(paragraph.links) ? paragraph.links : [];
  const placements = [];
  const occupied = [];
  for (const link of links) {
    const label = String(link?.text || "").trim();
    const url = safeUrl(link?.url);
    if (!label || !url) continue;
    let start = text.indexOf(label);
    while (start >= 0 && occupied.some(([a, b]) => !(start + label.length <= a || start >= b))) start = text.indexOf(label, start + label.length);
    if (start < 0) continue;
    const end = start + label.length;
    occupied.push([start, end]);
    placements.push({ start, end, label, url });
  }
  placements.sort((a, b) => a.start - b.start);
  if (!placements.length) return esc(text);
  let cursor = 0;
  const out = [];
  for (const item of placements) {
    out.push(esc(text.slice(cursor, item.start)));
    out.push(`<a href="${esc(item.url)}" rel="noopener noreferrer" target="_blank">${esc(item.label)}</a>`);
    cursor = item.end;
  }
  out.push(esc(text.slice(cursor)));
  return out.join("");
}

function inlineSlots(sectionCount, imageCount) {
  const slots = new Map();
  if (!sectionCount || !imageCount) return slots;
  let last = -1;
  for (let i = 0; i < imageCount; i += 1) {
    let slot = Math.round(((i + 1) * sectionCount) / (imageCount + 1)) - 1;
    slot = Math.max(0, Math.min(sectionCount - 1, slot));
    if (slot <= last && last < sectionCount - 1) slot = last + 1;
    last = slot;
    if (!slots.has(slot)) slots.set(slot, []);
    slots.get(slot).push(i);
  }
  return slots;
}

function inlineFigure(image, locale) {
  const src = absoluteAsset(image?.src);
  if (!src) return "";
  const alt = localize(image?.alt, locale, "");
  const caption = localize(image?.caption, locale, "");
  const credit = String(image?.credit || "").trim();
  const sourceUrl = safeUrl(image?.sourceUrl);
  const bits = [];
  if (caption) bits.push(esc(caption));
  if (credit) {
    const prefix = locale === "ar" ? "المصدر: " : "Source: ";
    bits.push(sourceUrl ? `${esc(prefix)}<a href="${esc(sourceUrl)}" rel="nofollow noopener noreferrer" target="_blank">${esc(credit)}</a>` : esc(prefix + credit));
  }
  return `<figure class="rt-inline-media"><img src="${esc(src)}" alt="${esc(alt)}" width="${Number(image?.width || 1200)}" height="${Number(image?.height || 675)}" loading="lazy" decoding="async">${bits.length ? `<figcaption>${bits.join(" · ")}</figcaption>` : ""}</figure>`;
}

function bodyHtml(record, view, locale) {
  const images = record.images || {};
  const sections = Array.isArray(view.sections) ? view.sections : [];
  const inline = Array.isArray(images.inline) ? images.inline : [];
  const slots = inlineSlots(sections.length, inline.length);
  const out = [];
  sections.forEach((section, index) => {
    out.push(`<h2>${esc(section?.heading)}</h2>`);
    for (const paragraph of (section?.paragraphs || [])) out.push(`<p>${linkedParagraph(paragraph)}</p>`);
    for (const imageIndex of (slots.get(index) || [])) out.push(inlineFigure(inline[imageIndex], locale));
  });
  out.push(`<h2>${esc(UI[locale].sources)}</h2><ul class="rt-source-list">`);
  for (const source of (record.sources || [])) {
    const url = safeUrl(source?.url);
    if (!url) continue;
    const name = source?.name || new URL(url).hostname;
    out.push(`<li><a href="${esc(url)}" rel="nofollow noopener noreferrer" target="_blank">${esc(name)}</a>${source?.title ? `<small>${esc(source.title)}</small>` : ""}</li>`);
  }
  out.push("</ul>");
  return out.join("");
}

function schemaFor(record, view, locale, canonical, social) {
  const other = locale === "ar" ? "en" : "ar";
  return {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "NewsArticle",
        "@id": canonical + "#article",
        headline: view.title,
        description: view.description,
        datePublished: record.datePublished,
        dateModified: record.dateModified || record.datePublished,
        inLanguage: locale,
        mainEntityOfPage: canonical,
        image: [social],
        articleSection: view.category || record.categorySlug,
        keywords: view.tags || [],
        author: { "@type": "Person", name: UI[locale].author, url: ORIGIN + "/authors/radwan-abdulhadi/" },
        publisher: {
          "@type": "NewsMediaOrganization",
          "@id": ORIGIN + "/#publisher",
          name: UI[locale].site,
          url: ORIGIN + "/",
          logo: { "@type": "ImageObject", url: ORIGIN + "/assets/brand/mikhbar/06-web-ready/icon/mikhbar-app-icon-512.png" }
        }
      },
      {
        "@type": "BreadcrumbList",
        itemListElement: [
          { "@type": "ListItem", position: 1, name: UI[locale].site, item: ORIGIN + `/${locale}/` },
          { "@type": "ListItem", position: 2, name: view.category || record.categorySlug, item: ORIGIN + `/${locale}/${record.categorySlug}/` },
          { "@type": "ListItem", position: 3, name: view.title }
        ]
      },
      {
        "@type": "WebPage",
        url: canonical,
        inLanguage: locale,
        isPartOf: { "@id": ORIGIN + "/#publisher" },
        alternateName: record?.locales?.[other]?.title || undefined
      }
    ]
  };
}

class TextHandler {
  constructor(value, html = false) { this.value = value; this.html = html; }
  element(element) { element.setInnerContent(String(this.value ?? ""), { html: this.html }); }
}
class AttrHandler {
  constructor(attrs = {}, text = null) { this.attrs = attrs; this.textValue = text; }
  element(element) {
    for (const [key, value] of Object.entries(this.attrs)) element.setAttribute(key, String(value ?? ""));
    if (this.textValue !== null) element.setInnerContent(String(this.textValue));
  }
}
class HideHandler { element(element) { element.setAttribute("hidden", ""); } }
class ShowHandler { element(element) { element.removeAttribute("hidden"); } }

export function isArticlePath(pathname) {
  return ARTICLE_ROUTE.test(pathname);
}

export async function renderDynamicArticle(request, env, pathname) {
  const match = pathname.match(ARTICLE_ROUTE);
  if (!match) return null;
  const locale = match[1].toLowerCase();
  const resolved = await resolveRecord(env, request, pathname);
  if (!resolved) return null;
  const { record } = resolved;
  const view = record?.locales?.[locale];
  if (!view) return null;
  const ui = UI[locale];

  const shellUrl = new URL("/article/", request.url);
  const shell = await env.ASSETS.fetch(new Request(shellUrl, request));
  if (!shell.ok) return null;

  const canonical = ORIGIN + pathname;
  const arUrl = ORIGIN + publicPath(record?.urls?.ar || pathname);
  const enUrl = ORIGIN + publicPath(record?.urls?.en || pathname);
  const images = record.images || {};
  const hero = absoluteAsset(images.hero || images.card || images.social || "");
  const social = absoluteAsset(images.social || images.hero || images.card || "/assets/brand/mikhbar/06-web-ready/icon/mikhbar-app-icon-512.png");
  const alt = localize(images.alt, locale, view.title || "");
  const category = view.category || record.categorySlug || "";
  const other = locale === "ar" ? "en" : "ar";
  const otherUrl = publicPath(record?.urls?.[other] || `/${other}/`);
  const summary = (view.summaryBullets || []).map((item) => `<li>${esc(item)}</li>`).join("");
  const tags = (view.tags || []).slice(0, 8).map((item) => `<span>${esc(item)}</span>`).join("");
  const credit = String(images.credit || "").trim();
  const schema = JSON.stringify(schemaFor(record, view, locale, canonical, social)).replaceAll("<", "\\u003c");

  const rewriter = new HTMLRewriter()
    .on("html", new AttrHandler({ lang: locale, dir: ui.dir }))
    .on("body", new AttrHandler({ class: `rt-locale-${locale}`, "data-ssr-rendered": "true" }))
    .on("title", new TextHandler(`${view.title} | ${ui.site}`))
    .on("#meta-description", new AttrHandler({ content: view.description || view.deck || "" }))
    .on("#meta-robots", new AttrHandler({ content: "index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1" }))
    .on("#canonical-link", new AttrHandler({ href: canonical }))
    .on("#alternate-ar", new AttrHandler({ href: arUrl }))
    .on("#alternate-en", new AttrHandler({ href: enUrl }))
    .on("#alternate-default", new AttrHandler({ href: ORIGIN + "/" }))
    .on("#og-site-name", new AttrHandler({ content: ui.site }))
    .on("#og-locale", new AttrHandler({ content: locale === "ar" ? "ar_IQ" : "en_US" }))
    .on("#og-title", new AttrHandler({ content: view.title || "" }))
    .on("#og-description", new AttrHandler({ content: view.description || "" }))
    .on("#og-url", new AttrHandler({ content: canonical }))
    .on("#og-image", new AttrHandler({ content: social }))
    .on("#article-published", new AttrHandler({ content: record.datePublished || "" }))
    .on("#article-modified", new AttrHandler({ content: record.dateModified || record.datePublished || "" }))
    .on("#twitter-title", new AttrHandler({ content: view.title || "" }))
    .on("#twitter-description", new AttrHandler({ content: view.description || "" }))
    .on("#twitter-image", new AttrHandler({ content: social }))
    .on("#article-schema", new TextHandler(schema))
    .on("#brand-name", new TextHandler(ui.site))
    .on("#brand-link", new AttrHandler({ href: `/${locale}/`, "aria-label": ui.site }))
    .on("#nav-home", new AttrHandler({ href: `/${locale}/` }, ui.home))
    .on("#nav-latest", new AttrHandler({ href: `/${locale}/#latest` }, ui.latest))
    .on("#nav-sections", new AttrHandler({ href: `/${locale}/#sections` }, ui.sections))
    .on("#nav-top", new AttrHandler({ href: `/${locale}/#top-stories` }, ui.top))
    .on("#nav-newsletter", new AttrHandler({ href: `/${locale}/#newsletter` }, ui.newsletter))
    .on("#nav-about", new AttrHandler({ href: "/about/" }, ui.about))
    .on("#nav-lang", new AttrHandler({ href: otherUrl }, ui.lang))
    .on("#article-loading", new HideHandler())
    .on("#article-error", new HideHandler())
    .on("#article-content", new ShowHandler())
    .on("#article-shell", new AttrHandler({ "aria-busy": "false" }))
    .on("#breadcrumbs", new AttrHandler({ "aria-label": ui.breadcrumb }))
    .on("#breadcrumbs", new TextHandler(`<a href="/${locale}/">${esc(ui.site)}</a><span>›</span><a href="/${locale}/${esc(record.categorySlug)}/">${esc(category)}</a><span>›</span><span>${esc(view.title)}</span>`, true))
    .on("#category-label", new TextHandler(category))
    .on("#article-title", new TextHandler(view.title || ""))
    .on("#article-deck", new TextHandler(view.deck || ""))
    .on("#author-link", new AttrHandler({ href: "/authors/radwan-abdulhadi/" }))
    .on("#author-name", new TextHandler(ui.author))
    .on("#author-role", new TextHandler(ui.role))
    .on("#article-dates", new TextHandler(`${ui.published}: ${view.dateLabel || ""} · ${ui.updated}: ${view.modifiedLabel || view.dateLabel || ""} · ${view.readMinutes || 3} ${ui.read}`))
    .on("#hero-image", new AttrHandler({ src: hero, alt }))
    .on("#image-credit", credit ? new AttrHandler({}, `${locale === "ar" ? "الصورة: " : "Image: "}${credit}`) : new HideHandler())
    .on("#summary-title", new TextHandler(ui.summary))
    .on("#summary-list", new TextHandler(summary, true))
    .on("#article-body", new TextHandler(bodyHtml(record, view, locale), true))
    .on("#article-tags", new TextHandler(tags, true))
    .on("#source-note", new TextHandler(ui.sourceNote))
    .on("#footer-brand", new TextHandler(ui.site))
    .on("#footer-copy-brand", new TextHandler(ui.site))
    .on("#footer-description", new TextHandler(ui.footerDesc))
    .on("#footer-publication-title", new TextHandler(ui.publication))
    .on("#footer-about", new AttrHandler({ href: "/about/" }, ui.about))
    .on("#footer-editorial", new AttrHandler({ href: "/editorial-policy/" }, ui.editorial))
    .on("#footer-trust-title", new TextHandler(ui.trust))
    .on("#footer-corrections", new AttrHandler({ href: "/corrections/" }, ui.corrections))
    .on("#footer-ai", new AttrHandler({ href: "/ai-policy/" }, ui.ai));

  const transformed = rewriter.transform(shell);
  const headers = new Headers(transformed.headers);
  headers.set("Content-Type", "text/html; charset=UTF-8");
  headers.set("X-Mikhbar-Article-Mode", "single-template-ssr");
  return new Response(transformed.body, { status: 200, headers });
}
