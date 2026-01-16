import pytest
from app import create_app, db
from app.models import User, WorkoutLog, StartingWeights, Plate
from datetime import date
from flask_login import login_user

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False
    })

    with app.app_context():
        db.create_all()
        # Create a test user
        user = User(username="testuser")
        user.set_password("password")
        db.session.add(user)
        db.session.flush() # get user.id
        weights = StartingWeights(user_id=user.id)
        db.session.add(weights)
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client, app):
    client.post('/login', data={'username': 'testuser', 'password': 'password'}, follow_redirects=True)
    return client

def test_duplicate_rest_day_prevention(auth_client, app):
    # Log first rest day
    response = auth_client.get('/rest-day', follow_redirects=True)
    assert response.status_code == 200
    assert b"REST DAY LOGGED" in response.data

    # Attempt to log second rest day on same date
    response = auth_client.get('/rest-day', follow_redirects=True)
    assert response.status_code == 200
    # Before fix, this will succeed. After fix, it should show warning.
    assert b"already logged today" in response.data

def test_duplicate_workout_prevention(auth_client, app):
    # Log rest day first
    auth_client.get('/rest-day', follow_redirects=True)

    # Attempt to complete a workout
    payload = {
        "workout_type": "A",
        "lift_details": {
            "Squat": {"completed_sets": 3, "required_sets": 3, "actual_weights": [225, 225, 225]}
        }
    }
    response = auth_client.post('/complete-workout', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is False
    assert "already logged today" in data['message']

def test_dashboard_loads(auth_client):
    response = auth_client.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert b"WFM LIFTS" in response.data
