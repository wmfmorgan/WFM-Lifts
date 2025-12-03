# app/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import date, timedelta
from app.models import WorkoutLog, StartingWeights
from app.utils import calculate_warmups
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.forms import RegistrationForm, LoginForm
from app.models import User, StartingWeights, LiftEntry, WorkoutLog, Plate
from app import db
from flask import jsonify

bp = Blueprint('routes', __name__)

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))
    return render_template('index.html')

# === TODAY'S WORKOUT DASHBOARD — THE MONEY MAKER ===
@bp.route('/')
@bp.route('/dashboard')
@login_required
def dashboard():
    today = date.today()
    
    # Get user's current phase
    phase = current_user.current_phase  # 1, 2, or 3
    
    # Get starting/current working weights
    weights = StartingWeights.query.filter_by(user_id=current_user.id).first()
    if not weights:
        flash("Set your starting weights first!", "warning")
        return redirect(url_for('routes.settings'))
    
    # Auto-detect what today should be: A, B, or C
    recent_workouts = WorkoutLog.query.filter(
        WorkoutLog.user_id == current_user.id,
        WorkoutLog.is_rest_day == False
    ).order_by(WorkoutLog.date.desc()).limit(10).all()
    
    last_workout = recent_workouts[0] if recent_workouts else None
    
    if not last_workout:
        workout_type = "A"
    else:
        if phase < 3:
            workout_type = "B" if last_workout.workout_type == "A" else "A"
        else:
            # Phase 3: A → B → C → A → ...
            cycle = ["A", "B", "C"]
            last_idx = cycle.index(last_workout.workout_type)
            workout_type = cycle[(last_idx + 1) % 3]
    
    # Define today's lifts based on phase + type
    lifts = {
        1: {"A": ["Squat", "Press", "Deadlift"], "B": ["Squat", "Bench Press", "Deadlift"]},
        2: {"A": ["Squat", "Press", "Deadlift"], "B": ["Squat", "Bench Press", "Power Clean"]},
        3: {"A": ["Squat", "Press", "Deadlift"], "B": ["Squat", "Bench Press", "Power Clean"], "C": ["Squat", "Bench Press", "Power Clean"]},
    }
    
    today_lifts = lifts[phase].get(workout_type, [])
    
    # Build full warmup schedule with plates
    workout_data = []
    # BULLETPROOF WEIGHT MAP — HANDLES EVERY POSSIBLE SPELLING
    weight_map = {
        "Squat": weights.squat or 45,
        "BenchPress": weights.bench or 45,
        "Bench Press": weights.bench or 45,
        "Press": weights.press or 45,
        "Deadlift": weights.deadlift or 135,
        "PowerClean": weights.powerclean or 95,
        "Power Clean": weights.powerclean or 95,     # <-- THIS WAS MISSING
    }

    for lift in today_lifts:
        # Try exact match first, then normalized
        key = lift.replace(" ", "")  # "Power Clean" → "PowerClean"
        working_weight = weight_map.get(lift) or weight_map.get(key) or 45
        if working_weight <= 0:
            working_weight = 45  # never allow 0
        sets = calculate_warmups(working_weight, lift, current_user.id)
        print(f"DEBUG → Lift: '{lift}' → Key tried: '{key}' → Weight: {working_weight}")
        workout_data.append({
            "name": lift,
            "working_weight": working_weight,
            "warmups": sets
        })
    
    return render_template(
        'dashboard.html',
        phase=phase,
        workout_type=workout_type,
        lifts=workout_data,
        today=today.strftime("%A, %B %d")
    )


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data.lower()
        user = User(username=username)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        # Auto-create starting weights for new user
        weights = StartingWeights(
            user_id=user.id,
            squat=45, bench=45, press=45, deadlift=135, powerclean=95
        )
        db.session.add(weights)
        db.session.commit()

        flash('ACCOUNT CREATED — WELCOME TO THE GYM, BROTHER!', 'success')
        return redirect(url_for('routes.login'))
    
    return render_template('register.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            flash('LOGGED IN — TIME TO LIFT!', 'success')
            return redirect(url_for('routes.dashboard'))
        else: 
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    flash('Logged out — rest up, champ!', 'info')
    return redirect(url_for('routes.index'))

@bp.route('/history')
@login_required
def history():
    workouts = WorkoutLog.query.filter_by(user_id=current_user.id)\
        .order_by(WorkoutLog.date.desc())\
        .limit(50).all()  # Last 50 sessions — plenty for now
    return render_template('history.html', workouts=workouts)

@bp.route('/settings')
@login_required
def settings():
    # Get user's current plates (as list of floats)
    user_plates = [p.weight for p in current_user.plates]
    return render_template(
        'settings.html',
        current_phase=current_user.current_phase,
        user_plates=user_plates
    )

@bp.route('/save-settings', methods=['POST'])
@login_required
def save_settings():
    # Update phase
    phase = int(request.form.get('phase', 1))
    if phase not in [1, 2, 3]:
        phase = 1
    current_user.current_phase = phase

    # Update plates — delete old, insert new
    Plate.query.filter_by(user_id=current_user.id).delete()

    plate_values = request.form.getlist('plates')  # list of strings
    for weight_str in plate_values:
        try:
            weight = float(weight_str)
            plate = Plate(user_id=current_user.id, weight=weight, pair_count=1)
            db.session.add(plate)
        except ValueError:
            pass  # skip garbage

    db.session.commit()
    flash("Settings locked in — your gym, your rules!", "success")
    return redirect(url_for('routes.dashboard'))

@bp.route('/rest-day')
@login_required
def rest_day():
    today = date.today()
    
    # Check if user already logged today (workout or rest)
    # existing = WorkoutLog.query.filter_by(user_id=current_user.id, date=today).first()
    # if existing:
    #     flash("You already logged today — no double-dipping, brother!", "warning")
    #     return redirect(url_for('routes.dashboard'))

    # Log the rest day
    rest_log = WorkoutLog(
        user_id=current_user.id,
        date=today,
        phase=current_user.current_phase,
        workout_type="R",
        is_rest_day=True
    )
    db.session.add(rest_log)
    db.session.commit()

    flash("REST DAY LOGGED — RECOVERY IS KING, BROTHER!", "success")
    return redirect(url_for('routes.dashboard'))

@bp.route('/complete-workout', methods=['POST'])
@login_required
def complete_workout():
    data = request.get_json()
    lift_details = data.get('lift_details', {})  # { "Squat": {completed_sets: 3, required_sets: 3, actual_weights: [225, 225, 225]} }
    workout_type = data.get('workout_type')

    workout = WorkoutLog(
        user_id=current_user.id,
        date=date.today(),
        phase=current_user.current_phase,
        workout_type=workout_type,
        is_rest_day=False
    )
    db.session.add(workout)
    db.session.flush()

    weights = StartingWeights.query.filter_by(user_id=current_user.id).first()
    if not weights:
        return jsonify(success=False, message="No weights found")

    field_map = {
        "Squat": "squat",
        "Bench Press": "bench",
        "BenchPress": "bench",
        "Press": "press",
        "Deadlift": "deadlift",
        "Power Clean": "powerclean",
        "Powerclean": "powerclean",
        "PowerClean": "powerclean"
    }

    for lift_name, details in lift_details.items():
        completed = details['completed_sets']
        required = details['required_sets']
        actual_weights = details.get('actual_weights', [])
        failed = completed < required

        # Use last actual_weight (or working weight if none entered)
        actual_weight = actual_weights[-1] if actual_weights else getattr(weights, field_map[lift_name.replace(" ", "")])

        # Save full truth
        entry = LiftEntry(
            workout_id=workout.id,
            exercise=lift_name,
            working_weight=getattr(weights, field_map[lift_name.replace(" ", "")]),
            actual_weight=actual_weight,
            work_sets_completed=completed,
            work_sets_required=required,
            failed=failed
        )
        db.session.add(entry)

        # PROGRESSION: NEXT WORKOUT USES actual_weight
        field = field_map.get(lift_name) or field_map.get(lift_name.replace(" ", ""))
        if field:
            # Only progress if you completed all sets
            if not failed:
                setattr(weights, field, actual_weight + 5)
            else:
                # Failed → next time you try the SAME actual_weight
                setattr(weights, field, actual_weight)
        else:
            continue

    db.session.commit()
    return jsonify(success=True, message="WORKOUT LOGGED — NEXT SESSION USES WHAT YOU ACTUALLY LIFTED")

@bp.route('/update-working-weights', methods=['POST'])
@login_required
def update_working_weights():
    data = request.get_json()

    if not data:
        return jsonify(success=False, message="No data received")

    # RE-LOAD the weights object fresh from DB to avoid stale data
    weights = StartingWeights.query.filter_by(user_id=current_user.id).first()
    if not weights:
        return jsonify(success=False, message="No starting weights found")

    db.session.expire(weights)   # ← THIS IS THE NUCLEAR BUTTON

    # Map lift names to DB fields
    field_map = {
        "Squat": "squat",
        "Bench Press": "bench",
        "Press": "press",
        "Deadlift": "deadlift",
        "Power Clean": "powerclean",
        "PowerClean": "powerclean"
    }

    updated = False
    for lift_name, new_weight in data.items():
        field = field_map.get(lift_name.replace(" ", ""))
        if field and hasattr(weights, field):
            old_val = getattr(weights, field)
            new_val = float(new_weight)
            if old_val != new_val:
                setattr(weights, field, new_val)
                updated = True

    if updated:
        db.session.commit()
        return jsonify(success=True, message="Weights updated — warmups recalculated!")
    else:
        return jsonify(success=True, message="No changes detected")