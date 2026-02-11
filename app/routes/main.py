from flask import render_template, Blueprint
from datetime import datetime

# Create blueprint
main_bp = Blueprint("main", __name__)

@main_bp.context_processor
def inject_now():
    return {
        "year": datetime.now().strftime("%Y"),
        "month": datetime.now().strftime("%B")
    }

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

@main_bp.route("/terms&conditions")
def terms():
    return render_template("landing/terms.html")

@main_bp.route("/privacy")
def privacy():
    return render_template("landing/privacy.html")

@main_bp.route("/cookie")
def cookie():
    return render_template("landing/cookie.html")

@main_bp.route("/legal")
def legal():
    return render_template("landing/legal.html")