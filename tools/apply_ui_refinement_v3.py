from pathlib import Path
import re

# Remove the three UI elements highlighted in the screenshots.
index_path = Path('index.html')
html = index_path.read_text(encoding='utf-8')
html, hero_values_removed = re.subn(r'\s*<div class="hero-values">.*?</div>', '', html, count=1, flags=re.S)
html, tech_band_removed = re.subn(r'\s*<div class="tech-band"><div class="container tech-band-inner">.*?</div></div></div>', '', html, count=1, flags=re.S)
index_path.write_text(html, encoding='utf-8')

# Redesign "What can I build for you?" as one long premium card.
js_path = Path('enhancements.js')
js = js_path.read_text(encoding='utf-8')
new_services = r'''  function addServices() {
    const projectsSection = $('#projects'); if (!projectsSection || $('#services')) return;
    const capabilities = lang==='ar' ? [
      ['01','ويب ومنصات','مواقع شخصية وتجارية، صفحات هبوط، متاجر، لوحات تحكم، تطبيقات ويب وواجهات عربية RTL متجاوبة.'],
      ['02','Windows والحاسوب','تطبيقات C# و.NET وWinUI، أدوات ملفات ونظام، برامج داخلية ولوحات تشغيل مخصصة.'],
      ['03','الهاتف','تطبيقات وتجارب Android، واجهات Kotlin، ونماذج Python/Kivy قابلة للتطوير.'],
      ['04','Python والأتمتة','معالجة ملفات وبيانات، نسخ احتياطي، تقارير، إعادة تسمية جماعية، وأتمتة خطوات وسير عمل متكرر.'],
      ['05','الذكاء الاصطناعي','دمج خدمات ونماذج AI، أدوات نصوص ومحتوى، مساعدين ذكيين وسير عمل مدعوم بالذكاء الاصطناعي.'],
      ['06','البيانات والأنظمة','واجهات API، قواعد بيانات، أنظمة إدارة، لوحات بيانات، IoT وحساسات وربط خدمات متعددة.'],
      ['07','أدوات مخصصة','إضافات متصفح، PDF وصور وصوت وفيديو، محولات، QR، أدوات مطورين وبرامج مصممة لفكرة محددة.']
    ] : [
      ['01','Web & platforms','Portfolios, business sites, landing pages, stores, dashboards, web apps and responsive RTL interfaces.'],
      ['02','Windows & desktop','C#, .NET and WinUI apps, file/system utilities, internal tools and custom desktop workflows.'],
      ['03','Mobile','Android experiences, Kotlin interfaces and extendable Python/Kivy prototypes.'],
      ['04','Python & automation','File/data processing, backups, reports, batch renaming and repeatable workflow automation.'],
      ['05','AI solutions','AI integrations, text/content tools, smart assistants and AI-assisted workflows.'],
      ['06','Data & systems','APIs, databases, management systems, dashboards, IoT/sensor projects and service integrations.'],
      ['07','Custom utilities','Browser extensions, PDF/image/audio/video tools, converters, QR utilities and purpose-built software.']
    ];
    const sec = document.createElement('section'); sec.id = 'services'; sec.className = 'enh-services enh-section enh-snap';
    sec.innerHTML = `<div class="enh-shell"><div class="enh-kicker" data-i18n="services">${t('services')}</div><h2 class="enh-title" data-i18n="servicesTitle">${t('servicesTitle')}</h2><p class="enh-subtitle">${lang==='ar'?'بدل أن أحصر فكرتك في قالب جاهز، أبني الحل حول الفكرة نفسها: من أداة صغيرة ذكية إلى نظام متكامل، مع اختيار التقنية المناسبة لكل مشروع.':'Rather than forcing your idea into a template, I build around the idea itself — from a focused smart utility to a complete system, using the right technology for each project.'}</p><article class="enh-capability-card enh-reveal"><div class="enh-capability-intro"><span class="enh-capability-code">BUILD / CREATE / AUTOMATE</span><h3>${lang==='ar'?'فكرتك يمكن أن تصبح منتجًا يعمل ويُستخدم.':'Your idea can become a product people can actually use.'}</h3><p>${lang==='ar'?'أستطيع تصميم الواجهة، برمجة المنطق، ربط البيانات والخدمات، أتمتة العمليات، وبناء تجربة واضحة وسريعة وقابلة للتوسع — سواء كانت الفكرة موقعًا، تطبيقًا، أداة، نظامًا داخليًا أو تجربة جديدة بالكامل.':'I can shape the interface, build the logic, connect data and services, automate workflows and deliver a clear, fast, extensible experience — whether it is a website, app, utility, internal system or something entirely new.'}</p><div class="enh-capability-tags"><span>Web</span><span>Windows</span><span>Mobile</span><span>Python</span><span>AI</span><span>Automation</span><span>Data</span><span>IoT</span><span>APIs</span><span>RTL</span></div></div><div class="enh-capability-list">${capabilities.map(([n,h,p])=>`<div class="enh-capability-row"><b>${n}</b><div><strong>${h}</strong><span>${p}</span></div></div>`).join('')}</div><div class="enh-capability-footer"><span>${lang==='ar'?'فكرتك غير موجودة ضمن الأمثلة؟ أرسلها كما هي. الهدف أن نصنع الحل المناسب لها، لا أن نجبرها على شكل جاهز.':'Do not see your exact idea in the examples? Send it as-is. The goal is to build the right solution around it, not force it into a preset shape.'}</span><div class="enh-request-row"><a class="enh-primary" id="enhOpenRequest" href="${projectRequestUrl}" target="_blank" rel="noopener noreferrer" data-i18n="request">${t('request')}</a><a class="enh-secondary" href="${consultationUrl}" target="_blank" rel="noopener noreferrer">${lang==='ar'?'احجز استشارة':'Book a consultation'}</a><a class="enh-secondary" href="${omnisendUpdates}" target="_blank" rel="noopener noreferrer">${lang==='ar'?'تحديثات المشاريع':'Project updates'}</a></div></div></article></div>`;
    projectsSection.insertAdjacentElement('beforebegin', sec);
  }

'''
js, replaced = re.subn(r'  function addServices\(\) \{.*?\n  function addProcess\(\) \{', new_services + '  function addProcess() {', js, count=1, flags=re.S)
if replaced != 1:
    raise SystemExit(f'addServices replacement failed: {replaced}')

# Stop generating the comparison section the user asked to remove.
js = js.replace(',addServiceComparison,', ',', 1)
js = js.replace('addServiceComparison,', '', 1)
js_path.write_text(js, encoding='utf-8')

# Add the one-card layout and safety-hide the removed runtime sections.
css_path = Path('enhancements.css')
css = css_path.read_text(encoding='utf-8')
if '/* capability-card-v1 */' not in css:
    css += r'''

/* capability-card-v1 */
.hero-values,.tech-band,#enhCompare,#enhToolsAreas{display:none!important}
.enh-capability-card{position:relative;overflow:hidden;margin-top:30px;border:1px solid rgba(198,241,108,.18);border-radius:30px;background:linear-gradient(135deg,rgba(198,241,108,.055),rgba(255,255,255,.012) 42%,rgba(255,255,255,.02));box-shadow:0 28px 80px rgba(0,0,0,.22)}
.enh-capability-card::before{content:"";position:absolute;width:430px;height:430px;border-radius:50%;inset:-235px auto auto -125px;background:radial-gradient(circle,rgba(198,241,108,.12),transparent 68%);pointer-events:none}
.enh-capability-intro{position:relative;padding:34px 34px 26px;border-bottom:1px solid var(--enh-line)}
.enh-capability-code{display:inline-flex;align-items:center;min-height:28px;padding:0 10px;border:1px solid rgba(198,241,108,.18);border-radius:999px;color:var(--enh-lime);font:700 10px/1 ui-monospace,Consolas,monospace;letter-spacing:1.4px;background:rgba(198,241,108,.045)}
.enh-capability-intro h3{max-width:860px;margin:16px 0 8px;font-size:clamp(1.55rem,3vw,2.5rem);line-height:1.35}.enh-capability-intro p{max-width:940px;margin:0;color:var(--enh-muted);font-size:14px;line-height:1.95}
.enh-capability-tags{display:flex;flex-wrap:wrap;gap:7px;margin-top:20px}.enh-capability-tags span{padding:6px 10px;border-radius:999px;border:1px solid var(--enh-line);color:#c7d0c0;background:rgba(255,255,255,.02);font:700 10px/1 ui-monospace,Consolas,monospace}
.enh-capability-list{display:grid;grid-template-columns:1fr 1fr;padding:8px 34px}.enh-capability-row{display:grid;grid-template-columns:42px 1fr;gap:14px;align-items:start;padding:20px 8px;border-bottom:1px solid rgba(255,255,255,.075)}.enh-capability-row:nth-last-child(-n+2){border-bottom:0}.enh-capability-row:nth-child(odd){padding-inline-end:26px}.enh-capability-row:nth-child(even){padding-inline-start:26px;border-inline-start:1px solid rgba(255,255,255,.075)}
.enh-capability-row>b{width:34px;height:34px;display:grid;place-items:center;border-radius:50%;background:rgba(198,241,108,.075);color:var(--enh-lime);font:700 10px/1 ui-monospace,Consolas,monospace}.enh-capability-row strong{display:block;color:var(--enh-text);font-size:14px;margin-bottom:5px}.enh-capability-row span{display:block;color:var(--enh-muted);font-size:12px;line-height:1.8}
.enh-capability-footer{display:flex;align-items:center;justify-content:space-between;gap:22px;padding:24px 34px;border-top:1px solid var(--enh-line);background:rgba(0,0,0,.08)}.enh-capability-footer>span{max-width:620px;color:var(--enh-muted);font-size:12px;line-height:1.8}.enh-capability-footer .enh-request-row{margin-top:0;justify-content:flex-end}
@media(max-width:760px){.enh-capability-intro{padding:26px 22px 22px}.enh-capability-list{grid-template-columns:1fr;padding:6px 22px}.enh-capability-row{padding:18px 0!important}.enh-capability-row:nth-child(even){border-inline-start:0}.enh-capability-row:nth-last-child(2){border-bottom:1px solid rgba(255,255,255,.075)}.enh-capability-footer{align-items:flex-start;flex-direction:column;padding:22px}.enh-capability-footer .enh-request-row{justify-content:flex-start}}
'''
css_path.write_text(css, encoding='utf-8')

# Cache bust.
sw_path = Path('service-worker.js')
sw = sw_path.read_text(encoding='utf-8')
sw = re.sub(r'rad-portfolio-v3\.\d+\.0', 'rad-portfolio-v3.12.0', sw, count=1)
sw_path.write_text(sw, encoding='utf-8')

print('hero_values_removed=', hero_values_removed, 'tech_band_removed=', tech_band_removed, 'services_replaced=', replaced)
