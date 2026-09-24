from __future__ import annotations

import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORUM = ROOT / "forum"
ORIGIN = "https://mikhbar.website"
UPDATED = "2026-09-24"
SOCIAL_IMAGE = ORIGIN + "/assets/social/home.jpg"

PILLARS = {
    "artificial-intelligence": {
        "category": "ai",
        "related": ("cybersecurity", "robotics"),
        "ar": {
            "title": "دليل الذكاء الاصطناعي: النماذج والأدوات والوكلاء | مِخبار",
            "description": "دليل مِخبار لفهم الذكاء الاصطناعي الحديث: النماذج التوليدية والوسائط المتعددة والوكلاء وأدوات AI وكيفية تقييمها ومتابعة تطورها.",
            "h1": "دليل الذكاء الاصطناعي",
            "deck": "مرجع دائم لفهم النماذج التوليدية وأدوات AI والوكلاء الذكيين وكيف تتحول التقنيات الجديدة إلى منتجات واستخدامات عملية.",
            "category_label": "الذكاء الاصطناعي",
            "guide_label": "دليل دائم",
            "latest": "أحدث تغطية الذكاء الاصطناعي",
            "category_cta": "كل أخبار الذكاء الاصطناعي",
            "sections": (
                ("ما المقصود بالذكاء الاصطناعي الحديث؟", "الذكاء الاصطناعي الحديث ليس منتجًا واحدًا، بل طبقات من النماذج والخدمات والأدوات. النماذج اللغوية الكبيرة تتعامل مع النصوص والبرمجة والاستدلال، بينما تضيف النماذج متعددة الوسائط الصور والصوت والفيديو. فوق هذه النماذج تظهر تطبيقات مثل المساعدات الذكية وأدوات البرمجة والبحث والتصميم. لفهم أي خبر جديد، من المهم التمييز بين النموذج الأساسي، والمنتج الذي يستخدمه، والبنية السحابية التي تشغله."),
                ("النماذج التوليدية والوسائط المتعددة", "تولد النماذج التوليدية نصوصًا وصورًا وصوتًا وفيديو وكودًا اعتمادًا على أنماط تعلمتها من بيانات كبيرة. لكن جودة النموذج لا تقاس باسم الإصدار فقط؛ بل بالسياق الذي يستطيع التعامل معه، ودقة الاستجابات، وسرعة التنفيذ، وتكلفة الاستخدام، ودعم الأدوات، وسياسات الخصوصية. لذلك تركز تغطية مِخبار على ما تغير فعليًا بين الإصدارات بدل الاكتفاء بإعلانات الشركات."),
                ("الوكلاء الذكيون والأتمتة", "الوكيل الذكي يضيف طبقة تنفيذ فوق النموذج: يستطيع استخدام أدوات وواجهات API وملفات وقواعد بيانات وخدمات خارجية لتنفيذ سلسلة خطوات بدل إعطاء إجابة واحدة. هذا يجعل الحدود بين الذكاء الاصطناعي والأتمتة أكثر تقاربًا، ويزيد أهمية الصلاحيات والمراقبة وسجلات التنفيذ. عند تقييم وكيل جديد، يجب النظر إلى قدرته على التخطيط، واستدعاء الأدوات، والتعامل مع الأخطاء، والعودة إلى المستخدم عند الحاجة."),
                ("كيف نقيم أدوات الذكاء الاصطناعي؟", "التقييم العملي يبدأ بالسؤال: ما المشكلة التي تحلها الأداة؟ بعد ذلك نراجع جودة النتائج، وإمكانية التحقق منها، والخصوصية، والتكلفة، والتكامل مع سير العمل، وحدود الاستخدام. الأدوات التي تبدو متشابهة قد تختلف جذريًا في مكان معالجة البيانات أو الاحتفاظ بها أو في قدرتها على الاتصال بخدمات أخرى. لهذا نربط الأخبار بالمصادر الأصلية والتوثيق الرسمي كلما أمكن."),
                ("ما الاتجاهات التي تستحق المتابعة؟", "أبرز المسارات التي تستحق المتابعة تشمل النماذج مفتوحة الأوزان، والذكاء الاصطناعي على الجهاز، والوكلاء المتخصصين، والنماذج متعددة الوسائط، وتكامل AI مع البحث والبرمجة والأمن والروبوتات. كما أن كفاءة الاستدلال واستهلاك الطاقة وتكلفة الحوسبة أصبحت عوامل تنافسية مهمة بجانب جودة النموذج نفسها."),
            ),
            "keywords": ("الذكاء الاصطناعي", "AI", "النماذج التوليدية", "الوكلاء الذكيون", "ChatGPT", "Gemini", "Claude"),
        },
        "en": {
            "title": "Artificial Intelligence Guide: Models, Tools & AI Agents | Mikhbar",
            "description": "Mikhbar's evergreen guide to modern artificial intelligence, generative models, multimodal AI, agents, AI tools, evaluation and the trends shaping the field.",
            "h1": "Artificial Intelligence Guide",
            "deck": "An evergreen reference for understanding generative models, AI tools and agents, and how new capabilities move from research into products and practical workflows.",
            "category_label": "Artificial Intelligence",
            "guide_label": "Evergreen guide",
            "latest": "Latest artificial intelligence coverage",
            "category_cta": "All artificial intelligence news",
            "sections": (
                ("What does modern artificial intelligence mean?", "Modern AI is not one product. It is a stack of models, services and applications. Large language models handle language, code and reasoning tasks, while multimodal systems add images, audio and video. Products such as assistants, coding tools, search systems and creative applications sit on top of these models. Understanding a new announcement starts with separating the foundation model from the product and infrastructure built around it."),
                ("Generative and multimodal models", "Generative systems create text, images, audio, video and code from patterns learned during training. Model quality cannot be reduced to a version name: context capacity, reliability, latency, cost, tool use and privacy policies all matter. Mikhbar therefore focuses on material capability changes, deployment details and documented limitations rather than repeating launch claims."),
                ("AI agents and automation", "An AI agent adds execution to a model. It can use tools, APIs, files, databases and external services to complete a sequence of actions rather than produce a single response. This makes permissions, observability and recovery behavior important. Useful agent evaluation looks at planning, tool selection, error handling, state, human approval points and the boundaries placed around autonomous actions."),
                ("How should AI tools be evaluated?", "Start with the task the tool is supposed to solve, then examine output quality, verifiability, privacy, cost, integrations and usage limits. Products that look similar may process or retain data differently, expose different control surfaces or support different enterprise safeguards. Source-linked reporting and official documentation are therefore essential when comparing fast-moving AI products."),
                ("Trends worth watching", "Key trends include open-weight models, on-device AI, specialized agents, multimodal systems and deeper integration with search, software development, security and robotics. Inference efficiency, energy use and compute cost are also becoming competitive factors alongside benchmark quality and feature breadth."),
            ),
            "keywords": ("artificial intelligence", "AI", "generative AI", "AI agents", "large language models", "multimodal AI", "AI tools"),
        },
    },
    "cybersecurity": {
        "category": "security",
        "related": ("artificial-intelligence", "robotics"),
        "ar": {
            "title": "دليل الأمن السيبراني: الثغرات والهجمات والحماية | مِخبار",
            "description": "دليل مِخبار لفهم الأمن السيبراني والثغرات والهجمات والبرمجيات الخبيثة والخصوصية والتحديثات الأمنية وكيفية قراءة التنبيهات والمخاطر.",
            "h1": "دليل الأمن السيبراني",
            "deck": "مرجع دائم لفهم الثغرات والهجمات والبرمجيات الخبيثة والخصوصية وكيف تتحول التنبيهات التقنية إلى مخاطر وإجراءات حماية واضحة.",
            "category_label": "الأمن السيبراني",
            "guide_label": "دليل دائم",
            "latest": "أحدث تغطية الأمن السيبراني",
            "category_cta": "كل أخبار الأمن السيبراني",
            "sections": (
                ("ما هو الأمن السيبراني؟", "الأمن السيبراني هو مجموعة ممارسات وتقنيات لحماية الأجهزة والحسابات والشبكات والتطبيقات والبيانات من الوصول غير المصرح به أو التعطيل أو السرقة. لا يقتصر على برامج مكافحة الفيروسات؛ بل يشمل إدارة الهوية والتحديثات والنسخ الاحتياطي والتشفير والمراقبة والتعامل مع الحوادث وسلاسل توريد البرمجيات."),
                ("الثغرات وأيام الصفر", "الثغرة الأمنية هي ضعف يمكن استغلاله لتجاوز حماية متوقعة. بعض الثغرات تحصل على معرف CVE ودرجة خطورة، لكن الدرجة وحدها لا تحدد الأولوية. الأهم هو معرفة ما إذا كان الاستغلال نشطًا، وما الأنظمة المتأثرة، وهل يتطلب الهجوم مصادقة أو وصولًا محليًا، وما إذا كان هناك تصحيح أو إجراء تخفيف. مصطلح صفر يوم يشير عادة إلى ثغرة تُستغل قبل توفر معالجة كافية أو قبل معرفة المدافعين بها على نطاق واسع."),
                ("البرمجيات الخبيثة والتصيد وسرقة الهوية", "الهجمات الحديثة تجمع غالبًا بين الهندسة الاجتماعية والبرمجيات الخبيثة وسرقة جلسات تسجيل الدخول أو الرموز المميزة. لذلك لا تكفي كلمة مرور قوية وحدها. المصادقة متعددة العوامل، ومديرو كلمات المرور، ومفاتيح المرور، والتحقق من الروابط والطلبات غير المعتادة، وتقليل الصلاحيات، كلها طبقات تقلل فرص نجاح الهجوم أو تحد من أثره."),
                ("الخصوصية وتسريبات البيانات", "الحوادث الأمنية لا تعني دائمًا اختراق جهاز؛ فقد تبدأ من إعداد سحابي مكشوف أو قاعدة بيانات مسربة أو جمع بيانات أوسع من اللازم. عند قراءة خبر تسريب، يجب التمييز بين عدد الحسابات المتأثرة، ونوع البيانات، وما إذا كانت كلمات المرور مشفرة، وهل هناك دليل على إساءة استخدام المعلومات، والإجراءات التي أعلنتها الجهة المتأثرة."),
                ("كيف تقرأ تنبيهًا أمنيًا؟", "ابدأ بالمصدر: جهة حكومية مختصة أو الشركة المطورة أو باحث موثوق. ثم تحقق من المنتجات والإصدارات المتأثرة، وحالة الاستغلال، والحلول المتاحة. في المؤسسات تضاف أسئلة مثل وجود الأصل داخل الشبكة وإمكانية الوصول إليه ومستوى الامتيازات. الهدف هو تحويل الخبر إلى قرار: تحديث، تخفيف، مراقبة أو عدم تأثر."),
            ),
            "keywords": ("الأمن السيبراني", "الثغرات", "CVE", "Zero Day", "البرمجيات الخبيثة", "الخصوصية", "حماية البيانات"),
        },
        "en": {
            "title": "Cybersecurity Guide: Vulnerabilities, Attacks & Protection | Mikhbar",
            "description": "Mikhbar's evergreen cybersecurity guide covering vulnerabilities, zero-days, malware, privacy, data breaches, security updates and how to interpret risk.",
            "h1": "Cybersecurity Guide",
            "deck": "An evergreen reference for understanding vulnerabilities, attacks, malware, privacy and how technical advisories translate into practical risk and protection decisions.",
            "category_label": "Cybersecurity",
            "guide_label": "Evergreen guide",
            "latest": "Latest cybersecurity coverage",
            "category_cta": "All cybersecurity news",
            "sections": (
                ("What is cybersecurity?", "Cybersecurity is the set of practices and technologies used to protect devices, identities, networks, applications and data from unauthorized access, disruption or theft. It extends far beyond antivirus software and includes identity management, patching, backups, encryption, monitoring, incident response and software supply-chain security."),
                ("Vulnerabilities and zero-days", "A vulnerability is a weakness that can be used to bypass an expected security boundary. Many vulnerabilities receive CVE identifiers and severity scores, but a score alone does not establish priority. Active exploitation, affected products, required access, authentication conditions and the availability of a patch or mitigation are all critical. A zero-day generally describes a vulnerability exploited before defenders have an adequate fix or broad awareness."),
                ("Malware, phishing and identity theft", "Modern attacks often combine social engineering with malware, session theft or stolen authentication tokens. Strong passwords alone are not enough. Multi-factor authentication, password managers, passkeys, careful verification of unusual requests and least-privilege access all reduce the chance of compromise or limit the blast radius after one occurs."),
                ("Privacy and data breaches", "A security incident does not always begin with a hacked laptop. It may result from exposed cloud storage, a leaked database or excessive data collection. When reading a breach report, distinguish the number of affected accounts, the sensitivity of the data, whether passwords were hashed, whether misuse has been observed and what remediation the organization has actually taken."),
                ("How to read a security advisory", "Start with the source: a responsible vendor, a national cybersecurity agency or a credible researcher. Confirm affected products and versions, exploitation status and available remediation. Organizations then add asset exposure, reachability and privilege context. The goal is to turn a headline into an action: patch, mitigate, monitor or document that the environment is not affected."),
            ),
            "keywords": ("cybersecurity", "vulnerabilities", "CVE", "zero-day", "malware", "privacy", "data breach"),
        },
    },
    "robotics": {
        "category": "robotics",
        "related": ("artificial-intelligence", "cybersecurity"),
        "ar": {
            "title": "دليل الروبوتات: الروبوتات البشرية وPhysical AI | مِخبار",
            "description": "دليل مِخبار لفهم الروبوتات البشرية والصناعية والأنظمة الذاتية والحساسات والتحكم وPhysical AI وكيفية تقييم قدرات الروبوتات الحديثة.",
            "h1": "دليل الروبوتات والذكاء الاصطناعي المادي",
            "deck": "مرجع دائم لفهم الروبوتات البشرية والصناعية والأنظمة الذاتية والحساسات والتحكم والانتقال من نماذج AI الرقمية إلى العالم المادي.",
            "category_label": "الروبوتات",
            "guide_label": "دليل دائم",
            "latest": "أحدث تغطية الروبوتات",
            "category_cta": "كل أخبار الروبوتات",
            "sections": (
                ("ما هي الروبوتات الحديثة؟", "الروبوت الحديث يجمع بين جسم ميكانيكي وحساسات ومحركات ووحدة حوسبة وبرمجيات تحكم. بعض الأنظمة تعمل في بيئات منظمة مثل خطوط الإنتاج، بينما تحاول الروبوتات البشرية والمتنقلة العمل في بيئات أكثر تنوعًا. الفرق المهم هو أن الأداء لا يعتمد على نموذج AI فقط؛ بل على جودة الإدراك والتحكم والسلامة والاعتمادية والهندسة الميكانيكية."),
                ("الروبوتات البشرية والصناعية", "الروبوتات الصناعية متخصصة عادة في مهام متكررة ودقيقة، بينما تسعى الروبوتات البشرية إلى الاستفادة من بيئات صممت أصلًا للبشر مثل الأبواب والسلالم وأدوات العمل. الشكل البشري لا يعني بالضرورة ذكاءً أعلى؛ لذلك يجب تقييم القدرة الفعلية على المشي والتقاط الأشياء والعمل لفترات طويلة والتعامل مع تغير البيئة بدل التركيز على العروض القصيرة."),
                ("Physical AI والإدراك والتحكم", "يشير Physical AI إلى الأنظمة التي تربط التعلم والإدراك باتخاذ قرارات في العالم المادي. الكاميرات ومستشعرات العمق والقوة واللمس تساعد الروبوت على تقدير البيئة، بينما تحول خوارزميات التخطيط والتحكم تلك التقديرات إلى حركة. النماذج متعددة الوسائط قد تضيف فهمًا لغويًا وبصريًا، لكنها لا تلغي الحاجة إلى حلقات تحكم سريعة وآمنة."),
                ("كيف تقاس قدرات الروبوت؟", "العروض المرئية مفيدة لكنها لا تكفي. مؤشرات أكثر معنى تشمل نسبة نجاح المهمة، والوقت اللازم، والقدرة على التكرار، وعمر البطارية، والحمولة، والدقة، ومعدل التدخل البشري، والأداء خارج المختبر. في التطبيقات التجارية تضاف تكلفة التشغيل والصيانة والسلامة والتكامل مع الأنظمة الحالية."),
                ("ما الذي يستحق المتابعة؟", "المجالات الأسرع تطورًا تشمل الروبوتات البشرية للمصانع والخدمات، والروبوتات المتنقلة للمخازن، والطائرات والأنظمة الذاتية، ونماذج الرؤية-اللغة-الفعل، والمحاكاة لتدريب السياسات، والحوسبة الطرفية. كما أن الأمن السيبراني للروبوتات سيزداد أهمية كلما اتصلت هذه الأنظمة بالخدمات السحابية والوكلاء الذكيين."),
            ),
            "keywords": ("الروبوتات", "الروبوتات البشرية", "Physical AI", "الأنظمة الذاتية", "الحساسات", "التحكم", "التصنيع الذكي"),
        },
        "en": {
            "title": "Robotics Guide: Humanoids, Autonomous Systems & Physical AI | Mikhbar",
            "description": "Mikhbar's evergreen robotics guide covering humanoids, industrial robots, autonomous systems, sensors, control, physical AI and how robot capability is evaluated.",
            "h1": "Robotics and Physical AI Guide",
            "deck": "An evergreen reference for understanding humanoid and industrial robots, autonomous systems, sensing, control and the move from digital AI models into the physical world.",
            "category_label": "Robotics",
            "guide_label": "Evergreen guide",
            "latest": "Latest robotics coverage",
            "category_cta": "All robotics news",
            "sections": (
                ("What are modern robots?", "A modern robot combines a mechanical body, sensors, actuators, compute and control software. Some systems operate in structured environments such as production lines, while humanoid and mobile robots attempt to work in more varied spaces. Performance therefore depends on perception, control, safety, reliability and mechanical engineering as much as it depends on an AI model."),
                ("Humanoid and industrial robots", "Industrial robots are typically optimized for repetitive and precise tasks. Humanoids aim to take advantage of environments originally designed for people, including stairs, doors and human-scale tools. A human shape does not automatically imply greater intelligence, so useful evaluation focuses on sustained walking, manipulation, task completion, recovery from errors and operation outside carefully staged demonstrations."),
                ("Physical AI, perception and control", "Physical AI connects learning and perception with decisions in the real world. Cameras, depth sensors, force sensing and tactile input help estimate the environment, while planning and control algorithms translate those estimates into motion. Multimodal models can add language and visual understanding, but they do not replace the fast, safety-critical control loops required for physical machines."),
                ("How should robot capability be measured?", "Visual demonstrations are informative but incomplete. More useful measures include task success rate, completion time, repeatability, battery life, payload, precision, human intervention rate and performance outside the laboratory. Commercial deployments also depend on operating cost, maintenance, safety certification and integration with existing systems."),
                ("Trends worth following", "Fast-moving areas include humanoids for factories and services, warehouse mobile robots, autonomous drones and vehicles, vision-language-action models, simulation for policy training and edge computing. Cybersecurity is also becoming more important as robots connect to cloud services, remote management systems and AI agents."),
            ),
            "keywords": ("robotics", "humanoid robots", "physical AI", "autonomous systems", "robot sensors", "robot control", "smart manufacturing"),
        },
    },
}


def load_posts(locale: str) -> list[dict]:
    path = FORUM / f"posts-{locale}.json"
    if locale == "ar" and not path.exists():
        path = FORUM / "posts.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError):
        return []
    return list(payload.get("posts", []) if isinstance(payload, dict) else payload or [])


def public_path(value: str | None) -> str:
    path = str(value or "").strip()
    if path.startswith("https://") or path.startswith("http://"):
        return path
    if path.startswith("/forum/"):
        path = path[len("/forum"):]
    if not path.startswith("/"):
        path = "/" + path
    return path


def latest_for(posts: list[dict], category: str, limit: int = 6) -> list[dict]:
    return [post for post in posts if str(post.get("categorySlug") or "") == category][:limit]


def publisher_schema() -> dict:
    return {
        "@type": "NewsMediaOrganization",
        "@id": ORIGIN + "/#publisher",
        "name": "Mikhbar",
        "alternateName": "مِخبار",
        "url": ORIGIN + "/",
        "logo": {"@type": "ImageObject", "url": ORIGIN + "/assets/brand/mikhbar/06-web-ready/icon/mikhbar-app-icon-512.png"},
    }


def header(locale: str) -> str:
    ar = locale == "ar"
    home = "الرئيسية" if ar else "Home"
    latest = "أحدث الأخبار" if ar else "Latest"
    sections = "الأقسام" if ar else "Sections"
    about = "عن مِخبار" if ar else "About Mikhbar"
    switch = "EN" if ar else "عربي"
    other = "en" if ar else "ar"
    return f'''<header class="rt-site-header"><div class="rt-navbar">
<a class="mikhbar-brand" href="/{locale}/" aria-label="Mikhbar"><span class="mikhbar-brand-mark"><img src="/assets/brand/mikhbar/06-web-ready/icon/mikhbar-logo-mark.png" alt="" width="64" height="64"></span><span class="mikhbar-brand-copy"><strong>{'مِخبار' if ar else 'Mikhbar'}</strong><small dir="ltr">MIKHBAR</small></span></a>
<nav class="nav-links rt-platform-nav" aria-label="{'التنقل الرئيسي' if ar else 'Main navigation'}"><a href="/{locale}/">{home}</a><a href="/{locale}/#latest">{latest}</a><a href="/{locale}/#sections">{sections}</a><a href="/{locale}/guides/">{'الأدلة' if ar else 'Guides'}</a><a href="/about/">{about}</a><a class="rt-lang-switch" href="/{other}/guides/">{switch}</a></nav>
</div></header>'''


def categories(locale: str, active: str = "") -> str:
    ar = locale == "ar"
    labels = {
        "ai": "الذكاء الاصطناعي" if ar else "AI",
        "robotics": "الروبوتات" if ar else "Robotics",
        "automation": "الأتمتة" if ar else "Automation",
        "mobile": "الهواتف" if ar else "Mobile",
        "computers": "الحواسيب" if ar else "Computers",
        "apps": "التطبيقات والبرامج" if ar else "Apps & Software",
        "web": "الويب" if ar else "Web",
        "social": "التواصل الاجتماعي" if ar else "Social",
        "security": "الأمن السيبراني" if ar else "Security",
    }
    links = []
    for slug, label in labels.items():
        current = ' aria-current="page"' if slug == active else ""
        links.append(f'<a href="/{locale}/{slug}/"{current}>{label}</a>')
    return '<nav class="rt-categories" aria-label="Sections"><div class="rt-shell rt-category-scroll">' + "".join(links) + "</div></nav>"


def latest_html(locale: str, rows: list[dict]) -> str:
    out = []
    for post in rows:
        title = escape(str(post.get("title") or ""))
        excerpt_text = escape(str(post.get("excerpt") or ""))
        url = escape(public_path(post.get("url")), quote=True)
        date = escape(str(post.get("dateLabel") or str(post.get("date") or "")[:10]))
        out.append(
            f'<a class="rt-feed-item" href="{url}"><div class="rt-feed-copy"><h3>{title}</h3>'
            f'<p>{excerpt_text}</p><div class="rt-feed-time">{date}</div></div></a>'
        )
    return "".join(out)


def guide_schema(locale: str, slug: str, config: dict) -> str:
    canonical = f"{ORIGIN}/{locale}/guides/{slug}/"
    other = "en" if locale == "ar" else "ar"
    data = {
        "@context": "https://schema.org",
        "@graph": [
            publisher_schema(),
            {
                "@type": "Article",
                "@id": canonical + "#article",
                "headline": config["title"].split(" | ")[0],
                "description": config["description"],
                "datePublished": UPDATED,
                "dateModified": UPDATED,
                "inLanguage": locale,
                "mainEntityOfPage": canonical,
                "author": {"@type": "Organization", "name": "Mikhbar Editorial", "url": ORIGIN + f"/{locale}/guides/"},
                "publisher": {"@id": ORIGIN + "/#publisher"},
                "image": [SOCIAL_IMAGE],
                "keywords": list(config["keywords"]),
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "مِخبار" if locale == "ar" else "Mikhbar", "item": ORIGIN + f"/{locale}/"},
                    {"@type": "ListItem", "position": 2, "name": "الأدلة" if locale == "ar" else "Guides", "item": ORIGIN + f"/{locale}/guides/"},
                    {"@type": "ListItem", "position": 3, "name": config["h1"]},
                ],
            },
            {"@type": "WebPage", "url": canonical, "inLanguage": locale, "isPartOf": {"@id": ORIGIN + "/#publisher"}, "alternateName": PILLARS[slug][other]["h1"]},
        ],
    }
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")


def guide_page(locale: str, slug: str, spec: dict, posts: list[dict]) -> str:
    config = spec[locale]
    ar = locale == "ar"
    direction = "rtl" if ar else "ltr"
    other = "en" if ar else "ar"
    canonical = f"{ORIGIN}/{locale}/guides/{slug}/"
    alternate = f"{ORIGIN}/{other}/guides/{slug}/"
    recent = latest_for(posts, spec["category"])
    toc = "".join(f'<li><a href="#section-{idx}">{escape(title)}</a></li>' for idx, (title, _body) in enumerate(config["sections"], 1))
    sections = "".join(
        f'<section class="rt-prose" id="section-{idx}"><h2>{escape(title)}</h2><p>{escape(body)}</p></section>'
        for idx, (title, body) in enumerate(config["sections"], 1)
    )
    related = "".join(
        f'<a class="rt-topic-card" href="/{locale}/guides/{target}/"><b>{escape(PILLARS[target][locale]["h1"])}</b><span>{"اقرأ الدليل" if ar else "Read the guide"}</span></a>'
        for target in spec["related"]
    )
    schema = guide_schema(locale, slug, config)
    updated_label = "آخر تحديث" if ar else "Last updated"
    contents_label = "في هذا الدليل" if ar else "In this guide"
    related_label = "أدلة مرتبطة" if ar else "Related guides"
    source_note = "هذا دليل تحريري دائم من مِخبار ويُحدَّث عند تغير المفاهيم أو التقنيات الأساسية." if ar else "This is an evergreen Mikhbar editorial guide, updated when the underlying concepts or technologies materially change."
    return f'''<!DOCTYPE html><html lang="{locale}" dir="{direction}"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#ffffff">
<title>{escape(config['title'])}</title><meta name="description" content="{escape(config['description'], quote=True)}"><meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
<link rel="canonical" href="{canonical}"><link rel="alternate" hreflang="ar" href="{ORIGIN}/ar/guides/{slug}/"><link rel="alternate" hreflang="en" href="{ORIGIN}/en/guides/{slug}/"><link rel="alternate" hreflang="x-default" href="{ORIGIN}/en/guides/{slug}/">
<meta property="og:type" content="article"><meta property="og:site_name" content="{'مِخبار' if ar else 'Mikhbar'}"><meta property="og:title" content="{escape(config['title'], quote=True)}"><meta property="og:description" content="{escape(config['description'], quote=True)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{SOCIAL_IMAGE}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(config['title'], quote=True)}"><meta name="twitter:description" content="{escape(config['description'], quote=True)}"><meta name="twitter:image" content="{SOCIAL_IMAGE}">
<link rel="stylesheet" href="/styles.css"><link rel="stylesheet" href="/forum.css?v=20260924-guides1"><link rel="stylesheet" href="/forum-media.css"><link rel="icon" type="image/png" href="/assets/brand/mikhbar/06-web-ready/favicon/favicon-large.png?v=20260922-tab4">
<script type="application/ld+json">{schema}</script><style>.rt-guide-meta{{color:#6b6b6b;margin:.75rem 0 1.5rem}}.rt-guide-toc{{padding:1rem 1.25rem;border:1px solid #e3e3df;border-radius:18px;margin:1.5rem 0}}.rt-guide-toc ul{{margin:.6rem 0 0;padding-inline-start:1.4rem}}.rt-guide-toc li{{margin:.35rem 0}}.rt-guide-toc a{{color:inherit}}.rt-topic-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}}.rt-topic-card{{display:flex;flex-direction:column;gap:6px;padding:16px;border:1px solid #e3e3df;border-radius:16px;text-decoration:none;color:inherit}}.rt-guide-note{{margin-top:1.5rem;font-size:.95rem;color:#666}}</style></head>
<body class="rt-locale-{locale}" data-pillar-guide="{slug}">{header(locale)}<main class="rt-main" id="main">{categories(locale, spec['category'])}<div class="rt-shell">
<section class="rt-category-hero"><nav class="rt-breadcrumbs"><a href="/{locale}/">{'مِخبار' if ar else 'Mikhbar'}</a><span>›</span><a href="/{locale}/guides/">{'الأدلة' if ar else 'Guides'}</a><span>›</span><span>{escape(config['h1'])}</span></nav><div class="rt-category-title"><span class="rt-label">{escape(config['guide_label'])}</span><h1>{escape(config['h1'])}</h1><p>{escape(config['deck'])}</p><div class="rt-guide-meta">{updated_label}: {UPDATED}</div></div></section>
<article class="rt-section rt-guide"><nav class="rt-guide-toc" aria-label="{contents_label}"><strong>{contents_label}</strong><ul>{toc}</ul></nav>{sections}
<p class="rt-guide-note">{source_note}</p></article>
<section class="rt-section"><header class="rt-section-head"><div><h2>{escape(config['latest'])}</h2></div><a href="/{locale}/{spec['category']}/">{escape(config['category_cta'])}</a></header><div class="rt-feed">{latest_html(locale, recent)}</div></section>
<section class="rt-section"><header class="rt-section-head"><div><h2>{related_label}</h2></div><a href="/{locale}/guides/">{'كل الأدلة' if ar else 'All guides'}</a></header><div class="rt-topic-grid">{related}</div></section>
</div></main><footer class="rt-footer"><div class="rt-shell rt-copyright">© 2026 {'مِخبار' if ar else 'Mikhbar'}</div></footer></body></html>'''


def guides_index(locale: str) -> str:
    ar = locale == "ar"
    direction = "rtl" if ar else "ltr"
    title = "أدلة مِخبار التقنية | الذكاء الاصطناعي والأمن السيبراني والروبوتات" if ar else "Mikhbar Technology Guides | AI, Cybersecurity & Robotics"
    description = "أدلة تقنية دائمة من مِخبار لفهم الذكاء الاصطناعي والأمن السيبراني والروبوتات بعيدًا عن دورة الأخبار اليومية." if ar else "Evergreen Mikhbar technology guides for understanding artificial intelligence, cybersecurity and robotics beyond the daily news cycle."
    canonical = f"{ORIGIN}/{locale}/guides/"
    other = "en" if ar else "ar"
    cards = "".join(
        f'<a class="rt-topic-card" href="/{locale}/guides/{slug}/"><b>{escape(spec[locale]["h1"])}</b><span>{escape(spec[locale]["deck"])}</span></a>'
        for slug, spec in PILLARS.items()
    )
    items = [
        {"@type": "ListItem", "position": i, "url": f"{ORIGIN}/{locale}/guides/{slug}/", "name": spec[locale]["h1"]}
        for i, (slug, spec) in enumerate(PILLARS.items(), 1)
    ]
    schema = json.dumps({
        "@context": "https://schema.org",
        "@graph": [publisher_schema(), {"@type": "CollectionPage", "@id": canonical + "#page", "url": canonical, "name": title, "inLanguage": locale, "publisher": {"@id": ORIGIN + "/#publisher"}}, {"@type": "ItemList", "itemListElement": items}],
    }, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    heading = "أدلة مِخبار التقنية" if ar else "Mikhbar Technology Guides"
    deck = "صفحات مرجعية دائمة تُشرح فيها المفاهيم الأساسية وتُربط بأحدث تغطية مِخبار المتخصصة." if ar else "Evergreen reference pages that explain core concepts and connect them with Mikhbar's latest specialist coverage."
    return f'''<!DOCTYPE html><html lang="{locale}" dir="{direction}"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#ffffff">
<title>{escape(title)}</title><meta name="description" content="{escape(description, quote=True)}"><meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1"><link rel="canonical" href="{canonical}"><link rel="alternate" hreflang="ar" href="{ORIGIN}/ar/guides/"><link rel="alternate" hreflang="en" href="{ORIGIN}/en/guides/"><link rel="alternate" hreflang="x-default" href="{ORIGIN}/en/guides/">
<meta property="og:type" content="website"><meta property="og:site_name" content="{'مِخبار' if ar else 'Mikhbar'}"><meta property="og:title" content="{escape(title, quote=True)}"><meta property="og:description" content="{escape(description, quote=True)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{SOCIAL_IMAGE}"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(title, quote=True)}"><meta name="twitter:description" content="{escape(description, quote=True)}"><meta name="twitter:image" content="{SOCIAL_IMAGE}">
<link rel="stylesheet" href="/styles.css"><link rel="stylesheet" href="/forum.css?v=20260924-guides1"><link rel="stylesheet" href="/forum-media.css"><script type="application/ld+json">{schema}</script><style>.rt-topic-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px}}.rt-topic-card{{display:flex;flex-direction:column;gap:8px;padding:18px;border:1px solid #e3e3df;border-radius:18px;text-decoration:none;color:inherit}}.rt-topic-card span{{line-height:1.7;color:#666}}</style></head>
<body class="rt-locale-{locale}" data-guide-index="true">{header(locale)}<main class="rt-main" id="main">{categories(locale)}<div class="rt-shell"><section class="rt-category-hero"><nav class="rt-breadcrumbs"><a href="/{locale}/">{'مِخبار' if ar else 'Mikhbar'}</a><span>›</span><span>{'الأدلة' if ar else 'Guides'}</span></nav><div class="rt-category-title"><span class="rt-label">{'EVERGREEN'}</span><h1>{heading}</h1><p>{deck}</p></div></section><section class="rt-section"><div class="rt-topic-grid">{cards}</div></section></div></main><footer class="rt-footer"><div class="rt-shell rt-copyright">© 2026 {'مِخبار' if ar else 'Mikhbar'}</div></footer></body></html>'''


def main() -> int:
    written: list[str] = []
    for locale in ("ar", "en"):
        posts = load_posts(locale)
        index_path = FORUM / locale / "guides" / "index.html"
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.write_text(guides_index(locale), encoding="utf-8")
        written.append(f"{locale}/guides")
        for slug, spec in PILLARS.items():
            path = FORUM / locale / "guides" / slug / "index.html"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(guide_page(locale, slug, spec, posts), encoding="utf-8")
            written.append(f"{locale}/guides/{slug}")
    print(f"Mikhbar pillar pages generated: {len(written)} pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
