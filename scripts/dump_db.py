
import json
import os
import sys
from datetime import date, datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User, StartingWeights, Plate, WorkoutLog, LiftEntry

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def dump_data():
    app = create_app()
    with app.app_context():
        print(f"Connected to: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        data = {
            "users": [],
            "starting_weights": [],
            "plates": [],
            "workouts": [],
            "lifts": []
        }

        # 1. Users
        users = User.query.all()
        for u in users:
            data["users"].append({
                "id": u.id,
                "username": u.username,
                "password_hash": u.password_hash,
                "current_phase": u.current_phase,
                "created_at": u.created_at
            })
        print(f"Exported {len(data['users'])} Users")

        # 2. Starting Weights
        weights = StartingWeights.query.all()
        for w in weights:
            data["starting_weights"].append({
                "id": w.id,
                "user_id": w.user_id,
                "squat": w.squat,
                "bench": w.bench,
                "press": w.press,
                "deadlift": w.deadlift,
                "powerclean": w.powerclean
            })
        print(f"Exported {len(data['starting_weights'])} Starting Weights")

        # 3. Plates
        plates = Plate.query.all()
        for p in plates:
            data["plates"].append({
                "id": p.id,
                "user_id": p.user_id,
                "weight": p.weight,
                "pair_count": p.pair_count
            })
        print(f"Exported {len(data['plates'])} Plates")

        # 4. Workouts
        workouts = WorkoutLog.query.all()
        for w in workouts:
            data["workouts"].append({
                "id": w.id,
                "user_id": w.user_id,
                "date": w.date,
                "phase": w.phase,
                "workout_type": w.workout_type,
                "is_rest_day": w.is_rest_day,
                "notes": w.notes,
                "created_at": w.created_at
            })
        print(f"Exported {len(data['workouts'])} Workouts")

        # 5. Lift Entries
        lifts = LiftEntry.query.all()
        for l in lifts:
            data["lifts"].append({
                "id": l.id,
                "workout_id": l.workout_id,
                "exercise": l.exercise,
                "working_weight": l.working_weight,
                "actual_weight": l.actual_weight,
                "warmup_data": l.warmup_data,
                "work_sets_completed": l.work_sets_completed,
                "work_sets_required": l.work_sets_required,
                "failed": l.failed,
                "notes": l.notes
            })
        print(f"Exported {len(data['lifts'])} Lift Entries")

        # Save to file
        filename = "db_backup_full.json"
        with open(filename, "w") as f:
            json.dump(data, f, default=json_serial, indent=2)
        
        print(f"\nSUCCESS! Database dumped to {filename}")

if __name__ == "__main__":
    dump_data()
