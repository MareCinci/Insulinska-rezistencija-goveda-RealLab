import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Insulin Resistance & Hemolysis", layout="centered")

st.title("Uticaj hemolize na indekse insulinske rezistencije")

st.markdown("""
Ova aplikacija simulira kako **hemoliza (Hb g/L)** utiče na:
- HOMA-IR  
- QUICKI  
- RQUICKI  
- RQUICKI-BHB  

na osnovu regresionih modela (% bias).
""")

# =========================
# Regresioni modeli
# =========================
regression = {
    "GLU":  {"a": -2.9538, "b": -1.401},
    "NEFA": {"a":  9.8218, "b":  2.5353},
    "BHB":  {"a":  5.3201, "b":  0.957},
    "INS":  {"a": -5.5017, "b": -3.7803}
}

# =========================
# User input
# =========================
st.sidebar.header("Unos izmerenih vrednosti")

GLU_m = st.sidebar.slider("GLU (mmol/L)", 2.0, 10.0, 5.0, 0.1)
INS_m = st.sidebar.slider("INS (µIU/mL)", 1.0, 50.0, 10.0, 0.5)
NEFA_m = st.sidebar.slider("NEFA (mmol/L)", 0.1, 2.0, 0.6, 0.05)
BHB_m = st.sidebar.slider("BHB (mmol/L)", 0.05, 3.0, 0.4, 0.05)

Hb = np.linspace(0, 10, 100)

results = []

for hb in Hb:
    corrected = {}
    for p, val in zip(
        ["GLU", "INS", "NEFA", "BHB"],
        [GLU_m, INS_m, NEFA_m, BHB_m]
    ):
        bias = regression[p]["a"] * hb + regression[p]["b"]
        corrected[p] = val / (1 + bias / 100)

    HOMA = (corrected["INS"] * corrected["GLU"]) / 22.5
    QUICKI = 1 / (np.log(corrected["INS"]) + np.log(corrected["GLU"]))
    RQUICKI = 1 / (np.log(corrected["INS"]) +
                   np.log(corrected["GLU"]) +
                   np.log(corrected["NEFA"]))
    RQUICKI_BHB = 1 / (np.log(corrected["INS"]) +
                       np.log(corrected["GLU"]) +
                       np.log(corrected["NEFA"]) +
                       np.log(corrected["BHB"]))

    results.append([hb, HOMA, QUICKI, RQUICKI, RQUICKI_BHB])

df = pd.DataFrame(results, columns=[
    "Hb (g/L)", "HOMA-IR", "QUICKI", "RQUICKI", "RQUICKI-BHB"
])

# =========================
# Grafički prikaz
# =========================
st.subheader("Promena indeksa u funkciji hemolize")

fig, ax = plt.subplots(figsize=(8,5))
ax.plot(df["Hb (g/L)"], df["HOMA-IR"], label="HOMA-IR")
ax.plot(df["Hb (g/L)"], df["QUICKI"], label="QUICKI")
ax.plot(df["Hb (g/L)"], df["RQUICKI"], label="RQUICKI")
ax.plot(df["Hb (g/L)"], df["RQUICKI-BHB"], label="RQUICKI-BHB")

ax.set_xlabel("Hemoliza (Hb g/L)")
ax.set_ylabel("Indeks")
ax.legend()
ax.grid(True)

st.pyplot(fig)
