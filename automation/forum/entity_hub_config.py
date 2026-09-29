from __future__ import annotations

MIN_PAIRED_STORIES = 8
MIN_THEME_COUNT = 3

# Deliberately curated. Entity hubs are not created from arbitrary NER output;
# a candidate must be strategically useful and then pass the coverage threshold.
ENTITY_CANDIDATES = {
    "openai": {
        "name": "OpenAI",
        "aliases": {
            "en": ("OpenAI", "ChatGPT"),
            "ar": ("OpenAI", "أوبن أي آي", "اوبن اي اي", "شات جي بي تي", "ChatGPT"),
        },
    },
    "microsoft": {
        "name": "Microsoft",
        "aliases": {
            "en": ("Microsoft", "Microsoft Copilot"),
            "ar": ("Microsoft", "مايكروسوفت", "كوبايلوت", "Microsoft Copilot"),
        },
    },
    "github": {
        "name": "GitHub",
        "aliases": {
            "en": ("GitHub", "GitHub Copilot"),
            "ar": ("GitHub", "جيت هاب", "غيت هاب", "GitHub Copilot"),
        },
    },
    "google": {
        "name": "Google",
        "aliases": {
            "en": ("Google", "Gemini"),
            "ar": ("Google", "جوجل", "غوغل", "Gemini", "جيميني"),
        },
    },
    "anthropic": {
        "name": "Anthropic",
        "aliases": {
            "en": ("Anthropic", "Claude"),
            "ar": ("Anthropic", "أنثروبيك", "انثروبيك", "Claude", "كلود"),
        },
    },
    "cloudflare": {
        "name": "Cloudflare",
        "aliases": {
            "en": ("Cloudflare",),
            "ar": ("Cloudflare", "كلاودفلير", "كلاود فلير"),
        },
    },
    "apple": {
        "name": "Apple",
        "aliases": {
            "en": ("Apple", "Apple Intelligence"),
            "ar": ("Apple", "آبل", "ابل", "Apple Intelligence"),
        },
    },
    "meta": {
        "name": "Meta",
        "aliases": {
            "en": ("Meta", "Llama"),
            "ar": ("Meta", "ميتا", "Llama", "لاما"),
        },
    },
    "nvidia": {
        "name": "NVIDIA",
        "aliases": {
            "en": ("NVIDIA", "Nvidia"),
            "ar": ("NVIDIA", "Nvidia", "إنفيديا", "انفيديا"),
        },
    },
    "amazon-web-services": {
        "name": "Amazon Web Services",
        "aliases": {
            "en": ("Amazon Web Services", "AWS"),
            "ar": ("Amazon Web Services", "AWS", "أمازون ويب سيرفيسز", "خدمات أمازون ويب"),
        },
    },
}

PILLAR_BY_CATEGORY = {
    "ai": "artificial-intelligence",
    "security": "cybersecurity",
    "robotics": "robotics",
}

GENERIC_THEME_TERMS = {
    "ai", "artificial intelligence", "technology", "tech", "software", "apps", "app",
    "security", "cybersecurity", "mobile", "web", "computing", "computer", "robotics",
    "automation", "news", "update", "updates", "platform", "model", "models",
    "الذكاء الاصطناعي", "تقنية", "التقنية", "برمجيات", "تطبيقات", "تطبيق",
    "الأمن السيبراني", "امن سيبراني", "الهواتف", "الويب", "الحواسيب", "الروبوتات",
    "الأتمتة", "اخبار", "أخبار", "تحديث", "تحديثات", "منصة", "نموذج", "نماذج",
}
