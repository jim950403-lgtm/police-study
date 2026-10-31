const CACHE='pstudy-v4';
const ASSETS=['./','./index.html','./manifest.json','./icon.svg','./icon.png','./icon-192.png','./apple-touch-icon.png','./laws.json','./exams.json','./notes.json'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)));self.skipWaiting();});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))));self.clients.claim();});
// 網頁與資料：先抓網路最新版（法條自動更新），沒網路時用快取
self.addEventListener('fetch',e=>{
  const r=e.request;if(r.method!=='GET'||new URL(r.url).origin!==location.origin)return;
  const u=new URL(r.url);const fresh=r.mode==='navigate'||u.pathname.endsWith('.json')||u.pathname.endsWith('index.html');
  if(fresh){
    e.respondWith(fetch(r).then(res=>{if(res.ok){const cp=res.clone();caches.open(CACHE).then(c=>c.put(r.mode==='navigate'?'./index.html':r,cp));}return res;}).catch(()=>caches.match(r.mode==='navigate'?'./index.html':r)));
    return;
  }
  e.respondWith(caches.match(r).then(m=>m||fetch(r).then(res=>{const cp=res.clone();caches.open(CACHE).then(c=>c.put(r,cp));return res;})));
});
