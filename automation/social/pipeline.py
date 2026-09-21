from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib import error, request
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[2]
SOCIAL_ROOT = ROOT / "automation" / "social"
SOCIAL_STATE = SOCIAL_ROOT / "state"
FORUM_PUBLISHED = ROOT / "automation" / "forum" / "state" / "published.json"
RULES_PATH = SOCIAL_ROOT / "config" / "platform_rules.json"
SITE_BASE = "https://rdwan.dev"
TZ = timezone(timedelta(hours=3))

PLATFORM_TO_METRICOOL = {
    "facebook": "facebook",
    "instagram": "instagram",
    "threads": "threads",
    "tiktok": "tiktok",
}


class SocialConfigError(RuntimeError):
    pass


@dataclass
class ScheduleResult:
    ok: bool
    response: dict[str, Any]
    external_id: str | None = None
    planner_url: str | None = None


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def now_local() -> datetime:
    return datetime.now(TZ)


def parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=TZ)
    except ValueError:
        return None


def canonical_url(content: dict[str, Any], locale: str = "ar") -> str:
    path = str((content.get("urls") or {}).get(locale) or "").strip()
    if path.startswith("http://") or path.startswith("https://"):
        return path.split("?", 1)[0]
    if not path.startswith("/"):
        path = "/" + path
    return SITE_BASE + path.split("?", 1)[0]


def with_utm(url: str, platform: str) -> str:
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query.update({
        "utm_source": platform,
        "utm_medium": "social",
        "utm_campaign": "mikhbar_social",
    })
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def story_id(content: dict[str, Any]) -> str:
    explicit = str(content.get("id") or "").strip()
    if explicit:
        return explicit
    return hashlib.sha256(canonical_url(content).encode("utf-8")).hexdigest()


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def social_score(content: dict[str, Any], published_item: dict[str, Any] | None = None) -> float:
    published_item = published_item or {}
    trend = float(content.get("trendScore") or published_item.get("trend_score") or 0)
    verification = content.get("verification") or {}
    images = content.get("images") or {}
    category = str(content.get("categorySlug") or published_item.get("category") or "").lower()

    score = 35.0 + _clamp(trend, 0, 150) * 0.28
    score += _clamp(float(verification.get("confidence") or 0), 0, 1) * 10
    if verification.get("official"):
        score += 6
    if images.get("social") or images.get("card") or images.get("hero"):
        score += 5
    if not images.get("generatedFallback"):
        score += 2
    if category in {"ai", "security", "mobile", "robotics", "social", "apps"}:
        score += 3
    return round(_clamp(score, 0, 100), 2)


def social_priority(content: dict[str, Any], score: float) -> str:
    explicit = str(content.get("social_priority") or "").lower()
    if explicit in {"breaking", "high", "normal", "low"}:
        return explicit
    if score >= 84:
        return "high"
    if score >= 68:
        return "normal"
    return "low"


def _media_url(content: dict[str, Any]) -> str | None:
    images = content.get("images") or {}
    for key in ("social", "card", "hero"):
        path = str(images.get(key) or "").strip()
        if not path:
            continue
        if path.startswith(("http://", "https://")):
            return path
        if not path.startswith("/"):
            path = "/" + path
        return SITE_BASE + path
    return None


def _category_tag(content: dict[str, Any]) -> str:
    tags = {
        "ai": "#ذكاء_اصطناعي",
        "security": "#أمن_تقني",
        "mobile": "#هواتف",
        "robotics": "#روبوتات",
        "automation": "#أتمتة",
        "apps": "#تطبيقات",
        "computers": "#حواسيب",
        "web": "#ويب",
        "social": "#تواصل_اجتماعي",
    }
    return tags.get(str(content.get("categorySlug") or ""), "#تقنية")


def generate_copy(content: dict[str, Any], platform: str) -> dict[str, str]:
    ar = (content.get("locales") or {}).get("ar") or {}
    title = re.sub(r"\s+", " ", str(ar.get("title") or "خبر تقني جديد")).strip()
    description = re.sub(r"\s+", " ", str(ar.get("description") or ar.get("deck") or "")).strip()
    deck = re.sub(r"\s+", " ", str(ar.get("deck") or description)).strip()
    link = with_utm(canonical_url(content), platform)
    category_tag = _category_tag(content)

    if platform == "facebook":
        text = f"{title}\n\n{description}\n\nاقرأ التفاصيل على مِخبار:\n{link}\n\n#مخبار {category_tag}"
        return {"text": text, "link": link}
    if platform == "instagram":
        text = f"{title}\n\n{description}\n\nالتفاصيل كاملة على مِخبار.\n\n#مخبار #تقنية {category_tag}"
        return {"text": text, "link": link}
    if platform == "threads":
        compact = deck[:360].rstrip()
        text = f"{title}\n\n{compact}\n\n{link}"
        return {"text": text, "link": link}
    if platform == "tiktok":
        hook = title[:95].rstrip(" .،")
        script = (
            f"{hook}. ما الذي حدث؟ {description[:180]} "
            f"لماذا يهم؟ {deck[:160]} التفاصيل على مِخبار."
        )
        caption = f"{title}\n\n#مخبار #تقنية {category_tag}"
        return {"text": caption, "script": script, "link": link}
    raise ValueError(f"Unsupported platform: {platform}")


def select_platforms(content: dict[str, Any], score: float, rules: dict[str, Any]) -> list[str]:
    media = _media_url(content)
    category = str(content.get("categorySlug") or "").lower()
    selected: list[str] = []
    for platform in ("facebook", "instagram", "threads", "tiktok"):
        cfg = (rules.get("platforms") or {}).get(platform) or {}
        if not cfg.get("enabled", True):
            continue
        if score < float(cfg.get("min_score", 101)):
            continue
        if platform in {"instagram", "tiktok"} and not media:
            continue
        if platform == "tiktok":
            allowed = set(cfg.get("preferred_categories") or [])
            if allowed and category not in allowed:
                continue
        selected.append(platform)
    return selected


def retry_at(attempts: int, base_minutes: int = 15) -> str:
    wait_minutes = min(base_minutes * (2 ** max(attempts - 1, 0)), 12 * 60)
    return (now_local() + timedelta(minutes=wait_minutes)).isoformat()


def _recent_platform_count(published_state: dict[str, Any], platform: str, since: datetime) -> int:
    total = 0
    for item in published_state.get("items", []):
        p = (item.get("platforms") or {}).get(platform) or {}
        dt = parse_dt(p.get("scheduled_at") or p.get("published_at"))
        if dt and dt.astimezone(TZ) >= since:
            total += 1
    return total


def _last_platform_time(published_state: dict[str, Any], platform: str) -> datetime | None:
    times = []
    for item in published_state.get("items", []):
        p = (item.get("platforms") or {}).get(platform) or {}
        dt = parse_dt(p.get("scheduled_at") or p.get("published_at"))
        if dt:
            times.append(dt.astimezone(TZ))
    return max(times) if times else None


def next_slot(platform: str, rules: dict[str, Any], published_state: dict[str, Any], priority: str) -> datetime | None:
    cfg = (rules.get("platforms") or {}).get(platform) or {}
    now = now_local()
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    daily_cap = int(cfg.get("daily_cap", 99))
    if priority != "breaking" and _recent_platform_count(published_state, platform, day_start) >= daily_cap:
        return None

    base_delay = int(cfg.get("default_delay_minutes", 15))
    minimum_gap = int(cfg.get("minimum_gap_minutes", 60))
    if priority == "breaking":
        base_delay = min(base_delay, 5)
        minimum_gap = min(minimum_gap, 15)

    candidate = now + timedelta(minutes=base_delay)
    last = _last_platform_time(published_state, platform)
    if last:
        candidate = max(candidate, last + timedelta(minutes=minimum_gap))
    return candidate.replace(second=0, microsecond=0)


def _metricool_credentials() -> tuple[str, str, str]:
    token = os.getenv("METRICOOL_USER_TOKEN", "").strip()
    user_id = os.getenv("METRICOOL_USER_ID", "").strip()
    blog_id = os.getenv("METRICOOL_BLOG_ID", "").strip()
    if not token or not user_id or not blog_id:
        raise SocialConfigError("Metricool live mode requires METRICOOL_USER_TOKEN, METRICOOL_USER_ID and METRICOOL_BLOG_ID.")
    return token, user_id, blog_id


def schedule_metricool(platform: str, copy: dict[str, str], media_url: str | None, scheduled_at: datetime) -> ScheduleResult:
    token, user_id, blog_id = _metricool_credentials()
    network = PLATFORM_TO_METRICOOL[platform]
    body: dict[str, Any] = {
        "publicationDate": {"dateTime": scheduled_at.strftime("%Y-%m-%dT%H:%M:%S"), "timezone": "Asia/Baghdad"},
        "text": copy["text"],
        "providers": [{"network": network}],
        "autoPublish": True,
        "draft": False,
        "shortener": False,
    }
    if media_url:
        body["media"] = [media_url]
        body["saveExternalMediaFiles"] = True
    if platform == "facebook":
        body["facebookData"] = {"type": "POST", "title": ""}
    elif platform == "instagram":
        body["instagramData"] = {"type": "POST", "showReelOnFeed": True, "isAiGenerated": False}
    elif platform == "threads":
        body["threadsData"] = {"allowedCountryCodes": []}
    elif platform == "tiktok":
        body["tiktokData"] = {
            "disableComment": False,
            "disableDuet": False,
            "disableStitch": False,
            "privacyOption": "PUBLIC_TO_EVERYONE",
            "commercialContentThirdParty": False,
            "commercialContentOwnBrand": False,
            "title": copy["text"][:150],
            "autoAddMusic": False,
            "photoCoverIndex": 0,
            "isAigc": False,
        }

    url = f"https://app.metricool.com/api/v2/scheduler/posts?blogId={blog_id}&userId={user_id}"
    payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = request.Request(url, data=payload, method="POST", headers={
        "Content-Type": "application/json",
        "X-Mc-Auth": token,
        "User-Agent": "Mikhbar-Social-Automation/1.0",
    })
    last_error: Exception | None = None
    for attempt in range(1, 4):
        try:
            with request.urlopen(req, timeout=30) as response:
                raw = response.read().decode("utf-8", errors="replace")
                data = json.loads(raw) if raw.strip().startswith(("{", "[")) else {"raw": raw}
                external_id = str(data.get("id") or data.get("postId") or "").strip() or None if isinstance(data, dict) else None
                planner_url = str(data.get("plannerUrl") or "").strip() or None if isinstance(data, dict) else None
                return ScheduleResult(True, data if isinstance(data, dict) else {"data": data}, external_id, planner_url)
        except error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            if exc.code not in {408, 429, 500, 502, 503, 504}:
                return ScheduleResult(False, {"status": exc.code, "error": raw[:1200]})
            last_error = exc
        except (error.URLError, TimeoutError) as exc:
            last_error = exc
        if attempt < 3:
            time.sleep(2 ** (attempt - 1))
    return ScheduleResult(False, {"error": f"{type(last_error).__name__}: {last_error}" if last_error else "unknown Metricool error"})


def _content_for_published(item: dict[str, Any]) -> dict[str, Any] | None:
    rel = str(item.get("content_file") or "").strip()
    if not rel:
        return None
    path = ROOT / rel
    data = load_json(path, None)
    return data if isinstance(data, dict) else None


def _seen_ids(queue_state: dict[str, Any], published_state: dict[str, Any]) -> set[str]:
    ids = {str(x.get("story_id")) for x in queue_state.get("items", []) if x.get("story_id")}
    ids.update(str(x.get("story_id")) for x in published_state.get("items", []) if x.get("story_id"))
    return ids


def discover(limit: int, rules: dict[str, Any], queue_state: dict[str, Any], published_state: dict[str, Any]) -> list[dict[str, Any]]:
    forum = load_json(FORUM_PUBLISHED, {"items": []})
    seen = _seen_ids(queue_state, published_state)
    found: list[dict[str, Any]] = []
    for published_item in (forum.get("items") or [])[:limit]:
        content = _content_for_published(published_item)
        if not content:
            continue
        sid = story_id(content)
        if sid in seen:
            continue
        score = social_score(content, published_item)
        priority = social_priority(content, score)
        platforms = select_platforms(content, score, rules)
        canonical = canonical_url(content)
        status = "selected" if platforms else "skipped"
        reason = None if platforms else "low_social_score_or_missing_media"
        found.append({
            "story_id": sid,
            "canonical_url": canonical,
            "content_file": published_item.get("content_file") or content.get("contentFile"),
            "site_published_at": published_item.get("published_at") or content.get("datePublished"),
            "social_score": score,
            "social_priority": priority,
            "status": status,
            "skip_reason": reason,
            "selected_platforms": platforms,
            "platforms": {
                p: {
                    "status": "media_pending" if p == "tiktok" else "ready",
                    "attempts": 0,
                    "last_error": None,
                    "last_attempt_at": None,
                    "next_retry_at": None,
                } for p in platforms
            },
            "created_at": now_local().isoformat(),
            "updated_at": now_local().isoformat(),
        })
        seen.add(sid)
    return found


def _platform_due(platform_state: dict[str, Any]) -> bool:
    status = platform_state.get("status")
    if status not in {"ready", "failed", "retrying"}:
        return False
    next_retry = parse_dt(platform_state.get("next_retry_at"))
    return next_retry is None or next_retry <= now_local()


def process_queue(mode: str, rules: dict[str, Any], queue_state: dict[str, Any], published_state: dict[str, Any], failed_state: dict[str, Any]) -> dict[str, Any]:
    report = {
        "mode": mode,
        "detected": 0,
        "selected": 0,
        "scheduled": {"facebook": 0, "instagram": 0, "threads": 0, "tiktok": 0},
        "dry_run_ready": {"facebook": 0, "instagram": 0, "threads": 0, "tiktok": 0},
        "media_pending": {"tiktok": 0},
        "failed": 0,
        "skipped": 0,
        "details": [],
    }

    existing_published_ids = {str(x.get("story_id")) for x in published_state.get("items", []) if x.get("story_id")}
    completed_records = []

    for item in queue_state.get("items", []):
        report["detected"] += 1
        if item.get("status") == "skipped":
            report["skipped"] += 1
            continue
        report["selected"] += 1
        content = _content_for_published(item)
        if not content:
            item["status"] = "failed"
            item["skip_reason"] = "content_file_missing_or_invalid"
            report["failed"] += 1
            continue
        media_url = _media_url(content)
        platform_output: dict[str, Any] = {}

        for platform in item.get("selected_platforms", []):
            pstate = (item.get("platforms") or {}).setdefault(platform, {"status": "ready", "attempts": 0})
            if platform == "tiktok":
                if pstate.get("status") == "media_pending":
                    pstate["video_script"] = generate_copy(content, platform).get("script")
                    pstate["source_image"] = media_url
                    report["media_pending"]["tiktok"] += 1
                continue
            if not _platform_due(pstate):
                continue

            copy = generate_copy(content, platform)
            slot = next_slot(platform, rules, published_state, item.get("social_priority") or "normal")
            if slot is None:
                pstate["status"] = "skipped"
                pstate["skip_reason"] = "daily_cap_reached"
                continue

            if mode == "dry-run":
                pstate["status"] = "ready"
                pstate["proposed_at"] = slot.isoformat()
                pstate["caption_preview"] = copy["text"]
                pstate["media"] = media_url
                report["dry_run_ready"][platform] += 1
                platform_output[platform] = {"status": "ready", "scheduled_at": slot.isoformat(), "copy": copy, "media": media_url}
                continue

            pstate["attempts"] = int(pstate.get("attempts") or 0) + 1
            pstate["last_attempt_at"] = now_local().isoformat()
            result = schedule_metricool(platform, copy, media_url, slot)
            if result.ok:
                pstate.update({
                    "status": "scheduled",
                    "scheduled_at": slot.isoformat(),
                    "post_id": result.external_id,
                    "planner_url": result.planner_url,
                    "last_error": None,
                    "next_retry_at": None,
                    "caption_version": 1,
                    "media": media_url,
                })
                report["scheduled"][platform] += 1
                platform_output[platform] = dict(pstate)
            else:
                pstate["status"] = "failed"
                pstate["last_error"] = json.dumps(result.response, ensure_ascii=False)[:1600]
                pstate["next_retry_at"] = retry_at(pstate["attempts"])
                failed_state.setdefault("items", []).append({
                    "story_id": item["story_id"],
                    "platform": platform,
                    "attempt": pstate["attempts"],
                    "last_error": pstate["last_error"],
                    "last_attempt_at": pstate["last_attempt_at"],
                    "next_retry_at": pstate["next_retry_at"],
                })
                report["failed"] += 1

        item["updated_at"] = now_local().isoformat()
        states = [v.get("status") for v in (item.get("platforms") or {}).values()]
        if any(s == "scheduled" for s in states):
            terminal = {"scheduled", "published", "skipped", "media_pending"}
            item["status"] = "scheduled" if all(s in terminal for s in states) else "partial"
            record_payload = {
                "story_id": item["story_id"],
                "canonical_url": item["canonical_url"],
                "social_score": item["social_score"],
                "social_priority": item["social_priority"],
                "platforms": item["platforms"],
                "recorded_at": now_local().isoformat(),
            }
            existing_record = next(
                (x for x in published_state.get("items", []) if x.get("story_id") == item["story_id"]),
                None,
            )
            if existing_record is not None:
                existing_record.update(record_payload)
            else:
                completed_records.append(record_payload)
                existing_published_ids.add(item["story_id"])
        elif states and all(s in {"skipped", "media_pending"} for s in states):
            item["status"] = "media_pending" if "media_pending" in states else "skipped"
        report["details"].append({
            "story_id": item["story_id"],
            "score": item["social_score"],
            "priority": item["social_priority"],
            "platforms": platform_output,
        })

    if completed_records:
        published_state.setdefault("items", [])[0:0] = completed_records
        published_state["items"] = published_state["items"][:1000]
    return report


def run(mode: str, discover_limit: int = 20) -> int:
    if mode not in {"dry-run", "live"}:
        raise ValueError("mode must be dry-run or live")
    if mode == "live":
        _metricool_credentials()

    rules = load_json(RULES_PATH, {"platforms": {}})
    queue_path = SOCIAL_STATE / "queue.json"
    published_path = SOCIAL_STATE / "published.json"
    failed_path = SOCIAL_STATE / "failed.json"
    status_path = SOCIAL_STATE / "platform_status.json"
    report_path = SOCIAL_STATE / "last_run.json"

    queue_state = load_json(queue_path, {"version": 1, "items": []})
    published_state = load_json(published_path, {"version": 1, "items": []})
    failed_state = load_json(failed_path, {"version": 1, "items": []})

    found = discover(discover_limit, rules, queue_state, published_state)
    if found:
        queue_state.setdefault("items", [])[0:0] = found
        queue_state["items"] = queue_state["items"][:1000]
    report = process_queue(mode, rules, queue_state, published_state, failed_state)
    report["newly_discovered"] = len(found)
    report["ran_at"] = now_local().isoformat()
    report["source_of_truth"] = "automation/forum/state/published.json + forum/content/**/*.json"

    queue_state["updated_at"] = now_local().isoformat()
    published_state["updated_at"] = now_local().isoformat()
    failed_state["updated_at"] = now_local().isoformat()
    platform_status = {
        "updated_at": now_local().isoformat(),
        "mode": mode,
        "metricool": {
            "live_configured": bool(os.getenv("METRICOOL_USER_TOKEN") and os.getenv("METRICOOL_USER_ID") and os.getenv("METRICOOL_BLOG_ID")),
            "required_brand": "Mikhbar / مِخبار",
            "connected_brand_verified": False,
            "note": "Set to true only after the dedicated Mikhbar Metricool brand and networks are verified.",
        },
        "platforms": {p: {"adapter": "metricool", "enabled": True} for p in PLATFORM_TO_METRICOOL},
    }

    save_json(queue_path, queue_state)
    save_json(published_path, published_state)
    save_json(failed_path, failed_state)
    save_json(status_path, platform_status)
    save_json(report_path, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Mikhbar social editorial automation")
    parser.add_argument("--mode", choices=["dry-run", "live"], default="dry-run")
    parser.add_argument("--discover-limit", type=int, default=20)
    args = parser.parse_args()
    return run(args.mode, max(1, min(args.discover_limit, 100)))


if __name__ == "__main__":
    raise SystemExit(main())
