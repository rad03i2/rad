import assert from "node:assert/strict";
import worker, { legacyForumTarget } from "./src/index.js";

const cases = [
  ["https://rdwan.dev/forum", "https://mikhbar.website/ar/"],
  ["https://rdwan.dev/forum?utm_source=google", "https://mikhbar.website/ar/?utm_source=google"],
  ["https://rdwan.dev/forum/", "https://mikhbar.website/ar/"],
  ["https://rdwan.dev/forum/ar/ai/example/", "https://mikhbar.website/ar/ai/example/"],
  ["https://rdwan.dev/forum/en/security/example/?ref=old", "https://mikhbar.website/en/security/example/?ref=old"],
  ["https://www.rdwan.dev/forum/", "https://mikhbar.website/ar/"],
  ["https://www.rdwan.dev/forum/en/ai/example/", "https://mikhbar.website/en/ai/example/"],
];

for (const [source, expected] of cases) {
  assert.equal(legacyForumTarget(source), expected, source);
}

for (const source of [
  "https://rdwan.dev/",
  "https://rdwan.dev/forumanything",
  "https://rdwan.dev/portfolio/",
  "https://rdwan.dev/assets/forum/logo.png",
]) {
  assert.equal(legacyForumTarget(source), null, source);
}

const response = await worker.fetch(new Request("https://rdwan.dev/forum/en/"));
assert.equal(response.status, 308);
assert.equal(response.headers.get("location"), "https://mikhbar.website/en/");
assert.equal(response.headers.get("x-mikhbar-migration"), "legacy-forum");
assert.equal(response.headers.get("x-robots-tag"), null);

console.log("Legacy forum redirect mapping tests passed.");
