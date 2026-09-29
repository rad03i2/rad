const OWNER = "rad03i2";
const REPO = "rad";
const WORKFLOW = "forum-collector.yml";
const WORKFLOW_PATH = ".github/workflows/forum-collector.yml";
const BRANCH = "main";
const CRON = "*/5 * * * *";
const ACTIVE_STATUSES = new Set(["queued", "in_progress", "waiting", "pending", "requested"]);

async function triggerPublisher(env) {
  if (!env.GITHUB_TOKEN) {
    throw new Error("Missing GITHUB_TOKEN secret");
  }

  const headers = {
      Authorization: `Bearer ${env.GITHUB_TOKEN}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "User-Agent": "RDWAN-Tech-External-Scheduler/1.0",
      "Content-Type": "application/json",
  };
  const base = `https://api.github.com/repos/${OWNER}/${REPO}/actions/workflows`;
  for (const workflow of [WORKFLOW, "forum-publisher-backup.yml"]) {
    const runs = await fetch(`${base}/${workflow}/runs?branch=${BRANCH}&per_page=100`, {
      method: "GET", headers, signal: AbortSignal.timeout(15000),
    });
    if (!runs.ok) {
      throw new Error(`GitHub publisher status check failed (${runs.status})`);
    }
    const payload = await runs.json();
    if ((payload.workflow_runs || []).some((run) => ACTIVE_STATUSES.has(run.status))) {
      return { ok: true, skipped: true, reason: "publisher_already_active", workflow };
    }
  }

  const response = await fetch(`${base}/${WORKFLOW}/dispatches`, {
    method: "POST", headers, signal: AbortSignal.timeout(15000),
    body: JSON.stringify({ ref: BRANCH, inputs: { trigger: "external-20m" } }),
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
        (result) => console.log("Mikhbar wakeup dispatched", result),
        (error) => {
          console.error("Mikhbar wakeup failed", error);
          throw error; // Mark the scheduled event failed instead of hiding it.
        },
      ),
    );
  },

  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/health") {
      return Response.json({
        ok: Boolean(env.GITHUB_TOKEN),
        service: "mikhbar-publisher-wakeup",
        role: "wakeup-only",
        repository: `${OWNER}/${REPO}`,
        workflow: WORKFLOW_PATH,
        branch: BRANCH,
        schedule: CRON,
        publication_minimum_minutes: 20,
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

    return new Response("Mikhbar scheduler is running. Use /health for status.", {
      status: 200,
      headers: { "content-type": "text/plain; charset=utf-8" },
    });
  },
};
