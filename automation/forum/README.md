# RDWAN Tech Automation

This directory powers the automated RDWAN Tech publishing pipeline.

## Publishing model

RDWAN Tech now uses a template-driven static publishing architecture:

1. collect and verify a technology story
2. generate structured Arabic article data
3. save that data under `forum/content/YYYY/MM/*.json`
4. render the public article through the single shared template at `forum/templates/article.html`
5. publish a static, indexable URL under `/forum/<category>/<slug>/`
6. update `posts.json`, RSS, the forum sitemap and Google News sitemap

The JSON content file is the source of truth. The generated HTML page is an SEO-ready build artifact. Changing the shared template does not require editing every article: `rebuild_articles.py` regenerates all structured article pages from their content files.

## Current production target

- collect trusted technology stories
- rank trends and corroborate them
- publish at most one complete Arabic article per hour
- generate SEO metadata and structured data
- update posts.json, RSS, sitemap and Google News sitemap
- keep a publication history to prevent duplicates

## Safety

The hourly publisher refuses to publish if the generated article fails the quality gate or if sources are insufficient. Official sources may stand alone; journalism stories require independent corroboration.

## Core files

- `collector.py` — fetch RSS/Atom sources
- `verifier.py` — trust, freshness and category scoring
- `deduplicator.py` — URL/title duplicate filtering
- `trend.py` — trend score and corroboration
- `writer.py` — source extraction + Copilot CLI Arabic writer
- `publisher.py` — creates structured content and publication metadata
- `renderer.py` — turns a content record into an SEO-ready HTML article using the shared template
- `indexes.py` — generates RSS, sitemap and Google News sitemap
- `rebuild_articles.py` — rebuilds every structured article after template changes
- `run.py` — collection pipeline

## Workflows

- `forum-collector.yml` — hourly collection, writing and publication
- `forum-rebuild.yml` — rebuilds all structured article pages when the shared template or content source files change

The production workflow uses the built-in GitHub token for repository writes and GitHub Copilot CLI requests.
