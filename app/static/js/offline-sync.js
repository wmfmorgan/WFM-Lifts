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


function syncPending() {
  if (!db || !navigator.onLine) return;

  const tx = db.transaction(STORE_NAME, 'readonly');
  const store = tx.objectStore(STORE_NAME);
  
  const itemsRequest = store.getAll();
  const keysRequest = store.getAllKeys();

  // Wait for BOTH requests
  let items, keys;
  let completed = 0;

  const checkDone = () => {
    if (++completed === 2 && items && keys) {
      processNext(items, keys);
    }
  };

  itemsRequest.onsuccess = () => {
    items = itemsRequest.result;
    checkDone();
  };

  keysRequest.onsuccess = () => {
    keys = keysRequest.result;
    checkDone();
  };

  function processNext(items, keys) {
    if (items.length === 0) return;

    const item = items[0];
    const key = keys[0];
    // REST DAY — HIGHEST PRIORITY (recovery is king)
    if (item.type === 'rest-day') {
        fetch('/rest-day', { method: 'GET' })
        .then(r => {
            if (!r.ok) throw new Error("Rest day failed");
            return r.text();
        })
        .then(() => {
            console.log("REST DAY SYNCED — RECOVERY IS KING");
            deleteAndContinue(key);
        })
        .catch(err => {
            console.log("Rest day sync failed — will retry:", err);
            // Don't delete — retry later
        });
        return;
    }
    
    if (item.type === 'weight-update') {
      fetch('/update-working-weights', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(item.updates)
      })
      .then(r => { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
      .then(data => {
        if (data.success) deleteAndContinue(key);
      })
      .catch(err => console.log("Weight sync failed (retry):", err));
      return;
    }

    // workout log
    fetch('/complete-workout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(item)
    })
    .then(r => { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
    .then(data => {
      if (data.success) deleteAndContinue(key);
    })
    .catch(err => console.log("Workout sync failed (retry):", err));
  }

  function deleteAndContinue(key) {
    const deleteTx = db.transaction(STORE_NAME, 'readwrite');
    deleteTx.objectStore(STORE_NAME).delete(key);
    deleteTx.oncomplete = () => {
      hideOfflineBanner();
      syncPending();
    };
  }
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