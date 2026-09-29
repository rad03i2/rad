import test from 'node:test';
import assert from 'node:assert/strict';
import worker from '../src/index.js';

const env = { GITHUB_TOKEN: 'test-only', MANUAL_TRIGGER_KEY: 'test-key' };
const trigger = () => new Request('https://scheduler.example/trigger', {
  method: 'POST', headers: { authorization: 'Bearer test-key' },
});

test('checks primary and backup before an authenticated main dispatch', async () => {
  const original = globalThis.fetch;
  const calls = [];
  globalThis.fetch = async (url, options) => {
    calls.push({ url, options });
    return options.method === 'POST' ? new Response(null, { status: 204 })
      : Response.json({ workflow_runs: [] });
  };
  try {
    const response = await worker.fetch(trigger(), env);
    assert.equal(response.status, 200);
    assert.equal((await response.json()).status, 204);
    assert.equal(calls.length, 3);
    assert.equal(calls[0].options.method, 'GET');
    assert.match(calls[1].url, /forum-publisher-backup.yml\/runs/);
    assert.deepEqual(JSON.parse(calls[2].options.body), {
      ref: 'main', inputs: { trigger: 'external-20m' },
    });
  } finally { globalThis.fetch = original; }
});

test('skips dispatch when the backup publisher is active', async () => {
  const original = globalThis.fetch;
  let calls = 0;
  globalThis.fetch = async () => Response.json({
    workflow_runs: ++calls === 2 ? [{ status: 'in_progress' }] : [],
  });
  try {
    const response = await worker.fetch(trigger(), env);
    assert.equal((await response.json()).reason, 'publisher_already_active');
    assert.equal(calls, 2);
  } finally { globalThis.fetch = original; }
});

test('rejects scheduled failures so cron monitoring records an error', async () => {
  const original = globalThis.fetch;
  globalThis.fetch = async () => new Response(null, { status: 401 });
  let pending;
  try {
    await worker.scheduled({}, env, { waitUntil: (promise) => { pending = promise; } });
    await assert.rejects(pending, /status check failed \(401\)/);
  } finally { globalThis.fetch = original; }
});

test('health exposes missing token and the distinct wakeup/publication cadences', async () => {
  const response = await worker.fetch(new Request('https://scheduler.example/health'), {});
  const health = await response.json();
  assert.equal(health.ok, false);
  assert.equal(health.schedule, '*/5 * * * *');
  assert.equal(health.publication_minimum_minutes, 20);
});

test('manual trigger cannot run without its configured key', async () => {
  const response = await worker.fetch(trigger(), { GITHUB_TOKEN: 'test-only' });
  assert.equal(response.status, 401);
});
