(()=>{
'use strict';
const $=(s,r=document)=>r.querySelector(s);const $$=(s,r=document)=>Array.from(r.querySelectorAll(s));
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const locale=(document.body.dataset.locale||document.documentElement.lang||'ar').toLowerCase().startsWith('en')?'en':'ar';
const isAr=locale==='ar';
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
menu();bind();year();load();
})();
