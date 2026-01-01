from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # Ambil data dari form
        tegangan = float(request.form.get("tegangan", 0))
        suhu = float(request.form.get("suhu", 0))
        kipas = request.form.get("kipas", "")
        battery = request.form.get("battery", "")
        power = request.form.get("power", "")
        beep = request.form.get("beep", "")

        # Contoh logika diagnosa (ganti dengan model ML + certainty factor kamu)
        hasil = f"Tegangan: {tegangan}V, Suhu: {suhu}°C, Kipas: {kipas}, Battery: {battery}, Power: {power}, Beep: {beep}"

        return render_template("index.html", hasil=hasil)

    return render_template("index.html")

# Jangan pakai app.run() di Railway, karena Railway pakai gunicorn
