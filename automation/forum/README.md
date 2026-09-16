# RDWAN Tech Automation

This directory powers the automated RDWAN Tech publishing pipeline.

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

- collector.py — fetch RSS/Atom sources
- verifier.py — trust, freshness and category scoring
- deduplicator.py — URL/title duplicate filtering
- trend.py — trend score and corroboration
- writer.py — source extraction + GitHub Models Arabic writer
- publisher.py — hourly article rendering and SEO/index updates
- run.py — collection pipeline

The production workflow runs from GitHub Actions and uses the built-in GITHUB_TOKEN for both repository writes and GitHub Models inference.
