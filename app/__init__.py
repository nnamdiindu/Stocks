import os
from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv
from app.database import db, init_db

load_dotenv()

# Initialize Flask-Login
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    # Secret key for sessions
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

    # Database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URI")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Session configuration
    app.config["SESSION_COOKIE_SECURE"] = False  # Set True in production with HTTPS
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["PERMANENT_SESSION_LIFETIME"] = 86400  # 24 hours

    # Initialize database
    db.init_app(app)

    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"  # Redirect to /login/ if not authenticated
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        # Load user by ID for Flask-Login
        from app.models.user import User
        from sqlalchemy import select
        return db.session.execute(
            select(User).where(User.id == int(user_id))
        ).scalar_one_or_none()

    # REGISTER BLUEPRINTS
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    # CREATE DATABASE TABLES
    with app.app_context():
        init_db()

    # ERROR HANDLERS
    @app.errorhandler(404)
    def not_found(error):
        from flask import render_template
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()
        return render_template("errors/500.html"), 500

    return app

app = create_app()