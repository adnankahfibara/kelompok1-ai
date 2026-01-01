from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # proses input form dan hasil diagnosa
        return render_template("index.html", hasil=hasil)
    return render_template("index.html")
