import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# Regresioni parametri (% bias = a*Hb + b)
# =========================
regression = {
    "GLU":  {"a": -2.9538, "b": -1.401},
    "NEFA": {"a":  9.8218, "b":  2.5353},
    "BHB":  {"a":  5.3201, "b":  0.957},
    "INS":  {"a": -5.5017, "b": -3.7803}
}

# =========================
# Početne IZMERENE vrednosti (bez hemolize)
# =========================
measured = {
    "GLU": 5.0,     # mmol/L
    "INS": 10.0,    # µIU/mL
    "NEFA": 0.6,    # mmol/L
    "BHB": 0.4      # mmol/L
}

# =========================
# Hb raspon hemolize
# =========================
Hb = np.linspace(0, 10, 100)

results = []

for hb in Hb:
    corrected = {}

    for param in measured:
        bias = regression[param]["a"] * hb + regression[param]["b"]
        corrected[param] = measured[param] / (1 + bias / 100)

    # Indeksi insulinske rezistencije
    HOMA = (corrected["INS"] * corrected["GLU"]) / 22.5
    QUICKI = 1 / (np.log(corrected["INS"]) + np.log(corrected["GLU"]))
    RQUICKI = 1 / (np.log(corrected["INS"]) +
                   np.log(corrected["GLU"]) +
                   np.log(corrected["NEFA"]))
    RQUICKI_BHB = 1 / (np.log(corrected["INS"]) +
                       np.log(corrected["GLU"]) +
                       np.log(corrected["NEFA"]) +
                       np.log(corrected["BHB"]))

    results.append([
        hb,
        corrected["GLU"],
        corrected["INS"],
        corrected["NEFA"],
        corrected["BHB"],
        HOMA,
        QUICKI,
        RQUICKI,
        RQUICKI_BHB
    ])

# =========================
# DataFrame
# =========================
df = pd.DataFrame(results, columns=[
    "Hb (g/L)",
    "GLU realna",
    "INS realna",
    "NEFA realna",
    "BHB realna",
    "HOMA-IR",
    "QUICKI",
    "RQUICKI",
    "RQUICKI-BHB"
])

# =========================
# Grafički prikaz
# =========================
plt.figure(figsize=(10,6))
plt.plot(df["Hb (g/L)"], df["HOMA-IR"], label="HOMA-IR")
plt.plot(df["Hb (g/L)"], df["QUICKI"], label="QUICKI")
plt.plot(df["Hb (g/L)"], df["RQUICKI"], label="RQUICKI")
plt.plot(df["Hb (g/L)"], df["RQUICKI-BHB"], label="RQUICKI-BHB")
plt.xlabel("Hemoliza (Hb g/L)")
plt.ylabel("Indeks insulinske rezistencije")
plt.title("Uticaj hemolize na indekse insulinske rezistencije")
plt.legend()
plt.grid(True)
plt.show()
