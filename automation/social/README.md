# Mikhbar Facebook publishing

The active workflow is **Mikhbar Social Automation** in `.github/workflows/mikhbar-social.yml`.
After a successful **Mikhbar 20-Minute Publisher** run, it shares the latest Arabic article to the configured Facebook Page.
A manual workflow run uses `mode=live` to publish; `dry-run` runs the tests without posting.

## Connection

GitHub Actions repository secrets:

- `FACEBOOK_PAGE_ID`: the Mikhbar Facebook Page ID.
- `FACEBOOK_PAGE_ACCESS_TOKEN`: a valid token for that Page. The workflow also supports a User token and resolves its Page token through `/me/accounts`.

User-token permissions required by the existing adapter are `pages_show_list`, `pages_read_engagement`, and `pages_manage_posts`.
The workflow verifies the Page ID before publishing. Keep all token values in GitHub Secrets.

Facebook error `190 / 463` means the session token has expired. Renew the authorized Facebook connection, replace `FACEBOOK_PAGE_ACCESS_TOKEN`, then run the workflow with `mode=live`.
A successful GitHub publisher run does not imply that Facebook accepted the social post.

## Article links and state

Shares point to `https://mikhbar.website/ar/...`.
Legacy `/forum/ar/...` and `rdwan.dev` article URLs are converted to the current canonical host and path.
UTM tags exist only on outbound Facebook links. External article hosts are rejected.

`automation/social/state/facebook.json` records successful Facebook story IDs and post IDs.
The duplicate check runs before Facebook authentication, so a previously shared article makes no Graph API calls.
Only the social state file is committed by this workflow; website article state is managed by the website publisher.

## Verification

```sh
python -m unittest discover -s automation/social/tests -v
```

The tests cover canonical links, duplicate suppression, Page identity validation, and rejection of external URLs.
The separate `pipeline.py` Metricool adapter and `config/platform_rules.json` are available for future multi-network distribution; they are not the active Facebook workflow.
