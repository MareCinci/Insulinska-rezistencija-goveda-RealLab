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
BHB_m = st.sidebar.slider("BHB (mmol/L)",_
