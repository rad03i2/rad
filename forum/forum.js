/* Mikhbar permanent light theme */
(()=>{document.documentElement.style.colorScheme='light';let m=document.querySelector('meta[name="theme-color"]');if(!m){m=document.createElement('meta');m.name='theme-color';document.head.appendChild(m)}m.content='#ffffff';})();

(()=>{
'use strict';
document.documentElement.classList.add('js');
if(!document.querySelector('link[href*="forum-media.css"]')){const l=document.createElement('link');l.rel='stylesheet';l.href='/forum-media.css?v=20260930-lead2';l.dataset.rtMedia='1';document.head.appendChild(l)}
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
  $$('link[rel*="icon"]').forEach(link=>{if(link!==fav)link.remove()});
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

const BRAND_INTRO_SRC='/assets/images/06_Mikhbar_Sticker_Animated_512.webp?v=20260930-brandintro7';
const BRAND_INTRO_MS=2050;
const BRAND_SAMPLE_SIZE=112;
const BRAND_ALPHA_TRIM=.018;

function brandAlphaBounds(imageData,w,h,trim=BRAND_ALPHA_TRIM){
  const rows=new Float64Array(h);
  const cols=new Float64Array(w);
  const data=imageData.data;
  let total=0;
  for(let y=0;y<h;y++){
    const rowOffset=y*w*4;
    for(let x=0;x<w;x++){
      const a=data[rowOffset+x*4+3];
      if(a<=8)continue;
      rows[y]+=a;
      cols[x]+=a;
      total+=a;
    }
  }
  if(total<=0)return{x:0,y:0,width:w,height:h};

  const cut=total*trim;
  const edge=(arr,reverse=false)=>{
    let sum=0;
    if(!reverse){
      for(let i=0;i<arr.length;i++){sum+=arr[i];if(sum>=cut)return i}
      return 0;
    }
    for(let i=arr.length-1;i>=0;i--){sum+=arr[i];if(sum>=cut)return i}
    return arr.length-1;
  };

  const left=edge(cols,false);
  const right=edge(cols,true);
  const top=edge(rows,false);
  const bottom=edge(rows,true);
  return{
    x:left,
    y:top,
    width:Math.max(1,right-left+1),
    height:Math.max(1,bottom-top+1)
  };
}

function brandSampleBounds(img,size=BRAND_SAMPLE_SIZE){
  const canvas=document.createElement('canvas');
  canvas.width=size;
  canvas.height=size;
  const ctx=canvas.getContext('2d',{alpha:true,willReadFrequently:true});
  if(!ctx)return{x:0,y:0,width:size,height:size};
  ctx.clearRect(0,0,size,size);
  ctx.drawImage(img,0,0,size,size);
  try{
    return brandAlphaBounds(ctx.getImageData(0,0,size,size),size,size);
  }catch{
    return{x:0,y:0,width:size,height:size};
  }
}

function brandImageReady(img){
  if(img.complete&&img.naturalWidth>0)return Promise.resolve(true);
  return new Promise(resolve=>{
    const done=ok=>resolve(ok);
    img.addEventListener('load',()=>done(true),{once:true});
    img.addEventListener('error',()=>done(false),{once:true});
    window.setTimeout(()=>done(false),2200);
  });
}

function brandIntro(){
  const marks=$$('.mikhbar-brand-mark');
  if(!marks.length)return;
  const reduced=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if(reduced){
    marks.forEach(mark=>mark.classList.add('is-brand-static'));
    return;
  }

  marks.forEach(async mark=>{
    const staticImg=Array.from(mark.children).find(node=>node.tagName==='IMG'&&!node.classList.contains('mikhbar-brand-intro-source'));
    if(!staticImg){mark.classList.add('is-brand-static');return}

    $$('.mikhbar-brand-intro,.mikhbar-brand-intro-source',mark).forEach(node=>node.remove());
    mark.classList.remove('is-brand-static');

    const source=document.createElement('img');
    source.className='mikhbar-brand-intro-source';
    source.src=BRAND_INTRO_SRC;
    source.alt='';
    source.setAttribute('aria-hidden','true');
    source.decoding='async';

    const canvas=document.createElement('canvas');
    canvas.className='mikhbar-brand-intro';
    canvas.setAttribute('aria-hidden','true');

    mark.appendChild(source);
    mark.appendChild(canvas);

    const ready=await Promise.all([brandImageReady(staticImg),brandImageReady(source)]);
    if(!ready[0]||!ready[1]){
      mark.classList.add('is-brand-static');
      source.remove();
      canvas.remove();
      return;
    }

    const cssW=mark.clientWidth||52;
    const cssH=mark.clientHeight||52;
    const dpr=Math.min(Math.max(window.devicePixelRatio||1,1),3);
    canvas.width=Math.max(1,Math.round(cssW*dpr));
    canvas.height=Math.max(1,Math.round(cssH*dpr));

    const ctx=canvas.getContext('2d',{alpha:true});
    if(!ctx){
      mark.classList.add('is-brand-static');
      source.remove();
      canvas.remove();
      return;
    }
    ctx.setTransform(dpr,0,0,dpr,0,0);
    ctx.imageSmoothingEnabled=true;
    ctx.imageSmoothingQuality='high';

    const target=brandSampleBounds(staticImg);
    const targetX=target.x/BRAND_SAMPLE_SIZE*cssW;
    const targetY=target.y/BRAND_SAMPLE_SIZE*cssH;
    const targetW=target.width/BRAND_SAMPLE_SIZE*cssW;
    const targetH=target.height/BRAND_SAMPLE_SIZE*cssH;
    const targetCX=targetX+targetW/2;
    const targetCY=targetY+targetH/2;

    const probe=document.createElement('canvas');
    probe.width=BRAND_SAMPLE_SIZE;
    probe.height=BRAND_SAMPLE_SIZE;
    const pctx=probe.getContext('2d',{alpha:true,willReadFrequently:true});
    const started=performance.now();
    let raf=0;
    let done=false;

    const finish=()=>{
      if(done)return;
      done=true;
      if(raf)cancelAnimationFrame(raf);
      mark.classList.add('is-brand-static');
      canvas.classList.add('is-finishing');
      window.setTimeout(()=>{
        canvas.remove();
        source.remove();
      },90);
    };

    const paint=now=>{
      if(done)return;
      if(!pctx){finish();return}

      pctx.clearRect(0,0,BRAND_SAMPLE_SIZE,BRAND_SAMPLE_SIZE);
      pctx.drawImage(source,0,0,BRAND_SAMPLE_SIZE,BRAND_SAMPLE_SIZE);

      let bounds;
      try{
        bounds=brandAlphaBounds(
          pctx.getImageData(0,0,BRAND_SAMPLE_SIZE,BRAND_SAMPLE_SIZE),
          BRAND_SAMPLE_SIZE,
          BRAND_SAMPLE_SIZE
        );
      }catch{
        bounds={x:0,y:0,width:BRAND_SAMPLE_SIZE,height:BRAND_SAMPLE_SIZE};
      }

      const naturalW=source.naturalWidth||512;
      const naturalH=source.naturalHeight||512;
      const sx=bounds.x/BRAND_SAMPLE_SIZE*naturalW;
      const sy=bounds.y/BRAND_SAMPLE_SIZE*naturalH;
      const sw=Math.max(1,bounds.width/BRAND_SAMPLE_SIZE*naturalW);
      const sh=Math.max(1,bounds.height/BRAND_SAMPLE_SIZE*naturalH);

      const scale=Math.min(targetW/sw,targetH/sh);
      const dw=Math.max(.5,sw*scale);
      const dh=Math.max(.5,sh*scale);
      const dx=targetCX-dw/2;
      const dy=targetCY-dh/2;

      ctx.clearRect(0,0,cssW,cssH);
      ctx.drawImage(source,sx,sy,sw,sh,dx,dy,dw,dh);

      if(now-started>=BRAND_INTRO_MS){finish();return}
      raf=requestAnimationFrame(paint);
    };

    raf=requestAnimationFrame(paint);
    window.setTimeout(finish,BRAND_INTRO_MS+350);
  });
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
const pageSize=document.body.classList.contains('rt-home')?24:12;
let allPosts=[],visibleCount=pageSize,currentFilter=document.body.dataset.category||'all';
const HERO_INTERVAL_MS=3000;
let heroPosts=[],heroIndex=0,heroTimer=null;
function menu(){
  const b=$('.menu-button'),n=$('#navigation');if(!b||!n)return;
  const setOpen=open=>{b.setAttribute('aria-expanded',String(open));b.setAttribute('aria-label',isAr?(open?'إغلاق قائمة التنقل':'فتح قائمة التنقل'):(open?'Close navigation':'Open navigation'));n.classList.toggle('is-open',open)};
  b.addEventListener('click',()=>setOpen(b.getAttribute('aria-expanded')!=='true'));
  $$('a',n).forEach(a=>a.addEventListener('click',()=>setOpen(false)));
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&b.getAttribute('aria-expanded')==='true'){setOpen(false);b.focus()}});
  document.addEventListener('click',e=>{if(!n.contains(e.target)&&!b.contains(e.target))setOpen(false)});
  const desktop=matchMedia('(min-width:981px)');desktop.addEventListener('change',e=>{if(e.matches)setOpen(false)});
}
function card(p){const cat=esc(p.category||categoryMap[slugFor(p)]||dict.fallbackCat);const time=esc(p.dateLabel||fmt(p.date));const read=esc(p.readTime||'');const image=esc(imageFor(p));const alt=esc(p.title||dict.imgAlt);return `<a class="rt-feed-item" href="${esc(p.url||'#')}"><div class="rt-feed-copy"><div class="rt-feed-kicker">${p.breaking?`<span class="rt-breaking">${isAr?'عاجل':'BREAKING'}</span>`:''}<span>${cat}</span></div><h3>${esc(p.title||'')}</h3><p>${esc(p.excerpt||'')}</p><div class="rt-feed-time">${time}${read?` · ${read}`:''}</div></div><div class="rt-thumb"><img src="${image}" alt="${alt}" loading="lazy" decoding="async" width="800" height="450"></div></a>`}
function nowItem(p,i){return `<a class="rt-now-item" href="${esc(p.url||'#')}"><span class="rt-now-num">0${i+1}</span><span><strong>${esc(p.title||'')}</strong><small>${esc(p.dateLabel||fmt(p.date))}</small></span><img class="rt-now-thumb" src="${esc(imageFor(p))}" alt="" width="80" height="70" loading="lazy" decoding="async"></a>`}
function filtered(){const q=($('#rtSearch')?.value||'').trim().toLowerCase();return allPosts.filter(p=>{const byCat=currentFilter==='all'||slugFor(p)===currentFilter;const hay=[p.title,p.excerpt,p.category,...(p.tags||[])].join(' ').toLowerCase();return byCat&&(!q||hay.includes(q))})}
function renderFeed(){const box=$('#rtFeed'),empty=$('#rtEmpty'),count=$('#rtCount'),more=$('#rtLoadMore');if(!box)return;const list=filtered();if(count)count.textContent=dict.count(list.length);box.innerHTML=list.slice(0,visibleCount).map(card).join('');if(empty)empty.hidden=!!list.length;if(more){more.style.display=list.length>visibleCount?'block':'none';more.onclick=()=>{visibleCount+=pageSize;renderFeed()}}}
function paintHero(p,index,animate=true){
  const lead=$('#rtLead'),wrap=$('#rtLeadCarousel');if(!lead||!p)return;
  heroIndex=((index%heroPosts.length)+heroPosts.length)%heroPosts.length;
  lead.href=p.url||'#';
  $('#rtLeadCategory',lead).textContent=p.category||categoryMap[slugFor(p)]||dict.fallbackCat;
  $('#rtLeadTitle',lead).textContent=p.title||'';
  $('#rtLeadExcerpt',lead).textContent=p.excerpt||'';
  $('#rtLeadDate',lead).textContent=p.dateLabel||fmt(p.date);
  $('#rtLeadRead',lead).textContent=p.readTime||'';
  const img=$('#rtLeadImage',lead);if(img){img.src=imageFor(p);img.alt=p.title||dict.imgAlt}
  $$('.rt-lead-dot').forEach((dot,i)=>{const active=i===heroIndex;dot.classList.toggle('is-active',active);if(active)dot.setAttribute('aria-current','true');else dot.removeAttribute('aria-current')});
  if(animate&&wrap){wrap.classList.remove('is-changing');void wrap.offsetWidth;wrap.classList.add('is-changing');window.setTimeout(()=>wrap.classList.remove('is-changing'),320)}
  const next=heroPosts[(heroIndex+1)%heroPosts.length];if(next){const preload=new Image();preload.src=imageFor(next)}
}
function stopHero(){
  if(heroTimer){window.clearInterval(heroTimer);heroTimer=null}
}
function startHero(){
  stopHero();
  if(heroPosts.length<2)return;
  heroTimer=window.setInterval(()=>{
    if(document.hidden)return;
    const nextIndex=(heroIndex+1)%heroPosts.length;
    paintHero(heroPosts[nextIndex],nextIndex,true);
  },HERO_INTERVAL_MS);
}
function renderHeroDots(){
  const box=$('#rtLeadDots');if(!box)return;
  box.innerHTML=heroPosts.map((_,i)=>`<button class="rt-lead-dot" type="button" data-hero-dot="${i}" aria-label="${isAr?'عرض الخبر':'Show story'} ${i+1}"><span aria-hidden="true"></span></button>`).join('');
  $$('.rt-lead-dot',box).forEach((dot,i)=>dot.addEventListener('click',()=>{
    paintHero(heroPosts[i],i,true);
    startHero();
  }));
}
function stepHero(delta){
  if(!heroPosts.length)return;
  const nextIndex=(heroIndex+delta+heroPosts.length)%heroPosts.length;
  paintHero(heroPosts[nextIndex],nextIndex,true);
  startHero();
}
function renderHome(){
  if(!allPosts.length)return;
  const latest=$('#rtNowList');
  heroPosts=allPosts.slice(0,20);
  heroIndex=0;
  renderHeroDots();
  paintHero(heroPosts[0],0,false);
  startHero();
  if(latest){const list=allPosts.slice(1,4);latest.innerHTML=list.length?list.map(nowItem).join(''):`<div class="rt-empty-mini">${dict.emptyNow}</div>`}
}
function renderCategory(){const slug=document.body.dataset.category;if(!slug)return;currentFilter=slug;const title=$('#rtCategoryCount');if(title)title.textContent=categoryMap[slug]||slug;renderFeed()}
async function load(){const urls=locale==='ar'?['/posts-ar.json','/forum/posts-ar.json','/posts.json','/forum/posts.json']:['/posts-en.json','/forum/posts-en.json'];for(const url of urls){try{const r=await fetch(url,{cache:'no-store'});if(!r.ok)continue;const data=await r.json();allPosts=(Array.isArray(data)?data:(data.posts||[])).slice().sort((a,b)=>String(b.date||'').localeCompare(String(a.date||'')));renderHome();renderFeed();renderCategory();return}catch{}}}
function bind(){
  const search=$('#rtSearch');if(search)search.addEventListener('input',()=>{visibleCount=pageSize;renderFeed()});
  $$('[data-filter]').forEach(b=>b.addEventListener('click',e=>{e.preventDefault();currentFilter=b.dataset.filter||'all';visibleCount=12;$$('[data-filter]').forEach(x=>x.removeAttribute('aria-current'));b.setAttribute('aria-current','page');renderFeed()}));
  const prev=$('#rtLeadPrev'),next=$('#rtLeadNext');
  if(prev)prev.addEventListener('click',()=>stepHero(-1));
  if(next)next.addEventListener('click',()=>stepHero(1));
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stopHero();else startHero()});
}
function smartHeader(){
  const header=$('.rt-site-header');if(!header)return;
  let lastY=Math.max(0,window.scrollY||0);
  let ticking=false;
  const update=()=>{
    const y=Math.max(0,window.scrollY||0);
    const delta=y-lastY;
    const menuOpen=$('#navigation')?.classList.contains('is-open');
    if(y<80||menuOpen){
      header.classList.remove('rt-nav-hidden');
    }else if(delta>8){
      header.classList.add('rt-nav-hidden');
    }else if(delta<-4){
      header.classList.remove('rt-nav-hidden');
    }
    lastY=y;
    ticking=false;
  };
  window.addEventListener('scroll',()=>{
    if(ticking)return;
    ticking=true;
    window.requestAnimationFrame(update);
  },{passive:true});
  window.addEventListener('pageshow',()=>{lastY=Math.max(0,window.scrollY||0);header.classList.remove('rt-nav-hidden')});
}
function articleProgress(){
  const article=$('.rt-article');if(!article)return;
  let bar=$('.rt-reading-progress');
  if(!bar){
    bar=document.createElement('div');
    bar.className='rt-reading-progress';
    bar.setAttribute('aria-hidden','true');
    document.body.append(bar);
  }
  let fill=$('span',bar);
  if(!fill){fill=document.createElement('span');bar.append(fill)}
  let ticking=false;
  const update=()=>{
    const rect=article.getBoundingClientRect();
    const start=window.scrollY+rect.top;
    const end=start+article.offsetHeight-window.innerHeight;
    const progress=end>start?Math.min(1,Math.max(0,(window.scrollY-start)/(end-start))):0;
    fill.style.width=`${(progress*100).toFixed(2)}%`;
    ticking=false;
  };
  const onScroll=()=>{if(ticking)return;ticking=true;requestAnimationFrame(update)};
  window.addEventListener('scroll',onScroll,{passive:true});
  window.addEventListener('resize',onScroll,{passive:true});
  update();
}
function year(){$$('[data-year]').forEach(e=>e.textContent=new Date().getFullYear())}
brandAssets();brandIntro();menu();smartHeader();articleProgress();bind();bindAboutTransition();year();load();
})();
