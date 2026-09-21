# Mikhbar Social Automation

This directory is a separate social-distribution layer for **مِخبار / Mikhbar**. It does not control or block the website publisher.

## Source of truth

The detector reads only successful website publication state from:

- \`automation/forum/state/published.json\`
- the referenced \`forum/content/YYYY/MM/*.json\` article record

It does **not** scrape the website. A stable article \`id\` is used as \`story_id\`; if a future article lacks an ID, the SHA-256 of its canonical URL is used.

## Pipeline

\`Published story -> detector -> editorial score -> platform selection -> platform-specific copy -> media reference -> schedule/retry -> independent social state\`

Initial networks are Facebook, Instagram, Threads and TikTok. TikTok is intentionally left in \`media_pending\` until the vertical-video stage produces a real video; the system will not fake news footage.

## Safety defaults

- \`dry-run\` is the default mode.
- The GitHub workflow's automatic \`workflow_run\` path is gated behind the repository variable \`MIKHBAR_SOCIAL_ENABLED=true\`.
- Live mode fails closed unless \`METRICOOL_USER_TOKEN\`, \`METRICOOL_USER_ID\`, and \`METRICOOL_BLOG_ID\` are present as secrets/environment variables.
- The dedicated Metricool brand must be **Mikhbar / مِخبار**. Do not reuse another brand's connected account IDs.
- A social failure never changes the website article or website publication history.
- Retries are platform-specific with exponential backoff.
- No API keys, access tokens or passwords are written to logs/state.

## State

The first run creates:

- \`state/queue.json\`
- \`state/published.json\`
- \`state/failed.json\`
- \`state/platform_status.json\`
- \`state/last_run.json\`

## Metricool live adapter

The server-side adapter uses Metricool's scheduler endpoint and keeps the token in GitHub Secrets. The canonical article URL remains clean; UTM parameters exist only on outbound social links.

## Local dry run

\`\`\`bash
python automation/social/pipeline.py --mode dry-run
python -m unittest discover -s automation/social/tests -v
\`\`\`

## Activation checklist

1. Create/select the dedicated Mikhbar brand in Metricool.
2. Connect and verify Facebook, Instagram, Threads and TikTok for that brand.
3. Record the correct Metricool \`userId\` and \`blogId\`.
4. Store the API token and IDs as GitHub Secrets.
5. Run one manual dry run and inspect \`state/last_run.json\`.
6. Run one manual live test per network, one at a time.
7. Only then set \`MIKHBAR_SOCIAL_ENABLED=true\`.
