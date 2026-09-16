const CACHE_VERSION='rad-portfolio-v3.19.0';
const CORE=['./','index.html','styles.css','projects.css','script.js','enhancements.css','enhancements.js','manifest.webmanifest','offline.html','assets/images/radwan-favicon.png','assets/images/radwan-favicon-180.png','favicon.ico'];
const UI_CLEANUP='<style id="rad-ui-cleanup">#enhHeaderControls{display:none!important}.enh-tech-strip:hover .enh-tech-track{animation-play-state:running!important}.enh-tech-icon{pointer-events:none!important}@media(max-width:760px){.enh-tech-strip{overflow-x:auto!important;overflow-y:hidden!important;scrollbar-width:none;-ms-overflow-style:none;-webkit-overflow-scrolling:touch}.enh-tech-strip::-webkit-scrollbar{display:none}.enh-tech-track{animation:none!important;transform:none!important;will-change:auto!important}.enh-tech-sequence[aria-hidden="true"]{display:none!important}}</style>';
const patchHtml=async res=>{const text=await res.text();const body=text.includes('</head>')?text.replace('</head>',UI_CLEANUP+'</head>'):UI_CLEANUP+text;const headers=new Headers(res.headers);headers.set('content-type','text/html; charset=utf-8');return new Response(body,{status:res.status,statusText:res.statusText,headers});};
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