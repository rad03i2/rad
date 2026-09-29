# Mikhbar External Scheduler

This Worker wakes the GitHub publisher every five minutes. GitHub remains the source of truth for the publication cadence: `publisher_scheduler.py` prepares during the cooldown and publishes only when the configured 20-minute gap is due.

## Required secrets

The deployment workflow expects these GitHub Actions repository secrets:

- `CLOUDFLARE_API_TOKEN` — Cloudflare API token with Workers Scripts edit permission for the target account.
- `CLOUDFLARE_ACCOUNT_ID` — Cloudflare account ID.
- `RDWAN_SCHEDULER_GITHUB_TOKEN` — fine-grained GitHub token limited to repository `rad03i2/rad` with **Actions: Read and write**. It is installed into the Worker as the `GITHUB_TOKEN` Worker secret and is never committed.
- `RDWAN_SCHEDULER_MANUAL_KEY` — a long random value protecting the optional `/trigger` endpoint.

## Deployment

Run the GitHub Actions workflow **Deploy Mikhbar External Scheduler** after the required secrets exist. Updates to this scheduler also deploy automatically from `main`. The workflow tests the Worker, installs its secrets, attaches the cron trigger from `wrangler.toml`, verifies health, and tests an authenticated publisher dispatch. The manual trigger key is optional.

## Schedule

Cloudflare wakes the publisher every five minutes using:

```text
*/5 * * * *
```

The Worker calls GitHub `workflow_dispatch` for `.github/workflows/forum-collector.yml` on `main`. It checks both the primary and backup publishers before dispatching, and skips the wakeup when either is active. The repository publisher enforces a minimum 20-minute gap and a shared concurrency group. Publication normally follows the due boundary on the next wakeup, plus GitHub runner and deployment time; cron is not a guarantee of exact-to-the-second delivery. Drafts still must pass verification and quality checks.

## Health

After deployment, `GET /health` returns the scheduler target, wakeup cadence and 20-minute publication minimum. It reports `ok: false` if the dispatch token is missing. `POST /trigger` is available only with `Authorization: Bearer <RDWAN_SCHEDULER_MANUAL_KEY>`. GitHub API failures reject the scheduled event and appear in Cloudflare logs.
