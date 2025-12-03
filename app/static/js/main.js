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

        fetch('/update-working-weights', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updates)
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                alert('WORKING WEIGHTS UPDATED — LOCKED IN!');
                location.reload();  // refresh to show new warmups from server
            }
        });
    });

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
        const plates = [45, 35, 25, 10, 5, 2.5];
        let remaining = perSide;
        let result = [];

        for (const p of plates) {
            const count = Math.floor(remaining / p);
            if (count > 0) {
                result.push(count > 1 ? `${count}×${p}` : `${p}`);
                remaining -= count * p;
                if (remaining < 1) break;
            }
        }
        return "bar + " + result.join(" + ");
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
        alert("NO SIGNAL — WORKOUT SAVED OFFLINE.\nWill sync when you're back online, brother.");
        location.reload();
    }
});

// SEND TO SERVER (WHEN ONLINE)
function sendWorkoutToServer(payload) {
    fetch('/complete-workout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            alert("REAL GAINS LOGGED — SYNCED TO SERVER!");
            location.reload();
        } else {
            alert("Sync failed — saving offline...");
            saveWorkoutOffline(payload);
        }
    })
    .catch(err => {
        console.log("Network error — going offline", err);
        saveWorkoutOffline(payload);
        alert("OFFLINE — workout saved locally. Will sync later.");
        location.reload();
    });
}