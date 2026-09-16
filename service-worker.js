const CACHE_VERSION='rad-portfolio-v3.18.0';
const CORE=['./','index.html','styles.css','projects.css','script.js','enhancements.css','enhancements.js','manifest.webmanifest','offline.html','assets/images/radwan-favicon.png','assets/images/radwan-favicon-180.png','favicon.ico'];
const PAGE_PATCH=`<style id="rad-ui-cleanup">#enhHeaderControls{display:none!important}.rad-telegram-link svg{width:15px;height:15px;display:block}</style><script id="rad-site-patch">(()=>{const TELEGRAM='https://t.me/DVDRH';const SVG='<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M21.6 3.4 18.4 19.9c-.24 1.16-.88 1.45-1.78.9l-4.88-3.6-2.35 2.26c-.26.26-.48.48-.98.48l.35-4.97 9.04-8.16c.39-.35-.09-.55-.61-.2L6.02 13.63l-4.81-1.5c-1.05-.33-1.07-1.05.22-1.55L20.25 3.32c.87-.32 1.63.2 1.35.08Z"/></svg>';const patch=()=>{document.getElementById('enhHeaderControls')?.remove();const floating=document.getElementById('enhFloatContact');if(floating){floating.href=TELEGRAM;floating.removeAttribute('target');floating.rel='noopener';floating.setAttribute('aria-label','Telegram');floating.title='Telegram';floating.textContent='@'}const socials=document.getElementById('heroSocials');if(socials&&!socials.querySelector('.rad-telegram-link')){const link=document.createElement('a');link.href=TELEGRAM;link.className='rad-telegram-link';link.rel='noopener';link.setAttribute('aria-label','Telegram');link.title='Telegram';link.innerHTML=SVG;socials.appendChild(link)}};const run=()=>{patch();setTimeout(patch,250)};if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',run,{once:true});else run()})();<\/script>`;
const patchHtml=async res=>{const text=await res.text();const body=text.includes('</head>')?text.replace('</head>',PAGE_PATCH+'</head>'):PAGE_PATCH+text;const headers=new Headers(res.headers);headers.set('content-type','text/html; charset=utf-8');return new Response(body,{status:res.status,statusText:res.statusText,headers});};
self.addEventListener('install',event=>{event.waitUntil(caches.open(CACHE_VERSION).then(cache=>cache.addAll(CORE)).then(()=>self.skipWaiting()));});
self.addEventListener('activate',event=>{event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE_VERSION).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));});
self.addEventListener('fetch',event=>{
  const req=event.request;
  if(req.method!=='GET')return;
  const url=new URL(req.url);
  if(url.origin!==self.location.origin)return;
  if(req.mode==='navigate'){
    event.respondWith(fetch(req).then(async res=>{const raw=res.clone();caches.open(CACHE_VERSION).then(c=>c.put(req,raw));return patchHtml(res);}).catch(()=>caches.match(req).then(async r=>r?patchHtml(r):patchHtml(await caches.match('offline.html')))));
    return;
  }
  if(/\.(?:png|jpe?g|webp|svg|gif|woff2?|ttf)$/i.test(url.pathname)){
    event.respondWith(caches.match(req).then(cached=>cached||fetch(req).then(res=>{const clone=res.clone();caches.open(CACHE_VERSION).then(c=>c.put(req,clone));return res;})));
    return;
  }
  event.respondWith(caches.match(req).then(cached=>{
    const network=fetch(req).then(res=>{const clone=res.clone();caches.open(CACHE_VERSION).then(c=>c.put(req,clone));return res;}).catch(()=>cached);
    return cached||network;
  }));
});
self.addEventListener('message',event=>{if(event.data==='SKIP_WAITING')self.skipWaiting();});