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


if __name__ == "__main__":
    app.run(debug=True)