# RDWAN Tech External Scheduler

This Worker wakes the GitHub publisher every five minutes. GitHub remains the source of truth for the publication cadence: `publisher_scheduler.py` prepares during the cooldown and publishes only when the configured 20-minute gap is due.

## Required secrets

The deployment workflow expects these GitHub Actions repository secrets:

- `CLOUDFLARE_API_TOKEN` — Cloudflare API token with Workers Scripts edit permission for the target account.
- `CLOUDFLARE_ACCOUNT_ID` — Cloudflare account ID.
- `RDWAN_SCHEDULER_GITHUB_TOKEN` — fine-grained GitHub token limited to repository `rad03i2/rad` with **Actions: Read and write**. It is installed into the Worker as the `GITHUB_TOKEN` Worker secret and is never committed.
- `RDWAN_SCHEDULER_MANUAL_KEY` — a long random value protecting the optional `/trigger` endpoint.

## Deployment

Run the GitHub Actions workflow **Deploy RDWAN Tech External Scheduler** after the four secrets exist. The workflow deploys the Worker, installs its secrets, and attaches the cron trigger from `wrangler.toml`.

## Schedule

Cloudflare wakes the publisher every five minutes using:

```text
*/5 * * * *
```

The Worker calls GitHub `workflow_dispatch` for `.github/workflows/forum-collector.yml` on `main`. Frequent wakeups do not create duplicate posts because the repository publisher enforces the 20-minute publication boundary and shared concurrency group.

## Health

After deployment, `GET /health` returns the scheduler target and cadence. `POST /trigger` is available only with `Authorization: Bearer <RDWAN_SCHEDULER_MANUAL_KEY>`.
