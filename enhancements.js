(() => {
  'use strict';

  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const githubBase = 'https://github.com/rad03i2/';
  const instagram = 'https://www.instagram.com/rad_03i';
  const facebook = 'https://www.facebook.com/rad03e';

  const projectMeta = [
    {n:'01',name:'Smart File Manager',repo:'SmartFileManager',cat:['windows','tools'],tags:['C#','WinUI 3','.NET'],desc:'برنامج Windows لإدارة الملفات وإعادة التسمية الجماعية وفحص التكرار.'},
    {n:'02',name:'Robotics Language Lab',repo:'robotics-language-lab',cat:['robotics','tools'],tags:['Python','C++','ROS 2'],desc:'مختبر برمجي لتجارب الروبوتات والتحكم والحساسات باستخدام أكثر من لغة.'},
    {n:'03',name:'Python Toolbox',repo:'python-toolbox',cat:['python','tools'],tags:['Python','CLI','Automation'],desc:'مجموعة أدوات Python للملفات والنصوص والمهام اليومية السريعة.'},
    {n:'04',name:'JavaScript Lab',repo:'javascript-lab',cat:['web'],tags:['JavaScript','HTML','CSS'],desc:'تجارب JavaScript وواجهات ويب صغيرة تركز على التفاعل والتخزين المحلي.'},
    {n:'05',name:'AI Tools Lab',repo:'ai-tools-lab',cat:['ai','python','web'],tags:['Python','JavaScript','AI'],desc:'أدوات وتجارب إنتاجية مرتبطة بالذكاء الاصطناعي ومعالجة النصوص.'},
    {n:'06',name:'Desktop Automation Suite',repo:'desktop-automation-suite',cat:['windows','automation','tools'],tags:['PowerShell','C#','AutoHotkey'],desc:'مجموعة أتمتة لأعمال Windows المتكررة والاختصارات وسير العمل.'},
    {n:'07',name:'Windows System Toolkit',repo:'windows-system-toolkit',cat:['windows','tools'],tags:['Windows','PowerShell','C#'],desc:'أدوات لفحص النظام والتخزين وتنفيذ مهام صيانة آمنة.'},
    {n:'08',name:'Arabic UI Components',repo:'arabic-ui-components',cat:['web'],tags:['RTL','HTML','CSS'],desc:'مكونات واجهات عربية RTL قابلة لإعادة الاستخدام في المواقع واللوحات.'},
    {n:'09',name:'Student Management System',repo:'student-management-system',cat:['desktop','data'],tags:['Java','SQL','OOP'],desc:'نموذج نظام لإدارة بيانات الطلاب والدرجات وقاعدة البيانات.'},
    {n:'10',name:'File Processing Toolkit',repo:'file-processing-toolkit',cat:['python','tools','automation'],tags:['Python','C#','Bash'],desc:'أدوات لمعالجة الملفات وتجميعها وإعادة تسميتها واستخراج المعلومات منها.'},
    {n:'11',name:'IoT Sensor Dashboard',repo:'iot-sensor-dashboard',cat:['iot','web','data'],tags:['Arduino','Node.js','IoT'],desc:'لوحة عرض لقراءات الحساسات والقياسات المرتبطة بمشاريع إنترنت الأشياء.'},
    {n:'12',name:'Data Analysis Notebooks',repo:'data-analysis-notebooks',cat:['data','python'],tags:['Python','CSV','Analysis'],desc:'دفاتر تحليل بيانات تشمل الاستكشاف والإحصاءات والرسوم.'},
    {n:'13',name:'Web Security Lab',repo:'web-security-lab',cat:['web','security'],tags:['PHP','JavaScript','Security'],desc:'مختبر تعليمي لمفاهيم أمان الويب والممارسات الدفاعية.'},
    {n:'14',name:'Mobile App Starter Kit',repo:'mobile-app-starter-kit',cat:['mobile'],tags:['Kotlin','Android','Python'],desc:'قاعدة بداية لتطبيقات الهاتف وتجارب Android وPython Kivy.'},
    {n:'15',name:'C++ Algorithms Lab',repo:'cpp-algorithms-lab',cat:['cpp','tools'],tags:['C++','CMake','Algorithms'],desc:'تطبيقات تدريبية للخوارزميات والبحث والفرز وهياكل البيانات.'},
    {n:'16',name:'Python Automation Hub',repo:'python-automation-hub',cat:['python','automation'],tags:['Python','Automation','CLI'],desc:'سكربتات Python لأتمتة الملفات والتقارير والنسخ الاحتياطي.'},
    {n:'17',name:'Fullstack Mini Projects',repo:'fullstack-mini-projects',cat:['web','data'],tags:['PHP','JavaScript','SQL'],desc:'مشاريع Fullstack صغيرة تربط الواجهة بالخادم وقاعدة البيانات.'},
    {n:'18',name:'Developer Portfolio',repo:'developer-portfolio',cat:['web'],tags:['HTML','CSS','JavaScript'],desc:'تجربة موقع شخصي متجاوب لعرض الهوية والمهارات والمشاريع.'},
    {n:'19',name:'Portfolio',repo:'portfolio',cat:['web'],tags:['HTML','CSS','JavaScript'],desc:'واجهة Portfolio لعرض الأعمال البرمجية بصورة منظمة.'},
    {n:'20',name:'RAD / Main Portfolio',repo:'rad',cat:['web'],tags:['Portfolio','Projects','RAD'],desc:'الموقع الرئيسي الحالي لعرض الهوية والمشاريع وروابط التواصل.',demo:true}
  ];

  const icons = {
    github:'<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 .7A11.3 11.3 0 0 0 8.43 22.72c.57.11.78-.25.78-.55v-2c-3.16.69-3.83-1.35-3.83-1.35-.52-1.31-1.27-1.67-1.27-1.67-1.03-.7.08-.69.08-.69 1.14.08 1.74 1.18 1.74 1.18 1.02 1.73 2.67 1.23 3.32.94.1-.73.4-1.23.72-1.51-2.52-.29-5.18-1.26-5.18-5.62 0-1.24.45-2.25 1.17-3.05-.12-.29-.5-1.45.12-3.02 0 0 .95-.3 3.12 1.16a10.8 10.8 0 0 1 5.69 0c2.16-1.46 3.11-1.16 3.11-1.16.62 1.57.23 2.73.11 3.02.73.8 1.16 1.81 1.16 3.05 0 4.37-2.66 5.33-5.19 5.61.41.35.78 1.05.78 2.12v2.99c0 .3.21.66.79.55A11.3 11.3 0 0 0 12 .7Z"/></svg>',
    instagram:'<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M7.75 2h8.5A5.76 5.76 0 0 1 22 7.75v8.5A5.76 5.76 0 0 1 16.25 22h-8.5A5.76 5.76 0 0 1 2 16.25v-8.5A5.76 5.76 0 0 1 7.75 2Zm0 2A3.76 3.76 0 0 0 4 7.75v8.5A3.76 3.76 0 0 0 7.75 20h8.5A3.76 3.76 0 0 0 20 16.25v-8.5A3.76 3.76 0 0 0 16.25 4h-8.5ZM12 7a5 5 0 1 1 0 10 5 5 0 0 1 0-10Zm0 2a3 3 0 1 0 0 6 3 3 0 0 0 0-6Zm5.25-3.5a1.25 1.25 0 1 1 0 2.5 1.25 1.25 0 0 1 0-2.5Z"/></svg>',
    facebook:'<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M13.5 22v-8h2.75l.41-3.2H13.5V8.76c0-.93.26-1.56 1.59-1.56h1.7V4.34c-.29-.04-1.3-.12-2.47-.12-2.44 0-4.11 1.49-4.11 4.23v2.35H7.45V14h2.76v8h3.29Z"/></svg>',
    search:'<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" d="m21 21-4.5-4.5m2-5A7.5 7.5 0 1 1 3.5 11.5a7.5 7.5 0 0 1 15 0Z"/></svg>',
    up:'<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="m6 15 6-6 6 6"/></svg>'
  };

  function injectHead(){
    if (!document.querySelector('link[href="enhancements.css"]')) {
      const l=document.createElement('link'); l.rel='stylesheet'; l.href='enhancements.css'; document.head.appendChild(l);
    }
  }

  function addAvailability(){
    const copy=$('.hero-copy');
    if(!copy || $('.enh-availability',copy)) return;
    const badge=document.createElement('div');
    badge.className='enh-availability enh-reveal';
    badge.textContent='متاح لتنفيذ المشاريع';
    const actions=$('.hero-actions',copy);
    if(actions) actions.insertAdjacentElement('beforebegin',badge); else copy.appendChild(badge);
  }

  function addStatsAndTicker(){
    const hero=$('.hero'); if(!hero || $('#enhStats')) return;
    const stats=document.createElement('section');
    stats.id='enhStats'; stats.className='enh-shell enh-reveal';
    stats.innerHTML=`<div class="enh-stats">
      <div class="enh-stat"><strong>20</strong><span>مشروعًا معروضًا</span></div>
      <div class="enh-stat"><strong>Web</strong><span>واجهات ومواقع ويب</span></div>
      <div class="enh-stat"><strong>Desktop</strong><span>أدوات وتطبيقات حاسوب</span></div>
      <div class="enh-stat"><strong>Automation</strong><span>أتمتة وسير عمل</span></div>
    </div>`;
    hero.insertAdjacentElement('afterend',stats);

    const tech=document.createElement('div');
    tech.className='enh-tech-strip enh-reveal';
    const names=['Python','C#','.NET','JavaScript','HTML','CSS','Git','GitHub','PowerShell','C++','SQL','Android','Kotlin','PHP','Automation','IoT'];
    const repeated=[...names,...names];
    tech.innerHTML=`<div class="enh-tech-track">${repeated.map(x=>`<span class="enh-tech-chip">${x}</span>`).join('')}</div>`;
    stats.insertAdjacentElement('afterend',tech);
  }

  function addServices(){
    const projects=$('#projects'); if(!projects || $('#services')) return;
    const services=document.createElement('section');
    services.id='services'; services.className='enh-services enh-section';
    const items=[
      ['WEB','مواقع ويب','مواقع شخصية، صفحات تعريفية، لوحات وواجهات متجاوبة.'],
      ['WIN','تطبيقات Windows','أدوات سطح مكتب وإدارة ملفات وواجهات عملية.'],
      ['APP','تطبيقات هاتف','واجهات وتجارب Android وKivy قابلة للتطوير.'],
      ['PY','Python','سكربتات وأدوات لمعالجة الملفات والبيانات.'],
      ['AUTO','الأتمتة','اختصارات وسير عمل لتقليل المهام المتكررة.'],
      ['AI','أدوات AI','دمج أدوات ذكية في تجارب وبرامج إنتاجية.']
    ];
    services.innerHTML=`<div class="enh-shell"><div class="enh-kicker">الخدمات</div><h2 class="enh-title">ماذا أستطيع أن أنجز لك؟</h2><p class="enh-subtitle">حلول برمجية مباشرة ومركزة حسب احتياج المشروع، من الواجهة إلى الأتمتة والأدوات.</p><div class="enh-services-grid">${items.map(([i,t,d])=>`<article class="enh-service enh-reveal"><div class="enh-service-icon">${i}</div><h3>${t}</h3><p>${d}</p></article>`).join('')}</div><div class="enh-request-row"><a class="enh-primary" href="#contact">اطلب مشروعك</a><a class="enh-secondary" href="${instagram}" target="_blank" rel="noopener">تواصل عبر Instagram</a></div></div>`;
    projects.insertAdjacentElement('beforebegin',services);
  }

  function prepareProjectCards(){
    const grid=$('#projectsShowcaseGrid'); if(!grid) return false;
    const cards=$$('.showcase-card',grid);
    cards.forEach((card,i)=>{
      const m=projectMeta[i]; if(!m) return;
      card.dataset.projectIndex=String(i);
      card.dataset.categories=m.cat.join(' ');
      card.dataset.search=`${m.name} ${m.repo} ${m.tags.join(' ')} ${m.desc}`.toLowerCase();
      const imgLink=$('.showcase-image-link',card);
      if(imgLink){ imgLink.setAttribute('aria-label',`تفاصيل ${m.name}`); imgLink.dataset.tip='عرض التفاصيل'; }
      const gh=$('.github-icon-button',card); if(gh) gh.dataset.tip='GitHub';
    });
    return true;
  }

  function addProjectTools(){
    const grid=$('#projectsShowcaseGrid'); if(!grid || $('#enhProjectTools')) return;
    const tools=document.createElement('div');
    tools.id='enhProjectTools'; tools.className='enh-project-tools enh-reveal';
    tools.innerHTML=`<label class="enh-search">${icons.search}<input id="enhProjectSearch" type="search" placeholder="ابحث في المشاريع..." autocomplete="off" aria-label="بحث في المشاريع"></label><div class="enh-filters" role="group" aria-label="تصنيفات المشاريع"><button class="enh-filter is-active" data-filter="all">الكل</button><button class="enh-filter" data-filter="web">Web</button><button class="enh-filter" data-filter="windows">Windows</button><button class="enh-filter" data-filter="python">Python</button><button class="enh-filter" data-filter="automation">Automation</button><button class="enh-filter" data-filter="mobile">Mobile</button><button class="enh-filter" data-filter="data">Data / IoT</button></div>`;
    grid.insertAdjacentElement('beforebegin',tools);
    const empty=document.createElement('div'); empty.id='enhProjectEmpty'; empty.className='enh-project-empty'; empty.textContent='لا توجد مشاريع مطابقة للبحث الحالي.'; grid.insertAdjacentElement('afterend',empty);

    const moreWrap=$('.projects-more-wrap');
    if(moreWrap && !$('#enhProjectExtra')){
      const extra=document.createElement('div'); extra.id='enhProjectExtra'; extra.className='enh-project-extra-actions';
      extra.innerHTML=`<a class="enh-secondary" href="https://github.com/rad03i2?tab=repositories" target="_blank" rel="noopener">${icons.github}<span>عرض جميع المستودعات</span></a><button class="enh-secondary" id="enhShareProjects" type="button">مشاركة الموقع</button>`;
      moreWrap.insertAdjacentElement('afterend',extra);
    }

    let filter='all';
    const apply=()=>{
      const q=$('#enhProjectSearch').value.trim().toLowerCase();
      const cards=$$('.showcase-card',grid);
      const active=q || filter!=='all';
      grid.classList.toggle('show-all',Boolean(active));
      if(moreWrap) moreWrap.style.display=active?'none':'';
      let visible=0;
      cards.forEach(card=>{
        const okText=!q || (card.dataset.search||'').includes(q);
        const cats=(card.dataset.categories||'').split(' ');
        const okCat=filter==='all' || cats.includes(filter) || (filter==='data' && (cats.includes('iot')||cats.includes('data')));
        const hide=!(okText&&okCat);
        card.classList.toggle('enh-hidden',hide);
        if(!hide) visible++;
      });
      $('#enhProjectEmpty').classList.toggle('is-visible',visible===0);
    };
    $('#enhProjectSearch').addEventListener('input',apply);
    $$('.enh-filter',tools).forEach(btn=>btn.addEventListener('click',()=>{filter=btn.dataset.filter; $$('.enh-filter',tools).forEach(b=>b.classList.toggle('is-active',b===btn)); apply();}));
    const share=$('#enhShareProjects'); if(share) share.addEventListener('click',shareSite);
  }

  function ensureModal(){
    if($('#enhProjectModal')) return $('#enhProjectModal');
    const modal=document.createElement('div'); modal.id='enhProjectModal'; modal.className='enh-modal'; modal.setAttribute('role','dialog'); modal.setAttribute('aria-modal','true'); modal.setAttribute('aria-hidden','true');
    modal.innerHTML=`<div class="enh-modal-card"><button class="enh-modal-close" type="button" aria-label="إغلاق">×</button><img class="enh-modal-image" alt=""><div class="enh-modal-body"><div class="enh-modal-head"><div><div class="enh-kicker">تفاصيل المشروع</div><h3></h3></div></div><p class="enh-modal-desc"></p><div class="enh-modal-tags"></div><div class="enh-modal-actions"><a class="enh-primary enh-modal-github" target="_blank" rel="noopener">${icons.github}<span>GitHub</span></a><a class="enh-secondary enh-modal-demo" target="_blank" rel="noopener">معاينة المشروع</a></div></div></div>`;
    document.body.appendChild(modal);
    const close=()=>{modal.classList.remove('is-open');modal.setAttribute('aria-hidden','true');document.body.style.overflow='';};
    $('.enh-modal-close',modal).addEventListener('click',close);
    modal.addEventListener('click',e=>{if(e.target===modal) close();});
    document.addEventListener('keydown',e=>{if(e.key==='Escape'&&modal.classList.contains('is-open')) close();});
    return modal;
  }

  function bindProjectModal(){
    const grid=$('#projectsShowcaseGrid'); if(!grid) return;
    const modal=ensureModal();
    grid.addEventListener('click',e=>{
      const link=e.target.closest('.showcase-image-link'); if(!link) return;
      const card=link.closest('.showcase-card'); const i=Number(card?.dataset.projectIndex); const m=projectMeta[i]; if(!m) return;
      e.preventDefault();
      $('.enh-modal-image',modal).src=`assets/images/projects/project-${m.n}.webp`;
      $('.enh-modal-image',modal).alt=m.name;
      $('.enh-modal h3',modal).textContent=m.name;
      $('.enh-modal-desc',modal).textContent=m.desc;
      $('.enh-modal-tags',modal).innerHTML=m.tags.map(x=>`<span>${x}</span>`).join('');
      $('.enh-modal-github',modal).href=githubBase+m.repo;
      const demo=$('.enh-modal-demo',modal); demo.hidden=!m.demo; if(m.demo) demo.href=location.href.split('#')[0];
      modal.classList.add('is-open');modal.setAttribute('aria-hidden','false');document.body.style.overflow='hidden';
    });
  }

  async function shareSite(){
    const data={title:document.title,text:'ملف رضوان عبد الهادي البرمجي',url:location.href.split('#')[0]};
    try{if(navigator.share){await navigator.share(data);}else{await navigator.clipboard.writeText(data.url);showToast('تم نسخ رابط الموقع');}}catch(e){/* user cancelled */}
  }

  function showToast(text){
    let t=$('#enhToast'); if(!t){t=document.createElement('div');t.id='enhToast';t.style.cssText='position:fixed;right:18px;bottom:18px;z-index:10001;padding:10px 14px;border:1px solid rgba(255,255,255,.14);border-radius:12px;background:rgba(15,18,15,.92);color:#d8ddd5;font:600 12px/1.4 Cairo,sans-serif;backdrop-filter:blur(10px);transition:.2s';document.body.appendChild(t);} t.textContent=text;t.style.opacity='1';clearTimeout(t._tm);t._tm=setTimeout(()=>t.style.opacity='0',1800);
  }

  function addContact(){
    const footer=$('.site-footer'); if(!footer || $('#contact')) return;
    const section=document.createElement('section'); section.id='contact'; section.className='enh-contact enh-section';
    section.innerHTML=`<div class="enh-shell"><div class="enh-contact-card enh-reveal"><div class="enh-kicker">لنبدأ</div><h2 class="enh-title">لديك فكرة؟ يمكننا تحويلها إلى مشروع.</h2><p class="enh-subtitle">اطلع على المشاريع ثم تواصل معي مباشرة عبر Instagram أو Facebook. ويمكنك أيضًا نسخ وسيلة التواصل أو مشاركة هذا الموقع.</p><div class="enh-contact-actions"><a class="enh-primary" href="${instagram}" target="_blank" rel="noopener">تواصل معي</a><button class="enh-secondary" id="enhCopyContact" type="button">نسخ وسيلة التواصل</button><button class="enh-secondary" id="enhShareSite" type="button">مشاركة الموقع</button><a class="enh-secondary enh-cv-link" id="enhCvLink" href="assets/Radwan-CV.pdf" download hidden>تحميل CV</a></div><div class="enh-copy-status" id="enhCopyStatus" aria-live="polite"></div><div class="enh-contact-socials"><a href="${instagram}" target="_blank" rel="noopener" data-tip="Instagram" aria-label="Instagram">${icons.instagram}</a><a href="${facebook}" target="_blank" rel="noopener" data-tip="Facebook" aria-label="Facebook">${icons.facebook}</a><a href="https://github.com/rad03i2" target="_blank" rel="noopener" data-tip="GitHub" aria-label="GitHub">${icons.github}</a></div></div></div>`;
    footer.insertAdjacentElement('beforebegin',section);
    $('#enhCopyContact').addEventListener('click',async()=>{try{await navigator.clipboard.writeText(instagram);$('#enhCopyStatus').textContent='تم نسخ رابط التواصل.';showToast('تم نسخ وسيلة التواصل');}catch(e){$('#enhCopyStatus').textContent=instagram;}});
    $('#enhShareSite').addEventListener('click',shareSite);
    fetch('assets/Radwan-CV.pdf',{method:'HEAD'}).then(r=>{if(r.ok) $('#enhCvLink').hidden=false;}).catch(()=>{});
  }

  function addBackToTop(){
    if($('#enhBackTop')) return;
    const b=document.createElement('button'); b.id='enhBackTop'; b.className='enh-backtop'; b.type='button'; b.setAttribute('aria-label','العودة إلى أعلى الصفحة'); b.dataset.tip='للأعلى'; b.innerHTML=icons.up; document.body.appendChild(b);
    b.addEventListener('click',()=>window.scrollTo({top:0,behavior:'smooth'}));
    const update=()=>b.classList.toggle('is-visible',window.scrollY>650); window.addEventListener('scroll',update,{passive:true}); update();
  }

  function polishTooltips(){
    $$('.hero-socials a').forEach(a=>a.dataset.tip=a.getAttribute('title')||a.getAttribute('aria-label')||'');
    $$('.github-icon-button').forEach(a=>a.dataset.tip='GitHub');
    const heroProject=$('.hero-actions .button'); if(heroProject) heroProject.dataset.tip='استعرض المشاريع';
  }

  function revealOnScroll(){
    const nodes=$$('.enh-reveal');
    if(!nodes.length) return;
    if(matchMedia('(prefers-reduced-motion: reduce)').matches){nodes.forEach(n=>n.classList.add('is-visible'));return;}
    const io=new IntersectionObserver(entries=>entries.forEach(x=>{if(x.isIntersecting){x.target.classList.add('is-visible');io.unobserve(x.target);}}),{threshold:.12,rootMargin:'0px 0px -30px'});
    nodes.forEach(n=>io.observe(n));
  }

  function bootProjects(retries=0){
    if(!prepareProjectCards()){
      if(retries<30) setTimeout(()=>bootProjects(retries+1),100);
      return;
    }
    addProjectTools(); bindProjectModal(); polishTooltips(); revealOnScroll();
  }

  function boot(){
    injectHead(); addAvailability(); addStatsAndTicker(); addServices(); addContact(); addBackToTop(); polishTooltips(); revealOnScroll(); bootProjects();
  }

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',boot,{once:true}); else boot();
})();
