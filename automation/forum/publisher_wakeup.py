"""Wake the publisher without creating competing publication runs."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "config"
STATE = ROOT / "state"

ACTIVE_STATUSES = {"queued", "in_progress", "waiting", "pending", "requested"}


def load_json(path: Path, default: dict) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def wake(trigger: str, minimum_age_minutes: int) -> int:
    settings = load_json(CONFIG / "settings.json", {})
    if not settings.get("publishingEnabled") or settings.get("dryRun"):
        print("Publication is disabled; no wakeup dispatched.")
        return 0

    history = load_json(STATE / "published.json", {})
    raw = history.get("last_published_at")
    if raw:
        last = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - last.astimezone(timezone.utc)).total_seconds() / 60
        if age < minimum_age_minutes:
            print(f"Latest story age={age:.1f} minutes; no wakeup needed.")
            return 0

    repository = os.environ["GITHUB_REPOSITORY"]
    for workflow in ("forum-collector.yml", "forum-publisher-backup.yml"):
        # gh switches to POST when fields are supplied unless GET is explicit.
        # Keep stderr visible so API/authentication failures appear in job logs.
        result = subprocess.run(
            ["gh", "api", "--method", "GET",
             f"repos/{repository}/actions/workflows/{workflow}/runs",
             "-f", "per_page=100", "-f", "branch=main"],
            stdout=subprocess.PIPE, text=True, check=True, timeout=30,
        )
        runs = json.loads(result.stdout).get("workflow_runs", [])
        if any(run.get("status") in ACTIVE_STATUSES for run in runs):
            print(f"{workflow} is already active; skipping duplicate dispatch.")
            return 0

    body = json.dumps({"ref": "main", "inputs": {"trigger": trigger}})
    subprocess.run(
        ["gh", "api", "--method", "POST",
         f"repos/{repository}/actions/workflows/forum-collector.yml/dispatches",
         "--input", "-"],
        input=body, text=True, check=True, timeout=30,
    )
    print(f"Publisher dispatched successfully: {trigger}.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--trigger", required=True)
    parser.add_argument("--minimum-age-minutes", type=int, default=18)
    args = parser.parse_args()
    raise SystemExit(wake(args.trigger, args.minimum_age_minutes))
