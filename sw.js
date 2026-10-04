// Offline support: the app shell and the divrei Torah bank are cached on install;
// the weekly dvar Torah is fetched fresh when online and falls back to the cache.
const VERSION = "zmanim-v3";
const SHELL = [
  "./", "index.html", "manifest.webmanifest", "vendor/hebcal-core-6.10.0.min.js",
  "data/bank.json", "data/weekly.json", "icons/icon.svg", "icons/icon-192.png", "icons/apple-touch-icon.png"
];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== VERSION).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});

const networkFirst = async req => {
  const cache = await caches.open(VERSION);
  try {
    const res = await fetch(req);
    if (res.ok) cache.put(req, res.clone());
    return res;
  } catch {
    return (await cache.match(req, { ignoreSearch: true })) || Response.error();
  }
};

const cacheFirst = async req => {
  const hit = await caches.match(req);
  if (hit) return hit;
  const res = await fetch(req);
  if (res.ok || res.type === "opaque") (await caches.open(VERSION)).put(req, res.clone());
  return res;
};

self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  // Page and weekly data: prefer fresh, so updates show up without a new version
  if (req.mode === "navigate" || url.pathname.endsWith("/data/weekly.json")) { e.respondWith(networkFirst(req)); return; }
  // Everything else (code, bank, icons, Google Fonts): cache first
  if (url.origin === location.origin || url.hostname.endsWith("gstatic.com") || url.hostname.endsWith("googleapis.com")) e.respondWith(cacheFirst(req));
});
