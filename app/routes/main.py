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