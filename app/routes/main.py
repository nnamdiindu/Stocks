from flask import render_template, Blueprint
from datetime import datetime
from flask_login import current_user

# Create blueprint
main_bp = Blueprint('main', __name__)

@main_bp.context_processor
def inject_now():
    return {"now": datetime.now().strftime("%Y")}

@main_bp.route("/")
def index():
    return render_template("landing/index.html")

@main_bp.route("/about-us")
def about_us():
    return render_template("landing/about-us.html")

@main_bp.route("/features")
def features():
    return render_template("landing/features.html")

@main_bp.route("/contact-us")
def contact_us():
    return render_template("landing/contact-us.html")

@main_bp.route("/dashboard")
def dashboard():
    return render_template("dashboard/dashboard.html", current_user=current_user)

@main_bp.route("/dashboard/portfolio")
def portfolio():
    return render_template("dashboard/portfolio.html")

@main_bp.route("/dashboard/invest")
def invest():
    return render_template("dashboard/invest.html")

@main_bp.route("/dashboard/settings")
def settings():
    return render_template("dashboard/settings.html")

@main_bp.route("/dashboard/wallet")
def wallet():
    return render_template("dashboard/wallet.html")

@main_bp.route("/dashboard/insights")
def insights():
    return render_template("dashboard/insights.html")

@main_bp.route("/dashboard/notifications")
def notifications():
    return render_template("dashboard/notifications.html")

@main_bp.route("/dashboard/support")
def support():
    return render_template("dashboard/support.html")

@main_bp.route("/dashboard/referrals")
def referrals():
    return render_template("dashboard/referrals.html")