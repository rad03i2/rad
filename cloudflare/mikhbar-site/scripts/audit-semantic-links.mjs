import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { selectRelatedPosts } from "../src/index.js";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "../../..");
const FORUM = path.join(ROOT, "forum");

function loadPosts(locale) {
  const file = path.join(FORUM, `posts-${locale}.json`);
  const payload = JSON.parse(fs.readFileSync(file, "utf8"));
  return Array.isArray(payload) ? payload : (Array.isArray(payload?.posts) ? payload.posts : []);
}

function publicRoute(value) {
  let route = String(value || "").trim();
  if (route.startsWith("/forum/")) route = route.slice("/forum".length);
  if (!route.startsWith("/")) route = "/" + route;
  return route;
}

let articles = 0;
let relatedLinks = 0;
let semanticLinks = 0;
let semanticArticles = 0;
let crossCategoryLinks = 0;
let duplicates = 0;
let selfLinks = 0;
let localeLeaks = 0;

for (const locale of ["ar", "en"]) {
  const posts = loadPosts(locale);
  for (const post of posts) {
    const route = publicRoute(post?.url);
    if (!/^\/(ar|en)\/[a-z0-9-]+\/[^/]+\/$/i.test(route)) continue;
    articles += 1;
    const related = selectRelatedPosts(posts, route, 4);
    const seen = new Set();
    let hasSemantic = false;

    for (const candidate of related) {
      relatedLinks += 1;
      const candidateRoute = publicRoute(candidate?.url);
      if (candidateRoute === route) selfLinks += 1;
      if (seen.has(candidateRoute)) duplicates += 1;
      seen.add(candidateRoute);
      if (String(candidate?.locale || locale).toLowerCase() !== locale) localeLeaks += 1;

      if (Number(candidate?._semanticScore || 0) > 0) {
        semanticLinks += 1;
        hasSemantic = true;
        if (String(candidate?.categorySlug || "") !== String(post?.categorySlug || "")) {
          crossCategoryLinks += 1;
        }
      }
    }
    if (hasSemantic) semanticArticles += 1;
  }
}

const coverage = articles ? semanticArticles / articles : 0;
const averageSemantic = articles ? semanticLinks / articles : 0;

console.log(
  "Mikhbar semantic link audit: " +
  `articles=${articles} related_links=${relatedLinks} semantic_links=${semanticLinks} ` +
  `semantic_articles=${semanticArticles} coverage=${(coverage * 100).toFixed(1)}% ` +
  `cross_category=${crossCategoryLinks} avg_semantic_per_article=${averageSemantic.toFixed(2)} ` +
  `self=${selfLinks} duplicates=${duplicates} locale_leaks=${localeLeaks}`
);

if (!articles || !relatedLinks || !semanticLinks || !crossCategoryLinks || selfLinks || duplicates || localeLeaks) {
  process.exitCode = 1;
}
