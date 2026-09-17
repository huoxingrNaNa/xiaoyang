/* xiao小小阳 个人主页 · Service Worker
   策略：
   - HTML（导航请求）：网络优先，失败回退缓存 —— 保证你随时能拿到最新版，离线也能看
   - 静态资源（图片/图标/manifest）：缓存优先 + 后台更新
   - 第三方（abacus 计数器 / busuanzi / B站封面）：完全不碰，避免缓存住动态数据
   换图（头像/og.jpg/图标）后想强制刷新缓存，把 VER 改一下即可
*/
var VER = 'v2';
var CACHE = 'xiaoyang-' + VER;
var CORE = ['./', './index.html', './works.html', './game.html', './manifest.json', './avatar.jpg', './og.jpg', './icon-192.png', './icon-512.png'];

self.addEventListener('install', function (e) {
  e.waitUntil(
    caches.open(CACHE).then(function (c) {
      return Promise.all(CORE.map(function (u) {
        return c.add(new Request(u, { cache: 'reload' })).catch(function () {});
      }));
    }).then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener('activate', function (e) {
  e.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(keys.filter(function (k) { return k !== CACHE; }).map(function (k) { return caches.delete(k); }));
    }).then(function () { return self.clients.claim(); })
  );
});

self.addEventListener('fetch', function (e) {
  var req = e.request;
  if (req.method !== 'GET') return;
  var url;
  try { url = new URL(req.url); } catch (err) { return; }
  if (url.origin !== self.location.origin) return;   /* 第三方一律放行 */

  var isHTML = req.mode === 'navigate' || /\/$/.test(url.pathname) || /\.html$/i.test(url.pathname);
  if (isHTML) {
    e.respondWith(
      fetch(req).then(function (r) {
        var cp = r.clone();
        caches.open(CACHE).then(function (c) { c.put(req, cp); });
        return r;
      }).catch(function () {
        return caches.match(req).then(function (hit) {
          return hit || caches.match('./index.html');
        });
      })
    );
    return;
  }

  /* presence.txt：网络优先，尽量别吃缓存 —— 否则后门改了状态要等缓存过期才看到 */
  if (/\/presence\.txt$/i.test(url.pathname)) {
    e.respondWith(
      fetch(req).then(function (r) {
        var cp = r.clone();
        caches.open(CACHE).then(function (c) { c.put(req, cp); });
        return r;
      }).catch(function () { return caches.match(req); })
    );
    return;
  }

  e.respondWith(
    caches.match(req).then(function (hit) {
      var net = fetch(req).then(function (r) {
        var cp = r.clone();
        caches.open(CACHE).then(function (c) { c.put(req, cp); });
        return r;
      }).catch(function () { return hit; });
      return hit || net;
    })
  );
});
