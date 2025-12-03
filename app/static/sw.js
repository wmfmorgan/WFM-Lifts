// // static/sw.js — FINAL VERSION
const CACHE_NAME = 'wfm-lifts-v9';

const urlsToCache = [
  '/',                     // index.html
  '/history',
  '/history/',  
  '/settings',
  '/login',
  '/logout',
  '/register',

  // Templates (served as full pages)
  '/static/css/style.css',
  '/static/js/main.js',
  '/static/js/offline-sync.js',
  '/static/js/register-sw.js',

  // Icons
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',

  // Fonts (if you ever add any)
  // 'https://fonts.googleapis.com/...',
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(names => {
      return Promise.all(
        names.filter(name => name !== CACHE_NAME)
             .map(name => caches.delete(name))
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const url = event.request.url;

  // NEVER cache manifest.json — must always be fresh
  if (url.includes('manifest.json')) {
    event.respondWith(fetch(event.request));
    return;
  }

  // ALWAYS GET DASHBOARD FRESH — this is the magic line
  if (url.endsWith('/dashboard') || url.includes('/dashboard')) {
    event.respondWith(fetch(event.request));
    return;
  }

  // API CALLS — ALWAYS NETWORK. NO CACHED FALLBACK.
  if (url.includes('/complete-workout') || 
      url.includes('/update-working-weights') ||
      url.includes('/rest-day') ||
      url.includes('/login') ||
      url.includes('/logout')) {
    event.respondWith(fetch(event.request));
    return;
  }

  // Everything else — cache first, fallback to network
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});

// static/sw.js — DEBUG VERSION



// const CACHE_NAME = 'wfm-lifts-debug';

// self.addEventListener('install', e => {
//   console.log("SW installing");
//   self.skipWaiting();
// });

// self.addEventListener('activate', e => {
//   console.log("SW activating");
//   self.clients.claim();
// });

// self.addEventListener('fetch', event => {
//   const url = event.request.url;
//   console.log("SW FETCH:", url);

//   // BYPASS EVERYTHING — FORCE NETWORK
//   event.respondWith(
//     fetch(event.request)
//       .then(response => {
//         console.log("Fetched from network:", url, response.status);
//         return response;
//       })
//       .catch(err => {
//         console.error("Network failed:", err);
//         return new Response("OFFLINE MODE — NO CACHED DASHBOARD", { 
//           headers: {'Content-Type': 'text/plain'} 
//         });
//       })
//   );
// });