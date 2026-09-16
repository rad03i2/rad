from __future__ import annotations

import math
import re
from collections import Counter
from datetime import datetime, timezone
from difflib import SequenceMatcher

from common import normalize_title

CATEGORY_BOOST = {
    "ai": 10,
    "robotics": 10,
    "automation": 8,
    "mobile": 5,
    "computers": 5,
    "apps": 4,
    "web": 4,
    "social": 4,
    "security": 6,
}

TREND_TERMS = {
    "launch": 5, "launches": 5, "announces": 5, "announced": 5,
    "release": 5, "released": 5, "new": 3, "update": 3, "updates": 3,
    "ai": 4, "robot": 5, "robotics": 5, "humanoid": 6, "automation": 5,
    "android": 4, "iphone": 4, "windows": 4, "nvidia": 4, "openai": 5,
    "google": 3, "microsoft": 3, "apple": 3, "meta": 3, "github": 3,
    "security": 4, "vulnerability": 5, "chip": 4, "gpu": 4,
}

STOP_ENTITIES = {"the", "and", "for", "with", "from", "into", "this", "that", "new", "how", "why", "what"}


def _dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def _age_hours(item: dict) -> float:
    published = _dt(item.get("published_at")) or _dt(item.get("discovered_at"))
    if not published:
        return 999.0
    return max(0.0, (datetime.now(timezone.utc) - published.astimezone(timezone.utc)).total_seconds() / 3600)


def _tokens(title: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9][a-z0-9+.-]{1,}", title.lower()) if t not in STOP_ENTITIES}


def _story_similarity(a: dict, b: dict) -> float:
    ta = normalize_title(a.get("title", ""))
    tb = normalize_title(b.get("title", ""))
    seq = SequenceMatcher(None, ta, tb).ratio() if ta and tb else 0.0
    sa, sb = _tokens(a.get("title", "")), _tokens(b.get("title", ""))
    jac = len(sa & sb) / max(1, len(sa | sb))
    return max(seq, jac * 1.35)


def _entity_counter(items: list[dict], window_hours: float) -> Counter:
    c: Counter = Counter()
    for item in items:
        if _age_hours(item) > window_hours:
            continue
        for token in _tokens(item.get("title", "")):
            if len(token) >= 3 and not token.isdigit():
                c[token] += 1
    return c


def rank_candidates(items: list[dict], settings: dict, published_posts: list[dict]) -> list[dict]:
    window = float(settings.get("trendWindowHours", 24))
    min_trend = float(settings.get("minimumTrendScore", 62))
    entity_counts = _entity_counter(items, window)
    recently_published_categories = [p.get("categorySlug") for p in published_posts[:6] if p.get("categorySlug")]

    ranked: list[dict] = []
    for item in items:
        age = _age_hours(item)
        if age > max(window, 36):
            continue

        source = item.get("source", {})
        source_domain = item.get("domain", "")
        corroboration = []
        for other in items:
            if other is item or other.get("domain") == source_domain:
                continue
            if _age_hours(other) > max(window, 36):
                continue
            if _story_similarity(item, other) >= 0.58:
                corroboration.append({
                    "name": other.get("source", {}).get("name", other.get("domain", "source")),
                    "url": other.get("url"),
                    "domain": other.get("domain"),
                    "title": other.get("title"),
                })

        recency = max(0.0, 28.0 * (1.0 - min(age, window) / max(window, 1.0)))
        official = 12 if source.get("type") == "official" else 0
        corroboration_bonus = min(24, len(corroboration) * 8)
        category = item.get("category", "apps")
        category_bonus = CATEGORY_BOOST.get(category, 3)

        terms = _tokens(item.get("title", ""))
        term_bonus = min(14, sum(TREND_TERMS.get(t, 0) for t in terms))
        momentum = sum(max(0, entity_counts.get(t, 0) - 1) for t in terms)
        momentum_bonus = min(18, math.log2(1 + momentum) * 6 if momentum else 0)

        diversity_penalty = recently_published_categories.count(category) * 5
        base = float(item.get("score", 0))
        trend_score = round(base + recency + official + corroboration_bonus + category_bonus + term_bonus + momentum_bonus - diversity_penalty, 2)

        verification = dict(item.get("verification", {}))
        if source.get("type") != "official" and corroboration:
            verification["confidence"] = max(float(verification.get("confidence", 0)), min(0.98, 0.90 + len(corroboration) * 0.02))
            verification["reason"] = "trusted_journalism_with_corroboration"
            verification["publish_eligible"] = verification["confidence"] >= float(settings.get("minimumVerificationConfidence", 0.90))
        verification["corroborating_sources"] = corroboration[:4]

        enriched = dict(item)
        enriched["verification"] = verification
        enriched["trend"] = {
            "score": trend_score,
            "age_hours": round(age, 2),
            "corroboration_count": len(corroboration),
            "entity_momentum": round(momentum_bonus, 2),
            "category_boost": category_bonus,
        }
        if trend_score >= min_trend and verification.get("publish_eligible"):
            ranked.append(enriched)

    ranked.sort(key=lambda x: (x.get("trend", {}).get("score", 0), x.get("published_at") or ""), reverse=True)
    return ranked
