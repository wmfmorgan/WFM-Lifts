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

def get_available_plates(user_id=None) -> Dict[float, int]:
    if user_id:
        plates = Plate.query.filter_by(user_id=user_id).all()
        if plates:
            return {p.weight: p.pair_count for p in plates}
    # Default inventory: infinite of everything for calculation, but we'll return 10 pairs if none specified
    return {p: 10 for p in DEFAULT_PLATES}

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

def calculate_plates(target_weight: float, available_inventory: Dict[float, int] = None) -> str:
    if available_inventory is None:
        available_inventory = get_available_plates()
    
    # If a list was passed, convert to dict with large counts
    if isinstance(available_inventory, list):
        available_inventory = {p: 10 for p in available_inventory}

    if abs(target_weight - BAR_WEIGHT) < 0.1:
        return "Empty Barbell"

    per_side = (target_weight - BAR_WEIGHT) / 2
    per_side = round(per_side, 1)
    
    if per_side <= 0:
        return "Empty Barbell"

    # Perfect math uses all standard plates regardless of inventory
    # But we want to calculate based on what *should* be there
    # Let's use a standard list for the math breakdown
    standard_plates = sorted(available_inventory.keys(), reverse=True)
    
    needed = {}
    remaining = per_side

    for plate in standard_plates:
        count = int(remaining // plate)
        if count > 0:
            needed[plate] = count
            remaining -= (count * plate)
            remaining = round(remaining, 1)

    # Build string — flag what's missing
    parts = []
    
    for plate in sorted(needed.keys(), reverse=True):
        count_needed = needed[plate]
        count_available = available_inventory.get(plate, 0)
        
        display = f"{count_needed}×{plate}" if count_needed > 1 else f"{plate}"
        
        if count_needed > count_available:
            missing = count_needed - count_available
            display += f" (MISSING {missing})"
            
        parts.append(display)

    result = "\n".join(parts)
    return f"bar \n {result}" if result else "Empty Barbell"
