import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { prepareArticleDiscovery } from "../src/index.js";
import { articleContextPath } from "../src/article.js";

export function buildArticleContexts(root) {
  const map = JSON.parse(fs.readFileSync(path.join(root, "article-map.json"), "utf8"));
  const prepared = new Map();
  for (const locale of ["ar", "en"]) {
    const payload = JSON.parse(fs.readFileSync(path.join(root, `posts-${locale}.json`), "utf8"));
    prepared.set(locale, prepareArticleDiscovery(Array.isArray(payload) ? payload : payload.posts));
  }
  let count = 0;
  let largest = 0;
  for (const [rawRoute, entry] of Object.entries(map.routes)) {
    const route = rawRoute.startsWith("/forum/") ? rawRoute.slice(6) : rawRoute;
    const contextPath = articleContextPath(route);
    if (!contextPath) throw new Error(`Invalid article route: ${route}`);
    const content = entry.content.startsWith("/forum/") ? entry.content.slice(6) : entry.content;
    if (!content.startsWith("/content/") || !fs.existsSync(path.join(root, content))) {
      throw new Error(`Missing article record: ${content}`);
    }
    const locale = route.split("/")[1];
    const document = JSON.stringify({
      schemaVersion: 1, route, content,
      discoveryHtml: prepared.get(locale)(route),
    });
    const bytes = Buffer.byteLength(document);
    if (bytes > 128 * 1024) throw new Error(`Article context too large: ${route}`);
    const target = path.resolve(root, "." + contextPath);
    const directory = path.resolve(root, "_article-context") + path.sep;
    if (!target.startsWith(directory)) throw new Error(`Unsafe article route: ${route}`);
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.writeFileSync(target, document + "\n");
    count += 1;
    largest = Math.max(largest, bytes);
  }
  console.log(`Mikhbar article contexts: routes=${count} max_bytes=${largest}`);
  return count;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  buildArticleContexts(path.resolve(process.argv[2] || "dist/mikhbar"));
}
