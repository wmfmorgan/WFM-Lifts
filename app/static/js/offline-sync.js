// static/js/offline-sync.js
const DB_NAME = 'wfm-lifts-offline';
const STORE_NAME = 'pending-workouts';
let db;

function openDB() {
  return indexedDB.open(DB_NAME, 1, upgradeDB => {
    upgradeDB.createObjectStore(STORE_NAME, { autoIncrement: true });
  });
}

openDB().then(database => db = database);

// Save workout when offline
window.saveWorkoutOffline = function(workoutData) {
  if (!db) return;
  const tx = db.transaction(STORE_NAME, 'readwrite');
  tx.objectStore(STORE_NAME).add(workoutData);
  showOfflineBanner();
};

// Sync when back online
function syncPending() {
  if (!db || !navigator.onLine) return;
  const tx = db.transaction(STORE_NAME, 'readonly');
  const store = tx.objectStore(STORE_NAME);
  store.getAll().onsuccess = e => {
    const pending = e.target.result;
    if (pending.length === 0) return;

    fetch('/complete-workout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(pending[0])
    })
    .then(r => r.json())
    .then(data => {
      if (data.success) {
        // Remove synced workout
        const deleteTx = db.transaction(STORE_NAME, 'readwrite');
        deleteTx.objectStore(STORE_NAME).delete(pending[0].id || 1);
        hideOfflineBanner();
        syncPending(); // sync next
      }
    })
    .catch(() => console.log("Still offline or server down"));
  };
}

// Trigger sync on reconnect
window.addEventListener('online', syncPending);

// Banner
function showOfflineBanner() {
  let banner = document.getElementById('offline-banner');
  if (!banner) {
    banner = document.createElement('div');
    banner.id = 'offline-banner';
    banner.textContent = 'Offline — workout saved, will sync when online';
    banner.style.cssText = 'background:#f80;color:#000;padding:1rem;text-align:center;font-weight:bold;position:fixed;bottom:0;width:100%;z-index:9999;';
    document.body.appendChild(banner);
  }
}
function hideOfflineBanner() {
  const banner = document.getElementById('offline-banner');
  if (banner) banner.remove();
}