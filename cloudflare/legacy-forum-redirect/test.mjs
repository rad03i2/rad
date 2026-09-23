import assert from "node:assert/strict";
import { legacyForumTarget } from "./src/index.js";

const cases = [
  ["https://rdwan.dev/forum", "https://mikhbar.website/"],
  ["https://rdwan.dev/forum?utm_source=google", "https://mikhbar.website/?utm_source=google"],
  ["https://rdwan.dev/forum/", "https://mikhbar.website/"],
  ["https://rdwan.dev/forum/ar/ai/example/", "https://mikhbar.website/ar/ai/example/"],
  ["https://rdwan.dev/forum/en/security/example/?ref=old", "https://mikhbar.website/en/security/example/?ref=old"],
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

console.log("Legacy forum redirect mapping tests passed.");
