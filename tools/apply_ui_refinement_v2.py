from pathlib import Path
import re

# 1) Tone down the animated code background slightly.
styles_path = Path('styles.css')
styles = styles_path.read_text(encoding='utf-8')
styles = re.sub(
    r"\.code-bg\{position:fixed;inset:0;z-index:-1;overflow:hidden;pointer-events:none;user-select:none;opacity:\.55;filter:blur\(\.7px\);",
    ".code-bg{position:fixed;inset:0;z-index:-1;overflow:hidden;pointer-events:none;user-select:none;opacity:.38;filter:blur(.75px) brightness(.78);",
    styles,
    count=1,
)
styles = styles.replace("@media(max-width:760px){.code-bg{opacity:.4}}", "@media(max-width:760px){.code-bg{opacity:.30;filter:blur(.7px) brightness(.78)}}", 1)
styles_path.write_text(styles, encoding='utf-8')

# 2) Remove the UI strips highlighted by the user and replace the text ticker placeholder.
index_path = Path('index.html')
html = index_path.read_text(encoding='utf-8')
html, hero_removed = re.subn(r'\s*<div class="hero-values">.*?</div>', '', html, count=1, flags=re.S)
html, band_removed = re.subn(r'\s*<div class="tech-band"><div class="container tech-band-inner">.*?</div></div></div>', '', html, count=1, flags=re.S)
html, ticker_replaced = re.subn(
    r'<div class="enh-tech-strip enh-reveal"><div class="enh-tech-track">.*?</div></div>',
    '<div class="enh-tech-strip enh-reveal" aria-label="Programming languages and technologies"><div class="enh-tech-track" id="programmingIconTicker" aria-hidden="true"></div></div>',
    html,
    count=1,
    flags=re.S,
)
if ticker_replaced != 1:
    raise SystemExit(f'Expected one ticker replacement, found {ticker_replaced}')
index_path.write_text(html, encoding='utf-8')

# 3) Replace the multiple service cards with one premium long capability panel,
#    remove the tools/areas/timeline and service-comparison sections from runtime,
#    and convert the moving ticker to icon-only.
js_path = Path('enhancements.js')
js = js_path.read_text(encoding='utf-8')

if 'const techIcons = ' not in js:
    marker = "  const consultationUrl = `${calendlyConsultation}?utm_source=rdwan.dev&utm_medium=website&utm_campaign=project_consultation`;\n"
    tech_icons = """  const techIcons = [
    ['python','Python'],['javascript','JavaScript'],['typescript','TypeScript'],['java','Java'],['c','C'],['cplusplus','C++'],['csharp','C#'],['go','Go'],['rust','Rust'],['ruby','Ruby'],['php','PHP'],['swift','Swift'],['kotlin','Kotlin'],['dart','Dart'],['r','R'],['scala','Scala'],['perl','Perl'],['lua','Lua'],['haskell','Haskell'],['elixir','Elixir'],['erlang','Erlang'],['fsharp','F#'],['clojure','Clojure'],['groovy','Groovy'],['objectivec','Objective-C'],['visualbasic','Visual Basic'],['fortran','Fortran'],['matlab','MATLAB'],['julia','Julia'],['nim','Nim'],['zig','Zig'],['solidity','Solidity'],['bash','Bash'],['powershell','PowerShell'],['html5','HTML5'],['css3','CSS3'],['sass','Sass'],['less','Less'],['markdown','Markdown'],['nodejs','Node.js'],['denojs','Deno'],['bun','Bun'],['react','React'],['vuejs','Vue.js'],['angular','Angular'],['svelte','Svelte'],['nextjs','Next.js'],['nuxtjs','Nuxt'],['jquery','jQuery'],['bootstrap','Bootstrap'],['tailwindcss','Tailwind CSS'],['django','Django'],['flask','Flask'],['fastapi','FastAPI'],['laravel','Laravel'],['rails','Ruby on Rails'],['spring','Spring'],['dotnetcore','.NET'],['flutter','Flutter'],['electron','Electron'],['qt','Qt'],['tensorflow','TensorFlow'],['pytorch','PyTorch'],['opencv','OpenCV'],['numpy','NumPy'],['pandas','Pandas'],['mysql','MySQL'],['postgresql','PostgreSQL'],['mongodb','MongoDB'],['sqlite','SQLite'],['redis','Redis'],['mariadb','MariaDB'],['microsoftsqlserver','SQL Server'],['oracle','Oracle'],['cassandra','Cassandra'],['neo4j','Neo4j'],['firebase','Firebase'],['supabase','Supabase'],['docker','Docker'],['kubernetes','Kubernetes'],['git','Git'],['github','GitHub'],['gitlab','GitLab'],['npm','npm'],['yarn','Yarn'],['pnpm','pnpm'],['vitejs','Vite'],['webpack','Webpack'],['cmake','CMake'],['gradle','Gradle'],['maven','Maven'],['terraform','Terraform'],['ansible','Ansible'],['jenkins','Jenkins'],['githubactions','GitHub Actions'],['linux','Linux'],['ubuntu','Ubuntu'],['android','Android'],['arduino','Arduino'],['raspberrypi','Raspberry Pi'],['graphql','GraphQL'],['nginx','Nginx'],['apache','Apache'],['cloudflare','Cloudflare'],['azure','Azure'],['amazonwebservices','AWS']
  ];
"""
    if marker not in js:
        raise SystemExit('Could not locate tech icon insertion marker')
    js = js.replace(marker, marker + tech_icons, 1)

if 'function hydrateTechIconTicker()' not in js:
    hydrate = """
  function hydrateTechIconTicker() {
    const track = $('#programmingIconTicker') || $('.enh-tech-track');
    if (!track || track.dataset.iconsReady === '1') return;
    if (!document.querySelector('link[data-devicon]')) {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = 'https://cdn.jsdelivr.net/npm/devicon@2.17.0/devicon.min.css';
      link.dataset.devicon = '2.17.0';
      document.head.appendChild(link);
    }
    const icons = techIcons.map(([slug,label]) => `<span class="enh-tech-icon" title="${label}"><i class="devicon-${slug}-plain colored"></i></span>`).join('');
    track.innerHTML = `<div class="enh-tech-sequence">${icons}</div><div class="enh-tech-sequence" aria-hidden="true">${icons}</div>`;
    track.dataset.iconsReady = '1';
  }

"""
    js = js.replace('  function addStatsAndTicker() {', hydrate + '  function addStatsAndTicker() {', 1)

old_ticker = """    const tech = document.createElement('div'); tech.className = 'enh-tech-strip enh-reveal';
    const names = ['Python','C#','.NET','JavaScript','HTML','CSS','Git','GitHub','PowerShell','C++','SQL','Android','Kotlin','PHP','Automation','IoT'];
    tech.innerHTML = `<div class=\"enh-tech-track\">${[...names,...names].map(x=>`<span class=\"enh-tech-chip\">${x}</span>`).join('')}</div>`;
    stats.insertAdjacentElement('afterend', tech);"""
new_ticker = """    const tech = document.createElement('div'); tech.className = 'enh-tech-strip enh-reveal'; tech.setAttribute('aria-label','Programming languages and technologies');
    tech.innerHTML = '<div class="enh-tech-track" id="programmingIconTicker" aria-hidden="true"></div>';
    stats.insertAdjacentElement('afterend', tech);
    hydrateTechIconTicker();"""
if old_ticker in js:
    js = js.replace(old_ticker, new_ticker, 1)

new_services = r'''  function addServices() {
    const projectsSection = $('#projects'); if (!projectsSection || $('#services')) return;
    const capabilities = lang==='ar' ? [
      ['01','ويب ومنصات','مواقع شخصية وتجارية، صفحات هبوط، متاجر، لوحات تحكم، تطبيقات ويب وواجهات RTL متجاوبة.'],
      ['02','Windows والحاسوب','تطبيقات C# و.NET وWinUI، أدوات ملفات ونظام، برامج داخلية ولوحات تشغيل مخصصة.'],
      ['03','الهاتف','تطبيقات وتجارب Android، واجهات Kotlin، ونماذج Python/Kivy قابلة للتطوير.'],
      ['04','Python والأتمتة','سكربتات معالجة ملفات وبيانات، نسخ احتياطي، تقارير، إعادة تسمية جماعية، وأتمتة خطوات متكررة.'],
      ['05','الذكاء الاصطناعي','دمج خدمات ونماذج AI، أدوات نصوص ومحتوى، مساعدين ذكيين وسير عمل مدعوم بالذكاء الاصطناعي.'],
      ['06','البيانات والأنظمة','واجهات API، قواعد بيانات، أنظمة إدارة، لوحات بيانات، مشاريع IoT وحساسات وربط خدمات متعددة.'],
      ['07','أدوات خاصة','إضافات متصفح، أدوات PDF وصور وصوت وفيديو، محولات، QR، أدوات مطورين وبرامج مصممة لفكرة محددة.']
    ] : [
      ['01','Web & platforms','Portfolios, business sites, landing pages, stores, dashboards, web apps and responsive RTL interfaces.'],
      ['02','Windows & desktop','C#, .NET and WinUI apps, file/system utilities, internal tools and custom desktop workflows.'],
      ['03','Mobile','Android experiences, Kotlin interfaces and extendable Python/Kivy prototypes.'],
      ['04','Python & automation','File/data processing, backups, reporting, batch renaming and workflow automation.'],
      ['05','AI solutions','AI integrations, text/content tools, smart assistants and AI-assisted workflows.'],
      ['06','Data & systems','APIs, databases, management systems, dashboards, IoT/sensor projects and service integrations.'],
      ['07','Custom utilities','Browser extensions, PDF/image/audio/video tools, converters, QR utilities and purpose-built software.']
    ];
    const sec = document.createElement('section'); sec.id = 'services'; sec.className = 'enh-services enh-section enh-snap';
    sec.innerHTML = `<div class="enh-shell"><div class="enh-kicker" data-i18n="services">${t('services')}</div><h2 class="enh-title" data-i18n="servicesTitle">${t('servicesTitle')}</h2><p class="enh-subtitle">${lang==='ar'?'بدل حلول جاهزة متشابهة، أبني حول الفكرة نفسها: من أبسط أداة إلى نظام متكامل، مع اختيار التقنية المناسبة لكل مشروع.':'Rather than forcing ideas into templates, I build around the idea itself — from a focused utility to a complete system, using the right technology for the job.'}</p><article class="enh-capability-card enh-reveal"><div class="enh-capability-intro"><span class="enh-capability-code">BUILD / CREATE / AUTOMATE</span><h3>${lang==='ar'?'فكرتك يمكن أن تتحول إلى منتج يعمل.':'Your idea can become a working product.'}</h3><p>${lang==='ar'?'أستطيع تصميم الواجهة، برمجة المنطق، ربط البيانات والخدمات، أتمتة العمليات، ثم تجهيز التجربة لتكون واضحة وسريعة وقابلة للتوسع.':'I can shape the interface, build the logic, connect data and services, automate the workflow, and refine the experience for clarity, speed and growth.'}</p><div class="enh-capability-tags"><span>Web</span><span>Windows</span><span>Mobile</span><span>Python</span><span>AI</span><span>Automation</span><span>Data</span><span>IoT</span><span>APIs</span><span>RTL</span></div></div><div class="enh-capability-list">${capabilities.map(([n,h,p])=>`<div class="enh-capability-row"><b>${n}</b><div><strong>${h}</strong><span>${p}</span></div></div>`).join('')}</div><div class="enh-capability-footer"><span>${lang==='ar'?'لا ترى فكرتك مكتوبة هنا؟ أرسلها كما هي، وسأحوّلها إلى مسار تقني واضح.':'Do not see your exact idea here? Send it as-is and I will turn it into a clear technical direction.'}</span><div class="enh-request-row"><a class="enh-primary" id="enhOpenRequest" href="${projectRequestUrl}" target="_blank" rel="noopener noreferrer" data-i18n="request">${t('request')}</a><a class="enh-secondary" href="${consultationUrl}" target="_blank" rel="noopener noreferrer">${lang==='ar'?'احجز استشارة':'Book a consultation'}</a><a class="enh-secondary" href="${omnisendUpdates}" target="_blank" rel="noopener noreferrer">${lang==='ar'?'تحديثات المشاريع':'Project updates'}</a></div></div></article></div>`;
    projectsSection.insertAdjacentElement('beforebegin', sec);
  }

'''
js, service_count = re.subn(r'  function addServices\(\) \{.*?\n  function addProcess\(\) \{', new_services + '  function addProcess() {', js, count=1, flags=re.S)
if service_count != 1:
    raise SystemExit(f'Expected to replace addServices once, found {service_count}')

# Remove the unwanted generated sections from the boot sequence.
js = js.replace('addProcess,addToolsAreasTimeline,addServiceComparison,', 'addProcess,', 1)
js = js.replace('const tasks=[addStatsAndTicker,', 'const tasks=[hydrateTechIconTicker,addStatsAndTicker,', 1) if 'const tasks=[hydrateTechIconTicker,addStatsAndTicker,' not in js else js
js_path.write_text(js, encoding='utf-8')

# 4) New visual treatment: icon-only ticker + single premium capability card.
css_path = Path('enhancements.css')
css = css_path.read_text(encoding='utf-8')
marker = '/* ui-refinement-v2 */'
if marker not in css:
    css += r'''

/* ui-refinement-v2 */
.hero-values,.tech-band,#enhToolsAreas,#enhCompare{display:none!important}
.enh-tech-strip{position:relative;direction:ltr;overflow:hidden;border-block:1px solid var(--enh-line);background:rgba(255,255,255,.012);-webkit-mask-image:linear-gradient(to right,transparent 0,#000 4%,#000 96%,transparent 100%);mask-image:linear-gradient(to right,transparent 0,#000 4%,#000 96%,transparent 100%)}
.enh-tech-track{display:flex;width:max-content;gap:0;padding:9px 0;animation:enhTicker 68s linear infinite;will-change:transform;direction:ltr}
.enh-tech-sequence{display:flex;align-items:center;gap:9px;padding-inline-end:9px;flex:none}
.enh-tech-icon{width:31px;height:31px;display:grid;place-items:center;flex:0 0 31px;border:1px solid rgba(255,255,255,.07);border-radius:10px;background:rgba(255,255,255,.025);transition:transform .18s ease,border-color .18s ease,background .18s ease}
.enh-tech-icon i{display:block;font-size:18px;line-height:1;filter:saturate(.92) brightness(1.07)}
.enh-tech-icon:hover{transform:translateY(-1px);border-color:rgba(198,241,108,.25);background:rgba(198,241,108,.045)}
.enh-tech-icon .devicon-github-plain,.enh-tech-icon .devicon-nextjs-plain,.enh-tech-icon .devicon-bash-plain,.enh-tech-icon .devicon-linux-plain{color:#d9dfd4!important}
.enh-capability-card{position:relative;overflow:hidden;margin-top:30px;border:1px solid rgba(198,241,108,.18);border-radius:30px;background:linear-gradient(135deg,rgba(198,241,108,.055),rgba(255,255,255,.012) 42%,rgba(255,255,255,.02));box-shadow:0 28px 80px rgba(0,0,0,.22)}
.enh-capability-card::before{content:"";position:absolute;width:420px;height:420px;border-radius:50%;inset:-220px auto auto -120px;background:radial-gradient(circle,rgba(198,241,108,.12),transparent 68%);pointer-events:none}
.enh-capability-intro{position:relative;padding:34px 34px 26px;border-bottom:1px solid var(--enh-line)}
.enh-capability-code{display:inline-flex;align-items:center;min-height:28px;padding:0 10px;border:1px solid rgba(198,241,108,.18);border-radius:999px;color:var(--enh-lime);font:700 10px/1 ui-monospace,Consolas,monospace;letter-spacing:1.4px;background:rgba(198,241,108,.045)}
.enh-capability-intro h3{max-width:820px;margin:16px 0 8px;font-size:clamp(1.55rem,3vw,2.5rem);line-height:1.35}
.enh-capability-intro p{max-width:900px;margin:0;color:var(--enh-muted);font-size:14px;line-height:1.95}
.enh-capability-tags{display:flex;flex-wrap:wrap;gap:7px;margin-top:20px}.enh-capability-tags span{padding:6px 10px;border-radius:999px;border:1px solid var(--enh-line);color:#c7d0c0;background:rgba(255,255,255,.02);font:700 10px/1 ui-monospace,Consolas,monospace}
.enh-capability-list{display:grid;grid-template-columns:1fr 1fr;padding:8px 34px}.enh-capability-row{display:grid;grid-template-columns:42px 1fr;gap:14px;align-items:start;padding:20px 8px;border-bottom:1px solid rgba(255,255,255,.075)}.enh-capability-row:nth-last-child(-n+2){border-bottom:0}.enh-capability-row:nth-child(odd){padding-inline-end:26px}.enh-capability-row:nth-child(even){padding-inline-start:26px;border-inline-start:1px solid rgba(255,255,255,.075)}
.enh-capability-row>b{width:34px;height:34px;display:grid;place-items:center;border-radius:50%;background:rgba(198,241,108,.075);color:var(--enh-lime);font:700 10px/1 ui-monospace,Consolas,monospace}.enh-capability-row strong{display:block;color:var(--enh-text);font-size:14px;margin-bottom:5px}.enh-capability-row span{display:block;color:var(--enh-muted);font-size:12px;line-height:1.8}
.enh-capability-footer{display:flex;align-items:center;justify-content:space-between;gap:22px;padding:24px 34px;border-top:1px solid var(--enh-line);background:rgba(0,0,0,.08)}.enh-capability-footer>span{max-width:620px;color:var(--enh-muted);font-size:12px;line-height:1.8}.enh-capability-footer .enh-request-row{margin-top:0;justify-content:flex-end}
@media(max-width:760px){.enh-tech-track{padding:8px 0;animation-duration:56s}.enh-tech-sequence{gap:8px;padding-inline-end:8px}.enh-tech-icon{width:29px;height:29px;flex-basis:29px}.enh-tech-icon i{font-size:17px}.enh-capability-intro{padding:26px 22px 22px}.enh-capability-list{grid-template-columns:1fr;padding:6px 22px}.enh-capability-row{padding:18px 0!important}.enh-capability-row:nth-child(even){border-inline-start:0}.enh-capability-row:nth-last-child(2){border-bottom:1px solid rgba(255,255,255,.075)}.enh-capability-footer{align-items:flex-start;flex-direction:column;padding:22px}.enh-capability-footer .enh-request-row{justify-content:flex-start}}
'''
css_path.write_text(css, encoding='utf-8')

# 5) Bust the PWA cache so users receive the new UI quickly.
sw_path = Path('service-worker.js')
sw = sw_path.read_text(encoding='utf-8')
sw = re.sub(r"rad-portfolio-v3\.\d+\.0", "rad-portfolio-v3.12.0", sw, count=1)
sw_path.write_text(sw, encoding='utf-8')

print(f'hero_values_removed={hero_removed}, tech_band_removed={band_removed}, ticker_replaced={ticker_replaced}, service_replaced={service_count}')
