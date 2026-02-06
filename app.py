import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("Uticaj hemolize na indekse insulinske rezistencije (sa 95% CI)")

# =========================
# Regresioni parametri
# =========================
regression = {
    "GLU":  {"a": -2.9538, "b": -1.401,  "R2": 0.9794},
    "NEFA": {"a":  9.8218, "b":  2.5353, "R2": 0.9972},
    "BHB":  {"a":  5.3201, "b":  0.957,  "R2": 0.9913},
    "INS":  {"a": -5.5017, "b": -3.7803,"R2": 0.9875}
}

# =========================
# Sidebar – izmerene vrednosti
# =========================
st.sidebar.header("Izmerene vrednosti (bez hemolize)")

measured = {
    "GLU": st.sidebar.number_input("GLU (mmol/L)", 1.0, 20.0, 5.0),
    "INS": st.sidebar.number_input("INS (µIU/mL)", 1.0, 50.0, 10.0),
    "NEFA": st.sidebar.number_input("NEFA (mmol/L)", 0.1, 2.0, 0.6),
    "BHB": st.sidebar.number_input("BHB (mmol/L)", 0.1, 5.0, 0.4)
}

# =========================
# Hb – hemoliza
# =========================
Hb = np.linspace(0, 10, 100)

HOMA, HOMA_L, HOMA_H = [], [], []
QUICKI, QUICKI_L, QUICKI_H = [], [], []
RQUICKI, RQUICKI_L, RQUICKI_H = [], [], []
RQBHB, RQBHB_L, RQBHB_H = [], [], []

# =========================
# Glavna petlja
# =========================
for hb in Hb:

    corr, corr_L, corr_H = {}, {}, {}

    for p in measured:
        a, b, R2 = regression[p].values()
        bias = a * hb + b
        SE = abs(bias) * np.sqrt(1 - R2)

        bias_L = bias - 1.96 * SE
        bias_H = bias + 1.96 * SE

        corr[p]   = measured[p] / (1 + bias / 100)
        corr_L[p] = measured[p] / (1 + bias_H / 100)
        corr_H[p] = measured[p] / (1 + bias_L / 100)

    # HOMA
    HOMA.append((corr["INS"] * corr["GLU"]) / 22.5)
    HOMA_L.append((corr_L["INS"] * corr_L["GLU"]) / 22.5)
    HOMA_H.append((corr_H["INS"] * corr_H["GLU"]) / 22.5)

    # QUICKI
    QUICKI.append(1 / (np.log(corr["INS"]) + np.log(corr["GLU"])))
    QUICKI_L.append(1 / (np.log(corr_H["INS"]) + np.log(corr_H["GLU"])))
    QUICKI_H.append(1 / (np.log(corr_L["INS"]) + np.log(corr_L["GLU"])))

    # RQUICKI
    RQUICKI.append(1 / (np.log(corr["INS"]) + np.log(corr["GLU"]) + np.log(corr["NEFA"])))
    RQUICKI_L.append(1 / (np.log(corr_H["INS"]) + np.log(corr_H["GLU"]) + np.log(corr_H["NEFA"])))
    RQUICKI_H.append(1 / (np.log(corr_L["INS"]) + np.log(corr_L["GLU"]) + np.log(corr_L["NEFA"])))

    # RQUICKI-BHB
    RQBHB.append(1 / (np.log(corr["INS"]) + np.log(corr["GLU"]) +
                      np.log(corr["NEFA"]) + np.log(corr["BHB"])))
    RQBHB_L.append(1 / (np.log(corr_H["INS"]) + np.log(corr_H["GLU"]) +
                        np.log(corr_H["NEFA"]) + np.log(corr_H["BHB"])))
    RQBHB_H.append(1 / (np.log(corr_L["INS"]) + np.log(corr_L["GLU"]) +
                        np.log(corr_L["NEFA"]) + np.log(corr_L["BHB"])))

# =========================
# Funkcija za graf
# =========================
def plot_ci(x, y, yL, yH, title, ylabel):
    fig, ax = plt.subplots(figsize=(6,4))
    ax.plot(x, y, linewidth=2)
    ax.fill_between(x, yL, yH, alpha=0.3)
    ax.set_xlabel("Hemoliza (Hb g/L)")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True)
    st.pyplot(fig)

# =========================
# 4 ODVOJENA GRAFA
# =========================
c1, c2 = st.columns(2)
c3, c4 = st.columns(2)

with c1:
    plot_ci(Hb, HOMA, HOMA_L, HOMA_H, "HOMA-IR (95% CI)", "HOMA-IR")

with c2:
    plot_ci(Hb, QUICKI, QUICKI_L, QUICKI_H, "QUICKI (95% CI)", "QUICKI")

with c3:
    plot_ci(Hb, RQUICKI, RQUICKI_L, RQUICKI_H, "RQUICKI (95% CI)", "RQUICKI")

with c4:
    plot_ci(Hb, RQBHB, RQBHB_L, RQBHB_H, "RQUICKI-BHB (95% CI)", "RQUICKI-BHB")
