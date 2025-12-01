# app/models.py
from flask_login import UserMixin
from datetime import datetime
from . import db
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    current_phase = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    workouts = db.relationship('WorkoutLog', backref='user', lazy=True)
    plates = db.relationship('Plate', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class WorkoutLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    phase = db.Column(db.Integer, nullable=False)
    workout_type = db.Column(db.String(1), nullable=False)  # 'A', 'B', or 'C'
    is_rest_day = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    lifts = db.relationship('LiftEntry', backref='workout', lazy=True, cascade='all, delete-orphan')


class LiftEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workout_log.id'), nullable=False)
    exercise = db.Column(db.String(50), nullable=False)  # 'Squat', 'Bench Press', etc.
    
    # Starting / current working weights
    working_weight = db.Column(db.Float, nullable=False)  # lbs
    
    # Actual lifted (can differ if failed)
    actual_weight = db.Column(db.Float)
    
    # Warmup sets tracking (JSON because flexible)
    warmup_data = db.Column(db.JSON)  # [{weight: 135, reps: 5, completed: True}, ...]
    
    # Work sets tracking
    work_sets_completed = db.Column(db.Integer, default=0)  # out of 3 (or 1 for DL)
    work_sets_required = db.Column(db.Integer, default=3)
    
    failed = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)


class Plate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    weight = db.Column(db.Float, nullable=False)  # e.g., 45, 25, 10, 5, 2.5
    pair_count = db.Column(db.Integer, default=1)  # how many pairs you have


# === Starting Working Weights (one row per user) ===
class StartingWeights(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    
    squat = db.Column(db.Float, default=45.0)
    bench = db.Column(db.Float, default=45.0)
    press = db.Column(db.Float, default=45.0)
    deadlift = db.Column(db.Float, default=135.0)
    powerclean = db.Column(db.Float, default=95.0)