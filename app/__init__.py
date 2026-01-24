import os
from flask import Flask, flash
from flask_login import LoginManager
from dotenv import load_dotenv
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.database import db, init_db
from app.utils.stocks_api import format_number

load_dotenv()

# Initialize Flask-Login
login_manager = LoginManager()

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

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
    migrate = Migrate(app, db)
    limiter.init_app(app)

    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"  # Redirect to /login/ if not authenticated
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    app.limiter = limiter

    # Register it as a Jinja filter
    app.jinja_env.filters['compact'] = format_number

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
    from app.routes.dashboard import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(dashboard_bp)

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
        # return render_template("errors/500.html"), 500
        # Return actual 500 error page here
        return "<h1>500 Error</h1>"

    @app.errorhandler(429)
    def ratelimit_handler(e):
        flash("Too many requests. Please try again later.", "error")
        # return render_template("errors/429.html"), 429
        # Return actual 429 error page here
        return "<h1>429 Error</h1>"


    return app

app = create_app()