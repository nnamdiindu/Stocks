from flask import Flask, render_template, url_for
from datetime import datetime

app = Flask(__name__)


@app.context_processor
def inject_now():
    return {'now': datetime.now().strftime("%Y")}


@app.route("/")
def index():
    return render_template("landing/index.html")

@app.route("/about-us")
def about_us():
    return render_template("landing/about-us.html")

@app.route("/features")
def features():
    return render_template("landing/features.html")

@app.route("/contact-us")
def contact_us():
    return render_template("landing/contact-us.html")

@app.route("/sign-in")
def sign_in():
    return render_template("auth/sign-in.html")

@app.route("/sign-up")
def sign_up():
    return render_template("auth/sign-up.html")

@app.route("/forget-password")
def forget_password():
    return render_template("auth/forget-password.html")

@app.route("/new-password")
def create_new_password():
    return render_template("auth/create-new-password.html")

@app.route("/verify-otp")
def verify_otp():
    return render_template("auth/enter-otp.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard/dashboard.html")

@app.route("/dashboard/portfolio")
def portfolio():
    return render_template("dashboard/portfolio.html")

@app.route("/dashboard/invest")
def invest():
    return render_template("dashboard/invest.html")

@app.route("/dashboard/settings")
def settings():
    return render_template("dashboard/settings.html")

@app.route("/dashboard/wallet")
def wallet():
    return render_template("dashboard/wallet.html")

@app.route("/dashboard/insights")
def insights():
    return render_template("dashboard/insights.html")

@app.route("/dashboard/notifications")
def notifications():
    return render_template("dashboard/notifications.html")

@app.route("/dashboard/support")
def support():
    return render_template("dashboard/support.html")

@app.route("/dashboard/referrals")
def referrals():
    return render_template("dashboard/referrals.html")

if __name__ == "__main__":
    app.run(debug=True)