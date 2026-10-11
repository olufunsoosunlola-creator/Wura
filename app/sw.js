// WURA service worker: keeps the app working offline.
// Bump VERSION whenever the app files change so phones pick up the update.
const VERSION = 'wura-ca6561941b';
const SHELL = [
  './',
  'index.html',
  'manifest.webmanifest',
  'pwa-shim.js',
  'support.js',
  'image-slot.js',
  'image-slots.state.json',
  'styles.css',
  'ds_bundle.js',
  'vendor/react.production.min.js',
  'vendor/react-dom.production.min.js',
  'icons/icon-192.png',
  'icons/icon-512.png',
  'icons/apple-touch-icon.png'
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(VERSION).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== VERSION && k !== 'wura-fonts').map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  // Google Fonts: cache-first, kept across app updates.
  if (url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com') {
    e.respondWith(caches.open('wura-fonts').then((c) =>
      c.match(req).then((hit) => hit || fetch(req).then((res) => { if (res.ok || res.type === 'opaque') c.put(req, res.clone()); return res; }))
    ));
    return;
  }
  if (url.origin !== location.origin) return;

  // App files: serve from cache instantly, refresh in the background.
  e.respondWith(caches.open(VERSION).then((c) =>
    c.match(req, { ignoreSearch: true }).then((hit) => {
      const net = fetch(req).then((res) => { if (res.ok) c.put(req, res.clone()); return res; }).catch(() => hit || (req.mode === 'navigate' ? c.match('index.html') : undefined));
      return hit || net;
    })
  ));
});
