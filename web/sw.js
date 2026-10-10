// 快取版本號，未來如果更新了 Flet 版本或核心檔案，改這個版本號即可強制刷新
const CACHE_NAME = 'nou-tools-engine-v1';

// 優先在背景預先快取的巨大靜態檔案（精確鎖定拖慢載入的元兇）
const ASSETS_TO_PRECACHE = [
  './',
  './index.html',
  './pyodide.asm.wasm',
  './python_stdlib.zip',
  './canvaskit.wasm',
  './main.dart.js'
];

// 安裝階段：將上述大型靜態檔寫入快取
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      // 容錯快取：即使個別檔案不存在也不會導致整批失敗
      return Promise.allSettled(
        ASSETS_TO_PRECACHE.map((url) => cache.add(url))
      );
    }).then(() => self.skipWaiting())
  );
});

// 啟動階段：清理舊版本的快取空間
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((name) => {
          if (name !== CACHE_NAME) {
            return caches.delete(name);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// 攔截網路請求：快取優先策略（Cache First）
self.addEventListener('fetch', (event) => {
  const url = event.request.url;

  // 針對 wasm、zip、大型 js 採取快取優先，其餘走網路
  const isLargeAsset = url.endsWith('.wasm') || 
                       url.endsWith('.zip') || 
                       url.endsWith('.whl') || 
                       url.includes('main.dart.js') ||
                       url.includes('canvaskit');

  if (isLargeAsset) {
    event.respondWith(
      caches.match(event.request).then((cachedResponse) => {
        if (cachedResponse) {
          // 快取命中，直接本機秒開回傳！
          return cachedResponse;
        }
        // 第一次造訪快取沒有，走網路請求並自動存進快取供下次使用
        return fetch(event.request).then((networkResponse) => {
          if (!networkResponse || networkResponse.status !== 200) {
            return networkResponse;
          }
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });
          return networkResponse;
        });
      })
    );
  } else {
    // 一般頁面請求採網路優先，網路斷線時回退至快取
    event.respondWith(
      fetch(event.request).catch(() => caches.match(event.request))
    );
  }
});
