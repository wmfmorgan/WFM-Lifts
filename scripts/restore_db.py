
import json
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User, StartingWeights, Plate, WorkoutLog, LiftEntry
from sqlalchemy import text

def restore_data():
    filename = "db_backup_full.json"
    if not os.path.exists(filename):
        print(f"Error: {filename} not found. Run dump_db.py first.")
        return

    app = create_app()
    with app.app_context():
        print(f"Connected to: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Confirm
        confirm = input("WARNING: This will WIPE the current database and import data from JSON. Type 'YES' to proceed: ")
        if confirm != "YES":
            print("Aborted.")
            return

        # Load JSON
        with open(filename, "r") as f:
            data = json.load(f)

        # 1. Clear Tables
        print("Clearing existing tables...")
        try:
            db.session.query(LiftEntry).delete()
            db.session.query(WorkoutLog).delete()
            db.session.query(Plate).delete()
            db.session.query(StartingWeights).delete()
            db.session.query(User).delete()
            db.session.commit()
            print("Tables cleared.")
        except Exception as e:
            print(f"Error clearing tables: {e}")
            db.session.rollback()
            return

        # 2. Import Users
        print("Importing Users...")
        for row in data["users"]:
            u = User(
                id=row["id"],
                username=row["username"],
                password_hash=row["password_hash"],
                current_phase=row["current_phase"],
                created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None
            )
            db.session.add(u)
        db.session.commit()
        # Reset sequence
        try:
            max_id = max([x['id'] for x in data["users"]]) if data["users"] else 1
            db.session.execute(text(f"SELECT setval('user_id_seq', {max_id}, true)"))
            db.session.commit()
        except:
            pass # Sequence update might fail on SQLite or if seq name differs, ignore

        # 3. Import StartingWeights
        print("Importing StartingWeights...")
        for row in data["starting_weights"]:
            w = StartingWeights(
                id=row["id"],
                user_id=row["user_id"],
                squat=row["squat"],
                bench=row["bench"],
                press=row["press"],
                deadlift=row["deadlift"],
                powerclean=row["powerclean"]
            )
            db.session.add(w)
        db.session.commit()

        # 4. Import Plates
        print("Importing Plates...")
        for row in data["plates"]:
            p = Plate(
                id=row["id"],
                user_id=row["user_id"],
                weight=row["weight"],
                pair_count=row["pair_count"]
            )
            db.session.add(p)
        db.session.commit()

        # 5. Import Workouts
        print("Importing Workouts...")
        for row in data["workouts"]:
            w = WorkoutLog(
                id=row["id"],
                user_id=row["user_id"],
                date=datetime.fromisoformat(row["date"]).date(),
                phase=row["phase"],
                workout_type=row["workout_type"],
                is_rest_day=row["is_rest_day"],
                notes=row["notes"],
                created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None
            )
            db.session.add(w)
        db.session.commit()

        # 6. Import Lifts
        print("Importing LiftEntries...")
        for row in data["lifts"]:
            l = LiftEntry(
                id=row["id"],
                workout_id=row["workout_id"],
                exercise=row["exercise"],
                working_weight=row["working_weight"],
                actual_weight=row["actual_weight"],
                warmup_data=row["warmup_data"],
                work_sets_completed=row["work_sets_completed"],
                work_sets_required=row["work_sets_required"],
                failed=row["failed"],
                notes=row["notes"]
            )
            db.session.add(l)
        db.session.commit()

        print("\nSUCCESS! Database Restored.")

if __name__ == "__main__":
    restore_data()
