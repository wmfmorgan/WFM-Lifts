// app/static/js/main.js
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('weight-form');
    if (!form) return;

    form.addEventListener('submit', function (e) {
        e.preventDefault();

        const updates = {};
        document.querySelectorAll('.weight-input').forEach(input => {
            const liftName = input.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            updates[liftName] = parseFloat(input.value) || 45;
        });

        if (navigator.onLine) {
            sendWeightsToServer(updates);
        } else {
            // Save offline — will sync on reconnect
            saveWorkoutOffline({ type: 'weight-update', updates });
            showOfflineBanner();  // reuse the banner function
            alert("OFFLINE — Weights saved locally. Will sync when online.");
            // location.reload();
            Object.keys(updates).forEach(liftName => {
            const card = Array.from(document.querySelectorAll('.lift-card'))
                .find(c => {
                                const headerText = c.querySelector('h2')?.textContent || '';
                                return headerText.trim().replace(/\s+/g, ' ') === liftName;
                            });
            if (card) {
                    const newWeight = updates[liftName];
                    const workingWeightEl = card.querySelector('.working-weight');
                    if (workingWeightEl) workingWeightEl.textContent = `${newWeight} lb`;
                    console.log('generating new lifts');
                    // Re-generate warmups
                    const warmups = generateWarmups(newWeight, liftName);
                    const setsContainer = card.querySelector('.sets');
                    if (setsContainer) {
                        setsContainer.innerHTML = ''; // clear old
                        warmups.forEach(set => {
                            const setEl = document.createElement('div');
                            setEl.className = `set ${set.is_work ? 'work-set' : 'warmup-set'}`;
                            setEl.innerHTML = `
                                <div class="weight">${set.weight} lb</div>
                                <div class="reps-sets">${set.reps} × ${set.sets}</div>
                                <div class="plates">${set.plates}</div>
                                ${set.is_work ? '<button class="done-btn">WORK SET</button>' : '<button class="done-btn">Done</button>'}
                            `;
                            setsContainer.appendChild(setEl);
                        });
                    }
                }
            });


        }
    });

    function sendWeightsToServer(updates) {
        fetch('/update-working-weights', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updates)
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                alert('WORKING WEIGHTS UPDATED — LOCKED IN!');
                location.reload();
            }
        })
        .catch(err => {
            console.log("Weight update failed — saving offline", err);
            saveWorkoutOffline({ type: 'weight-update', updates });
            showOfflineBanner();  // reuse the banner function
            alert("OFFLINE — Weights saved locally. Will sync later.");
            // location.reload();
        });
    }
    // Pure JS version of calculate_warmups (client-side only)
    function generateWarmups(workingWeight, liftName) {
        const BAR = 45;
        const sets = [];

        if (workingWeight <= BAR) {
            // Classic empty-bar warmups
            sets.push({ weight: BAR, reps: 5, sets: 2, plates: "Empty Barbell", is_work: false });
            sets.push({ weight: BAR, reps: 5, sets: 1, plates: "Empty Barbell", is_work: false });
            sets.push({ weight: BAR, reps: 3, sets: 1, plates: "Empty Barbell", is_work: false });
            sets.push({ weight: BAR, reps: 2, sets: 1, plates: "Empty Barbell", is_work: false });
        } else {
            const diff = workingWeight - BAR;
            const jump = Math.round(diff / 4 / 5) * 5;  // nearest 5 lb

            sets.push({ weight: BAR, reps: 5, sets: 2, plates: "Empty Barbell", is_work: false });
            sets.push({ weight: BAR + jump, reps: 5, sets: 1, plates: calculatePlates(BAR + jump), is_work: false });
            sets.push({ weight: BAR + 2*jump, reps: 3, sets: 1, plates: calculatePlates(BAR + 2*jump), is_work: false });
            sets.push({ weight: BAR + 3*jump, reps: 2, sets: 1, plates: calculatePlates(BAR + 3*jump), is_work: false });
        }

        // Work sets
        const workSets = (liftName.toLowerCase().includes('deadlift') || liftName.toLowerCase().includes('clean')) ? 1 : 3;
        sets.push({
            weight: workingWeight,
            reps: 5,
            sets: workSets,
            plates: calculatePlates(workingWeight),
            is_work: true
        });

        return sets;
    }

    function calculatePlates(total) {
        if (total <= 45) return "Empty Barbell";
        const perSide = (total - 45) / 2;
        const plates = [45, 35, 25, 20, 15, 10, 5, 2.5];
        let remaining = perSide;
        console.log(remaining);
        let result = [];
        for (const p of plates) {
            const count = Math.floor(remaining / p);
            if (count > 0) {
                result.push(`2x${p}`);
                // result.push(count > 1 ? `${count+1}×${p}` : `${p}`);
                remaining -= p;
                console.log(remaining);
                if (remaining < 1) break;
            }
        }
        return "bar \n " + result.join("\n");
    }
});

// WORKOUT COMPLETE BUTTON — LOCK IN +5 lb GAINS
// WORKOUT COMPLETE BUTTON — NOW WITH OFFLINE SUPERPOWERS
document.getElementById('complete-btn')?.addEventListener('click', function () {
    const liftData = {};
    document.querySelectorAll('.lift-card').forEach(card => {
        const name = card.querySelector('h2').textContent.trim();
        const workSets = card.querySelectorAll('.work-set');
        const completed = card.querySelectorAll('.work-set .done-btn.completed').length;
        const required = workSets.length;
        const actualWeights = [];
        workSets.forEach(set => {
            const input = set.querySelector('.actual-input');
            const weight = parseFloat(input.value) || 0;
            actualWeights.push(weight);
        });
        liftData[name] = {
            completed_sets: completed,
            required_sets: required,
            actual_weights: actualWeights
        };
    });

    const phaseLine = Array.from(document.querySelectorAll('.subtitle'))
    .find(el => el.textContent.includes('Phase'));

    const workout_type = phaseLine 
    ? phaseLine.textContent.split(' • ')[1]?.split(' ')[1] 
    : 'A';

    const payload = {
        lift_details: liftData,
        workout_type: workout_type
    };

    // OFFLINE FIRST — TRUTH ALWAYS WINS
   if (navigator.onLine) {
        sendWorkoutToServer(payload);
    } else {
        saveWorkoutOffline(payload);
        showOfflineBanner();
        alert("NO SIGNAL — WORKOUT SAVED OFFLINE.\nWill sync when you're back online, brother.");
        // NO RELOAD — stay on page
    }
});

// SEND TO SERVER (WHEN ONLINE)
// SEND TO SERVER — BUT CATCH EVERYTHING
function sendWorkoutToServer(payload) {
    fetch('/complete-workout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(r => {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
    })
    .then(data => {
        if (data.success) {
            alert("REAL GAINS LOGGED — SYNCED!");
            location.reload();
        } else {
            throw new Error("Server said no");
        }
    })
    .catch(err => {
        console.log("Network failed — saving offline:", err);
        saveWorkoutOffline(payload);
        showOfflineBanner();
        alert("OFFLINE — Workout saved locally. Will sync later.");
        // NO RELOAD
    });
}

// OFFLINE REST DAY — THE ULTIMATE RECOVERY
document.getElementById('rest-day-btn')?.addEventListener('click', function (e) {
    e.preventDefault();

    const payload = {
        type: 'rest-day',
        date: new Date().toISOString().split('T')[0]  // today's date YYYY-MM-DD
    };

    if (navigator.onLine) {
        // Try server first
        fetch('/rest-day', { method: 'GET' })
            .then(r => r.text())
            .then(() => {
                // alert("REST DAY LOGGED — RECOVERY IS KING!");
                location.reload();
            })
            .catch(() => {
                // Fall back to offline
                saveWorkoutOffline(payload);
                showOfflineBanner();
                alert("OFFLINE — Rest day saved. Will sync when online.");
            });
    } else {
        saveWorkoutOffline(payload);
        showOfflineBanner();
        alert("OFFLINE — Rest day saved. Recovery is king.");
    }
});

// ONE GOD FUNCTION — MAKES ALL INTERNAL LINKS WORK OFFLINE
document.addEventListener('click', function (e) {
    const link = e.target.closest('a[href^="/"]');
    if (!link) return;
    console.log("god mode");
    const href = link.getAttribute('href');

    // Only intercept internal routes (not external links)
    if (href.startsWith('/') && !href.startsWith('//')) {
        e.preventDefault();

        // Offline or online — this always works
        window.location.href = href;
    }
});