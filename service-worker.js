const CACHE_VERSION='rad-portfolio-v3.5.0';
const CORE=['./','index.html','styles.css','projects.css','script.js','enhancements.css','enhancements.js','manifest.webmanifest','offline.html','assets/rad-icon.svg'];
self.addEventListener('install',event=>{event.waitUntil(caches.open(CACHE_VERSION).then(cache=>cache.addAll(CORE)).then(()=>self.skipWaiting()));});
self.addEventListener('activate',event=>{event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE_VERSION).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));});
self.addEventListener('fetch',event=>{
  const req=event.request;
  if(req.method!=='GET')return;
  const url=new URL(req.url);
  if(url.origin!==self.location.origin)return;
  if(req.mode==='navigate'){
    event.respondWith(fetch(req).then(res=>{const clone=res.clone();caches.open(CACHE_VERSION).then(c=>c.put(req,clone));return res;}).catch(()=>caches.match(req).then(r=>r||caches.match('offline.html'))));
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