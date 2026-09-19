from __future__ import annotations

from datetime import datetime, timezone

from common import CONFIG, domain_of, load_json, normalize_title


def _classify(story: dict, categories: dict) -> tuple[str, str, int]:
    haystack = normalize_title((story.get("title") or "") + " " + (story.get("summary") or ""))
    best_slug = story.get("source", {}).get("defaultCategory", "apps")
    best_hits = 0
    for slug, cfg in categories.items():
        hits = 0
        for keyword in cfg.get("keywords", []):
            k = normalize_title(keyword)
            if k and k in haystack:
                hits += 1
        if hits > best_hits:
            best_slug, best_hits = slug, hits
    label = categories.get(best_slug, {}).get("label", best_slug)
    return best_slug, label, best_hits


def _age_hours(iso: str | None) -> float | None:
    if not iso:
        return None
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return max(0.0, (datetime.now(timezone.utc) - dt.astimezone(timezone.utc)).total_seconds() / 3600)
    except Exception:
        return None


def _verification_policy(source: dict, settings: dict) -> dict:
    source_type = source.get("type", "journalism")
    trust = float(source.get("trust", 0.7))
    min_conf = float(settings.get("minimumVerificationConfidence", 0.90))
    allow_single = bool(settings.get("allowTrustedJournalismSingleSource", True))
    single_threshold = float(settings.get("trustedJournalismSingleSourceThreshold", 0.84))

    if source_type == "official":
        confidence = max(0.94, trust)
        return {
            "confidence": round(confidence, 3),
            "reason": "official_source",
            "official": True,
            "single_source_trusted": True,
            "publish_eligible": confidence >= min_conf,
            "corroborating_sources": [],
        }

    confidence = min(0.92, trust)
    single_source_trusted = allow_single and trust >= single_threshold
    return {
        "confidence": round(confidence, 3),
        "reason": "trusted_journalism_single_source" if single_source_trusted else "trusted_journalism",
        "official": False,
        "single_source_trusted": single_source_trusted,
        "publish_eligible": confidence >= min_conf or single_source_trusted,
        "corroborating_sources": [],
    }


def refresh_queue_verification(items: list[dict], settings: dict) -> list[dict]:
    """Refresh verification policy for queued stories after editorial policy changes."""
    for item in items:
        if item.get("status") in {"published", "quality_rejected"}:
            continue
        source = item.get("source", {})
        existing = dict(item.get("verification", {}))
        refreshed = _verification_policy(source, settings)
        # Preserve corroboration discovered during ranking when present.
        if existing.get("corroborating_sources"):
            refreshed["corroborating_sources"] = existing["corroborating_sources"]
        item["verification"] = refreshed
    return items


def verify_and_score(stories: list[dict], settings: dict) -> tuple[list[dict], int]:
    categories = load_json(CONFIG / "categories.json", {"categories": {}}).get("categories", {})
    blocked = {d.lower().removeprefix("www.") for d in load_json(CONFIG / "blocked_domains.json", {"domains": []}).get("domains", [])}
    max_age = float(settings.get("maxAgeHours", 96))
    min_conf = float(settings.get("minimumVerificationConfidence", 0.85))

    accepted: list[dict] = []
    rejected = 0

    for story in stories:
        domain = story.get("domain") or domain_of(story.get("url", ""))
        if domain in blocked:
            rejected += 1
            continue

        age = _age_hours(story.get("published_at"))
        if age is not None and age > max_age:
            rejected += 1
            continue

        source = story.get("source", {})
        source_type = source.get("type", "journalism")
        trust = float(source.get("trust", 0.7))
        priority = int(source.get("priority", 10))
        category, category_label, keyword_hits = _classify(story, categories)

        verification = _verification_policy(source, settings)
        confidence = float(verification["confidence"])

        freshness_bonus = 0
        if age is not None:
            if age <= 6:
                freshness_bonus = 18
            elif age <= 24:
                freshness_bonus = 12
            elif age <= 48:
                freshness_bonus = 7
            elif age <= 96:
                freshness_bonus = 3

        score = priority + freshness_bonus + min(keyword_hits * 3, 15)
        if source_type == "official":
            score += 15

        story["category"] = category
        story["category_label"] = category_label
        story["score"] = score
        story["verification"] = verification
        story["status"] = "incoming"
        accepted.append(story)

    accepted.sort(key=lambda x: (x.get("score", 0), x.get("published_at") or x.get("discovered_at") or ""), reverse=True)
    return accepted, rejected
