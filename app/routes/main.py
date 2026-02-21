from flask import render_template, Blueprint, request, flash, redirect, url_for
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

@main_bp.route("/contact-us", methods=["GET", "POST"])
def contact_us():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        phone_number = request.form.get("tel")
        email = request.form.get("email")
        message = request.form.get("message")
        flash("Your message has been sent successfully.", "success")

        print(first_name, phone_number, email, message)
        return redirect(url_for("main.contact_us"))
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