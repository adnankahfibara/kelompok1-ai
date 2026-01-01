import joblib
import numpy as np
from flask import Flask, render_template, request

app = Flask(__name__)

# Load model ML (misalnya RandomForest)
model = joblib.load("rf_model_joblib.pkl")

def proses_diagnosa(tegangan, suhu, kipas, battery, power, beep):
    # --- 1. Preprocessing input ---
    # Ubah input ke format numerik sesuai training model
    # Contoh sederhana (sesuaikan dengan dataset kamu)
    fan_val = 1 if kipas == "Normal" else 0
    battery_map = {"Good":3, "Normal":2, "Poor":1, "Bad":0}
    power_map = {"Stable":2, "Unstable":1, "Failed":0}
    beep_map = {"None":0, "Short":1, "Long":2, "Continuous":3}

    X = np.array([[tegangan, suhu, fan_val,
                   battery_map.get(battery,0),
                   power_map.get(power,0),
                   beep_map.get(beep,0)]])

    # --- 2. Prediksi ML ---
    pred = model.predict(X)[0]
    prob = model.predict_proba(X).max()

    # --- 3. Certainty Factor (contoh sederhana) ---
    cf = {
        "tegangan": tegangan/100,   # misalnya normalisasi
        "suhu": suhu/100,
        "kipas": fan_val
    }

    # --- 4. Hybrid skor akhir ---
    final = {
        "ML": prob,
        "CF": sum(cf.values())/len(cf)
    }

    # --- 5. Kesimpulan diagnosa ---
    diagnosis = "Kerusakan Motherboard" if pred == 1 else "Laptop Normal"

    return {
        "pred": pred,
        "prob": f"{prob:.2f}",
        "cf": cf,
        "final": final,
        "diagnosis": diagnosis
    }

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        tegangan = float(request.form.get("tegangan", 0))
        suhu = float(request.form.get("suhu", 0))
        kipas = request.form.get("kipas", "")
        battery = request.form.get("battery", "")
        power = request.form.get("power", "")
        beep = request.form.get("beep", "")

        hasil = proses_diagnosa(tegangan, suhu, kipas, battery, power, beep)
        return render_template("index.html", hasil=hasil)

    return render_template("index.html")
