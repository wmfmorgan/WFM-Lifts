// static/js/offline-sync.js
const DB_NAME = 'wfm-lifts-offline';
const STORE_NAME = 'pending-workouts';
let db = null;

// Open IndexedDB the CORRECT way (no .then!)
const request = indexedDB.open(DB_NAME, 1);

request.onerror = () => {
  console.error("IndexedDB error:", request.error);
};

request.onsuccess = () => {
  db = request.result;
  console.log("Offline DB ready — WFM Lifts never forgets");
};

request.onupgradeneeded = (event) => {
  db = event.target.result;
  if (!db.objectStoreNames.contains(STORE_NAME)) {
    db.createObjectStore(STORE_NAME, { autoIncrement: true });
  }
};

// Save workout when offline
window.saveWorkoutOffline = function(workoutData) {
  if (!db) {
    console.warn("DB not ready yet — will try again in 1s");
    setTimeout(() => saveWorkoutOffline(workoutData), 1000);
    return;
  }
  const tx = db.transaction(STORE_NAME, 'readwrite');
  const store = tx.objectStore(STORE_NAME);
  store.add(workoutData);
  tx.oncomplete = () => {
    console.log("Workout saved offline");
    showOfflineBanner();
  };
};

// Sync when back online
function syncPending() {
  if (!db || !navigator.onLine) return;

  const tx = db.transaction(STORE_NAME, 'readonly');
  const store = tx.objectStore(STORE_NAME);
  const getAllRequest = store.getAll();

  getAllRequest.onsuccess = () => {
    const pending = getAllRequest.result;
    if (pending.length === 0) return;

    fetch('/complete-workout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(pending[0])
    })
    .then(r => r.json())
    .then(data => {
      if (data.success) {
        const deleteTx = db.transaction(STORE_NAME, 'readwrite');
        deleteTx.objectStore(STORE_NAME).delete(getAllRequest.resultKeys?.[0] || pending[0].id || 1);
        hideOfflineBanner();
        syncPending(); // next
      }
    })
    .catch(() => console.log("Still offline"));
  };
}

window.addEventListener('online', syncPending);

// Banner
function showOfflineBanner() {
  if (document.getElementById('offline-banner')) return;
  const banner = document.createElement('div');
  banner.id = 'offline-banner';
  banner.textContent = 'OFFLINE — Workout saved. Will sync when online.';
  banner.style.cssText = 'background:#f80;color:#000;padding:1rem;text-align:center;font-weight:bold;position:fixed;bottom:0;width:100%;z-index:9999;font-size:1.2rem;';
  document.body.appendChild(banner);
}

function hideOfflineBanner() {
  const banner = document.getElementById('offline-banner');
  if (banner) banner.remove();
}