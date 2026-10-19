import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { buildArticleContexts } from "../scripts/build-article-context.mjs";
import { articleDiscoveryHtml, prepareArticleDiscovery } from "../src/index.js";
import { articleContextPath, renderDynamicArticle } from "../src/article.js";

test("build contexts preserve existing bilingual discovery HTML and SSR avoids global indexes", async () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "mikhbar-context-"));
  const original = globalThis.HTMLRewriter;
  try {
    const routes = {};
    const expected = new Map();
    for (const locale of ["ar", "en"]) {
      const posts = [0, 1, 2].map(i => ({
        id: `${locale}-${i}`, locale, categorySlug: i === 2 ? "apps" : "ai",
        url: `/forum/${locale}/${i === 2 ? "apps" : "ai"}/story-${i}/`,
        title: `OpenAI <script>story ${i}</script>`, excerpt: "A real excerpt",
        entities: ["OpenAI"], tags: ["Coding agents"], date: `2026-10-${19-i}T00:00:00Z`,
        entityHubs: [{ name: "OpenAI", url: `/${locale}/entities/openai/` }],
      }));
      fs.writeFileSync(path.join(root, `posts-${locale}.json`), JSON.stringify({ posts }));
      const prepared = prepareArticleDiscovery(posts);
      for (const post of posts) {
        const route = post.url.slice(6);
        assert.equal(prepared(route), articleDiscoveryHtml(posts, route));
        expected.set(route, articleDiscoveryHtml(posts, route));
        routes[post.url] = { content: `/forum/content/${post.id}.json` };
        fs.mkdirSync(path.join(root, "content"), { recursive: true });
        fs.writeFileSync(path.join(root, "content", `${post.id}.json`), JSON.stringify({
          id: post.id, categorySlug: post.categorySlug,
          urls: { [locale]: route }, locales: { [locale]: { title: post.title, sections: [] } },
        }));
      }
    }
    fs.writeFileSync(path.join(root, "article-map.json"), JSON.stringify({ routes }));
    assert.equal(buildArticleContexts(root), 6);
    for (const [route, html] of expected) {
      const context = JSON.parse(fs.readFileSync(path.join(root, articleContextPath(route))));
      assert.equal(context.discoveryHtml, html);
      assert.ok(html.includes("&lt;script&gt;"));
      assert.ok(!html.includes("<script>story"));
      assert.ok(html.includes('data-related-strategy="semantic"'));
      assert.ok(html.includes('data-article-entity-hub="true"'));
    }
    const fetched = [];
    const handlers = new Map();
    globalThis.HTMLRewriter = class {
      on(selector, handler) { handlers.set(selector, handler); return this; }
      transform(response) { return response; }
    };
    const env = { ASSETS: { async fetch(request) {
      const pathname = new URL(request.url).pathname;
      fetched.push(pathname);
      assert.ok(!/posts-(ar|en)\.json|article-map\.json/.test(pathname));
      if (pathname === "/article/") return new Response("<main>Shared template</main>");
      const file = path.join(root, pathname);
      return fs.existsSync(file) ? new Response(fs.readFileSync(file)) : new Response("missing", { status: 404 });
    } } };
    const route = "/ar/ai/story-0/";
    const response = await renderDynamicArticle(new Request("https://mikhbar.website" + route), env, route);
    assert.equal(response.status, 200);
    assert.equal(response.headers.get("X-Mikhbar-Discovery"), "build-context-v1");
    assert.deepEqual(fetched, [articleContextPath(route), "/content/ar-0.json", "/article/"]);
    let renderedBody = "";
    handlers.get("#article-body").element({ setInnerContent(html) { renderedBody = html; } });
    assert.ok(renderedBody.endsWith(expected.get(route)));
    fetched.length = 0;
    assert.equal(await renderDynamicArticle(new Request("https://mikhbar.website/ar/ai/missing/"), env, "/ar/ai/missing/"), null);
    assert.deepEqual(fetched, [articleContextPath("/ar/ai/missing/")]);
  } finally {
    globalThis.HTMLRewriter = original;
    fs.rmSync(root, { recursive: true, force: true });
  }
});
