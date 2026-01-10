from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import select
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import db
from app.models.user import User

# Create blueprint
auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # If user is already logged in, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        remember = request.form.get("remember", False)  # "Remember me" checkbox

        # Validate input
        if not email or not password:
            flash("Please provide email and password.", "error")
            return render_template("auth/login.html")

        # Find user
        stmt = select(User).where(User.email == email)
        user = db.session.execute(stmt).scalar_one_or_none()

        # Check user exists and password is correct
        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid email or password.", "error")
            return render_template("auth/login.html")

        # Check if account is active
        if not user.is_active:
            flash("Your account is inactive. Please contact support.", "error")
            return render_template("auth/login.html")

        # Log user in
        login_user(user, remember=remember)

        flash(f"Welcome back, {user.first_name}!", "success")

        # Redirect to next page or dashboard
        next_page = request.args.get("next")
        if next_page:
            return redirect(next_page)
        return redirect(url_for("main.dashboard"))

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == "POST":
        # Get form data
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        dob_string = request.form.get("dob")
        phone_number = request.form.get("phone_number")

        # Convert string to date object
        date_of_birth = datetime.strptime(dob_string, "%Y-%m-%d").date()

        # Validate input
        errors = []

        if not email:
            errors.append("Email is required.")
        if not username or len(username) < 3:
            errors.append("Username must be at least 3 characters.")
        if not password or len(password) < 8:
            errors.append("Password must be at least 8 characters.")
        if password != confirm_password:
            errors.append("Passwords do not match.")
        if not first_name:
            errors.append("First name is required.")
        if not last_name:
            errors.append("Last name is required.")

        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("auth/register.html")

        # Check if email already exists
        stmt = select(User).where(User.email == email)
        if db.session.execute(stmt).scalar_one_or_none():
            flash("Email already registered. Please sign in.", "error")
            return render_template("auth/login.html")

        # Check if username already exists
        stmt = select(User).where(User.username == username)
        if db.session.execute(stmt).scalar_one_or_none():
            flash("Username already taken.", "error")
            return render_template("auth/register.html")

        # Create new user
        new_user = User(
            email=email,
            username=username,
            password_hash=generate_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            date_of_birth=date_of_birth,
        )

        try:
            db.session.add(new_user)
            db.session.commit()

            # Log user in automatically after registration
            login_user(new_user)

            flash("Registration successful! Welcome!", "success")
            return redirect(url_for('main.dashboard'))

        except Exception as e:
            db.session.rollback()
            flash("An error occurred. Please try again.", "error")
            print(f'{e}')
            return render_template("auth/register.html")

    return render_template("auth/register.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/forget-password")
def forget_password():
    return render_template("auth/forget-password.html")

@auth_bp.route("/new-password")
def create_new_password():
    return render_template("auth/create-new-password.html")

@auth_bp.route("/verify-otp")
def verify_otp():
    return render_template("auth/enter-otp.html")



# ============================================
# Flask-Login provides:
# - login_user(user) → Log user in
# - logout_user() → Log user out
# - current_user → Access current logged-in user
# - login_required → Decorator to protect routes
# ============================================