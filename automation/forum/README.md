# RDWAN Tech Automation — Phase 1

This branch contains the safe collection pipeline for `rdwan.dev/forum/`.

## Current mode

- `publishingEnabled: false`
- `dryRun: true`
- No article HTML is generated.
- No public forum files are modified.
- The collector only writes automation state on the `forum-automation` branch.

## Pipeline

1. Fetch RSS/Atom feeds from configured sources.
2. Normalize URLs, titles, summaries and dates.
3. Reject blocked or stale items.
4. Classify into the fixed RDWAN Tech taxonomy.
5. Assign source confidence and importance score.
6. Deduplicate by canonical URL and title similarity.
7. Store new items in `state/queue.json`.
8. Store publish-eligible review candidates in `state/candidates.json`.
9. Write health metrics and source errors to `state/run_report.json`.

## Important files

- `config/sources.json` — source registry and trust level.
- `config/categories.json` — fixed taxonomy and classifier keywords.
- `config/blocked_domains.json` — hard block list.
- `config/settings.json` — thresholds and safety switches.
- `state/queue.json` — incoming stories for review.
- `state/seen.json` — deduplication registry.
- `state/candidates.json` — high-confidence candidates produced after a run.
- `state/run_report.json` — source health and pipeline metrics.

## Local run

```bash
python -m pip install -r automation/forum/requirements.txt
python -m unittest discover -s automation/forum/tests
python automation/forum/run.py --dry-run
```

## Safety switches

Publishing cannot happen unless both conditions are changed intentionally:

```json
"publishingEnabled": true,
"dryRun": false
```

Phase 1 does not include a publisher module, so changing those values alone still cannot publish articles.

## Next phase

After the queue has collected enough real stories, review source quality, duplication rate and classification accuracy. Then add fact extraction, multi-source corroboration, article generation and the quality gate on top of this collector.
