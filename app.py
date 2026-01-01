from flask import Flask, render_template, url_for
from datetime import datetime

app = Flask(__name__)


@app.context_processor
def inject_now():
    return {'now': datetime.now().strftime("%Y")}


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about-us")
def about_us():
    return render_template("about-us.html")

@app.route("/features")
def features():
    return render_template("features.html")

@app.route("/contact-us")
def contact_us():
    return render_template("contact-us.html")

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

if __name__ == "__main__":
    app.run(debug=True)