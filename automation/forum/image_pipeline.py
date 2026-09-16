from __future__ import annotations

import hashlib
import io
import math
import re
from pathlib import Path
from urllib.parse import urlparse

import requests
from PIL import Image, ImageDraw, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[2]
FORUM = ROOT / "forum"
SITE = "https://rdwan.dev"

BAD_IMAGE_TOKENS = (
    "logo", "favicon", "icon", "avatar", "sprite", "badge", "emoji", "tracking", "pixel", "author"
)

CATEGORY_ACCENTS = {
    "ai": (103, 232, 166),
    "robotics": (116, 193, 255),
    "automation": (198, 241, 108),
    "mobile": (199, 142, 255),
    "computers": (255, 174, 102),
    "apps": (109, 220, 255),
    "web": (125, 246, 214),
    "social": (255, 116, 162),
    "security": (255, 105, 105),
}


def _clean_image_url(value: str | None) -> str:
    value = str(value or "").strip()
    if not value.startswith(("http://", "https://")):
        return ""
    low = value.lower()
    if any(token in low for token in BAD_IMAGE_TOKENS):
        return ""
    return value


def _rank_candidates(source_pack: list[dict]) -> list[dict]:
    ranked = []
    for index, source in enumerate(source_pack):
        url = _clean_image_url(source.get("image_url"))
        if not url:
            continue
        kind = str(source.get("kind") or "").lower()
        score = 100 if kind == "official" else 50
        if index == 0:
            score += 25
        if source.get("image_width") and source.get("image_height"):
            try:
                score += min(20, int(source["image_width"]) * int(source["image_height"]) / 250000)
            except Exception:
                pass
        ranked.append({"url": url, "score": score, "source": source})
    ranked.sort(key=lambda x: x["score"], reverse=True)
    return ranked


def _download_image(url: str, user_agent: str) -> Image.Image | None:
    headers = {
        "User-Agent": user_agent,
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        "Referer": f"{urlparse(url).scheme}://{urlparse(url).netloc}/",
    }
    try:
        response = requests.get(url, headers=headers, timeout=24, allow_redirects=True, stream=True)
        response.raise_for_status()
        content_type = (response.headers.get("content-type") or "").lower()
        if "svg" in content_type:
            return None
        data = response.raw.read(16 * 1024 * 1024 + 1)
        if len(data) > 16 * 1024 * 1024:
            return None
        image = Image.open(io.BytesIO(data))
        image.load()
        if image.width < 700 or image.height < 350:
            return None
        return ImageOps.exif_transpose(image).convert("RGB")
    except Exception:
        return None


def _soften_background(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    background = ImageOps.fit(image, size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
    return background


def _save_variants(image: Image.Image, directory: Path) -> dict:
    directory.mkdir(parents=True, exist_ok=True)
    hero = _soften_background(image, (1600, 900))
    card = _soften_background(image, (800, 450))
    social = _soften_background(image, (1200, 630))

    hero_path = directory / "hero.webp"
    card_path = directory / "card.webp"
    social_path = directory / "social.jpg"

    hero.save(hero_path, "WEBP", quality=88, method=6)
    card.save(card_path, "WEBP", quality=86, method=6)
    social.save(social_path, "JPEG", quality=90, optimize=True, progressive=True)
    return {
        "hero": hero_path,
        "card": card_path,
        "social": social_path,
    }


def _fallback_visual(category_slug: str, seed: str) -> Image.Image:
    width, height = 1600, 900
    base = Image.new("RGB", (width, height), (12, 17, 13))
    accent = CATEGORY_ACCENTS.get(category_slug, (198, 241, 108))
    draw = ImageDraw.Draw(base, "RGBA")

    digest = hashlib.sha256(seed.encode("utf-8", "ignore")).digest()
    for i in range(32):
        x = int((digest[i % len(digest)] / 255) * width)
        y = int((digest[(i + 7) % len(digest)] / 255) * height)
        radius = 25 + (digest[(i + 11) % len(digest)] % 90)
        alpha = 16 + digest[(i + 17) % len(digest)] % 34
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*accent, alpha))

    for i in range(12):
        x1 = int(width * (i / 12))
        y1 = int(height * (0.15 + 0.7 * ((digest[i] / 255))))
        x2 = int(width * ((i + 3) / 12))
        y2 = int(height * (0.15 + 0.7 * ((digest[(i + 5) % len(digest)] / 255))))
        draw.line((x1, y1, x2, y2), fill=(*accent, 45), width=2)
        draw.ellipse((x1 - 5, y1 - 5, x1 + 5, y1 + 5), fill=(*accent, 120))

    draw.rounded_rectangle((90, 90, 1510, 810), radius=42, outline=(*accent, 80), width=2)
    draw.rectangle((90, 740, 1510, 810), fill=(7, 10, 8, 165))
    draw.text((122, 760), "RDWAN TECH  /  " + category_slug.upper(), fill=(232, 238, 229, 205))
    return base.filter(ImageFilter.GaussianBlur(radius=0.3))


def prepare_images(story: dict, source_pack: list[dict], slug: str, published_year: int, published_month: int,
                   title_ar: str, title_en: str, settings: dict) -> dict:
    category_slug = story.get("category", "apps")
    directory = FORUM / "assets" / "posts" / f"{published_year:04d}" / f"{published_month:02d}" / slug
    user_agent = settings.get("userAgent", "RDWAN-Tech-Publisher/1.0")

    chosen = None
    for candidate in _rank_candidates(source_pack):
        image = _download_image(candidate["url"], user_agent)
        if image is not None:
            chosen = {"image": image, **candidate}
            break

    if chosen:
        variants = _save_variants(chosen["image"], directory)
        source = chosen["source"]
        image_source_url = chosen["url"]
        credit = source.get("name") or urlparse(source.get("url") or image_source_url).netloc
        source_type = source.get("kind") or "source"
        generated = False
    else:
        visual = _fallback_visual(category_slug, f"{story.get('id')}|{title_en}|{title_ar}")
        variants = _save_variants(visual, directory)
        image_source_url = ""
        credit = "RDWAN Tech"
        source_type = "generated-fallback"
        generated = True

    def public(path: Path) -> str:
        return "/" + path.relative_to(ROOT).as_posix()

    return {
        "hero": public(variants["hero"]),
        "card": public(variants["card"]),
        "social": public(variants["social"]),
        "alt": {"ar": title_ar, "en": title_en},
        "credit": credit,
        "sourceUrl": image_source_url,
        "sourceType": source_type,
        "generatedFallback": generated,
    }
