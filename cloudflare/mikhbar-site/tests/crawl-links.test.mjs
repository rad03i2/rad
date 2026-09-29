import test from "node:test";
import assert from "node:assert/strict";

import {
  selectChronologicalNeighbors,
  selectRelatedPosts,
  semanticRelatedScore,
} from "../src/index.js";
import { isArticlePath } from "../src/article.js";

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


test("category archive paths are reserved from dynamic article routing", () => {
  assert.equal(isArticlePath("/en/ai/archive/"), false);
  assert.equal(isArticlePath("/ar/computers/archive/"), false);
  assert.equal(isArticlePath("/en/ai/real-story-slug/"), true);
});


test("semantic related stories can outrank recency and cross category boundaries on strong entity overlap", () => {
  const semanticPosts = [
    {
      locale: "en",
      categorySlug: "ai",
      url: "/en/ai/current/",
      title: "OpenAI GPT-6 lands in GitHub Copilot",
      date: "2026-09-30T12:00:00Z",
      entities: ["OpenAI", "GitHub Copilot"],
      tags: ["OpenAI", "GPT-6", "Coding Agents"],
    },
    {
      locale: "en",
      categorySlug: "ai",
      url: "/en/ai/generic-new/",
      title: "New AI model benchmark arrives",
      date: "2026-09-30T11:00:00Z",
      entities: ["Benchmark Lab"],
      tags: ["AI", "Models"],
    },
    {
      locale: "en",
      categorySlug: "ai",
      url: "/en/ai/openai-older/",
      title: "OpenAI updates GPT-6 reasoning",
      date: "2026-09-20T00:00:00Z",
      entities: ["OpenAI"],
      tags: ["OpenAI", "GPT-6"],
    },
    {
      locale: "en",
      categorySlug: "apps",
      url: "/en/apps/copilot-tools/",
      title: "GitHub Copilot adds new developer tools",
      date: "2026-09-29T00:00:00Z",
      entities: ["GitHub Copilot"],
      tags: ["GitHub Copilot", "Developer Tools"],
    },
  ];

  const related = selectRelatedPosts(semanticPosts, "/en/ai/current/", 3);
  assert.deepEqual(
    related.map((post) => post.url),
    ["/en/ai/openai-older/", "/en/apps/copilot-tools/", "/en/ai/generic-new/"],
  );
  assert.ok(related[0]._semanticScore > related[1]._semanticScore);
  assert.ok(related[1]._semanticScore > 0);
  assert.equal(related[2]._semanticScore, 0);
});

test("a single generic cross-category tag is not enough to create a semantic link", () => {
  const current = {
    categorySlug: "ai",
    title: "AI platform update",
    entities: [],
    tags: ["Artificial Intelligence"],
  };
  const candidate = {
    categorySlug: "security",
    title: "Security platform update",
    entities: [],
    tags: ["Artificial Intelligence"],
  };
  assert.equal(semanticRelatedScore(current, candidate).score, 0);
});
