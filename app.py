import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# Podešavanje stranice
# =========================
st.set_page_config(
    page_title="Hemoliza i insulinska rezistencija",
    layout="centered"
)

st.title("Uticaj hemolize na indekse insulinske rezistencije")

st.markdown("""
Aplikacija računa **indekse insulinske rezistencije**
pre i posle korekcije hemolize i prikazuje njihov **bias (%) u funkciji Hb**.
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
# Sidebar – unos
# =========================
st.sidebar.header("Unos izmerenih vrednosti")

GLU_m = st.sidebar.number_input("GLU (mmol/L)", 2.0, 15.0, 5.0)
INS_m = st.sidebar.number_input("INS (µIU/mL)", 1.0, 100.0, 10.0)
NEFA_m = st.sidebar.number_input("NEFA (mmol/L)", 0.1, 3.0, 0.6)
BHB_m = st.sidebar.number_input("BHB (mmol/L)", 0.05, 5.0, 0.4)

Hb_input = st.sidebar.slider("Hb (g/L) – hemoliza uzorka", 0.0, 10.0, 1.0, 0.1)

# =========================
# Funkcije
# =========================
def correct_value(value, param, hb):
    bias = regression[param]["a"] * hb + regression[param]["b"]
    return value / (1 + bias / 100)

def indices(vals):
    HOMA = (vals["INS"] * vals["GLU"]) / 22.5
    QUICKI = 1 / (np.log(vals["INS"]) + np.log(vals["GLU"]))
    RQUICKI = 1 / (np.log(vals["INS"]) +
                   np.log(vals["GLU"]) +
                   np.log(vals["NEFA"]))
    RQUICKI_BHB = 1 / (np.log(vals["INS"]) +
                       np.log(vals["GLU"]) +
                       np.log(vals["NEFA"]) +
                       np.log(vals["BHB"]))
    return HOMA, QUICKI, RQUICKI, RQUICKI_BHB

# =========================
# Izračun – jedna Hb vrednost
# =========================
measured = {
    "GLU": GLU_m,
    "INS": INS_m,
    "NEFA": NEFA_m,
    "BHB": BHB_m
}

corrected = {
    p: correct_value(v, p, Hb_input)
    for p, v in measured.items()
}

idx_meas = indices(measured)
idx_corr = indices(corrected)

st.subheader("Indeksi insulinske rezistencije (Hb = {:.1f} g/L)".format(Hb_input))

df_idx = pd.DataFrame({
    "Indeks": ["HOMA-IR", "QUICKI", "RQUICKI", "RQUICKI-BHB"],
    "Izmerena vrednost": idx_meas,
    "Korigovana vrednost": idx_corr
})

st.dataframe(df_idx, use_container_width=True)

# =========================
# Bias indeksa vs Hb
# =========================
Hb_range = np.linspace(0, 10, 100)
bias_results = []

for hb in Hb_range:
    corr_vals = {p: correct_value(v, p, hb) for p, v in measured.items()}
    idx_c = indices(corr_vals)
    idx_m = idx_meas

    bias_results.append([
        hb,
        100 * (idx_c[0] - idx_m[0]) / idx_m[0],
        100 * (idx_c[1] - idx_m[1]) / idx_m[1],
        100 * (idx_c[2] - idx_m[2]) / idx_m[2],
        100 * (idx_c[3] - idx_m[3]) / idx_m[3]
    ])

df_bias = pd.DataFrame(
    bias_results,
    columns=["Hb", "HOMA bias", "QUICKI bias", "RQUICKI bias", "RQUICKI-BHB bias"]
)

# =========================
# Grafikon 1 – bias indeksa
# =========================
st.subheader("Bias (%) indeksa insulinske rezistencije u funkciji Hb")

fig1, ax1 = plt.subplots(figsize=(8,5))
ax1.plot(df_bias["Hb"], df_bias["HOMA bias"], label="HOMA-IR")
ax1.plot(df_bias["Hb"], df_bias["QUICKI bias"], label="QUICKI")
ax1.plot(df_bias["Hb"], df_bias["RQUICKI bias"], label="RQUICKI")
ax1.plot(df_bias["Hb"], df_bias["RQUICKI-BHB bias"], label="RQUICKI-BHB")

ax1.axvline(Hb_input, color="red", linestyle="--", label="Hb uzorka")
ax1.set_xlabel("Hb (g/L)")
ax1.set_ylabel("Bias (%)")
ax1.legend()
ax1.grid(True)

st.pyplot(fig1)

# =========================
# Grafikon 2 – RQUICKI posle korekcije
# =========================
rquicki_corr = []

for hb in Hb_range:
    vals = {p: correct_value(v, p, hb) for p, v in measured.items()}
    rquicki_corr.append(indices(vals)[2])

st.subheader("RQUICKI nakon korekcije hemolize")

fig2, ax2 = plt.subplots(figsize=(8,5))
ax2.plot(Hb_range, rquicki_corr, color="green")
ax2.axvline(Hb_input, color="red", linestyle="--", label="Hb uzorka")
ax2.set_xlabel("Hb (g/L)")
ax2.set_ylabel("RQUICKI (korigovana vrednost)")
ax2.legend()
ax2.grid(True)

st.pyplot(fig2)
