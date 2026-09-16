from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from html import unescape

import requests
from bs4 import BeautifulSoup


def _clean_text(text: str) -> str:
    text = unescape(text or "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _extract_page(url: str, user_agent: str) -> dict:
    headers = {"User-Agent": user_agent, "Accept": "text/html,application/xhtml+xml"}
    try:
        response = requests.get(url, headers=headers, timeout=18, allow_redirects=True)
        response.raise_for_status()
    except Exception as exc:
        return {"url": url, "ok": False, "error": str(exc), "text": ""}

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg", "nav", "footer", "header", "form", "aside"]):
        tag.decompose()

    title = _clean_text((soup.title.string if soup.title and soup.title.string else ""))
    meta = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
    description = _clean_text(meta.get("content", "") if meta else "")

    candidates = []
    for selector in ["article", "main", "[role='main']", ".article-body", ".post-content", ".entry-content"]:
        node = soup.select_one(selector)
        if node:
            candidates.append(node)
    root = max(candidates, key=lambda n: len(n.get_text(" ", strip=True)), default=soup.body or soup)

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
            "kind": "corroborating",
            "feed_title": source.get("title", ""),
            "feed_summary": "",
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


def _call_copilot(prompt: str) -> dict:
    if not shutil.which("copilot"):
        raise RuntimeError("GitHub Copilot CLI is not installed")
    if not (os.environ.get("GITHUB_TOKEN") or os.environ.get("COPILOT_GITHUB_TOKEN")):
        raise RuntimeError("GITHUB_TOKEN is required for Copilot CLI automation")

    command = [
        "copilot",
        "-p", prompt,
        "-s",
        "--no-ask-user",
        "--no-color",
        "--no-custom-instructions",
        "--no-auto-update",
    ]
    last_error = None
    for attempt in range(2):
        try:
            proc = subprocess.run(command, text=True, capture_output=True, timeout=150, env=os.environ.copy())
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


def write_article(story: dict, source_pack: list[dict], settings: dict) -> dict:
    usable = [s for s in source_pack if s.get("ok") and (s.get("text") or s.get("feed_summary"))]
    if not usable:
        raise RuntimeError("No usable source text available")

    source_text = []
    for index, src in enumerate(usable, 1):
        source_text.append(
            f"SOURCE {index}\n"
            f"Name: {src.get('name')}\n"
            f"Type: {src.get('kind')}\n"
            f"URL: {src.get('url')}\n"
            f"Feed title: {src.get('feed_title', '')}\n"
            f"Feed summary: {src.get('feed_summary', '')}\n"
            f"Page title: {src.get('title', '')}\n"
            f"Page description: {src.get('description', '')}\n"
            f"Extracted text:\n{src.get('text', '')[:7000]}"
        )

    joined_sources = "\n\n".join(source_text)
    prompt = f"""
أنت المحرر الآلي لمنصة RDWAN Tech العربية. مهمتك كتابة خبر تقني أصلي اعتماداً حصراً على المادة المصدرية أدناه.

القصة المرشحة:
العنوان الأصلي: {story.get('title')}
التصنيف: {story.get('category_label')} ({story.get('category')})
درجة الترند الداخلية: {story.get('trend', {}).get('score')}
وقت النشر لدى المصدر: {story.get('published_at')}

المصادر:
{joined_sources}

اكتب مقالاً عربياً أصلياً متكاملاً. ركز على: ما الذي حدث، التفاصيل المؤكدة، لماذا يهم، السياق التقني، وما الذي ينبغي متابعته لاحقاً. لا تجعل المقال إعلاناً للشركة. إذا كان المصدر بياناً رسمياً فصغ ما تقوله الشركة على أنه إعلان أو ادعاء من الشركة عندما يلزم. إذا اختلفت المصادر فاذكر الاختلاف. لا تضف أي معلومة غير موجودة في المصادر.

أخرج JSON صالحاً فقط، بلا Markdown وبلا أي نص قبله أو بعده، بهذا الشكل:
{{
  "title": "عنوان عربي واضح وغير مضلل، يفضل 45-85 حرفاً",
  "description": "وصف SEO دقيق بين 120 و165 حرفاً",
  "deck": "مقدمة قصيرة من جملة أو جملتين",
  "summary_bullets": ["3 إلى 5 نقاط مختصرة"],
  "sections": [
    {{"heading": "عنوان قسم", "paragraphs": ["فقرة", "فقرة"]}}
  ],
  "tags": ["4 إلى 8 وسوم عربية أو أسماء كيانات"],
  "entities": ["الشركات أو المنتجات أو التقنيات الرئيسية"],
  "article_type": "news",
  "confidence_note": "سطر داخلي قصير يصف مدى اعتماد المقال على مصدر رسمي أو عدة مصادر"
}}

الشروط:
- استهدف 650 إلى 1100 كلمة عربية إجمالاً.
- أنشئ 4 إلى 7 أقسام مفيدة بلا حشو.
- لا تستخدم عبارات مثل «بحسب معلوماتي» أو «كمساعد».
- لا تخترع سعراً أو تاريخ إتاحة أو مواصفات إذا لم تذكرها المصادر.
- لا تضع روابط داخل نص الفقرات؛ روابط المصادر ستضاف آلياً.
- لا تنقل جملاً طويلة حرفياً من المصادر؛ لخص وأعد الصياغة.
- لا تكرر المقدمة في الأقسام.
""".strip()

    article = _call_copilot(prompt)
    required = ["title", "description", "deck", "summary_bullets", "sections", "tags"]
    missing = [k for k in required if not article.get(k)]
    if missing:
        raise RuntimeError(f"Copilot output missing fields: {', '.join(missing)}")
    return article
