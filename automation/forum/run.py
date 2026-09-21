from __future__ import annotations

import argparse
from datetime import datetime, timezone

from collector import collect
from common import CONFIG, STATE, load_json, now_iso, save_json
from deduplicator import deduplicate
from verifier import refresh_queue_verification, verify_and_score


def main() -> int:
    parser = argparse.ArgumentParser(description="Mikhbar collection pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Collect and evaluate only; never publish")
    args = parser.parse_args()

    settings = load_json(CONFIG / "settings.json", {})
    dry_run = True if args.dry_run else bool(settings.get("dryRun", True))
    publishing_enabled = bool(settings.get("publishingEnabled", False)) and not dry_run

    queue_doc = load_json(STATE / "queue.json", {"updated_at": None, "items": []})
    seen = load_json(STATE / "seen.json", {"urls": {}, "titles": {}})
    queue_items = list(queue_doc.get("items", []))

    started = now_iso()
    stories, collection_report = collect(settings)
    verified, rejected = verify_and_score(stories, settings)
    fresh, duplicates, seen = deduplicate(
        verified,
        queue_items,
        seen,
        float(settings.get("duplicateTitleThreshold", 0.90)),
    )

    queue_items.extend(fresh)
    queue_items = refresh_queue_verification(queue_items, settings)
    queue_items.sort(
        key=lambda item: (item.get("score", 0), item.get("published_at") or item.get("discovered_at") or ""),
        reverse=True,
    )
    max_queue = int(settings.get("maxQueueItems", 500))
    queue_items = queue_items[:max_queue]

    finished = now_iso()
    queue_doc = {"updated_at": finished, "items": queue_items}
    save_json(STATE / "queue.json", queue_doc)
    save_json(STATE / "seen.json", seen)

    candidates = [
        item for item in queue_items
        if item.get("verification", {}).get("publish_eligible")
        and item.get("status") not in {"published", "quality_rejected"}
    ]
    candidates.sort(key=lambda x: x.get("score", 0), reverse=True)
    save_json(STATE / "candidates.json", {
        "updated_at": finished,
        "publishing_enabled": publishing_enabled,
        "dry_run": dry_run,
        "items": candidates[:100],
    })

    status = "ok"
    if collection_report["sources_ok"] == 0:
        status = "degraded"
    elif collection_report["sources_failed"]:
        status = "partial"

    report = {
        "status": status,
        "mode": "dry-run" if dry_run else "publishing-disabled" if not publishing_enabled else "publishing",
        "started_at": started,
        "finished_at": finished,
        "sources_ok": collection_report["sources_ok"],
        "sources_failed": collection_report["sources_failed"],
        "fetched": collection_report["fetched"],
        "verified": len(verified),
        "accepted_new": len(fresh),
        "duplicates": duplicates,
        "rejected": rejected,
        "queue_size": len(queue_items),
        "publish_eligible": len(candidates),
        "publishing_enabled": publishing_enabled,
        "errors": collection_report["errors"],
    }
    save_json(STATE / "run_report.json", report)

    print("Mikhbar collector")
    print(f"status={status} fetched={report['fetched']} new={len(fresh)} duplicates={duplicates} rejected={rejected}")
    print(f"queue={len(queue_items)} publish_eligible={len(candidates)} mode={report['mode']}")
    if collection_report["errors"]:
        print(f"source_errors={len(collection_report['errors'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
