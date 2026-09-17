const OWNER = "rad03i2";
const REPO = "rad";
const WORKFLOW = "forum-collector.yml";
const WORKFLOW_PATH = ".github/workflows/forum-collector.yml";
const BRANCH = "main";
const CRON = "*/5 * * * *";

async function triggerPublisher(env) {
  if (!env.GITHUB_TOKEN) {
    throw new Error("Missing GITHUB_TOKEN secret");
  }

  const endpoint = `https://api.github.com/repos/${OWNER}/${REPO}/actions/workflows/${WORKFLOW}/dispatches`;
  const response = await fetch(endpoint, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${env.GITHUB_TOKEN}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "User-Agent": "RDWAN-Tech-External-Scheduler/1.0",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ ref: BRANCH }),
  });

  if (response.status === 204) {
    return {
      ok: true,
      status: response.status,
      repository: `${OWNER}/${REPO}`,
      workflow: WORKFLOW_PATH,
      branch: BRANCH,
      at: new Date().toISOString(),
    };
  }

  const body = await response.text();
  throw new Error(`GitHub dispatch failed (${response.status}): ${body.slice(0, 500)}`);
}

export default {
  async scheduled(_controller, env, ctx) {
    ctx.waitUntil(
      triggerPublisher(env).then(
        (result) => console.log("RDWAN Tech wakeup dispatched", result),
        (error) => console.error("RDWAN Tech wakeup failed", error),
      ),
    );
  },

  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/health") {
      return Response.json({
        ok: true,
        service: "rdwan-tech-publisher-wakeup",
        role: "wakeup-only",
        repository: `${OWNER}/${REPO}`,
        workflow: WORKFLOW_PATH,
        branch: BRANCH,
        schedule: CRON,
        publication_cadence_source: "GitHub publisher scheduler",
      });
    }

    if (url.pathname === "/trigger") {
      if (request.method !== "POST") {
        return new Response("Method Not Allowed", { status: 405, headers: { Allow: "POST" } });
      }

      const expected = env.MANUAL_TRIGGER_KEY || "";
      const supplied = request.headers.get("authorization")?.replace(/^Bearer\s+/i, "") || "";
      if (!expected || supplied !== expected) {
        return new Response("Unauthorized", { status: 401 });
      }

      try {
        return Response.json(await triggerPublisher(env));
      } catch (error) {
        return Response.json({ ok: false, error: String(error) }, { status: 502 });
      }
    }

    return new Response("RDWAN Tech scheduler is running. Use /health for status.", {
      status: 200,
      headers: { "content-type": "text/plain; charset=utf-8" },
    });
  },
};
