import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# Podešavanje stranice
# =========================
st.set_page_config(
    page_title="Insulinska rezistencija i hemoliza",
    layout="centered"
)

st.title("Uticaj hemolize na indekse insulinske rezistencije")

st.markdown("""
Ova aplikacija prikazuje kako **hemoliza (Hb g/L)** utiče na:
- **HOMA-IR**
- **QUICKI**
- **RQUICKI**
- **RQUICKI-BHB**

na osnovu regresionih modela (% bias).
""")

# =========================
# Regresioni modeli (% bias = a*Hb + b)
# =========================
regression = {
    "GLU":  {"a": -2.9538, "b": -1.401},
    "NEFA": {"a":  9.8218, "b":  2.5353},
    "BHB":  {"a":  5.3201, "b":  0.957},
    "INS":  {"a": -5.5017, "b": -3.7803}
}

# =========================
# Sidebar – unos vrednosti
# =========================
st.sidebar.header("Unos izmerenih vrednosti")

GLU_m = st.sidebar.slider("GLU (mmol/L)", 2.0, 10.0, 5.0, 0.1)
INS_m = st.sidebar.slider("INS (µIU/mL)", 1.0, 50.0, 10.0, 0.5)
NEFA_m = st.sidebar.slider("NEFA (mmol/L)", 0.1, 2.0, 0.6, 0.05)
BHB_m = st.sidebar.slider("BHB (mmol/L)", 0.05, 3.0, 0.4, 0.05)

# =========================
# Hb – raspon hemolize
# =========================
Hb = np.linspace(0, 10, 100)

results = []

for hb in Hb:
    corrected = {}

    for param, value in {
        "GLU": GLU_m,
        "INS": INS_m,
        "NEFA": NEFA_m,
        "BHB": BHB_m
    }.items():
        bias = regression[param]["a"] * hb + regression[param]["b"]
        corrected[param] = value / (1 + bias / 100)

    HOMA = (corrected["INS"] * corrected["GLU"]) / 22.5
    QUICKI = 1 / (np.log(corrected["INS"]) + np.log(corrected["GLU"]))
    RQUICKI = 1 / (
        np.log(corrected["INS"]) +
        np.log(corrected["GLU"]) +
        np.log(corrected["NEFA"])
    )
    RQUICKI_BHB = 1 / (
        np.log(corrected["INS"]) +
        np.log(corrected["GLU"]) +
        np.log(corrected["NEFA"]) +
        np.log(corrected["BHB"])
    )

    results.append([
        hb,
        HOMA,
        QUICKI,
        RQUICKI,
        RQUICKI_BHB
    ])

# =========================
# DataFrame
# =========================
df = pd.DataFrame(
    results,
    columns=[
        "Hb (g/L)",
        "HOMA-IR",
        "QUICKI",
        "RQUICKI",
        "RQUICKI-BHB"
    ]
)

# =========================
# Grafički prikaz
# =========================
st.subheader("Promena indeksa insulinske rezistencije u funkciji hemolize")

fig, ax = plt.subplots(figsize=(8, 5))

ax.plot(df["Hb (g/L)"], df["HOMA-IR"], label="HOMA-IR")
ax.plot(df["Hb (g/L)"], df["QUICKI"], label="QUICKI")
ax.plot(df["Hb (g/L)"], df["RQUICKI"], label="RQUICKI")
ax.plot(df["Hb (g/L)"], df["RQUICKI-BHB"], label="RQUICKI-BHB")

ax.set_xlabel("Hemoliza (Hb g/L)")
ax.set_ylabel("Indeks")
ax.legend()
ax.grid(True)

st.pyplot(fig)
