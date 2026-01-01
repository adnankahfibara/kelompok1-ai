from flask import Flask, render_template, request
import joblib
import numpy as np

app = Flask(__name__)

# Load model ML dengan aman
try:
    model = joblib.load("rf_model_joblib.pkl")
except Exception as e:
    print("Model gagal dimuat:", e)
    model = None

# Certainty Factor rules
def hitung_cf(tegangan, suhu, kipas, battery, power, beep):
    cf = {}

    if tegangan < 19:
        cf["Tegangan Rendah"] = 0.8
    else:
        cf["Tegangan Normal"] = 0.2

    if suhu > 70:
        cf["Suhu Tinggi"] = 0.9
    else:
        cf["Suhu Normal"] = 0.2

    cf["Kipas"] = 0.7 if kipas == "Mati" else 0.2

    battery_cf_map = {"Good": 0.1, "Normal": 0.3, "Poor": 0.6, "Bad": 0.8}
    cf["Battery"] = battery_cf_map.get(battery, 0.0)

    power_cf_map = {"Stable": 0.1, "Unstable": 0.8, "Failed": 0.9}
    cf["Power Rail"] = power_cf_map.get(power, 0.0)

    beep_cf_map = {"None": 0.1, "Short": 0.5, "Long": 0.9, "Continuous": 0.9}
    cf["Beep"] = beep_cf_map.get(beep, 0.0)

    return cf

# Proses diagnosa hybrid
def proses_diagnosa(tegangan, suhu, kipas, battery, power, beep):
    fan_val = 1 if kipas == "Normal" else 0
    battery_map = {"Good": 3, "Normal": 2, "Poor": 1, "Bad": 0}
    power_map = {"Stable": 2, "Unstable": 1, "Failed": 0}
    beep_map = {"None": 0, "Short": 1, "Long": 2, "Continuous": 3}

    # Fitur ke-7 (dummy sementara)
    extra_feature = 1

    # Pastikan input ke model punya 7 fitur
    X = np.array([[tegangan,
                   suhu,
                   fan_val,
                   battery_map.get(battery, 0),
                   power_map.get(power, 0),
                   beep_map.get(beep, 0),
                   extra_feature]])

    # Prediksi ML (fallback kalau model error)
    if model:
        try:
            pred = model.predict(X)[0]
            prob = model.predict_proba(X)[0][pred]
        except Exception as e:
            print("Error prediksi:", e)
            pred = 0
            prob = 0.0
    else:
        pred = 0
        prob = 0.0

    # Certainty Factor
    cf = hitung_cf(tegangan, suhu, kipas, battery, power, beep)
    cf_score = sum(cf.values()) / len(cf)
    final_score = (prob + cf_score) / 2

    diagnosis = "Kerusakan Motherboard" if final_score > 0.6 else "Laptop Normal"

    return {
        "pred": "Kerusakan Motherboard" if pred == 1 else "Laptop Normal",
        "prob": f"{prob:.2f}",
        "cf": cf,
        "final": {"Hybrid": final_score},
        "diagnosis": diagnosis
    }

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        try:
            tegangan = float(request.form.get("tegangan", 0))
            suhu = float(request.form.get("suhu", 0))
            kipas = request.form.get("kipas", "")
            battery = request.form.get("battery", "")
            power = request.form.get("power", "")
            beep = request.form.get("beep", "")

            hasil = proses_diagnosa(tegangan, suhu, kipas, battery, power, beep)
            return render_template("index.html", hasil=hasil)
        except Exception as e:
            print("Error input:", e)
            return render_template("index.html", hasil=None)

    return render_template("index.html")
