from flask import render_template, Blueprint
from datetime import datetime
from flask_login import current_user, login_required

# Create blueprint
main_bp = Blueprint('main', __name__)

@main_bp.context_processor
def inject_now():
    return {"year": datetime.now().strftime("%Y")}

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
@login_required
def dashboard():
    return render_template("dashboard/dashboard.html", current_user=current_user)

@main_bp.route("/dashboard/portfolio")
@login_required
def portfolio():
    return render_template("dashboard/portfolio.html")

@main_bp.route("/dashboard/invest")
@login_required
def invest():
    return render_template("dashboard/invest.html")

@main_bp.route("/dashboard/settings")
@login_required
def settings():
    return render_template("dashboard/settings.html")

@main_bp.route("/dashboard/wallet")
@login_required
def wallet():
    return render_template("dashboard/wallet.html")

@main_bp.route("/dashboard/insights")
@login_required
def insights():
    return render_template("dashboard/insights.html")

@main_bp.route("/dashboard/notifications")
@login_required
def notifications():
    return render_template("dashboard/notifications.html")

@main_bp.route("/dashboard/support")
@login_required
def support():
    return render_template("dashboard/support.html")

@main_bp.route("/dashboard/referrals")
@login_required
def referrals():
    return render_template("dashboard/referrals.html")