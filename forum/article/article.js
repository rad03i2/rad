(() => {
  'use strict';

  const PUBLIC_ORIGIN = 'https://mikhbar.website';
  const SOURCE_PREFIX = '/forum';
  const UI = {
    ar: {
      dir: 'rtl', site: 'مِخبار', home: 'الرئيسية', latest: 'أحدث الأخبار', sections: 'الأقسام', top: 'الأهم الآن', newsletter: 'النشرة', about: 'عن مِخبار', lang: 'EN',
      loading: 'جاري تحميل الخبر…', errorTitle: 'تعذر تحميل الخبر', errorMessage: 'لم نعثر على بيانات هذا الخبر. تحقق من الرابط ثم حاول مرة أخرى.',
      breadcrumb: 'مسار التنقل', published: 'نُشر', updated: 'آخر تحديث', read: 'دقائق قراءة', summary: 'الخلاصة', sources: 'المصادر',
      author: 'رضوان عبدالهادي', role: 'مؤسس ومحرر مِخبار', sourceNote: 'صيغ هذا الخبر اعتمادًا على المصادر المدرجة أعلاه، مع فصل المعلومات المؤكدة عن ادعاءات الشركات أو التقديرات.',
      footerDesc: 'منصة تقنية عربية وإنجليزية مستقلة.', publication: 'عن المنصة', editorial: 'السياسة التحريرية', trust: 'الثقة', corrections: 'التصحيحات', ai: 'سياسة AI'
    },
    en: {
      dir: 'ltr', site: 'Mikhbar', home: 'Home', latest: 'Latest', sections: 'Sections', top: 'Top stories', newsletter: 'Newsletter', about: 'About Mikhbar', lang: 'عربي',
      loading: 'Loading story…', errorTitle: 'Unable to load this story', errorMessage: 'The structured data for this story could not be found. Check the URL and try again.',
      breadcrumb: 'Breadcrumb', published: 'Published', updated: 'Updated', read: 'min read', summary: 'Key points', sources: 'Sources',
      author: 'Radwan Abdulhadi', role: 'Founder and editor, Mikhbar', sourceNote: 'This report was produced from the sources listed above, separating confirmed information from company claims or estimates.',
      footerDesc: 'An independent bilingual technology publication.', publication: 'Publication', editorial: 'Editorial policy', trust: 'Trust', corrections: 'Corrections', ai: 'AI policy'
    }
  };

  const $ = (id) => document.getElementById(id);

  function sourceRoot() {
    return location.pathname.startsWith('/forum/') ? SOURCE_PREFIX : '';
  }

  function normalizePath(value, root = sourceRoot()) {
    let path = String(value || '').trim();
    try {
      if (/^https?:\/\//i.test(path)) path = new URL(path).pathname;
    } catch (_) {}
    if (!path.startsWith('/')) path = '/' + path;
    path = path.replace(/\/{2,}/g, '/');
    if (root === SOURCE_PREFIX && !path.startsWith('/forum/')) path = '/forum' + path;
    if (root === '' && path.startsWith('/forum/')) path = path.slice('/forum'.length) || '/';
    if (!path.endsWith('/')) path += '/';
    return path;
  }

  function requestedPath() {
    const params = new URLSearchParams(location.search);
    const explicit = params.get('path') || params.get('url') || window.__MIKHBAR_ARTICLE_PATH__;
    return normalizePath(explicit || location.pathname);
  }

  function localeFromPath(path) {
    const cleaned = path.replace(/^\/forum/, '');
    const match = cleaned.match(/^\/(ar|en)\//i);
    return match ? match[1].toLowerCase() : 'ar';
  }

  function publicPath(path) {
    let out = String(path || '/');
    if (out.startsWith('/forum/')) out = out.slice('/forum'.length);
    if (!out.startsWith('/')) out = '/' + out;
    return out;
  }

  function sourcePath(path) {
    let out = String(path || '/');
    if (!out.startsWith('/')) out = '/' + out;
    if (sourceRoot() === SOURCE_PREFIX && !out.startsWith('/forum/')) out = '/forum' + out;
    if (sourceRoot() === '' && out.startsWith('/forum/')) out = out.slice('/forum'.length);
    return out;
  }

  function assetPath(value) {
    const raw = String(value || '').trim();
    if (!raw) return '';
    if (/^https?:\/\//i.test(raw)) return raw;
    return sourcePath(raw);
  }

  function publicUrl(path) {
    return PUBLIC_ORIGIN + publicPath(path);
  }

  async function getJson(url) {
    const response = await fetch(url, { cache: 'no-store', headers: { Accept: 'application/json' } });
    if (!response.ok) throw new Error(`HTTP ${response.status} for ${url}`);
    return response.json();
  }

  async function resolveArticle(path, locale) {
    const root = sourceRoot();
    const mapUrl = `${root}/article-map.json` || '/article-map.json';
    try {
      const map = await getJson(mapUrl);
      const key = normalizePath(path, root);
      const entry = map && map.routes ? map.routes[key] : null;
      if (entry && entry.content) return { entry, contentUrl: sourcePath(entry.content) };
    } catch (_) {
      // The map is an optimization. Fall through to the locale index so the
      // single-template system works immediately during the migration.
    }

    const indexUrl = `${root}/posts-${locale}.json` || `/posts-${locale}.json`;
    const doc = await getJson(indexUrl);
    const posts = Array.isArray(doc) ? doc : (doc.posts || []);
    const wanted = normalizePath(path, root);
    const post = posts.find((item) => normalizePath(item.url || '', root) === wanted);
    if (!post || !post.contentFile) throw new Error('Article route has no structured content record');
    return {
      entry: { locale, content: '/' + String(post.contentFile).replace(/^\/+/, '') },
      contentUrl: sourcePath('/' + String(post.contentFile).replace(/^\/+/, ''))
    };
  }

  function clear(node) {
    while (node && node.firstChild) node.removeChild(node.firstChild);
  }

  function appendLinkedText(parent, paragraph) {
    const text = typeof paragraph === 'object' && paragraph ? String(paragraph.text || '') : String(paragraph || '');
    const links = typeof paragraph === 'object' && paragraph && Array.isArray(paragraph.links) ? paragraph.links : [];
    const placements = [];
    const occupied = [];
    for (const link of links) {
      const label = String(link && link.text || '').trim();
      const url = String(link && link.url || '').trim();
      if (!label || !/^https?:\/\//i.test(url)) continue;
      let start = text.indexOf(label);
      while (start >= 0 && occupied.some(([a, b]) => !(start + label.length <= a || start >= b))) {
        start = text.indexOf(label, start + label.length);
      }
      if (start < 0) continue;
      const end = start + label.length;
      occupied.push([start, end]);
      placements.push({ start, end, label, url });
    }
    placements.sort((a, b) => a.start - b.start);
    let cursor = 0;
    for (const item of placements) {
      parent.append(document.createTextNode(text.slice(cursor, item.start)));
      const a = document.createElement('a');
      a.href = item.url;
      a.target = '_blank';
      a.rel = 'noopener noreferrer';
      a.textContent = item.label;
      parent.append(a);
      cursor = item.end;
    }
    parent.append(document.createTextNode(text.slice(cursor)));
  }

  function localized(value, locale, fallback = '') {
    if (value && typeof value === 'object' && !Array.isArray(value)) return String(value[locale] || value.en || value.ar || fallback);
    return String(value || fallback);
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

  function renderInlineFigure(image, locale) {
    const src = assetPath(image && image.src);
    if (!src) return null;
    const figure = document.createElement('figure');
    figure.className = 'rt-inline-media';
    const img = document.createElement('img');
    img.src = src;
    img.alt = localized(image.alt, locale, '');
    img.width = Number(image.width || 1200);
    img.height = Number(image.height || 675);
    img.loading = 'lazy';
    img.decoding = 'async';
    figure.append(img);
    const caption = localized(image.caption, locale, '');
    const credit = String(image.credit || '').trim();
    if (caption || credit) {
      const figcaption = document.createElement('figcaption');
      if (caption) figcaption.append(document.createTextNode(caption));
      if (credit) {
        if (caption) figcaption.append(document.createTextNode(' · '));
        figcaption.append(document.createTextNode(locale === 'ar' ? 'المصدر: ' : 'Source: '));
        const sourceUrl = String(image.sourceUrl || '').trim();
        if (/^https?:\/\//i.test(sourceUrl)) {
          const a = document.createElement('a');
          a.href = sourceUrl; a.target = '_blank'; a.rel = 'nofollow noopener noreferrer'; a.textContent = credit;
          figcaption.append(a);
        } else figcaption.append(document.createTextNode(credit));
      }
      figure.append(figcaption);
    }
    return figure;
  }

  function setMeta(record, view, locale, routePath) {
    const canonical = publicUrl(routePath);
    const ar = publicUrl(record.urls && record.urls.ar || routePath);
    const en = publicUrl(record.urls && record.urls.en || routePath);
    const images = record.images || {};
    const social = assetPath(images.social || images.hero || images.card || '/assets/brand/mikhbar/06-web-ready/icon/mikhbar-app-icon-512.png');
    const socialAbsolute = /^https?:\/\//i.test(social) ? social : PUBLIC_ORIGIN + publicPath(social);

    document.title = `${view.title} | ${UI[locale].site}`;
    $('meta-description').content = view.description || view.deck || '';
    $('meta-robots').content = 'index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1';
    $('canonical-link').href = canonical;
    $('alternate-ar').href = ar;
    $('alternate-en').href = en;
    $('alternate-default').href = PUBLIC_ORIGIN + '/';
    $('og-site-name').content = UI[locale].site;
    $('og-locale').content = locale === 'ar' ? 'ar_IQ' : 'en_US';
    $('og-title').content = view.title || '';
    $('og-description').content = view.description || '';
    $('og-url').content = canonical;
    $('og-image').content = socialAbsolute;
    $('article-published').content = record.datePublished || '';
    $('article-modified').content = record.dateModified || record.datePublished || '';
    $('twitter-title').content = view.title || '';
    $('twitter-description').content = view.description || '';
    $('twitter-image').content = socialAbsolute;

    const schema = {
      '@context': 'https://schema.org',
      '@type': 'NewsArticle',
      headline: view.title,
      description: view.description,
      datePublished: record.datePublished,
      dateModified: record.dateModified || record.datePublished,
      inLanguage: locale,
      mainEntityOfPage: canonical,
      image: [socialAbsolute],
      articleSection: view.category || record.categorySlug,
      keywords: view.tags || [],
      author: { '@type': 'Person', name: UI[locale].author },
      publisher: {
        '@type': 'NewsMediaOrganization', name: UI[locale].site, url: PUBLIC_ORIGIN + '/',
        logo: { '@type': 'ImageObject', url: PUBLIC_ORIGIN + '/assets/brand/mikhbar/06-web-ready/icon/mikhbar-app-icon-512.png' }
      }
    };
    $('article-schema').textContent = JSON.stringify(schema);
  }

  function applyChrome(locale, record) {
    const ui = UI[locale];
    document.documentElement.lang = locale;
    document.documentElement.dir = ui.dir;
    document.body.className = `rt-locale-${locale}`;
    const root = sourceRoot();
    const home = `${root}/${locale}/`;
    $('brand-name').textContent = ui.site;
    $('brand-link').href = home;
    $('brand-link').setAttribute('aria-label', ui.site);
    $('nav-home').textContent = ui.home; $('nav-home').href = home;
    $('nav-latest').textContent = ui.latest; $('nav-latest').href = `${home}#latest`;
    $('nav-sections').textContent = ui.sections; $('nav-sections').href = `${home}#sections`;
    $('nav-top').textContent = ui.top; $('nav-top').href = `${home}#top-stories`;
    $('nav-newsletter').textContent = ui.newsletter; $('nav-newsletter').href = `${home}#newsletter`;
    $('nav-about').textContent = ui.about; $('nav-about').href = `${root}/about/`;
    $('nav-lang').textContent = ui.lang;
    const other = locale === 'ar' ? 'en' : 'ar';
    $('nav-lang').href = sourcePath(record.urls && record.urls[other] || `/${other}/`);
    $('author-name').textContent = ui.author;
    $('author-role').textContent = ui.role;
    $('author-link').href = `${root}/authors/radwan-abdulhadi/`;
    $('footer-brand').textContent = ui.site;
    $('footer-copy-brand').textContent = ui.site;
    $('footer-description').textContent = ui.footerDesc;
    $('footer-publication-title').textContent = ui.publication;
    $('footer-about').textContent = ui.about; $('footer-about').href = `${root}/about/`;
    $('footer-editorial').textContent = ui.editorial; $('footer-editorial').href = `${root}/editorial-policy/`;
    $('footer-trust-title').textContent = ui.trust;
    $('footer-corrections').textContent = ui.corrections; $('footer-corrections').href = `${root}/corrections/`;
    $('footer-ai').textContent = ui.ai; $('footer-ai').href = `${root}/ai-policy/`;
    $('source-note').textContent = ui.sourceNote;
    const year = document.querySelector('[data-year]');
    if (year) year.textContent = String(new Date().getFullYear());
  }

  function renderArticle(record, locale, routePath) {
    const view = record.locales && record.locales[locale];
    if (!view) throw new Error(`Missing ${locale} edition`);
    const ui = UI[locale];
    applyChrome(locale, record);
    setMeta(record, view, locale, routePath);

    $('category-label').textContent = view.category || record.categorySlug || '';
    $('article-title').textContent = view.title || '';
    $('article-deck').textContent = view.deck || '';
    $('article-dates').textContent = `${ui.published}: ${view.dateLabel || ''} · ${ui.updated}: ${view.modifiedLabel || view.dateLabel || ''} · ${view.readMinutes || 3} ${ui.read}`;

    clear($('breadcrumbs'));
    const home = document.createElement('a'); home.href = `${sourceRoot()}/${locale}/`; home.textContent = ui.site;
    const sep1 = document.createElement('span'); sep1.textContent = '›';
    const cat = document.createElement('a'); cat.href = `${sourceRoot()}/${locale}/${record.categorySlug}/`; cat.textContent = view.category || record.categorySlug || '';
    const sep2 = document.createElement('span'); sep2.textContent = '›';
    const current = document.createElement('span'); current.textContent = view.title || '';
    $('breadcrumbs').append(home, sep1, cat, sep2, current);
    $('breadcrumbs').setAttribute('aria-label', ui.breadcrumb);

    const images = record.images || {};
    const hero = assetPath(images.hero || images.card || images.social || '');
    if (hero) {
      $('hero-image').src = hero;
      $('hero-image').alt = localized(images.alt, locale, view.title || '');
      $('article-media').hidden = false;
    } else $('article-media').hidden = true;
    const credit = String(images.credit || '').trim();
    if (credit) {
      $('image-credit').hidden = false;
      $('image-credit').textContent = `${locale === 'ar' ? 'الصورة: ' : 'Image: '}${credit}`;
    } else $('image-credit').hidden = true;

    $('summary-title').textContent = ui.summary;
    clear($('summary-list'));
    for (const bullet of (view.summaryBullets || [])) {
      const li = document.createElement('li'); li.textContent = String(bullet); $('summary-list').append(li);
    }

    const body = $('article-body'); clear(body);
    const sections = Array.isArray(view.sections) ? view.sections : [];
    const inlineImages = Array.isArray(images.inline) ? images.inline : [];
    const slots = inlineSlots(sections.length, inlineImages.length);
    sections.forEach((section, sectionIndex) => {
      const h2 = document.createElement('h2'); h2.textContent = String(section.heading || ''); body.append(h2);
      for (const paragraph of (section.paragraphs || [])) {
        const p = document.createElement('p'); appendLinkedText(p, paragraph); body.append(p);
      }
      for (const imageIndex of (slots.get(sectionIndex) || [])) {
        const figure = renderInlineFigure(inlineImages[imageIndex], locale); if (figure) body.append(figure);
      }
    });

    const sourcesTitle = document.createElement('h2'); sourcesTitle.textContent = ui.sources; body.append(sourcesTitle);
    const sourceList = document.createElement('ul'); sourceList.className = 'rt-source-list';
    for (const source of (record.sources || [])) {
      const url = String(source.url || ''); if (!/^https?:\/\//i.test(url)) continue;
      const li = document.createElement('li');
      const a = document.createElement('a'); a.href = url; a.target = '_blank'; a.rel = 'nofollow noopener noreferrer'; a.textContent = String(source.name || new URL(url).hostname);
      li.append(a);
      if (source.title) { const small = document.createElement('small'); small.textContent = String(source.title); li.append(small); }
      sourceList.append(li);
    }
    body.append(sourceList);

    clear($('article-tags'));
    for (const tag of (view.tags || []).slice(0, 8)) { const span = document.createElement('span'); span.textContent = String(tag); $('article-tags').append(span); }

    $('article-loading').hidden = true;
    $('article-error').hidden = true;
    $('article-content').hidden = false;
    $('article-shell').setAttribute('aria-busy', 'false');
  }

  function showError(locale, error) {
    const ui = UI[locale] || UI.ar;
    console.error('Mikhbar dynamic article error:', error);
    document.documentElement.lang = locale;
    document.documentElement.dir = ui.dir;
    $('article-loading').hidden = true;
    $('article-content').hidden = true;
    $('article-error').hidden = false;
    $('article-error-title').textContent = ui.errorTitle;
    $('article-error-message').textContent = ui.errorMessage;
    $('article-shell').setAttribute('aria-busy', 'false');
    $('meta-robots').content = 'noindex,follow';
  }

  async function boot() {
    const path = requestedPath();
    const locale = localeFromPath(path);
    $('article-loading').textContent = UI[locale].loading;
    try {
      const resolved = await resolveArticle(path, locale);
      const record = await getJson(resolved.contentUrl);
      renderArticle(record, locale, path);
    } catch (error) {
      showError(locale, error);
    }
  }

  boot();
})();
