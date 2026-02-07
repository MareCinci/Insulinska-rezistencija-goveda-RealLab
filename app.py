import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("Hemoliza i indeksi insulinske rezistencije (95% CI + prag nestabilnosti)")

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
tolerance = st.sidebar.slider("Prag nestabilnosti indeksa (%)", 1, 20, 5) / 100

# =========================
# Odabir Hb za korekciju
# =========================
st.sidebar.header("Korekcija indeksa za odabrani Hb")
selected_Hb = st.sidebar.slider("Odaberi Hb (g/L)", 0.0, 10.0, 0.0, 0.1)

# =========================
# Hemoliza Hb 0–10 g/L za grafike
# =========================
Hb = np.linspace(0, 10, 100)

# Liste za rezultate indeksa
HOMA, HOMA_L, HOMA_H = [], [], []
QUICKI, QUICKI_L, QUICKI_H = [], [], []
RQUICKI, RQUICKI_L, RQUICKI_H = [], [], []
RQBHB, RQBHB_L, RQBHB_H = [], [], []

for hb in Hb:
    corr, corr_L, corr_H = {}, {}, {}
    for p in measured:
        a, b, R2 = regression[p].values()
        bias = a * hb + b
        SE = abs(bias) * np.sqrt(1 - R2)
        bias_L = bias - 1.96 * SE
        bias_H = bias + 1.96 * SE
        corr[p] = measured[p] / (1 + bias / 100)
        corr_L[p] = measured[p] / (1 + bias_H / 100)
        corr_H[p] = measured[p] / (1 + bias_L / 100)

    # Indeksi
    HOMA.append((corr["INS"] * corr["GLU"]) / 22.5)
    HOMA_L.append((corr_L["INS"] * corr_L["GLU"]) / 22.5)
    HOMA_H.append((corr_H["INS"] * corr_H["GLU"]) / 22.5)

    QUICKI.append(1 / (np.log(corr["INS"]) + np.log(corr["GLU"])))
    QUICKI_L.append(1 / (np.log(corr_H["INS"]) + np.log(corr_H["GLU"])))
    QUICKI_H.append(1 / (np.log(corr_L["INS"]) + np.log(corr_L["GLU"])))

    RQUICKI.append(1 / (np.log(corr["INS"]) + np.log(corr["GLU"]) + np.log(corr["NEFA"])))
    RQUICKI_L.append(1 / (np.log(corr_H["INS"]) + np.log(corr_H["GLU"]) + np.log(corr_H["NEFA"])))
    RQUICKI_H.append(1 / (np.log(corr_L["INS"]) + np.log(corr_L["GLU"]) + np.log(corr_L["NEFA"])))

    RQBHB.append(1 / (np.log(corr["INS"]) + np.log(corr["GLU"]) + np.log(corr["NEFA"]) + np.log(corr["BHB"])))
    RQBHB_L.append(1 / (np.log(corr_H["INS"]) + np.log(corr_H["GLU"]) + np.log(corr_H["NEFA"]) + np.log(corr_H["BHB"])))
    RQBHB_H.append(1 / (np.log(corr_L["INS"]) + np.log(corr_L["GLU"]) + np.log(corr_L["NEFA"]) + np.log(corr_L["BHB"])))

# =========================
# Funkcija za crtanje grafika sa pragom
# =========================
def plot_index_with_ci_and_threshold(x, y, yL, yH, title, ylabel):
    fig, ax = plt.subplots(figsize=(6,4))
    ax.plot(x, y, linewidth=2, label="Vrednost indeksa")
    ax.fill_between(x, yL, yH, alpha=0.3, color='orange', label="95% CI")
    y0 = y[0]
    rel_change = np.abs(np.array(y) - y0) / y0
    above_tol = np.where(rel_change > tolerance)[0]

    if len(above_tol) > 0:
        Hb_threshold = x[above_tol[0]]
    else:
        Hb_threshold = x[-1]

    ax.axvline(Hb_threshold, color='red', linestyle='--', label=f"Hb prag nestabilnosti")
    if Hb_threshold > 10:
        text_label = "Hb > 10 g/L"
    else:
        text_label = f"Hb = {Hb_threshold:.2f} g/L"
    ax.text(Hb_threshold + 0.2, max(y), text_label, color='red')

    # Plava linija za odabrani Hb
    ax.axvline(selected_Hb, color='blue', linestyle='-.', label=f"Odabrani Hb = {selected_Hb:.1f}")
    ax.set_xlabel("Hemoliza (Hb g/L)")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True)
    ax.legend()
    st.pyplot(fig)

# =========================
# Prikaz 4 grafika
# =========================
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

with col1:
    plot_index_with_ci_and_threshold(Hb, HOMA, HOMA_L, HOMA_H, "HOMA-IR", "HOMA-IR")
with col2:
    plot_index_with_ci_and_threshold(Hb, QUICKI, QUICKI_L, QUICKI_H, "QUICKI", "QUICKI")
with col3:
    plot_index_with_ci_and_threshold(Hb, RQUICKI, RQUICKI_L, RQUICKI_H, "RQUICKI", "RQUICKI")
with col4:
    plot_index_with_ci_and_threshold(Hb, RQBHB, RQBHB_L, RQBHB_H, "RQUICKI-BHB", "RQUICKI-BHB")

# =========================
# Funkcija za korekciju indeksa pri odabranoj Hb
# =========================
def correct_for_Hb(values, Hb_value):
    corr = {}
    for p in values:
        a, b, R2 = regression[p].values()
        bias = a * Hb_value + b
        corr[p] = values[p] / (1 + bias / 100)
    HOMA = (corr["INS"] * corr["GLU"]) / 22.5
    QUICKI = 1 / (np.log(corr["INS"]) + np.log(corr["GLU"]))
    RQUICKI = 1 / (np.log(corr["INS"]) + np.log(corr["GLU"]) + np.log(corr["NEFA"]))
    RQBHB = 1 / (np.log(corr["INS"]) + np.log(corr["GLU"]) + np.log(corr["NEFA"]) + np.log(corr["BHB"]))
    return {"HOMA-IR": HOMA, "QUICKI": QUICKI, "RQUICKI": RQUICKI, "RQUICKI-BHB": RQBHB}

# =========================
# Prikaz tabele sa originalnim i korigovanim vrednostima
# =========================
st.subheader(f"Originalne i korigovane vrednosti indeksa pri Hb = {selected_Hb:.1f} g/L")
corrected_indices = correct_for_Hb(measured, selected_Hb)

table_data = {
    "Indeks": ["HOMA-IR", "QUICKI", "RQUICKI", "RQUICKI-BHB"],
    "Originalna vrednost (Hb=0)": [
        (measured["INS"] * measured["GLU"]) / 22.5,
        1 / (np.log(measured["INS"]) + np.log(measured["GLU"])),
        1 / (np.log(measured["INS"]) + np.log(measured["GLU"]) + np.log(measured["NEFA"])),
        1 / (np.log(measured["INS"]) + np.log(measured["GLU"]) + np.log(measured["NEFA"]) + np.log(measured["BHB"]))
    ],
    f"Korigovana vrednost (Hb={selected_Hb:.1f})": [
        corrected_indices["HOMA-IR"],
        corrected_indices["QUICKI"],
        corrected_indices["RQUICKI"],
        corrected_indices["RQUICKI-BHB"]
    ]
}

df_table = pd.DataFrame(table_data)
st.dataframe(df_table.style.format("{:.3f}"))
