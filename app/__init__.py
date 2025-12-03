# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from dotenv import load_dotenv
import os
from datetime import timedelta

# Load .env (for Render + local)
load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'routes.login'
login_manager.login_message = 'Log in to access this page, brother.'
login_manager.login_message_category = 'info'

# THIS IS THE KEY LINE — MAKES SESSION PERMANENT
login_manager.session_protection = "strong"
login_manager.remember = True   # ← optional, but makes it explicit

def create_app():
    app = Flask(__name__)
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=365)  # 1 year
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365)
    # === CONFIG — Works locally AND on Render ===
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'macho-man-secret-yeah'
    app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL') or 
    'postgresql://postgres:password@localhost/lifts'
    ).replace("postgres://", "postgresql://", 1)  # Render fix
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Register blueprints
    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    # User loader for Flask-Login
    from .models import User
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app