/* Mikhbar permanent light theme */
(()=>{document.documentElement.style.colorScheme='light';let m=document.querySelector('meta[name="theme-color"]');if(!m){m=document.createElement('meta');m.name='theme-color';document.head.appendChild(m)}m.content='#ffffff';})();

(()=>{
'use strict';
document.documentElement.classList.add('js');
if(!document.querySelector('link[data-rt-media]')){const l=document.createElement('link');l.rel='stylesheet';l.href='/forum/forum-media.css';l.dataset.rtMedia='1';document.head.appendChild(l)}
const $=(s,r=document)=>r.querySelector(s);const $$=(s,r=document)=>Array.from(r.querySelectorAll(s));
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const locale=(document.body.dataset.locale||document.documentElement.lang||'ar').toLowerCase().startsWith('en')?'en':'ar';
const isAr=locale==='ar';
function normalizePlatformNav(){
  const nav=$('#navigation');
  if(!nav)return;
  const forbidden=new Set([
    'المنتدى','اطلب مشروعك','احجز استشارة',
    'Forum','Request a project','Request your project','Book consultation','Book a consultation'
  ]);
  $$('a',nav).forEach(a=>{if(forbidden.has((a.textContent||'').trim()))a.remove()});
  const homeUrl=isAr?'/forum/ar/':'/forum/en/';
  const items=[
    ['sections',homeUrl+'#sections',isAr?'الأقسام':'Sections'],
    ['top',homeUrl+'#top-stories',isAr?'الأهم الآن':'Top stories'],
    ['newsletter',homeUrl+'#newsletter',isAr?'النشرة':'Newsletter']
  ];
  const lang=$('.rt-lang-switch',nav);
  const about=$$('a',nav).find(a=>(a.getAttribute('href')||'')==='/forum/about/');
  items.forEach(([key,href,label])=>{
    if(nav.querySelector('[data-mikhbar-nav="'+key+'"]'))return;
    const a=document.createElement('a');
    a.dataset.mikhbarNav=key;a.href=href;a.textContent=label;
    nav.insertBefore(a,about||lang||null);
  });
}
function brandAssets(){
  const mark='/assets/brand/mikhbar/06-web-ready/icon/mikhbar-logo-mark.png';
  const favicon='/assets/brand/mikhbar/06-web-ready/favicon/favicon-large.png?v=20260922-tab4';
  let fav=document.querySelector('link[rel="icon"]');
  if(!fav){fav=document.createElement('link');fav.rel='icon';fav.type='image/png';document.head.appendChild(fav)}
  fav.href=favicon;
  $('link[rel*="icon"]').forEach(link=>{if(link!==fav)link.remove()});
  if(!document.querySelector('.rt-site-header')){
    const legacy=document.querySelector('.site-header');
    if(legacy){
      const site=isAr?'مِخبار':'Mikhbar',home=isAr?'الرئيسية':'Home',latest=isAr?'أحدث الأخبار':'Latest',about=isAr?'عن مِخبار':'About Mikhbar',lang=isAr?'EN':'عربي';
      const homeUrl=isAr?'/forum/ar/':'/forum/en/',langUrl=isAr?'/forum/en/':'/forum/ar/';
      legacy.outerHTML='<header class="rt-site-header"><div class="rt-navbar"><a class="mikhbar-brand" href="'+homeUrl+'" aria-label="'+site+'"><span class="mikhbar-brand-mark"><img src="'+mark+'" alt="" width="64" height="64"></span><span class="mikhbar-brand-copy"><strong>'+site+'</strong><small dir="ltr">MIKHBAR</small></span></a><button class="menu-button rt-menu-button" type="button" aria-label="'+(isAr?'فتح قائمة التنقل':'Open navigation')+'" aria-expanded="false" aria-controls="navigation"><svg aria-hidden="true" viewBox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h16"/></svg></button><nav class="nav-links rt-platform-nav" id="navigation" aria-label="'+(isAr?'التنقل الرئيسي':'Main navigation')+'"><a href="'+homeUrl+'">'+home+'</a><a href="'+homeUrl+'#latest">'+latest+'</a><a href="/forum/about/">'+about+'</a><a class="rt-lang-switch" href="'+langUrl+'">'+lang+'</a></nav></div></header>';
    }
  }
  $$('.mikhbar-brand-mark').forEach(el=>{if(!el.querySelector('img'))el.innerHTML='<img src="'+mark+'" alt="" width="64" height="64">'});
  normalizePlatformNav();
  setTimeout(normalizePlatformNav,350);
  setTimeout(normalizePlatformNav,1400);
}

const ABOUT_TRANSITION_VIDEO='/assets/brand/mikhbar/06-web-ready/lightweight-animations/mikhbar-logo-mark-alpha.webm?v=20260922-about1';
const ABOUT_TRANSITION_POSTER='/assets/brand/mikhbar/06-web-ready/lightweight-animations/mikhbar-logo-mark-poster-transparent.png';
const ABOUT_TRANSITION_MS=2000;
let aboutTransitionActive=false;

function ensureAboutTransition(){
  let overlay=$('#mikhbarAboutTransition');
  if(overlay)return overlay;
  overlay=document.createElement('div');
  overlay.id='mikhbarAboutTransition';
  overlay.className='mikhbar-about-transition';
  overlay.setAttribute('aria-hidden','true');
  overlay.innerHTML='<video class="mikhbar-about-transition__mark" muted playsinline preload="auto" poster="'+ABOUT_TRANSITION_POSTER+'"><source src="'+ABOUT_TRANSITION_VIDEO+'" type="video/webm"></video>';
  document.body.appendChild(overlay);
  const video=$('video',overlay);
  try{video.load()}catch{}
  return overlay;
}

function playAboutTransition(destination){
  if(aboutTransitionActive)return;
  aboutTransitionActive=true;
  const overlay=ensureAboutTransition();
  const video=$('video',overlay);
  overlay.classList.remove('is-leaving');
  overlay.classList.add('is-visible');
  overlay.setAttribute('aria-hidden','false');
  let navigated=false;
  const go=()=>{
    if(navigated)return;
    navigated=true;
    window.location.href=destination;
  };
  const leave=()=>{
    overlay.classList.add('is-leaving');
    window.setTimeout(go,150);
  };
  window.setTimeout(leave,Math.max(0,ABOUT_TRANSITION_MS-150));
  window.setTimeout(go,ABOUT_TRANSITION_MS+120);
  if(video){
    try{video.pause();video.currentTime=0}catch{}
    const p=video.play();
    if(p&&typeof p.catch==='function')p.catch(()=>{});
  }
}

function bindAboutTransition(){
  const preload=ensureAboutTransition();
  const warm=()=>{const v=$('video',preload);if(v&&v.readyState<2){try{v.load()}catch{}}};
  document.addEventListener('pointerover',e=>{
    const a=e.target.closest&&e.target.closest('a[href]');
    if(a&&new URL(a.href,location.href).pathname.replace(/\/+$/,'')==='/forum/about')warm();
  },{passive:true});
  document.addEventListener('click',e=>{
    if(e.defaultPrevented||e.button!==0||e.metaKey||e.ctrlKey||e.shiftKey||e.altKey)return;
    const a=e.target.closest&&e.target.closest('a[href]');
    if(!a)return;
    let url;
    try{url=new URL(a.href,location.href)}catch{return}
    if(url.origin!==location.origin)return;
    if(url.pathname.replace(/\/+$/,'')!=='/forum/about')return;
    if(location.pathname.replace(/\/+$/,'')==='/forum/about')return;
    e.preventDefault();
    playAboutTransition(url.href);
  });
}
const dict={
 ar:{count:n=>`${n} منشور`,fallbackCat:'تقنية',emptyNow:'ستظهر هنا الموضوعات الأحدث فور بدء النشر اليومي.',read:'',imgAlt:'صورة الخبر'},
 en:{count:n=>`${n} ${n===1?'post':'posts'}`,fallbackCat:'Technology',emptyNow:'The latest and most important stories will appear here as they are published.',read:'',imgAlt:'Story image'}
}[locale];
const fmt=d=>{try{return new Intl.DateTimeFormat(isAr?'ar-IQ':'en-US',{year:'numeric',month:'long',day:'numeric',hour:'numeric',minute:'2-digit'}).format(new Date(d))}catch{return d||''}};
const categoryMaps={
 ar:{ai:'الذكاء الاصطناعي',robotics:'الروبوتات',automation:'الأتمتة',mobile:'الهواتف',computers:'الحواسيب',apps:'التطبيقات والبرامج',web:'الويب',social:'التواصل الاجتماعي',security:'الأمن التقني',announcements:'إعلانات المنصة'},
 en:{ai:'Artificial Intelligence',robotics:'Robotics',automation:'Automation',mobile:'Mobile',computers:'Computing',apps:'Apps & Software',web:'Web',social:'Social Media',security:'Cybersecurity',announcements:'Announcements'}
};
const categoryMap=categoryMaps[locale];
const slugFor=p=>p.categorySlug||'general';
const imageFor=p=>p.image||p.images?.card||p.images?.hero||'/assets/social/home.jpg';
let allPosts=[],visibleCount=12,currentFilter=document.body.dataset.category||'all';
function menu(){const b=$('.menu-button'),n=$('#navigation');if(!b||!n)return;b.addEventListener('click',()=>{const open=b.getAttribute('aria-expanded')!=='true';b.setAttribute('aria-expanded',String(open));n.classList.toggle('is-open',open)});$$('a',n).forEach(a=>a.addEventListener('click',()=>{b.setAttribute('aria-expanded','false');n.classList.remove('is-open')}));}
function card(p){const cat=esc(p.category||categoryMap[slugFor(p)]||dict.fallbackCat);const time=esc(p.dateLabel||fmt(p.date));const read=esc(p.readTime||'');const image=esc(imageFor(p));const alt=esc(p.title||dict.imgAlt);return `<a class="rt-feed-item" href="${esc(p.url||'#')}"><div class="rt-feed-copy"><div class="rt-feed-kicker">${p.breaking?`<span class="rt-breaking">${isAr?'عاجل':'BREAKING'}</span>`:''}<span>${cat}</span></div><h3>${esc(p.title||'')}</h3><p>${esc(p.excerpt||'')}</p><div class="rt-feed-time">${time}${read?` · ${read}`:''}</div></div><div class="rt-thumb"><img src="${image}" alt="${alt}" loading="lazy" decoding="async" width="800" height="450"></div></a>`}
function nowItem(p,i){return `<a class="rt-now-item" href="${esc(p.url||'#')}"><span class="rt-now-num">0${i+1}</span><span><strong>${esc(p.title||'')}</strong><small>${esc(p.dateLabel||fmt(p.date))}</small></span></a>`}
function filtered(){const q=($('#rtSearch')?.value||'').trim().toLowerCase();return allPosts.filter(p=>{const byCat=currentFilter==='all'||slugFor(p)===currentFilter;const hay=[p.title,p.excerpt,p.category,...(p.tags||[])].join(' ').toLowerCase();return byCat&&(!q||hay.includes(q))})}
function renderFeed(){const box=$('#rtFeed'),empty=$('#rtEmpty'),count=$('#rtCount'),more=$('#rtLoadMore');if(!box)return;const list=filtered();if(count)count.textContent=dict.count(list.length);box.innerHTML=list.slice(0,visibleCount).map(card).join('');if(empty)empty.hidden=!!list.length;if(more){more.style.display=list.length>visibleCount?'block':'none';more.onclick=()=>{visibleCount+=12;renderFeed()}}}
function renderHome(){if(!allPosts.length)return;const lead=$('#rtLead'),latest=$('#rtNowList');const featured=allPosts.find(p=>p.featured)||allPosts[0];if(lead&&featured){lead.href=featured.url||'#';$('#rtLeadCategory',lead).textContent=featured.category||categoryMap[slugFor(featured)]||dict.fallbackCat;$('#rtLeadTitle',lead).textContent=featured.title||'';$('#rtLeadExcerpt',lead).textContent=featured.excerpt||'';$('#rtLeadDate',lead).textContent=featured.dateLabel||fmt(featured.date);$('#rtLeadRead',lead).textContent=featured.readTime||'';const img=$('#rtLeadImage',lead);if(img){img.src=imageFor(featured);img.alt=featured.title||dict.imgAlt}}if(latest){const list=allPosts.filter(p=>p!==featured).slice(0,5);latest.innerHTML=list.length?list.map(nowItem).join(''):`<div class="rt-empty-mini">${dict.emptyNow}</div>`}}
function renderCategory(){const slug=document.body.dataset.category;if(!slug)return;currentFilter=slug;const title=$('#rtCategoryCount');if(title)title.textContent=categoryMap[slug]||slug;renderFeed()}
async function load(){const urls=locale==='ar'?['/forum/posts-ar.json','/forum/posts.json']:['/forum/posts-en.json'];for(const url of urls){try{const r=await fetch(url,{cache:'no-store'});if(!r.ok)continue;const data=await r.json();allPosts=(Array.isArray(data)?data:(data.posts||[])).slice().sort((a,b)=>String(b.date||'').localeCompare(String(a.date||'')));renderHome();renderFeed();renderCategory();return}catch{}}renderFeed()}
function bind(){const search=$('#rtSearch');if(search)search.addEventListener('input',()=>{visibleCount=12;renderFeed()});$$('[data-filter]').forEach(b=>b.addEventListener('click',e=>{e.preventDefault();currentFilter=b.dataset.filter||'all';visibleCount=12;$$('[data-filter]').forEach(x=>x.removeAttribute('aria-current'));b.setAttribute('aria-current','page');renderFeed()}));}
function year(){$$('[data-year]').forEach(e=>e.textContent=new Date().getFullYear())}
brandAssets();menu();bind();bindAboutTransition();year();load();
})();
