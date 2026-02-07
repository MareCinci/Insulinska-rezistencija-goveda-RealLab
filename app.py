import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(layout="wide")
st.title("Hemoliza i korekcija indeksa insulinske rezistencije")

# =========================
# Regresione formule (% bias)
# =========================
regression = {
    "GLU":  {"a": -2.9538, "b": -1.401,  "R2": 0.9794},
    "NEFA": {"a":  9.8218, "b":  2.5353, "R2": 0.9972},
    "BHB":  {"a":  5.3201, "b":  0.957,  "R2": 0.9913},
    "INS":  {"a": -5.5017, "b": -3.7803,"R2": 0.9875}
}

# =========================
# Sidebar – unos izmerenih vrednosti
# =========================
st.sidebar.header("Izmerene vrednosti (bez hemolize)")
measured = {
    "GLU": st.sidebar.number_input("GLU (mmol/L)", 1.0, 20.0, 5.0),
    "INS": st.sidebar.number_input("INS (µIU/mL)", 1.0, 50.0, 10.0),
    "NEFA": st.sidebar.number_input("NEFA (mmol/L)", 0.1, 2.0, 0.6),
    "BHB": st.sidebar.number_input("BHB (mmol/L)", 0.1, 5.0, 0.4)
}

# =========================
# Funkcija za izračunavanje indeksa
# =========================
def calculate_indices(values):
    HOMA = (values["INS"] * values["GLU"]) / 22.5
    QUICKI = 1 / (np.log(values["INS"]) + np.log(values["GLU"]))
    RQUICKI = 1 / (np.log(values["INS"]) + np.log(values["GLU"]) + np.log(values["NEFA"]))
    RQBHB = 1 / (np.log(values["INS"]) + np.log(values["GLU"]) + np.log(values["NEFA"]) + np.log(values["BHB"]))
    return {"HOMA-IR": HOMA, "QUICKI": QUICKI, "RQUICKI": RQUICKI, "RQUICKI-BHB": RQBHB}

# =========================
# Prikaz indeksa pri Hb = 0
# =========================
st.subheader("Izračunati indeksi pri Hb = 0 (bez hemolize)")
base_indices = calculate_indices(measured)
st.write(pd.DataFrame(base_indices, index=["Vrednost"]).T)

# =========================
# Odabir Hb
# =========================
st.sidebar.header("Odaberi Hb vrednost za korekciju")
selected_Hb = st.sidebar.slider("Hb (g/L)", 0.0, 10.0, 0.0, 0.1)

# =========================
# Funkcija za korekciju indeksa pri odabranoj Hb
# =========================
def correct_for_Hb(values, Hb_value):
    corr = {}
    for p in values:
        a, b, R2 = regression[p].values()
        bias = a * Hb_value + b
        corr[p] = values[p] / (1 + bias / 100)
    return calculate_indices(corr)

# =========================
# Prikaz korigovanih vrednosti
# =========================
st.subheader(f"Korigovane vrednosti indeksa pri Hb = {selected_Hb:.1f} g/L")
corrected_indices = correct_for_Hb(measured, selected_Hb)
st.write(pd.DataFrame(corrected_indices, index=["Korigovana vrednost"]).T)
