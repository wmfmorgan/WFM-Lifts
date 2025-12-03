# app/utils.py
# THE ULTIMATE STARTING STRENGTH WARMUP & PLATE CALCULATOR
# HULKAMANIA CERTIFIED — NO WEAKNESS ALLOWED

from typing import List, Dict
from flask import current_app
from app.models import Plate

# Standard Olympic bar
BAR_WEIGHT = 45.0

# Default plates — user can override in settings later
DEFAULT_PLATES = [45, 35, 25, 10, 5, 2.5]

def get_available_plates(user_id=None):
    if user_id:
        plates = Plate.query.filter_by(user_id=user_id).all()
        if plates:
            return sorted([p.weight for p in plates], reverse=True)
    return DEFAULT_PLATES.copy()  # only if you somehow have zero plates

def calculate_warmups(working_weight: float, exercise: str = "", user_id=None) -> List[Dict]:
    plates = get_available_plates(user_id)
    
    if working_weight <= BAR_WEIGHT:
        return [{
            "weight": BAR_WEIGHT,
            "reps": 5,
            "sets": 2,
            "plates": "Empty Barbell",
            "type": "warmup",
            "is_work": False
        }]

    diff = working_weight - BAR_WEIGHT
    # Use Starting Strength actual logic: round jump to nearest 5 lb
    jump = round((working_weight - BAR_WEIGHT) / 4 / 5) * 5
    if jump < 10:
        jump = 10                           # Never jump less than 10 lb

    warmups = [
        {"weight": BAR_WEIGHT, "reps": 5, "sets": 2, "type": "warmup", "is_work": False},
        {"weight": round(BAR_WEIGHT + jump, 1), "reps": 5, "sets": 1, "type": "warmup", "is_work": False},
        {"weight": round(BAR_WEIGHT + 2*jump, 1), "reps": 3, "sets": 1, "type": "warmup", "is_work": False},
        {"weight": round(BAR_WEIGHT + 3*jump, 1), "reps": 2, "sets": 1, "type": "warmup", "is_work": False},
    ]

    # Work sets
    work_sets = 1 if exercise.lower() in ["deadlift", "power clean", "powerclean"] else 3
    warmups.append({
        "weight": working_weight,
        "reps": 5,
        "sets": work_sets,
        "type": "work",
        "is_work": True
    })

    # Calculate plates for every set
    for s in warmups:
        s["plates"] = calculate_plates(s["weight"], plates)

    return warmups

def calculate_plates(target_weight: float, available_plates: List[float] = None) -> str:
    if available_plates is None:
        available_plates = get_available_plates()

    if abs(target_weight - BAR_WEIGHT) < 0.1:
        return "Empty Barbell"

    per_side = (target_weight - BAR_WEIGHT) / 2
    per_side = round(per_side, 1)
    
    if per_side <= 0:
        return "Empty Barbell"

    # Sort descending
    plates = sorted(available_plates, reverse=True)

    used = {}

    for plate in plates:
        count = int(per_side // plate)
        if count > 0:
            used[plate] = count + 1
            per_side -= plate
            per_side = round(per_side, 1)

    # Build string — always show pairs
    parts = []
    
    for plate in sorted(used.keys(), reverse=True):
        count = used[plate]
        if count == 1:
            parts.append(f"{plate}")
        else:
            parts.append(f"2×{plate}")

    result = "\n".join(parts)
    return f"bar \n {result}" if result else "Empty Barbell"

# TEST IT LIKE A BOSS
if __name__ == "__main__":
    print("SQUAT 315")
    for s in calculate_warmups(315, "squat"):
        print(f"{s['weight']} × {s['reps']} × {s['sets']} → {s['plates']}")
    
    print("\nDEADLIFT 405")
    for s in calculate_warmups(405, "deadlift"):
        print(f"{s['weight']} × {s['reps']} × {s['sets']} → {s['plates']}")