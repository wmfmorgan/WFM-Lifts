# app/utils.py
# THE ULTIMATE STARTING STRENGTH WARMUP & PLATE CALCULATOR
# HULKAMANIA CERTIFIED — NO WEAKNESS ALLOWED

from typing import List, Dict
from flask import current_app

# Standard Olympic bar
BAR_WEIGHT = 45.0

# Default plates — user can override in settings later
DEFAULT_PLATES = [45, 35, 25, 10, 5, 2.5]

def get_available_plates() -> List[float]:
    """Get plates from user settings or fall back to defaults"""
    # Later we'll pull from DB — for now, use defaults
    return DEFAULT_PLATES.copy()

def calculate_warmups(working_weight: float, exercise: str = "") -> List[Dict]:
    """
    Returns full warmup + work sets with perfect plate calculations
    Starting Strength style — 4 jumps from bar to working weight
    """
    if working_weight <= BAR_WEIGHT:
        return [{
            "weight": BAR_WEIGHT,
            "reps": 5,
            "sets": 2,
            "plates": "Empty Barbell",
            "type": "warmup",
            "is_work": False
        }]

    plates = get_available_plates()
    diff = working_weight - BAR_WEIGHT
    jump = round(diff / 4, 1)  # Clean rounding

    warmups = [
        {"weight": BAR_WEIGHT, "reps": 5, "sets": 2, "type": "warmup", "is_work": False},
        {"weight": BAR_WEIGHT + jump, "reps": 5, "sets": 1, "type": "warmup", "is_work": False},
        {"weight": BAR_WEIGHT + 2*jump, "reps": 3, "sets": 1, "type": "warmup", "is_work": False},
        {"weight": BAR_WEIGHT + 3*jump, "reps": 2, "sets": 1, "type": "warmup", "is_work": False},
    ]

    # Final work set
    work_sets = 3
    if exercise.lower() in ["deadlift", "power clean", "powerclean"]:
        work_sets = 1

    warmups.append({
        "weight": working_weight,
        "reps": 5,
        "sets": work_sets,
        "type": "work",
        "is_work": True
    })

    # Fix last warmup so it lands perfectly
    if len(warmups) > 1:
        warmups[-2]["weight"] = round(working_weight - jump, 1)

    # Calculate plates for every set
    for s in warmups:
        s["plates"] = calculate_plates(s["weight"], plates)

    return warmups


def calculate_plates(target_weight: float, available_plates: List[float] = None) -> str:
    """Returns perfect plate string: bar + 2×45 + 1×25 + 1×10"""
    if available_plates is None:
        available_plates = get_available_plates()

    if abs(target_weight - BAR_WEIGHT) < 0.1:
        return "Empty Barbell"

    to_load_per_side = (target_weight - BAR_WEIGHT) / 2
    remaining = round(to_load_per_side, 5)
    used = []

    for plate in sorted(available_plates, reverse=True):
        if remaining <= 0:
            break
        count = int(remaining // plate)
        if count > 0:
            used.append(f"{count}×{plate}" if count > 1 else f"{plate}")
            remaining -= count * plate
            remaining = round(remaining, 5)

    if remaining > 0.1:
        used.append(f"+ {remaining * 2:.1f} (micro)")

    plates_str = " + ".join(used)
    return f"bar + {plates_str}" if plates_str else "Empty Barbell"


# TEST IT LIKE A BOSS
if __name__ == "__main__":
    print("SQUAT 315")
    for s in calculate_warmups(315, "squat"):
        print(f"{s['weight']} × {s['reps']} × {s['sets']} → {s['plates']}")
    
    print("\nDEADLIFT 405")
    for s in calculate_warmups(405, "deadlift"):
        print(f"{s['weight']} × {s['reps']} × {s['sets']} → {s['plates']}")