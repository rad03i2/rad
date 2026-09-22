from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from html import unescape
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


def _clean_text(text: str) -> str:
    text = unescape(text or "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _meta_content(soup: BeautifulSoup, *queries: tuple[str, str]) -> str:
    for key, value in queries:
        tag = soup.find("meta", attrs={key: value})
        if tag and tag.get("content"):
            return str(tag.get("content")).strip()
    return ""


BAD_MEDIA_TOKENS = (
    "logo", "favicon", "icon", "avatar", "sprite", "badge", "emoji", "tracking", "pixel",
    "author", "profile", "newsletter", "advert", "ads/", "banner-cookie",
)


def _positive_int(value) -> int:
    try:
        return max(0, int(str(value or "").strip()))
    except (TypeError, ValueError):
        return 0


def _srcset_best(value: str | None) -> str:
    best_url = ""
    best_score = -1
    for item in str(value or "").split(","):
        bits = item.strip().split()
        if not bits:
            continue
        url = bits[0].strip()
        score = 0
        if len(bits) > 1:
            descriptor = bits[-1].lower()
            try:
                if descriptor.endswith("w"):
                    score = int(float(descriptor[:-1]))
                elif descriptor.endswith("x"):
                    score = int(float(descriptor[:-1]) * 1000)
            except ValueError:
                score = 0
        if score >= best_score:
            best_score = score
            best_url = url
    return best_url


def _clean_http_url(base_url: str, value: str | None) -> str:
    value = str(value or "").strip()
    if not value or value.startswith(("data:", "blob:", "javascript:", "mailto:", "#")):
        return ""
    absolute = urljoin(base_url, value)
    if not absolute.startswith(("http://", "https://")):
        return ""
    return absolute


def _extract_media_candidates(root, base_url: str, limit: int = 16) -> list[dict]:
    items = []
    seen = set()
    for img in root.find_all("img"):
        raw = (
            img.get("data-src")
            or img.get("data-original")
            or img.get("data-lazy-src")
            or _srcset_best(img.get("srcset"))
            or img.get("src")
        )
        url = _clean_http_url(base_url, raw)
        low = url.lower()
        if not url or url in seen or any(token in low for token in BAD_MEDIA_TOKENS):
            continue

        width = _positive_int(img.get("width"))
        height = _positive_int(img.get("height"))
        alt = _clean_text(img.get("alt") or img.get("title") or "")
        caption = ""
        figure = img.find_parent("figure")
        if figure:
            figcaption = figure.find("figcaption")
            if figcaption:
                caption = _clean_text(figcaption.get_text(" ", strip=True))
        if not caption:
            caption = _clean_text(img.get("data-caption") or "")
        if width and height and (width < 480 or height < 240):
            continue

        seen.add(url)
        items.append({
            "url": url,
            "alt": alt[:220],
            "caption": caption[:320],
            "width": width,
            "height": height,
        })
        if len(items) >= limit:
            break
    return items


def _extract_link_candidates(root, base_url: str, limit: int = 18) -> list[dict]:
    items = []
    seen = set()
    for anchor in root.find_all("a", href=True):
        label = _clean_text(anchor.get_text(" ", strip=True))
        url = _clean_http_url(base_url, anchor.get("href"))
        if not url or not label or len(label) < 2 or len(label) > 90:
            continue
        key = (label.casefold(), url)
        if key in seen:
            continue
        seen.add(key)
        items.append({"text": label, "url": url})
        if len(items) >= limit:
            break
    return items


def _extract_page(url: str, user_agent: str) -> dict:
    headers = {"User-Agent": user_agent, "Accept": "text/html,application/xhtml+xml"}
    try:
        response = requests.get(url, headers=headers, timeout=18, allow_redirects=True)
        response.raise_for_status()
    except Exception as exc:
        return {"url": url, "ok": False, "error": str(exc), "text": "", "image_url": "", "images": [], "link_candidates": []}

    soup = BeautifulSoup(response.text, "html.parser")
    title = _clean_text((soup.title.string if soup.title and soup.title.string else ""))
    description = _clean_text(_meta_content(
        soup,
        ("name", "description"),
        ("property", "og:description"),
        ("name", "twitter:description"),
    ))
    image_raw = _meta_content(
        soup,
        ("property", "og:image:secure_url"),
        ("property", "og:image"),
        ("name", "twitter:image"),
        ("name", "twitter:image:src"),
    )
    image_url = urljoin(response.url, image_raw) if image_raw else ""
    image_width = _meta_content(soup, ("property", "og:image:width"))
    image_height = _meta_content(soup, ("property", "og:image:height"))

    for tag in soup(["script", "style", "noscript", "svg", "nav", "footer", "header", "form", "aside"]):
        tag.decompose()

    candidates = []
    for selector in ["article", "main", "[role='main']", ".article-body", ".post-content", ".entry-content"]:
        node = soup.select_one(selector)
        if node:
            candidates.append(node)
    root = max(candidates, key=lambda n: len(n.get_text(" ", strip=True)), default=soup.body or soup)

    inline_images = _extract_media_candidates(root, response.url)
    link_candidates = _extract_link_candidates(root, response.url)

    paragraphs = []
    for p in root.find_all(["p", "li", "h2", "h3"]):
        text = _clean_text(p.get_text(" ", strip=True))
        if len(text) >= 45:
            paragraphs.append(text)
    body = "\n".join(paragraphs)
    if not body:
        body = _clean_text(root.get_text(" ", strip=True))

    return {
        "url": response.url,
        "ok": True,
        "title": title,
        "description": description,
        "text": body[:9000],
        "image_url": image_url,
        "image_width": image_width,
        "image_height": image_height,
        "images": inline_images,
        "link_candidates": link_candidates,
    }


def build_source_pack(story: dict, settings: dict) -> list[dict]:
    user_agent = settings.get("userAgent", "RDWAN-Tech-Publisher/1.0")
    sources = [{
        "name": story.get("source", {}).get("name", story.get("domain", "Primary source")),
        "url": story.get("url"),
        "kind": story.get("source", {}).get("type", "unknown"),
        "feed_title": story.get("title", ""),
        "feed_summary": story.get("summary", ""),
    }]
    for source in story.get("verification", {}).get("corroborating_sources", [])[:3]:
        sources.append({
            "name": source.get("name", source.get("domain", "Corroborating source")),
            "url": source.get("url"),
            "kind": source.get("type", "corroborating"),
            "feed_title": source.get("title", ""),
            "feed_summary": source.get("summary", ""),
        })

    pack = []
    seen = set()
    for src in sources:
        url = src.get("url")
        if not url or url in seen:
            continue
        seen.add(url)
        page = _extract_page(url, user_agent)
        pack.append({**src, **page})
    return pack


def _extract_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start:end + 1])
        raise


def _call_openai_compatible(prompt: str, api_key: str, endpoint: str, model: str, provider: str, extra_headers: dict | None = None) -> dict:
    if not api_key:
        raise RuntimeError(f"{provider} API key is not configured")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "RDWAN-Tech-Publisher/1.0",
    }
    if extra_headers:
        headers.update(extra_headers)

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.35,
        "max_tokens": 8192,
    }

    last_error = None
    for _ in range(2):
        try:
            response = requests.post(endpoint, headers=headers, json=payload, timeout=180)
            if response.status_code >= 400:
                last_error = f"{provider} API failed ({response.status_code}): {response.text[:1600]}"
                continue

            data = response.json()
            choices = data.get("choices") or []
            if not choices:
                last_error = f"{provider} returned no choices: {json.dumps(data)[:1200]}"
                continue

            message = choices[0].get("message") or {}
            text = message.get("content")
            if isinstance(text, list):
                text = "\n".join(
                    str(part.get("text", ""))
                    for part in text
                    if isinstance(part, dict) and part.get("text")
                )
            text = str(text or "").strip()
            if not text:
                last_error = f"{provider} returned no text: {json.dumps(data)[:1200]}"
                continue
            return _extract_json(text)
        except Exception as exc:
            last_error = f"{provider} request failed: {type(exc).__name__}: {exc}"

    raise RuntimeError(last_error or f"{provider} API failed")


def _unique_models(*models: str) -> list[str]:
    seen = set()
    result = []
    for model in models:
        model = str(model or "").strip()
        if model and model not in seen:
            seen.add(model)
            result.append(model)
    return result


def _groq_available_models(api_key: str) -> set[str]:
    if not api_key:
        return set()
    try:
        response = requests.get(
            "https://api.groq.com/openai/v1/models",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "RDWAN-Tech-Publisher/1.0",
            },
            timeout=20,
        )
        if response.status_code >= 400:
            return set()
        data = response.json()
        return {
            str(item.get("id") or "").strip()
            for item in (data.get("data") or [])
            if str(item.get("id") or "").strip()
        }
    except Exception:
        return set()


def _call_groq(prompt: str, models: list[str]) -> dict:
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Groq API key is not configured")

    available = _groq_available_models(api_key)
    candidates = [model for model in models if not available or model in available]
    if not candidates:
        candidates = list(models)

    errors = []
    for model in candidates:
        try:
            return _call_openai_compatible(
                prompt=prompt,
                api_key=api_key,
                endpoint="https://api.groq.com/openai/v1/chat/completions",
                model=model,
                provider=f"Groq/{model}",
            )
        except Exception as exc:
            errors.append(str(exc))
    raise RuntimeError("No Groq model succeeded: " + " | ".join(errors))


def _call_openrouter(prompt: str, model: str) -> dict:
    return _call_openai_compatible(
        prompt=prompt,
        api_key=os.environ.get("OPENROUTER_API_KEY", "").strip(),
        endpoint="https://openrouter.ai/api/v1/chat/completions",
        model=model,
        provider="OpenRouter",
        extra_headers={
            "HTTP-Referer": "https://rdwan.dev/forum/",
            "X-Title": "Mikhbar",
        },
    )


def _call_gemini(prompt: str, models: list[str]) -> dict:
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    endpoint = "https://generativelanguage.googleapis.com/v1beta/interactions"
    errors = []
    for model in models:
        payload = {
            "model": model,
            "input": prompt,
            "generation_config": {
                "max_output_tokens": 8192,
            },
        }
        last_error = None
        for _ in range(2):
            try:
                response = requests.post(
                    endpoint,
                    headers={
                        "x-goog-api-key": api_key,
                        "Content-Type": "application/json",
                        "User-Agent": "RDWAN-Tech-Publisher/1.0",
                    },
                    json=payload,
                    timeout=180,
                )
                if response.status_code >= 400:
                    body = response.text[:1600]
                    last_error = f"{model} failed ({response.status_code}): {body}"
                    # Quota/service pressure can be model-specific, so try the next model.
                    if response.status_code in (404, 429, 500, 502, 503, 504):
                        break
                    continue

                data = response.json()
                if data.get("status") not in (None, "completed"):
                    last_error = f"{model} did not complete: {json.dumps(data)[:1200]}"
                    continue

                text_parts = []
                for step in data.get("steps") or []:
                    if step.get("type") != "model_output":
                        continue
                    for part in step.get("content") or []:
                        if part.get("type") == "text" and part.get("text"):
                            text_parts.append(str(part["text"]))

                text = "\n".join(text_parts).strip()
                if not text:
                    last_error = f"{model} returned no text: {json.dumps(data)[:1200]}"
                    continue
                return _extract_json(text)
            except Exception as exc:
                last_error = f"{model} request failed: {type(exc).__name__}: {exc}"
        errors.append(last_error or f"{model} failed")

    raise RuntimeError("No Gemini model succeeded: " + " | ".join(errors))


def _call_copilot(prompt: str) -> dict:
    if not shutil.which("copilot"):
        raise RuntimeError("GitHub Copilot CLI is not installed")
    if not (os.environ.get("GITHUB_TOKEN") or os.environ.get("COPILOT_GITHUB_TOKEN")):
        raise RuntimeError("GITHUB_TOKEN is required for Copilot CLI automation")

    command = [
        "copilot", "-p", prompt, "-s", "--no-ask-user", "--no-color",
        "--no-custom-instructions", "--no-auto-update",
    ]
    last_error = None
    for _ in range(2):
        try:
            proc = subprocess.run(command, text=True, capture_output=True, timeout=180, env=os.environ.copy())
        except subprocess.TimeoutExpired as exc:
            last_error = f"Copilot CLI timed out: {exc}"
            continue
        if proc.returncode != 0:
            last_error = f"Copilot CLI failed ({proc.returncode}): {(proc.stderr or proc.stdout)[-1200:]}"
            continue
        try:
            return _extract_json(proc.stdout)
        except Exception as exc:
            last_error = f"Copilot returned invalid JSON: {exc}; output={proc.stdout[:900]}"
    raise RuntimeError(last_error or "Copilot CLI failed")


def _call_model(prompt: str, settings: dict) -> dict:
    errors = []

    groq_models = _unique_models(
        settings.get("groqModel"),
        "qwen/qwen3.6-27b",
        "qwen/qwen3.8-27b",
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
    )
    if os.environ.get("GROQ_API_KEY", "").strip():
        try:
            return _call_groq(prompt, groq_models)
        except Exception as exc:
            errors.append(f"Groq: {exc}")

    # Gemini comes before the rate-limited free OpenRouter fallback. Model-level
    # fallback avoids stopping publication when one Flash tier is under pressure.
    gemini_models = _unique_models(
        settings.get("geminiModel"),
        "gemini-3.5-flash-lite",
        "gemini-2.5-flash-lite",
        "gemini-3.6-flash",
    )
    if os.environ.get("GEMINI_API_KEY", "").strip():
        try:
            return _call_gemini(prompt, gemini_models)
        except Exception as exc:
            errors.append(f"Gemini: {exc}")

    if os.environ.get("OPENROUTER_API_KEY", "").strip():
        try:
            return _call_openrouter(prompt, settings.get("openRouterModel", "openrouter/free"))
        except Exception as exc:
            errors.append(f"OpenRouter: {exc}")

    try:
        return _call_copilot(prompt)
    except Exception as exc:
        errors.append(f"Copilot: {exc}")

    raise RuntimeError("All article generation providers failed: " + " | ".join(errors))


def _source_text(usable: list[dict]) -> str:
    blocks = []
    for index, src in enumerate(usable, 1):
        blocks.append(
            f"SOURCE {index}\nName: {src.get('name')}\nType: {src.get('kind')}\nURL: {src.get('url')}\n"
            f"Feed title: {src.get('feed_title', '')}\nFeed summary: {src.get('feed_summary', '')}\n"
            f"Page title: {src.get('title', '')}\nPage description: {src.get('description', '')}\n"
            f"Allowed link targets (use ONLY these exact URLs for inline links):\n"
            + "\n".join(
                [f"- {src.get('name')}: {src.get('url')}"]
                + [f"- {item.get('text')}: {item.get('url')}" for item in (src.get('link_candidates') or [])[:10]]
            )
            + f"\nExtracted text:\n{src.get('text', '')[:7000]}"
        )
    return "\n\n".join(blocks)


def _retry_guidance(locale: str, feedback: list[str] | None) -> str:
    if not feedback:
        return ""
    relevant = [str(item).split(":", 1)[-1] for item in feedback if str(item).startswith(f"{locale}:")]
    if not relevant:
        return ""
    hints = {
        "title_length": "Keep the headline inside the requested length range.",
        "description_length": "Rewrite the SEO description inside the requested character range.",
        "summary_bullets": "Provide at least 3 concrete summary bullets.",
        "sections": "Provide at least 4 substantial sections.",
        "article_too_short": "The previous draft was too short. Produce at least 650 words and make each section substantively useful without padding or repetition.",
        "malformed_sections": "Every section must have a non-empty heading and one or more non-empty paragraphs.",
        "model_meta_language": "Remove model/meta commentary and write only publication-ready journalism.",
        "inline_links": "Add at least 2 natural inline link placements in the article body. Use only exact URLs listed in Allowed link targets and attach links to meaningful source, company, product, or report names.",
        "malformed_inline_links": "Every inline link must contain non-empty text and an exact http(s) URL from the supplied allowed link targets.",
        "missing_edition": "Return the complete requested language edition.",
    }
    instructions = [hints.get(code, f"Correct the failed quality check: {code}.") for code in relevant]
    if locale == "ar":
        return "\n\nهذه إعادة محاولة بعد رفض المسودة السابقة في بوابة الجودة. التعليمات التالية إلزامية:\n- " + "\n- ".join(instructions)
    return "\n\nThis is a retry after the previous draft failed the quality gate. The following corrections are mandatory:\n- " + "\n- ".join(instructions)


def _write_locale(story: dict, usable: list[dict], locale: str, settings: dict, quality_feedback: list[str] | None = None) -> dict:
    joined_sources = _source_text(usable)
    retry_guidance = _retry_guidance(locale, quality_feedback)
    if locale == "ar":
        prompt = f"""
أنت محرر تقني عربي دقيق لمنصة مِخبار. اكتب نسخة عربية أصلية من الخبر اعتماداً حصراً على المصادر أدناه، من دون ترجمة حرفية ومن دون اختراع أي معلومة.

القصة: {story.get('title')}
التصنيف: {story.get('category_label')} ({story.get('category')})
وقت المصدر: {story.get('published_at')}

المصادر:
{joined_sources}

أخرج JSON صالحاً فقط:
{{
  "title":"عنوان عربي صحفي واضح ومباشر، استهدف 40-60 حرفاً ولا تتجاوز 62 حرفاً إلا للضرورة",
  "description":"وصف SEO دقيق وجذاب من 115-155 حرفاً يشرح الخبر بلا حشو",
  "deck":"مقدمة قصيرة من جملة أو جملتين",
  "summary_bullets":["3 إلى 5 نقاط"],
  "sections":[{{"heading":"عنوان قسم","paragraphs":[{{"text":"فقرة صحفية طبيعية تتضمن عند الحاجة اسم مصدر أو شركة","links":[{{"text":"اسم المصدر أو الكيان كما يظهر حرفياً في text","url":"رابط مسموح به حرفياً من Allowed link targets"}}]}}]}}],
  "tags":["4 إلى 8 وسوم"],
  "entities":["الكيانات الرئيسية"],
  "article_type":"news",
  "confidence_note":"ملاحظة داخلية قصيرة"
}}

الشروط: 650-1000 كلمة عربية، 4-7 أقسام، لغة صحفية تقنية طبيعية، ضع اسم الشركة أو المنتج والحدث الأساسي مبكرًا في العنوان، تجنب العناوين العامة والـClickbait، فرّق بين الحقائق وما تعلنه الشركات، لا تستخدم رأياً شخصياً، ولا تنقل جملاً طويلة حرفياً. اجعل كل فقرة كائناً يحوي text وlinks. أدرج 2-4 روابط مضمّنة طبيعية داخل متن المقال على الأقل، ويفضل توزيعها على أقسام مختلفة. يجب أن يكون نص الرابط موجوداً حرفياً داخل text وأن يكون url مطابقاً تماماً لأحد Allowed link targets أعلاه. لا تخترع أي رابط ولا تضع الرابط خاماً في النص.{retry_guidance}
""".strip()
    else:
        prompt = f"""
You are the English technology editor for Mikhbar. Write an original English news article based ONLY on the supplied source material. Do not translate the Arabic edition and do not invent facts, prices, dates, specifications, quotes, or context that is absent from the sources.

Candidate story: {story.get('title')}
Category: {story.get('category')} / {story.get('category_label')}
Source publication time: {story.get('published_at')}

Sources:
{joined_sources}

Return valid JSON only:
{{
  "title":"Clear factual headline; target 45-60 characters and avoid exceeding about 62 unless necessary",
  "description":"Accurate compelling SEO description of 120-155 characters",
  "deck":"One or two concise opening sentences",
  "summary_bullets":["3 to 5 concise points"],
  "sections":[{{"heading":"Section heading","paragraphs":[{{"text":"Natural news paragraph that can mention a source, company, product or report","links":[{{"text":"Exact anchor text as it appears in text","url":"Exact URL copied from Allowed link targets"}}]}}]}}],
  "tags":["4 to 8 useful tags or entity names"],
  "entities":["Main companies, products or technologies"],
  "article_type":"news",
  "confidence_note":"Short internal note about source confidence"
}}

Requirements: 650-1000 English words, 4-7 useful sections, professional technology-news style, put the primary entity and news action early in the headline, avoid clickbait and vague headlines, clearly attribute company claims when appropriate, no first-person opinion, and no long copied passages. Every paragraph must be an object with text and links. Add at least 2-4 natural inline link placements across the article body, preferably in different sections. Each link text must appear verbatim in the paragraph text, and each URL must exactly match one of the Allowed link targets above. Never invent a URL and never paste raw URLs into prose.{retry_guidance}
""".strip()

    article = _call_model(prompt, settings)
    required = ["title", "description", "deck", "summary_bullets", "sections", "tags"]
    missing = [key for key in required if not article.get(key)]
    if missing:
        raise RuntimeError(f"Generated {locale} output missing fields: {', '.join(missing)}")
    return article


def write_article(story: dict, source_pack: list[dict], settings: dict, quality_feedback: list[str] | None = None) -> dict:
    usable = [s for s in source_pack if s.get("ok") and (s.get("text") or s.get("feed_summary"))]
    if not usable:
        raise RuntimeError("No usable source text available")
    return {
        "ar": _write_locale(story, usable, "ar", settings, quality_feedback),
        "en": _write_locale(story, usable, "en", settings, quality_feedback),
    }
