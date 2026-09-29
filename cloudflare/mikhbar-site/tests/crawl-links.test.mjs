import test from "node:test";
import assert from "node:assert/strict";

import {
  selectChronologicalNeighbors,
  selectRelatedPosts,
} from "../src/index.js";

const posts = [
  { locale: "en", categorySlug: "ai", url: "/en/ai/newest/", title: "Newest", date: "2026-09-30T00:00:00Z" },
  { locale: "en", categorySlug: "ai", url: "/en/ai/middle/", title: "Middle", date: "2026-09-29T00:00:00Z" },
  { locale: "en", categorySlug: "ai", url: "/en/ai/oldest/", title: "Oldest", date: "2026-09-28T00:00:00Z" },
  { locale: "en", categorySlug: "security", url: "/en/security/other/", title: "Other", date: "2026-09-30T00:00:00Z" },
  { locale: "ar", categorySlug: "ai", url: "/ar/ai/arabic/", title: "Arabic", date: "2026-09-30T00:00:00Z" },
];

test("chronological neighbors connect an article to newer and older stories in the same locale/category", () => {
  const neighbors = selectChronologicalNeighbors(posts, "/en/ai/middle/");
  assert.equal(neighbors.newer?.url, "/en/ai/newest/");
  assert.equal(neighbors.older?.url, "/en/ai/oldest/");
});

test("chronological endpoints expose only the available neighbor", () => {
  const newest = selectChronologicalNeighbors(posts, "/en/ai/newest/");
  assert.equal(newest.newer, null);
  assert.equal(newest.older?.url, "/en/ai/middle/");

  const oldest = selectChronologicalNeighbors(posts, "/en/ai/oldest/");
  assert.equal(oldest.newer?.url, "/en/ai/middle/");
  assert.equal(oldest.older, null);
});

test("related stories stay inside the current locale/category and exclude the current article", () => {
  const related = selectRelatedPosts(posts, "/en/ai/middle/", 4);
  assert.deepEqual(
    related.map((post) => post.url),
    ["/en/ai/newest/", "/en/ai/oldest/"],
  );
});
