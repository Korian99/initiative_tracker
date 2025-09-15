self.addEventListener("install", e => {
  console.log("Service Worker installed");
});

self.addEventListener("fetch", e => {
  // For now just pass everything through
  e.respondWith(fetch(e.request));
});
